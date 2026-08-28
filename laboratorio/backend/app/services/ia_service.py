"""Evaluación de muestras con Claude (visión) — mismo proveedor que ya usa
task-verifier (ver task-verifier/backend/app/services/ia_service.py) y
mismo patrón general: nada de fine-tuning ni entrenamiento propio. En cada
análisis se le mandan al modelo las fotos de referencia (aprobado/
rechazado) del tipo de análisis correspondiente + la foto nueva de la
muestra + los criterios en texto de ese tipo de análisis, y se le pide un
veredicto estructurado. Agregar un tipo de análisis nuevo es solo cargar
fotos de referencia nuevas desde el admin — no toca este archivo.
"""

import json

import anthropic

from app.core.config import settings
from app.services.storage import read_photo_as_base64

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Límite razonable de fotos de referencia por llamada (costo/tokens). Si un
# tipo de análisis acumula muchas, se manda un subconjunto reciente.
MAX_REFERENCE_PHOTOS = 6


def _build_content(
    criterios: str,
    foto_muestra_url: str,
    fotos_referencia: list[tuple[str, str, str | None]],
) -> list[dict]:
    content: list[dict] = []

    for url, etiqueta, descripcion in fotos_referencia[:MAX_REFERENCE_PHOTOS]:
        try:
            data, media_type = read_photo_as_base64(url)
        except Exception:
            # Si una referencia puntual no se puede descargar, seguimos sin
            # ella en vez de romper todo el análisis.
            continue

        etiqueta_texto = "un cultivo APROBADO (así se ve bien)" if etiqueta == "aprobado" else "un cultivo RECHAZADO (así se ve mal)"
        texto = f"Foto de referencia — ejemplo de {etiqueta_texto}."
        if descripcion:
            texto += f" Nota: {descripcion}"

        content.append({"type": "text", "text": texto})
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}})

    muestra_data, muestra_media_type = read_photo_as_base64(foto_muestra_url)
    content.append({"type": "text", "text": "Foto de la MUESTRA A EVALUAR:"})
    content.append(
        {"type": "image", "source": {"type": "base64", "media_type": muestra_media_type, "data": muestra_data}}
    )

    instruccion = f"""
Sos un asistente que ayuda al personal de laboratorio de un tambo a
evaluar cultivos. No reemplazás el criterio del laboratorista: tu
veredicto se muestra como ayuda y siempre lo confirma o corrige una
persona antes de guardarse como definitivo.

Criterios para este tipo de análisis: {criterios}

Compará la foto de la muestra con las fotos de referencia (aprobadas y
rechazadas de arriba) y devolvé tu evaluación.

Respondé ÚNICAMENTE con un JSON válido, sin texto adicional, con este
formato exacto:
{{
  "veredicto": "aprobado" o "no_aprobado",
  "ufc_estimado": string con la estimación de UFC (unidades formadoras de colonias) o un rango (ej. "10.000-50.000"), o null si no aplica a este tipo de análisis,
  "confianza": número entre 0.0 y 1.0,
  "justificacion": "explicación breve en español, máximo 3 oraciones"
}}
"""
    content.append({"type": "text", "text": instruccion})
    return content


def analizar_muestra(
    criterios: str,
    foto_muestra_url: str,
    fotos_referencia: list[tuple[str, str, str | None]],
) -> dict:
    """Devuelve {veredicto, ufc_estimado, confianza, justificacion}.
    Puede levantar excepción (falla de red, respuesta no parseable, etc.) —
    a propósito: acá no se enmascara el error con un resultado neutro,
    porque en un contexto de laboratorio es preferible que la carga falle
    y se reintente a que quede guardado un veredicto inventado."""
    content = _build_content(criterios, foto_muestra_url, fotos_referencia)

    response = client.messages.create(
        model=settings.ai_model,
        max_tokens=500,
        messages=[{"role": "user", "content": content}],
    )

    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    resultado = json.loads(raw_text)

    veredicto = resultado.get("veredicto")
    if veredicto not in ("aprobado", "no_aprobado"):
        veredicto = "no_aprobado"

    return {
        "veredicto": veredicto,
        "ufc_estimado": resultado.get("ufc_estimado"),
        "confianza": float(resultado.get("confianza", 0.5)),
        "justificacion": str(resultado.get("justificacion", "Sin justificación")),
    }
