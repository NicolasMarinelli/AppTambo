"""Almacenamiento de fotos en Cloudinary — mismo proveedor que ya usa
task-verifier (ver task-verifier/backend/app/utils/storage.py), mismo
patrón: se sube el binario, se guarda solo la URL pública en la base de
datos."""

import base64

import cloudinary
import cloudinary.uploader
import httpx
from fastapi import UploadFile

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
)


async def save_photo(file: UploadFile, subfolder: str = "") -> str:
    """Sube una foto a Cloudinary y devuelve su URL pública."""
    contents = await file.read()
    folder = f"laboratorio/{subfolder}" if subfolder else "laboratorio"
    result = cloudinary.uploader.upload(contents, folder=folder, resource_type="image")
    return result["secure_url"]


def read_photo_as_base64(url: str) -> tuple[str, str]:
    """Descarga una foto (de Cloudinary) y la devuelve en base64, para
    mandarla a la API de Anthropic (que no acepta URLs directamente)."""
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    data = base64.standard_b64encode(response.content).decode("utf-8")

    url_lower = url.lower()
    if ".png" in url_lower:
        media_type = "image/png"
    elif ".webp" in url_lower:
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    return data, media_type
