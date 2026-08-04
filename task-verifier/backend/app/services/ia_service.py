import anthropic
from app.config import settings
from app.utils.storage import read_photo_as_base64


# Cliente de Anthropic — se inicializa una vez
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def analizar_foto(
    pregunta: str,
    foto_respuesta_url: str,
    foto_referencia_url: str | None = None,
    prompt_extra: str | None = None,   # ← nuevo
) -> dict:
    """
    Analiza una foto usando Claude con visión.

    Args:
        pregunta: El texto del item del checklist
        foto_respuesta_url: URL de la foto subida por el operario
        foto_referencia_url: URL de la foto de referencia (opcional)
        
    Returns:
        { aprobado: bool, confianza: float, observacion: str }
    
   
    """
    
    # Construir el contenido del mensaje
    content = []
    contexto_extra = f"\nContexto adicional sobre cómo debe verse la tarea correcta: {prompt_extra}" if prompt_extra else ""
    
    # Si hay foto de referencia, la incluimos primero con contexto
    if foto_referencia_url:
        try:
            ref_base64, ref_media_type = read_photo_as_base64(foto_referencia_url)
            content.append({
                "type": "text",
                "text": "Esta es la FOTO DE REFERENCIA que muestra cómo debe verse la tarea correctamente completada:",
            })
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": ref_media_type,
                    "data": ref_base64,
                },
            })
        except Exception:
            # Si no se puede leer la referencia, continuamos sin ella
            pass

    # Foto enviada por el operario
    resp_base64, resp_media_type = read_photo_as_base64(foto_respuesta_url)

    content.append({
        "type": "text",
        "text": "Esta es la FOTO ENVIADA POR EL OPERARIO para verificación:",
    })
    content.append({
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": resp_media_type,
            "data": resp_base64,
        },
    })

    # Instrucción final
    if foto_referencia_url:
        instruccion = f"""
Tarea a verificar: "{pregunta}"{contexto_extra}

Compará la foto del operario con la foto de referencia y determiná si la tarea está correctamente completada.

Respondé ÚNICAMENTE con un JSON válido con este formato exacto, sin texto adicional:
{{
  "aprobado": true o false,
  "confianza": número entre 0.0 y 1.0,
  "observacion": "explicación breve de tu decisión en español"
}}

Criterios:
- aprobado: true si la tarea está completada de forma similar a la referencia
- confianza: qué tan seguro estás (0.9+ = muy seguro, 0.5-0.8 = dudoso, <0.5 = muy incierto)
- observacion: máximo 2 oraciones explicando qué viste
"""
    else:
        instruccion = f"""
Tarea a verificar: "{pregunta}"{contexto_extra}

Analizá la foto enviada por el operario y determiná si la tarea descripta está correctamente completada.

Respondé ÚNICAMENTE con un JSON válido con este formato exacto, sin texto adicional:
{{
  "aprobado": true o false,
  "confianza": número entre 0.0 y 1.0,
  "observacion": "explicación breve de tu decisión en español"
}}

Criterios:
- aprobado: true si la foto evidencia que la tarea fue completada
- confianza: qué tan seguro estás (0.9+ = muy seguro, 0.5-0.8 = dudoso, <0.5 = muy incierto)
- observacion: máximo 2 oraciones explicando qué viste
"""

    content.append({"type": "text", "text": instruccion})

    # Llamada a la API
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": content}],
    )

    # Parsear la respuesta JSON
    raw_text = response.content[0].text.strip()

    # Limpiar posibles backticks si Claude los incluyó
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    import json
    resultado = json.loads(raw_text)

    # Validar estructura
    return {
        "aprobado": bool(resultado.get("aprobado", False)),
        "confianza": float(resultado.get("confianza", 0.5)),
        "observacion": str(resultado.get("observacion", "Sin observación")),
    }



def analizar_foto_seguro(
    pregunta: str,
    foto_respuesta_url: str,
    foto_referencia_url: str | None = None,
) -> dict:
    """
    Wrapper con manejo de errores.
    Si la IA falla por cualquier razón, retorna un resultado neutro
    en vez de romper el endpoint del operario.
    """
    try:
        return analizar_foto(pregunta, foto_respuesta_url, foto_referencia_url)
    except Exception as e:
        return {
            "aprobado": False,
            "confianza": 0.0,
            "observacion": f"Error al analizar la imagen: {str(e)}",
        }