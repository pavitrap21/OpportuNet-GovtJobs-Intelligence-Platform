from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Generator
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./govjobs.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    organization_type = Column(Text, nullable=False)
    parent_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    official_domain = Column(Text, nullable=True)
    state_code = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    recruitments = relationship("Recruitment", back_populates="organization")


class Recruitment(Base):
    __tablename__ = "recruitments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    title = Column(Text, nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    recruitment_type = Column(Text, nullable=False)  # EXAM, DIRECT, DEPUTATION
    status = Column(Text, nullable=False)  # ACTIVE, UPCOMING, CLOSED, SAMPLE
    published_at = Column(DateTime, nullable=True)
    last_verified_at = Column(DateTime, nullable=True)
    application_start_date = Column(Date, nullable=True)
    application_deadline = Column(Date, nullable=True)
    exam_date = Column(Date, nullable=True)
    official_apply_url = Column(Text, nullable=True)
    required_education_level = Column(Text, nullable=True)
    verification_status = Column(Text, default="VERIFIED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="recruitments")
    posts = relationship("RecruitmentPost", back_populates="recruitment", cascade="all, delete-orphan")
    source_documents = relationship("SourceDocument", back_populates="recruitment", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recruitment", cascade="all, delete-orphan")


class RecruitmentPost(Base):
    __tablename__ = "recruitment_posts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recruitment_id = Column(String(36), ForeignKey("recruitments.id"), nullable=False)
    title = Column(Text, nullable=False)
    department = Column(Text, nullable=True)
    job_family = Column(Text, nullable=True)
    location_type = Column(Text, nullable=True)
    salary_min = Column(Numeric, nullable=True)
    salary_max = Column(Numeric, nullable=True)
    salary_text = Column(Text, nullable=True)
    vacancies = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    recruitment = relationship("Recruitment", back_populates="posts")
    eligibility_rules = relationship("EligibilityRule", back_populates="post", cascade="all, delete-orphan")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recruitment_id = Column(String(36), ForeignKey("recruitments.id"), nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    url = Column(Text, nullable=False)
    canonical_url = Column(Text, nullable=True)
    title = Column(Text, nullable=False)
    document_type = Column(Text, nullable=False)  # NOTIFICATION, CORRIGENDUM, PORTAL, SYLLABUS
    content_hash = Column(Text, nullable=False)
    version_number = Column(Integer, default=1)
    published_at = Column(DateTime, nullable=True)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    page = Column(Integer, nullable=True)
    section = Column(Text, nullable=True)
    parser_version = Column(Text, nullable=True)
    extraction_status = Column(Text, default="SUCCESS")
    review_status = Column(Text, default="VERIFIED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    recruitment = relationship("Recruitment", back_populates="source_documents")
    evidence_fragments = relationship("EvidenceFragment", back_populates="source_document", cascade="all, delete-orphan")


class EvidenceFragment(Base):
    __tablename__ = "evidence_fragments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_document_id = Column(String(36), ForeignKey("source_documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    section_heading = Column(Text, nullable=True)
    text_content = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    source_document = relationship("SourceDocument", back_populates="evidence_fragments")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recruitment_id = Column(String(36), ForeignKey("recruitments.id"), nullable=False)
    notification_number = Column(Text, nullable=True)
    notification_type = Column(Text, nullable=False)
    status = Column(Text, default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    recruitment = relationship("Recruitment", back_populates="notifications")


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recruitment_post_id = Column(String(36), ForeignKey("recruitment_posts.id"), nullable=False)
    rule_type = Column(Text, nullable=False)  # AGE, EDUCATION, EXPERIENCE, CATEGORY_RELAXATION, DOMICILE, GENDER
    operator = Column(Text, nullable=True)
    parameters_json = Column(Text, nullable=False)  # JSON-encoded rule details
    evidence_fragment_id = Column(String(36), ForeignKey("evidence_fragments.id"), nullable=True)
    confidence = Column(Float, default=1.0)
    review_status = Column(Text, default="VERIFIED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    post = relationship("RecruitmentPost", back_populates="eligibility_rules")
    evidence_fragment = relationship("EvidenceFragment")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), unique=True, nullable=True)
    auth_provider = Column(Text, default="local")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Text, default="F")
    category = Column(Text, default="GENERAL")
    domicile_state = Column(Text, default="Telangana")
    preferred_states = Column(Text, default="Telangana,India")  # Comma separated
    education_level = Column(Text, default="GRADUATE")
    degree_name = Column(Text, default="B.Tech")
    specialization = Column(Text, default="Computer Science")
    experience_years = Column(Float, default=2.0)
    profile_version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")


class SavedRecruitment(Base):
    __tablename__ = "saved_recruitments"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    recruitment_id = Column(String(36), ForeignKey("recruitments.id"), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recruitment_id = Column(String(36), ForeignKey("recruitments.id"), nullable=False)
    reminder_type = Column(Text, nullable=False)  # DEADLINE, EXAM_DATE, DOCUMENT_CHECK
    scheduled_for = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
