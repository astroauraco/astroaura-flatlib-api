from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import os

app = FastAPI()

# Allow only astroaura.co for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "demo")

class NatalRequest(BaseModel):
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    lat: float
    lon: float
    tz: float  # e.g., 3.0 for GMT+3

@app.post("/natal")
def get_natal_chart(data: NatalRequest, request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    dt = Datetime(data.date, data.time, data.tz)
    pos = GeoPos(data.lat, data.lon)
    chart = Chart(dt, pos)

    result = {
        obj.id: {
            "sign": obj.sign,
            "lon": round(obj.lon, 2),
            "house": chart.houses.getHouse(obj.lon).id
        }
        for obj in chart.objects
    }
    return result
