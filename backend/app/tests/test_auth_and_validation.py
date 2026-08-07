from datetime import UTC, datetime, timedelta


def _create_customer(client, auth_headers, *, name="Acme", email="ops@acme.example.com"):
    response = client.post(
        "/api/v1/customers",
        json={"name": name, "email": email, "company": name},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_user(client, auth_headers, customer_id, *, full_name="Jane Dev", email="jane@acme.example.com"):
    response = client.post(
        "/api/v1/users",
        json={
            "customer_id": customer_id,
            "full_name": full_name,
            "email": email,
            "role": "owner",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_admin_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@syntaxnation.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["admin"]["email"] == "admin@syntaxnation.com"


def test_license_validation_flow_accepts_generated_key_and_aliases(client, auth_headers, monkeypatch):
    customer = _create_customer(client, auth_headers)
    user = _create_user(client, auth_headers, customer["id"])
    expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
    fixed_key = "SYNTAX-5C0588-633B74-D48DA7-F48404"
    monkeypatch.setattr("app.api.v1.licenses.create_license_key", lambda: fixed_key)

    issued = client.post(
        "/api/v1/licenses",
        json={
            "user_id": user["id"],
            "product": "syntax-cli",
            "plan": "pro",
            "expires_at": expires_at,
            "features": ["offline-cache", "priority-support"],
        },
        headers=auth_headers,
    )
    assert issued.status_code == 201, issued.text
    issued_body = issued.json()
    assert issued_body["license_key"] == fixed_key
    assert issued_body["license"]["product"] == "syntax"

    validated = client.post(
        "/api/v1/licenses/validate",
        json={
            "license_key": fixed_key,
            "installation_id": "inst-001",
            "product": "syntax",
            "version": "1.2.0",
            "hostname": "devbox",
            "platform": "darwin-arm64",
        },
    )
    assert validated.status_code == 200, validated.text
    body = validated.json()
    assert body["valid"] is True
    assert body["status"] == "active"
    assert body["license"]["plan"] == "pro"
    assert body["license"]["email"] == "jane@acme.example.com"

    alias_validated = client.post(
        "/api/v1/licenses/validate",
        json={
            "license_key": fixed_key,
            "installation_id": "inst-002",
            "product": "syntax-desktop",
            "version": "1.2.1",
            "hostname": "studio-mac",
            "platform": "darwin-arm64",
        },
    )
    assert alias_validated.status_code == 200, alias_validated.text
    alias_body = alias_validated.json()
    assert alias_body["valid"] is True
    assert alias_body["status"] == "active"


def test_unknown_key_returns_clean_invalid_response_for_alias_products(client):
    for product in ("syntax", "syntax-cli", "syntax-desktop"):
        response = client.post(
            "/api/v1/licenses/validate",
            json={
                "license_key": "SYNTAX-000000-000000-000000-000000",
                "installation_id": f"{product}-missing",
                "product": product,
                "version": "1.0.0",
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["valid"] is False
        assert body["status"] == "invalid"
        assert body["message"] == "License key not found"


def test_admin_can_reveal_newly_issued_license_key(client, auth_headers, monkeypatch):
    customer = _create_customer(client, auth_headers, name="Reveal Co", email="ops@reveal.example.com")
    user = _create_user(client, auth_headers, customer["id"], full_name="Reveal User", email="reveal@reveal.example.com")
    fixed_key = "SYNTAX-5C0588-633B74-D48DA7-F48404"
    monkeypatch.setattr("app.api.v1.licenses.create_license_key", lambda: fixed_key)

    issued = client.post(
        "/api/v1/licenses",
        json={
            "user_id": user["id"],
            "product": "syntax",
            "plan": "enterprise",
            "features": ["priority-support"],
        },
        headers=auth_headers,
    )
    assert issued.status_code == 201, issued.text

    license_id = issued.json()["license"]["id"]
    revealed = client.get(f"/api/v1/licenses/{license_id}/key", headers=auth_headers)
    assert revealed.status_code == 200, revealed.text
    assert revealed.json()["license_key"] == fixed_key
