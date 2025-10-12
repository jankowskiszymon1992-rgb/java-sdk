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
    
    # Calculate total hours this month
    from datetime import datetime as dt
    current_month_start = dt.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    
    workhours = await db.workhours.find({"date": {"$gte": current_month_start}}, {"_id": 0}).to_list(10000)
    total_hours_month = sum(wh.get("hours", 0) for wh in workhours)
    
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
    
    workhours = await db.workhours.find(query, {"_id": 0}).to_list(10000)
    
    total_hours = sum(wh.get("hours", 0) for wh in workhours)
    total_entries = len(workhours)
    
    # Group by project
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


# ============= ROOT ENDPOINT =============

@api_router.get("/")
async def root():
    return {"message": "API Aplikacji dla Elektryka - Działa!"}


# Gmail OAuth callback endpoint (without /api prefix to match Google Console)
@app.get("/auth/google/callback")
async def gmail_oauth_callback(request: Request):
    """Handle Gmail OAuth callback - matches Google Console redirect URI"""
    try:
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
        return RedirectResponse(url="https://elektron-dashboard.preview.emergentagent.com/mail?connected=true")
        
    except Exception as e:
        logger.error(f"Error in Gmail callback: {e}")
        return RedirectResponse(url=f"https://elektron-dashboard.preview.emergentagent.com/mail?error={str(e)}")


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
