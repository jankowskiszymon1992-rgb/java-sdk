from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums
class ProjectStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# ============= MODELS =============

class Client(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: Optional[str] = None
    address: str
    city: str
    postal_code: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClientCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: str
    city: str
    postal_code: str
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    notes: Optional[str] = None


# ============= EMPLOYEE MODELS =============

class Employee(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hourly_rate: float  # Stawka za godzinę
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmployeeCreate(BaseModel):
    name: str
    hourly_rate: float
    notes: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    hourly_rate: Optional[float] = None
    notes: Optional[str] = None


class EmployeeWorkEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str  # Denormalized for easier queries
    date: str  # Format: YYYY-MM-DD
    hours: float
    hourly_rate: float  # Snapshot of rate at time of entry
    total_earnings: float  # hours * hourly_rate
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmployeeWorkEntryCreate(BaseModel):
    employee_id: str
    date: str
    hours: float
    notes: Optional[str] = None


class VoiceWorkEntryRequest(BaseModel):
    transcript: str  # Text from Whisper


# ============= FINANCIAL ENTRIES MODELS =============

class FinancialCategory(str, Enum):
    # Przychody
    invoice_sales = "invoice_sales"  # Faktura sprzedażowa
    cash_income = "cash_income"  # Pieniądze bez faktury
    
    # Wydatki
    invoice_purchase = "invoice_purchase"  # Faktura zakupowa
    fuel = "fuel"  # Paliwo
    salaries = "salaries"  # Wypłaty pracowników
    taxes = "taxes"  # Podatki
    zus = "zus"  # ZUS
    equipment = "equipment"  # Sprzęt
    clothes = "clothes"  # Ciuchy dla pracowników


class FinancialEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # Format: YYYY-MM-DD
    category: FinancialCategory
    description: str  # Numer faktury, opis, etc.
    amount_net: float  # Kwota netto
    amount_gross: float  # Kwota brutto
    vat_rate: Optional[float] = None  # Stawka VAT %
    image_url: Optional[str] = None  # Opcjonalnie zdjęcie faktury
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinancialEntryCreate(BaseModel):
    date: str
    category: FinancialCategory
    description: str
    amount_net: float
    amount_gross: float
    vat_rate: Optional[float] = None
    notes: Optional[str] = None


class FinancialEntryUpdate(BaseModel):
    date: Optional[str] = None
    category: Optional[FinancialCategory] = None
    description: Optional[str] = None
    amount_net: Optional[float] = None
    amount_gross: Optional[float] = None
    vat_rate: Optional[float] = None
    notes: Optional[str] = None


class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    title: str
    description: str
    status: ProjectStatus = ProjectStatus.new
    start_date: str  # ISO date string
    end_date: Optional[str] = None  # ISO date string
    location: str
    estimated_hours: Optional[float] = None
    materials_notes: Optional[list] = []  # Lista materiałów
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectCreate(BaseModel):
    client_id: str
    title: str
    description: str
    status: Optional[ProjectStatus] = ProjectStatus.new
    start_date: str
    end_date: Optional[str] = None
    location: str
    estimated_hours: Optional[float] = None


class ProjectUpdate(BaseModel):
    client_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    estimated_hours: Optional[float] = None
    materials_notes: Optional[list] = None


class WorkHour(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    date: str  # ISO date string
    hours: float
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkHourCreate(BaseModel):
    project_id: str
    date: str
    hours: float
    notes: Optional[str] = None


class WorkHourUpdate(BaseModel):
    project_id: Optional[str] = None
    date: Optional[str] = None
    hours: Optional[float] = None
    notes: Optional[str] = None


class Photo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    image_data: str  # base64 encoded image
    taken_date: str  # ISO date string
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PhotoCreate(BaseModel):
    project_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    image_data: str
    taken_date: str


class PhotoUpdate(BaseModel):
    project_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    taken_date: Optional[str] = None


# ============= HELPER FUNCTIONS =============

def serialize_doc(doc):
    """Convert datetime objects to ISO strings for MongoDB"""
    if doc:
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
    return doc


def deserialize_doc(doc):
    """Convert ISO strings back to datetime objects"""
    if doc:
        for key in ['created_at', 'updated_at']:
            if key in doc and isinstance(doc[key], str):
                doc[key] = datetime.fromisoformat(doc[key])
    return doc


# ============= CLIENT ENDPOINTS =============

@api_router.post("/clients", response_model=Client)
async def create_client(client_input: ClientCreate):
    client_obj = Client(**client_input.model_dump())
    doc = serialize_doc(client_obj.model_dump())
    await db.clients.insert_one(doc)
    return client_obj


@api_router.get("/clients", response_model=List[Client])
async def get_clients():
    clients = await db.clients.find({}, {"_id": 0}).to_list(1000)
    return [deserialize_doc(client) for client in clients]


@api_router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    return deserialize_doc(client)


@api_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client_update: ClientUpdate):
    # Check if client exists
    existing = await db.clients.find_one({"id": client_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    
    # Update only provided fields
    update_data = {k: v for k, v in client_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.clients.update_one({"id": client_id}, {"$set": update_data})
    
    updated_client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    return deserialize_doc(updated_client)


@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str):
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    return {"message": "Klient usunięty pomyślnie"}


# ============= EMPLOYEE ENDPOINTS =============

@api_router.post("/employees", response_model=Employee)
async def create_employee(employee_input: EmployeeCreate):
    employee = Employee(**employee_input.dict())
    await db.employees.insert_one(employee.dict())
    return employee


@api_router.get("/employees", response_model=List[Employee])
async def get_employees():
    employees = await db.employees.find().to_list(None)
    return [Employee(**emp) for emp in employees]


@api_router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Pracownik nie znaleziony")
    return Employee(**employee)


@api_router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee_input: EmployeeUpdate):
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Pracownik nie znaleziony")
    
    update_data = {k: v for k, v in employee_input.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.employees.update_one({"id": employee_id}, {"$set": update_data})
    updated_employee = await db.employees.find_one({"id": employee_id})
    return Employee(**updated_employee)


@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    # First, check if employee exists
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Pracownik nie znaleziony")
    
    # Delete all work entries for this employee (cascade delete)
    await db.employee_work_entries.delete_many({"employee_id": employee_id})
    
    # Delete the employee
    await db.employees.delete_one({"id": employee_id})
    
    return {"message": "Pracownik i jego godziny pracy usunięte pomyślnie"}


# ============= EMPLOYEE WORK ENTRIES =============

@api_router.post("/employee-work-entries", response_model=EmployeeWorkEntry)
async def create_work_entry(entry_input: EmployeeWorkEntryCreate):
    # Get employee to fetch current rate and name
    employee = await db.employees.find_one({"id": entry_input.employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Pracownik nie znaleziony")
    
    total_earnings = entry_input.hours * employee["hourly_rate"]
    
    entry = EmployeeWorkEntry(
        employee_id=entry_input.employee_id,
        employee_name=employee["name"],
        date=entry_input.date,
        hours=entry_input.hours,
        hourly_rate=employee["hourly_rate"],
        total_earnings=total_earnings,
        notes=entry_input.notes
    )
    
    await db.employee_work_entries.insert_one(entry.dict())
    return entry


@api_router.get("/employee-work-entries", response_model=List[EmployeeWorkEntry])
async def get_work_entries(
    employee_id: Optional[str] = None,
    month: Optional[str] = None  # Format: YYYY-MM
):
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if month:
        # Filter by month (date starts with YYYY-MM)
        query["date"] = {"$regex": f"^{month}"}
    
    entries = await db.employee_work_entries.find(query).sort("date", -1).to_list(None)
    return [EmployeeWorkEntry(**entry) for entry in entries]


@api_router.get("/employee-work-entries/summary")
async def get_work_summary(month: Optional[str] = None):
    """Get summary of earnings by employee for a given month"""
    match_stage = {}
    if month:
        match_stage = {"date": {"$regex": f"^{month}"}}
    
    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$employee_id",
                "employee_name": {"$first": "$employee_name"},
                "total_hours": {"$sum": "$hours"},
                "total_earnings": {"$sum": "$total_earnings"}
            }
        }
    ]
    
    summary = await db.employee_work_entries.aggregate(pipeline).to_list(None)
    
    return {
        "month": month if month else "all_time",
        "employees": [
            {
                "employee_id": item["_id"],
                "employee_name": item["employee_name"],
                "total_hours": item["total_hours"],
                "total_earnings": item["total_earnings"]
            }
            for item in summary
        ],
        "grand_total": sum(item["total_earnings"] for item in summary)
    }


@api_router.put("/employee-work-entries/{entry_id}", response_model=EmployeeWorkEntry)
async def update_work_entry(entry_id: str, entry_input: EmployeeWorkEntryCreate):
    # Check if entry exists
    existing = await db.employee_work_entries.find_one({"id": entry_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")
    
    # Get employee to fetch current rate and name
    employee = await db.employees.find_one({"id": entry_input.employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Pracownik nie znaleziony")
    
    # Calculate earnings
    total_earnings = entry_input.hours * employee["hourly_rate"]
    
    # Prepare update data
    update_data = {
        "employee_id": entry_input.employee_id,
        "employee_name": employee["name"],
        "date": entry_input.date,
        "hours": entry_input.hours,
        "hourly_rate": employee["hourly_rate"],
        "total_earnings": total_earnings,
        "notes": entry_input.notes or "",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.employee_work_entries.update_one({"id": entry_id}, {"$set": update_data})
    
    updated_entry = await db.employee_work_entries.find_one({"id": entry_id}, {"_id": 0})
    return deserialize_doc(updated_entry)


@api_router.delete("/employee-work-entries/{entry_id}")
async def delete_work_entry(entry_id: str):
    result = await db.employee_work_entries.delete_one({"id": entry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")
    return {"message": "Wpis usunięty pomyślnie"}


# ============= VOICE WORK ENTRY (WITH LLM PARSING) =============

@api_router.post("/employee-work-entries/voice")
async def create_voice_work_entry(request: VoiceWorkEntryRequest):
    """Parse voice transcript and create work entries"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Brak klucza API")
        
        # Get all employees for context
        employees = await db.employees.find().to_list(None)
        employee_names = [emp["name"] for emp in employees]
        
        # Use LLM to parse the transcript
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompt = f"""Analyze this transcript and extract work hours information.

Available employees: {', '.join(employee_names)}

Transcript: "{request.transcript}"

Extract:
1. Employee names (match to available employees)
2. Hours worked for each employee
3. Date mentioned (interpret "dzisiaj"=today, "wczoraj"=yesterday, or specific date)

Return ONLY valid JSON in this format:
{{
  "entries": [
    {{"employee_name": "Name", "hours": 8.0, "date": "YYYY-MM-DD"}}
  ]
}}

Today's date is: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
"""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"voice_work_{datetime.now().timestamp()}"
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON from response
        import json
        import re
        
        # Extract JSON from response (might be wrapped in markdown)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise HTTPException(status_code=400, detail="Nie udało się sparsować odpowiedzi")
        
        parsed_data = json.loads(json_match.group())
        
        # Create work entries
        created_entries = []
        for entry_data in parsed_data.get("entries", []):
            # Find employee by name
            employee = next(
                (emp for emp in employees if emp["name"].lower() == entry_data["employee_name"].lower()),
                None
            )
            
            if not employee:
                continue  # Skip if employee not found
            
            # Create entry
            entry_input = EmployeeWorkEntryCreate(
                employee_id=employee["id"],
                date=entry_data["date"],
                hours=float(entry_data["hours"]),
                notes=f"Dodano głosowo: {request.transcript}"
            )
            
            total_earnings = entry_input.hours * employee["hourly_rate"]
            
            entry = EmployeeWorkEntry(
                employee_id=entry_input.employee_id,
                employee_name=employee["name"],
                date=entry_input.date,
                hours=entry_input.hours,
                hourly_rate=employee["hourly_rate"],
                total_earnings=total_earnings,
                notes=entry_input.notes
            )
            
            await db.employee_work_entries.insert_one(entry.dict())
            created_entries.append(entry)
        
        return {
            "success": True,
            "entries_created": len(created_entries),
            "entries": created_entries
        }
        
    except Exception as e:
        logger.error(f"Error in voice work entry: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania: {str(e)}")


# ============= PROJECT ENDPOINTS =============

@api_router.post("/projects", response_model=Project)
async def create_project(project_input: ProjectCreate):
    # Verify client exists
    client = await db.clients.find_one({"id": project_input.client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    
    project_obj = Project(**project_input.model_dump())
    doc = serialize_doc(project_obj.model_dump())
    await db.projects.insert_one(doc)
    return project_obj


@api_router.get("/projects")
async def get_projects(status: Optional[str] = None, client_id: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if client_id:
        query["client_id"] = client_id
    
    projects = await db.projects.find(query, {"_id": 0}).to_list(1000)
    
    # Enrich with client data
    for project in projects:
        client = await db.clients.find_one({"id": project["client_id"]}, {"_id": 0})
        if client:
            project["client"] = deserialize_doc(client)
        deserialize_doc(project)
    
    return projects


@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Zlecenie nie znalezione")
    
    # Add client data
    client = await db.clients.find_one({"id": project["client_id"]}, {"_id": 0})
    if client:
        project["client"] = deserialize_doc(client)
    
    return deserialize_doc(project)


@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    existing = await db.projects.find_one({"id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Zlecenie nie znalezione")
    
    update_data = {k: v for k, v in project_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    updated_project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return deserialize_doc(updated_project)


@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Zlecenie nie znalezione")
    return {"message": "Zlecenie usunięte pomyślnie"}


@api_router.get("/projects/stats/dashboard")
async def get_dashboard_stats():
    total_clients = await db.clients.count_documents({})
    total_projects = await db.projects.count_documents({})
    active_projects = await db.projects.count_documents({"status": "in_progress"})
    completed_projects = await db.projects.count_documents({"status": "completed"})
    
    # Calculate total hours this month from BOTH workhours (projects) AND employee work entries
    from datetime import datetime as dt
    current_month_start = dt.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    
    # Get hours from regular workhours (linked to projects)
    workhours = await db.workhours.find({"date": {"$gte": current_month_start}}, {"_id": 0}).to_list(10000)
    project_hours = sum(wh.get("hours", 0) for wh in workhours)
    
    # Get hours from employee work entries
    employee_entries = await db.employee_work_entries.find({"date": {"$gte": current_month_start}}, {"_id": 0}).to_list(10000)
    employee_hours = sum(entry.get("hours", 0) for entry in employee_entries)
    
    # Total = project hours + employee hours
    total_hours_month = project_hours + employee_hours
    
    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_hours_month": total_hours_month
    }


# ============= WORKHOURS ENDPOINTS =============

@api_router.post("/workhours", response_model=WorkHour)
async def create_workhour(workhour_input: WorkHourCreate):
    # Verify project exists
    project = await db.projects.find_one({"id": workhour_input.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Zlecenie nie znalezione")
    
    workhour_obj = WorkHour(**workhour_input.model_dump())
    doc = serialize_doc(workhour_obj.model_dump())
    await db.workhours.insert_one(doc)
    return workhour_obj


@api_router.get("/workhours")
async def get_workhours(project_id: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    query = {}
    if project_id:
        query["project_id"] = project_id
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date
    
    workhours = await db.workhours.find(query, {"_id": 0}).to_list(10000)
    
    # Enrich with project data
    for wh in workhours:
        project = await db.projects.find_one({"id": wh["project_id"]}, {"_id": 0})
        if project:
            wh["project"] = deserialize_doc(project)
        deserialize_doc(wh)
    
    return workhours


@api_router.get("/workhours/{workhour_id}", response_model=WorkHour)
async def get_workhour(workhour_id: str):
    workhour = await db.workhours.find_one({"id": workhour_id}, {"_id": 0})
    if not workhour:
        raise HTTPException(status_code=404, detail="Wpis godzin nie znaleziony")
    return deserialize_doc(workhour)


@api_router.put("/workhours/{workhour_id}", response_model=WorkHour)
async def update_workhour(workhour_id: str, workhour_update: WorkHourUpdate):
    existing = await db.workhours.find_one({"id": workhour_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Wpis godzin nie znaleziony")
    
    update_data = {k: v for k, v in workhour_update.model_dump().items() if v is not None}
    
    await db.workhours.update_one({"id": workhour_id}, {"$set": update_data})
    
    updated_workhour = await db.workhours.find_one({"id": workhour_id}, {"_id": 0})
    return deserialize_doc(updated_workhour)


@api_router.delete("/workhours/{workhour_id}")
async def delete_workhour(workhour_id: str):
    result = await db.workhours.delete_one({"id": workhour_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wpis godzin nie znaleziony")
    return {"message": "Wpis godzin usunięty pomyślnie"}


@api_router.get("/workhours/summary/stats")
async def get_workhours_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    query = {}
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date
    
    # Get workhours (project-related hours)
    workhours = await db.workhours.find(query, {"_id": 0}).to_list(10000)
    project_total_hours = sum(wh.get("hours", 0) for wh in workhours)
    project_total_entries = len(workhours)
    
    # Get employee work entries
    employee_entries = await db.employee_work_entries.find(query, {"_id": 0}).to_list(10000)
    employee_total_hours = sum(entry.get("hours", 0) for entry in employee_entries)
    employee_total_entries = len(employee_entries)
    
    # Combined totals
    total_hours = project_total_hours + employee_total_hours
    total_entries = project_total_entries + employee_total_entries
    
    # Group by project (only for workhours)
    project_hours = {}
    for wh in workhours:
        pid = wh.get("project_id")
        if pid:
            project_hours[pid] = project_hours.get(pid, 0) + wh.get("hours", 0)
    
    return {
        "total_hours": total_hours,
        "total_entries": total_entries,
        "project_hours": project_hours
    }


# ============= PHOTOS ENDPOINTS =============

@api_router.post("/photos", response_model=Photo)
async def create_photo(photo_input: PhotoCreate):
    # Verify project exists if project_id provided
    if photo_input.project_id:
        project = await db.projects.find_one({"id": photo_input.project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Zlecenie nie znalezione")
    
    photo_obj = Photo(**photo_input.model_dump())
    doc = serialize_doc(photo_obj.model_dump())
    await db.photos.insert_one(doc)
    return photo_obj


@api_router.get("/photos")
async def get_photos(project_id: Optional[str] = None):
    query = {}
    if project_id:
        query["project_id"] = project_id
    
    photos = await db.photos.find(query, {"_id": 0}).to_list(10000)
    
    # Enrich with project data
    for photo in photos:
        if photo.get("project_id"):
            project = await db.projects.find_one({"id": photo["project_id"]}, {"_id": 0})
            if project:
                photo["project"] = deserialize_doc(project)
        deserialize_doc(photo)
    
    return photos


@api_router.get("/photos/{photo_id}", response_model=Photo)
async def get_photo(photo_id: str):
    photo = await db.photos.find_one({"id": photo_id}, {"_id": 0})
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione")
    return deserialize_doc(photo)


@api_router.put("/photos/{photo_id}", response_model=Photo)
async def update_photo(photo_id: str, photo_update: PhotoUpdate):
    existing = await db.photos.find_one({"id": photo_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione")
    
    update_data = {k: v for k, v in photo_update.model_dump().items() if v is not None}
    
    await db.photos.update_one({"id": photo_id}, {"$set": update_data})
    
    updated_photo = await db.photos.find_one({"id": photo_id}, {"_id": 0})
    return deserialize_doc(updated_photo)


@api_router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: str):
    result = await db.photos.delete_one({"id": photo_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione")
    return {"message": "Zdjęcie usunięte pomyślnie"}


# ============= VOICE REPORTS =============

class DailyReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # ISO date string
    title: str  # Nazwa klienta lub tytuł
    work_description: str  # Opis wykonanych prac
    materials_used: str  # Zużyte materiały
    additional_info: str  # Dodatkowe informacje
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DailyReportCreate(BaseModel):
    date: str
    title: str
    work_description: str
    materials_used: str
    additional_info: str


class DailyReportUpdate(BaseModel):
    date: Optional[str] = None
    title: Optional[str] = None
    work_description: Optional[str] = None
    materials_used: Optional[str] = None
    additional_info: Optional[str] = None


class VoiceTranscript(BaseModel):
    transcript: str  # Tekst z Web Speech API
    command_type: str  # "work_hours" lub "daily_report"


# AI Processing with Emergent LLM Key
async def process_voice_transcript(transcript: str, command_type: str):
    """Przetwarza transkrypcję głosową za pomocą AI"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    if command_type == "work_hours":
        system_message = """Jesteś asystentem który analizuje polski tekst o godzinach pracy.
Wyciągnij z tekstu:
- Imiona i nazwiska pracowników
- Liczbę przepracowanych godzin dla każdego
- Datę (jeśli podana, inaczej dzisiejsza)

Odpowiedz w formacie JSON:
{
  "date": "2025-01-12",
  "workers": [
    {"name": "Bartosz Kowalski", "hours": 9.0},
    {"name": "Norbert Fronckow iak", "hours": 9.0}
  ]
}"""
    else:  # daily_report
        system_message = """Jesteś asystentem który analizuje polski tekst o raporcie dziennym.
Wyciągnij z tekstu:
- Nazwę klienta (tytuł)
- Opis wykonanych prac
- Zużyte materiały (lista)
- Dodatkowe informacje
- Datę (jeśli podana, inaczej dzisiejsza)

Odpowiedz w formacie JSON:
{
  "date": "2025-01-12",
  "title": "Jan Kowalski",
  "work_description": "Rozciągnięcie instalacji oświetlenia garaż, wykopanie 20m przyłącza",
  "materials_used": "Kabel 5x10 30m, Puszki 20szt, Bezpieczniki B16 8szt, Paliwo 6 litrów",
  "additional_info": "3 osoby, 9 godzin, koparka 5 godzin, podnośnik 3 godziny. Praca przebiegła bez żadnych problemów."
}"""
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"voice-{uuid.uuid4()}",
        system_message=system_message
    ).with_model("openai", "gpt-4o-mini")
    
    user_message = UserMessage(text=transcript)
    response = await chat.send_message(user_message)
    
    # Parse JSON response
    import json
    try:
        # Extract JSON from response (handle markdown code blocks)
        response_text = response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Failed to parse AI response: {e}, response: {response}")
        raise HTTPException(status_code=500, detail=f"Błąd parsowania odpowiedzi AI: {str(e)}")


@api_router.post("/voice/process")
async def process_voice(data: VoiceTranscript):
    """Przetwarza transkrypcję głosową i automatycznie zapisuje dane"""
    try:
        result = await process_voice_transcript(data.transcript, data.command_type)
        
        if data.command_type == "work_hours":
            # Automatycznie zapisz godziny pracy
            work_hours_ids = []
            for worker in result.get("workers", []):
                work_hour_data = {
                    "id": str(uuid.uuid4()),
                    "date": result.get("date", datetime.now().date().isoformat()),
                    "hours": worker["hours"],
                    "project_id": None,  # Można później przypisać
                    "worker_name": worker["name"],
                    "notes": "Dodane przez asystenta głosowego",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await db.work_hours.insert_one(work_hour_data)
                work_hours_ids.append(work_hour_data["id"])
            
            return {
                "success": True,
                "type": "work_hours",
                "data": result,
                "saved_ids": work_hours_ids
            }
        
        else:  # daily_report
            # Sprawdź czy klient istnieje w bazie
            client = await db.clients.find_one(
                {"name": {"$regex": result.get("title", ""), "$options": "i"}},
                {"_id": 0}
            )
            
            report_data = {
                "id": str(uuid.uuid4()),
                "date": result.get("date", datetime.now().date().isoformat()),
                "title": result.get("title", "Bez tytułu"),
                "work_description": result.get("work_description", ""),
                "materials_used": result.get("materials_used", ""),
                "additional_info": result.get("additional_info", ""),
                "client_id": client["id"] if client else None,
                "client_found": bool(client),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.daily_reports.insert_one(report_data)
            
            return {
                "success": True,
                "type": "daily_report",
                "data": result,
                "saved_id": report_data["id"],
                "client_found": bool(client)
            }
    
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# CRUD for Daily Reports

@api_router.get("/daily-reports", response_model=List[DailyReport])
async def get_daily_reports():
    reports = await db.daily_reports.find({}, {"_id": 0}).sort("date", -1).to_list(length=None)
    return [deserialize_doc(report) for report in reports]


@api_router.get("/daily-reports/{report_id}", response_model=DailyReport)
async def get_daily_report(report_id: str):
    report = await db.daily_reports.find_one({"id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Raport nie znaleziony")
    return deserialize_doc(report)


@api_router.post("/daily-reports", response_model=DailyReport)
async def create_daily_report(report: DailyReportCreate):
    report_data = report.model_dump()
    report_data["id"] = str(uuid.uuid4())
    report_data["created_at"] = datetime.now(timezone.utc).isoformat()
    report_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.daily_reports.insert_one(report_data)
    return deserialize_doc(report_data)


@api_router.put("/daily-reports/{report_id}", response_model=DailyReport)
async def update_daily_report(report_id: str, report: DailyReportUpdate):
    existing = await db.daily_reports.find_one({"id": report_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Raport nie znaleziony")
    
    update_data = {k: v for k, v in report.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.daily_reports.update_one({"id": report_id}, {"$set": update_data})
    
    updated_report = await db.daily_reports.find_one({"id": report_id}, {"_id": 0})
    return deserialize_doc(updated_report)


@api_router.delete("/daily-reports/{report_id}")
async def delete_daily_report(report_id: str):
    result = await db.daily_reports.delete_one({"id": report_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Raport nie znaleziony")
    return {"message": "Raport usunięty pomyślnie"}


# ============= GMAIL INTEGRATION =============

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
import gmail_service

class GmailCredentials(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: str
    token: str
    refresh_token: Optional[str] = None
    token_uri: str = "https://oauth2.googleapis.com/token"
    scopes: list = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@api_router.get("/gmail/auth/start")
async def gmail_auth_start():
    """Start Gmail OAuth flow"""
    try:
        flow = gmail_service.create_oauth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return {"authorization_url": authorization_url, "state": state}
    except Exception as e:
        logger.error(f"Error starting Gmail auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gmail/auth/callback")
async def gmail_auth_callback(request: Request):
    """Handle Gmail OAuth callback"""
    try:
        # Get the full URL with query parameters
        code = request.query_params.get('code')
        
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code provided")
        
        flow = gmail_service.create_oauth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user email from Gmail API
        service = gmail_service.get_gmail_service({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token
        })
        profile = service.users().getProfile(userId='me').execute()
        user_email = profile['emailAddress']
        
        # Save credentials to database
        credentials_data = {
            "id": str(uuid.uuid4()),
            "user_email": user_email,
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "scopes": list(credentials.scopes),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update existing or insert new
        await db.gmail_credentials.update_one(
            {"user_email": user_email},
            {"$set": credentials_data},
            upsert=True
        )
        
        # Redirect to frontend mail page
        frontend_url = os.environ.get('REACT_APP_BACKEND_URL', '').replace('/api', '')
        return RedirectResponse(url=f"{frontend_url}/mail?connected=true")
        
    except Exception as e:
        logger.error(f"Error in Gmail callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gmail/status")
async def gmail_status():
    """Check if Gmail is connected"""
    try:
        # For now, check if any credentials exist
        credentials = await db.gmail_credentials.find_one({}, {"_id": 0})
        
        if credentials:
            return {
                "connected": True,
                "email": credentials.get("user_email")
            }
        return {"connected": False}
        
    except Exception as e:
        logger.error(f"Error checking Gmail status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gmail/emails")
async def get_gmail_emails(max_results: int = 50, page_token: Optional[str] = None):
    """Get list of emails"""
    try:
        # Get credentials from database
        credentials = await db.gmail_credentials.find_one({}, {"_id": 0})
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Gmail not connected")
        
        result = await gmail_service.list_emails(credentials, max_results, page_token)
        return result
        
    except Exception as e:
        logger.error(f"Error getting emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/gmail/emails/{message_id}")
async def get_gmail_email(message_id: str):
    """Get single email"""
    try:
        credentials = await db.gmail_credentials.find_one({}, {"_id": 0})
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Gmail not connected")
        
        email = await gmail_service.get_email(credentials, message_id)
        return email
        
    except Exception as e:
        logger.error(f"Error getting email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class EmailSend(BaseModel):
    to: str
    subject: str
    body: str


@api_router.post("/gmail/send")
async def send_gmail_email(email: EmailSend):
    """Send an email"""
    try:
        credentials = await db.gmail_credentials.find_one({}, {"_id": 0})
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Gmail not connected")
        
        result = await gmail_service.send_email(
            credentials,
            email.to,
            email.subject,
            email.body
        )
        return result
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/gmail/emails/{message_id}/read")
async def mark_gmail_read(message_id: str):
    """Mark email as read"""
    try:
        credentials = await db.gmail_credentials.find_one({}, {"_id": 0})
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Gmail not connected")
        
        result = await gmail_service.mark_as_read(credentials, message_id)
        return result
        
    except Exception as e:
        logger.error(f"Error marking email as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/gmail/disconnect")
async def disconnect_gmail():
    """Disconnect Gmail"""
    try:
        result = await db.gmail_credentials.delete_many({})
        return {"success": True, "deleted_count": result.deleted_count}
    except Exception as e:
        logger.error(f"Error disconnecting Gmail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= AI ASSISTANT =============

from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()

class ChatMessage(BaseModel):
    text: str
    session_id: Optional[str] = None

class ChatHistoryQuery(BaseModel):
    session_id: str
    limit: int = 50

@api_router.post("/ai/chat")
async def ai_chat(message: ChatMessage):
    """Send message to AI Assistant and get response"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Brak klucza API dla AI")
        
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Initialize LLM Chat with Claude Sonnet 4
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="""Jesteś inteligentnym asystentem biznesowym dla elektryka prowadzącego firmę.
            
Twoja rola:
- Pomagasz w analizie finansowej i biznesowej
- Odpowiadasz na pytania o projekty, klientów, wydatki
- Doradzasz w sprawach związanych z prowadzeniem firmy elektrycznej
- Pomagasz w planowaniu i organizacji pracy

Komunikujesz się po polsku, jesteś pomocny, konkretny i profesjonalny.
Jeśli nie masz wystarczających danych, zapytaj o nie."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Create user message
        user_message = UserMessage(text=message.text)
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        # Save conversation to database
        conversation_entry = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_message": message.text,
            "ai_response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": "claude-3-7-sonnet-20250219"
        }
        
        await db.ai_conversations.insert_one(conversation_entry)
        
        return {
            "response": response,
            "session_id": session_id,
            "timestamp": conversation_entry["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd AI: {str(e)}")


@api_router.post("/ai/history")
async def get_chat_history(query: ChatHistoryQuery):
    """Get chat history for a session"""
    try:
        conversations = await db.ai_conversations.find(
            {"session_id": query.session_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(query.limit).to_list(query.limit)
        
        # Reverse to get chronological order
        conversations.reverse()
        
        return {
            "session_id": query.session_id,
            "conversations": conversations,
            "count": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/ai/history/{session_id}")
async def delete_chat_history(session_id: str):
    """Delete chat history for a session"""
    try:
        result = await db.ai_conversations.delete_many({"session_id": session_id})
        return {
            "message": f"Usunięto {result.deleted_count} wiadomości",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error deleting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= VOICE (WHISPER) =============

from fastapi import File, UploadFile
import openai
import tempfile

@api_router.post("/ai/voice-to-text")
async def voice_to_text(audio: UploadFile = File(...)):
    """Convert voice audio to text using OpenAI Whisper"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Brak klucza OpenAI API")
        
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            # Use OpenAI Whisper API
            client = openai.OpenAI(api_key=api_key)
            with open(temp_audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pl"
                )
            
            return {
                "text": transcript.text,
                "success": True
            }
            
        finally:
            # Clean up temp file
            import os as os_module
            os_module.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error in voice-to-text: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania audio: {str(e)}")


# ============= ROOT ENDPOINT =============

@api_router.get("/")
async def root():
    return {"message": "API Aplikacji dla Elektryka - Działa!"}




# ============= FINANCIAL ENTRIES ENDPOINTS =============

@api_router.post("/financial-entries", response_model=FinancialEntry)
async def create_financial_entry(entry_input: FinancialEntryCreate):
    entry_obj = FinancialEntry(**entry_input.model_dump())
    doc = serialize_doc(entry_obj.model_dump())
    await db.financial_entries.insert_one(doc)
    return entry_obj


@api_router.get("/financial-entries", response_model=List[FinancialEntry])
async def get_financial_entries(
    month: Optional[str] = None,  # Format: YYYY-MM
    category: Optional[FinancialCategory] = None
):
    query = {}
    
    if month:
        # Filter by month
        start_date = f"{month}-01"
        # Get last day of month
        from calendar import monthrange
        year, mon = map(int, month.split('-'))
        last_day = monthrange(year, mon)[1]
        end_date = f"{month}-{last_day:02d}"
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    if category:
        query["category"] = category
    
    entries = await db.financial_entries.find(query, {"_id": 0}).sort("date", -1).to_list(10000)
    return [deserialize_doc(entry) for entry in entries]


@api_router.get("/financial-entries/summary")
async def get_financial_summary(month: Optional[str] = None):
    query = {}
    
    if month:
        start_date = f"{month}-01"
        from calendar import monthrange
        year, mon = map(int, month.split('-'))
        last_day = monthrange(year, mon)[1]
        end_date = f"{month}-{last_day:02d}"
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    entries = await db.financial_entries.find(query, {"_id": 0}).to_list(10000)
    
    # Calculate summary per category
    summary = {}
    income_categories = ["invoice_sales", "cash_income"]
    
    for entry in entries:
        cat = entry.get("category")
        if cat not in summary:
            summary[cat] = {
                "category": cat,
                "total_net": 0,
                "total_gross": 0,
                "count": 0,
                "type": "income" if cat in income_categories else "expense"
            }
        
        summary[cat]["total_net"] += entry.get("amount_net", 0)
        summary[cat]["total_gross"] += entry.get("amount_gross", 0)
        summary[cat]["count"] += 1
    
    # Calculate totals
    total_income_net = sum(s["total_net"] for s in summary.values() if s["type"] == "income")
    total_income_gross = sum(s["total_gross"] for s in summary.values() if s["type"] == "income")
    total_expense_net = sum(s["total_net"] for s in summary.values() if s["type"] == "expense")
    total_expense_gross = sum(s["total_gross"] for s in summary.values() if s["type"] == "expense")
    
    return {
        "categories": list(summary.values()),
        "totals": {
            "income_net": total_income_net,
            "income_gross": total_income_gross,
            "expense_net": total_expense_net,
            "expense_gross": total_expense_gross,
            "balance_net": total_income_net - total_expense_net,
            "balance_gross": total_income_gross - total_expense_gross
        }
    }


@api_router.put("/financial-entries/{entry_id}", response_model=FinancialEntry)
async def update_financial_entry(entry_id: str, entry_update: FinancialEntryUpdate):
    existing = await db.financial_entries.find_one({"id": entry_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")
    
    update_data = {k: v for k, v in entry_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.financial_entries.update_one({"id": entry_id}, {"$set": update_data})
    
    updated_entry = await db.financial_entries.find_one({"id": entry_id}, {"_id": 0})
    return deserialize_doc(updated_entry)


@api_router.delete("/financial-entries/{entry_id}")
async def delete_financial_entry(entry_id: str):
    result = await db.financial_entries.delete_one({"id": entry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")
    return {"message": "Wpis usunięty pomyślnie"}


@api_router.post("/financial-entries/ocr")
async def create_financial_entry_with_ocr(request: dict):
    """
    Extract data from invoice image using OCR (Claude Sonnet 4 Vision)
    """
    import json
    
    try:
        category = request.get("category")
        image = request.get("image")  # base64 encoded
        date = request.get("date")
        
        if not category or not image:
            raise HTTPException(status_code=400, detail="Brak wymaganych pól: category i image")
        
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Brak klucza API")
        
        # Category name mapping
        category_names = {
            "invoice_sales": "faktura sprzedażowa",
            "invoice_purchase": "faktura zakupowa",
            "fuel": "paragon paliwa"
        }
        cat_name = category_names.get(category, "dokument")
        
        # Initialize Claude with vision
        chat = LlmChat(
            api_key=api_key,
            session_id=f"ocr_{uuid.uuid4()}",
            system_message=f"""Jesteś ekspertem w analizie faktur i paragonów. 
Twoim zadaniem jest wyciągnięcie danych z {cat_name} w języku polskim.
Zwróć TYLKO JSON bez dodatkowego tekstu."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        # Create message with image
        image_content = ImageContent(image_base64=image)
        
        user_message = UserMessage(
            text=f"""Przeanalizuj ten dokument ({cat_name}) i wyciągnij następujące dane.
Zwróć odpowiedź TYLKO w formacie JSON bez żadnego dodatkowego tekstu:

{{
  "document_number": "numer faktury/paragonu lub 'brak'",
  "date": "data w formacie YYYY-MM-DD",
  "vendor": "nazwa sprzedawcy/dostawcy",
  "buyer": "nazwa nabywcy (jeśli jest na fakturze)",
  "amount_net": kwota netto jako liczba (float),
  "amount_gross": kwota brutto jako liczba (float),
  "vat_rate": stawka VAT jako liczba (float) lub null,
  "description": "krótki opis co było kupione/sprzedane"
}}

Jeśli jakiejś wartości nie ma na dokumencie, użyj null lub "brak".
Kwoty muszą być liczbami, nie tekstem.""",
            file_contents=[image_content]
        )
        
        # Get response from Claude (async method)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        # Clean response - remove markdown if present
        cleaned_response = response.strip()
        if cleaned_response.startswith("```"):
            # Remove ```json and ``` markers
            cleaned_response = cleaned_response.split("```")[1]
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:]
        
        ocr_data = json.loads(cleaned_response.strip())
        
        # Create financial entry
        entry_data = FinancialEntryCreate(
            date=date or ocr_data.get("date") or datetime.now(timezone.utc).date().isoformat(),
            category=category,
            description=(ocr_data.get("document_number") or "brak") + " - " + (ocr_data.get("description") or ""),
            amount_net=float(ocr_data.get("amount_net") or 0),
            amount_gross=float(ocr_data.get("amount_gross") or 0),
            vat_rate=float(ocr_data.get("vat_rate")) if ocr_data.get("vat_rate") else None,
            notes=f"Dostawca: {ocr_data.get('vendor') or 'brak'}"
        )
        
        entry_obj = FinancialEntry(**entry_data.model_dump())
        doc = serialize_doc(entry_obj.model_dump())
        await db.financial_entries.insert_one(doc)
        
        return {
            "entry": entry_obj,
            "ocr_data": ocr_data
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Błąd parsowania odpowiedzi OCR: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd OCR: {str(e)}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
