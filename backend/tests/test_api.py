from fastapi.testclient import TestClient

from app.data import RECRUITMENTS, SAVED_RECRUITMENT_IDS
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recruitments_list_contains_all_five_ecosystems():
    response = client.get("/v1/recruitments")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 5
    org_ids = {item["organization_id"] for item in payload["items"]}
    assert {"org_ssc", "org_upsc", "org_ibps", "org_rrb", "org_tspsc"}.issubset(org_ids)


def test_recruitment_detail_and_sources():
    response = client.get("/v1/recruitments/recruitment_tspsc_group1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "TSPSC Group-I Services Recruitment 2024-25"
    assert payload["official_apply_url"] == "https://www.tspsc.gov.in/"
    assert len(payload["posts"]) >= 1

    sources_resp = client.get("/v1/recruitments/recruitment_tspsc_group1/sources")
    assert sources_resp.status_code == 200
    assert len(sources_resp.json()["items"]) >= 1


def test_recruitment_evidence_fragments():
    response = client.get("/v1/recruitments/recruitment_ssc_cgl/evidence")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    assert any("Age" in ev["section_heading"] or "Qualification" in ev["section_heading"] for ev in items)


def test_recruitment_events_timeline():
    response = client.get("/v1/recruitments/recruitment_upsc_cse/events")
    assert response.status_code == 200
    events = response.json()["items"]
    assert len(events) >= 2


def test_search_and_filters():
    # Keyword search for railway
    rrb_resp = client.get("/v1/recruitments?q=Railway")
    assert rrb_resp.status_code == 200
    assert any("RRB" in item["title"] or "Railway" in item["title"] for item in rrb_resp.json()["items"])

    # Filter by organization
    ibps_resp = client.get("/v1/recruitments?organization_id=org_ibps")
    assert ibps_resp.status_code == 200
    assert len(ibps_resp.json()["items"]) == 1
    assert ibps_resp.json()["items"][0]["id"] == "recruitment_ibps_po"

    # Filter by education level
    grad_resp = client.get("/v1/recruitments?education_level=GRADUATE")
    assert grad_resp.status_code == 200
    assert grad_resp.json()["total"] >= 5


def test_eligibility_evaluation_with_relaxations():
    # Candidate who is 32 years old as on 2025-08-01: born 1993-01-01
    # Under General: max age 30 -> FAILS
    # Under OBC: max age 30 + 3 = 33 -> PASSES
    resp_gen = client.post(
        "/v1/eligibility/evaluate",
        json={
            "job_post_id": "post_ssc_cgl_tier1",
            "profile": {
                "date_of_birth": "1993-01-01",
                "category": "GENERAL",
                "education_level": "GRADUATE",
                "experience_years": 0,
            },
        },
    )
    assert resp_gen.status_code == 200
    assert resp_gen.json()["result"] == "NOT_ELIGIBLE"
    gen_age = next(r for r in resp_gen.json()["reasons"] if r["rule_type"] == "AGE")
    assert gen_age["status"] == "CHECK_FAILED"

    resp_obc = client.post(
        "/v1/eligibility/evaluate",
        json={
            "job_post_id": "post_ssc_cgl_tier1",
            "profile": {
                "date_of_birth": "1993-01-01",
                "category": "OBC",
                "education_level": "GRADUATE",
                "experience_years": 0,
            },
        },
    )
    assert resp_obc.status_code == 200
    assert resp_obc.json()["result"] == "ELIGIBLE"
    obc_age = next(r for r in resp_obc.json()["reasons"] if r["rule_type"] == "AGE")
    assert obc_age["status"] == "PASS"
    assert "relaxed up to 33 years for OBC" in obc_age["message"]
    assert obc_age["evidence_id"] is not None


def test_eligibility_domicile_check_tspsc():
    # Telangana local candidate
    resp_local = client.post(
        "/v1/eligibility/evaluate",
        json={
            "job_post_id": "post_tspsc_group1_2025",
            "profile": {
                "date_of_birth": "1995-06-12",
                "domicile_state": "Telangana",
                "education_level": "GRADUATE",
                "experience_years": 1,
            },
        },
    )
    assert resp_local.status_code == 200
    assert resp_local.json()["result"] == "ELIGIBLE"
    dom_reason = next(r for r in resp_local.json()["reasons"] if r["rule_type"] == "DOMICILE")
    assert dom_reason["status"] == "PASS"
    assert "95% local reservation" in dom_reason["message"]

    # Non-local candidate
    resp_non_local = client.post(
        "/v1/eligibility/evaluate",
        json={
            "job_post_id": "post_tspsc_group1_2025",
            "profile": {
                "date_of_birth": "1995-06-12",
                "domicile_state": "Maharashtra",
                "education_level": "GRADUATE",
                "experience_years": 1,
            },
        },
    )
    assert resp_non_local.status_code == 200
    assert resp_non_local.json()["result"] == "LIKELY_ELIGIBLE"


def test_eligibility_missing_birth_date_is_insufficient_data():
    response = client.post(
        "/v1/eligibility/evaluate",
        json={
            "job_post_id": "post_upsc_cse_2025",
            "profile": {"date_of_birth": None, "education_level": "GRADUATE", "experience_years": None},
        },
    )
    assert response.status_code == 200
    assert response.json()["result"] == "INSUFFICIENT_DATA"


def test_eligibility_rejects_unknown_job_and_invalid_input():
    assert client.post("/v1/eligibility/evaluate", json={"job_post_id": "not-a-post"}).status_code == 404
    assert client.post(
        "/v1/eligibility/evaluate",
        json={"job_post_id": "post_tspsc_group1_2025", "profile": {"experience_years": -1}},
    ).status_code == 422


def test_candidate_profile_crud_and_evaluations():
    # GET profile
    get_resp = client.get("/v1/profile")
    assert get_resp.status_code == 200
    assert get_resp.json()["user_id"] == "user_123"

    # PUT profile
    put_resp = client.put(
        "/v1/profile",
        json={
            "user_id": "user_123",
            "date_of_birth": "1996-04-15",
            "category": "OBC",
            "domicile_state": "Telangana",
            "preferred_states": ["Telangana", "India"],
            "education_level": "GRADUATE",
            "degree_name": "B.Tech",
            "specialization": "Information Technology",
            "experience_years": 3.0,
            "gender": "F",
        },
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["profile"]["category"] == "OBC"

    # GET evaluations
    eval_resp = client.get("/v1/profile/evaluations")
    assert eval_resp.status_code == 200
    items = eval_resp.json()["items"]
    assert len(items) >= 5


def test_assistant_query_grounded_answers():
    # Deadline query
    dl_resp = client.post(
        "/v1/assistant/query",
        json={"recruitment_id": "recruitment_ssc_cgl", "question": "What is the application deadline?"},
    )
    assert dl_resp.status_code == 200
    payload = dl_resp.json()
    assert "Closing Date" in payload["answer"]
    assert payload["verification_status"] == "VERIFIED"
    assert len(payload["citations"]) >= 1

    # Age query
    age_resp = client.post(
        "/v1/assistant/query",
        json={"recruitment_id": "recruitment_upsc_cse", "question": "What is the age limit and relaxation?"},
    )
    assert age_resp.status_code == 200
    assert "OBC" in age_resp.json()["answer"]
    assert len(age_resp.json()["citations"]) >= 1


def test_saving_and_reminders():
    # Save recruitment
    rec_id = "recruitment_ibps_po"
    assert client.post(f"/v1/recruitments/{rec_id}/save").json()["saved"] is True
    assert rec_id in [item["id"] for item in client.get("/v1/saved").json()["items"]]
    assert client.delete(f"/v1/recruitments/{rec_id}/save").json()["saved"] is False

    # Create reminder
    rem_resp = client.post(
        "/v1/reminders",
        json={
            "recruitment_id": "recruitment_rrb_ntpc",
            "event_type": "DEADLINE",
            "scheduled_for": "2025-10-15T09:00:00Z",
        },
    )
    assert rem_resp.status_code == 200
    rem_id = rem_resp.json()["id"]

    # Get reminders
    list_resp = client.get("/v1/reminders")
    assert any(r["id"] == rem_id for r in list_resp.json()["items"])

    # Delete reminder
    del_resp = client.delete(f"/v1/reminders/{rem_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True
