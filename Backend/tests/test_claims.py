async def test_create_claim_with_invalid_data_fails(client, auth_headers, policy):
    response = await client.post(
        "/api/claims/",
        headers=auth_headers,
        json={
            "claim_number": "CLM-INVALID",
            "policy_id": str(policy.id),
            "claim_type": "NOT_A_REAL_TYPE",  # expecting a fail. Not in the enum
            "claim_amount": 500,
            "incident_date": "2026-01-01",
        },
    )

    assert response.status_code == 422


async def test_create_claim_with_valid_data_succeeds(client, auth_headers, policy):
    response = await client.post(
        "/api/claims/",
        headers=auth_headers,
        json={
            "claim_number": "CLM-VALID-1",
            "policy_id": str(policy.id),
            "claim_type": "MOTOR",
            "claim_amount": 1500.75,
            "incident_date": "2026-01-15",
            "description": "Windshield crack",
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["claim_number"] == "CLM-VALID-1"
    assert body["status"] == "SUBMITTED"
    assert body["policy_id"] == str(policy.id)


async def test_invalid_status_transition_is_rejected(client, auth_headers, policy):
    create_response = await client.post(
        "/api/claims/",
        headers=auth_headers,
        json={
            "claim_number": "CLM-TRANSITION-1",
            "policy_id": str(policy.id),
            "claim_type": "HEALTH",
            "claim_amount": 800,
            "incident_date": "2026-02-01",
        },
    )
    claim_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/claims/{claim_id}",
        headers=auth_headers,
        json={"claim_amount": 800, "incident_date": "2026-02-01", "status": "APPROVED"},
    )

    assert response.status_code == 400


async def test_valid_status_transition_succeeds(client, auth_headers, policy):
    create_response = await client.post(
        "/api/claims/",
        headers=auth_headers,
        json={
            "claim_number": "CLM-TRANSITION-2",
            "policy_id": str(policy.id),
            "claim_type": "TRAVEL",
            "claim_amount": 300,
            "incident_date": "2026-03-01",
        },
    )
    claim_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/claims/{claim_id}",
        headers=auth_headers,
        json={"claim_amount": 300, "incident_date": "2026-03-01", "status": "UNDER_REVIEW"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"
