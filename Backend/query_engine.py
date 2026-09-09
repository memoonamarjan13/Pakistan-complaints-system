from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from Backend.models import Complaint, Department, DepartmentInformation


def _base_count_query(db: Session):
    return db.query(func.count(Complaint.id)).select_from(Complaint)


def count_complaints(
    db: Session,
    department: str | None = None,
    city: str | None = None,
    province: str | None = None,
    status: str | None = None,
):
    query = _base_count_query(db)

    if department:
        query = query.filter(func.lower(Complaint.department_name) == department.strip().lower())
    if city:
        query = query.filter(func.lower(Complaint.city) == city.strip().lower())
    if province:
        query = query.filter(func.lower(Complaint.province) == province.strip().lower())
    if status:
        query = query.filter(func.lower(Complaint.status) == status.strip().lower())

    return int(query.scalar() or 0)


def count_by_department(db: Session, department: str):
    return count_complaints(db, department=department)


def count_by_status(db: Session, status: str):
    return count_complaints(db, status=status)


def count_by_city(db: Session, city: str):
    return count_complaints(db, city=city)


def count_by_province(db: Session, province: str):
    return count_complaints(db, province=province)


def department_counts(db: Session):
    return (
        db.query(
            Complaint.department_name,
            func.count(Complaint.id).label("total"),
        )
        .group_by(Complaint.department_name)
        .order_by(Complaint.department_name)
        .all()
    )


def top_department(db: Session):
    return (
        db.query(
            Complaint.department_name,
            func.count(Complaint.id).label("total"),
        )
        .group_by(Complaint.department_name)
        .order_by(func.count(Complaint.id).desc())
        .first()
    )


def get_complaint(db: Session, complaint_id: int):
    return db.query(Complaint).filter(Complaint.id == complaint_id).first()


def get_complaint_by_number(db: Session, complaint_number: str):
    return (
        db.query(Complaint)
        .filter(func.lower(Complaint.complaint_number) == complaint_number.strip().lower())
        .first()
    )


def _cnic_normalized(column):
    # Allows 35202-1234567-8 and 3520212345678 to match the same database value.
    return func.replace(func.replace(column, "-", ""), " ", "")


def get_complaints_by_cnic(db: Session, cnic: str):
    value = cnic.strip().replace("-", "").replace(" ", "")
    return (
        db.query(Complaint)
        .filter(_cnic_normalized(Complaint.cnic) == value)
        .order_by(Complaint.id.desc())
        .all()
    )


def search_complaints(
    db: Session,
    *,
    name: str | None = None,
    cnic: str | None = None,
    complaint_number: str | None = None,
    complaint_id: int | None = None,
    department: str | None = None,
    address: str | None = None,
    city: str | None = None,
    province: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
):
    """Search real complaint records using one or more user supplied identifiers."""
    query = db.query(Complaint)

    if complaint_id is not None:
        query = query.filter(Complaint.id == complaint_id)

    if complaint_number:
        query = query.filter(
            func.lower(Complaint.complaint_number) == complaint_number.strip().lower()
        )

    if cnic:
        value = cnic.strip().replace("-", "").replace(" ", "")
        query = query.filter(_cnic_normalized(Complaint.cnic) == value)

    if name:
        query = query.filter(Complaint.citizen_name.ilike(f"%{name.strip()}%"))

    if department:
        query = query.filter(Complaint.department_name.ilike(f"%{department.strip()}%"))

    if address:
        query = query.filter(Complaint.address.ilike(f"%{address.strip()}%"))

    if city:
        query = query.filter(Complaint.city.ilike(f"%{city.strip()}%"))

    if province:
        query = query.filter(Complaint.province.ilike(f"%{province.strip()}%"))

    if status:
        query = query.filter(func.lower(Complaint.status) == status.strip().lower())

    if keyword:
        term = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Complaint.complaint_text.ilike(term),
                Complaint.complaint_category.ilike(term),
                Complaint.department_name.ilike(term),
                Complaint.citizen_name.ilike(term),
                Complaint.address.ilike(term),
                Complaint.city.ilike(term),
                Complaint.province.ilike(term),
                Complaint.status.ilike(term),
            )
        )

    return query.order_by(Complaint.id.desc()).limit(limit).all()


def get_department_information(db: Session, department_name: str):
    return (
        db.query(DepartmentInformation)
        .filter(func.lower(DepartmentInformation.department_name) == department_name.strip().lower())
        .first()
    )


def get_related_departments(db: Session, department_name: str):
    department = get_department_information(db, department_name)
    if not department:
        return []

    department_record = (
        db.query(Department)
        .filter(Department.department_info_id == department.department_info_id)
        .first()
    )
    if not department_record:
        return []

    from Backend.models import DepartmentRelationship

    return (
        db.query(
            DepartmentInformation.department_name,
            DepartmentRelationship.relationship_type,
            DepartmentRelationship.relationship_description,
        )
        .join(
            DepartmentRelationship,
            DepartmentRelationship.related_department_id == DepartmentInformation.department_info_id,
        )
        .filter(DepartmentRelationship.department_id == department_record.department_id)
        .all()
    )
