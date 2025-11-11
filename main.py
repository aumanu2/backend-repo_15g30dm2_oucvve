import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Barber, Appointment

app = FastAPI(title="cutConnect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "cutConnect", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or ""
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# -----------------------------
# Barber Endpoints
# -----------------------------

@app.post("/api/barbers", response_model=dict)
def create_barber(barber: Barber):
    barber_id = create_document("barber", barber)
    return {"id": barber_id}

@app.get("/api/barbers", response_model=List[dict])
def list_barbers(limit: Optional[int] = 50):
    docs = get_documents("barber", limit=limit)
    # Convert ObjectIds to strings
    for d in docs:
        d["_id"] = str(d["_id"]) 
    return docs

# -----------------------------
# Appointment Endpoints
# -----------------------------

class AppointmentCreate(Appointment):
    pass

@app.post("/api/appointments", response_model=dict)
def create_appointment(appt: AppointmentCreate):
    # Basic guard: ensure referenced barber exists
    from bson import ObjectId
    try:
        barber_oid = ObjectId(appt.barber_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid barber_id")

    if db["barber"].count_documents({"_id": barber_oid}) == 0:
        raise HTTPException(status_code=404, detail="Barber not found")

    appt_id = create_document("appointment", appt)
    return {"id": appt_id}

@app.get("/api/appointments", response_model=List[dict])
def list_appointments(barber_id: Optional[str] = None, limit: Optional[int] = 50):
    q = {}
    if barber_id:
        q["barber_id"] = barber_id
    docs = get_documents("appointment", filter_dict=q, limit=limit)
    for d in docs:
        d["_id"] = str(d["_id"]) 
    return docs

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
