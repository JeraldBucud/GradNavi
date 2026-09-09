# GradNavi Sprint 2 Test Plan

Status: Prepared for WBS 5.9 Sprint 2 Integration and Testing. Verified WBS 5.2, WBS 5.3, and WBS 5.5 scoring and Dataset 1.0 cases are recorded as Pass. Cases depending on WBS 5.4, WBS 5.6, WBS 5.7, or WBS 5.8 stay Blocked until those components are integrated.

## 1. Purpose

This document defines the team-level Sprint 2 testing approach for the GradNavi Career Analysis increment.

The purpose of Sprint 2 testing is to verify that Career and Skill reference data, recommendation scoring, Career Recommendation API, Skill Gap analysis, Career Readiness scoring, frontend Career Analysis, learning suggestions, and the learning roadmap work together as planned.

Detailed execution status is maintained in:

```text
docs/testing/sprint-2-test-cases.xlsx
```

This plan provides the higher-level team testing structure. It does not replace detailed implementation tests inside backend or frontend modules.

## 2. WBS Alignment

WBS 5.9 is owned by All Members and depends on WBS 5.4, WBS 5.5, WBS 5.7, and WBS 5.8. WBS 5.6 supplies the recommendation and readiness interface required for the integrated frontend flow.

The approved WBS places WBS 5.9 on 3 to 4 September 2026.

## 3. Sprint 2 Testing Goal

Sprint 2 testing should provide evidence that an authenticated Student is able to:

1. Use Student Profile Skills as Career Analysis input.
2. Receive deterministic ranked Career recommendations.
3. View recommendation scores and approved explanation factors.
4. Select a Career for detailed analysis.
5. Receive a Skill Gap result for the selected Career.
6. Receive a separate Career Readiness Score.
7. Distinguish missing, below-requirement, and met Skills.
8. Receive learning suggestions linked to unresolved Skill gaps.
9. View an ordered learning roadmap.
10. Receive controlled empty, insufficient-evidence, and error states.
11. Stay isolated from another Student's private profile-derived results.

Testing should also confirm that Sprint 2 changes do not break the working Sprint 1 authentication and Student Profile foundation.

## 4. Requirements Traceability

| Requirement | Test Focus |
| --- | --- |
| FR-03 | Ranked Career recommendations from Student Profile data |
| FR-04 | Recommendation score and explanation factors |
| FR-05 | Skill Gap analysis for a selected Career |
| FR-06 | Weighted Career Readiness Score |
| FR-11 | Learning suggestions for identified gaps |
| FR-12 | Ordered learning roadmap |
| NFR-01 | Usability of the Career Analysis flow |
| NFR-02 | Responsive design |
| NFR-03 | Normal non-AI API responses target 2 seconds |
| NFR-05 | Authentication and authorisation |
| NFR-06 | Student privacy and ownership isolation |
| NFR-08 | Deterministic structured scoring |
| NFR-09 | Explainability of recommendation and readiness results |
| NFR-10 | Accessibility basics |
| NFR-11 | Chrome, Edge, and Firefox compatibility |
| NFR-12 | Automated and acceptance test evidence |
| NFR-13 | Separation of frontend, API, service, and database layers |

## 5. Testing Scope

Sprint 2 testing covers:

- Career and Skill reference data.
- Dataset 1.0 integrity.
- Recommendation scoring and ranking.
- Recommendation explanation evidence.
- Career Recommendation API.
- API authentication and Student ownership.
- Recommendation and readiness frontend.
- Skill Gap analysis.
- Career Readiness scoring.
- O*NET Importance and Level evidence.
- Student proficiency mapping.
- Learning Suggestions and Roadmap API.
- Learning Roadmap frontend.
- Empty, error, and insufficient-evidence states.
- Security and privacy regression.
- Performance observation.
- Browser compatibility.
- Accessibility basics.
- Full Sprint 2 integration.
- Sprint 1 authentication and Student Profile regression.

Testing outside the Sprint 2 Career Analysis increment is not required by this plan.

## 6. Related Testing Documentation

Relevant documentation includes:

- `docs/system-design/sprint-2-integration-plan.md`
- `docs/testing/sprint-2-test-cases.xlsx`
- `docs/testing/evidence/sprint-2/`
- `docs/system-design/rest-api-design.md`
- `docs/system-design/recommendation-scoring-design.md`
- `docs/system-design/readiness_scoring_design.md`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`
- `docs/testing/sprint-1-test-plan.md`

The Sprint 2 Test Case Tracker records WBS traceability, requirements, priority, ownership, execution status, actual results, evidence IDs, blocked dependencies, defects, and automation type.

## 7. Testing Levels

### 7.1 Unit Testing

Unit testing covers individual deterministic service rules such as:

- Recommendation weighted scoring.
- Recommendation ranking and tie handling.
- Empty and insufficient-evidence recommendation states.
- Readiness proficiency mapping.
- Skill Gap calculation.
- Readiness weighting.
- Gap status classification.
- Gap ordering.
- Invalid or unsupported evidence handling.
- Learning suggestion logic where implemented.

Automate deterministic service tests where practical.

### 7.2 Database Testing

Database testing covers:

- Active Career records.
- Canonical Skill records.
- CareerSkill relationships.
- ReferenceSource and ReferenceDataset relationships.
- Eligible evidence source filtering.
- StudentSkill proficiency loading.
- Active dataset filtering.
- Duplicate evidence protection.
- Read-only scoring behaviour.
- Migration consistency.

### 7.3 API Testing

API testing covers:

- Authentication requirements.
- Request validation.
- Response structure.
- HTTP status codes.
- Student ownership.
- Recommendation serialization.
- Readiness serialization.
- Learning and roadmap serialization.
- Controlled error responses.
- Privacy isolation.

### 7.4 Permission Testing

Permission testing verifies that an authenticated Student receives only results derived from their own protected Student Profile.

A Student must not select another Student's profile through a client-supplied identifier or receive another Student's recommendation, readiness, gap, or roadmap result.

### 7.5 Integration Testing

Integration testing verifies communication across:

```text
React
  |
  v
Django REST API
  |
  v
Recommendation / Readiness / Learning Services
  |
  v
PostgreSQL and Dataset 1.0
```

Integration testing focuses on complete user flows rather than isolated components.

### 7.6 Manual Frontend Testing

Manual frontend testing covers:

- Recommendation list display.
- Career selection.
- Recommendation score and explanation presentation.
- Readiness score presentation.
- Skill Gap presentation.
- Learning suggestions.
- Roadmap display.
- Loading states.
- API error states.
- Empty states.
- Responsive layout.
- Keyboard interaction.
- Chrome, Edge, and Firefox.

### 7.7 Regression Testing

Regression testing covers the working Sprint 1 foundation after Sprint 2 integration changes:

- Registration.
- Login.
- JWT behaviour.
- Current-user retrieval.
- Student Profile load.
- Student Profile update.
- StudentSkill persistence.
- Ownership isolation.
- PostgreSQL connectivity.

## 8. Test Environment

| Component | Sprint 2 Environment |
| --- | --- |
| Frontend | React and Vite |
| Backend | Django and Django REST Framework |
| Authentication | JWT |
| Database | PostgreSQL |
| Reference Data | GradNavi Dataset 1.0 |
| API Testing | Django automated tests and manual API checks where required |
| Browser Testing | Current Chrome, Edge, and Firefox |
| Version Control | Git and GitHub |
| Integration Branch | `feature/sprint-2` |

Exact ports and environment variables should follow the approved local development configuration.

Secrets and passwords must not appear in test documentation, screenshots, committed files, or evidence.

## 9. Test Data Principles

Use safe development and testing data.

Test data should include:

- A valid Student account.
- A second Student account for ownership testing.
- A Student with no StudentSkill rows.
- A Student with one Skill.
- A Student with multiple Skills.
- A Student with Skills unrelated to a Career.
- A Student with a partial Career match.
- Foundational proficiency.
- Developing proficiency.
- Proficient proficiency.
- Advanced proficiency.
- Careers with valid recommendation and readiness evidence.
- A Career with insufficient readiness evidence.
- Invalid Career ID input.
- An inactive Career fixture where supported.

Dataset 1.0 must not be modified by read-only scoring tests.

## 10. Current Test Execution Status

The Sprint 2 Test Case Tracker contains 80 cases.

At this checkpoint:

- Pass: 28.
- Fail: 0.
- Blocked: 42.
- Retest: 0.
- Not Run: 10.

The 28 recorded Pass cases cover the verified WBS 5.2 reference-data checks, WBS 5.3 recommendation scoring checks, and WBS 5.5 Skill Gap and Readiness checks.

The 42 Blocked cases depend on unmerged or unavailable WBS 5.4, WBS 5.6, WBS 5.7, WBS 5.8, or the full WBS 5.9 integration gate.

The 10 Not Run cases are ready for later execution or require the final integrated branch and quality review.

A blocked test is not a failed test.

## 11. Entry Criteria

Before full WBS 5.9 execution:

- WBS 5.4 must be merged.
- WBS 5.5 must be merged. This condition is satisfied at the current repository checkpoint.
- WBS 5.7 must be merged.
- WBS 5.8 must be merged.
- WBS 5.6 must be available for frontend integration.
- Django checks and required migrations must pass.
- Backend automated tests must pass.
- React lint and production build must pass.
- Dataset 1.0 must be loaded.
- The tracker must be ready for result and evidence capture.

Missing dependencies leave affected tests Blocked.

## 12. Reference Data Tests

Verify:

- Active Career records are available.
- Canonical Skill records resolve through CareerSkill relationships.
- Eligible CareerSkill evidence loads only from active approved datasets.
- Duplicate readiness evidence does not silently double count.
- O*NET numerical evidence and explanation evidence stay in their approved roles.
- Read-only Dataset validation does not modify stored data.
- Reference import is repeatable in a disposable test database.
- Normal Student flow does not modify shared Career or Skill reference data.

## 13. Recommendation Scoring Tests

Verify:

- Full Skill match returns 100.00.
- Partial Skill match follows Importance weighting.
- Unrelated Skills return a scored zero where evidence exists.
- Empty Student Skill profile returns `insufficient_profile`.
- Career without numerical evidence returns `insufficient_evidence`.
- Duplicate Student Skill IDs do not double count.
- Duplicate CareerSkill evidence cannot increase numerical weight.
- Recommendation ranking is deterministic.
- Stable tie handling follows the approved rule.
- Explanation evidence does not change numerical rank.

## 14. Career Recommendation API Tests

After WBS 5.4 is merged, verify:

- Authenticated Student receives recommendations.
- Unauthenticated requests are rejected.
- API uses the authenticated Student Profile.
- API preserves service ranking order.
- Score and rank serialize correctly.
- Approved explanation data serialize correctly.
- Empty Student Skill profile stays controlled.
- Invalid requests use the approved REST error structure.
- Repeated unchanged requests return stable scores, ranks, and statuses.
- Another Student's protected profile data do not appear in the response.

## 15. Skill Gap and Readiness Tests

Approved proficiency mapping:

| Student Proficiency | Numerical Value |
| --- | ---: |
| Missing | 0 |
| Foundational | 25 |
| Developing | 50 |
| Proficient | 75 |
| Advanced | 100 |

Verify:

- Missing Skill handling.
- Below-requirement partial attainment.
- Meets-requirement full attainment.
- Attainment is capped at 1.00.
- Skill gaps do not become negative.
- Career Readiness uses Importance weighting.
- Readiness score is reported to two decimal places where required by the design.
- Empty Student Skill profile returns `insufficient_profile`.
- Career without readiness evidence returns `insufficient_evidence`.
- Technology explanation evidence does not enter the readiness formula.
- Duplicate evidence protection works.
- Skill Gap ordering is deterministic.
- Nonexistent and inactive Career handling follows the approved service behaviour.
- Dataset 1.0 readiness validation is non-destructive.

Dataset 1.0 validation for WBS 5.5 identified 1,849 eligible readiness requirements across 35 Careers with readiness evidence. One active Career, Health Information Manager, has no eligible readiness evidence and is used as the controlled insufficient-evidence case.

## 16. Recommendation and Readiness Interface Tests

After WBS 5.6 is available, verify:

- Recommendation list loads from the backend.
- Frontend preserves API rank order.
- Score and explanation factors display.
- Career selection loads readiness details.
- Recommendation and readiness scores are visually distinct.
- Missing and below-requirement Skills are distinguishable.
- `insufficient_profile` is understandable.
- `insufficient_evidence` is understandable.
- Loading and API-error states are controlled.
- Core flow stays usable at common widths and with keyboard navigation.

## 17. Learning Suggestions and Roadmap API Tests

After WBS 5.7 is available, verify:

- API accepts unresolved Skill gaps.
- Missing Skills receive relevant suggestions.
- Below-requirement Skills receive relevant suggestions.
- Met requirements are excluded from unresolved-gap priorities.
- Selected Career context is preserved.
- Empty or insufficient-evidence input is controlled.
- Invalid learning requests return validation errors.
- Repeated unchanged structured input is stable where deterministic behaviour applies.

## 18. Learning Roadmap Interface Tests

After WBS 5.8 is available, verify:

- Roadmap loads from the backend.
- Display order matches API order.
- Skill names match the selected Career gaps.
- Resources and actions map to the correct Skill.
- Empty roadmap state is controlled.
- API-error state is controlled.
- Navigation preserves selected Career context.

## 19. End-to-End Career Analysis Tests

Run:

```text
Login
  -> Student Profile
  -> Career Recommendations
  -> Recommendation Explanation
  -> Select Career
  -> Skill Gap
  -> Readiness Score
  -> Learning Suggestions
  -> Learning Roadmap
```

Execute the flow with:

- A partial-match Student.
- A Student with unrelated Skills.
- An empty Student Skill profile.
- A Career with insufficient readiness evidence.
- A second Student for privacy and ownership isolation.

## 20. Reliability and Explainability Tests

Verify:

- Repeated unchanged inputs produce the same recommendation score and rank.
- Repeated unchanged inputs produce the same readiness score and gap order.
- Read-only scoring does not modify reference data.
- Recommendation and readiness factors are visible.
- Missing and below-requirement Skills are distinguishable.
- Learning suggestions trace to identified Skill gaps.

## 21. Performance Tests

NFR-03 targets normal non-AI API responses within 2 seconds under expected classroom use.

For each performance observation, record:

- Endpoint or action tested.
- Local environment.
- Approximate response time.
- Dataset size where relevant.
- Debug-mode state.

This is a classroom-use observation. It is not a production load test.

## 22. Security and Privacy Tests

Verify:

- Unauthenticated access is rejected.
- Invalid authentication is controlled.
- Cross-student profile-derived result access is prevented.
- Frontend code exposes no backend secrets.
- API errors expose no sensitive internal details.
- Sprint 1 ownership controls stay working after Sprint 2 integration.

## 23. Accessibility and Compatibility Tests

Check:

- Keyboard access to core controls.
- Visible labels.
- Useful error feedback.
- Focus behaviour.
- Readable contrast.
- Responsive desktop, tablet, and mobile layouts.
- Current Chrome.
- Current Edge.
- Current Firefox.

## 24. Automation Strategy

Automate deterministic service, database, and API cases where practical.

Use manual execution for:

- Browser behaviour.
- Visual layout.
- Keyboard checks.
- Selected end-to-end flows.
- Browser compatibility.
- Exploratory error-state verification.

## 25. Status Rules

| Status | Meaning |
| --- | --- |
| Pass | Expected behaviour was verified |
| Fail | Implementation ran but expected behaviour was not met |
| Blocked | Required dependency or environment is unavailable |
| Not Run | Planned or ready but not executed |
| Retest | A prior failure was fixed and is awaiting verification |

A Blocked test is not a Failed test.

## 26. Evidence Rules

Store Sprint 2 evidence under:

```text
docs/testing/evidence/sprint-2/
```

Do not store:

- Passwords.
- JWT values.
- Database credentials.
- Private keys.
- Secret API keys.
- Sensitive personal information.

Record evidence IDs and evidence references in the tracker.

## 27. Defect Handling

For each failed test, record:

- Failed Test ID.
- Actual result.
- Defect reference.
- Component owner.
- Fix branch or pull request.
- Retest result.
- Affected regression result.

Do not mark a failed case Pass until the retest confirms the expected behaviour.

## 28. Current Verified Baseline

Repository and existing test preparation confirm:

- WBS 5.2 reference-data foundations are present in `feature/sprint-2`.
- WBS 5.3 recommendation scoring implementation and design are present.
- WBS 5.5 readiness scoring implementation and design are present.
- WBS 5.4 Career Recommendation API is not yet available in the shared branch. `backend/careers/views.py` still contains the default Django placeholder at this checkpoint.
- WBS 5.6, WBS 5.7, and WBS 5.8 are not yet available in the shared branch at this checkpoint.

Verified WBS 5.2, WBS 5.3, and WBS 5.5 cases stay recorded as Pass.

Dependent API, frontend, learning, roadmap, end-to-end, and selected regression cases stay Blocked until their prerequisites are available.

## 29. Sprint 2 Exit Criteria

Sprint 2 testing is complete when:

- Critical Career Analysis cases pass.
- No unresolved Critical or High defect blocks the core flow.
- Security and privacy regression passes.
- Recommendation and readiness determinism is preserved.
- React and Django integration works for the planned Career Analysis flow.
- Learning suggestions and roadmap connect to identified Skill gaps.
- Required evidence exists.
- Deferred issues are documented.
- The team agrees WBS 5.9 is ready for Sprint 2 review.

## 30. Test Plan Maintenance

Update this plan when:

- API contracts change.
- UI behaviour changes.
- Learning-resource behaviour changes.
- WBS ownership changes.
- Integration dependencies change.
- Test execution produces new verified results.

The Sprint 2 Test Case Tracker should reflect implemented and verified behaviour rather than outdated expectations.
