
def test_registration_requires_name(client):
    response = client.post("/api/register", json={
        "email": "student@jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_requires_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_requires_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@jiit.ac.in"
    })

    assert response.status_code == 400


def test_registration_success(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 201
    assert response.json["message"] == "Registration successful"
