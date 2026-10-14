import requests


BASE_URL = "http://127.0.0.1:8000/users/"


def test_users_invalid_password_qwerty():
    """The admin username with password qwerty should return HTTP 200."""
    response = requests.get(
        BASE_URL,
        params={"username": "admin", "password": "qwerty"},
        timeout=5,
    )
    assert response.status_code == 200


def test_users_admin_password():
    """The admin username with password admin should return HTTP 401."""
    response = requests.get(
        BASE_URL,
        params={"username": "admin", "password": "admin"},
        timeout=5,
    )
    assert response.status_code == 401
