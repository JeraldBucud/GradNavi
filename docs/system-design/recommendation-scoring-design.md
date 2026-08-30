# GradNavi Recommendation Scoring Design

Status: Approved Version 1 design for WBS 5.3 Weighted Recommendation Engine.

## 1. Purpose

This document defines the design for the GradNavi Weighted Recommendation Engine.

The recommendation engine compares structured Student Profile information with structured Career reference data and produces ranked career recommendations.

The engine uses deterministic weighted rules.

The same approved structured inputs and scoring configuration must produce the same numerical result.

This document defines:

- Scoring responsibilities.
- Required inputs.
- Expected outputs.
- Factor scoring structure.
- Weighting structure.
- Ranking behaviour.
- Explainability requirements.
- Missing-data behaviour.
- Validation rules.
- Service-layer boundaries.
- Testing requirements.
- Dependencies on other Sprint 2 work.

Version 1 uses deterministic canonical Skill matching weighted by source-backed O*NET normalized Importance. Student proficiency is reserved for WBS 5.5 readiness scoring.

## 2. Related Documents

This design aligns with:

- `backend/docs/BACKEND_ARCHITECTURE.md`
- `docs/system-design/rest-api-design.md`
- `docs/project-management/work-breakdown-structure.md`
- `docs/project-management/task-leads.md`
- `docs/project-management/product-backlog.md`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/requirements-assignment-matrix.md`

## 3. WBS Alignment

This design supports:

```text
WBS 5.3 Weighted Recommendation Engine
Owner: Jerald
```

WBS 5.3 depends on:

```text
WBS 5.2 Career and Skill Reference Data
Owner: MD
```

Related Sprint 2 work includes:

```text
WBS 5.4 Career Recommendation API
Owner: MD

WBS 5.5 Skill Gap and Readiness Scoring Logic
Owner: Jerald

WBS 5.6 Recommendation and Readiness Interface
Owner: Joyee

WBS 5.9 Sprint 2 Integration and Testing
Owner: All Members
```

The recommendation engine must not introduce Career or Skill database structures that conflict with WBS 5.2.

Final model integration must follow the approved Career and Skill reference-data structure.

## 4. Related Functional Requirements

### FR-03 Career Recommendations

GradNavi provides ranked career recommendations based on Student Profile information.

### FR-04 Recommendation Explanation

GradNavi provides recommendation scores and understandable reasons for each result.

The scoring design also supports later Sprint 2 work for:

### FR-05 Skill-Gap Analysis

GradNavi compares Student skills with the requirements of a selected Career.

### FR-06 Career-Readiness Score

GradNavi calculates readiness through documented scoring rules.

## 5. Architectural Principles

The recommendation engine follows these rules:

1. Numerical recommendation scores use deterministic logic.
2. Scoring rules must be documented.
3. Identical structured inputs must produce identical numerical results.
4. Recommendation scoring stays separate from HTTP request handling.
5. Recommendation scoring stays separate from generative AI.
6. The engine returns a factor breakdown for explainability.
7. Core scoring behaviour requires automated unit tests.
8. Student-owned information stays protected by backend authentication and permission rules.
9. Frontend behaviour does not control numerical recommendation logic.
10. Core scoring logic should stay separate from database-specific operations where practical.

## 6. High-Level Scoring Flow

```text
Structured Student Profile
          |
          v
Student Scoring Input
          |
          |
          +----------------------+
                                 |
                                 v
                     Career Reference Data
                                 |
                                 v
                       Career Scoring Input
                                 |
                                 v
                  Recommendation Scoring Service
                                 |
                  +--------------+--------------+
                  |                             |
                  v                             v
             Factor Scores              Factor Breakdown
                  |
                  v
             Weighted Score
                  |
                  v
             Career Ranking
                  |
                  v
        Ranked Recommendations
                  |
                  v
       Optional Explanation Layer
```

The explanation layer does not determine the numerical recommendation score.

## 7. Student Profile Input

The recommendation engine receives structured Student Profile information.

Current GradNavi profile areas include:

- Skills.
- Interests.
- Education.
- Experience.
- Projects.
- Career goals.
- Personality responses.

The final recommendation score does not need to include every available profile area.

Only approved factors should affect numerical recommendation results.

## 8. Student Skill Proficiency

GradNavi StudentSkill records use these proficiency values:

- Foundational.
- Developing.
- Proficient.
- Advanced.

The stored API values are:

```text
foundational
developing
proficient
advanced
```

Student proficiency does not change the WBS 5.3 Version 1 numerical recommendation score.

WBS 5.3 answers:

```text
How strongly does the Student's known Skill set align
with the source-backed competencies for this Career?
```

Student proficiency is reserved for:

```text
WBS 5.5 Skill Gap and Readiness Scoring Logic
```

This separation prevents WBS 5.3 from assigning proficiency multipliers without an approved Career-side required proficiency value.

The existing proficiency sequence remains available for WBS 5.5:

```text
Foundational
Developing
Proficient
Advanced
```

No WBS 5.3 numerical multiplier is assigned to these levels.

## 9. Career Reference Input

Career reference information comes from the approved WBS 5.2 Dataset 1.0 structure.

WBS 5.3 uses:

```text
Career
CareerSkill
CareerSkillEvidence
Skill
```

Canonical Skill identifiers connect StudentSkill and CareerSkill.

The Version 1 numerical score uses O*NET evidence rows that contain normalized Importance values.

Current Dataset 1.0 evidence also contains:

- O*NET software technology relationships without numerical Importance or Level values.
- ESCO essential and optional relationships.

Those relationships support structured explanations in Version 1 but do not receive invented numerical weights.

Career-side interests, education, experience, projects, career goals, and personality reference structures are not part of Dataset 1.0.

Those profile areas do not affect the WBS 5.3 Version 1 numerical score.

## 10. Recommendation Scoring Factors

The approved WBS 5.3 Version 1 numerical factor is:

| Factor | Student Source | Career Source | Version 1 Use |
| --- | --- | --- | --- |
| Skills and knowledge | StudentSkill | O*NET numerical CareerSkillEvidence | Numerical score |
| Technologies | StudentSkill | O*NET software evidence | Explanation only |
| ESCO essential relationships | StudentSkill | ESCO CareerSkillEvidence | Explanation only |
| ESCO optional relationships | StudentSkill | ESCO CareerSkillEvidence | Explanation only |
| Interests | Student Profile | No approved Career-side Dataset 1.0 structure | Excluded |
| Education | Student Profile | No approved Career-side Dataset 1.0 structure | Excluded |
| Experience | Student Profile | No approved Career-side Dataset 1.0 structure | Excluded |
| Projects | Student Profile | No approved Career-side Dataset 1.0 structure | Excluded |
| Career goals | Student Profile | No approved Career-side Dataset 1.0 structure | Excluded |
| Personality responses | Student Profile | No approved Career-side Dataset 1.0 structure | Excluded |

Version 1 does not convert missing source information into estimated weights.

Only source-backed numerical O*NET Importance values contribute to the numerical recommendation score.

## 11. Factor Score Range

The approved WBS 5.3 Version 1 recommendation-score range is:

```text
0.00 to 100.00
```

Interpretation:

```text
0.00
No weighted numerical Career competencies are matched.

100.00
All weighted numerical Career competencies are matched.
```

Intermediate values represent the proportion of total source-backed O*NET Importance covered by the Student's canonical Skill matches.

A null score is different from zero.

```text
recommendation_score = null
```

means the Career has insufficient numerical evidence for the Version 1 scoring method.

## 12. Weighting Model

WBS 5.3 Version 1 does not assign hand-written factor weights.

Each eligible CareerSkill receives its source-backed O*NET normalized Importance value as its scoring weight.

Conceptually:

```text
CareerSkill weight
    =
O*NET normalized Importance
```

The service does not assign artificial numerical values to:

- Student proficiency.
- O*NET software technologies.
- ESCO essential relationships.
- ESCO optional relationships.
- Interests.
- Education.
- Experience.
- Projects.
- Career goals.
- Personality responses.

This keeps the Version 1 numerical score traceable to the approved reference dataset.

## 13. Weight Validation

Version 1 validates source-backed scoring evidence.

Validation covers:

- CareerSkill review status must be approved.
- O*NET normalized Importance must be present for a numerical contribution.
- Normalized Importance must stay within the approved 0 to 100 evidence range.
- Evidence marked not relevant must not enter scoring.
- Evidence marked recommend suppress must not enter scoring.
- A CareerSkill must not be counted more than once in the numerical denominator.
- Ambiguous duplicate numerical O*NET evidence for one CareerSkill must not be silently double-counted.
- A Career with no eligible numerical O*NET evidence receives insufficient-evidence status.

Invalid evidence must not silently produce a misleading recommendation score.

## 14. Weighted Score Formula

For one Career, let each eligible numerical CareerSkill have:

```text
w_i = O*NET normalized Importance
```

Let:

```text
m_i = 1
```

when the Student has the same canonical Skill identifier.

Otherwise:

```text
m_i = 0
```

The matched weighted total is:

```text
matched_weight
    =
sum(w_i * m_i)
```

The total available weight is:

```text
total_weight
    =
sum(w_i)
```

The Version 1 recommendation score is:

```text
recommendation_score
    =
(matched_weight / total_weight) * 100
```

This formula is used only when:

```text
total_weight > 0
```

If the Career has no eligible numerical O*NET evidence:

```text
score_status = insufficient_evidence
recommendation_score = null
```

Student proficiency does not multiply the score in WBS 5.3 Version 1.

The formula measures weighted Career-fit coverage, not Career readiness.

## 15. Structural Example

Example Career evidence:

```text
Skill A normalized Importance = 80
Skill B normalized Importance = 60
Skill C normalized Importance = 40
```

Student canonical Skill matches:

```text
Skill A = matched
Skill B = matched
Skill C = missing
```

Calculation:

```text
matched_weight
    =
80 + 60
    =
140

total_weight
    =
80 + 60 + 40
    =
180

recommendation_score
    =
140 / 180 * 100
    =
77.78
```

Student proficiency does not change this WBS 5.3 score.

Proficiency-based readiness belongs to WBS 5.5.

## 16. Missing Profile Data

WBS 5.3 Version 1 requires at least one StudentSkill record before ranking Careers.

If the Student has no StudentSkill records:

```text
score_status = insufficient_profile
```

The service must not return a list of zero-score Careers as if a meaningful comparison occurred.

Missing interests, education, experience, projects, career goals, and personality responses do not block WBS 5.3 Version 1 because those areas are not numerical scoring factors.

For an individual Career with no eligible numerical O*NET evidence:

```text
score_status = insufficient_evidence
recommendation_score = null
```

Zero and null therefore have different meanings:

```text
0.00
Valid numerical evidence exists, but none of its weighted competencies matched.

null
The Version 1 numerical scoring method lacks enough Career evidence.
```

## 17. Skill Comparison

WBS 5.3 Version 1 uses canonical Skill identifiers.

The core comparison is:

```text
StudentSkill.skill_id
        ==
CareerSkill.skill_id
```

Free-text names do not determine numerical matches.

Aliases and external identifiers are resolved into canonical Skill records by the WBS 5.2 reference-data layer before recommendation scoring.

For numerical scoring, the CareerSkill must have eligible O*NET evidence containing normalized Importance.

Technology and ESCO relationships are collected separately for explanation.

## 18. Proficiency Comparison

Student proficiency is not part of the WBS 5.3 Version 1 recommendation formula.

Reason:

- Dataset 1.0 CareerSkill required_proficiency values are not populated.
- Dataset 1.0 CareerSkill required_level_score values are not populated.
- Assigning Foundational, Developing, Proficient, and Advanced multipliers would introduce project-created numerical assumptions into Career-fit scoring.

WBS 5.5 owns proficiency-based Skill Gap and Career Readiness calculations.

WBS 5.3 may return Student proficiency in structured matching details for later use, but the value does not alter the Version 1 recommendation score.

## 19. Interest Comparison

Interests are excluded from the WBS 5.3 Version 1 numerical recommendation score.

Dataset 1.0 does not contain an approved Career-to-Interest reference structure.

Interest scoring requires a future documented Career-side data model and comparison rule before activation.

## 20. Education Comparison

Education is excluded from the WBS 5.3 Version 1 numerical recommendation score.

Dataset 1.0 does not contain an approved Career education-requirement structure.

Education scoring requires a future documented Career-side data model and comparison rule before activation.

## 21. Experience Comparison

Experience is excluded from the WBS 5.3 Version 1 numerical recommendation score.

Dataset 1.0 does not contain an approved Career experience-requirement structure.

Experience scoring requires a future documented Career-side data model and comparison rule before activation.

## 22. Project Comparison

Student projects are excluded from the WBS 5.3 Version 1 numerical recommendation score.

Free-text project descriptions do not directly create numerical Career-fit values.

A future project factor requires an approved structured Career-side comparison rule.

## 23. Career Goal Comparison

Career goals are excluded from the WBS 5.3 Version 1 numerical recommendation score.

A future Career-goal factor requires an approved structured comparison between Student goals and Career reference data.

## 24. Personality Comparison

Personality responses are excluded from the WBS 5.3 Version 1 numerical recommendation score.

Personality scoring requires:

- An approved questionnaire.
- Approved response values.
- Approved Career personality reference information.
- A documented scoring relationship.
- Ethical review.

No personality value affects Version 1 ranking.

## 25. Protected and Sensitive Attributes

Sensitive or protected personal attributes must not be introduced as direct recommendation scoring factors without explicit project approval and ethical review.

Recommendation factors must come from approved GradNavi requirements and approved project data.

The recommendation engine must not infer unsupported personal attributes from Student information.

## 26. Career Score Calculation

For each active Career, Version 1 performs this process:

```text
1. Load approved CareerSkill relationships.
2. Load eligible O*NET numerical evidence.
3. Build the set of Student canonical Skill identifiers.
4. Sum total O*NET normalized Importance.
5. Sum Importance for matched canonical Skills.
6. Calculate weighted Career-fit coverage.
7. Collect matched and missing numerical competencies.
8. Collect matched technologies for explanation.
9. Collect ESCO essential and optional matches for explanation.
10. Return the structured Career result.
```

Each eligible numerical CareerSkill contributes once.

The calculation does not write database records.

The same Student skills, Career data, and Dataset 1.0 evidence produce the same numerical result.

## 27. Career Ranking

Careers with valid numerical scores are ranked from highest recommendation score to lowest.

Careers with:

```text
score_status = insufficient_evidence
```

do not receive a fabricated zero score and do not participate in normal numerical ranking.

The ranking service uses the unrounded internal score for ordering.

The displayed score is rounded separately.

The same Student input, Career data, and reference dataset must produce the same ranking.

## 28. Tie Handling

Tie handling is deterministic.

Approved Version 1 rule:

```text
1. Higher unrounded recommendation score first.
2. If scores are equal, Career name alphabetically.
3. If Career names are equal, Career identifier ascending.
```

Database return order must not decide tied ranking positions.

## 29. Recommendation Result Structure

The WBS 5.3 service returns structured information for WBS 5.4.

Version 1 logical result:

```text
RecommendationResult
    |
    +-- career_id
    +-- career_name
    +-- recommendation_score
    +-- score_status
    +-- rank
    +-- matched_weight
    +-- total_weight
    +-- matched_competencies
    +-- missing_competencies
    +-- matched_technologies
    +-- esco_essential_matches
    +-- esco_optional_matches
    +-- evidence_summary
```

WBS 5.4 decides the final serializer and HTTP response field names.

The service result must preserve enough information for FR-04 recommendation explanations.

## 30. Factor Breakdown

FR-04 requires understandable reasons for each recommendation.

Version 1 exposes a source-backed breakdown such as:

```json
{
  "career_id": 1,
  "career_name": "Software Engineer",
  "recommendation_score": 77.78,
  "score_status": "scored",
  "matched_weight": 140.0,
  "total_weight": 180.0,
  "matched_competencies": [
    "Skill A",
    "Skill B"
  ],
  "missing_competencies": [
    "Skill C"
  ],
  "matched_technologies": [
    "Python",
    "PostgreSQL"
  ],
  "esco_essential_matches": 4,
  "esco_optional_matches": 3
}
```

The values above illustrate the output shape only.

O*NET technology matches and ESCO relationship matches support explanation but do not alter the Version 1 numerical score.

## 31. Explanation Boundary

The deterministic scoring service produces:

- Numerical recommendation score.
- Factor scores.
- Ranking.
- Structured matching information.

A separate explanation layer may later convert structured scoring information into readable text.

Example:

```text
Strong alignment with programming skills and software-development interests.
```

The explanation layer must not alter the numerical recommendation score.

Generative AI does not replace the deterministic scoring calculation.

## 32. Service-Layer Design

Recommendation scoring belongs in a focused backend service.

Version 1 uses the existing Career domain rather than creating another Django app only for scoring.

Planned implementation structure:

```text
backend/
└── careers/
    ├── services/
    │   ├── __init__.py
    │   └── recommendation_scoring.py
    └── tests/
        ├── __init__.py
        └── test_recommendation_scoring.py
```

Conceptual flow:

```text
WBS 5.4 API
    |
    v
Career Recommendation Service
    |
    +-- load StudentSkill identifiers
    +-- load eligible CareerSkill evidence
    +-- calculate weighted Career-fit coverage
    +-- build explanation data
    +-- rank scored Careers
    |
    v
Structured Recommendation Results
```

The scoring service stays separate from HTTP request handling and generative AI.

## 33. API Layer Responsibility

The API layer is responsible for:

- Authentication.
- Permissions.
- Request validation.
- Loading approved Student and Career data.
- Calling the recommendation service.
- Serializing the service result.
- Returning the correct HTTP response.

The API view should not contain the full recommendation algorithm.

## 34. Recommendation Service Responsibility

The recommendation service is responsible for:

- Canonical Skill identifier matching.
- O*NET normalized Importance weighting.
- Career-fit score calculation.
- Insufficient-profile handling.
- Insufficient-evidence handling.
- Technology-match collection.
- ESCO essential-match collection.
- ESCO optional-match collection.
- Deterministic ranking.
- Deterministic tie handling.
- Numerical precision.
- Structured explanation data.
- Deterministic output.

Student proficiency-based readiness scoring does not belong to WBS 5.3.

WBS 5.5 owns Skill Gap and Career Readiness calculations.

## 35. Database Layer Responsibility

The database layer is responsible for persistence of approved entities and relationships.

Relevant data is expected to include:

- Student Profile data.
- Student Skill data.
- Shared Skill reference data.
- Career reference data.
- Career Skill relationships.
- Recommendation records if persistence is approved.

The scoring service should not create hidden database side effects while calculating a score.

## 36. AI Layer Responsibility

The AI layer is separate from numerical scoring.

AI-related work might later support:

- Recommendation explanation text.
- Readable summaries.
- Other approved generated content.

AI must not determine:

- Factor weights.
- Numerical factor scores.
- Numerical recommendation scores.
- Career ranking order.

## 37. Validation Rules

The recommendation flow must safely handle invalid or incomplete structured input.

Version 1 validation scenarios include:

- Missing Student Profile.
- Student Profile with no StudentSkill records.
- Unsupported Career reference.
- Non-approved CareerSkill relationship.
- Missing numerical O*NET Importance.
- Invalid normalized Importance range.
- Evidence marked not relevant.
- Evidence marked recommend suppress.
- Ambiguous duplicate numerical evidence for one CareerSkill.
- Career with no eligible numerical O*NET evidence.
- Duplicate Career input where duplication is not expected.

Missing optional non-scoring profile sections do not invalidate WBS 5.3 Version 1.

Invalid input must produce controlled service behaviour rather than a misleading score.

## 38. Numerical Precision

Version 1 uses Decimal-compatible numerical operations for scoring.

Rules:

```text
Internal ranking:
Use the unrounded recommendation score.

Returned recommendation score:
Round to 2 decimal places.

Minimum returned score:
0.00

Maximum returned score:
100.00
```

Rounding must occur after the weighted ratio is calculated.

Ranking must not use the displayed rounded value when a more precise internal value is available.

## 39. Recommendation Count

WBS 5.4 and WBS 5.6 must agree on how many Careers are returned.

Possible options include:

- All scored Careers.
- Top three Careers.
- Top five Careers.
- A controlled result limit.

Final recommendation count:

```text
TBD
```

## 40. Recommendation Persistence

The team must decide whether recommendation results are:

- Calculated on request only.
- Stored after generation.
- Stored only after Student action.
- Stored through another approved workflow.

Final persistence behaviour:

```text
TBD
```

This decision affects the Career Recommendation API and database design.

## 41. Determinism Requirements

The recommendation engine must satisfy these rules:

1. Identical Student input produces identical factor calculations.
2. Identical Career input produces identical comparison results.
3. Identical factor scores and weights produce identical recommendation scores.
4. Identical Career sets produce identical ranking order.
5. Random values are not used in scoring.
6. AI output does not change numerical results.
7. Current time does not change the score unless an approved time-based factor is introduced.
8. Database ordering does not control tied ranking results.
9. Hidden environment state does not alter scoring rules.
10. Weight configuration is explicit and testable.

## 42. Planned Unit Tests

### SCORE-01: Identical Input Produces Identical Score

Expected:

- Repeated calculations return the same score.

### SCORE-02: Identical Input Produces Identical Ranking

Expected:

- Repeated calculations return the same ranking.

### SCORE-03: Canonical Skill Match Contributes Weight

Expected:

- A matching StudentSkill and CareerSkill canonical identifier contributes the CareerSkill's eligible O*NET normalized Importance.

### SCORE-04: Missing Canonical Skill Does Not Contribute Weight

Expected:

- A missing Student Skill contributes zero matched weight.

### SCORE-05: Recommendation Score Stays Within Range

Expected:

- Scored results stay between 0.00 and 100.00.

### SCORE-06: Student Proficiency Does Not Change WBS 5.3 Score

Expected:

- Changing proficiency for the same matched canonical Skill does not change the Version 1 recommendation score.

### SCORE-07: No Student Skills Produces Insufficient Profile

Expected:

- The service does not return misleading zero-score rankings.

### SCORE-08: Career Without Numerical Evidence Is Marked Insufficient Evidence

Expected:

- recommendation_score is null.
- The Career does not receive a fabricated zero.

### SCORE-09: Technology Match Does Not Change Numerical Score

Expected:

- O*NET software technology matches appear in explanation data only.

### SCORE-10: ESCO Relationship Does Not Change Numerical Score

Expected:

- ESCO essential and optional matches appear in explanation data only.

### SCORE-11: Suppressed or Not-Relevant Evidence Is Excluded

Expected:

- Excluded evidence does not enter matched or total weight.

### SCORE-12: Tie Handling Is Deterministic

Expected:

- Equal scores use Career name alphabetically, then Career identifier.

### SCORE-13: Career Ordering Does Not Affect Scores

Expected:

- Input ordering does not change Career scores or final deterministic ranking.

### SCORE-14: Display Rounding Does Not Control Ranking

Expected:

- Ranking uses the unrounded internal score.

### SCORE-15: AI Does Not Affect Numerical Score

Expected:

- Explanation generation does not alter score or rank.

### SCORE-16: Scoring Has No Database Write Side Effect

Expected:

- Score calculation does not create or update database records.

## 43. Future Integration Tests

After WBS 5.2 and WBS 5.4 are available, integration testing should verify:

- Student Profile data reaches the scoring service correctly.
- Career reference data reaches the scoring service correctly.
- Career Skill relationships reach the comparison logic correctly.
- Career Recommendation API returns scoring-service results.
- Authentication protects recommendation requests.
- Student-owned recommendation information stays isolated.
- Factor breakdown reaches the frontend in the agreed format.
- Invalid input produces controlled API errors.
- Identical API input produces repeatable scoring output.

## 44. Performance Considerations

Recommendation scoring should avoid repeated unnecessary database queries inside factor calculations.

Where practical, required Student and Career data should be loaded before the core scoring calculation begins.

Correct deterministic behaviour has priority over premature performance optimisation.

Performance work should follow measured evidence from testing.

## 45. Current Dependencies

### WBS 5.2 Career and Skill Reference Data

Status:

```text
Available for WBS 5.3
```

Version 1 uses the approved Dataset 1.0 Career, Skill, CareerSkill, and CareerSkillEvidence structure.

### WBS 5.4 Career Recommendation API

Owner:

```text
MD
```

WBS 5.4 consumes the structured WBS 5.3 result.

The API decides the final serializer contract and recommendation result limit.

### WBS 5.5 Skill Gap and Readiness Scoring Logic

Owner:

```text
Jerald
```

WBS 5.5 follows WBS 5.3.

Student proficiency and Career readiness belong to WBS 5.5 rather than the WBS 5.3 Career-fit formula.

## 46. Decisions Required Before Final Coding

The core WBS 5.3 Version 1 scoring decisions are resolved.

Resolved:

1. Numerical factor: source-backed O*NET Skill and Knowledge Importance coverage.
2. Matching method: canonical Skill identifier.
3. Recommendation score range: 0.00 to 100.00.
4. Student proficiency: excluded from WBS 5.3 numerical scoring.
5. Technology evidence: explanation only.
6. ESCO essential and optional evidence: explanation only.
7. Missing Student skills: insufficient_profile.
8. Missing Career numerical evidence: insufficient_evidence.
9. Tie rule: score descending, Career name alphabetical, Career identifier ascending.
10. Returned precision: 2 decimal places.
11. Ranking precision: unrounded internal value.

Remaining cross-WBS decisions:

1. Number of recommendations returned by WBS 5.4.
2. Final API serializer field names.
3. Recommendation persistence behaviour.
4. Final WBS 5.5 readiness formula.
5. Future inclusion rules for non-Skill profile factors.

## 47. Decisions Already Established

The following principles are established for WBS 5.3 Version 1:

- Recommendation scoring is deterministic.
- Canonical Skill identifiers determine matches.
- O*NET normalized Importance supplies numerical CareerSkill weight.
- WBS 5.3 measures weighted Career-fit coverage.
- Student proficiency does not change the WBS 5.3 numerical score.
- Student proficiency is reserved for WBS 5.5 readiness.
- O*NET software technologies support explanation only.
- ESCO essential and optional relationships support explanation only.
- A Career without numerical evidence receives insufficient_evidence rather than zero.
- A Student with no skills receives insufficient_profile.
- Recommendation score range is 0.00 to 100.00.
- Returned scores use 2 decimal places.
- Ranking uses the unrounded internal score.
- Ties use Career name alphabetically, then Career identifier.
- Generative AI does not determine numerical recommendation scores.
- Recommendation scoring belongs in focused backend business logic.
- WBS 5.4 consumes the recommendation-scoring result.

## 48. Implementation Sequence

```text
Approved WBS 5.3 Version 1 Design
        |
        v
Define Recommendation Service Contract
        |
        v
Create Test Fixtures
        |
        v
Write Core Scoring Unit Tests
        |
        v
Implement Canonical Skill Matching
        |
        v
Implement O*NET Importance Weighting
        |
        v
Implement Insufficient-Data Handling
        |
        v
Implement Explanation Evidence Collection
        |
        v
Implement Deterministic Ranking
        |
        v
Verify No Database Write Side Effects
        |
        v
Connect WBS 5.4 Career Recommendation API
        |
        v
Sprint 2 Integration Testing
```

## 49. Definition of Ready for Final Scoring Implementation

WBS 5.3 Version 1 is ready for implementation because:

- Career reference structure is confirmed.
- Canonical Skill structure is confirmed.
- CareerSkill relationships are confirmed.
- CareerSkillEvidence is available.
- Numerical O*NET evidence coverage has been inspected.
- O*NET software evidence limitations have been inspected.
- ESCO relationship evidence has been inspected.
- Numerical scoring factor is approved.
- Weight source is approved.
- Missing-profile behaviour is approved.
- Missing-evidence behaviour is approved.
- Score range is approved.
- Tie behaviour is approved.
- Numerical precision is approved.
- WBS 5.3 and WBS 5.5 responsibilities are separated.

WBS 5.4 still owns the final HTTP serializer contract and recommendation result limit.

## 50. Definition of Done

WBS 5.3 is complete when:

- Approved scoring factors are implemented.
- Approved weights are implemented.
- Scoring is deterministic.
- Ranking is deterministic.
- Factor breakdown is returned.
- Invalid input is handled safely.
- Unit tests pass.
- Integration with approved Career data succeeds.
- Integration with approved Student Profile data succeeds.
- The output contract supports WBS 5.4.
- Technical documentation matches the implemented rules.
- Team review confirms alignment with the approved scoring design.

## 51. Change Control

If the Career model, Skill model, scoring factors, weights, score range, or API contract changes:

1. Record the proposed change.
2. Review the effect on WBS 5.3.
3. Review the effect on WBS 5.4.
4. Review the effect on WBS 5.5.
5. Confirm the team decision.
6. Update this design.
7. Update affected tests.
8. Update implementation after the relevant decision is confirmed.

Scoring behaviour must not change silently because of a model or API difference.
