from datetime import date
from fastapi.testclient import TestClient

from app.data import RECRUITMENTS
from app.main import app

client = TestClient(app)


# ==============================================================================
# 1. ECOSYSTEM & DATA INTEGRITY AUDIT
# ==============================================================================

def test_audit_all_five_ecosystems_present_and_structured():
    """Verify all 5 required MVP ecosystems are present with complete structured data."""
    response = client.get("/v1/recruitments")
    assert response.status_code == 200
    payload = response.json()
    items = payload["items"]
    assert len(items) >= 5

    required_ecosystems = {
        "org_ssc": "Staff Selection Commission",
        "org_upsc": "Union Public Service Commission",
        "org_ibps": "Institute of Banking Personnel Selection",
        "org_rrb": "Railway Recruitment Boards",
        "org_tspsc": "Telangana Public Service Commission",
    }

    found_orgs = {item["organization_id"]: item["organization_name"] for item in items}
    for org_id, org_name in required_ecosystems.items():
        assert org_id in found_orgs, f"Missing required ecosystem: {org_id}"
        assert found_orgs[org_id] == org_name

    # Audit high-impact fields on each recruitment
    for item in items:
        assert item["id"], "Recruitment must have an id"
        assert item["title"], "Recruitment must have a title"
        assert item["slug"], "Recruitment must have a slug"
        assert item["status"] in ["ACTIVE", "UPCOMING", "CLOSED", "SAMPLE"]
        assert item["verification_status"] == "VERIFIED"
        assert len(item["posts"]) >= 1, f"Recruitment {item['id']} must have at least one post"
        assert len(item["official_sources"]) >= 1, f"Recruitment {item['id']} must have official sources"

        # Check post fields
        post = item["posts"][0]
        assert post["title"]
        assert post["department"]
        assert post["vacancies"] is not None and post["vacancies"] > 0
        assert post["salary_text"]


def test_audit_official_sources_and_evidence_fragments():
    """Verify that official source URLs belong to legitimate official domains and evidence fragments exist."""
    approved_domains = [
        "ssc.gov.in",
        "upsc.gov.in",
        "ibps.in",
        "rrbapply.gov.in",
        "tspsc.gov.in",
    ]

    for rec in RECRUITMENTS:
        # Check source documents
        assert len(rec.official_sources) >= 1
        for src in rec.official_sources:
            assert any(domain in src.url for domain in approved_domains), (
                f"Source URL {src.url} does not belong to approved domains"
            )
            assert src.title
            assert src.document_type in ["NOTIFICATION", "OFFICIAL_PORTAL", "CORRIGENDUM", "SYLLABUS"]

        # Check evidence endpoint
        ev_resp = client.get(f"/v1/recruitments/{rec.id}/evidence")
        assert ev_resp.status_code == 200
        fragments = ev_resp.json()["items"]
        assert len(fragments) >= 1, f"No evidence fragments for recruitment {rec.id}"
        for frag in fragments:
            assert frag["id"]
            assert frag["text_content"], "Evidence fragment must have quote text"
            assert frag["source_title"]


# ==============================================================================
# 2. ELIGIBILITY ENGINE BACKTESTING: AGE & REFERENCE DATES
# ==============================================================================

def test_backtesting_ssc_cgl_age_boundaries():
    """SSC CGL: Reference Date 2025-08-01, Base Age 18-30.
    OBC relaxation: +3 yrs (max 33).
    SC/ST relaxation: +5 yrs (max 35).
    """
    post_id = "post_ssc_cgl_tier1"

    # 1. Exactly 18 years old on 2025-08-01: Born 2007-08-01 -> PASS
    res = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2007-08-01", "category": "GENERAL", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res["result"] == "ELIGIBLE"
    age_audit = next(r for r in res["reasons"] if r["rule_type"] == "AGE")
    assert age_audit["status"] == "PASS"

    # 2. Underage by 1 day: Born 2007-08-02 (17 years old on 2025-08-01) -> NOT_ELIGIBLE
    res = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2007-08-02", "category": "GENERAL", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res["result"] == "NOT_ELIGIBLE"
    age_audit = next(r for r in res["reasons"] if r["rule_type"] == "AGE")
    assert age_audit["status"] == "CHECK_FAILED"
    assert "below the minimum" in age_audit["message"]

    # 3. Exactly 30 years old on 2025-08-01: Born 1995-08-01 -> PASS
    res = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1995-08-01", "category": "GENERAL", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res["result"] == "ELIGIBLE"

    # 4. 31 years old: Born 1994-08-01.
    # General -> NOT_ELIGIBLE
    # OBC (+3y) -> ELIGIBLE
    # SC (+5y) -> ELIGIBLE
    res_gen = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1994-08-01", "category": "GENERAL", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_gen["result"] == "NOT_ELIGIBLE"

    res_obc = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1994-08-01", "category": "OBC", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_obc["result"] == "ELIGIBLE"

    res_sc = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1994-08-01", "category": "SC", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_sc["result"] == "ELIGIBLE"

    # 5. 34 years old: Born 1991-08-01.
    # OBC (max 33) -> NOT_ELIGIBLE
    # SC (max 35) -> ELIGIBLE
    res_obc_34 = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1991-08-01", "category": "OBC", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_obc_34["result"] == "NOT_ELIGIBLE"

    res_sc_34 = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1991-08-01", "category": "SC", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_sc_34["result"] == "ELIGIBLE"

    # 6. 36 years old: Born 1989-08-01 -> Exceeds SC limit (max 35) -> NOT_ELIGIBLE
    res_sc_36 = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "1989-08-01", "category": "SC", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_sc_36["result"] == "NOT_ELIGIBLE"


def test_backtesting_upsc_cse_minimum_age_boundary():
    """UPSC CSE: Reference Date 2025-08-01, Base Age 21-32."""
    post_id = "post_upsc_cse_2025"

    # 20 years old on 2025-08-01: Born 2005-01-01 -> FAIL (UPSC requires min 21)
    res_20 = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2005-01-01", "category": "GENERAL", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_20["result"] == "NOT_ELIGIBLE"
    age_audit = next(r for r in res_20["reasons"] if r["rule_type"] == "AGE")
    assert "below the minimum required age of 21" in age_audit["message"]

    # 21 years old on 2025-08-01: Born 2004-08-01 -> PASS
    res_21 = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2004-08-01", "category": "GENERAL", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_21["result"] == "ELIGIBLE"


# ==============================================================================
# 3. ELIGIBILITY ENGINE BACKTESTING: EDUCATION & DOMICILE
# ==============================================================================

def test_backtesting_education_hierarchy():
    """Educational level matching:
    SCHOOL (1) < HIGHER_SECONDARY (2) < DIPLOMA (3) < GRADUATE (4) < POSTGRADUATE (5) < DOCTORATE (6)
    """
    post_id = "post_ibps_po_xiv"

    # 1. 10th applying for Graduate post -> NOT_ELIGIBLE
    res_school = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2000-01-01", "education_level": "SCHOOL", "experience_years": 0}
    }).json()
    assert res_school["result"] == "NOT_ELIGIBLE"
    edu_audit = next(r for r in res_school["reasons"] if r["rule_type"] == "EDUCATION")
    assert edu_audit["status"] == "CHECK_FAILED"

    # 2. 12th / Higher Secondary applying for Graduate post -> NOT_ELIGIBLE
    res_hs = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2000-01-01", "education_level": "HIGHER_SECONDARY", "experience_years": 0}
    }).json()
    assert res_hs["result"] == "NOT_ELIGIBLE"

    # 3. Graduate applying for Graduate post -> PASS
    res_grad = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2000-01-01", "education_level": "GRADUATE", "experience_years": 0}
    }).json()
    assert res_grad["result"] == "ELIGIBLE"

    # 4. Postgraduate applying for Graduate post -> PASS (higher rank meets requirement)
    res_pg = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {"date_of_birth": "2000-01-01", "education_level": "POSTGRADUATE", "experience_years": 0}
    }).json()
    assert res_pg["result"] == "ELIGIBLE"


def test_backtesting_domicile_and_reservation():
    """TSPSC Group-I: 95% reservation for Telangana local candidates."""
    post_id = "post_tspsc_group1_2025"

    # Telangana local candidate -> ELIGIBLE with 95% local reservation pass
    res_tg = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {
            "date_of_birth": "1995-06-12",
            "domicile_state": "Telangana",
            "education_level": "GRADUATE",
            "experience_years": 0,
        }
    }).json()
    assert res_tg["result"] == "ELIGIBLE"
    dom_audit = next(r for r in res_tg["reasons"] if r["rule_type"] == "DOMICILE")
    assert dom_audit["status"] == "PASS"
    assert "95% local reservation quota" in dom_audit["message"]

    # Candidate from another state (e.g. Karnataka) -> LIKELY_ELIGIBLE under 5% open quota
    res_other = client.post("/v1/eligibility/evaluate", json={
        "job_post_id": post_id,
        "profile": {
            "date_of_birth": "1995-06-12",
            "domicile_state": "Karnataka",
            "education_level": "GRADUATE",
            "experience_years": 0,
        }
    }).json()
    assert res_other["result"] == "LIKELY_ELIGIBLE"
    dom_audit = next(r for r in res_other["reasons"] if r["rule_type"] == "DOMICILE")
    assert dom_audit["status"] == "NEEDS_VERIFICATION"
    assert "5% open unreserved quota" in dom_audit["message"]


# ==============================================================================
# 4. SEARCH, FILTERING & RECRUITMENT DISCOVERY
# ==============================================================================

def test_backtesting_search_and_multi_criteria_filtering():
    """Validate query search across all fields and filter dimensions."""
    # 1. Search by title keyword
    r = client.get("/v1/recruitments?q=Civil").json()
    assert r["total"] >= 1
    assert any("Civil" in item["title"] for item in r["items"])

    # 2. Search by department
    r = client.get("/v1/recruitments?q=Railways").json()
    assert r["total"] >= 1
    assert any("RRB" in item["title"] or "Railway" in item["title"] for item in r["items"])

    # 3. Filter by organization_id
    r = client.get("/v1/recruitments?organization_id=org_tspsc").json()
    assert r["total"] == 1
    assert r["items"][0]["id"] == "recruitment_tspsc_group1"

    # 4. Filter by education_level
    r = client.get("/v1/recruitments?education_level=GRADUATE").json()
    assert r["total"] >= 5

    # 5. Filter by location
    r = client.get("/v1/recruitments?location=Telangana").json()
    assert r["total"] >= 1
    assert any("tspsc" in item["id"] for item in r["items"])

    # 6. Pagination check
    r_page1 = client.get("/v1/recruitments?page=1&page_size=2").json()
    assert len(r_page1["items"]) == 2
    assert r_page1["page"] == 1
    assert r_page1["page_size"] == 2
    assert r_page1["total"] >= 5

    r_page2 = client.get("/v1/recruitments?page=2&page_size=2").json()
    assert len(r_page2["items"]) == 2
    assert r_page2["page"] == 2
    # Ensure items on page 1 and page 2 are distinct
    assert r_page1["items"][0]["id"] != r_page2["items"][0]["id"]


# ==============================================================================
# 5. AI ASSISTANT / COPILOT CITATION AUDIT
# ==============================================================================

def test_backtesting_assistant_citation_accuracy():
    """Verify assistant produces grounded answers and valid citations."""
    queries = [
        ("recruitment_ssc_cgl", "What is the application deadline?", ["Closing Date", "2025"]),
        ("recruitment_upsc_cse", "What is the age limit and category relaxation?", ["21", "32", "OBC", "SC"]),
        ("recruitment_ibps_po", "What qualification is required?", ["Bachelor's Degree", "Graduation"]),
        ("recruitment_rrb_ntpc", "How many vacancies and pay scale?", ["vacancies", "Pay Level"]),
    ]

    for rec_id, question, expected_keywords in queries:
        resp = client.post("/v1/assistant/query", json={
            "recruitment_id": rec_id,
            "question": question,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["verification_status"] == "VERIFIED"
        assert data["last_verified_at"] is not None

        # Check that answer contains expected facts
        for kw in expected_keywords:
            assert kw.lower() in data["answer"].lower(), (
                f"Expected keyword '{kw}' not found in assistant answer for {rec_id}"
            )

        # Audit citations
        assert len(data["citations"]) >= 1
        for citation in data["citations"]:
            assert citation["document_id"]
            assert citation["quote"]
            assert citation["section"]
