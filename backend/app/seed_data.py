from __future__ import annotations

import json
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from .database import (
    Base,
    EligibilityRule,
    EvidenceFragment,
    Notification,
    Organization,
    Recruitment,
    RecruitmentPost,
    SourceDocument,
    User,
    UserProfile,
    engine,
)

ORGANIZATIONS_DATA = [
    {
        "id": "org_ssc",
        "name": "Staff Selection Commission",
        "slug": "staff-selection-commission",
        "organization_type": "CENTRAL_RECRUITMENT_BODY",
        "official_domain": "ssc.gov.in",
        "state_code": "IN",
    },
    {
        "id": "org_upsc",
        "name": "Union Public Service Commission",
        "slug": "union-public-service-commission",
        "organization_type": "CONSTITUTIONAL_BODY",
        "official_domain": "upsc.gov.in",
        "state_code": "IN",
    },
    {
        "id": "org_ibps",
        "name": "Institute of Banking Personnel Selection",
        "slug": "institute-of-banking-personnel-selection",
        "organization_type": "AUTONOMOUS_BANKING_AGENCY",
        "official_domain": "ibps.in",
        "state_code": "IN",
    },
    {
        "id": "org_rrb",
        "name": "Railway Recruitment Boards",
        "slug": "railway-recruitment-boards",
        "organization_type": "MINISTRY_OF_RAILWAYS",
        "official_domain": "rrbapply.gov.in",
        "state_code": "IN",
    },
    {
        "id": "org_tspsc",
        "name": "Telangana Public Service Commission",
        "slug": "telangana-public-service-commission",
        "organization_type": "STATE_PSC",
        "official_domain": "tspsc.gov.in",
        "state_code": "TG",
    },
]

RECRUITMENTS_DATA = [
    {
        "id": "recruitment_ssc_cgl",
        "organization_id": "org_ssc",
        "title": "SSC CGL Examination 2025-26",
        "slug": "ssc-cgl-2025",
        "recruitment_type": "EXAM",
        "status": "ACTIVE",
        "published_at": datetime(2025, 6, 24, 10, 0, tzinfo=timezone.utc),
        "last_verified_at": datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        "application_start_date": date(2025, 6, 24),
        "application_deadline": date(2025, 7, 27),
        "exam_date": date(2025, 9, 15),
        "official_apply_url": "https://ssc.gov.in/",
        "required_education_level": "GRADUATE",
        "verification_status": "VERIFIED",
        "posts": [
            {
                "id": "post_ssc_cgl_tier1",
                "title": "Combined Graduate Level Group B & C Posts",
                "department": "Ministries/Departments of Govt. of India",
                "job_family": "Administrative & Inspection",
                "location_type": "All India",
                "salary_min": 35400,
                "salary_max": 142400,
                "salary_text": "Pay Level 4 to Level 7 (₹25,500 – ₹1,42,400)",
                "vacancies": 17727,
                "description": "Recruitment to various Group B and Group C posts in ministries, attached and subordinate offices of the Government of India.",
                "rules": {
                    "age_min": 18,
                    "age_max": 30,
                    "reference_date": "2025-08-01",
                    "minimum_education": "GRADUATE",
                    "minimum_experience_years": 0,
                    "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
                    "domicile_required": None,
                },
            }
        ],
        "source_document": {
            "id": "doc_ssc_cgl_notice_2025",
            "title": "SSC CGL 2025 Official Notification (Notice No. 3/1/2024-P&P-I)",
            "url": "https://ssc.gov.in/api/attachment/uploads/masterData/NoticeBoard/Notice_CGL_2025.pdf",
            "document_type": "NOTIFICATION",
            "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "version_number": 1,
            "page": 7,
            "section": "Clause 5: Age Limit & Essential Qualification",
            "evidence": [
                {
                    "id": "ev_ssc_cgl_age",
                    "page_number": 7,
                    "section_heading": "5.1 Age Limit (as on 01-08-2025)",
                    "text_content": "Requirement of age for various posts is 18 to 30 years as on 01-08-2025. Permissible relaxation in upper age limit for SC/ST is 5 years, for OBC is 3 years, and for PwBD is 10 years.",
                },
                {
                    "id": "ev_ssc_cgl_edu",
                    "page_number": 11,
                    "section_heading": "8. Essential Educational Qualifications",
                    "text_content": "Bachelor's Degree from a recognized University or equivalent. Candidates appearing in the final year may also apply provided they acquire essential qualification on or before cut-off date.",
                },
            ],
        },
    },
    {
        "id": "recruitment_upsc_cse",
        "organization_id": "org_upsc",
        "title": "UPSC Civil Services Examination (CSE) 2025",
        "slug": "upsc-cse-2025",
        "recruitment_type": "EXAM",
        "status": "ACTIVE",
        "published_at": datetime(2025, 1, 22, 10, 0, tzinfo=timezone.utc),
        "last_verified_at": datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        "application_start_date": date(2025, 1, 22),
        "application_deadline": date(2025, 2, 11),
        "exam_date": date(2025, 5, 25),
        "official_apply_url": "https://upsconline.nic.in/",
        "required_education_level": "GRADUATE",
        "verification_status": "VERIFIED",
        "posts": [
            {
                "id": "post_upsc_cse_2025",
                "title": "Civil Services (IAS, IPS, IFS & Allied Services)",
                "department": "Department of Personnel and Training",
                "job_family": "All India & Central Civil Services",
                "location_type": "All India",
                "salary_min": 56100,
                "salary_max": 250000,
                "salary_text": "Pay Level 10 (₹56,100 starting basic pay) up to Apex Level",
                "vacancies": 1056,
                "description": "Recruitment to Indian Administrative Service, Indian Foreign Service, Indian Police Service and Central Services Group A & B.",
                "rules": {
                    "age_min": 21,
                    "age_max": 32,
                    "reference_date": "2025-08-01",
                    "minimum_education": "GRADUATE",
                    "minimum_experience_years": 0,
                    "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
                    "domicile_required": None,
                },
            }
        ],
        "source_document": {
            "id": "doc_upsc_cse_notice_2025",
            "title": "UPSC Civil Services Examination 2025 Rules (Gazette Notification No. 01/2025-CSP)",
            "url": "https://upsc.gov.in/sites/default/files/Notification-CSP-2025-engl.pdf",
            "document_type": "NOTIFICATION",
            "content_hash": "c85d713063530089e37c2b54077c9f1ecf101fb57c201db744a3799d85e72db8",
            "version_number": 1,
            "page": 6,
            "section": "Section III: Eligibility Conditions",
            "evidence": [
                {
                    "id": "ev_upsc_cse_age",
                    "page_number": 6,
                    "section_heading": "III (b) Age Limits",
                    "text_content": "A candidate must have attained the age of 21 years and must not have attained the age of 32 years on the 1st of August 2025. Age relaxation: up to 5 years for SC/ST, up to 3 years for OBC, up to 10 years for PwBD.",
                },
                {
                    "id": "ev_upsc_cse_edu",
                    "page_number": 8,
                    "section_heading": "III (c) Minimum Educational Qualifications",
                    "text_content": "A candidate must hold a degree of any of the Universities incorporated by an Act of the Central or State Legislature in India or other educational institutions established by an Act of Parliament.",
                },
            ],
        },
    },
    {
        "id": "recruitment_ibps_po",
        "organization_id": "org_ibps",
        "title": "IBPS CRP PO/MT-XIV (Probationary Officers)",
        "slug": "ibps-po-xiv-2025",
        "recruitment_type": "EXAM",
        "status": "ACTIVE",
        "published_at": datetime(2025, 8, 1, 9, 0, tzinfo=timezone.utc),
        "last_verified_at": datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        "application_start_date": date(2025, 8, 1),
        "application_deadline": date(2025, 8, 28),
        "exam_date": date(2025, 10, 19),
        "official_apply_url": "https://ibps.in/",
        "required_education_level": "GRADUATE",
        "verification_status": "VERIFIED",
        "posts": [
            {
                "id": "post_ibps_po_xiv",
                "title": "Probationary Officer / Management Trainee (CRP PO/MT-XIV)",
                "department": "Participating Public Sector Commercial Banks",
                "job_family": "Public Sector Banking",
                "location_type": "All India",
                "salary_min": 48170,
                "salary_max": 85000,
                "salary_text": "Scale I Officer (₹48,480 starting basic pay + DA/HRA/Perks)",
                "vacancies": 3955,
                "description": "Common Recruitment Process for selection of Probationary Officers / Management Trainees in 11 participating public sector banks.",
                "rules": {
                    "age_min": 20,
                    "age_max": 30,
                    "reference_date": "2025-08-01",
                    "minimum_education": "GRADUATE",
                    "minimum_experience_years": 0,
                    "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
                    "domicile_required": None,
                },
            }
        ],
        "source_document": {
            "id": "doc_ibps_po_xiv",
            "title": "IBPS Detailed Advertisement for CRP PO/MT-XIV",
            "url": "https://www.ibps.in/crp-po-mt-xiv-notification.pdf",
            "document_type": "NOTIFICATION",
            "content_hash": "a425f381c1c92a95c4793f7da21e64627d3516cf4c95f190e4a9e5c464ef6590",
            "version_number": 1,
            "page": 4,
            "section": "Eligibility Criteria: Age & Education",
            "evidence": [
                {
                    "id": "ev_ibps_po_age",
                    "page_number": 4,
                    "section_heading": "Eligibility Criteria (A) Age (As on 01.08.2025)",
                    "text_content": "Minimum: 20 years, Maximum: 30 years. i.e. A candidate must have been born not earlier than 02.08.1995 and not later than 01.08.2005 (both dates inclusive). Upper age relaxation: SC/ST 5 years, OBC (NCL) 3 years, PwBD 10 years.",
                },
                {
                    "id": "ev_ibps_po_edu",
                    "page_number": 5,
                    "section_heading": "(B) Educational Qualifications",
                    "text_content": "A Degree (Graduation) in any discipline from a University recognized by the Govt. Of India or any equivalent qualification recognized as such by the Central Government.",
                },
            ],
        },
    },
    {
        "id": "recruitment_rrb_ntpc",
        "organization_id": "org_rrb",
        "title": "RRB NTPC Graduate Level Posts (CEN 05/2024)",
        "slug": "rrb-ntpc-graduate-2024-25",
        "recruitment_type": "EXAM",
        "status": "ACTIVE",
        "published_at": datetime(2024, 9, 14, 10, 0, tzinfo=timezone.utc),
        "last_verified_at": datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        "application_start_date": date(2024, 9, 14),
        "application_deadline": date(2024, 10, 20),
        "exam_date": date(2025, 4, 10),
        "official_apply_url": "https://www.rrbapply.gov.in/",
        "required_education_level": "GRADUATE",
        "verification_status": "VERIFIED",
        "posts": [
            {
                "id": "post_rrb_ntpc_grad",
                "title": "Station Master, Goods Train Manager, Chief Commercial Clerk",
                "department": "Indian Railways (All Zonal Railways)",
                "job_family": "Railway Operations & Commercial",
                "location_type": "Zonal Railways (National)",
                "salary_min": 29200,
                "salary_max": 92300,
                "salary_text": "Pay Level 5 & Level 6 (₹29,200 – ₹92,300)",
                "vacancies": 8113,
                "description": "Centralized Employment Notice for Graduate Posts under Non-Technical Popular Categories in Indian Railways.",
                "rules": {
                    "age_min": 18,
                    "age_max": 36,
                    "reference_date": "2025-01-01",
                    "minimum_education": "GRADUATE",
                    "minimum_experience_years": 0,
                    "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
                    "domicile_required": None,
                },
            }
        ],
        "source_document": {
            "id": "doc_rrb_ntpc_cen05",
            "title": "RRB Centralized Employment Notice CEN 05/2024",
            "url": "https://www.rrbapply.gov.in/documents/CEN_05_2024_NTPC_Grad.pdf",
            "document_type": "NOTIFICATION",
            "content_hash": "b2f0a1d48c8b671a53b5d2634e0c4a45a6878bc591c28c6e2697a5b3a4d6f81e",
            "version_number": 1,
            "page": 8,
            "section": "Age Limit & Educational Qualifications",
            "evidence": [
                {
                    "id": "ev_rrb_ntpc_age",
                    "page_number": 8,
                    "section_heading": "5.0 Age Limit (as on 01.01.2025)",
                    "text_content": "18 to 36 years (including 3 years one-time age relaxation beyond the prescribed upper age limit of 33 years due to Covid-19 pandemic). Relaxation: SC/ST 5 years, OBC-NCL 3 years, PwBD 10 years.",
                },
                {
                    "id": "ev_rrb_ntpc_edu",
                    "page_number": 10,
                    "section_heading": "Minimum Educational Qualification",
                    "text_content": "University Degree or its equivalent. Typing proficiency required for typist posts.",
                },
            ],
        },
    },
    {
        "id": "recruitment_tspsc_group1",
        "organization_id": "org_tspsc",
        "title": "TSPSC Group-I Services Recruitment 2024-25",
        "slug": "tspsc-group-i-2024",
        "recruitment_type": "RECRUITMENT",
        "status": "ACTIVE",
        "published_at": datetime(2024, 2, 23, 11, 0, tzinfo=timezone.utc),
        "last_verified_at": datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        "application_start_date": date(2024, 2, 23),
        "application_deadline": date(2024, 3, 14),
        "exam_date": date(2024, 10, 21),
        "official_apply_url": "https://www.tspsc.gov.in/",
        "required_education_level": "GRADUATE",
        "verification_status": "VERIFIED",
        "posts": [
            {
                "id": "post_tspsc_group1_2025",
                "title": "Deputy Collector, DSP, Commercial Tax Officer, RDO",
                "department": "Telangana State Civil Administration",
                "job_family": "State Civil Services",
                "location_type": "Telangana",
                "salary_min": 51320,
                "salary_max": 150000,
                "salary_text": "Scale of Pay ₹51,320 – ₹1,37,050 / ₹54,220 – ₹1,50,000",
                "vacancies": 563,
                "description": "Direct recruitment to Group-I Services in the State of Telangana under the Telangana Public Service Commission.",
                "rules": {
                    "age_min": 18,
                    "age_max": 46,
                    "reference_date": "2024-07-01",
                    "minimum_education": "GRADUATE",
                    "minimum_experience_years": 0,
                    "relaxations": {"OBC": 5, "SC": 5, "ST": 5, "PWBD": 10},
                    "domicile_required": "Telangana",
                },
            }
        ],
        "source_document": {
            "id": "doc_tspsc_group1_notif",
            "title": "TSPSC Group-I Services Detailed Notification (No. 02/2024)",
            "url": "https://www.tspsc.gov.in/notifications/022024_GroupI.pdf",
            "document_type": "NOTIFICATION",
            "content_hash": "f456789abcde0123456789abcdef0123456789abcdef0123456789abcdef0123",
            "version_number": 1,
            "page": 5,
            "section": "Age & Educational Qualifications",
            "evidence": [
                {
                    "id": "ev_tspsc_group1_age",
                    "page_number": 5,
                    "section_heading": "Para 4: Age Limit (as on 01/07/2024)",
                    "text_content": "Minimum 18 years & Maximum 46 years (as per G.O.Ms.No.30, GA (Ser.A) Dept., Dt. 08/02/2024 raising maximum age limit by two years). Telangana State Govt employees: up to 5 years, SC/ST/BCs/EWS: 5 years, Physically Handicapped: 10 years.",
                },
                {
                    "id": "ev_tspsc_group1_edu",
                    "page_number": 6,
                    "section_heading": "Para 3: Educational Qualifications",
                    "text_content": "Must possess a Bachelor's Degree of any recognized University in India established or incorporated by or under a Central Act, Provincial Act or a State Act.",
                },
                {
                    "id": "ev_tspsc_group1_local",
                    "page_number": 8,
                    "section_heading": "Para 7: Reservation to Local Candidates",
                    "text_content": "Reservation to local candidates is 95% in terms of Telangana Public Employment (Organization of Local Cadres and Regulation of Direct Recruitment) Order, 2018.",
                },
            ],
        },
    },
]


def seed_database(db: Session) -> None:
    # Check if already seeded
    if db.query(Organization).count() > 0:
        return

    # Seed Organizations
    for org_data in ORGANIZATIONS_DATA:
        org = Organization(**org_data)
        db.add(org)
    db.commit()

    # Seed Recruitments, Posts, SourceDocs, Evidence, Rules
    for rec_data in RECRUITMENTS_DATA:
        posts_data = rec_data.get("posts", [])
        src_data = rec_data.get("source_document")

        rec = Recruitment(
            id=rec_data["id"],
            organization_id=rec_data["organization_id"],
            title=rec_data["title"],
            slug=rec_data["slug"],
            recruitment_type=rec_data["recruitment_type"],
            status=rec_data["status"],
            published_at=rec_data["published_at"],
            last_verified_at=rec_data["last_verified_at"],
            application_start_date=rec_data["application_start_date"],
            application_deadline=rec_data["application_deadline"],
            exam_date=rec_data["exam_date"],
            official_apply_url=rec_data["official_apply_url"],
            required_education_level=rec_data["required_education_level"],
            verification_status=rec_data["verification_status"],
        )
        db.add(rec)
        db.commit()

        # Add Source Document & Evidence
        if src_data:
            doc = SourceDocument(
                id=src_data["id"],
                recruitment_id=rec.id,
                organization_id=rec.organization_id,
                title=src_data["title"],
                url=src_data["url"],
                document_type=src_data["document_type"],
                content_hash=src_data["content_hash"],
                version_number=src_data["version_number"],
                page=src_data.get("page"),
                section=src_data.get("section"),
                retrieved_at=rec_data["last_verified_at"],
            )
            db.add(doc)
            db.commit()

            evidence_items = src_data.get("evidence", [])
            for ev in evidence_items:
                evidence_obj = EvidenceFragment(
                    id=ev["id"],
                    source_document_id=doc.id,
                    page_number=ev["page_number"],
                    section_heading=ev["section_heading"],
                    text_content=ev["text_content"],
                )
                db.add(evidence_obj)
            db.commit()

        # Add Posts and Eligibility Rules
        for p_data in posts_data:
            post = RecruitmentPost(
                id=p_data["id"],
                recruitment_id=rec.id,
                title=p_data["title"],
                department=p_data.get("department"),
                job_family=p_data.get("job_family"),
                location_type=p_data.get("location_type"),
                salary_min=p_data.get("salary_min"),
                salary_max=p_data.get("salary_max"),
                salary_text=p_data.get("salary_text"),
                vacancies=p_data.get("vacancies"),
                description=p_data.get("description"),
            )
            db.add(post)
            db.commit()

            rules_data = p_data.get("rules", {})
            rule = EligibilityRule(
                recruitment_post_id=post.id,
                rule_type="COMBINED_CRITERIA",
                operator="AND",
                parameters_json=json.dumps(rules_data),
                confidence=1.0,
                review_status="VERIFIED",
            )
            db.add(rule)
            db.commit()

    # Seed Default User & Profile
    default_user = User(id="user_123", email="candidate@civiccareers.in")
    db.add(default_user)
    db.commit()

    default_profile = UserProfile(
        user_id="user_123",
        date_of_birth=date(1995, 6, 12),
        gender="F",
        category="GENERAL",
        domicile_state="Telangana",
        preferred_states="Telangana,India",
        education_level="GRADUATE",
        degree_name="B.Tech",
        specialization="Computer Science",
        experience_years=2.0,
        profile_version=1,
    )
    db.add(default_profile)
    db.commit()
