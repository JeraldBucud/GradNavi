# GradNavi Skill Gap and Readiness Scoring Design

Status: Approved Version 1 design for WBS 5.5 Skill Gap and Readiness Scoring Logic.

## 1. Purpose

This document defines the Version 1 design for GradNavi Skill Gap and Career Readiness scoring.

WBS 5.5 compares a Student's canonical Skills and recorded proficiency levels with source-backed Career requirements from GradNavi Dataset 1.0.

The service produces:

- A Career Readiness Score from 0.00 to 100.00 when sufficient evidence exists.
- A Skill Gap Analysis for one selected Career.
- Per-Skill readiness details for explanation and later API use.
- Explicit status values when the Student Profile or Career evidence is insufficient.

The scoring logic is deterministic.

The same structured Student Profile, Career, and reference dataset inputs must produce the same numerical result.

## 2. WBS Alignment

This design supports:

```text
WBS 5.5 Skill Gap and Readiness Scoring Logic
Owner: Jerald
```

Primary predecessor:

```text
WBS 5.3 Weighted Recommendation Engine
Owner: Jerald
```

Related Sprint 2 tasks:

```text
WBS 5.4 Career Recommendation API
Owner: MD

WBS 5.6 Recommendation and Readiness Interface
Owner: Joyee

WBS 5.7 Learning Suggestions and Roadmap API
Owner: MD

WBS 5.9 Sprint 2 Integration and Testing
Owner: All Members
```

WBS 5.7 depends on WBS 5.5.

WBS 5.9 depends on WBS 5.5 together with the other required Sprint 2 implementation tasks.

## 3. Related Functional Requirements

### FR-05 Skill-Gap Analysis

GradNavi compares the Student's current Skills with the requirements of a selected Career.

### FR-06 Career-Readiness Score

GradNavi calculates a Career Readiness Score using documented deterministic rules.

The WBS 5.5 output also supports later work for:

- FR-11 Learning Suggestions.
- FR-12 Career Roadmap.

## 4. Design Principles

WBS 5.5 follows these rules:

1. Readiness scoring stays deterministic.
2. Student proficiency affects WBS 5.5 only.
3. WBS 5.3 recommendation scores stay unchanged.
4. Career-side requirements come from source-backed O*NET evidence.
5. Missing Student Skills represent zero demonstrated proficiency for readiness scoring.
6. Missing Student Profile data does not produce a misleading zero readiness score.
7. Missing Career evidence does not produce a misleading zero readiness score.
8. Technology explanation evidence from WBS 5.3 does not enter the Version 1 readiness formula.
9. Skill-gap ordering stays deterministic.
10. Core scoring logic stays separate from HTTP request handling.

## 5. Dataset 1.0 Preflight Findings

The WBS 5.5 read-only preflight against `gradnavi_db` confirmed:

```text
Active Careers: 36

Eligible O*NET numerical evidence rows: 1849

Rows with normalized Importance: 1849
Rows with normalized Level: 1849
Rows with both Importance and Level: 1849

Importance-only rows: 0
Level-only rows: 0
Rows with neither: 0

Duplicate readiness evidence rows: 0

Careers with readiness evidence: 35
Careers without readiness evidence: 1
```

The Career without readiness evidence is:

```text
Health Information Manager
```

Readiness evidence concept types:

```text
knowledge: 820
skill: 1029
```

O*NET source-domain totals:

```text
onet_essential_skills: 333
onet_knowledge: 820
onet_transferable_skills: 696
```

Normalized Level distribution:

```text
Minimum: 5.43
Median: 43.00
Maximum: 91.86
```

Normalized Importance distribution:

```text
Minimum: 6.25
Median: 47.00
Maximum: 98.75
```

The preflight performed no database writes.

## 6. Student Proficiency Mapping

GradNavi StudentSkill records use four approved proficiency levels.

Version 1 maps them to numerical readiness values as follows:

| Student Proficiency | Numerical Value |
| --- | ---: |
| Foundational | 25 |
| Developing | 50 |
| Proficient | 75 |
| Advanced | 100 |
| Missing Skill | 0 |

Stored StudentSkill values remain:

```text
foundational
developing
proficient
advanced
```

The numerical mapping exists only inside WBS 5.5 readiness calculations.

It does not change the stored StudentSkill value.

## 7. Career Requirement Input

Version 1 readiness scoring uses approved O*NET evidence where both fields are present:

```text
normalized_importance
normalized_level
```

`normalized_importance` represents the weight of the Career requirement.

`normalized_level` represents the required Career-side level on a 0 to 100 scale.

Eligible source domains are:

```text
onet_essential_skills
onet_knowledge
onet_transferable_skills
```

Eligible evidence must satisfy all of these rules:

- CareerSkill review status is approved.
- ReferenceDataset status is active.
- Reference source is O*NET Database.
- Source domain is one of the approved numerical domains.
- `normalized_importance` is present.
- `normalized_level` is present.
- `not_relevant` is false.
- `recommend_suppress` is not true.

## 8. Technology Evidence Boundary

Technology evidence does not enter Version 1 readiness scoring.

WBS 5.3 already returns O*NET technology matches as explanation evidence.

Dataset 1.0 does not provide a directly comparable Career-side proficiency requirement for those technology explanation rows.

For this reason:

```text
Technology matches support explanation.
Technology matches do not change readiness_score.
```

## 9. Per-Skill Attainment

For every eligible Career requirement:

```text
student_score =
mapped Student proficiency value
```

If the Student does not have the canonical Skill:

```text
student_score = 0
```

The Career requirement is:

```text
required_level =
O*NET normalized Level
```

Per-Skill attainment is:

```text
attainment_ratio =
student_score / required_level
```

The ratio is capped at 1.00:

```text
capped_attainment =
min(attainment_ratio, 1.00)
```

Per-Skill attainment percentage is:

```text
attainment_percentage =
capped_attainment * 100
```

A Student who exceeds the required level receives full attainment for the requirement.

Exceeding the requirement does not create readiness above 100 percent for that Skill.

## 10. Weighted Readiness Contribution

Each Career requirement uses O*NET normalized Importance as its weight.

For one Skill:

```text
weighted_readiness_contribution =
normalized_importance * capped_attainment
```

A fully met requirement contributes its full normalized Importance.

A partially met requirement contributes a proportional share.

A missing Skill contributes zero.

## 11. Overall Career Readiness Formula

For one selected Career:

```text
total_weight =
sum(normalized_importance for all eligible Career requirements)
```

```text
achieved_weight =
sum(weighted_readiness_contribution for all eligible Career requirements)
```

```text
readiness_score =
achieved_weight / total_weight * 100
```

The returned readiness score is rounded to two decimal places.

Valid scored range:

```text
0.00 to 100.00
```

## 12. Example Calculation

Career requirement:

```text
Skill: Critical Thinking
Normalized Importance: 72.00
Required Level: 58.86
```

Student proficiency:

```text
Proficient
Mapped Student Score: 75
```

Attainment:

```text
75 / 58.86 = 1.274...
```

After the 1.00 cap:

```text
capped_attainment = 1.00
```

Weighted contribution:

```text
72.00 * 1.00 = 72.00
```

The Student fully meets this Career requirement.

Second example:

```text
Skill: Computers and Electronics
Normalized Importance: 93.75
Required Level: 89.00
```

Student proficiency:

```text
Developing
Mapped Student Score: 50
```

Attainment:

```text
50 / 89 = 0.561797...
```

Weighted contribution:

```text
93.75 * 0.561797... = 52.668...
```

The Student partially meets this Career requirement.

## 13. Skill Gap Status

Every eligible Career requirement receives one deterministic gap status.

### `missing`

The Student does not have the canonical Skill.

Rules:

```text
student_score = 0
gap_amount = required_level
attainment_percentage = 0
```

### `below_requirement`

The Student has the Skill, but the mapped proficiency value is below the required O*NET Level.

Rules:

```text
0 < student_score < required_level
gap_amount = required_level - student_score
```

### `meets_requirement`

The Student's mapped proficiency value meets or exceeds the required O*NET Level.

Rules:

```text
student_score >= required_level
gap_amount = 0
attainment_percentage = 100
```

## 14. Skill Gap Output

Each Skill Gap item should expose structured data for later API serialization.

Recommended fields:

```text
career_skill_id
skill_id
skill_name
concept_type
student_proficiency
student_score
required_level
importance
gap_amount
attainment_percentage
gap_status
```

The backend service returns structured data.

WBS 5.6 decides how the frontend displays the result.

## 15. Skill Gap Ordering

Skill gaps use deterministic ordering.

Order:

1. Missing Skills.
2. Below-requirement Skills.
3. Higher O*NET normalized Importance.
4. Larger gap amount.
5. Skill name alphabetically.
6. Skill ID ascending as the final stable tie rule.

Skills that meet the requirement stay available in the full readiness breakdown but should follow unresolved gaps in gap-focused views.

## 16. Score Status

WBS 5.5 uses explicit readiness status values.

### `scored`

The Student Profile has at least one StudentSkill record and the Career has eligible readiness evidence.

The service returns:

```text
readiness_score = 0.00 to 100.00
```

A readiness score of 0.00 is valid when the Student has profile Skills but none contribute readiness toward the selected Career.

### `insufficient_profile`

The Student Profile has zero StudentSkill records.

The service returns:

```text
readiness_score = null
```

This state means there is not enough Student evidence to interpret zero as a valid readiness result.

### `insufficient_evidence`

The selected Career has no eligible source-backed readiness evidence.

The service returns:

```text
readiness_score = null
```

Dataset 1.0 currently produces this state for:

```text
Health Information Manager
```

## 17. Missing Skill Behaviour

A missing Skill means:

```text
Student does not have a StudentSkill record for the canonical Skill.
```

For readiness calculation:

```text
student_score = 0
attainment = 0
weighted contribution = 0
```

The Skill also appears in the Skill Gap Analysis with:

```text
gap_status = missing
```

## 18. Readiness and Recommendation Separation

WBS 5.3 answers:

```text
How strongly does the Student's known Skill set align
with the source-backed competencies for this Career?
```

WBS 5.5 answers:

```text
How closely does the Student's demonstrated proficiency
meet the source-backed required levels for this Career?
```

WBS 5.5 must not change:

- WBS 5.3 recommendation score.
- WBS 5.3 ranking.
- WBS 5.3 tie handling.
- WBS 5.3 explanation evidence.

The two scores serve different purposes.

## 19. Service-Layer Boundary

WBS 5.5 should use a dedicated service module.

Planned location:

```text
backend/careers/services/readiness_scoring.py
```

The service should own:

- Student proficiency conversion.
- Career readiness evidence loading.
- Per-Skill attainment calculation.
- Skill Gap classification.
- Weighted readiness calculation.
- Deterministic gap ordering.
- Structured readiness result generation.

The service should not own:

- HTTP request parsing.
- Authentication.
- Serializer formatting.
- Frontend presentation.
- Learning-resource selection.
- AI-generated explanations.

## 20. Database Boundary

WBS 5.5 should read existing records.

Primary inputs:

```text
StudentSkill
Skill
Career
CareerSkill
CareerSkillEvidence
ReferenceDataset
ReferenceSource
```

Version 1 does not require writing aggregate readiness values back into:

```text
CareerSkill.importance_score
CareerSkill.required_level_score
CareerSkill.required_proficiency
```

The source-backed values stay in CareerSkillEvidence.

No new database model is required by the approved Version 1 formula unless implementation reveals a persistence requirement outside the current WBS scope.

## 21. Numerical Validation Rules

The scoring service should reject invalid scoring inputs.

Required checks include:

- Student numerical proficiency stays between 0 and 100.
- O*NET normalized Importance stays between 0 and 100.
- O*NET normalized Level stays greater than 0 and at most 100.
- A CareerSkill must not contribute duplicate readiness evidence.
- Total weight must be greater than zero before calculating a scored result.
- Readiness score must stay between 0 and 100.
- Gap amount must not be negative.
- Attainment must stay between 0 and 1.

## 22. Determinism

The same structured inputs must produce the same result.

Deterministic behaviour applies to:

- Student proficiency conversion.
- Evidence filtering.
- Per-Skill attainment.
- Weighted contribution.
- Overall readiness score.
- Gap classification.
- Gap ordering.
- Numerical rounding.

No generative AI service participates in the WBS 5.5 numerical calculation.

## 23. Planned Unit Tests

The pure scoring layer should test:

- Foundational mapping to 25.
- Developing mapping to 50.
- Proficient mapping to 75.
- Advanced mapping to 100.
- Missing Skill mapping to 0.
- Full requirement attainment.
- Partial requirement attainment.
- Requirement exceeded and capped at full attainment.
- Missing Skill gap.
- Below-requirement gap.
- Meets-requirement status.
- Weighted readiness calculation.
- Zero achieved readiness.
- Invalid Student proficiency value.
- Invalid Importance value.
- Invalid required Level value.
- Duplicate CareerSkill readiness evidence.
- Deterministic gap ordering.
- Two-decimal readiness rounding.

## 24. Planned Database Tests

Database-backed tests should verify:

- StudentSkill proficiency loading.
- Canonical Skill matching.
- O*NET eligibility filtering.
- Active ReferenceDataset filtering.
- ReviewStatus filtering.
- `not_relevant` exclusion.
- `recommend_suppress` exclusion.
- Importance and Level presence requirements.
- Skill and knowledge evidence inclusion.
- Technology evidence exclusion.
- One selected Career readiness calculation.
- Missing Student Profile Skill behaviour.
- Career without readiness evidence behaviour.

## 25. Integration Expectations

WBS 5.5 output should support:

### WBS 5.6

Recommendation and Readiness Interface.

Expected frontend data includes:

- Readiness score.
- Score status.
- Missing Skills.
- Below-requirement Skills.
- Met requirements.
- Required levels.
- Student proficiency.
- Gap values.

### WBS 5.7

Learning Suggestions and Roadmap API.

WBS 5.7 should use unresolved Skill gaps from WBS 5.5 as structured input for learning-resource selection and roadmap ordering.

### WBS 5.9

Sprint 2 Integration and Testing.

Integration should verify consistent flow across:

```text
Student Profile
-> WBS 5.3 Recommendation Engine
-> WBS 5.4 Recommendation API
-> WBS 5.5 Readiness Scoring
-> WBS 5.6 Interface
-> WBS 5.7 Learning Suggestions
-> WBS 5.8 Learning Roadmap Interface
```

## 26. Version 1 Decisions

Approved WBS 5.5 decisions:

### Decision 1

Return both:

- Skill Gap Analysis.
- Career Readiness Score.

### Decision 2

Use O*NET normalized Level directly as the Career-side numerical requirement.

### Decision 3

Use this Student proficiency mapping:

```text
Foundational = 25
Developing = 50
Proficient = 75
Advanced = 100
Missing = 0
```

### Decision 4

Use only approved O*NET numerical evidence where both normalized Importance and normalized Level are present.

### Decision 5

A Student Profile with zero StudentSkill records receives:

```text
status = insufficient_profile
readiness_score = null
```

### Decision 6

A Career with no eligible readiness evidence receives:

```text
status = insufficient_evidence
readiness_score = null
```

### Decision 7

Missing Student Skills receive zero demonstrated proficiency for readiness scoring.

### Decision 8

Technology evidence stays outside the Version 1 numerical readiness formula.

### Decision 9

Unresolved gaps are ordered by:

```text
missing
below_requirement
higher Importance
larger gap
Skill name
Skill ID
```

### Decision 10

WBS 5.5 does not modify WBS 5.3 recommendation scores or rankings.

## 27. Definition of Ready

WBS 5.5 implementation is ready when:

- WBS 5.3 is merged.
- Dataset 1.0 is available.
- StudentSkill proficiency values are confirmed.
- O*NET normalized Importance coverage is confirmed.
- O*NET normalized Level coverage is confirmed.
- Duplicate readiness evidence is checked.
- Student proficiency mapping is approved.
- Missing-data behaviour is approved.
- Gap ordering is approved.
- Readiness formula is approved.

These conditions are satisfied for Version 1.

## 28. Definition of Done

WBS 5.5 is complete when:

- The approved readiness formula is implemented.
- Skill Gap Analysis is implemented.
- Student proficiency mapping is implemented.
- Source-backed evidence filtering is implemented.
- Missing profile handling is implemented.
- Missing Career evidence handling is implemented.
- Gap ordering is deterministic.
- Numerical validation is implemented.
- Automated WBS 5.5 tests pass.
- Full backend tests pass.
- Django system checks pass.
- No unintended migration changes exist.
- Real Dataset 1.0 read-only validation passes.
- Documentation matches implemented behaviour.
- The implementation is reviewed and merged into `feature/sprint-2`.
