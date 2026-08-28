def test_login_admin_ok(client, admin_user):
    resp = client.post("/auth/login", json={"username": "admin_test", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_laboratorio_ok(client, lab_user):
    resp = client.post("/auth/login", json={"username": "lab_test", "password": "secret123"})
    assert resp.status_code == 200


def test_login_operario_denied(client, operario_user):
    """Un rol válido en tambo pero no habilitado acá recibe 403, no 401:
    la contraseña es correcta, lo que falta es permiso."""
    resp = client.post("/auth/login", json={"username": "operario_test", "password": "secret123"})
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Acceso denegado"


def test_login_wrong_password(client, admin_user):
    resp = client.post("/auth/login", json={"username": "admin_test", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/auth/login", json={"username": "no_existe", "password": "x"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, lab_user):
    from tests.conftest import login_headers

    headers = login_headers(client, "lab_test")
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "lab_test"
    assert resp.json()["role"] == "laboratorio"
