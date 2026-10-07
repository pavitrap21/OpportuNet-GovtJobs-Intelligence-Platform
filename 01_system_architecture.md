# Public Sector Jobs Platform --- System Architecture

## Architecture Principle

The database and official-source evidence are the source of truth. The
LLM is an explanation and interaction layer, not the authority.

## MVP Scope

Start with a limited recruitment ecosystem: SSC, UPSC, IBPS, RRB, and
one state ecosystem. National coverage is a later expansion.

## Logical Architecture

``` text
Web Client (Next.js/React/TypeScript)
              |
        API / BFF (Node)
              |
   +----------+-----------+-------------+
   |                      |             |
 Search               Eligibility     AI Copilot
   |                   Engine           |
   +----------+-----------+-------------+
              |
         PostgreSQL
     canonical recruitment
       + evidence data
              |
      Ingestion Workers
          (Python)
              |
 Official sites / PDFs / corrigenda
```

## Components

### Web

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   accessible component system

### API

-   Node.js
-   TypeScript
-   Fastify or NestJS
-   Zod validation
-   authentication and authorization

### Ingestion

-   Python workers
-   HTTP clients for simple sources
-   Playwright only where browser interaction is necessary
-   PDF extraction
-   OCR
-   Pydantic schemas
-   queue-based background processing

### Database

PostgreSQL is the system of record.

Store: - organizations - recruitments - posts - notification versions -
eligibility rules - users - saved jobs - reminders - applications -
evidence - audit events

### Object Storage

Store original PDFs and derived text/OCR artifacts. Never rely on a
third-party source remaining unchanged.

## Data Flow

``` text
Official source
 → discovery
 → download
 → hash/version detection
 → text extraction/OCR
 → structured extraction
 → schema validation
 → confidence scoring
 → human review when required
 → PostgreSQL
 → search
 → eligibility
 → alerts / AI
```

## Eligibility Flow

``` text
User profile + verified rules
 → normalization
 → deterministic evaluation
 → evidence collection
 → result
 → LLM explanation
```

## AI Flow

``` text
Question
 → intent
 → retrieve structured records + evidence
 → deterministic calculation if required
 → LLM explanation
 → citation validation
 → answer
```

## Deployment

Use a modular monolith for MVP:

``` text
Web
API
Worker
PostgreSQL
Redis
Object Storage
```

Do not begin with Kubernetes or a large microservice fleet.

## Reliability

Required: - idempotent ingestion - document hashes - versioned records -
retries - dead-letter queue - audit logs - backups - source health
monitoring

## Security

Required: - TLS - least privilege - secrets management - rate limiting -
input validation - secure file handling - audit logging - no arbitrary
server-side URL fetching

## Architecture Rules

1.  Official sources outrank secondary sources.
2.  Structured data outranks generated text.
3.  Deterministic eligibility outranks LLM judgment.
4.  Material claims must be traceable.
5.  Uncertainty must be visible.
6.  Freshness must be measurable.
7.  Human review is part of the system.
8.  Expand source coverage only after quality is proven.
