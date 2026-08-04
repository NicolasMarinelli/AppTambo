import cloudinary
import cloudinary.uploader
import cloudinary.api
import base64
import httpx
from app.config import settings

# Configurar Cloudinary al importar
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


async def save_photo(file, subfolder: str = "") -> str:
    """
    Sube una foto a Cloudinary y retorna la URL pública.
    Reemplaza el guardado local anterior.
    """
    contents = await file.read()

    folder = f"task-verifier/{subfolder}" if subfolder else "task-verifier"

    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type="image",
    )

    return result["secure_url"]


def read_photo_as_base64(url: str) -> tuple[str, str]:
    """
    Descarga una foto desde Cloudinary y la retorna como base64.
    Necesario para enviarla a la API de Anthropic.
    """
    response = httpx.get(url)
    response.raise_for_status()

    data = base64.standard_b64encode(response.content).decode("utf-8")

    # Determinar media type desde la URL
    url_lower = url.lower()
    if ".png" in url_lower:
        media_type = "image/png"
    elif ".webp" in url_lower:
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    return data, media_type