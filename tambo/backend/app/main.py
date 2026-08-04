from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import animals, auth, calf_records, users
from app.core.config import settings

app = FastAPI(
    title="Gestión de Nacimientos de Terneros",
    description="API para registrar partos, asignar caravana/SENASA y controlar el calostrado.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(animals.router)
app.include_router(calf_records.router)


@app.get("/health", description="Chequeo simple de disponibilidad del servicio")
def health():
    return {"status": "ok"}
