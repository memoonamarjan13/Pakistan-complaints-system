from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentInformationResponse(BaseModel):
    department_info_id: int
    department_name: str
    department_work: str
    department_head: str
    office_section: str
    section_officer: str
    officer_phone: str | None = None
    officer_email: str | None = None
    office_location: str | None = None
    services: str | None = None
    working_hours: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ComplaintCreate(BaseModel):
    citizen_name: str = Field(min_length=1, max_length=150)
    cnic: str = Field(min_length=1, max_length=20)
    phone: str = Field(min_length=1, max_length=30)
    address: str = Field(min_length=1)

    department_info_id: int

    complaint_category: str | None = None
    complaint_text: str = Field(min_length=1)

    city: str | None = None
    province: str | None = None

    priority: str = "Normal"


class ComplaintUpdate(BaseModel):
    department_response: str | None = None
    status: str | None = None
    priority: str | None = None


class ComplaintResponse(BaseModel):
    id: int
    complaint_number: str | None = None

    citizen_name: str
    cnic: str
    phone: str
    address: str

    city: str | None = None
    province: str | None = None

    department_name: str

    complaint_category: str | None = None
    complaint_text: str

    previous_complaint_count: int | None = None
    previous_complaint_details: str | None = None

    is_same_complaint: bool | None = None
    same_complaint_people_count: int | None = None

    department_review: str | None = None
    department_response: str | None = None

    status: str | None = None
    priority: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DepartmentResponse(BaseModel):
    department_id: int
    department_info_id: int
    complaint_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ChatMessage(BaseModel):
    question: str = Field(min_length=1)
    answer: str = ""


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str