from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class EvidenceCitation(BaseModel):
    document_id: str
    document_title: str | None = None
    url: str | None = None
    page: int | None = None
    section: str | None = None
    quote: str | None = None


class SourceDocument(BaseModel):
    id: str
    title: str
    url: str
    document_type: str
    version_number: int = 1
    published_at: str | None = None
    page: int | None = None
    section: str | None = None
    verification_status: str = "VERIFIED"


class RecruitmentPost(BaseModel):
    id: str
    title: str
    department: str | None = None
    job_family: str | None = None
    location_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_text: str | None = None
    vacancies: int | None = None
    description: str | None = None


class Recruitment(BaseModel):
    id: str
    organization_id: str
    organization_name: str | None = None
    title: str
    slug: str
    recruitment_type: str
    status: str
    published_at: str | None = None
    last_verified_at: str | None = None
    application_start_date: date | None = None
    application_deadline: date | None = None
    exam_date: date | None = None
    official_apply_url: str | None = None
    required_education_level: str | None = None
    verification_status: str = "VERIFIED"
    posts: list[RecruitmentPost] = Field(default_factory=list)
    official_sources: list[SourceDocument] = Field(default_factory=list)


class EligibilityAudit(BaseModel):
    rule_type: str
    status: Literal["PASS", "CHECK_FAILED", "NEEDS_VERIFICATION", "INSUFFICIENT_DATA"]
    evidence_id: str | None = None
    page: int | None = None
    section: str | None = None
    source_quote: str | None = None
    message: str


class CandidateProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = "user_123"
    date_of_birth: date | None = date(1995, 6, 12)
    category: str = "GENERAL"  # GENERAL, OBC, SC, ST, EWS, PWBD
    domicile_state: str = "Telangana"
    preferred_states: list[str] = ["Telangana", "India"]
    education_level: str = "GRADUATE"  # SCHOOL, HIGHER_SECONDARY, DIPLOMA, GRADUATE, POSTGRADUATE, DOCTORATE
    degree_name: str = "B.Tech"
    specialization: str = "Computer Science"
    experience_years: float | None = Field(default=2.0, ge=0, le=60)
    gender: str = "F"


class EligibilityRequest(BaseModel):
    job_post_id: str
    profile: CandidateProfile | None = None


class EligibilityResponse(BaseModel):
    result: Literal[
        "ELIGIBLE",
        "LIKELY_ELIGIBLE",
        "NEEDS_VERIFICATION",
        "NOT_ELIGIBLE",
        "INSUFFICIENT_DATA",
        "DATA_CONFLICT",
    ]
    engine_version: str
    reasons: list[EligibilityAudit]


class RemindersCreate(BaseModel):
    recruitment_id: str
    event_type: Literal["DEADLINE", "EXAM_DATE", "DOCUMENT_CHECK"]
    scheduled_for: datetime


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class AssistantRequest(BaseModel):
    recruitment_id: str
    question: str = Field(min_length=1, max_length=1000)


class AssistantResponse(BaseModel):
    answer: str
    citations: list[EvidenceCitation] = Field(default_factory=list)
    verification_status: str
    last_verified_at: str | None = None
