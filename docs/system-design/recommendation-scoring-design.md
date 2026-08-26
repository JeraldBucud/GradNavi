# GradNavi Recommendation Scoring Design

Status: Sprint 2 working design for WBS 5.3 Weighted Recommendation Engine.

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

Exact scoring weights and final Career reference-data fields are pending team confirmation.

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

GradNavi currently uses these Student Skill proficiency values:

- Foundational.
- Developing.
- Proficient.
- Advanced.

The API values are expected to follow the existing lowercase representation:

```text
foundational
developing
proficient
advanced
```

A deterministic comparison process needs an ordered representation.

A proposed internal order is:

```text
Foundational -> 1
Developing   -> 2
Proficient   -> 3
Advanced     -> 4
```

This ordering represents progression only.

The numbers above are not final recommendation-score contributions.

The team must approve the proficiency comparison rule before final scoring implementation.

## 9. Career Reference Input

Career reference information comes from WBS 5.2 Career and Skill Reference Data.

The recommendation engine needs enough Career information to compare a Student Profile with each Career.

Expected categories of Career information include:

- Career identifier.
- Career name.
- Relevant or required skills.
- Required or preferred proficiency levels where implemented.
- Relevant interests where implemented.
- Education requirements where implemented.
- Experience indicators where implemented.
- Career-goal alignment information where implemented.
- Personality-related reference information where approved.

Exact field names and relationships are pending WBS 5.2.

The scoring service must follow the approved Career model instead of defining a competing data model.

## 10. Recommendation Scoring Factors

The final scoring-factor set requires team approval.

Candidate factors from the current GradNavi requirements are:

| Factor | Student Source | Career Source | Final Inclusion |
| --- | --- | --- | --- |
| Skills | Student Profile | Career reference data | TBD |
| Interests | Student Profile | Career reference data | TBD |
| Education | Student Profile | Career reference data | TBD |
| Experience | Student Profile | Career reference data | TBD |
| Projects | Student Profile | Career reference data | TBD |
| Career goals | Student Profile | Career reference data | TBD |
| Personality responses | Student Profile | Approved Career reference data | TBD |

A factor must not affect the recommendation score until:

1. The team approves the factor.
2. Input data is defined.
3. The comparison rule is documented.
4. The weight is approved.
5. Expected behaviour is testable.

## 11. Factor Score Range

Each approved factor should produce a normalized factor score.

Proposed range:

```text
0 to 100
```

Proposed interpretation:

```text
0   = no alignment
100 = full alignment
```

Intermediate values depend on the approved comparison rules.

Final factor score range:

```text
TBD
```

## 12. Weighting Model

Each approved factor receives a weight.

Conceptual configuration:

```text
skills_weight
interests_weight
education_weight
experience_weight
projects_weight
career_goals_weight
personality_weight
```

Exact numerical weights are:

```text
TBD
```

Weights require team approval before final implementation.

The scoring implementation should store weight configuration in one clear location rather than spreading numerical values across several functions.

## 13. Weight Validation

The implementation must validate the scoring configuration.

Validation should cover:

- Unsupported factors.
- Negative weights.
- Missing required weights.
- No active weighted factors.
- Invalid numerical values.
- Invalid total weight where the chosen weighting method requires a specific total.

Invalid configuration must not silently produce a recommendation score.

## 14. Weighted Score Formula

The general weighted structure is:

```text
weighted_total =
    factor_score_1 × factor_weight_1
  + factor_score_2 × factor_weight_2
  + ...
  + factor_score_n × factor_weight_n
```

If approved weights use proportions whose total equals `1`:

```text
recommendation_score =
    sum(factor_score × factor_weight)
```

If approved weights use another scale:

```text
recommendation_score =
    sum(factor_score × factor_weight)
    /
    sum(active_factor_weights)
```

Final formula:

```text
TBD pending approved weight representation
```

Proposed final recommendation-score range:

```text
0 to 100
```

Final score range requires team confirmation.

## 15. Structural Example

The following example shows the scoring structure only.

The example does not define approved GradNavi weights.

```text
Skills score       × Skills weight
Interests score    × Interests weight
Education score    × Education weight
Experience score   × Experience weight
Projects score     × Projects weight
Career goals score × Career goals weight

                    |
                    v

          Weighted Recommendation Score
```

## 16. Missing Profile Data

The recommendation engine needs predictable behaviour when Student Profile information is incomplete.

Examples include:

- No Student skills.
- No interests.
- No education records.
- No experience records.
- No projects.
- No career goals.
- No personality responses.

The team must approve one missing-data policy.

### Option A: Missing Factor Receives Zero

Missing information produces a factor score of zero.

### Option B: Exclude Missing Optional Factors

An optional missing factor is removed from the calculation and active weights are normalized.

### Option C: Require Minimum Profile Completion

Recommendation scoring does not run until required profile information is present.

Final policy:

```text
TBD
```

The selected policy must be documented and covered by tests.

## 17. Skill Comparison

Skill comparison is expected to form a major part of recommendation scoring.

Conceptual structure:

```text
StudentSkill
    |
    +-- Skill reference
    +-- Student proficiency

Career Skill Requirement
    |
    +-- Skill reference
    +-- Required or preferred proficiency
```

Where shared Skill identifiers exist, comparison should use those references instead of relying only on free-text skill names.

The exact Career-to-Skill relationship remains dependent on WBS 5.2.

## 18. Proficiency Comparison

A future deterministic comparison might examine:

```text
Student proficiency
        versus
Career required proficiency
```

Example concept:

```text
Student: Proficient
Career: Developing

Result:
Student meets or exceeds the Career requirement
```

Another example:

```text
Student: Foundational
Career: Advanced

Result:
Student has a significant proficiency gap
```

The final mathematical contribution of these comparisons remains:

```text
TBD
```

## 19. Interest Comparison

If interests become an approved scoring factor, the comparison rule must define how Student interests match Career reference interests.

Possible data concerns include:

- Exact reference matches.
- Multiple matching interests.
- No matching interests.
- Duplicate Student interests.
- Career records with no interest references.

The final interest comparison rule is:

```text
TBD
```

## 20. Education Comparison

If education becomes an approved scoring factor, the team must define:

- Which education attributes matter.
- Whether field of study matters.
- Whether qualification level matters.
- How multiple education records are handled.
- How missing education requirements are handled.

Final education comparison rule:

```text
TBD
```

## 21. Experience Comparison

If experience becomes an approved scoring factor, the team must define:

- Which experience attributes matter.
- Whether role type matters.
- Whether duration matters.
- How multiple experience records are combined.
- How Careers without experience requirements are handled.

Final experience comparison rule:

```text
TBD
```

## 22. Project Comparison

If Student projects become an approved factor, the team must define how a project contributes to Career alignment.

Potential structured comparisons might use approved skills or categories attached to a project.

Free-text project descriptions should not directly produce numerical scores without a documented deterministic rule.

Final project comparison rule:

```text
TBD
```

## 23. Career Goal Comparison

If Career goals become an approved factor, the team must define the structure used to compare a Student goal with Career reference data.

Final Career goal comparison rule:

```text
TBD
```

## 24. Personality Comparison

Personality responses must not affect recommendation scoring until:

- The questionnaire is approved.
- Response values are approved.
- Career personality reference information is approved.
- The scoring relationship is documented.
- Ethical review confirms the factor is appropriate.

Final personality scoring status:

```text
TBD
```

## 25. Protected and Sensitive Attributes

Sensitive or protected personal attributes must not be introduced as direct recommendation scoring factors without explicit project approval and ethical review.

Recommendation factors must come from approved GradNavi requirements and approved project data.

The recommendation engine must not infer unsupported personal attributes from Student information.

## 26. Career Score Calculation

For each Career, the service performs the same general process:

```text
1. Receive normalized Student scoring input.
2. Receive one Career scoring input.
3. Calculate each approved factor score.
4. Apply approved weights.
5. Calculate final recommendation score.
6. Produce the factor breakdown.
7. Return the structured Career result.
```

Each Career should be scored independently using the same approved rules.

## 27. Career Ranking

After all selected Careers are scored, results are ordered from highest score to lowest score.

Example:

```text
Software Engineer      88
Data Analyst           82
Systems Administrator  74
```

Result:

```text
1. Software Engineer
2. Data Analyst
3. Systems Administrator
```

The values above are examples only.

The same Student input, Career data, and scoring configuration must produce the same ranking.

## 28. Tie Handling

Two or more Careers might receive equal recommendation scores.

Tie handling must remain deterministic.

Possible approaches include:

1. Equal score, then Career identifier.
2. Equal score, then alphabetical Career name.
3. Equal score, then an approved secondary deterministic factor.

Final tie-breaking rule:

```text
TBD
```

The selected rule must not depend on database return order.

## 29. Recommendation Result Structure

The scoring service should return structured information rather than formatted frontend text.

Proposed logical result:

```text
RecommendationResult
    |
    +-- career_id
    +-- career_name
    +-- recommendation_score
    +-- rank
    +-- factor_breakdown
    +-- matched_factors
    +-- weaker_factors
```

Exact field names remain dependent on WBS 5.4 Career Recommendation API.

## 30. Factor Breakdown

FR-04 requires understandable reasons for each recommendation.

The scoring service should expose the factors used in the calculation.

Conceptual example:

```json
{
  "career_id": 1,
  "career_name": "Software Engineer",
  "recommendation_score": 84,
  "factor_breakdown": {
    "skills": 90,
    "interests": 85,
    "education": 80,
    "experience": 70
  }
}
```

The values above are examples only.

The final factor list depends on the approved scoring configuration.

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

Conceptual flow:

```text
API View
   |
   v
Serializer and Request Validation
   |
   v
Recommendation Service
   |
   +-- Factor Calculations
   +-- Weight Application
   +-- Final Score
   +-- Ranking
   +-- Factor Breakdown
   |
   v
Structured Result
```

A possible future implementation structure is:

```text
backend/
└── recommendations/
    ├── services/
    │   └── scoring.py
    └── tests/
```

This folder structure is provisional.

Do not create a Django app only to match this document.

The implementation structure should be created when the recommendation domain is ready.

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

- Factor calculations.
- Proficiency comparison.
- Weight application.
- Final score calculation.
- Ranking.
- Tie handling.
- Factor breakdown.
- Deterministic output.

The service should receive structured Python data or approved domain objects and return structured results.

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

The recommendation flow must safely handle invalid structured input.

Validation scenarios include:

- Missing required Career identifier.
- Unsupported proficiency value.
- Invalid factor score.
- Invalid weight.
- Negative weight.
- No active scoring factors.
- Unsupported Career reference.
- Unsupported Student Profile value.
- Duplicate Career input where duplication is not expected.

Final responsibility between serializers and service validation will be confirmed during implementation.

## 38. Numerical Precision

The implementation must define:

- Internal numerical precision.
- Rounding point.
- Number of decimal places returned through the API.
- Whether ranking uses rounded or unrounded values.

Final precision rule:

```text
TBD
```

The ranking process must use one consistent precision rule.

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

Given the same Student Profile, Career data, and scoring configuration.

Expected result:

- Repeated calculations return the same numerical score.

### SCORE-02: Identical Input Produces Identical Ranking

Given the same Student Profile and Career set.

Expected result:

- Career ranking stays identical.

### SCORE-03: Stronger Approved Match Produces Higher Factor Score

Given two comparisons where one has stronger alignment under an approved rule.

Expected result:

- The stronger match receives a higher relevant factor score.

### SCORE-04: Recommendation Score Stays Within Approved Range

Expected result:

- The final score does not fall below the approved minimum.
- The final score does not exceed the approved maximum.

### SCORE-05: Invalid Weight Configuration Is Rejected

Expected result:

- Invalid weights do not silently produce a result.

### SCORE-06: Missing Optional Data Follows Approved Policy

Expected result:

- Missing optional profile information follows the documented missing-data policy.

### SCORE-07: Missing Required Data Is Handled Safely

Expected result:

- Missing required input does not produce an uncontrolled exception.
- No misleading recommendation result is returned.

### SCORE-08: Tie Handling Is Deterministic

Expected result:

- Equal scores use the approved tie-breaking rule.

### SCORE-09: Factor Breakdown Matches Final Score

Expected result:

- Factor contributions reproduce the documented final recommendation score.

### SCORE-10: AI Does Not Affect Numerical Score

Expected result:

- Recommendation score stays unchanged regardless of explanation generation.

### SCORE-11: Unsupported Proficiency Is Rejected

Expected result:

- A proficiency value outside the approved GradNavi set is rejected.

### SCORE-12: Career Ordering Does Not Affect Scores

Given the same Careers supplied in a different input order.

Expected result:

- Each Career receives the same score.
- Final ranking follows the approved deterministic ranking rule.

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

Owner:

```text
MD
```

Required before final model integration:

- Final Career model or representation.
- Final Skill reference structure.
- Career-to-Skill relationship.
- Required proficiency representation where implemented.
- Other approved Career comparison fields.

### WBS 5.4 Career Recommendation API

Owner:

```text
MD
```

The API needs the final scoring-service output contract.

The scoring service should return structured information suitable for serialization.

### WBS 5.5 Skill Gap and Readiness Scoring Logic

Owner:

```text
Jerald
```

WBS 5.5 follows WBS 5.3.

Reusable skill comparison rules should be separated clearly so WBS 5.5 does not duplicate logic without need.

## 46. Decisions Required Before Final Coding

The following decisions are still open:

1. Final Career data structure from WBS 5.2.
2. Final Career-to-Skill relationship.
3. Final list of recommendation scoring factors.
4. Weight assigned to each factor.
5. Factor score range.
6. Final recommendation score range.
7. Skill proficiency comparison rule.
8. Missing-data policy.
9. Tie-breaking rule.
10. Numerical precision and rounding.
11. Number of recommendations returned.
12. Final factor-breakdown output structure.
13. Recommendation persistence behaviour.
14. Shared rules between WBS 5.3 and WBS 5.5.
15. Final handling of personality responses.
16. Final handling of optional Student Profile sections.

## 47. Decisions Already Established

The following principles are already established in GradNavi project documentation:

- Recommendation scoring is deterministic.
- Recommendation scores use documented weighted rules.
- The same structured input produces the same numerical result.
- Recommendation scoring belongs in focused backend business logic.
- Generative AI does not independently determine numerical recommendation scores.
- Recommendation results require explainable scoring factors.
- Skill proficiency uses Foundational, Developing, Proficient, and Advanced.
- React does not access PostgreSQL directly.
- Django remains responsible for protected Student data.
- WBS 5.3 depends on WBS 5.2.
- WBS 5.4 consumes the recommendation-scoring result.
- WBS 5.5 follows the recommendation engine work.

## 48. Implementation Sequence

```text
Recommendation Scoring Design
        |
        v
WBS 5.2 Career and Skill Data Confirmed
        |
        v
Resolve Open Design Decisions
        |
        v
Define Test Fixtures
        |
        v
Write Scoring Unit Tests
        |
        v
Implement Recommendation Scoring Service
        |
        v
Verify Deterministic Results
        |
        v
Connect WBS 5.4 Career Recommendation API
        |
        v
Sprint 2 Integration Testing
```

## 49. Definition of Ready for Final Scoring Implementation

WBS 5.3 is ready for final implementation when:

- Career reference structure is confirmed.
- Skill reference structure is confirmed.
- Career-to-Skill relationship is confirmed.
- Required scoring factors are approved.
- Factor weights are approved.
- Missing-data policy is approved.
- Score range is approved.
- Tie behaviour is approved.
- Numerical precision is approved.
- Output contract is agreed with WBS 5.4.
- No unresolved model conflict exists with WBS 5.2.

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