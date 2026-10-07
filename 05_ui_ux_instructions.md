# Public Sector Jobs Platform --- UI/UX Instructions

## UX Goal

The user should quickly answer:

1.  What jobs are open?
2.  Can I apply?
3.  Why?
4.  What is the deadline?
5.  What do I need next?
6.  Where is the official source?

## Design Direction

Modern, calm, information-dense, trustworthy.

Avoid: - flashing banners - fake urgency - ad-heavy layouts -
unexplained AI recommendations - government-portal visual clutter

## Homepage

Primary sections:

-   search
-   personalized matches
-   closing soon
-   recently updated
-   upcoming exams

## Recruitment Card

``` text
SSC CHSL 2026
Staff Selection Commission

✓ Likely eligible

Last date: 14 Oct 2026
Vacancies: 2,741

Last verified: 2 hours ago

[View details] [Save]
```

## Detail Page

Top:

``` text
SSC CHSL 2026
Staff Selection Commission

Likely eligible

Deadline: 14 Oct 2026

[Apply on official site]
```

Sections: - overview - posts - eligibility - salary - selection
process - dates - documents - vacancies - evidence - updates

## Eligibility UI

``` text
Your eligibility

LIKELY ELIGIBLE

✓ Age
23 / maximum 27

✓ Education
B.Tech

✓ Experience
Not required

⚠ Specialization
Needs verification

[See why]
```

Use plain language.

## Evidence

For material facts:

``` text
Age limit: 18–27

Source:
Official notification
Page 12
Verified 05 Oct 2026

[View evidence]
```

## Confidence Labels

Use: - Verified - Likely match - Needs verification - Not a match - Data
conflict

Never use: - "AI thinks you qualify"

## Filters

Prioritize: - qualification - age - state - organization - job type -
salary - deadline - exam - experience - category

## Profile

Collect only what is required:

1.  DOB/age
2.  education
3.  specialization
4.  experience
5.  category/domicile where relevant
6.  preferences

## Dashboard

Action-oriented:

``` text
3 jobs need attention

Deadline tomorrow
SSC CHSL
[Apply]

Saved jobs
Upcoming exams
Recent updates
```

## Copilot

Make it contextual rather than a blank chat.

Suggested prompts: - Why am I eligible? - What documents do I need? -
Compare these exams - What changed in this notification? - Show jobs I
can apply for

Answers must show evidence.

## Mobile

Primary actions: - search - match - save - reminder - official apply -
evidence

Bottom navigation:

``` text
Home | Search | Saved | Alerts | Profile
```

## Accessibility

Target WCAG 2.1 AA-level practices:

-   keyboard navigation
-   semantic HTML
-   visible focus
-   sufficient contrast
-   labels
-   error messaging
-   screen-reader support
-   responsive text
-   no color-only status

## Trust UX

Prefer:

> Last verified 2h ago

over:

> 100% accurate

Prefer:

> Official source

over:

> AI verified

## Error State

If stale:

> This recruitment may have changed. Last verified: 18 hours ago.

If conflicting:

> Information conflict detected. We found different values across
> official documents.

## UX Rule

Every screen should answer:

> What should the user do next?
