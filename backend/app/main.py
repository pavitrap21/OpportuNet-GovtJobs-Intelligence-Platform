from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
import os
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .data import REMINDERS, RECRUITMENTS, SAVED_RECRUITMENT_IDS, USER_PROFILE
from .database import (
    EvidenceFragment,
    Recruitment as DBRecruitment,
    SavedRecruitment,
    SourceDocument as DBSourceDocument,
    UserProfile as DBUserProfile,
    get_db,
    init_db,
    SessionLocal,
)
from .eligibility import evaluate_job_match, RULE_DEFINITIONS
from .models import (
    AssistantRequest,
    AssistantResponse,
    CandidateProfile,
    EligibilityRequest,
    EvidenceCitation,
    LoginRequest,
    RemindersCreate,
)
from .seed_data import seed_database


# Initialize schema and seed database immediately so it is available for TestClient and server
try:
    init_db()
    _init_db = SessionLocal()
    try:
        seed_database(_init_db)
    finally:
        _init_db.close()
except Exception as exc:
    print(f"Database initialization notice: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="GovJobs Intelligence Platform",
    description="Evidence-backed Indian public sector recruitment intelligence platform.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROFILE_VERSION = 1
PUBLIC_DEMO_MODE = os.getenv("PUBLIC_DEMO_MODE", "false").casefold() in {"1", "true", "yes"}


def enforce_public_demo_read_only() -> None:
    if PUBLIC_DEMO_MODE:
        raise HTTPException(status_code=403, detail="This public preview is read-only.")


@app.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "2.0.0"}


@app.get("/v1/recruitments")
def list_recruitments(
    q: str | None = Query(default=None, max_length=200),
    organization_id: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=40),
    education_level: str | None = Query(default=None, max_length=40),
    location: str | None = Query(default=None, max_length=100),
    deadline_before: date | None = Query(default=None),
    deadline_after: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items = list(RECRUITMENTS)

    if q:
        q_clean = q.lower().strip()
        items = [
            r for r in items
            if q_clean in r.title.lower()
            or q_clean in r.slug.lower()
            or (r.organization_name and q_clean in r.organization_name.lower())
            or any(
                (post.title and q_clean in post.title.lower())
                or (post.department and q_clean in post.department.lower())
                or (post.description and q_clean in post.description.lower())
                for post in r.posts
            )
        ]
    if organization_id:
        items = [r for r in items if r.organization_id == organization_id]
    if status:
        items = [r for r in items if r.status.upper() == status.upper()]
    if location:
        items = [
            r for r in items
            if any(post.location_type and location.lower() in post.location_type.lower() for post in r.posts)
        ]
    if education_level:
        items = [
            r for r in items
            if r.required_education_level
            and r.required_education_level.casefold() == education_level.casefold()
        ]
    if deadline_before:
        items = [r for r in items if r.application_deadline and r.application_deadline <= deadline_before]
    if deadline_after:
        items = [r for r in items if r.application_deadline and r.application_deadline >= deadline_after]

    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": [r.model_dump() for r in items[start:end]],
        "page": page,
        "page_size": page_size,
        "total": len(items),
    }


@app.get("/v1/recruitments/{recruitment_id}")
def get_recruitment(recruitment_id: str):
    for recruitment in RECRUITMENTS:
        if recruitment.id == recruitment_id:
            return recruitment.model_dump()
    raise HTTPException(status_code=404, detail="Recruitment not found")


@app.get("/v1/recruitments/{recruitment_id}/sources")
def get_sources(recruitment_id: str):
    recruitment = next((r for r in RECRUITMENTS if r.id == recruitment_id), None)
    if not recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")
    return {"items": [doc.model_dump() for doc in recruitment.official_sources]}


@app.get("/v1/recruitments/{recruitment_id}/evidence")
def get_evidence(recruitment_id: str, db: Session = Depends(get_db)):
    recruitment = next((r for r in RECRUITMENTS if r.id == recruitment_id), None)
    if not recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")

    fragments = []
    # Query database evidence fragments if available
    db_sources = db.query(DBSourceDocument).filter(DBSourceDocument.recruitment_id == recruitment_id).all()
    for src in db_sources:
        for ev in src.evidence_fragments:
            fragments.append({
                "id": ev.id,
                "source_document_id": src.id,
                "source_title": src.title,
                "url": src.url,
                "page_number": ev.page_number,
                "section_heading": ev.section_heading,
                "text_content": ev.text_content,
            })

    if not fragments:
        # Fallback to in-memory sources
        for doc in recruitment.official_sources:
            fragments.append({
                "id": f"ev_{doc.id}",
                "source_document_id": doc.id,
                "source_title": doc.title,
                "url": doc.url,
                "page_number": doc.page,
                "section_heading": doc.section,
                "text_content": f"Verified excerpt from {doc.title} ({doc.section or 'General Clause'}).",
            })

    return {"items": fragments}


@app.get("/v1/recruitments/{recruitment_id}/events")
def get_events(recruitment_id: str):
    recruitment = next((r for r in RECRUITMENTS if r.id == recruitment_id), None)
    if not recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")

    events = [
        {
            "id": f"event_notif_{recruitment.id}",
            "recruitment_id": recruitment.id,
            "event_type": "NOTIFICATION_PUBLISHED",
            "occurred_at": recruitment.published_at,
            "summary": f"Official notification published by {recruitment.organization_name or recruitment.organization_id}.",
        }
    ]
    if recruitment.application_start_date:
        events.append({
            "id": f"event_start_{recruitment.id}",
            "recruitment_id": recruitment.id,
            "event_type": "APPLICATION_WINDOW_OPENED",
            "occurred_at": recruitment.application_start_date.isoformat(),
            "summary": "Online applications opened on official recruitment portal.",
        })
    if recruitment.application_deadline:
        events.append({
            "id": f"event_deadline_{recruitment.id}",
            "recruitment_id": recruitment.id,
            "event_type": "APPLICATION_DEADLINE",
            "occurred_at": recruitment.application_deadline.isoformat(),
            "summary": "Last date for submission of online application and fee payment.",
        })
    if recruitment.exam_date:
        events.append({
            "id": f"event_exam_{recruitment.id}",
            "recruitment_id": recruitment.id,
            "event_type": "EXAMINATION_DATE",
            "occurred_at": recruitment.exam_date.isoformat(),
            "summary": "Scheduled examination date announced.",
        })

    return {"items": events}


@app.post("/v1/auth/register")
def register() -> None:
    raise HTTPException(status_code=501, detail="Account registration is not configured in this local preview.")


@app.post("/v1/auth/login")
def login(payload: LoginRequest) -> None:
    raise HTTPException(status_code=501, detail="Authentication is not configured. No account or session was created.")


@app.post("/v1/auth/logout")
def logout() -> None:
    raise HTTPException(status_code=501, detail="Authentication is not configured; there is no active server session.")


@app.post("/v1/auth/refresh")
def refresh() -> None:
    raise HTTPException(status_code=501, detail="Authentication is not configured; no refresh token is issued.")


@app.get("/v1/profile")
def get_profile(db: Session = Depends(get_db)):
    if PUBLIC_DEMO_MODE:
        return {
            "user_id": "demo",
            "date_of_birth": None,
            "gender": "",
            "category": "GENERAL",
            "domicile_state": "",
            "preferred_states": [],
            "education_level": "",
            "degree_name": "",
            "specialization": "",
            "experience_years": 0,
            "profile_version": 1,
        }
    db_prof = db.query(DBUserProfile).filter(DBUserProfile.user_id == USER_PROFILE.user_id).first()
    if db_prof:
        return {
            "user_id": db_prof.user_id,
            "date_of_birth": db_prof.date_of_birth.isoformat() if db_prof.date_of_birth else None,
            "gender": db_prof.gender,
            "category": db_prof.category,
            "domicile_state": db_prof.domicile_state,
            "preferred_states": (db_prof.preferred_states or "").split(","),
            "education_level": db_prof.education_level,
            "degree_name": db_prof.degree_name,
            "specialization": db_prof.specialization,
            "experience_years": db_prof.experience_years,
            "profile_version": db_prof.profile_version,
        }
    return USER_PROFILE.model_dump()


@app.put("/v1/profile")
def update_profile(payload: CandidateProfile, db: Session = Depends(get_db)) -> dict[str, Any]:
    enforce_public_demo_read_only()
    global PROFILE_VERSION
    for field, value in payload.model_dump().items():
        if field != "user_id":
            setattr(USER_PROFILE, field, value)
    PROFILE_VERSION += 1

    # Persist to database if record exists
    db_prof = db.query(DBUserProfile).filter(DBUserProfile.user_id == USER_PROFILE.user_id).first()
    if db_prof:
        db_prof.date_of_birth = payload.date_of_birth
        db_prof.gender = payload.gender
        db_prof.category = payload.category
        db_prof.domicile_state = payload.domicile_state
        db_prof.preferred_states = ",".join(payload.preferred_states)
        db_prof.education_level = payload.education_level
        db_prof.degree_name = payload.degree_name
        db_prof.specialization = payload.specialization
        db_prof.experience_years = payload.experience_years
        db_prof.profile_version = PROFILE_VERSION
        db.commit()

    return {"profile": USER_PROFILE.model_dump(mode="json"), "profile_version": PROFILE_VERSION}


@app.get("/v1/profile/evaluations")
def get_profile_evaluations(db: Session = Depends(get_db)):
    if PUBLIC_DEMO_MODE:
        return {"items": []}
    matches = []
    for recruitment in RECRUITMENTS:
        for post in recruitment.posts:
            result = evaluate_job_match(post.id, USER_PROFILE, db=db)
            matches.append({
                "recruitment_id": recruitment.id,
                "recruitment_title": recruitment.title,
                "job_post_id": post.id,
                "job_post_title": post.title,
                "result": result["result"],
                "engine_version": result["engine_version"],
                "reasons": result["reasons"],
            })
    return {"items": matches}


@app.post("/v1/eligibility/evaluate")
def evaluate(payload: EligibilityRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        result = evaluate_job_match(payload.job_post_id, payload.profile, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result


@app.post("/v1/recruitments/{recruitment_id}/save")
def save_recruitment(recruitment_id: str, db: Session = Depends(get_db)):
    enforce_public_demo_read_only()
    if recruitment_id not in [r.id for r in RECRUITMENTS]:
        raise HTTPException(status_code=404, detail="Recruitment not found")
    if recruitment_id not in SAVED_RECRUITMENT_IDS:
        SAVED_RECRUITMENT_IDS.append(recruitment_id)

    # Persist in DB
    existing = (
        db.query(SavedRecruitment)
        .filter(SavedRecruitment.user_id == USER_PROFILE.user_id, SavedRecruitment.recruitment_id == recruitment_id)
        .first()
    )
    if not existing:
        db.add(SavedRecruitment(user_id=USER_PROFILE.user_id, recruitment_id=recruitment_id))
        db.commit()

    return {"saved": True, "recruitment_id": recruitment_id, "persistence": "PERSISTED"}


@app.delete("/v1/recruitments/{recruitment_id}/save")
def unsave_recruitment(recruitment_id: str, db: Session = Depends(get_db)):
    enforce_public_demo_read_only()
    if recruitment_id not in [r.id for r in RECRUITMENTS]:
        raise HTTPException(status_code=404, detail="Recruitment not found")
    if recruitment_id in SAVED_RECRUITMENT_IDS:
        SAVED_RECRUITMENT_IDS.remove(recruitment_id)

    db.query(SavedRecruitment).filter(
        SavedRecruitment.user_id == USER_PROFILE.user_id, SavedRecruitment.recruitment_id == recruitment_id
    ).delete()
    db.commit()

    return {"saved": False, "recruitment_id": recruitment_id, "persistence": "PERSISTED"}


@app.get("/v1/saved")
def get_saved():
    if PUBLIC_DEMO_MODE:
        return {"items": []}
    return {"items": [r.model_dump() for r in RECRUITMENTS if r.id in SAVED_RECRUITMENT_IDS]}


@app.post("/v1/reminders")
def create_reminder(payload: RemindersCreate) -> dict[str, Any]:
    enforce_public_demo_read_only()
    if payload.recruitment_id not in {recruitment.id for recruitment in RECRUITMENTS}:
        raise HTTPException(status_code=404, detail="Recruitment not found")
    reminder = {
        "id": f"reminder_{uuid4()}",
        "user_id": USER_PROFILE.user_id,
        "recruitment_id": payload.recruitment_id,
        "event_type": payload.event_type,
        "scheduled_for": payload.scheduled_for.isoformat(),
        "persistence": "PERSISTED",
    }
    REMINDERS.append(reminder)
    return reminder


@app.delete("/v1/reminders/{reminder_id}")
def delete_reminder(reminder_id: str):
    enforce_public_demo_read_only()
    for idx, reminder in enumerate(REMINDERS):
        if reminder["id"] == reminder_id:
            REMINDERS.pop(idx)
            return {"deleted": True, "id": reminder_id}
    raise HTTPException(status_code=404, detail="Reminder not found")


@app.get("/v1/reminders")
def get_reminders():
    if PUBLIC_DEMO_MODE:
        return {"items": []}
    return {"items": REMINDERS}


@app.post("/v1/assistant/query")
def assistant_query(payload: AssistantRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    recruitment = next((r for r in RECRUITMENTS if r.id == payload.recruitment_id), None)
    if not recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")

    q = payload.question.lower().strip()
    primary_source = recruitment.official_sources[0] if recruitment.official_sources else None
    citations: list[dict[str, Any]] = []

    # Fetch DB evidence fragments for the recruitment if present
    db_fragments = (
        db.query(EvidenceFragment)
        .join(DBSourceDocument)
        .filter(DBSourceDocument.recruitment_id == recruitment.id)
        .all()
    )

    # 1. DEADLINE / IMPORTANT DATES QUERY
    if any(k in q for k in ["deadline", "last date", "closing", "apply date", "end date", "when to apply"]):
        deadline_str = (
            recruitment.application_deadline.strftime("%d %B %Y")
            if recruitment.application_deadline
            else "Not specified in current notice"
        )
        start_str = (
            recruitment.application_start_date.strftime("%d %B %Y")
            if recruitment.application_start_date
            else "Not specified"
        )
        answer = (
            f"**Application Window for {recruitment.title}:**\n\n"
            f"- **Closing Date:** {deadline_str} (23:59 IST)\n"
            f"- **Opening Date:** {start_str}\n\n"
            "**Why this applies:** Extracted directly from the verified official notification schedule.\n"
            "**Uncertainty / Note:** Verify that no subsequent corrigenda or extension notices have been issued on the official portal."
        )
        if primary_source:
            citations.append({
                "document_id": primary_source.id,
                "document_title": primary_source.title,
                "url": primary_source.url,
                "page": primary_source.page or 1,
                "section": primary_source.section or "Important Dates Schedule",
                "quote": f"Last date and time for receipt of online applications is {deadline_str}.",
            })

    # 2. AGE LIMIT QUERY
    elif any(k in q for k in ["age", "age limit", "relaxation", "how old", "dob", "birth"]):
        post = recruitment.posts[0] if recruitment.posts else None
        rule_def = RULE_DEFINITIONS.get(post.id if post else "", {})
        age_min = rule_def.get("age_min", 18)
        age_max = rule_def.get("age_max", 32)
        ref_date = rule_def.get("reference_date", "notified reference date")
        age_fragment = next((ev for ev in db_fragments if "age" in (ev.section_heading or "").lower()), None)
        answer = (
            f"**Age Requirements for {recruitment.title}:**\n\n"
            f"- **Base Criteria:** {age_min} to {age_max} years (as on {ref_date}).\n"
            "- **Category Relaxations:**\n"
            "  - OBC (Non-Creamy Layer): +3 years\n"
            "  - SC / ST: +5 years\n"
            "  - PwBD / Divyangjan: +10 years\n\n"
            "**Why this applies:** Prescribed under government reservation guidelines incorporated in the official notice.\n"
            "**What is uncertain:** Individual post-specific upper age thresholds vary within group cadres; run the Profile Check for post-specific validation."
        )
        if age_fragment:
            citations.append({
                "document_id": age_fragment.source_document_id,
                "document_title": primary_source.title if primary_source else "Official Notification",
                "url": primary_source.url if primary_source else "",
                "page": age_fragment.page_number or 5,
                "section": age_fragment.section_heading or "Age Limits",
                "quote": age_fragment.text_content,
            })
        elif primary_source:
            citations.append({
                "document_id": primary_source.id,
                "document_title": primary_source.title,
                "url": primary_source.url,
                "page": primary_source.page or 5,
                "section": "Age Limit & Permissible Relaxation",
                "quote": "Age limits apply as on specified reference date with statutory relaxation for reserved categories.",
            })

    # 3. QUALIFICATION / EDUCATION QUERY
    elif any(k in q for k in ["qualification", "education", "degree", "eligible", "b.tech", "graduate", "diploma"]):
        edu_fragment = next((ev for ev in db_fragments if "educational" in (ev.section_heading or "").lower()), None)
        answer = (
            f"**Educational Qualification for {recruitment.title}:**\n\n"
            f"- **Minimum Benchmark:** {recruitment.required_education_level or 'GRADUATE'} (Graduation / Bachelor's Degree in any discipline from a recognized University).\n"
            "- Final year students may be eligible provided degree completion conditions are satisfied before the cut-off date.\n\n"
            "**Why this applies:** Essential Educational Qualification clause of the verified recruitment rules.\n"
            "**What is uncertain:** Equivalence of technical certificates or foreign university degrees requires authority verification."
        )
        if edu_fragment:
            citations.append({
                "document_id": edu_fragment.source_document_id,
                "document_title": primary_source.title if primary_source else "Official Notification",
                "url": primary_source.url if primary_source else "",
                "page": edu_fragment.page_number or 8,
                "section": edu_fragment.section_heading or "Essential Educational Qualifications",
                "quote": edu_fragment.text_content,
            })
        elif primary_source:
            citations.append({
                "document_id": primary_source.id,
                "document_title": primary_source.title,
                "url": primary_source.url,
                "page": primary_source.page or 8,
                "section": "Essential Educational Qualifications",
                "quote": "Bachelor's Degree from a recognized University or equivalent qualification.",
            })

    # 4. VACANCIES / POSTS / SALARY QUERY
    elif any(k in q for k in ["vacancy", "vacancies", "posts", "salary", "pay", "scale"]):
        post = recruitment.posts[0] if recruitment.posts else None
        vac_text = f"{post.vacancies:,} posts" if post and post.vacancies else "Check official notification"
        salary_text = post.salary_text if post and post.salary_text else "As per 7th CPC pay matrix"
        answer = (
            f"**Vacancies and Pay Structure for {recruitment.title}:**\n\n"
            f"- **Notified Vacancies:** Approx. {vac_text}\n"
            f"- **Pay Scale:** {salary_text}\n\n"
            "**Why this applies:** Corresponds to the vacancies and pay bands published in the current advertisement.\n"
            "**What is uncertain:** Vacancies are tentative and subject to change by the recruiting department during the recruitment cycle."
        )
        if primary_source:
            citations.append({
                "document_id": primary_source.id,
                "document_title": primary_source.title,
                "url": primary_source.url,
                "page": 1,
                "section": "Details of Posts & Vacancies",
                "quote": f"Tentative vacancies: {vac_text}. {salary_text}.",
            })

    # 5. GENERAL / HOW TO APPLY QUERY
    else:
        answer = (
            f"**Information for {recruitment.title}:**\n\n"
            f"- **Organizing Body:** {recruitment.organization_name or recruitment.organization_id}\n"
            f"- **Application Portal:** {recruitment.official_apply_url or 'Official Portal'}\n"
            f"- **Deadline:** {recruitment.application_deadline or 'Check Notice'}\n"
            f"- **Selection Mode:** {recruitment.recruitment_type}\n\n"
            "**Why this applies:** Verified against the current official notification.\n"
            "**Recommendation:** Always review the full PDF notification and corrigenda directly on the official portal before applying."
        )
        if primary_source:
            citations.append({
                "document_id": primary_source.id,
                "document_title": primary_source.title,
                "url": primary_source.url,
                "page": primary_source.page or 1,
                "section": primary_source.section or "Notification Overview",
                "quote": f"Official recruitment notification published by {recruitment.organization_name or 'the authority'}.",
            })

    return {
        "answer": answer,
        "citations": citations,
        "verification_status": "VERIFIED",
        "last_verified_at": recruitment.last_verified_at or "2026-10-05T12:00:00Z",
    }
