from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import auth, checklists, asignaciones, usuarios, operario, notificaciones, admin
import os


app = FastAPI(
    title="Task Verifier API",
    description="Sistema de verificacion de tareas con IA",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(checklists.router, prefix="/api/v1/checklists", tags=["Checklists"])
app.include_router(asignaciones.router, prefix="/api/v1/checklists", tags=["Asignaciones"])
app.include_router(usuarios.router, prefix="/api/v1/usuarios", tags=["Usuarios"])
app.include_router(operario.router, prefix="/api/v1/operario", tags=["Operario"])
app.include_router(notificaciones.router, prefix="/api/v1/notificaciones", tags=["Notificaciones"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])



@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }

