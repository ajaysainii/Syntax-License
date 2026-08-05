def test_admin_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@syntaxnation.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["admin"]["email"] == "admin@syntaxnation.com"


def test_license_validation_flow(client, auth_headers):
    customer = client.post(
        "/api/v1/customers",
        json={"name": "Acme", "email": "ops@acme.test", "company": "Acme"},
        headers=auth_headers,
    ).json()
    user = client.post(
        "/api/v1/users",
        json={
            "customer_id": customer["id"],
            "full_name": "Jane Dev",
            "email": "jane@acme.test",
            "role": "owner",
        },
        headers=auth_headers,
    ).json()
    issued = client.post(
        "/api/v1/licenses",
        json={
            "user_id": user["id"],
            "product": "syntax-cli",
            "plan": "pro",
            "features": ["offline-cache", "priority-support"],
        },
        headers=auth_headers,
    )
    assert issued.status_code == 201
    license_key = issued.json()["license_key"]

    validated = client.post(
        "/api/v1/licenses/validate",
        json={
            "license_key": license_key,
            "installation_id": "inst-001",
            "product": "syntax-cli",
            "version": "1.2.0",
            "hostname": "devbox",
            "platform": "darwin-arm64",
        },
    )
    assert validated.status_code == 200
    body = validated.json()
    assert body["valid"] is True
    assert body["status"] == "active"
    assert body["license"]["plan"] == "pro"
    assert body["license"]["email"] == "jane@acme.test"

