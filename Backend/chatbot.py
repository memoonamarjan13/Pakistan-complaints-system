from typing import Literal
import re

from google import genai
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend.config import settings
from Backend.query_engine import (
    count_complaints,
    count_by_city,
    count_by_province,
    count_by_department,
    count_by_status,
    top_department,
    get_department_information,
    get_related_departments,
    search_complaints,
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

ALLOWED_DEPARTMENTS = [
    "Police", "Health", "Education", "Electricity", "Gas",
    "Water & Sanitation", "Local Government", "Transport", "Revenue",
    "Public Works",
]

ALLOWED_STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]


class QueryIntent(BaseModel):
    intent: Literal[
        "total_count", "department_count", "status_count", "city_count",
        "province_count", "top_department", "complaint_search",
        "complaint_details", "department_information", "department_relationship", "invalid",
    ]
    name: str | None = None
    cnic: str | None = None
    complaint_number: str | None = None
    complaint_id: int | None = None
    department: str | None = None
    related_department: str | None = None
    address: str | None = None
    city: str | None = None
    province: str | None = None
    status: str | None = None
    keyword: str | None = None
    requested_field: Literal[
        "id", "complaint_number", "citizen_name", "cnic", "phone", "address",
        "department_name", "category", "complaint_text", "previous_complaint_count",
        "previous_complaint_details", "is_same_complaint", "same_complaint_people_count",
        "department_review", "department_response", "status", "priority", "city", "province",
        "created_at", "updated_at", "resolved_at", "all", "none",
    ] = "none"


def _history_text(history: list[dict] | None) -> str:
    if not history:
        return "No previous conversation."
    recent = history[-6:]
    return "\n".join(
        f"User: {item.get('question', '')}\nAssistant: {item.get('answer', '')}"
        for item in recent
    )


def understand_question(question: str, history: list[dict] | None = None) -> QueryIntent:
    prompt = f"""
You classify questions for a Pakistan Public Complaint System.
The database table complaints has: id, complaint_number, citizen_name, cnic, phone,
address, city, province, department_name, complaint_category, complaint_text,
previous_complaint_count, previous_complaint_details, is_same_complaint,
same_complaint_people_count, department_review, department_response, status, priority,
created_at, updated_at, resolved_at.

Allowed departments: {", ".join(ALLOWED_DEPARTMENTS)}
Allowed statuses: {", ".join(ALLOWED_STATUSES)}

PREVIOUS CONVERSATION:
{_history_text(history)}

CURRENT QUESTION:
{question}

Rules:
1. total_count = asks only how many complaints exist.
2. department_count/status_count/city_count/province_count = asks only for a count.
3. top_department = asks which department has the most complaints.
4. complaint_search = asks to FIND/LIST one or more complaint records using a name, CNIC,
   complaint number, department, address, city, province, status, or keyword.
5. complaint_details = asks for details of a particular complaint and supplies an identifier,
   such as complaint ID/number, CNIC, name, department, or address. Use complaint_search if
   multiple records may match and the user asks to list/show them.
6. If a user gives a CNIC, ALWAYS put it in cnic. Do not confuse CNIC with complaint ID.
7. If a user gives a complaint number such as CMP-001, put it in complaint_number.
8. If the user asks by citizen name, put the name in name.
9. If the user asks by address, put the address in address.
10. If the user asks by department, put it in department.
11. If the user says "this CNIC", "this complaint", "their complaint", "that complaint",
    or another follow-up without repeating the identifier, use the previous conversation to
    recover the relevant identifier.
12. requested_field=all when the user asks for complete/full/details of the complaint.
13. For a single-field question, set requested_field to only that field.
14. Never invent an identifier. If no identifier is available, use complaint_search only when
    a useful keyword/filter is present.
15. Return JSON only.
"""
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": QueryIntent.model_json_schema(),
        },
    )
    return QueryIntent.model_validate_json(response.text)


def _extract_cnic(question: str) -> str | None:
    match = re.search(r"\b\d{5}[- ]?\d{7}[- ]?\d\b", question)
    return match.group(0) if match else None


def _extract_complaint_number(question: str) -> str | None:
    match = re.search(r"\b(?:CMP|COMP|COMPLAINT)[-_ ]?\d+\b", question, re.I)
    return match.group(0).replace(" ", "-").upper() if match else None


def _value(v):
    return "N/A" if v is None or v == "" else str(v)


def _format_complaint(c) -> str:
    return (
        f"Complaint ID: {_value(c.id)}\n"
        f"Complaint Number: {_value(c.complaint_number)}\n"
        f"Citizen Name: {_value(c.citizen_name)}\n"
        f"CNIC: {_value(c.cnic)}\n"
        f"Phone: {_value(c.phone)}\n"
        f"Address: {_value(c.address)}\n"
        f"City: {_value(c.city)}\n"
        f"Province: {_value(c.province)}\n"
        f"Department: {_value(c.department_name)}\n"
        f"Category: {_value(c.complaint_category)}\n"
        f"Complaint: {_value(c.complaint_text)}\n"
        f"Previous Complaint Count: {_value(c.previous_complaint_count)}\n"
        f"Previous Complaint Details: {_value(c.previous_complaint_details)}\n"
        f"Same Complaint: {_value(c.is_same_complaint)}\n"
        f"Same Complaint People Count: {_value(c.same_complaint_people_count)}\n"
        f"Department Review: {_value(c.department_review)}\n"
        f"Department Response: {_value(c.department_response)}\n"
        f"Status: {_value(c.status)}\n"
        f"Priority: {_value(c.priority)}\n"
        f"Created At: {_value(c.created_at)}\n"
        f"Updated At: {_value(c.updated_at)}\n"
        f"Resolved At: {_value(c.resolved_at)}"
    )


def _format_requested_field(c, field: str) -> str:
    fields = {
        "id": ("Complaint ID", c.id),
        "complaint_number": ("Complaint Number", c.complaint_number),
        "citizen_name": ("Citizen Name", c.citizen_name),
        "cnic": ("CNIC", c.cnic),
        "phone": ("Phone", c.phone),
        "address": ("Address", c.address),
        "department_name": ("Department", c.department_name),
        "category": ("Category", c.complaint_category),
        "complaint_text": ("Complaint", c.complaint_text),
        "previous_complaint_count": ("Previous Complaint Count", c.previous_complaint_count),
        "previous_complaint_details": ("Previous Complaint Details", c.previous_complaint_details),
        "is_same_complaint": ("Same Complaint", c.is_same_complaint),
        "same_complaint_people_count": ("Same Complaint People Count", c.same_complaint_people_count),
        "department_review": ("Department Review", c.department_review),
        "department_response": ("Department Response", c.department_response),
        "status": ("Status", c.status),
        "priority": ("Priority", c.priority),
        "city": ("City", c.city),
        "province": ("Province", c.province),
        "created_at": ("Created At", c.created_at),
        "updated_at": ("Updated At", c.updated_at),
        "resolved_at": ("Resolved At", c.resolved_at),
    }
    if field not in fields:
        return "Please specify what information you want."
    label, value = fields[field]
    return f"{label}: {_value(value)}"


def answer_question(db: Session, question: str, history: list[dict] | None = None) -> str:
    try:
        query = understand_question(question, history)
    except Exception as exc:
        return f"I could not understand the question. Please try again."

    # Deterministic identifier extraction prevents Gemini from losing an exact CNIC/number.
    extracted_cnic = _extract_cnic(question)
    if extracted_cnic:
        query.cnic = extracted_cnic
        if query.intent in {"invalid", "total_count", "department_count", "status_count", "city_count", "province_count", "top_department"}:
            query.intent = "complaint_details"
        if query.requested_field == "none":
            query.requested_field = "all"

    extracted_number = _extract_complaint_number(question)
    if extracted_number:
        query.complaint_number = extracted_number
        if query.intent in {"invalid", "total_count", "department_count", "status_count", "city_count", "province_count", "top_department"}:
            query.intent = "complaint_details"
        if query.requested_field == "none":
            query.requested_field = "all"

    if query.intent == "invalid":
        return "I can answer questions related to complaints and departments."

    if query.intent == "total_count":
        return f"There are {count_complaints(db)} complaints."

    if query.intent == "department_count":
        if not query.department:
            return "Please specify a department."
        return f"There are {count_by_department(db, query.department)} complaints against {query.department}."

    if query.intent == "status_count":
        if not query.status:
            return "Please specify a complaint status."
        return f"There are {count_by_status(db, query.status)} complaints with status {query.status}."

    if query.intent == "city_count":
        if not query.city:
            return "Please specify a city."
        return f"There are {count_by_city(db, query.city)} complaints in {query.city}."

    if query.intent == "province_count":
        if not query.province:
            return "Please specify a province."
        return f"There are {count_by_province(db, query.province)} complaints in {query.province}."

    if query.intent == "top_department":
        result = top_department(db)
        if not result:
            return "There are no complaints."
        name, total = result
        return f"{name} has the highest number of complaints with {total} complaints."

    if query.intent in {"complaint_search", "complaint_details"}:
        complaints = search_complaints(
            db,
            name=query.name,
            cnic=query.cnic,
            complaint_number=query.complaint_number,
            complaint_id=query.complaint_id,
            department=query.department,
            address=query.address,
            city=query.city,
            province=query.province,
            status=query.status,
            keyword=query.keyword,
        )

        if not complaints:
            return "No complaint was found matching the information you provided."

        # A single exact/strong match can be returned in full or as one requested field.
        if len(complaints) == 1:
            complaint = complaints[0]
            if query.requested_field not in {"none", "all"}:
                return _format_requested_field(complaint, query.requested_field)
            return "Here are the complaint details:\n\n" + _format_complaint(complaint)

        # Multiple matches: show all matching records with enough detail to distinguish them.
        lines = [f"I found {len(complaints)} matching complaints:"]
        for i, complaint in enumerate(complaints, 1):
            lines.append(
                f"\n{i}. ID: {_value(complaint.id)} | Number: {_value(complaint.complaint_number)} | "
                f"Name: {_value(complaint.citizen_name)} | CNIC: {_value(complaint.cnic)} | "
                f"Department: {_value(complaint.department_name)} | Status: {_value(complaint.status)}\n"
                f"   Complaint: {_value(complaint.complaint_text)}\n"
                f"   Address: {_value(complaint.address)} | City: {_value(complaint.city)} | "
                f"Priority: {_value(complaint.priority)}"
            )
        return "\n".join(lines)

    if query.intent == "department_information":
        if not query.department:
            return "Please specify a department."
        department = get_department_information(db, query.department)
        if not department:
            return "Department not found."
        return (
            f"Department: {_value(department.department_name)}\n"
            f"Work: {_value(department.department_work)}\n"
            f"Head: {_value(department.department_head)}\n"
            f"Office Section: {_value(department.office_section)}\n"
            f"Section Officer: {_value(department.section_officer)}\n"
            f"Officer Phone: {_value(department.officer_phone)}\n"
            f"Officer Email: {_value(department.officer_email)}\n"
            f"Office Location: {_value(department.office_location)}\n"
            f"Services: {_value(department.services)}\n"
            f"Working Hours: {_value(department.working_hours)}"
        )

    if query.intent == "department_relationship":
        if not query.department:
            return "Please specify a department."
        relationships = get_related_departments(db, query.department)
        if not relationships:
            return f"No department relationships found for {query.department}."
        return f"{query.department} is related to: " + ", ".join(item[0] for item in relationships) + "."

    return "I could not understand the question."
