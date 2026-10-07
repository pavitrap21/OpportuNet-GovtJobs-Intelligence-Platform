# Public Sector Jobs Platform --- PostgreSQL Schema Design

## Modeling Principle

A recruitment is a lifecycle, not a single static job row.

``` text
Organization
  └── Recruitment
       ├── Posts
       ├── Notification
       │    └── Versions / Corrigenda
       ├── Eligibility Rules
       ├── Application Window
       └── Exam Events
```

## Core Tables

### organizations

``` sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  organization_type TEXT NOT NULL,
  parent_id UUID REFERENCES organizations(id),
  official_domain TEXT,
  state_code TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### recruitments

``` sql
CREATE TABLE recruitments (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  recruitment_type TEXT NOT NULL,
  status TEXT NOT NULL,
  published_at TIMESTAMPTZ,
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### recruitment_posts

``` sql
CREATE TABLE recruitment_posts (
  id UUID PRIMARY KEY,
  recruitment_id UUID NOT NULL REFERENCES recruitments(id),
  title TEXT NOT NULL,
  department TEXT,
  job_family TEXT,
  location_type TEXT,
  salary_min NUMERIC,
  salary_max NUMERIC,
  salary_text TEXT,
  vacancies INTEGER,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### source_documents

``` sql
CREATE TABLE source_documents (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  url TEXT NOT NULL,
  canonical_url TEXT,
  title TEXT,
  document_type TEXT,
  content_hash TEXT NOT NULL,
  version_number INTEGER NOT NULL DEFAULT 1,
  published_at TIMESTAMPTZ,
  retrieved_at TIMESTAMPTZ NOT NULL,
  parser_version TEXT,
  extraction_status TEXT NOT NULL,
  review_status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### evidence_fragments

``` sql
CREATE TABLE evidence_fragments (
  id UUID PRIMARY KEY,
  source_document_id UUID NOT NULL REFERENCES source_documents(id),
  page_number INTEGER,
  section_heading TEXT,
  text_content TEXT NOT NULL,
  normalized_text TEXT,
  embedding VECTOR,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### notifications

``` sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY,
  recruitment_id UUID NOT NULL REFERENCES recruitments(id),
  notification_number TEXT,
  notification_type TEXT NOT NULL,
  current_version_id UUID,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### notification_versions

``` sql
CREATE TABLE notification_versions (
  id UUID PRIMARY KEY,
  notification_id UUID NOT NULL REFERENCES notifications(id),
  source_document_id UUID NOT NULL REFERENCES source_documents(id),
  version_number INTEGER NOT NULL,
  effective_from TIMESTAMPTZ,
  extracted_json JSONB NOT NULL,
  extraction_confidence NUMERIC,
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### eligibility_rules

``` sql
CREATE TABLE eligibility_rules (
  id UUID PRIMARY KEY,
  recruitment_post_id UUID NOT NULL REFERENCES recruitment_posts(id),
  rule_type TEXT NOT NULL,
  operator TEXT,
  value JSONB NOT NULL,
  applies_to JSONB,
  effective_from DATE,
  effective_until DATE,
  evidence_fragment_id UUID REFERENCES evidence_fragments(id),
  confidence NUMERIC NOT NULL,
  review_status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## User Tables

``` sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  phone TEXT UNIQUE,
  auth_provider TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  date_of_birth DATE,
  gender TEXT,
  category TEXT,
  domicile_state TEXT,
  preferred_states TEXT[],
  experience_years NUMERIC,
  profile_version INTEGER NOT NULL DEFAULT 1,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_education (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  qualification_level TEXT NOT NULL,
  degree_name TEXT,
  specialization TEXT,
  institution TEXT,
  completion_year INTEGER
);
```

## Tracking

``` sql
CREATE TABLE saved_recruitments (
  user_id UUID REFERENCES users(id),
  recruitment_id UUID REFERENCES recruitments(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, recruitment_id)
);

CREATE TABLE reminders (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  recruitment_id UUID NOT NULL REFERENCES recruitments(id),
  reminder_type TEXT NOT NULL,
  scheduled_for TIMESTAMPTZ NOT NULL,
  sent_at TIMESTAMPTZ
);

CREATE TABLE applications (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  recruitment_id UUID NOT NULL REFERENCES recruitments(id),
  status TEXT NOT NULL,
  applied_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Audit

``` sql
CREATE TABLE audit_events (
  id UUID PRIMARY KEY,
  actor_type TEXT NOT NULL,
  actor_id UUID,
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  action TEXT NOT NULL,
  before_json JSONB,
  after_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Non-Negotiable Modeling Rule

Never overwrite historical recruitment facts. If a deadline changes,
preserve the previous version and make the latest effective version
current.
