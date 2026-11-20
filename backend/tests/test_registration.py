# Check registration when name is missing
def test_registration_requires_name(client):
    response = client.post("/api/register", json={
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Check registration when email is missing
def test_registration_requires_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Check registration when password is missing
def test_registration_requires_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in"
    })
    assert response.status_code == 400


# Check successful registration
def test_registration_success(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 201
    assert response.json["message"] == (
        "Registration successful. You can now log in."
    )


# Reject invalid email format
def test_registration_rejects_invalid_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "invalid-email",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Reject duplicate email registration
def test_registration_rejects_duplicate_email(client):
    data = {
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    }

    client.post("/api/register", json=data)
    response = client.post("/api/register", json=data)

    assert response.status_code == 409


# Reject weak passwords
def test_registration_rejects_weak_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "weak"
    })
    assert response.status_code == 400


# Reject non-college email addresses
def test_registration_rejects_non_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@gmail.com",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Accept valid college email addresses
def test_registration_accepts_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 201
