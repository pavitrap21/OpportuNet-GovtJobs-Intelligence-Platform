# MVP API Contract

Base path: `/v1`

## Authentication

### POST `/auth/register`
Creates a user.

### POST `/auth/login`
Authenticates a user and establishes a session.

### POST `/auth/logout`
Terminates the current session.

### POST `/auth/refresh`
Rotates a refresh token where token-based authentication is used.

## Profile

### GET `/profile`
Returns the current candidate profile.

### PUT `/profile`
Updates candidate data and increments `profile_version`.

### GET `/profile/evaluations`
Returns current eligibility evaluations for saved/eligible jobs.

## Recruitments

### GET `/recruitments`

Query parameters:
- `q`
- `organization_id`
- `status`
- `education_level`
- `location`
- `deadline_before`
- `deadline_after`
- `page`
- `page_size`

### GET `/recruitments/{id}`
Returns the recruitment detail, current job posts, verification state and official sources.

### GET `/recruitments/{id}/sources`
Returns official source documents and provenance metadata.

### GET `/recruitments/{id}/events`
Returns published recruitment lifecycle/change events.

## Eligibility

### POST `/eligibility/evaluate`

Request:
```json
{
  "job_post_id": "uuid"
}
```

Response:
```json
{
  "result": "LIKELY_MATCH",
  "engine_version": "1.0.0",
  "reasons": [
    {
      "rule_type": "AGE",
      "status": "PASS",
      "evidence_id": "uuid"
    },
    {
      "rule_type": "SPECIALIZATION",
      "status": "NEEDS_VERIFICATION",
      "evidence_id": "uuid"
    }
  ]
}
```

## Saved jobs

### POST `/recruitments/{id}/save`
### DELETE `/recruitments/{id}/save`
### GET `/saved`

## Reminders

### POST `/reminders`
```json
{
  "recruitment_id": "uuid",
  "event_type": "DEADLINE",
  "scheduled_for": "2026-10-15T09:00:00+05:30"
}
```

### DELETE `/reminders/{id}`
### GET `/reminders`

## Assistant

### POST `/assistant/query`

Request:
```json
{
  "recruitment_id": "uuid",
  "question": "What is the last date to apply?"
}
```

Response:
```json
{
  "answer": "The last date shown in the verified source is ...",
  "citations": [
    {
      "document_id": "uuid",
      "page": 3,
      "section": "Important Dates"
    }
  ],
  "verification_status": "VERIFIED",
  "last_verified_at": "2026-10-03T10:05:00Z"
}
```

## Error contract

```json
{
  "error": {
    "code": "RECRUITMENT_SOURCE_UNAVAILABLE",
    "message": "The official source could not be verified right now.",
    "request_id": "req_..."
  }
}
```
