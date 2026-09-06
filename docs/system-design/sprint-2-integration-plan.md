# GradNavi Sprint 2 Integration Plan

Status: Prepared for WBS 5.9 Sprint 2 Integration and Testing. WBS 5.2, WBS 5.3, and WBS 5.5 are present in the current `feature/sprint-2` branch. Cases depending on WBS 5.4, WBS 5.6, WBS 5.7, or WBS 5.8 remain blocked until those components are merged and available for integration.

## 1. Purpose

This document defines the GradNavi Sprint 2 integration approach.

Sprint 2 focuses on Career Recommendations and Skill Gaps. The integrated increment connects Career and Skill reference data, deterministic recommendation scoring, the Career Recommendation API, Skill Gap and Career Readiness scoring, the recommendation and readiness interface, learning suggestions, and the learning roadmap interface.

This plan prepares the team for WBS 5.9. It does not mark WBS 5.9 complete before its required predecessors are ready.

## 2. WBS Alignment

| WBS | Task | Official Owner | Predecessors |
| --- | --- | --- | --- |
| 5.1 | Sprint 2 Planning | All Members | 4.11 |
| 5.2 | Career and Skill Reference Data | MD | 5.1 |
| 5.3 | Weighted Recommendation Engine | Jerald | 5.1, 5.2 |
| 5.4 | Career Recommendation API | MD | 5.3 |
| 5.5 | Skill Gap and Readiness Scoring Logic | Jerald | 5.3 |
| 5.6 | Recommendation and Readiness Interface | Joyee | 5.1, 3.8 |
| 5.7 | Learning Suggestions and Roadmap API | MD | 5.5 |
| 5.8 | Learning Roadmap Interface | Joyee | 5.6 |
| 5.9 | Sprint 2 Integration and Testing | All Members | 5.4, 5.5, 5.7, 5.8 |
| 5.10 | Sprint 2 Review and Retrospective | All Members | 5.9 |
| 5.11 | Sprint 2 Complete | All Members | 5.10 |

The approved WBS places WBS 5.9 on 3 to 4 September 2026.

## 3. Integration Goal

Sprint 2 integration should prove one coherent Career Analysis flow:

```text
Authenticated Student
        |
        v
Student Profile Skills and Proficiency
        |
        v
Career and Skill Reference Data
        |
        v
Weighted Career Recommendations
        |
        v
Career Recommendation API
        |
        v
Recommendation and Readiness Interface
        |
        v
Selected Career
        |
        +--------------------+
        |                    |
        v                    v
Skill Gap Analysis     Career Readiness Score
        |                    |
        +---------+----------+
                  |
                  v
       Learning Suggestions API
                  |
                  v
        Learning Roadmap Interface
```

Recommendation score and readiness score must stay separate metrics.

## 4. Requirements Covered

Sprint 2 integration directly supports FR-03, FR-04, FR-05, FR-06, FR-11, and FR-12.

Important quality requirements include usability, responsive design, performance, security, privacy, maintainability, reliability, explainability, accessibility, compatibility, testability, and separation of frontend, API, service, and database layers.

## 5. Current Repository Baseline

Repository review of `feature/sprint-2` on 3 September 2026 confirms:

- WBS 5.2 reference-data models, migrations, curated data, mappings, and import support are present.
- WBS 5.3 deterministic recommendation scoring is present in `backend/careers/services/recommendation_scoring.py`.
- WBS 5.3 design documentation is present in `docs/system-design/recommendation-scoring-design.md`.
- WBS 5.5 Skill Gap and Career Readiness scoring is present in `backend/careers/services/readiness_scoring.py`.
- WBS 5.5 design documentation is present in `docs/system-design/readiness_scoring_design.md`.
- Backend Career tests are present in `backend/careers/tests.py`.
- `backend/careers/views.py` still contains the default Django placeholder only. The WBS 5.4 Career Recommendation API is therefore not available in the shared Sprint 2 branch at this checkpoint.
- The shared Sprint 2 branch does not contain the planned WBS 5.6 recommendation/readiness interface, WBS 5.7 learning suggestions and roadmap API, or WBS 5.8 learning roadmap interface at this checkpoint.

A missing integration dependency is recorded as Blocked in the Sprint 2 Test Case Tracker. A blocked case is not treated as a failed test.

## 6. Integration Branch Strategy

Integration target: `feature/sprint-2`.

Rules:

1. Merge each WBS implementation through a reviewed pull request.
2. Update the local `feature/sprint-2` branch before integration testing.
3. Do not exchange uncommitted local files as the integration method.
4. Keep producer and consumer contracts stable before dependent integration.
5. Record integration defects and retests in the Sprint 2 Test Case Tracker.
6. Use GitHub history and pull requests as integration evidence.
7. Do not rewrite shared branch history.

## 7. Integration Entry Criteria

WBS 5.9 full execution starts when:

- WBS 5.4, WBS 5.5, WBS 5.7, and WBS 5.8 are merged into `feature/sprint-2`.
- WBS 5.6 is available for the integrated UI flow.
- Django system checks pass.
- Required migrations apply successfully.
- Backend automated tests pass.
- React lint and production build pass.
- Dataset 1.0 is available.
- No unresolved merge conflict exists.
- Safe test accounts and test data are available.
- Secrets stay outside Git and test evidence.

If a prerequisite is missing, affected cases stay Blocked.

## 8. Integration Sequence

### 8.1 Baseline Verification

1. Update `feature/sprint-2` from the remote repository.
2. Confirm a clean working tree.
3. Run Django system checks.
4. Check migration status and apply required migrations.
5. Run backend regression tests.
6. Run frontend lint and production build.
7. Confirm PostgreSQL connectivity.
8. Confirm Dataset 1.0 is loaded and valid.

### 8.2 WBS 5.2 and WBS 5.3 Verification

Verify:

- Active Career reference records are available.
- Canonical Skill mappings resolve correctly.
- Only approved active source-backed evidence enters numerical scoring.
- Recommendation scores are deterministic.
- Recommendation ranking follows the approved stable tie rules.
- Empty Student Skill profiles return `insufficient_profile` rather than a false numeric score.
- Careers without eligible numerical evidence return `insufficient_evidence`.
- Explanation evidence does not alter the numerical recommendation score.

### 8.3 WBS 5.4 Career Recommendation API

After WBS 5.4 is merged, verify:

- Authentication is required.
- The authenticated Student Profile supplies the Student Skill input.
- One Student cannot request another Student's profile-derived results.
- API ranking order matches the WBS 5.3 service order.
- Career ID, score, rank, status, and approved explanation information serialize correctly.
- Empty-profile and insufficient-evidence states stay controlled.
- Errors follow the shared REST API conventions.

### 8.4 WBS 5.5 Readiness Integration

Verify:

- Foundational maps to 25.
- Developing maps to 50.
- Proficient maps to 75.
- Advanced maps to 100.
- Missing Skills map to 0.
- O*NET Level provides the requirement threshold.
- O*NET Importance provides the weighting.
- Gap statuses distinguish `missing`, `below_requirement`, and `meets_requirement`.
- Readiness score stays separate from recommendation score.
- Empty Student Skill profiles return `insufficient_profile`.
- Careers without readiness evidence return `insufficient_evidence`.
- Gap ordering is deterministic.
- Readiness calculation does not modify Dataset 1.0.

### 8.5 WBS 5.6 Frontend Integration

After WBS 5.6 is available, verify:

- Ranked Careers load from the API.
- Frontend order matches API rank order.
- Recommendation score and explanation are visible.
- A Student selects a Career for detailed analysis.
- Readiness score is displayed separately from recommendation score.
- Missing and below-requirement Skills are distinguishable.
- Loading, empty, insufficient-profile, insufficient-evidence, and API-error states are controlled.
- Core functions work with keyboard navigation.
- Layout stays usable at common desktop, tablet, and mobile widths.

### 8.6 WBS 5.7 Learning Suggestions and Roadmap API

After WBS 5.7 is merged, verify:

- Unresolved WBS 5.5 gaps are consumed.
- Missing and below-requirement Skills receive appropriate learning suggestions.
- Met requirements are not prioritised as unresolved gaps.
- Selected Career context is preserved.
- Empty and insufficient-evidence states are handled safely.
- Invalid input returns a controlled validation response.
- Repeated unchanged structured input produces stable output where the implementation is deterministic.

### 8.7 WBS 5.8 Learning Roadmap Interface

After WBS 5.8 is available, verify:

- Ordered roadmap items render from the backend response.
- Display order matches API order.
- Skill names match the selected Career gaps.
- Resources and actions map to the correct Skill.
- Empty and API-error states are controlled.
- Navigation preserves selected Career context.

### 8.8 Full Sprint 2 Flow

Run this end-to-end flow:

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

Repeat the flow with:

- A partial-match Student.
- A Student with unrelated Skills.
- A Student with no StudentSkill rows.
- A Career with insufficient readiness evidence.
- A second Student for privacy and ownership isolation.

## 9. Integration Contract Matrix

| Handoff | Producer | Consumer | Minimum data to verify |
| --- | --- | --- | --- |
| Student Profile to Recommendation Engine | Student Profile | WBS 5.3 | Canonical Skill IDs |
| Recommendation Engine to API | WBS 5.3 | WBS 5.4 | Career ID, score, rank, status, explanation data |
| API to Recommendation UI | WBS 5.4 | WBS 5.6 | Authenticated response structure |
| Student Profile to Readiness | Student Profile | WBS 5.5 | Canonical Skill IDs and proficiency |
| Readiness to UI | WBS 5.5 and API layer | WBS 5.6 | Readiness score, status, Skill gaps |
| Readiness to Learning API | WBS 5.5 | WBS 5.7 | Missing and below-requirement Skills plus gap context |
| Learning API to Roadmap UI | WBS 5.7 | WBS 5.8 | Ordered roadmap items |

Producer contract changes must be communicated to the consumer owner before integration.

## 10. Database Integration Checks

Verify:

- Career and Skill reference-data integrity.
- Valid CareerSkill relationships.
- No unintended duplicate readiness evidence.
- StudentSkill ownership and proficiency persistence.
- Read-only recommendation and readiness scoring behaviour.
- Valid foreign keys.
- Consistent migration history.
- Dataset 1.0 stays unchanged after read-only validation.

## 11. Security and Privacy Checks

Verify:

- Protected Career Analysis endpoints reject unauthenticated requests.
- Invalid authentication is handled safely.
- One Student does not receive another Student's profile-derived recommendation, readiness, or roadmap information.
- Frontend code does not expose backend secrets, database credentials, signing secrets, or AI keys.
- API errors do not expose stack traces, server paths, SQL, secrets, or credentials.

## 12. Error and Empty-State Integration

Test these states:

- Empty Student Skill profile.
- Insufficient recommendation evidence.
- Insufficient readiness evidence.
- Invalid Career ID.
- Inactive Career.
- Empty learning suggestions.
- API validation errors.
- Unauthenticated request.
- Invalid authentication.
- Backend request failure.
- Loading state.
- Empty result state.

A controlled empty or insufficient-evidence state is not a failed calculation.

## 13. Performance, Reliability, and Explainability

- Normal non-AI API responses target 2 seconds under expected classroom use.
- Repeated unchanged structured inputs should return repeatable recommendation and readiness results.
- Recommendation and readiness factors should be visible to the Student.
- Missing and below-requirement Skills should be distinguishable.
- Learning suggestions should trace to identified Skill gaps.

## 14. Defect Process

For each failed test, record:

- Test ID.
- Actual result.
- Defect reference.
- Likely component owner.
- Fix branch or pull request.
- Retest result.
- Affected regression result.

Do not change Fail to Pass until a retest verifies the fix.

## 15. Rollback and Recovery

If a merge breaks `feature/sprint-2`:

1. Stop dependent merges.
2. Identify the regression source.
3. Preserve relevant logs and test results.
4. Prefer a corrective pull request for a small fix.
5. Revert only with team agreement when correction is not the safer option.
6. Rerun affected automated and regression tests.
7. Update the tracker and team task board.

## 16. Team Responsibilities

### Jerald

- WBS 5.3 and WBS 5.5 regression support.
- Recommendation and readiness calculation verification.
- Dataset 1.0 integrity checks.
- Shared integration support.

### MD

- WBS 5.4 and WBS 5.7 API verification.
- Backend and API defect support.

### Joyee

- WBS 5.6 and WBS 5.8 frontend verification.
- Responsive and accessibility defect support.

### All Members

- WBS 5.9 end-to-end testing.
- Defect triage.
- Regression testing.
- Sprint 2 exit review.

## 17. Evidence Management

Store Sprint 2 evidence under:

```text
docs/testing/evidence/sprint-2/
```

Evidence may include:

- Automated test output.
- Sanitised terminal output.
- Screenshots.
- API responses with secrets removed.
- Browser compatibility checks.
- GitHub pull request checks.
- Dataset validation summaries.
- Defect and retest results.

Record evidence IDs in `docs/testing/sprint-2-test-cases.xlsx`.

## 18. Integration Exit Criteria

WBS 5.9 is ready for completion when:

- Required predecessors are merged.
- Critical Career Analysis cases pass.
- No unresolved Critical or High defect blocks the core flow.
- Recommendation and readiness determinism checks pass.
- Security and privacy regression checks pass.
- React and Django integration works for the planned Career Analysis flow.
- Learning suggestions and roadmap data connect to identified Skill gaps.
- Required test evidence is recorded.
- Deferred issues are documented.
- The team agrees the Sprint 2 increment is ready for review.

## 19. Repository Verification Basis

This plan was aligned against the following current repository paths:

- `docs/project-management/work-breakdown-structure.md`
- `docs/system-design/rest-api-design.md`
- `docs/system-design/recommendation-scoring-design.md`
- `docs/system-design/readiness_scoring_design.md`
- `backend/careers/models.py`
- `backend/careers/services/recommendation_scoring.py`
- `backend/careers/services/readiness_scoring.py`
- `backend/careers/tests.py`
- `backend/careers/views.py`
- `data/reference/`

## 20. Current Plan Status

Prepared and aligned with the current shared Sprint 2 branch.

WBS 5.2, WBS 5.3, and WBS 5.5 have integration-ready backend foundations in `feature/sprint-2`.

Cases dependent on WBS 5.4, WBS 5.6, WBS 5.7, or WBS 5.8 stay Blocked until those components satisfy their entry criteria.
