from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from Backend.database import Base


# ============================================================
# 1. DEPARTMENT INFORMATION
# ============================================================

class DepartmentInformation(Base):
    """
    Stores information about the 10 Pakistani public departments.
    """

    __tablename__ = "department_information"

    department_info_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    department_name = Column(
        String(100),
        nullable=False
    )

    department_work = Column(
        Text,
        nullable=False
    )

    department_head = Column(
        String(100),
        nullable=False
    )

    office_section = Column(
        String(150),
        nullable=False
    )

    section_officer = Column(
        String(100),
        nullable=False
    )

    officer_phone = Column(
        String(30),
        nullable=True
    )

    officer_email = Column(
        String(150),
        nullable=True
    )

    office_location = Column(
        String(200),
        nullable=True
    )

    services = Column(
        Text,
        nullable=True
    )

    working_hours = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationship with departments link table
    complaint_links = relationship(
        "Department",
        back_populates="department_information",
        foreign_keys="Department.department_info_id",
    )

    # Relationships with other departments
    outgoing_relationships = relationship(
        "DepartmentRelationship",
        foreign_keys="DepartmentRelationship.department_id",
        back_populates="department",
    )

    incoming_relationships = relationship(
        "DepartmentRelationship",
        foreign_keys="DepartmentRelationship.related_department_id",
        back_populates="related_department",
    )


# ============================================================
# 2. COMPLAINTS
# ============================================================

class Complaint(Base):
    """
    Stores complaints submitted by citizens.
    """

    __tablename__ = "complaints"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    complaint_number = Column(
        String(30),
        nullable=True,
        unique=True
    )

    citizen_name = Column(
        String(150),
        nullable=False
    )

    cnic = Column(
        String(20),
        nullable=False
    )

    phone = Column(
        String(30),
        nullable=False
    )

    address = Column(
        Text,
        nullable=False
    )

    city = Column(
        String(100),
        nullable=True
    )

    province = Column(
        String(100),
        nullable=True
    )

    department_name = Column(
        String(100),
        nullable=False
    )

    complaint_category = Column(
        String(100),
        nullable=True
    )

    complaint_text = Column(
        Text,
        nullable=False
    )

    previous_complaint_count = Column(
        BigInteger,
        nullable=True,
        default=0
    )

    previous_complaint_details = Column(
        Text,
        nullable=True
    )

    is_same_complaint = Column(
        Boolean,
        nullable=True,
        default=False
    )

    same_complaint_people_count = Column(
        BigInteger,
        nullable=True,
        default=1
    )

    department_review = Column(
        Text,
        nullable=True
    )

    department_response = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=True,
        default="Pending"
    )

    priority = Column(
        String(30),
        nullable=True,
        default="Normal"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationship with departments link table
    department_links = relationship(
        "Department",
        back_populates="complaint",
        foreign_keys="Department.complaint_id",
    )


# ============================================================
# 3. DEPARTMENTS
# ============================================================

class Department(Base):
    """
    Link table between department_information and complaints.

    One row means:
    this complaint belongs to this department.
    """

    __tablename__ = "departments"

    department_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    department_info_id = Column(
        BigInteger,
        ForeignKey(
            "department_information.department_info_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    complaint_id = Column(
        BigInteger,
        ForeignKey(
            "complaints.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    department_information = relationship(
        "DepartmentInformation",
        back_populates="complaint_links",
        foreign_keys=[department_info_id],
    )

    complaint = relationship(
        "Complaint",
        back_populates="department_links",
        foreign_keys=[complaint_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "department_info_id",
            "complaint_id",
            name="unique_department_complaint",
        ),
    )


# ============================================================
# 4. DEPARTMENT RELATIONSHIPS
# ============================================================

class DepartmentRelationship(Base):
    """
    Stores relationships between two departments.
    """

    __tablename__ = "department_relationships"

    relationship_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    department_id = Column(
        BigInteger,
        ForeignKey(
            "department_information.department_info_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    related_department_id = Column(
        BigInteger,
        ForeignKey(
            "department_information.department_info_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    relationship_type = Column(
        String(100),
        nullable=False
    )

    relationship_description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    department = relationship(
        "DepartmentInformation",
        foreign_keys=[department_id],
        back_populates="outgoing_relationships",
    )

    related_department = relationship(
        "DepartmentInformation",
        foreign_keys=[related_department_id],
        back_populates="incoming_relationships",
    )

    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "related_department_id",
            name="unique_department_relationship",
        ),

        CheckConstraint(
            "department_id <> related_department_id",
            name="no_self_relationship",
        ),
    )