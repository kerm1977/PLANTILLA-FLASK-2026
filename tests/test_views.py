"""Pruebas de humo: todas las vistas responden correctamente."""
import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "ruta",
    ["/", "/dashboard", "/perfil", "/auth/login", "/auth/registro", "/admin/"],
)
def test_vistas_responden(client, ruta):
    assert client.get(ruta).status_code == 200


def test_health(client):
    respuesta = client.get("/api/health")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["app"] == "ok"


def test_404_personalizado(client):
    respuesta = client.get("/no-existe")
    assert respuesta.status_code == 404
    assert "404" in respuesta.get_data(as_text=True)


def test_home_sin_boton_back(client):
    html = client.get("/").get_data(as_text=True)
    assert "Back to Home" not in html


def test_login_con_boton_back(client):
    html = client.get("/auth/login").get_data(as_text=True)
    assert "Back to Home" in html
    assert "btn-warning" in html
