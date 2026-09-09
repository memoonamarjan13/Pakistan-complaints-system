from datetime import datetime, timezone

from sqlalchemy.orm import Session

from Backend.models import Complaint, Department, DepartmentInformation
from Backend.schemas import ComplaintCreate, ComplaintUpdate


# =========================================================
# DEPARTMENTS
# =========================================================

def get_departments(db: Session):
    """
    Return all department information rows.
    Multiple rows with the same department name are allowed.
    """
    return (
        db.query(DepartmentInformation)
        .order_by(DepartmentInformation.department_info_id)
        .all()
    )


def get_department(db: Session, department_info_id: int):
    return (
        db.query(DepartmentInformation)
        .filter(
            DepartmentInformation.department_info_id == department_info_id
        )
        .first()
    )


# =========================================================
# CREATE COMPLAINT
# =========================================================

def create_complaint(
    db: Session,
    complaint_data: ComplaintCreate
):
    # Find selected department
    department_info = (
        db.query(DepartmentInformation)
        .filter(
            DepartmentInformation.department_info_id
            == complaint_data.department_info_id
        )
        .first()
    )

    if not department_info:
        raise ValueError(
            "Department information does not exist."
        )

    # Create complaint
    complaint = Complaint(
        citizen_name=complaint_data.citizen_name,
        cnic=complaint_data.cnic,
        phone=complaint_data.phone,
        address=complaint_data.address,
        city=complaint_data.city,
        province=complaint_data.province,

        department_name=department_info.department_name,

        complaint_category=complaint_data.complaint_category,
        complaint_text=complaint_data.complaint_text,

        priority=complaint_data.priority,
        status="Pending",
    )

    db.add(complaint)

    # Get complaint ID before creating department relationship
    db.flush()

    # Automatically link complaint with department
    link = Department(
        department_info_id=department_info.department_info_id,
        complaint_id=complaint.id,
    )

    db.add(link)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(complaint)

    return complaint


# =========================================================
# GET SINGLE COMPLAINT
# =========================================================

def get_complaint(
    db: Session,
    complaint_id: int
):
    return (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )


# =========================================================
# GET DEPARTMENT COMPLAINTS
# =========================================================

def get_department_complaints(
    db: Session,
    department_info_id: int
):
    """
    Return all complaints assigned to a specific department.
    """

    return (
        db.query(Complaint)
        .join(
            Department,
            Department.complaint_id == Complaint.id
        )
        .filter(
            Department.department_info_id
            == department_info_id
        )
        .order_by(
            Complaint.created_at.desc()
        )
        .all()
    )


# =========================================================
# UPDATE COMPLAINT
# =========================================================

def update_complaint(
    db: Session,
    complaint_id: int,
    complaint_data: ComplaintUpdate
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if not complaint:
        return None

    # -----------------------------------------
    # Department Response
    # -----------------------------------------

    if complaint_data.department_response is not None:
        complaint.department_response = (
            complaint_data.department_response
        )

    # -----------------------------------------
    # Status
    # -----------------------------------------

    if complaint_data.status is not None:

        allowed_statuses = [
            "Pending",
            "In Progress",
            "Resolved",
            "Closed",
            "Rejected",
        ]

        if complaint_data.status not in allowed_statuses:
            raise ValueError(
                "Invalid status. "
                "Allowed values: Pending, In Progress, "
                "Resolved, Closed, Rejected."
            )

        complaint.status = complaint_data.status

        # If complaint is resolved or closed
        if complaint_data.status in [
            "Resolved",
            "Closed"
        ]:
            complaint.resolved_at = datetime.now(
                timezone.utc
            )

        else:
            complaint.resolved_at = None

    # -----------------------------------------
    # Priority
    # -----------------------------------------

    if complaint_data.priority is not None:

        allowed_priorities = [
            "Low",
            "Normal",
            "High",
            "Urgent",
        ]

        if complaint_data.priority not in allowed_priorities:
            raise ValueError(
                "Invalid priority. "
                "Allowed values: Low, Normal, High, Urgent."
            )

        complaint.priority = complaint_data.priority

    # -----------------------------------------
    # Updated time
    # -----------------------------------------

    complaint.updated_at = datetime.now(
        timezone.utc
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(complaint)

    return complaint