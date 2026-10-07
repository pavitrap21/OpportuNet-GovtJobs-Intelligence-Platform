# Public Sector Jobs Platform --- Logical Interpretation and Eligibility Engine

## Core Principle

> Interpretation may use AI; final evaluation must be deterministic and
> evidence-backed.

## Pipeline

``` text
Official notification
 → text/OCR
 → requirement identification
 → structured rules
 → schema validation
 → normalization
 → evidence attachment
 → human review when needed
 → deterministic evaluation
 → explanation
```

## Rule Categories

-   age
-   education
-   specialization
-   experience
-   nationality
-   domicile
-   category
-   gender
-   physical standards
-   language
-   professional registration
-   attempts
-   application dates
-   document requirements

## Operators

``` text
EQUALS
NOT_EQUALS
IN
NOT_IN
GREATER_THAN
GREATER_THAN_OR_EQUAL
LESS_THAN
LESS_THAN_OR_EQUAL
BETWEEN
CONTAINS
CONTAINS_ANY
CONTAINS_ALL
REQUIRES
EXCLUDES
DATE_BEFORE
DATE_AFTER
DATE_BETWEEN
AND
OR
NOT
```

## Example Rule

``` json
{
  "rule_type": "AGE",
  "operator": "BETWEEN",
  "parameters": {
    "min": 18,
    "max": 27,
    "reference_date": "2026-01-01"
  },
  "evidence": {
    "document_id": "doc_123",
    "page": 12,
    "section": "Age Limit"
  }
}
```

## Result Model

Never return only true/false.

``` json
{
  "status": "LIKELY_ELIGIBLE",
  "conditions": [
    {
      "name": "Age",
      "status": "PASS",
      "evidence": "Notification page 12"
    },
    {
      "name": "Education",
      "status": "PASS",
      "evidence": "Notification page 14"
    },
    {
      "name": "Specialization",
      "status": "NEEDS_VERIFICATION",
      "evidence": "Notification page 14"
    }
  ]
}
```

Allowed statuses:

-   ELIGIBLE
-   LIKELY_ELIGIBLE
-   NEEDS_VERIFICATION
-   NOT_ELIGIBLE
-   INSUFFICIENT_DATA
-   DATA_CONFLICT

## Age

Always calculate age against the notification's reference date, not
today's date.

Do not ask an LLM to perform date arithmetic.

## Category Relaxation

Do not assume generic government relaxations.

Apply a relaxation only when the specific notification supports it.

## Ambiguity

Terms such as:

-   equivalent qualification
-   relevant experience
-   recognized institution
-   related discipline
-   desirable qualification

must generate an ambiguity flag when the system cannot deterministically
resolve them.

## Explanation

The UI should answer:

### Why do I match?

-   Age satisfied
-   Education satisfied
-   Experience satisfied

### Why don't I match?

-   Mandatory age limit exceeded

### What is uncertain?

-   Specialization equivalence needs verification

## LLM Boundary

Allowed:

``` text
Natural language → candidate structured rule
```

Not allowed:

``` text
Natural language → final eligibility decision
```

The deterministic engine owns the final classification.

## Testing

Maintain a golden dataset:

``` text
notification
rules
candidate profile
expected result
evidence
```

Every eligibility-engine change must run against it.
