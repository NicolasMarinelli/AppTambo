import io

import app.api.fotos_referencia as fotos_mod
import app.api.resultados as resultados_mod
from app.models.enums import EtiquetaFoto
from tests.conftest import login_headers


async def _fake_save_photo(file, subfolder=""):
    return "https://cloudinary.test/fake.jpg"


def _fake_analizar(**kwargs):
    return {"veredicto": "aprobado", "ufc_estimado": "10.000", "confianza": 0.9, "justificacion": "Se ve bien."}


def _crear_tipo_con_referencia(client, headers, monkeypatch):
    monkeypatch.setattr(fotos_mod, "save_photo", _fake_save_photo)

    tipo_id = client.post(
        "/tipos-analisis",
        json={"nombre": "Mastitis", "slug": "mastitis", "criterios_ia": "Buscar turbidez."},
        headers=headers,
    ).json()["id"]

    client.post(
        f"/tipos-analisis/{tipo_id}/fotos-referencia",
        data={"etiqueta": EtiquetaFoto.aprobado.value},
        files={"file": ("ref.jpg", io.BytesIO(b"fake"), "image/jpeg")},
        headers=headers,
    )
    return tipo_id


def test_create_resultado_requires_referencia_photos(client, admin_user):
    headers = login_headers(client, "admin_test")
    tipo_id = client.post(
        "/tipos-analisis", json={"nombre": "Calostro", "slug": "calostro", "criterios_ia": "x"}, headers=headers
    ).json()["id"]

    resp = client.post(
        "/resultados",
        data={"tipo_analisis_id": tipo_id, "identificacion_muestra": "Lote 1"},
        files={"file": ("muestra.jpg", io.BytesIO(b"fake"), "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 409


def test_full_flow_carga_muestra_y_revision(client, admin_user, monkeypatch):
    headers = login_headers(client, "admin_test")
    tipo_id = _crear_tipo_con_referencia(client, headers, monkeypatch)

    monkeypatch.setattr(resultados_mod, "save_photo", _fake_save_photo)
    monkeypatch.setattr(resultados_mod, "analizar_muestra", _fake_analizar)

    resp = client.post(
        "/resultados",
        data={"tipo_analisis_id": tipo_id, "identificacion_muestra": "Lote 12"},
        files={"file": ("muestra.jpg", io.BytesIO(b"fake"), "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["estado"] == "pendiente"
    assert body["veredicto_final"] is None
    assert body["veredicto_ia"] == "aprobado"
    assert body["ufc"] == "10.000"

    resultado_id = body["id"]

    # Confirma el veredicto de la IA: pasa a definitivo, con quién y cuándo.
    resp2 = client.patch(
        f"/resultados/{resultado_id}/revision", json={"veredicto_final": "aprobado"}, headers=headers
    )
    assert resp2.status_code == 200
    revisado = resp2.json()
    assert revisado["estado"] == "aprobado"
    assert revisado["veredicto_final"] == "aprobado"
    assert revisado["revisado_por"] is not None
    assert revisado["revisado_en"] is not None


def test_create_resultado_requires_auth(client):
    resp = client.post(
        "/resultados",
        data={"tipo_analisis_id": 1, "identificacion_muestra": "Lote 1"},
        files={"file": ("muestra.jpg", io.BytesIO(b"fake"), "image/jpeg")},
    )
    assert resp.status_code == 401
