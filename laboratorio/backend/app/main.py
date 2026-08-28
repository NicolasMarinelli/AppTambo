from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, fotos_referencia, resultados, tipos_analisis
from app.core.config import settings

app = FastAPI(
    title="Laboratorio",
    description=(
        "API para el personal de laboratorio del tambo: evaluación de "
        "cultivos con IA con visión (mastitis, calostro, etc.) a partir de "
        "fotos de referencia configurables por tipo de análisis. No tiene "
        "usuarios propios — reutiliza el login y los roles de tambo."
    ),
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
app.include_router(tipos_analisis.router)
app.include_router(fotos_referencia.router)
app.include_router(resultados.router)


@app.get("/health", description="Chequeo simple de disponibilidad del servicio")
def health():
    return {"status": "ok"}
