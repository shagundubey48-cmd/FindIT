
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
        "email": "student@mail.jiit.ac.in"
    })

    assert response.status_code == 400


def test_registration_success(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 201
    assert response.json["message"] == "Registration successful"

def test_registration_rejects_invalid_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "invalid-email",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_rejects_duplicate_email(client):
    data = {
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    }

    client.post("/api/register", json=data)
    response = client.post("/api/register", json=data)

    assert response.status_code == 409


def test_registration_rejects_weak_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student2@mail.jiit.ac.in",
        "password": "123"
    })

    assert response.status_code == 400


def test_registration_rejects_non_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@gmail.com",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_accepts_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 201
    assert response.json["message"] == "Registration successful"
