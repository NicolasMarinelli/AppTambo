from tests.conftest import login_headers


def test_create_tipo_analisis_as_admin(client, admin_user):
    headers = login_headers(client, "admin_test")
    resp = client.post(
        "/tipos-analisis",
        json={"nombre": "Mastitis", "slug": "mastitis", "criterios_ia": "Buscar turbidez y color."},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["slug"] == "mastitis"
    assert resp.json()["activo"] is True


def test_create_tipo_analisis_as_laboratorio(client, lab_user):
    headers = login_headers(client, "lab_test")
    resp = client.post(
        "/tipos-analisis",
        json={"nombre": "Calostro", "slug": "calostro", "criterios_ia": "x"},
        headers=headers,
    )
    assert resp.status_code == 201


def test_create_tipo_analisis_duplicate_slug(client, admin_user):
    headers = login_headers(client, "admin_test")
    payload = {"nombre": "Mastitis", "slug": "mastitis", "criterios_ia": "x"}
    client.post("/tipos-analisis", json=payload, headers=headers)
    resp = client.post("/tipos-analisis", json=payload, headers=headers)
    assert resp.status_code == 409


def test_create_tipo_analisis_requires_auth(client):
    resp = client.post("/tipos-analisis", json={"nombre": "X", "slug": "x", "criterios_ia": "x"})
    assert resp.status_code == 401


def test_list_tipos_analisis_excludes_inactive_by_default(client, admin_user):
    headers = login_headers(client, "admin_test")
    client.post(
        "/tipos-analisis", json={"nombre": "Mastitis", "slug": "mastitis", "criterios_ia": "x"}, headers=headers
    )
    tipo_id = client.get("/tipos-analisis", headers=headers).json()[0]["id"]

    client.put(f"/tipos-analisis/{tipo_id}", json={"activo": False}, headers=headers)

    assert client.get("/tipos-analisis", headers=headers).json() == []
    incluidos = client.get("/tipos-analisis", params={"incluir_inactivos": True}, headers=headers).json()
    assert len(incluidos) == 1
