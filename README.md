# Pakistan Complaint System

## Run backend

```powershell
cd E:\Pakistan-complaint-System
.\venv\Scripts\Activate.ps1
python -m uvicorn Backend.main:app --reload
```

## Run frontend in a second terminal

```powershell
cd E:\Pakistan-complaint-System
.\venv\Scripts\Activate.ps1
python -m streamlit run Frontend/app.py
```

## Database design

- `department_information`: department/office information
- `department`: relationship between `department_information` and `complaints`
- `complaints`: submitted public complaints
- `department_relationship`: relationships between department_information rows
