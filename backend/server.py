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
from datetime import datetime, timezone, date, timedelta
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


# ============= REMINDERS MODELS =============

class ReminderType(str, Enum):
    custom = "custom"  # Własne przypomnienie
    zus = "zus"  # ZUS - 18-go miesiąca
    taxes = "taxes"  # Podatki - 18-go miesiąca


class Reminder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    reminder_date: str  # Format: YYYY-MM-DD
    reminder_time: str = "09:00"  # Format: HH:MM
    reminder_type: ReminderType = ReminderType.custom
    is_recurring: bool = False  # Powtarza się co miesiąc (dla ZUS/podatków)
    is_completed: bool = False
    sent: bool = False  # Czy powiadomienie zostało wysłane
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    reminder_date: str
    reminder_time: str = "09:00"
    reminder_type: ReminderType = ReminderType.custom
    is_recurring: bool = False


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_date: Optional[str] = None
    reminder_time: Optional[str] = None
    is_completed: Optional[bool] = None


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


# ============= MARKET INTELLIGENCE MODELS =============

class SupplierName(str, Enum):
    kanlux = "kanlux"
    tme = "tme"
    conrad = "conrad"
    rs_components = "rs_components"


class ProductPrice(BaseModel):
    """Ceny produktów z różnych hurtowni"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str  # Nazwa produktu (np. "Przewód YDYp 3x1.5 mm²")
    product_category: str  # Kategoria (np. "przewody", "gniazda")
    supplier: SupplierName  # Hurtownia
    price: float  # Cena w PLN
    currency: str = "PLN"
    availability: bool = True  # Czy dostępny
    url: Optional[str] = None  # Link do produktu
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class USDRate(BaseModel):
    """Kurs dolara USD/PLN"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rate: float  # Kurs USD/PLN
    date: str  # Data w formacie YYYY-MM-DD
    source: str = "NBP"  # Źródło kursu
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScrapingLog(BaseModel):
    """Logi scrapingu"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier: SupplierName
    status: str  # "success", "failed", "partial"
    products_scraped: int = 0
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class PriceAlert(BaseModel):
    """Alerty cenowe"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    supplier: SupplierName
    old_price: float
    new_price: float
    change_percent: float  # % zmiany (np. -15.5 = spadek o 15.5%)
    alert_type: str  # "price_drop", "price_increase"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_read: bool = False


class AIReportType(str, Enum):
    daily = "daily"  # Raport dzienny
    weekly = "weekly"  # Raport tygodniowy
    on_demand = "on_demand"  # Na żądanie


class AIReport(BaseModel):
    """Raporty AI Analityka"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: AIReportType
    title: str
    summary: str  # Krótkie podsumowanie
    analysis: str  # Pełna analiza od AI
    recommendations: List[str]  # Lista rekomendacji
    predictions: List[str]  # Lista predykcji
    key_insights: List[str]  # Kluczowe wnioski
    data_snapshot: dict  # Snapshot danych na moment generowania
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIInsight(BaseModel):
    """Pojedyncze wnioski AI"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: Optional[str] = None
    insight_type: str  # "buy_now", "wait", "price_optimal", "trend_up", "trend_down"
    message: str
    confidence: float = 0.0  # 0-100%
    action_items: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


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


@api_router.get("/financial-entries/export/excel")
async def export_financial_entries_excel(month: Optional[str] = None):
    """
    Export financial entries to Excel
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    
    # Get data
    query = {}
    if month:
        start_date = f"{month}-01"
        from calendar import monthrange
        year, mon = map(int, month.split('-'))
        last_day = monthrange(year, mon)[1]
        end_date = f"{month}-{last_day:02d}"
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    entries = await db.financial_entries.find(query, {"_id": 0}).sort("date", -1).to_list(10000)
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = f"Finanse {month or 'Wszystkie'}"
    
    # Headers
    headers = ["Data", "Kategoria", "Opis", "Kwota netto (zł)", "Kwota brutto (zł)", "VAT %", "Notatki"]
    ws.append(headers)
    
    # Style headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Category names
    cat_names = {
        "invoice_sales": "Faktura sprzedażowa",
        "cash_income": "Pieniądze bez faktury",
        "invoice_purchase": "Faktura zakupowa",
        "fuel": "Paliwo",
        "salaries": "Wypłaty pracowników",
        "taxes": "Podatki",
        "zus": "ZUS",
        "equipment": "Sprzęt",
        "clothes": "Ciuchy"
    }
    
    # Add data
    for entry in entries:
        ws.append([
            entry.get("date"),
            cat_names.get(entry.get("category"), entry.get("category")),
            entry.get("description"),
            entry.get("amount_net"),
            entry.get("amount_gross"),
            entry.get("vat_rate"),
            entry.get("notes", "")
        ])
    
    # Add summary
    ws.append([])
    ws.append(["PODSUMOWANIE"])
    
    income_net = sum(e.get("amount_net", 0) for e in entries if e.get("category") in ["invoice_sales", "cash_income"])
    income_gross = sum(e.get("amount_gross", 0) for e in entries if e.get("category") in ["invoice_sales", "cash_income"])
    expense_net = sum(e.get("amount_net", 0) for e in entries if e.get("category") not in ["invoice_sales", "cash_income"])
    expense_gross = sum(e.get("amount_gross", 0) for e in entries if e.get("category") not in ["invoice_sales", "cash_income"])
    
    ws.append(["Przychody netto:", "", "", income_net])
    ws.append(["Przychody brutto:", "", "", "", income_gross])
    ws.append(["Wydatki netto:", "", "", expense_net])
    ws.append(["Wydatki brutto:", "", "", "", expense_gross])
    ws.append(["Bilans netto:", "", "", income_net - expense_net])
    ws.append(["Bilans brutto:", "", "", "", income_gross - expense_gross])
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 35
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 10
    ws.column_dimensions['G'].width = 30
    
    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    filename = f"finanse_{month or 'wszystkie'}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@api_router.get("/financial-entries/export/pdf")
async def export_financial_entries_pdf(month: Optional[str] = None):
    """
    Export financial entries to PDF
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    
    # Get data
    query = {}
    if month:
        start_date = f"{month}-01"
        from calendar import monthrange
        year, mon = map(int, month.split('-'))
        last_day = monthrange(year, mon)[1]
        end_date = f"{month}-{last_day:02d}"
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    entries = await db.financial_entries.find(query, {"_id": 0}).sort("date", -1).to_list(10000)
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20
    )
    
    # Title
    title = Paragraph(f"Raport finansowy - {month or 'Wszystkie miesiące'}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Category names
    cat_names = {
        "invoice_sales": "Faktura sprzedażowa",
        "cash_income": "Pieniądze bez faktury",
        "invoice_purchase": "Faktura zakupowa",
        "fuel": "Paliwo",
        "salaries": "Wypłaty pracowników",
        "taxes": "Podatki",
        "zus": "ZUS",
        "equipment": "Sprzęt",
        "clothes": "Ciuchy"
    }
    
    # Table data
    table_data = [["Data", "Kategoria", "Opis", "Netto (zł)", "Brutto (zł)"]]
    
    for entry in entries:
        table_data.append([
            entry.get("date"),
            cat_names.get(entry.get("category"), entry.get("category")),
            entry.get("description")[:30] + "..." if len(entry.get("description", "")) > 30 else entry.get("description", ""),
            f"{entry.get('amount_net', 0):.2f}",
            f"{entry.get('amount_gross', 0):.2f}"
        ])
    
    # Create table
    table = Table(table_data, colWidths=[60, 100, 200, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Summary
    income_net = sum(e.get("amount_net", 0) for e in entries if e.get("category") in ["invoice_sales", "cash_income"])
    income_gross = sum(e.get("amount_gross", 0) for e in entries if e.get("category") in ["invoice_sales", "cash_income"])
    expense_net = sum(e.get("amount_net", 0) for e in entries if e.get("category") not in ["invoice_sales", "cash_income"])
    expense_gross = sum(e.get("amount_gross", 0) for e in entries if e.get("category") not in ["invoice_sales", "cash_income"])
    
    summary_data = [
        ["PODSUMOWANIE", "Netto (zł)", "Brutto (zł)"],
        ["Przychody", f"{income_net:.2f}", f"{income_gross:.2f}"],
        ["Wydatki", f"{expense_net:.2f}", f"{expense_gross:.2f}"],
        ["Bilans", f"{income_net - expense_net:.2f}", f"{income_gross - expense_gross:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[150, 100, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(summary_table)
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    filename = f"finanse_{month or 'wszystkie'}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@api_router.get("/financial-entries/export/pdf")
async def export_financial_entries_pdf(month: Optional[str] = None):
    """
    Export financial entries to PDF
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    
    # Get data
    query = {}
    if month:
        start_date = f"{month}-01"
        from calendar import monthrange
        year, mon = map(int, month.split('-'))
        last_day = monthrange(year, mon)[1]
        end_date = f"{month}-{last_day:02d}"
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    entries = await db.financial_entries.find(query, {"_id": 0}).sort("date", -1).to_list(10000)
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20
    )
    
    # Title
    title = Paragraph(f"Raport finansowy - {month or 'Wszystkie miesiące'}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Category names
    cat_names = {
        "invoice_sales": "Faktura sprzedażowa",
        "cash_income": "Pieniądze bez faktury",
        "invoice_purchase": "Faktura zakupowa",
        "fuel": "Paliwo",
        "salaries": "Wypłaty pracowników",
        "taxes": "Podatki",
        "zus": "ZUS",
        "equipment": "Sprzęt",
        "clothes": "Ciuchy"
    }
    
    # Table data
    table_data = [["Data", "Kategoria", "Opis", "Netto (zł)", "Brutto (zł)"]]
    
    for entry in entries:
        table_data.append([
            entry.get("date"),
            cat_names.get(entry.get("category"), entry.get("category")),
            entry.get("description")[:30] + "..." if len(entry.get("description", "")) > 30 else entry.get("description", ""),
            f"{entry.get('amount_net', 0):.2f}",
            f"{entry.get('amount_gross', 0):.2f}"
        ])
    
    # Create table
    table = Table(table_data, colWidths=[60, 100, 200, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Summary
    income_net = sum(e.get("amount_net", 0) for e in entries if e.get("category") in ["invoice_sales", "cash_income"])
    income_gross = sum(e.get("amount_gross", 0) for e in entries if e.get("category") in ["invoice_sales", "cash_income"])
    expense_net = sum(e.get("amount_net", 0) for e in entries if e.get("category") not in ["invoice_sales", "cash_income"])
    expense_gross = sum(e.get("amount_gross", 0) for e in entries if e.get("category") not in ["invoice_sales", "cash_income"])
    
    summary_data = [
        ["PODSUMOWANIE", "Netto (zł)", "Brutto (zł)"],
        ["Przychody", f"{income_net:.2f}", f"{income_gross:.2f}"],
        ["Wydatki", f"{expense_net:.2f}", f"{expense_gross:.2f}"],
        ["Bilans", f"{income_net - expense_net:.2f}", f"{income_gross - expense_gross:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[150, 100, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(summary_table)
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    filename = f"finanse_{month or 'wszystkie'}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@api_router.get("/financial-entries/charts")
async def get_financial_charts_data(year: Optional[int] = None):
    """
    Get data for financial charts - full year (January to December)
    """
    from datetime import datetime
    from collections import defaultdict
    
    # Use current year if not specified
    if not year:
        year = datetime.now(timezone.utc).year
    
    # Calculate date range - full year
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    # Get all entries for the year
    entries = await db.financial_entries.find(
        {"date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).to_list(10000)
    
    # Aggregate by month
    monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
    category_data = defaultdict(lambda: {"income": 0, "expense": 0})
    
    income_categories = ["invoice_sales", "cash_income"]
    
    # Initialize all 12 months with 0
    for month in range(1, 13):
        month_key = f"{year}-{month:02d}"
        monthly_data[month_key] = {"income": 0, "expense": 0}
    
    for entry in entries:
        date_str = entry.get("date", "")
        month = date_str[:7]  # YYYY-MM
        category = entry.get("category")
        amount = entry.get("amount_gross", 0)
        
        # Monthly aggregation
        if category in income_categories:
            monthly_data[month]["income"] += amount
        else:
            monthly_data[month]["expense"] += amount
        
        # Category aggregation
        if category in income_categories:
            category_data[category]["income"] += amount
        else:
            category_data[category]["expense"] += amount
    
    # Convert to lists - all 12 months
    months_list = sorted(monthly_data.keys())
    monthly_chart = [
        {
            "month": m,
            "income": monthly_data[m]["income"],
            "expense": monthly_data[m]["expense"],
            "balance": monthly_data[m]["income"] - monthly_data[m]["expense"]
        }
        for m in months_list
    ]
    
    # Category names
    cat_names = {
        "invoice_sales": "Faktury sprzedażowe",
        "cash_income": "Bez faktury",
        "invoice_purchase": "Faktury zakupowe",
        "fuel": "Paliwo",
        "salaries": "Wypłaty",
        "taxes": "Podatki",
        "zus": "ZUS",
        "equipment": "Sprzęt",
        "clothes": "Ciuchy"
    }
    
    category_chart = [
        {
            "category": cat_names.get(cat, cat),
            "amount": abs(data["income"] + data["expense"]),
            "type": "income" if cat in income_categories else "expense"
        }
        for cat, data in category_data.items()
        if data["income"] + data["expense"] != 0
    ]
    
    return {
        "year": year,
        "monthly": monthly_chart,
        "by_category": category_chart
    }


@api_router.get("/financial-entries/charts")
async def get_financial_charts_data(year: Optional[int] = None):
    """
    Get data for financial charts - full year (January to December)
    """
    from datetime import datetime
    from collections import defaultdict
    
    # Use current year if not specified
    if not year:
        year = datetime.now(timezone.utc).year
    
    # Calculate date range - full year
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    # Get all entries for the year
    entries = await db.financial_entries.find(
        {"date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).to_list(10000)
    
    # Aggregate by month
    monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
    category_data = defaultdict(lambda: {"income": 0, "expense": 0})
    
    income_categories = ["invoice_sales", "cash_income"]
    
    # Initialize all 12 months with 0
    for month in range(1, 13):
        month_key = f"{year}-{month:02d}"
        monthly_data[month_key] = {"income": 0, "expense": 0}
    
    for entry in entries:
        date_str = entry.get("date", "")
        month = date_str[:7]  # YYYY-MM
        category = entry.get("category")
        amount = entry.get("amount_gross", 0)
        
        # Monthly aggregation
        if category in income_categories:
            monthly_data[month]["income"] += amount
        else:
            monthly_data[month]["expense"] += amount
        
        # Category aggregation
        if category in income_categories:
            category_data[category]["income"] += amount
        else:
            category_data[category]["expense"] += amount
    
    # Convert to lists - all 12 months
    months_list = sorted(monthly_data.keys())
    monthly_chart = [
        {
            "month": m,
            "income": monthly_data[m]["income"],
            "expense": monthly_data[m]["expense"],
            "balance": monthly_data[m]["income"] - monthly_data[m]["expense"]
        }
        for m in months_list
    ]
    
    # Category names
    cat_names = {
        "invoice_sales": "Faktury sprzedażowe",
        "cash_income": "Bez faktury",
        "invoice_purchase": "Faktury zakupowe",
        "fuel": "Paliwo",
        "salaries": "Wypłaty",
        "taxes": "Podatki",
        "zus": "ZUS",
        "equipment": "Sprzęt",
        "clothes": "Ciuchy"
    }
    
    category_chart = [
        {
            "category": cat_names.get(cat, cat),
            "amount": abs(data["income"] + data["expense"]),
            "type": "income" if cat in income_categories else "expense"
        }
        for cat, data in category_data.items()
        if data["income"] + data["expense"] != 0
    ]
    
    return {
        "year": year,
        "monthly": monthly_chart,
        "by_category": category_chart
    }


# ============= REMINDERS ENDPOINTS =============

@api_router.post("/reminders", response_model=Reminder)
async def create_reminder(reminder_input: ReminderCreate):
    reminder_obj = Reminder(**reminder_input.model_dump())
    doc = serialize_doc(reminder_obj.model_dump())
    await db.reminders.insert_one(doc)
    return reminder_obj


@api_router.get("/reminders", response_model=List[Reminder])
async def get_reminders(
    upcoming_only: bool = False,
    completed: Optional[bool] = None
):
    query = {}
    
    if completed is not None:
        query["is_completed"] = completed
    
    if upcoming_only:
        # Get reminders from today onwards
        today = datetime.now(timezone.utc).date().isoformat()
        query["reminder_date"] = {"$gte": today}
    
    reminders = await db.reminders.find(query, {"_id": 0}).sort("reminder_date", 1).to_list(1000)
    return [deserialize_doc(reminder) for reminder in reminders]


@api_router.get("/reminders/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: str):
    reminder = await db.reminders.find_one({"id": reminder_id}, {"_id": 0})
    if not reminder:
        raise HTTPException(status_code=404, detail="Przypomnienie nie znalezione")
    return deserialize_doc(reminder)


@api_router.put("/reminders/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: str, reminder_update: ReminderUpdate):
    existing = await db.reminders.find_one({"id": reminder_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Przypomnienie nie znalezione")
    
    update_data = {k: v for k, v in reminder_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.reminders.update_one({"id": reminder_id}, {"$set": update_data})
    
    updated_reminder = await db.reminders.find_one({"id": reminder_id}, {"_id": 0})
    return deserialize_doc(updated_reminder)


@api_router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str):
    result = await db.reminders.delete_one({"id": reminder_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Przypomnienie nie znalezione")
    return {"message": "Przypomnienie usunięte pomyślnie"}


@api_router.get("/reminders/check/pending")
async def check_pending_reminders():
    """
    Check for reminders that should be sent now
    Returns list of reminders ready to be sent
    """
    from datetime import datetime
    
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    current_time = now.strftime("%H:%M")
    
    # Find reminders for today that haven't been sent yet
    query = {
        "reminder_date": today,
        "sent": False,
        "is_completed": False,
        "reminder_time": {"$lte": current_time}
    }
    
    pending = await db.reminders.find(query, {"_id": 0}).to_list(100)
    
    # Mark as sent
    for reminder in pending:
        await db.reminders.update_one(
            {"id": reminder["id"]},
            {"$set": {"sent": True}}
        )
    
    return {
        "count": len(pending),
        "reminders": [deserialize_doc(r) for r in pending]
    }


@api_router.post("/reminders/setup-recurring")
async def setup_recurring_reminders():
    """
    Setup recurring reminders for ZUS and Taxes (18th of each month)
    """
    from datetime import datetime
    from calendar import monthrange
    
    current_year = datetime.now(timezone.utc).year
    
    # Create reminders for rest of the year
    created_count = 0
    
    for month in range(1, 13):
        month_str = f"{current_year}-{month:02d}"
        reminder_date = f"{current_year}-{month:02d}-18"
        
        # Check if ZUS reminder exists
        existing_zus = await db.reminders.find_one({
            "reminder_type": "zus",
            "reminder_date": reminder_date
        })
        
        if not existing_zus:
            zus_reminder = Reminder(
                title="Płatność ZUS",
                description="Przypomnienie o opłaceniu składek ZUS za poprzedni miesiąc",
                reminder_date=reminder_date,
                reminder_time="09:00",
                reminder_type=ReminderType.zus,
                is_recurring=True
            )
            await db.reminders.insert_one(serialize_doc(zus_reminder.model_dump()))
            created_count += 1
        
        # Check if Taxes reminder exists
        existing_taxes = await db.reminders.find_one({
            "reminder_type": "taxes",
            "reminder_date": reminder_date
        })
        
        if not existing_taxes:
            taxes_reminder = Reminder(
                title="Płatność Podatków",
                description="Przypomnienie o rozliczeniu podatków za poprzedni miesiąc",
                reminder_date=reminder_date,
                reminder_time="09:00",
                reminder_type=ReminderType.taxes,
                is_recurring=True
            )
            await db.reminders.insert_one(serialize_doc(taxes_reminder.model_dump()))
            created_count += 1
    
    return {
        "message": f"Utworzono {created_count} przypomnień cyklicznych",
        "year": current_year
    }


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
        
        # Convert image to PNG format and compress if needed (Claude limit: 5MB)
        import base64
        from PIL import Image
        from io import BytesIO
        
        try:
            # Decode base64 image
            img_data = base64.b64decode(image)
            original_size = len(img_data)
            
            # Open image with PIL
            img = Image.open(BytesIO(img_data))
            
            # Calculate max dimensions to stay under 5MB
            # Start with original size, then resize if needed
            max_size_bytes = 4.5 * 1024 * 1024  # 4.5 MB to be safe
            quality = 85
            max_dimension = 2048  # Start with reasonable max dimension
            
            # If image is too large, resize it
            if original_size > max_size_bytes or max(img.size) > max_dimension:
                # Calculate new dimensions maintaining aspect ratio
                ratio = min(max_dimension / img.size[0], max_dimension / img.size[1])
                if ratio < 1:  # Only resize if image is larger than max_dimension
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Try PNG first, if too large fall back to JPEG
            png_buffer = BytesIO()
            img.save(png_buffer, format='PNG', optimize=True)
            png_size = png_buffer.tell()
            
            if png_size > max_size_bytes:
                # PNG too large, use JPEG with compression
                jpeg_buffer = BytesIO()
                img.save(jpeg_buffer, format='JPEG', quality=quality, optimize=True)
                jpeg_buffer.seek(0)
                
                # Check if still too large
                while jpeg_buffer.tell() > max_size_bytes and quality > 20:
                    quality -= 10
                    jpeg_buffer = BytesIO()
                    img.save(jpeg_buffer, format='JPEG', quality=quality, optimize=True)
                    jpeg_buffer.seek(0)
                
                final_base64 = base64.b64encode(jpeg_buffer.getvalue()).decode('utf-8')
                final_size = len(jpeg_buffer.getvalue())
            else:
                # PNG is fine
                png_buffer.seek(0)
                final_base64 = base64.b64encode(png_buffer.getvalue()).decode('utf-8')
                final_size = png_size
            
            print(f"Image processed: {original_size} bytes -> {final_size} bytes ({final_size/1024/1024:.2f} MB)")
            
        except Exception as e:
            print(f"Warning: Image conversion failed: {e}")
            # Use original but this might fail if too large
            final_base64 = image
        
        # Create ImageContent with processed image
        image_content = ImageContent(image_base64=final_base64)
        
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


# ============= MARKET INTELLIGENCE ENDPOINTS =============

# Lista produktów do monitorowania (PEŁNA LISTA)
MONITORED_PRODUCTS = [
    # PRZEWODY (różne przekroje i liczba żył)
    {"name": "Przewód YDYp 2x1.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 3x1.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 3x1.5 mm² 100m", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 4x1.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 5x1.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 2x2.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 3x2.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 4x2.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 5x2.5 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 3x4 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 5x4 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 3x6 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 5x6 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 3x10 mm²", "category": "przewody", "usd_sensitive": True},
    {"name": "Przewód YDYp 5x10 mm²", "category": "przewody", "usd_sensitive": True},
    
    # GNIAZDA - Simon 10
    {"name": "Gniazdko Simon 10 pojedyncze", "category": "gniazda", "usd_sensitive": False},
    {"name": "Gniazdko Simon 10 podwójne", "category": "gniazda", "usd_sensitive": False},
    
    # GNIAZDA - Simon 54
    {"name": "Gniazdko Simon 54 pojedyncze", "category": "gniazda", "usd_sensitive": False},
    {"name": "Gniazdko Simon 54 podwójne", "category": "gniazda", "usd_sensitive": False},
    
    # GNIAZDA - Hager
    {"name": "Gniazdko Hager pojedyncze", "category": "gniazda", "usd_sensitive": False},
    {"name": "Gniazdko Hager podwójne", "category": "gniazda", "usd_sensitive": False},
    
    # NAŚWIETLACZE LED
    {"name": "Naświetlacz LED 10W", "category": "naswietlacze", "usd_sensitive": False},
    {"name": "Naświetlacz LED 20W", "category": "naswietlacze", "usd_sensitive": False},
    {"name": "Naświetlacz LED 30W", "category": "naswietlacze", "usd_sensitive": False},
    {"name": "Naświetlacz LED 50W", "category": "naswietlacze", "usd_sensitive": False},
    
    # ROZDZIELNICE
    {"name": "Rozdzielnica podtynkowa 12M", "category": "rozdzielnice", "usd_sensitive": False},
    {"name": "Rozdzielnica podtynkowa 24M", "category": "rozdzielnice", "usd_sensitive": False},
    {"name": "Rozdzielnica natynkowa 12M", "category": "rozdzielnice", "usd_sensitive": False},
    {"name": "Rozdzielnica natynkowa 24M", "category": "rozdzielnice", "usd_sensitive": False},
    
    # BEZPIECZNIKI 1-fazowe
    {"name": "Bezpiecznik B10 1P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik B16 1P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik B20 1P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik B25 1P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik C16 1P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik C25 1P", "category": "bezpieczniki", "usd_sensitive": False},
    
    # BEZPIECZNIKI 3-fazowe
    {"name": "Bezpiecznik B16 3P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik B25 3P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik C16 3P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik C25 3P", "category": "bezpieczniki", "usd_sensitive": False},
    {"name": "Bezpiecznik C32 3P", "category": "bezpieczniki", "usd_sensitive": False},
    
    # ŻARÓWKI LED
    {"name": "Żarówka LED E27 9W", "category": "zarowki", "usd_sensitive": False},
    {"name": "Żarówka LED E27 12W", "category": "zarowki", "usd_sensitive": False},
    {"name": "Żarówka LED E14 6W", "category": "zarowki", "usd_sensitive": False},
    {"name": "Żarówka LED GU10 5W", "category": "zarowki", "usd_sensitive": False},
    
    # LAMPY HERMETYCZNE
    {"name": "Lampa hermetyczna LED 18W 60cm okrągła", "category": "lampy_hermetyczne", "usd_sensitive": False},
    {"name": "Lampa hermetyczna LED 36W 120cm okrągła", "category": "lampy_hermetyczne", "usd_sensitive": False},
    {"name": "Lampa hermetyczna LED 18W 60cm kwadratowa", "category": "lampy_hermetyczne", "usd_sensitive": False},
    {"name": "Lampa hermetyczna LED 36W 120cm kwadratowa", "category": "lampy_hermetyczne", "usd_sensitive": False},
    
    # ŚWIETLÓWKI LED
    {"name": "Świetlówka LED 120cm 18W", "category": "swietlowki", "usd_sensitive": False},
    {"name": "Świetlówka LED 150cm 22W", "category": "swietlowki", "usd_sensitive": False},
    
    # PESZLE I RURKI
    {"name": "Peszel 16mm (50m)", "category": "peszle", "usd_sensitive": False},
    {"name": "Peszel 20mm (50m)", "category": "peszle", "usd_sensitive": False},
    {"name": "Peszel 25mm (50m)", "category": "peszle", "usd_sensitive": False},
    {"name": "Peszel 32mm (25m)", "category": "peszle", "usd_sensitive": False},
    {"name": "Rurka PCV 16mm (3m)", "category": "rurki", "usd_sensitive": False},
    {"name": "Rurka PCV 20mm (3m)", "category": "rurki", "usd_sensitive": False},
    {"name": "Uchwyt do rurki PCV 16mm", "category": "uchwyty", "usd_sensitive": False},
    {"name": "Kolano PCV 16mm", "category": "kolanka", "usd_sensitive": False},
    {"name": "Kolano PCV 20mm", "category": "kolanka", "usd_sensitive": False},
    
    # DRUT ODGROMOWY
    {"name": "Drut odgromowy aluminium 8mm (25m)", "category": "odgromienie", "usd_sensitive": True},
    {"name": "Uchwyt odgromowy dachowy", "category": "odgromienie", "usd_sensitive": False},
    {"name": "Uchwyt odgromowy ścienny", "category": "odgromienie", "usd_sensitive": False},
    
    # BEDNARKA
    {"name": "Bednarka 25mm (25m)", "category": "bednarka", "usd_sensitive": False},
    {"name": "Bednarka 32mm (25m)", "category": "bednarka", "usd_sensitive": False},
    
    # KOSTKI ELEKTRYCZNE
    {"name": "Kostka Wago 2-przewodowa (100szt)", "category": "kostki", "usd_sensitive": False},
    {"name": "Kostka Wago 3-przewodowa (100szt)", "category": "kostki", "usd_sensitive": False},
    {"name": "Kostka Wago 5-przewodowa (50szt)", "category": "kostki", "usd_sensitive": False},
    {"name": "Kostka Tor 3-przewodowa (100szt)", "category": "kostki", "usd_sensitive": False},
    
    # TAŚMY IZOLACYJNE
    {"name": "Taśma izolacyjna PCV czarna", "category": "tasmy", "usd_sensitive": False},
    {"name": "Taśma izolacyjna PCV kolorowa (mix)", "category": "tasmy", "usd_sensitive": False},
]


# Helper: Pobierz kurs USD z NBP API
async def fetch_usd_rate():
    """Pobiera aktualny kurs USD/PLN z API NBP"""
    try:
        import aiohttp
        url = "https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    rate = data['rates'][0]['mid']
                    date = data['rates'][0]['effectiveDate']
                    return {"rate": rate, "date": date}
                else:
                    return None
    except Exception as e:
        logger.error(f"Error fetching USD rate: {e}")
        return None


# Helper: Scraping Kanlux (Przykład - wymaga dostosowania do rzeczywistej struktury)
async def scrape_kanlux(product_name: str, search_term: str):
    """
    Scraper dla Kanlux.com
    UWAGA: To jest przykładowa implementacja. Wymaga dostosowania do rzeczywistej struktury HTML.
    """
    try:
        import aiohttp
        from bs4 import BeautifulSoup
        
        # Przykładowy URL - wymaga dostosowania
        search_url = f"https://www.kanlux.com/pl/search?q={search_term.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # TODO: Dostosować selektory do rzeczywistej struktury Kanlux
                    # To jest placeholder - wymaga analizy HTML strony
                    price_element = soup.select_one('.product-price, .price')
                    
                    if price_element:
                        price_text = price_element.get_text(strip=True)
                        # Ekstrakcja ceny (usuń "PLN", "zł", spacje, przecinki)
                        import re
                        price_match = re.search(r'(\d+[,.]?\d*)', price_text.replace(',', '.'))
                        if price_match:
                            price = float(price_match.group(1))
                            return {
                                "price": price,
                                "url": search_url,
                                "availability": True
                            }
        
        return None
    except Exception as e:
        logger.error(f"Kanlux scraping error for {product_name}: {e}")
        return None


# Helper: Scraping TME (Placeholder)
async def scrape_tme(product_name: str, search_term: str):
    """Scraper dla TME.eu - Placeholder"""
    # TODO: Implementacja scrapingu TME
    logger.info(f"TME scraping not implemented yet for: {product_name}")
    return None


# Helper: Scraping Conrad (Placeholder)
async def scrape_conrad(product_name: str, search_term: str):
    """Scraper dla Conrad.pl - Placeholder"""
    # TODO: Implementacja scrapingu Conrad
    logger.info(f"Conrad scraping not implemented yet for: {product_name}")
    return None


# Helper: Scraping RS Components (Placeholder)
async def scrape_rs_components(product_name: str, search_term: str):
    """Scraper dla RS Components - Placeholder"""
    # TODO: Implementacja scrapingu RS Components
    logger.info(f"RS Components scraping not implemented yet for: {product_name}")
    return None


# Mapa scraperów
SCRAPERS = {
    "kanlux": scrape_kanlux,
    "tme": scrape_tme,
    "conrad": scrape_conrad,
    "rs_components": scrape_rs_components
}


@api_router.post("/market-intelligence/scrape")
async def trigger_scraping(supplier: Optional[str] = None):
    """
    Ręczne uruchomienie scrapingu cen
    supplier: opcjonalnie - nazwa hurtowni (kanlux, tme, conrad, rs_components)
    """
    results = []
    suppliers_to_scrape = [supplier] if supplier else list(SCRAPERS.keys())
    
    for supp in suppliers_to_scrape:
        if supp not in SCRAPERS:
            continue
            
        log_entry = {
            "id": str(uuid.uuid4()),
            "supplier": supp,
            "status": "started",
            "products_scraped": 0,
            "started_at": datetime.now(timezone.utc)
        }
        
        try:
            scraper_func = SCRAPERS[supp]
            products_scraped = 0
            
            for product in MONITORED_PRODUCTS:
                # Automatyczne generowanie search term z nazwy produktu
                product_name = product["name"]
                search_term = product.get("search_terms", {}).get(supp, product_name.lower())
                
                scrape_result = await scraper_func(product_name, search_term)
                
                if scrape_result and scrape_result.get("price"):
                    # Zapisz cenę do bazy
                    price_doc = {
                        "id": str(uuid.uuid4()),
                        "product_name": product["name"],
                        "product_category": product["category"],
                        "supplier": supp,
                        "price": scrape_result["price"],
                        "currency": "PLN",
                        "availability": scrape_result.get("availability", True),
                        "url": scrape_result.get("url"),
                        "scraped_at": datetime.now(timezone.utc),
                        "created_at": datetime.now(timezone.utc)
                    }
                    await db.product_prices.insert_one(price_doc)
                    products_scraped += 1
            
            log_entry["status"] = "success"
            log_entry["products_scraped"] = products_scraped
            log_entry["completed_at"] = datetime.now(timezone.utc)
            log_entry["duration_seconds"] = (log_entry["completed_at"] - log_entry["started_at"]).total_seconds()
            
        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["error_message"] = str(e)
            log_entry["completed_at"] = datetime.now(timezone.utc)
            log_entry["duration_seconds"] = (log_entry["completed_at"] - log_entry["started_at"]).total_seconds()
        
        # Zapisz log
        await db.scraping_logs.insert_one(log_entry)
        results.append(log_entry)
    
    return {"results": results, "total_suppliers": len(results)}


@api_router.get("/market-intelligence/usd-rate")
async def get_usd_rate_current():
    """Pobierz aktualny kurs USD/PLN"""
    usd_data = await fetch_usd_rate()
    
    if usd_data:
        # Sprawdź czy już mamy dzisiaj kurs
        existing = await db.usd_rates.find_one(
            {"date": usd_data["date"]},
            {"_id": 0}
        )
        
        if existing:
            return existing
        
        # Zapisz do bazy
        rate_obj = USDRate(
            rate=usd_data["rate"],
            date=usd_data["date"],
            source="NBP"
        )
        rate_doc = serialize_doc(rate_obj.model_dump())
        await db.usd_rates.insert_one(rate_doc)
        
        return rate_obj.model_dump()
    else:
        raise HTTPException(status_code=500, detail="Nie udało się pobrać kursu USD")


@api_router.get("/market-intelligence/usd-rate/history")
async def get_usd_rate_history(days: int = 30):
    """Historia kursu USD za ostatnie N dni"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    rates = await db.usd_rates.find(
        {"created_at": {"$gte": cutoff_date}},
        {"_id": 0}
    ).sort("date", -1).to_list(1000)
    
    return {"rates": rates, "count": len(rates)}


@api_router.get("/market-intelligence/prices/compare")
async def compare_prices(product_name: Optional[str] = None):
    """Porównanie cen produktu między hurtowniami"""
    query = {}
    if product_name:
        query["product_name"] = product_name
    
    # Pobierz najnowsze ceny dla każdego produktu i hurtowni
    pipeline = [
        {"$match": query},
        {"$sort": {"scraped_at": -1}},
        {
            "$group": {
                "_id": {"product_name": "$product_name", "supplier": "$supplier"},
                "latest_price": {"$first": "$price"},
                "latest_scraped": {"$first": "$scraped_at"},
                "url": {"$first": "$url"},
                "availability": {"$first": "$availability"}
            }
        },
        {
            "$group": {
                "_id": "$_id.product_name",
                "prices": {
                    "$push": {
                        "supplier": "$_id.supplier",
                        "price": "$latest_price",
                        "scraped_at": "$latest_scraped",
                        "url": "$url",
                        "availability": "$availability"
                    }
                }
            }
        }
    ]
    
    results = await db.product_prices.aggregate(pipeline).to_list(1000)
    
    # Dodaj analizę
    for result in results:
        prices_list = [p["price"] for p in result["prices"] if p.get("availability", True)]
        if prices_list:
            result["min_price"] = min(prices_list)
            result["max_price"] = max(prices_list)
            result["avg_price"] = sum(prices_list) / len(prices_list)
            result["price_spread"] = result["max_price"] - result["min_price"]
            result["spread_percent"] = (result["price_spread"] / result["min_price"] * 100) if result["min_price"] > 0 else 0
    
    return {"products": results, "count": len(results)}


@api_router.get("/market-intelligence/prices/history")
async def get_price_history(product_name: str, days: int = 30):
    """Historia cen produktu za ostatnie N dni"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    prices = await db.product_prices.find(
        {
            "product_name": product_name,
            "scraped_at": {"$gte": cutoff_date}
        },
        {"_id": 0}
    ).sort("scraped_at", 1).to_list(10000)
    
    return {"product_name": product_name, "prices": prices, "count": len(prices)}


@api_router.get("/market-intelligence/alerts")
async def get_price_alerts(limit: int = 50):
    """Pobierz ostatnie alerty cenowe"""
    alerts = await db.price_alerts.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"alerts": alerts, "count": len(alerts)}


@api_router.get("/market-intelligence/logs")
async def get_scraping_logs(limit: int = 20):
    """Historia logów scrapingu"""
    logs = await db.scraping_logs.find(
        {},
        {"_id": 0}
    ).sort("started_at", -1).limit(limit).to_list(limit)
    
    return {"logs": logs, "count": len(logs)}


@api_router.get("/market-intelligence/dashboard")
async def get_market_dashboard():
    """Dashboard - podsumowanie danych rynkowych"""
    # Najnowszy kurs USD
    latest_usd = await db.usd_rates.find_one(
        {},
        {"_id": 0},
        sort=[("date", -1)]
    )
    
    # Liczba monitorowanych produktów
    products_count = len(MONITORED_PRODUCTS)
    
    # Ostatni scraping
    last_scraping = await db.scraping_logs.find_one(
        {},
        {"_id": 0},
        sort=[("started_at", -1)]
    )
    
    # Liczba alertów nieprzeczytanych
    unread_alerts = await db.price_alerts.count_documents({"is_read": False})
    
    # Porównanie cen (wszystkie produkty)
    price_comparison = await compare_prices()
    
    return {
        "usd_rate": latest_usd,
        "monitored_products": products_count,
        "last_scraping": last_scraping,
        "unread_alerts": unread_alerts,
        "price_comparison": price_comparison
    }


# ============= AI ANALYST ENDPOINTS =============

async def generate_ai_analysis(price_data: dict, usd_data: dict):
    """
    Generuje analizę AI na podstawie danych cenowych i kursu USD
    Używa Emergent LLM (Claude Sonnet 4)
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Przygotuj dane do analizy
        products_summary = []
        for product in price_data.get("products", []):
            prod_info = {
                "nazwa": product.get("_id"),
                "cena_min": product.get("min_price"),
                "cena_max": product.get("max_price"),
                "średnia": product.get("avg_price"),
                "rozpiętość": f"{product.get('spread_percent', 0):.1f}%",
                "ceny": product.get("prices", [])
            }
            products_summary.append(prod_info)
        
        # Prompt dla AI
        prompt = f"""Jesteś ekspertem ds. analizy rynku artykułów elektrycznych. 
Przeanalizuj poniższe dane i wygeneruj szczegółowy raport.

DANE RYNKOWE:
- Kurs USD/PLN: {usd_data.get('rate', 0):.4f} ({usd_data.get('date', 'N/A')})
- Liczba monitorowanych produktów: {len(products_summary)}

CENY PRODUKTÓW:
{products_summary}

ZADANIE:
1. Przeanalizuj ceny i znajdź najlepsze okazje
2. Porównaj ceny między hurtowniami
3. Oceń wpływ kursu USD na ceny przewodów
4. Wygeneruj 3-5 konkretnych rekomendacji
5. Podaj 2-3 predykcje cenowe
6. Wskaż kluczowe wnioski (3-5 punktów)

FORMAT ODPOWIEDZI (JSON):
{{
  "podsumowanie": "Krótkie podsumowanie sytuacji rynkowej (2-3 zdania)",
  "analiza": "Szczegółowa analiza każdego produktu i dostawcy (akapity)",
  "rekomendacje": ["Rekomendacja 1", "Rekomendacja 2", ...],
  "predykcje": ["Predykcja 1", "Predykcja 2", ...],
  "kluczowe_wnioski": ["Wniosek 1", "Wniosek 2", ...]
}}

Pisz KONKRETNIE, z liczbami i nazwami. Po polsku."""

        # Wywołaj AI
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        if not llm_key:
            return {"error": "Brak klucza EMERGENT_LLM_KEY"}
        
        # Użyj LlmChat z Emergent Integrations
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"market-analysis-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            system_message="Jesteś ekspertem ds. analizy rynku artykułów elektrycznych. Generujesz szczegółowe raporty w języku polskim z konkretnymi liczbami i nazwami."
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parsuj odpowiedź
        import json
        ai_response = response  # response jest już tekstem z LlmChat
        
        # Spróbuj wyciągnąć JSON z odpowiedzi
        try:
            # Znajdź JSON w odpowiedzi (może być w markdown code block)
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = ai_response.strip()
            
            analysis_data = json.loads(json_str)
        except:
            # Fallback - jeśli nie ma JSON, użyj całej odpowiedzi
            analysis_data = {
                "podsumowanie": "Analiza dostępna poniżej",
                "analiza": ai_response,
                "rekomendacje": ["Zobacz pełną analizę"],
                "predykcje": ["Brak predykcji"],
                "kluczowe_wnioski": ["Zobacz pełną analizę"]
            }
        
        return analysis_data
        
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return {
            "error": str(e),
            "podsumowanie": "Błąd generowania analizy",
            "analiza": f"Wystąpił błąd: {str(e)}",
            "rekomendacje": [],
            "predykcje": [],
            "kluczowe_wnioski": []
        }


@api_router.post("/ai-analyst/generate-report")
async def generate_ai_report(report_type: str = "on_demand"):
    """Generuj nowy raport AI"""
    
    # Pobierz aktualne dane
    price_data = await compare_prices()
    
    usd_rate = await db.usd_rates.find_one(
        {},
        {"_id": 0},
        sort=[("date", -1)]
    )
    
    if not usd_rate:
        raise HTTPException(status_code=404, detail="Brak danych o kursie USD")
    
    # Generuj analizę AI
    ai_analysis = await generate_ai_analysis(price_data, usd_rate)
    
    if "error" in ai_analysis:
        raise HTTPException(status_code=500, detail=f"Błąd AI: {ai_analysis['error']}")
    
    # Utwórz raport
    report = AIReport(
        report_type=report_type,
        title=f"Raport AI - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        summary=ai_analysis.get("podsumowanie", ""),
        analysis=ai_analysis.get("analiza", ""),
        recommendations=ai_analysis.get("rekomendacje", []),
        predictions=ai_analysis.get("predykcje", []),
        key_insights=ai_analysis.get("kluczowe_wnioski", []),
        data_snapshot={
            "usd_rate": usd_rate,
            "price_comparison": price_data
        }
    )
    
    # Zapisz do bazy
    report_doc = serialize_doc(report.model_dump())
    await db.ai_reports.insert_one(report_doc)
    
    return report.model_dump()


@api_router.get("/ai-analyst/reports")
async def get_ai_reports(limit: int = 10):
    """Pobierz ostatnie raporty AI"""
    reports = await db.ai_reports.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"reports": reports, "count": len(reports)}


@api_router.get("/ai-analyst/reports/{report_id}")
async def get_ai_report(report_id: str):
    """Pobierz konkretny raport"""
    report = await db.ai_reports.find_one(
        {"id": report_id},
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Raport nie znaleziony")
    
    return report


@api_router.get("/ai-analyst/insights")
async def get_current_insights():
    """Pobierz aktualne wnioski AI (krótkie, szybkie)"""
    
    # Pobierz ostatni raport
    latest_report = await db.ai_reports.find_one(
        {},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    
    if not latest_report:
        return {"insights": [], "message": "Brak raportów. Wygeneruj pierwszy raport."}
    
    # Zwróć kluczowe wnioski z ostatniego raportu
    insights = []
    for idx, insight in enumerate(latest_report.get("key_insights", [])):
        insights.append({
            "id": f"insight-{idx}",
            "message": insight,
            "created_at": latest_report.get("created_at")
        })
    
    return {
        "insights": insights,
        "report_id": latest_report.get("id"),
        "report_date": latest_report.get("created_at")
    }


@api_router.post("/ai-analyst/trend-analysis")
async def analyze_price_trends():
    """
    Drugi AI Agent (GPT-5) - Analiza trendów cenowych
    Pokazuje co drożeje, co tanieje, rekomendacje KUP/CZEKAJ
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Pobierz dane cenowe
        price_data = await compare_prices()
        
        # Pobierz historię USD (ostatnie 7 dni)
        usd_history = await db.usd_rates.find({}, {"_id": 0}).sort("date", -1).limit(7).to_list(7)
        
        usd_trend = "stabilny"
        usd_change = 0
        if len(usd_history) >= 2:
            current = usd_history[0]["rate"]
            week_ago = usd_history[-1]["rate"]
            usd_change = ((current - week_ago) / week_ago) * 100
            
            if usd_change > 2:
                usd_trend = "rośnie"
            elif usd_change < -2:
                usd_trend = "spada"
        
        # Przygotuj dane dla AI
        products_summary = []
        for product in price_data.get("products", []):
            if product.get("prices"):
                products_summary.append({
                    "nazwa": product.get("_id"),
                    "cena_min": product.get("min_price"),
                    "cena_max": product.get("max_price"),
                    "rozpiętość": f"{product.get('spread_percent', 0):.1f}%",
                    "najtańszy": next((p["supplier"] for p in product["prices"] if p["price"] == product.get("min_price")), "N/A")
                })
        
        prompt = f"""Jesteś ekspertem analizy trendów cenowych artykułów elektrycznych.

DANE:
- Kurs USD/PLN: {usd_history[0]['rate'] if usd_history else 'N/A':.4f} (trend: {usd_trend}, zmiana 7 dni: {usd_change:+.2f}%)
- Liczba produktów: {len(products_summary)}

PRODUKTY:
{products_summary[:20]}  

ZADANIE:
Dla KAŻDEGO produktu oceń:
1. Czy KUPIĆ TERAZ czy CZEKAĆ?
2. Trend: DROŻEJE / TANIEJE / STABILNY
3. Krótkie uzasadnienie (1 zdanie)

FORMAT (JSON):
{{
  "podsumowanie": "Ogólna sytuacja rynkowa (2-3 zdania)",
  "produkty": [
    {{
      "nazwa": "Przewód YDYp 3x1.5 mm²",
      "rekomendacja": "KUP_TERAZ" lub "CZEKAJ",
      "trend": "DROŻEJE" lub "TANIEJE" lub "STABILNY",
      "uzasadnienie": "Krótkie uzasadnienie",
      "confidence": 85
    }}
  ],
  "kluczowe_wnioski": ["Wniosek 1", "Wniosek 2", "Wniosek 3"]
}}

Pisz KONKRETNIE. Po polsku."""

        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        if not llm_key:
            return {"error": "Brak EMERGENT_LLM_KEY"}
        
        # Użyj GPT-5 do analizy trendów
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"trend-analysis-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            system_message="Jesteś ekspertem analizy trendów cenowych. Dajesz konkretne rekomendacje KUP/CZEKAJ."
        ).with_model("openai", "gpt-5")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parsuj JSON
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            analysis = json.loads(json_str)
        except:
            analysis = {
                "podsumowanie": response[:200],
                "produkty": [],
                "kluczowe_wnioski": ["Błąd parsowania odpowiedzi AI"]
            }
        
        # Zapisz analizę
        analysis_doc = {
            "id": str(uuid.uuid4()),
            "analysis_type": "trend_analysis",
            "summary": analysis.get("podsumowanie", ""),
            "products": analysis.get("produkty", []),
            "key_insights": analysis.get("kluczowe_wnioski", []),
            "usd_rate": usd_history[0] if usd_history else None,
            "usd_trend": usd_trend,
            "usd_change_7d": usd_change,
            "created_at": datetime.now(timezone.utc)
        }
        analysis_doc = serialize_doc(analysis_doc)
        await db.trend_analyses.insert_one(analysis_doc)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Trend analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd analizy trendów: {str(e)}")


@api_router.get("/ai-analyst/latest-trend-analysis")
async def get_latest_trend_analysis():
    """Pobierz ostatnią analizę trendów"""
    analysis = await db.trend_analyses.find_one(
        {},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    
    if not analysis:
        return {"message": "Brak analiz. Wygeneruj pierwszą analizę."}
    
    return analysis


@api_router.post("/ai-analyst/chat")
async def chat_with_gpt5(message: str, session_id: Optional[str] = None):
    """
    Chat z GPT-5 - zadawaj pytania o produkty, ceny, trendy
    PEŁNY DOSTĘP do wszystkich danych i kontroli systemu
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # ==== PEŁNY DOSTĘP DO BAZY DANYCH ====
        
        # 1. WSZYSTKIE ceny produktów (nie tylko top 30)
        all_prices = await db.product_prices.find({}, {"_id": 0}).sort("scraped_at", -1).limit(500).to_list(500)
        
        # Grupuj po produktach
        products_prices = {}
        for price in all_prices:
            prod_name = price.get("product_name")
            if prod_name not in products_prices:
                products_prices[prod_name] = []
            products_prices[prod_name].append({
                "supplier": price.get("supplier"),
                "price": price.get("price"),
                "date": price.get("scraped_at")
            })
        
        # 2. Historia USD (ostatnie 30 dni)
        usd_history = await db.usd_rates.find({}, {"_id": 0}).sort("date", -1).limit(30).to_list(30)
        usd_current = usd_history[0] if usd_history else None
        
        # 3. Logi botów scrapujących
        scraping_logs = await db.scraping_logs.find({}, {"_id": 0}).sort("started_at", -1).limit(20).to_list(20)
        
        # 4. Ostatnie analizy trendów
        trend_analyses = await db.trend_analyses.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
        
        # 5. Ostatnie raporty AI
        ai_reports = await db.ai_reports.find({}, {"_id": 0}).sort("created_at", -1).limit(3).to_list(3)
        
        # ==== PRZYGOTUJ ROZSZERZONY KONTEKST ====
        
        products_summary = []
        for prod_name, prices in products_prices.items():
            if prices:
                prices_vals = [p["price"] for p in prices]
                products_summary.append({
                    "nazwa": prod_name,
                    "cena_min": min(prices_vals),
                    "cena_max": max(prices_vals),
                    "liczba_ofert": len(prices),
                    "dostawcy": [p["supplier"] for p in prices],
                    "najtańszy": next((p["supplier"] for p in prices if p["price"] == min(prices_vals)), "N/A")
                })
        
        # Status botów
        bot_status = []
        for log in scraping_logs[:5]:
            bot_status.append({
                "supplier": log.get("supplier"),
                "status": log.get("status"),
                "products_scraped": log.get("products_scraped", 0),
                "czas": log.get("started_at"),
                "błąd": log.get("error_message")
            })
        
        # Trend USD
        usd_trend = "stabilny"
        if len(usd_history) >= 7:
            current = usd_history[0]["rate"]
            week_ago = usd_history[6]["rate"]
            change = ((current - week_ago) / week_ago) * 100
            if change > 2:
                usd_trend = f"rośnie ({change:+.1f}% w tyg.)"
            elif change < -2:
                usd_trend = f"spada ({change:+.1f}% w tyg.)"
        
        context = f"""=== PEŁNY DOSTĘP DO SYSTEMU MARKET INTELLIGENCE ===

🔍 BAZA DANYCH (Ostatnie 500 wpisów):
- Liczba produktów: {len(products_summary)}
- Liczba zapisanych cen: {len(all_prices)}
- Produkty z cenami: {len([p for p in products_summary if p['liczba_ofert'] > 0])}

💰 CENY PRODUKTÓW (WSZYSTKIE):
{products_summary}

📊 KURS USD/PLN:
- Aktualny: {usd_current['rate'] if usd_current else 'N/A'} ({usd_current['date'] if usd_current else 'N/A'})
- Trend: {usd_trend}
- Historia 30 dni dostępna

🤖 STATUS BOTÓW SCRAPUJĄCYCH:
{bot_status}

📈 OSTATNIE ANALIZY:
- Liczba analiz trendów: {len(trend_analyses)}
- Liczba raportów AI: {len(ai_reports)}

🎯 MONITOROWANE PRODUKTY (definicja):
- Łącznie: {len(MONITORED_PRODUCTS)}
- Kategorie: przewody, gniazda, naświetlacze, rozdzielnice, bezpieczniki, żarówki, lampy, świetlówki, peszle, rurki, odgromienie, bednarka, kostki, taśmy

📋 MOŻLIWOŚCI:
- Możesz analizować wszystkie dane
- Możesz sprawdzić status botów
- Możesz polecić uruchomienie scrapingu (powiedz "uruchom scraping dla [dostawca]")
- Możesz analizować trendy historyczne

INSTRUKCJA:
Odpowiadaj KONKRETNIE z danymi. Jeśli użytkownik pyta o cenę - podaj DOKŁADNĄ wartość z bazy.
Jeśli nie ma danych o produkcie - powiedz "Brak danych w bazie, uruchomić scraping?"""

        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        if not llm_key:
            return {"error": "Brak EMERGENT_LLM_KEY"}
        
        # Utwórz lub użyj istniejącej sesji
        if not session_id:
            session_id = f"chat-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # ==== WYKRYJ POLECENIA KONTROLI ====
        command_detected = None
        if "uruchom scraping" in message.lower() or "pobierz ceny" in message.lower():
            # Wykryj dostawcę
            suppliers_map = {
                "kanlux": "kanlux",
                "tme": "tme", 
                "conrad": "conrad",
                "rs": "rs_components",
                "wszystkie": None
            }
            for keyword, supplier in suppliers_map.items():
                if keyword in message.lower():
                    command_detected = {"action": "scrape", "supplier": supplier}
                    break
        
        chat = LlmChat(
            api_key=llm_key,
            session_id=session_id,
            system_message=f"""Jesteś GŁÓWNYM AGENTEM KONTROLNYM systemu Market Intelligence dla sklepu elektrycznego.

{context}

TWOJE MOŻLIWOŚCI:
1. Analizujesz WSZYSTKIE dane z bazy (ceny, trendy, historię)
2. Kontrolujesz działanie botów scrapujących
3. Rekomenujesz akcje (np. "uruchom scraping dla Kanlux")
4. Dajesz KONKRETNE ceny i porównania
5. Analizujesz efektywność operacji

SPOSÓB ODPOWIEDZI:
- KRÓTKO (2-5 zdań)
- Z KONKRETNYMI DANYMI (ceny, %, dostawcy)
- AKCJE jeśli potrzeba (np. "Brak danych - pobieram ceny z Kanlux...")
- Po POLSKU
- Jak szef analityki rynkowej

PRZYKŁAD:
User: "Jaka cena YDYP 3x1.5 100m?"
You: "W bazie mam 3 oferty: Kanlux 245 PLN netto, TME 268 PLN, Conrad 289 PLN. Najtaniej Kanlux. Ostatni scraping: 2 dni temu. Polecam kupić teraz - trend stabilny."

Jeśli brak danych - zaproponuj uruchomienie scrapingu."""
        ).with_model("openai", "gpt-5")
        
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        # ==== WYKONAJ POLECENIE JEŚLI WYKRYTE ====
        action_result = None
        if command_detected:
            if command_detected["action"] == "scrape":
                try:
                    # Uruchom scraping w tle
                    import asyncio
                    supplier = command_detected.get("supplier")
                    # Nie czekamy na wynik - scraping działa w tle
                    asyncio.create_task(trigger_scraping(supplier))
                    action_result = f"✅ Uruchomiono scraping dla {supplier or 'wszystkich dostawców'}"
                except Exception as e:
                    action_result = f"❌ Błąd uruchamiania scrapingu: {str(e)}"
        
        # Zapisz do historii
        chat_entry = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_message": message,
            "ai_response": response,
            "action_detected": command_detected,
            "action_result": action_result,
            "created_at": datetime.now(timezone.utc)
        }
        chat_entry = serialize_doc(chat_entry)
        await db.ai_chat_history.insert_one(chat_entry)
        
        # Dodaj info o akcji do odpowiedzi
        final_response = response
        if action_result:
            final_response = f"{response}\n\n{action_result}"
        
        return {
            "response": final_response,
            "session_id": session_id,
            "action_executed": action_result
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd czatu: {str(e)}")


@api_router.get("/ai-analyst/chat/history")
async def get_chat_history(session_id: str, limit: int = 50):
    """Pobierz historię czatu"""
    history = await db.ai_chat_history.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("created_at", 1).limit(limit).to_list(limit)
    
    return {"history": history, "count": len(history)}


@api_router.get("/ai-analyst/comparison-table")
async def get_comparison_table():
    """
    Tabela porównawcza z obliczeniami dla AI Analityka
    Zawiera więcej metryk niż podstawowe porównanie
    """
    
    price_data = await compare_prices()
    
    usd_rate = await db.usd_rates.find_one(
        {},
        {"_id": 0},
        sort=[("date", -1)]
    )
    
    # Pobierz historię USD (ostatnie 7 dni)
    usd_history = await db.usd_rates.find(
        {},
        {"_id": 0}
    ).sort("date", -1).limit(7).to_list(7)
    
    usd_trend = "stable"
    if len(usd_history) >= 2:
        current = usd_history[0]["rate"]
        week_ago = usd_history[-1]["rate"]
        change = ((current - week_ago) / week_ago) * 100
        
        if change > 2:
            usd_trend = "rising"
        elif change < -2:
            usd_trend = "falling"
    
    # Wzbogać dane o dodatkowe obliczenia
    enriched_products = []
    for product in price_data.get("products", []):
        if not product.get("prices"):
            continue
        
        # Oblicz oszczędność przy zakupie od najtańszego
        min_price = product.get("min_price", 0)
        max_price = product.get("max_price", 0)
        savings_percent = ((max_price - min_price) / max_price * 100) if max_price > 0 else 0
        savings_amount = max_price - min_price
        
        # Znajdź najtańszego dostawcę
        cheapest_supplier = None
        for price in product["prices"]:
            if price["price"] == min_price:
                cheapest_supplier = price["supplier"]
                break
        
        # Oceń konkurencyjność
        competitiveness = "high" if savings_percent > 10 else "medium" if savings_percent > 5 else "low"
        
        enriched_products.append({
            **product,
            "cheapest_supplier": cheapest_supplier,
            "savings_percent": round(savings_percent, 2),
            "savings_amount": round(savings_amount, 2),
            "competitiveness": competitiveness,
            "usd_sensitive": "przewód" in product["_id"].lower()  # Przewody są wrażliwe na USD
        })
    
    return {
        "products": enriched_products,
        "usd_rate": usd_rate,
        "usd_trend": usd_trend,
        "usd_change_7d": round(((usd_history[0]["rate"] - usd_history[-1]["rate"]) / usd_history[-1]["rate"] * 100), 2) if len(usd_history) >= 2 else 0,
        "total_products": len(enriched_products)
    }


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
