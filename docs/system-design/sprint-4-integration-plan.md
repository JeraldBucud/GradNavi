# GradNavi Sprint 4 Integration Plan

Status: Prepared for WBS 7.9 Sprint 4 Integration and Testing. Planning is ready. Final WBS 7.9 execution stays blocked until required Sprint 4 predecessors are integrated.

WBS: 7.9 Sprint 4 Integration and Testing

Owner: All Members

Integration branch: `feature/sprint-4`

Planning branch: `jerald/wbs-7.9-sprint-4-integration-testing`

Planned Sprint 4 dates: 21 September to 2 October 2026

## 1. Purpose

This document defines the integration approach for GradNavi Sprint 4.

WBS 7.9 verifies that the completed Sprint 4 components work together with the existing Sprint 1, Sprint 2, and Sprint 3 functionality.

The plan covers integration preparation, dependency gates, end-to-end flows, regression coverage, security-sensitive checks, evidence requirements, defect handling, and Sprint 4 exit conditions.

This plan does not mark any integration test as passed.

Detailed execution status will be maintained in:

`docs/testing/sprint-4-test-cases.xlsx`

## 2. WBS Alignment

WBS 7.9 is owned by All Members.

The approved WBS lists these predecessors:

- WBS 7.4 AI Response Validation and Error Handling
- WBS 7.5 Job Matching Interface
- WBS 7.6 Admin Models and API
- WBS 7.7 Admin Dashboard Interface
- WBS 7.8 Role Permissions and Audit Records

Full WBS 7.9 execution starts only after the required predecessor work is integrated into `feature/sprint-4`.

Planning, test definition, fixture preparation, and evidence preparation are allowed before the final integration gate opens.

## 3. Current Dependency Snapshot

Current Sprint 4 integration state at this planning checkpoint:

- WBS 7.2 Job Description Extraction and Matching is merged.
- WBS 7.3 OpenAI Service Integration is merged.
- WBS 7.4 AI Response Validation and Error Handling is technically complete in PR #66 and awaiting review and merge.
- WBS 7.5 Job Matching Interface is merged through PR #61.
- WBS 7.6 Admin Models and API is open in PR #62.
- WBS 7.7 Admin Dashboard Interface is open as draft PR #64 and remains in progress.
- WBS 7.8 Role Permissions and Audit Records is still required before final WBS 7.9 execution.

The current repository planning records still require alignment with the latest team decision for WBS 7.8 ownership.

## 4. Integration Goal

Sprint 4 integration should provide evidence that the following work together through the shared application:

1. Authentication and Student Profile.
2. Career Recommendations and explanation.
3. Skill Gap and Career Readiness.
4. Learning Suggestions and Career Roadmap.
5. Resume generation.
6. Cover Letter generation.
7. Interview Question generation and feedback.
8. Job Description Matching.
9. AI response validation and controlled provider failure handling.
10. Basic Administration.
11. Administrator permissions.
12. Student rejection from administrator-only operations.
13. Audit-record creation for approved critical actions.

## 5. Integration Environment

| Component | Sprint 4 Environment |
| --- | --- |
| Frontend | React and Vite |
| Backend | Django and Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT |
| AI Provider Boundary | GradNavi `ai_services` |
| External AI Provider | OpenAI through the Django backend |
| Version Control | Git and GitHub |
| Shared Integration Branch | `feature/sprint-4` |
| Evidence Directory | `docs/testing/evidence/sprint-4/` |
| Test Tracker | `docs/testing/sprint-4-test-cases.xlsx` |

Secrets, passwords, JWT values, database credentials, and real private Student information must not appear in committed evidence.

## 6. Integration Entry Criteria

Before final WBS 7.9 execution:

- WBS 7.4 must be merged.
- WBS 7.5 must be merged.
- WBS 7.6 must be merged.
- WBS 7.7 must be merged.
- WBS 7.8 must be merged.
- Local `feature/sprint-4` must match `origin/feature/sprint-4`.
- PostgreSQL must be available.
- Django system check must pass.
- Migration drift check must pass.
- Backend automated tests must pass.
- Frontend lint must pass.
- Frontend production build must pass.
- The Sprint 4 test tracker must be ready.
- Required test accounts and safe synthetic test data must be available.
- No unresolved Critical dependency defect may prevent the main Sprint 4 flows.

## 7. Integration Sequence

Run integration in this order:

1. Environment and baseline verification.
2. Authentication and Student Profile smoke checks.
3. Sprint 1 regression.
4. Sprint 2 regression.
5. Sprint 3 document and Interview regression.
6. WBS 7.2 and WBS 7.5 Job Matching integration.
7. WBS 7.3 and WBS 7.4 AI provider integration and failure handling.
8. WBS 7.6 Admin API integration.
9. WBS 7.7 Admin Dashboard integration.
10. WBS 7.8 permission and audit integration.
11. Cross-feature Sprint 4 flows.
12. Full backend regression.
13. Frontend lint and production build.
14. Responsive and browser checks.
15. Evidence review.
16. Defect retest.
17. WBS 7.9 completion review.

## 8. Job Matching Integration Flow

Required flow:

Login
-> Student Profile
-> Job Matching
-> Enter Job Description
-> Submit
-> Extract Requirements
-> Compare with Student Profile
-> Display Matched Requirements
-> Display Missing Requirements

Verify:

- The Job Matching page is protected.
- The authenticated Student Profile is used.
- One job description is accepted at a time.
- Blank job descriptions are rejected.
- Oversized job descriptions are rejected.
- Unsupported or ambiguous terms are not guessed.
- Matched requirements reflect the Student Profile.
- Missing requirements are clearly separated.
- Job Matching does not present an employment suitability score.
- Student ownership identifiers are not accepted from the client.
- Job-description text is not persisted by the matching endpoint.
- Job Matching results do not modify Student Profile data.
- Job-description handoff to Resume Builder works.
- Job-description handoff to Cover Letter Builder works.
- Skill Gap and Student Profile next-step navigation works.

## 9. Resume AI Integration Flow

Required flow:

Login
-> Student Profile
-> Resume Builder
-> Generate Draft
-> OpenAI Provider
-> Validate Response
-> Review or Edit Draft

Verify:

- Authentication is required.
- Approved Student Profile context is used.
- Private or unapproved profile fields stay excluded.
- The backend owns the OpenAI request.
- The frontend does not call OpenAI directly.
- Generated output satisfies the Resume contract.
- Invalid or incomplete provider output is rejected.
- Controlled provider failures do not expose internal details.
- Generated content stays reviewable and editable.
- The UI shows loading and controlled error states.

## 10. Cover Letter AI Integration Flow

Required flow:

Login
-> Student Profile
-> Cover Letter Builder
-> Enter Job Description
-> Generate Draft
-> OpenAI Provider
-> Validate Response
-> Review or Edit Draft

Verify:

- Authentication is required.
- One job description is supplied as untrusted input.
- Student-owned profile context is used.
- Client ownership override is rejected.
- Provider output satisfies the Cover Letter contract.
- Invalid or incomplete output is rejected.
- Controlled provider failures do not expose internal details.
- Student facts are not fabricated by the integration layer.
- Generated content stays reviewable and editable.
- Job Matching handoff text reaches the Cover Letter Builder where expected.

## 11. Interview AI Integration Flow

Required flow:

Login
-> Interview Preparation
-> Generate Questions
-> OpenAI Provider
-> Validate Response
-> Enter Answer
-> Submit Answer
-> Receive Validated Feedback

Verify:

- Authentication is required.
- Question count validation is enforced.
- Returned question count matches the requested count.
- Question focus areas satisfy the approved semantic contract.
- Blank, duplicate, missing, or extra focus areas are rejected where required.
- Typed answers remain untrusted input.
- Feedback output satisfies the approved schema.
- Hiring probability and pass or fail classification are not introduced.
- Provider errors are controlled.
- Generated content remains reviewable by the Student.

## 12. Administration Integration Flow

Required flow:

Administrator Login
-> Admin Dashboard
-> Approved Administration Action
-> Backend Permission Check
-> Data Update
-> Audit Record

Verify the approved administration workflows exposed by WBS 7.6 and WBS 7.7.

Expected administration areas include:

- Users
- Careers
- Skills
- Learning Resources

Verify:

- Administrator authentication.
- Administrator authorisation.
- Loading state.
- Empty state.
- Validation state.
- Permission-denied state.
- Controlled API error state.
- Successful approved administration action.
- Frontend behaviour matches the backend contract.
- Private Student fields are not unnecessarily exposed.
- The React interface does not act as the security boundary.

## 13. Permission Rejection Flow

Required flow:

Student Login
-> Attempt Administrator Operation
-> Backend Permission Check
-> Access Denied

Verify:

- Student users cannot call administrator-only APIs.
- Hiding a frontend control is not treated as permission enforcement.
- Direct API access is rejected by Django.
- Unauthenticated administration access is rejected.
- The response does not expose sensitive internal details.
- Role isolation remains correct after integration.

## 14. Audit Integration

After WBS 7.8 is integrated, verify approved critical actions create the required audit evidence.

Audit verification should confirm:

- Required critical actions create records.
- Records identify the relevant action.
- Records include only approved audit data.
- Secrets are not stored.
- Passwords are not stored.
- JWT values are not stored.
- Unnecessary private Student information is not stored.
- Audit access follows the approved permission model.

## 15. AI Failure Integration

WBS 7.4 requires controlled handling of external AI failures.

Verify:

- Timeout handling.
- Provider unavailable handling.
- Connection failure handling.
- Rate-limit handling.
- Provider HTTP failure handling.
- Malformed output handling.
- Incomplete output handling.
- Missing response status handling.
- Sanitized frontend-facing errors.

AI failure must not modify deterministic:

- Career Recommendation scores.
- Career Recommendation rank.
- Skill Gap calculations.
- Career Readiness scores.
- Job Matching matched and missing requirements.

## 16. Regression Scope

WBS 7.9 regression must include:

- Registration and login.
- JWT behaviour.
- Current-user retrieval.
- Student Profile load and update.
- Student ownership isolation.
- Career Recommendations.
- Recommendation explanation.
- Skill Gap.
- Career Readiness.
- Learning Suggestions.
- Career Roadmap.
- Resume generation.
- Cover Letter generation.
- Interview Questions.
- Interview Feedback.
- Job Matching.
- Administration permissions.
- PostgreSQL connectivity.
- Django checks.
- Frontend lint.
- Frontend production build.

## 17. Performance and Reliability Checks

NFR-03 requires normal non-AI API responses to complete within 2 seconds under expected classroom use.

AI operations should show a loading state and use configured timeout handling.

Record:

- Endpoint or action.
- Whether AI is involved.
- Approximate response time.
- Loading-state behaviour.
- Timeout behaviour where applicable.
- Environment used for the observation.

This is a classroom-use verification, not a production load test.

## 18. Responsive, Accessibility, and Browser Checks

Check planned Sprint 4 interfaces at current desktop, tablet, and mobile widths.

Verify:

- Labels.
- Keyboard operation.
- Focus behaviour.
- Validation feedback.
- Readable contrast.
- Loading states.
- Error states.
- Chrome.
- Edge.
- Firefox.

## 19. Test Data

Use safe synthetic or development data.

Required test-data categories:

- Valid Student account.
- Second Student account for ownership isolation.
- Administrator account.
- Student Profile with Skills.
- Student Profile with Education, Experience, Projects, Goals, and approved AI context.
- Valid job description.
- Blank job description.
- Oversized job description.
- Instruction-like job description for trust-boundary verification.
- Valid target career.
- Valid Resume generation request.
- Valid Cover Letter generation request.
- Valid Interview request.
- Typed Interview answer.
- Simulated provider failure conditions.
- Approved administration records for test updates.

Do not commit real passwords, access tokens, API keys, or private employment data.

## 20. Evidence Rules

Store WBS 7.9 evidence under:

`docs/testing/evidence/sprint-4/`

Each executed test should record:

- Test ID.
- Status.
- Actual result.
- Tester.
- Test date.
- Evidence ID where required.
- Evidence reference.
- Defect reference for failures.
- Blocked dependency for blocked cases.
- Retest result where applicable.

A Blocked case is not a Failed case.

## 21. Defect Handling

Defect severity:

| Severity | Meaning |
| --- | --- |
| Critical | Core flow cannot complete, serious security or privacy failure, or major data exposure |
| High | Major Sprint 4 function fails with no acceptable workaround |
| Medium | Function works partially or has a contained integration or usability defect |
| Low | Minor issue which does not block the planned demonstration flow |

For every fixed defect:

1. Retest the failed case.
2. Record new evidence.
3. Update the defect reference.
4. Run affected nearby regression cases.
5. Mark Pass only after verification.

## 22. Branch and Merge Rule

WBS 7.9 planning work stays on:

`jerald/wbs-7.9-sprint-4-integration-testing`

Final integration execution must use the latest integrated Sprint 4 code.

Before final execution:

1. Fetch `origin/feature/sprint-4`.
2. Update the local integration baseline.
3. Confirm all required predecessor PRs are merged.
4. Rebase or recreate the execution branch if required.
5. Run the planned integration suite.
6. Record results without overwriting historical evidence.

## 23. Exit Criteria

WBS 7.9 is ready for completion when:

- Required Sprint 4 predecessors are integrated.
- Core Job Matching flow passes.
- Core Resume flow passes.
- Core Cover Letter flow passes.
- Core Interview Question and Feedback flow passes.
- Core Administration flow passes.
- Student permission rejection passes.
- Required audit-record checks pass.
- AI controlled failure checks pass.
- Sprint 1 to Sprint 3 regression checks pass.
- Full backend regression passes.
- Django system check passes.
- Migration drift check passes.
- Frontend lint passes.
- Frontend production build passes.
- Required responsive, browser, and accessibility checks are recorded.
- No unresolved Critical or High defect blocks the planned Sprint 4 demonstration.
- Required evidence is indexed.
- The team accepts the Sprint 4 integrated increment.

## 24. Current Integration Status

Planning status:

READY

Final integration execution status:

DEPENDENCY BLOCKED

Current blocking predecessor work:

- WBS 7.4 awaiting merge.
- WBS 7.6 awaiting merge.
- WBS 7.7 in progress.
- WBS 7.8 required before final integration.

WBS 7.5 is already integrated.

No WBS 7.9 test result is recorded as Pass or Fail by this planning document.
