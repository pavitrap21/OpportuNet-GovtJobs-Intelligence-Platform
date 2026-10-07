# Public Sector Jobs Platform --- Technology Stack

## Recommended Stack

  Layer              Technology
  ------------------ ---------------------------------------
  Web                Next.js + React + TypeScript
  UI                 Tailwind CSS + accessible components
  API                Node.js + TypeScript + Fastify/NestJS
  Validation         Zod
  Database           PostgreSQL
  Cache/Queue        Redis
  Ingestion          Python
  Parsing/OCR        Python document pipeline
  Data validation    Pydantic
  Vector retrieval   pgvector initially
  Storage            Object storage
  Deployment         Docker + managed services

## TypeScript

Use for: - UI - API - authentication - authorization - search -
profiles - saved jobs - reminders - application tracking

TypeScript owns the product-facing API contract.

## Python

Use for: - PDF parsing - OCR orchestration - document preprocessing -
structured extraction - rule extraction - batch data quality -
evaluation

Do not duplicate eligibility business rules in two languages. Share a
canonical JSON schema.

## PostgreSQL

System of record for: - recruitment data - source metadata - eligibility
rules - users - applications - evidence - audit history

Use JSONB for variable notification data, but keep frequently queried
fields relational.

## Search

MVP: PostgreSQL full-text search, trigram matching, and structured
filters.

Only introduce OpenSearch/Elasticsearch when search scale or ranking
complexity justifies it.

## Redis

Use for: - queues - rate limiting - short-lived cache - distributed
locks

Never treat Redis as permanent truth.

## AI

Use LLMs for: - document classification - structured extraction -
ambiguous language detection - user-facing explanation -
natural-language search

Do not use an LLM alone for: - deadlines - vacancies - salary - age
limits - reservation rules - final eligibility - official application
URLs

## Testing

Maintain a golden dataset of manually verified recruitment
notifications.

Run it after every parser and eligibility-engine change.

Test: - age calculations - date rules - education rules - category
exceptions - notification versioning - parser extraction - citation
correctness

## API

``` text
GET  /api/v1/recruitments
GET  /api/v1/recruitments/:id
GET  /api/v1/recruitments/:id/evidence
POST /api/v1/eligibility/check
GET  /api/v1/me/matches
POST /api/v1/saved-recruitments
POST /api/v1/reminders
POST /api/v1/copilot/query
```

Every endpoint requires schema validation, pagination where applicable,
authentication where needed, and rate limiting.

## Deployment

Start as:

``` text
Frontend
Backend
Worker
PostgreSQL
Redis
Object Storage
```

Do not start with microservices unless real operational bottlenecks
require them.
