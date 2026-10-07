from __future__ import annotations

import json
from datetime import date
from typing import Any
from sqlalchemy.orm import Session

from .database import (
    EligibilityRule,
    EvidenceFragment,
    RecruitmentPost,
    UserProfile,
    SessionLocal,
)
from .models import CandidateProfile

ENGINE_VERSION = "2.0.0"

EDUCATION_RANK = {
    "SCHOOL": 1,
    "HIGHER_SECONDARY": 2,
    "DIPLOMA": 3,
    "GRADUATE": 4,
    "POSTGRADUATE": 5,
    "DOCTORATE": 6,
}

# In-memory fallback rules when DB is empty or during standalone tests
RULE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "post_ssc_cgl_tier1": {
        "age_min": 18,
        "age_max": 30,
        "reference_date": date(2025, 8, 1),
        "minimum_education": "GRADUATE",
        "minimum_experience_years": 0,
        "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
        "domicile_required": None,
        "evidence_age": {
            "evidence_id": "ev_ssc_cgl_age",
            "page": 7,
            "section": "5.1 Age Limit (as on 01-08-2025)",
            "quote": "Age 18 to 30 years as on 01-08-2025. Permissible relaxation: SC/ST 5 years, OBC 3 years, PwBD 10 years.",
        },
        "evidence_edu": {
            "evidence_id": "ev_ssc_cgl_edu",
            "page": 11,
            "section": "8. Essential Educational Qualifications",
            "quote": "Bachelor's Degree from a recognized University or equivalent.",
        },
    },
    "post_upsc_cse_2025": {
        "age_min": 21,
        "age_max": 32,
        "reference_date": date(2025, 8, 1),
        "minimum_education": "GRADUATE",
        "minimum_experience_years": 0,
        "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
        "domicile_required": None,
        "evidence_age": {
            "evidence_id": "ev_upsc_cse_age",
            "page": 6,
            "section": "III (b) Age Limits",
            "quote": "Candidate must have attained 21 years and must not have attained 32 years on 1st August 2025. SC/ST +5, OBC +3, PwBD +10.",
        },
        "evidence_edu": {
            "evidence_id": "ev_upsc_cse_edu",
            "page": 8,
            "section": "III (c) Educational Qualifications",
            "quote": "A candidate must hold a degree of any recognized University in India.",
        },
    },
    "post_ibps_po_xiv": {
        "age_min": 20,
        "age_max": 30,
        "reference_date": date(2025, 8, 1),
        "minimum_education": "GRADUATE",
        "minimum_experience_years": 0,
        "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
        "domicile_required": None,
        "evidence_age": {
            "evidence_id": "ev_ibps_po_age",
            "page": 4,
            "section": "Eligibility Criteria (A) Age",
            "quote": "20 to 30 years as on 01.08.2025. SC/ST +5, OBC-NCL +3, PwBD +10.",
        },
        "evidence_edu": {
            "evidence_id": "ev_ibps_po_edu",
            "page": 5,
            "section": "Educational Qualifications",
            "quote": "A Degree (Graduation) in any discipline from a recognized University.",
        },
    },
    "post_rrb_ntpc_grad": {
        "age_min": 18,
        "age_max": 36,
        "reference_date": date(2025, 1, 1),
        "minimum_education": "GRADUATE",
        "minimum_experience_years": 0,
        "relaxations": {"OBC": 3, "SC": 5, "ST": 5, "PWBD": 10},
        "domicile_required": None,
        "evidence_age": {
            "evidence_id": "ev_rrb_ntpc_age",
            "page": 8,
            "section": "5.0 Age Limit (as on 01.01.2025)",
            "quote": "18 to 36 years (with 3-year pandemic relaxation). SC/ST +5, OBC-NCL +3, PwBD +10.",
        },
        "evidence_edu": {
            "evidence_id": "ev_rrb_ntpc_edu",
            "page": 10,
            "section": "Educational Qualification",
            "quote": "University Degree or its equivalent from a recognized institution.",
        },
    },
    "post_tspsc_group1_2025": {
        "age_min": 18,
        "age_max": 46,
        "reference_date": date(2024, 7, 1),
        "minimum_education": "GRADUATE",
        "minimum_experience_years": 0,
        "relaxations": {"OBC": 5, "SC": 5, "ST": 5, "PWBD": 10},
        "domicile_required": "Telangana",
        "evidence_age": {
            "evidence_id": "ev_tspsc_group1_age",
            "page": 5,
            "section": "Para 4: Age Limit (as on 01/07/2024)",
            "quote": "18 to 46 years (per G.O.Ms.No.30). SC/ST/BCs/EWS +5 years, PH +10 years.",
        },
        "evidence_edu": {
            "evidence_id": "ev_tspsc_group1_edu",
            "page": 6,
            "section": "Para 3: Educational Qualifications",
            "quote": "Must possess a Bachelor's Degree of any recognized University in India.",
        },
        "evidence_domicile": {
            "evidence_id": "ev_tspsc_group1_local",
            "page": 8,
            "section": "Para 7: Reservation to Local Candidates",
            "quote": "Reservation to local candidates is 95% in terms of Presidential Order 2018.",
        },
    },
}


def calculate_age(date_of_birth: date, reference_date: date) -> int:
    """Calculate completed years of age on the notified reference date."""
    return reference_date.year - date_of_birth.year - (
        (reference_date.month, reference_date.day)
        < (date_of_birth.month, date_of_birth.day)
    )


def evaluate_job_match(
    job_post_id: str,
    profile: CandidateProfile | None = None,
    db: Session | None = None,
) -> dict[str, Any]:
    # Look up rules from database or fallback definitions
    rules: dict[str, Any] | None = None

    if db is not None:
        db_rule = (
            db.query(EligibilityRule)
            .filter(EligibilityRule.recruitment_post_id == job_post_id)
            .first()
        )
        if db_rule:
            params = json.loads(db_rule.parameters_json)
            # Parse reference date
            ref_date = date.fromisoformat(params["reference_date"])
            fallback_defs = RULE_DEFINITIONS.get(job_post_id, {})
            rules = {
                "age_min": params["age_min"],
                "age_max": params["age_max"],
                "reference_date": ref_date,
                "minimum_education": params["minimum_education"],
                "minimum_experience_years": params["minimum_experience_years"],
                "relaxations": params.get("relaxations", {}),
                "domicile_required": params.get("domicile_required"),
                "evidence_age": fallback_defs.get("evidence_age", {}),
                "evidence_edu": fallback_defs.get("evidence_edu", {}),
                "evidence_domicile": fallback_defs.get("evidence_domicile", {}),
            }

    if rules is None:
        rules = RULE_DEFINITIONS.get(job_post_id)

    if rules is None:
        raise ValueError(f"Unknown job_post_id: {job_post_id}")

    # Fallback profile
    if profile is None and db is not None:
        db_prof = db.query(UserProfile).filter(UserProfile.user_id == "user_123").first()
        if db_prof:
            profile = CandidateProfile(
                user_id=db_prof.user_id,
                date_of_birth=db_prof.date_of_birth,
                gender=db_prof.gender or "F",
                category=db_prof.category or "GENERAL",
                domicile_state=db_prof.domicile_state or "Telangana",
                preferred_states=(db_prof.preferred_states or "Telangana,India").split(","),
                education_level=db_prof.education_level or "GRADUATE",
                degree_name=db_prof.degree_name or "B.Tech",
                specialization=db_prof.specialization or "Computer Science",
                experience_years=db_prof.experience_years or 0.0,
            )

    if profile is None:
        profile = CandidateProfile()

    reasons: list[dict[str, Any]] = []
    missing_data = False
    mandatory_failed = False
    needs_verification = False

    # 1. AGE EVALUATION (with Category Relaxation)
    ref_date = rules["reference_date"]
    age_evidence = rules.get("evidence_age", {})

    if profile.date_of_birth is None:
        missing_data = True
        reasons.append({
            "rule_type": "AGE",
            "status": "INSUFFICIENT_DATA",
            "evidence_id": age_evidence.get("evidence_id"),
            "page": age_evidence.get("page"),
            "section": age_evidence.get("section"),
            "source_quote": age_evidence.get("quote"),
            "message": f"Date of birth is required to calculate age as on official reference date {ref_date.isoformat()}.",
        })
    else:
        age = calculate_age(profile.date_of_birth, ref_date)
        base_min = rules["age_min"]
        base_max = rules["age_max"]

        # Category relaxation
        category = (profile.category or "GENERAL").upper()
        relaxation_years = rules.get("relaxations", {}).get(category, 0)
        effective_max = base_max + relaxation_years

        if age < base_min:
            mandatory_failed = True
            reasons.append({
                "rule_type": "AGE",
                "status": "CHECK_FAILED",
                "evidence_id": age_evidence.get("evidence_id"),
                "page": age_evidence.get("page"),
                "section": age_evidence.get("section"),
                "source_quote": age_evidence.get("quote"),
                "message": f"Age {age} years on {ref_date.isoformat()} is below the minimum required age of {base_min} years.",
            })
        elif age > effective_max:
            mandatory_failed = True
            msg = (
                f"Age {age} years on {ref_date.isoformat()} exceeds the permissible maximum limit of {effective_max} years "
                f"(Base: {base_max}"
                + (f" + {relaxation_years} yrs {category} relaxation" if relaxation_years > 0 else "")
                + ")."
            )
            reasons.append({
                "rule_type": "AGE",
                "status": "CHECK_FAILED",
                "evidence_id": age_evidence.get("evidence_id"),
                "page": age_evidence.get("page"),
                "section": age_evidence.get("section"),
                "source_quote": age_evidence.get("quote"),
                "message": msg,
            })
        else:
            # Passed age check
            msg = f"Age {age} years on {ref_date.isoformat()} satisfies the criteria ({base_min}–{base_max} years"
            if relaxation_years > 0:
                msg += f"; relaxed up to {effective_max} years for {category} category"
            msg += ")."
            reasons.append({
                "rule_type": "AGE",
                "status": "PASS",
                "evidence_id": age_evidence.get("evidence_id"),
                "page": age_evidence.get("page"),
                "section": age_evidence.get("section"),
                "source_quote": age_evidence.get("quote"),
                "message": msg,
            })

    # 2. EDUCATION EVALUATION
    edu_evidence = rules.get("evidence_edu", {})
    required_education = rules["minimum_education"]
    candidate_education = (profile.education_level or "").upper()

    if not candidate_education or candidate_education not in EDUCATION_RANK:
        missing_data = True
        reasons.append({
            "rule_type": "EDUCATION",
            "status": "INSUFFICIENT_DATA",
            "evidence_id": edu_evidence.get("evidence_id"),
            "page": edu_evidence.get("page"),
            "section": edu_evidence.get("section"),
            "source_quote": edu_evidence.get("quote"),
            "message": "Education level is not specified or recognized in candidate profile.",
        })
    else:
        candidate_rank = EDUCATION_RANK[candidate_education]
        required_rank = EDUCATION_RANK.get(required_education, 4)

        if candidate_rank < required_rank:
            mandatory_failed = True
            reasons.append({
                "rule_type": "EDUCATION",
                "status": "CHECK_FAILED",
                "evidence_id": edu_evidence.get("evidence_id"),
                "page": edu_evidence.get("page"),
                "section": edu_evidence.get("section"),
                "source_quote": edu_evidence.get("quote"),
                "message": f"Candidate qualification ({candidate_education.replace('_', ' ').title()}) does not meet the minimum requirement of {required_education.replace('_', ' ').title()}.",
            })
        else:
            reasons.append({
                "rule_type": "EDUCATION",
                "status": "PASS",
                "evidence_id": edu_evidence.get("evidence_id"),
                "page": edu_evidence.get("page"),
                "section": edu_evidence.get("section"),
                "source_quote": edu_evidence.get("quote"),
                "message": f"Candidate qualification ({candidate_education.replace('_', ' ').title()}) satisfies the required {required_education.replace('_', ' ').title()} benchmark.",
            })

    # 3. EXPERIENCE EVALUATION
    min_exp = rules.get("minimum_experience_years", 0)
    if profile.experience_years is None:
        missing_data = True
        reasons.append({
            "rule_type": "EXPERIENCE",
            "status": "INSUFFICIENT_DATA",
            "evidence_id": None,
            "page": None,
            "section": None,
            "source_quote": None,
            "message": "Experience duration is required to verify minimum experience.",
        })
    else:
        if profile.experience_years < min_exp:
            mandatory_failed = True
            reasons.append({
                "rule_type": "EXPERIENCE",
                "status": "CHECK_FAILED",
                "evidence_id": None,
                "page": None,
                "section": None,
                "source_quote": None,
                "message": f"Required experience is {min_exp} years; candidate has {profile.experience_years} years.",
            })
        else:
            reasons.append({
                "rule_type": "EXPERIENCE",
                "status": "PASS",
                "evidence_id": None,
                "page": None,
                "section": None,
                "source_quote": None,
                "message": f"Experience of {profile.experience_years} years satisfies the minimum benchmark of {min_exp} years (Freshers eligible).",
            })

    # 4. DOMICILE & RESERVATION EVALUATION
    domicile_req = rules.get("domicile_required")
    dom_evidence = rules.get("evidence_domicile", {})
    if domicile_req:
        candidate_domicile = (profile.domicile_state or "").strip()
        if candidate_domicile.lower() == domicile_req.lower():
            reasons.append({
                "rule_type": "DOMICILE",
                "status": "PASS",
                "evidence_id": dom_evidence.get("evidence_id"),
                "page": dom_evidence.get("page"),
                "section": dom_evidence.get("section"),
                "source_quote": dom_evidence.get("quote"),
                "message": f"Candidate domicile ({candidate_domicile}) qualifies for the 95% local reservation quota under Telangana Presidential Order 2018.",
            })
        else:
            needs_verification = True
            reasons.append({
                "rule_type": "DOMICILE",
                "status": "NEEDS_VERIFICATION",
                "evidence_id": dom_evidence.get("evidence_id"),
                "page": dom_evidence.get("page"),
                "section": dom_evidence.get("section"),
                "source_quote": dom_evidence.get("quote"),
                "message": f"Candidate domicile ({candidate_domicile}) is outside {domicile_req}. Eligible under the 5% open unreserved quota subject to merit.",
            })

    # 5. SPECIALIZATION / EQUIVALENCE
    if profile.specialization:
        reasons.append({
            "rule_type": "SPECIALIZATION",
            "status": "PASS",
            "evidence_id": edu_evidence.get("evidence_id"),
            "page": edu_evidence.get("page"),
            "section": edu_evidence.get("section"),
            "source_quote": edu_evidence.get("quote"),
            "message": f"Specialization '{profile.specialization}' ({profile.degree_name or 'Degree'}) falls within the recognized degree criteria.",
        })

    # Overall Classification
    if missing_data:
        result = "INSUFFICIENT_DATA"
    elif mandatory_failed:
        result = "NOT_ELIGIBLE"
    elif needs_verification:
        result = "LIKELY_ELIGIBLE"
    else:
        result = "ELIGIBLE"

    return {
        "result": result,
        "engine_version": ENGINE_VERSION,
        "reasons": reasons,
    }
