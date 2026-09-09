from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session

from Backend import crud
from Backend.chatbot import answer_question
from Backend.database import get_db

from Backend.schemas import (
    ChatRequest,
    ChatResponse,
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
    DepartmentInformationResponse,
)


app = FastAPI(
    title="Pakistan Public Complaint System",
    version="1.0.0",
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "Pakistan Public Complaint API is running"
    }


# =========================================================
# DEPARTMENTS
# =========================================================

@app.get(
    "/departments",
    response_model=list[DepartmentInformationResponse],
)
def departments(
    db: Session = Depends(get_db)
):
    return crud.get_departments(db)


# =========================================================
# SINGLE DEPARTMENT
# =========================================================

@app.get(
    "/departments/{department_info_id}",
    response_model=DepartmentInformationResponse,
)
def get_department(
    department_info_id: int,
    db: Session = Depends(get_db)
):

    department = crud.get_department(
        db,
        department_info_id
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    return department


# =========================================================
# DEPARTMENT COMPLAINTS
# =========================================================

@app.get(
    "/departments/{department_info_id}/complaints",
    response_model=list[ComplaintResponse],
)
def get_department_complaints(
    department_info_id: int,
    db: Session = Depends(get_db)
):

    # Check department exists
    department = crud.get_department(
        db,
        department_info_id
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    return crud.get_department_complaints(
        db,
        department_info_id
    )


# =========================================================
# CREATE COMPLAINT
# =========================================================

@app.post(
    "/complaints",
    response_model=ComplaintResponse
)
def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db),
):

    try:

        return crud.create_complaint(
            db,
            complaint
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not save complaint: {error}",
        ) from error


# =========================================================
# GET SINGLE COMPLAINT
# =========================================================

@app.get(
    "/complaints/{complaint_id}",
    response_model=ComplaintResponse
)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):

    complaint = crud.get_complaint(
        db,
        complaint_id
    )

    if not complaint:

        raise HTTPException(
            status_code=404,
            detail="Complaint not found."
        )

    return complaint


# =========================================================
# UPDATE COMPLAINT
# =========================================================

@app.patch(
    "/complaints/{complaint_id}",
    response_model=ComplaintResponse
)
def update_complaint(
    complaint_id: int,
    complaint_data: ComplaintUpdate,
    db: Session = Depends(get_db),
):

    try:

        complaint = crud.update_complaint(
            db,
            complaint_id,
            complaint_data
        )

        if not complaint:

            raise HTTPException(
                status_code=404,
                detail="Complaint not found."
            )

        return complaint

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except HTTPException:

        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not update complaint: {error}",
        ) from error


# =========================================================
# CHATBOT
# =========================================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    return {
        "answer": answer_question(
            db,
            request.question
        )
    }