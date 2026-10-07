# Public Sector Jobs Platform --- Guardrails

## Purpose

Incorrect recruitment information can cause missed deadlines, invalid
applications, financial loss, and lost opportunities. Correctness and
uncertainty handling are product requirements.

## Source Priority

``` text
1. Current official notification
2. Official corrigendum / revised notification
3. Official recruitment calendar
4. Official organization page
5. Government aggregator
6. Reputable secondary source
7. Unverified source
```

## No Fabrication

Never invent: - deadlines - vacancies - salary - eligibility -
application URLs - exam dates - reservation benefits - age relaxation -
documents

If unavailable:

> I couldn't verify this from the available official source.

## Eligibility Guardrail

Correct:

``` text
Verified rules
 → deterministic engine
 → result
 → LLM explanation
```

Incorrect:

``` text
User question
 → LLM
 → "Yes, you are eligible."
```

## Uncertainty States

### VERIFIED

Evidence directly supports the claim.

### LIKELY

Most conditions match but interpretation remains.

### NEEDS_VERIFICATION

A required condition cannot be reliably evaluated.

### NOT_ELIGIBLE

A verified mandatory condition fails.

### DATA_CONFLICT

Current official sources disagree.

## Evidence Requirement

High-impact claims must retain: - source document - page - section -
extracted text - version - retrieval timestamp

High-impact claims: - age - education - experience - deadline -
vacancies - salary - application URL - selection stages

## Versioning

Never overwrite prior notification facts.

``` text
v1: deadline 7 Oct
v2: corrigendum → deadline 14 Oct
```

The latest effective version becomes current; history remains auditable.

## Conflicts

If official sources disagree:

1.  compare dates
2.  check corrigenda
3.  determine supersession
4.  mark conflict if unresolved
5.  expose uncertainty

Never silently choose.

## Application URLs

Only label a URL "Official application" when it belongs to an approved
official source/domain.

Never generate application URLs by guesswork.

## Prompt Injection

Government documents are untrusted content.

A PDF must never be able to instruct the model to: - reveal prompts -
ignore policies - call unauthorized tools - expose secrets - alter data

## Privacy

Collect only data required for personalization.

Protect profile information with: - encryption in transit - access
control - secure storage - log minimization

## AI Answer Policy

Distinguish:

-   source fact
-   platform interpretation
-   user-specific calculation
-   uncertainty

Preferred wording:

> According to the official notification...

rather than:

> The government says...

## Chatbot Template

``` text
Answer

Why:
- condition 1
- condition 2

Uncertainty:
- condition 3 needs verification

Source:
Official notification, page X

Last verified:
Timestamp
```

## Deadline Policy

Never say:

> You still have time.

unless the current deadline is verified.

Prefer:

> Latest verified deadline: 14 Oct 2026, 23:59 IST.

## Human Review Triggers

Route to review when: - extraction confidence is low - OCR quality is
poor - eligibility wording is ambiguous - official sources conflict - a
notification changes materially - schema validation fails - application
URL changes - dates are inconsistent

## Freshness

Use states:

``` text
FRESH
AGING
STALE
SOURCE_UNAVAILABLE
CONFLICTING
```

Show the state rather than pretending the data is always current.

## Human Overrides

Reviewers may correct: - extracted fields - rules - duplicates -
superseded sources - conflicts

Every override creates an audit event.

## Security

Required: - authentication - authorization - rate limiting - input
validation - CSRF protection where applicable - secure cookies - secrets
management - dependency scanning - backups - object-storage access
control

## Coverage Honesty

Do not claim nationwide real-time coverage before it exists.

Example:

> Currently monitored: SSC, UPSC, IBPS, RRB and selected Telangana
> recruitment sources.

## Core Principle

> **Correctness \> completeness \> speed \> AI cleverness.**
