# GradNavi Sprint 4 Test Plan

Status: Prepared for WBS 7.9 Sprint 4 Integration and Testing. Test definitions are ready for controlled execution. Final execution stays blocked where a required Sprint 4 dependency is not yet integrated.

WBS: 7.9 Sprint 4 Integration and Testing

Owner: All Members

Test tracker:

`docs/testing/sprint-4-test-cases.xlsx`

Evidence directory:

`docs/testing/evidence/sprint-4/`

## 1. Purpose

This document defines the team-level Sprint 4 testing approach for GradNavi.

Sprint 4 testing verifies Job Description Matching, external AI service integration, AI response validation, Basic Administration, role permissions, audit behaviour, and regression across the completed GradNavi system.

The detailed execution status belongs in the Sprint 4 Test Case Tracker.

This plan does not replace focused automated tests inside backend or frontend modules.

## 2. WBS Alignment

WBS 7.9 is owned by All Members.

WBS 7.9 depends on:

- WBS 7.4 AI Response Validation and Error Handling
- WBS 7.5 Job Matching Interface
- WBS 7.6 Admin Models and API
- WBS 7.7 Admin Dashboard Interface
- WBS 7.8 Role Permissions and Audit Records

Test planning proceeds before all dependencies are merged.

A test is marked Blocked only when a specific required dependency or environment is unavailable.

A defined test which is ready but has not been executed is marked Not Run.

## 3. Sprint 4 Testing Goal

Sprint 4 testing should provide evidence that:

1. Job Description Matching works through the Student interface and deterministic backend.
2. OpenAI-backed Resume, Cover Letter, and Interview flows work through the approved backend provider boundary.
3. Invalid, incomplete, or unavailable AI responses fail safely.
4. Deterministic recommendation, Skill Gap, Career Readiness, and Job Matching results remain protected during AI failure.
5. Authorised administrators can perform approved administration operations.
6. Students cannot perform administrator-only operations.
7. Approved critical actions create audit evidence after WBS 7.8 integration.
8. Sprint 1, Sprint 2, and Sprint 3 core behaviour remains stable.
9. Required frontend states work across planned browser widths and current browsers.
10. Required evidence and defect records are complete.

## 4. Requirements Traceability

| Requirement | Sprint 4 Test Focus |
| --- | --- |
| FR-01 | Authentication regression |
| FR-02 | Student Profile regression and ownership |
| FR-03 | Career Recommendation regression |
| FR-04 | Recommendation explanation regression |
| FR-05 | Skill Gap regression |
| FR-06 | Career Readiness regression |
| FR-07 | Job Description Matching |
| FR-08 | Resume generation regression and OpenAI integration |
| FR-09 | Cover Letter regression and OpenAI integration |
| FR-10 | Interview Questions and Feedback integration |
| FR-11 | Learning Suggestions regression |
| FR-12 | Career Roadmap regression |
| FR-14 | Basic Administration |
| FR-16 | Review and edit generated content |
| FR-18 | Audit and controlled external-service error handling |
| NFR-02 | Responsive design |
| NFR-03 | API performance, loading, and timeout behaviour |
| NFR-05 | Authentication and authorisation |
| NFR-06 | Privacy and Student isolation |
| NFR-08 | Deterministic repeatability |
| NFR-09 | Explainability |
| NFR-10 | Accessibility basics |
| NFR-11 | Chrome, Edge, and Firefox |
| NFR-12 | Acceptance and automated test evidence |
| NFR-13 | Frontend, backend, database, and AI service separation |
| NFR-14 | Ethical AI and review limitations |

FR-15 Admin Analytics stays outside mandatory WBS 7.9 acceptance unless the team confirms its Sprint 4 scope.

FR-13 and FR-17 remain schedule-alignment items unless separately approved.

## 5. Testing Scope

Sprint 4 testing covers:

- Job Matching backend.
- Job Matching frontend.
- Job-description handoff to Resume Builder.
- Job-description handoff to Cover Letter Builder.
- OpenAI provider integration.
- AI response-state validation.
- AI structured-output validation.
- AI semantic validation.
- Controlled provider failures.
- Resume integration.
- Cover Letter integration.
- Interview Question integration.
- Interview Feedback integration.
- Admin API.
- Admin Dashboard.
- Administrator permission enforcement.
- Student rejection from administrator operations.
- Audit records after WBS 7.8.
- Authentication regression.
- Student Profile regression.
- Career Recommendation regression.
- Recommendation Explanation regression.
- Skill Gap regression.
- Career Readiness regression.
- Learning Suggestions regression.
- Career Roadmap regression.
- PostgreSQL connectivity.
- Django checks.
- Frontend lint and build.
- Responsive checks.
- Browser compatibility.
- Accessibility basics.
- Evidence review.

## 6. Related Testing Documentation

Relevant documents include:

- `docs/project-management/sprint-4-plan.md`
- `docs/system-design/sprint-4-integration-plan.md`
- `docs/testing/sprint-4-test-cases.xlsx`
- `docs/testing/evidence/sprint-4/`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`
- `docs/system-design/rest-api-design.md`
- `docs/system-design/security-architecture.md`
- Sprint 1 Test Plan
- Sprint 2 Test Plan
- Sprint 3 Test Plan

## 7. Testing Levels

### 7.1 Unit and Schema Testing

Verify:

- Request validation.
- Required fields.
- Field length limits.
- Extra-field rejection.
- AI response schemas.
- AI response status validation.
- Interview semantic rules.
- Admin serializer validation.
- Deterministic scoring and matching logic.

### 7.2 API Testing

Verify:

- JWT requirements.
- Authentication.
- Authorisation.
- Student ownership.
- Job Matching request and response contracts.
- Resume and Cover Letter operations.
- Interview operations.
- Admin endpoints.
- Controlled HTTP errors.
- Provider failure translation.
- Audit endpoints or records where approved.

### 7.3 Integration Testing

Verify communication across:

React
-> Django REST API
-> Feature Service
-> PostgreSQL where required

For AI flows:

React
-> Django REST API
-> Feature Service
-> Prompt and Safety Layer
-> OpenAI Provider Boundary
-> OpenAI Service
-> AI Response Validation
-> Structured Application Result

### 7.4 Permission Testing

Verify:

- Unauthenticated access rejection.
- Student access to Student functions.
- Administrator access to approved administration functions.
- Student rejection from administrator-only endpoints.
- Direct backend permission enforcement.
- Role isolation.
- Cross-student privacy isolation.

### 7.5 Frontend Testing

Verify:

- Loading states.
- Empty states.
- Validation states.
- Permission-denied states.
- Controlled API-error states.
- Successful result states.
- Review and edit generated content.
- Responsive layout.
- Keyboard use.
- Browser compatibility.

### 7.6 Regression Testing

Verify Sprint 1, Sprint 2, and Sprint 3 core behaviour remains stable after Sprint 4 integration.

## 8. Test Environment

| Component | Sprint 4 Environment |
| --- | --- |
| Frontend | React and Vite |
| Backend | Django and Django REST Framework |
| Authentication | JWT |
| Database | PostgreSQL |
| AI Provider | OpenAI through the GradNavi backend |
| API Testing | Django tests and controlled manual API checks |
| Browser Testing | Current Chrome, Edge, and Firefox |
| Integration Branch | `feature/sprint-4` |
| Evidence Folder | `docs/testing/evidence/sprint-4/` |

## 9. Test Data Principles

Use safe development data.

Test data should include:

- Valid Student account.
- Second Student account for privacy testing.
- Administrator account.
- Student Profile with canonical Skills.
- Student Profile with Education, Experience, Projects, Career Goals, and approved AI context.
- Valid target career.
- Valid job description.
- Blank job description.
- Oversized job description.
- Instruction-like job description.
- Valid Interview request.
- Invalid Interview request.
- Typed Interview answer.
- Simulated provider timeout or unavailable state.
- Approved administration records.

Do not store real passwords, API keys, access tokens, private employment data, or unnecessary Student information in committed evidence.

## 10. Current Dependency Status

At this planning checkpoint:

- WBS 7.5 is integrated.
- WBS 7.4 is technically complete but awaiting merge.
- WBS 7.6 is awaiting merge.
- WBS 7.7 is in progress.
- WBS 7.8 is required before final integration.

The tracker should therefore use:

- Not Run for defined tests which are ready for later execution.
- Blocked only where a named dependency prevents execution.

## 11. Entry Criteria

Before final WBS 7.9 execution:

- Required predecessor work is merged.
- PostgreSQL is available.
- Django system check passes.
- Migration drift check passes.
- Backend automated tests pass.
- Frontend lint passes.
- Frontend production build passes.
- Safe test accounts exist.
- The Sprint 4 tracker is ready.
- Required dependency-specific test data exists.
- No unresolved Critical defect blocks the main integration flows.

## 12. Authentication and Student Profile Regression

Verify:

- Registration where still supported by the current baseline.
- Login.
- JWT access.
- Token refresh where supported.
- Current-user retrieval.
- Student Profile retrieval.
- Student Profile update.
- Student ownership isolation.
- Invalid authentication handling.
- Protected page behaviour.

## 13. Career Recommendation Regression

Verify:

- Authenticated recommendation request.
- Stable deterministic ranking for the same structured profile.
- Recommendation score display.
- Explanation availability where expected.
- Recommendation cache behaviour where applicable.
- Student isolation.
- AI explanation failure does not alter deterministic recommendation results.

## 14. Skill Gap and Career Readiness Regression

Verify:

- Selected-career Skill Gap.
- Matched requirements.
- Missing requirements.
- Career Readiness score.
- Readiness factors.
- Repeatable deterministic output.
- AI summary failure does not alter deterministic results.

## 15. Learning Suggestions and Career Roadmap Regression

Verify:

- Learning Resources load for the selected career.
- Ranked learning suggestions.
- Roadmap load.
- Roadmap ordered steps.
- Progress update where supported.
- Student ownership.
- Existing feedback actions where supported.

## 16. Job Matching Tests

Verify:

- Protected Job Matching page.
- Job-description submission.
- Blank input validation.
- Oversized input validation.
- Loading state.
- API error state.
- Matched requirement display.
- Missing requirement display.
- Canonical matching.
- Alias matching.
- Conservative handling of unsupported or ambiguous terms.
- No suitability or hiring score.
- Student Profile ownership.
- No client ownership override.
- No profile mutation.
- No job-description persistence by the matching endpoint.
- Resume Builder handoff.
- Cover Letter Builder handoff.
- Skill Gap navigation.
- Student Profile navigation.

## 17. Resume Integration Tests

Verify:

- Protected Resume Builder.
- Approved Student Profile context.
- OpenAI provider path through Django.
- Valid structured response.
- Response validation.
- Controlled provider failure.
- Loading state.
- Error state.
- Editable draft.
- Review requirement.
- Job Matching handoff where supported.

## 18. Cover Letter Integration Tests

Verify:

- Protected Cover Letter Builder.
- Required job description.
- Blank input validation.
- Untrusted job-description handling.
- Student ownership.
- OpenAI provider path through Django.
- Valid structured response.
- Controlled provider failure.
- Editable draft.
- Review requirement.
- Job Matching handoff where supported.

## 19. Interview Integration Tests

Verify:

- Protected Interview Preparation page.
- Valid question-generation request.
- Question-count boundaries.
- Question rendering.
- Focus-area semantic validation.
- Typed-answer submission.
- Feedback generation.
- Feedback rendering.
- Controlled provider failure.
- No hiring probability.
- No pass or fail hiring classification.
- Review and limitation messaging.

## 20. AI Response Validation and Failure Tests

Verify:

- Completed response acceptance.
- Incomplete response rejection.
- Non-completed response rejection.
- Missing response status rejection.
- Empty output rejection.
- Malformed JSON rejection.
- Timeout translation.
- Connection failure translation.
- Rate-limit translation.
- Provider HTTP failure translation.
- Unexpected provider failure translation.
- Sanitized provider errors.
- Deterministic result protection.

## 21. Admin API Tests

After WBS 7.6 is integrated, verify approved administrator APIs for:

- Users.
- Careers.
- Skills.
- Learning Resources.

Verify:

- Authentication.
- Administrator authorisation.
- Validation.
- Collection endpoints.
- Detail endpoints.
- Create, update, and delete behaviour where approved.
- No unnecessary password exposure.
- No unnecessary private Student Profile exposure.
- Controlled API errors.

## 22. Admin Dashboard Tests

After WBS 7.7 is integrated, verify:

- Protected admin route.
- Admin-only access.
- Loading state.
- Empty state.
- Permission-denied state.
- API-error state.
- Summary information.
- Approved management screens.
- Successful administration actions.
- Responsive layout.
- Keyboard operation.

Any Admin Analytics check is included only if the team confirms FR-15 Sprint 4 scope.

## 23. Role Permission Tests

After WBS 7.8 is integrated, verify:

- Administrator access to approved admin operations.
- Student rejection from admin APIs.
- Unauthenticated rejection.
- Direct backend enforcement.
- Frontend manipulation does not bypass permissions.
- Role isolation.
- Student-owned resource isolation.

## 24. Audit Record Tests

After WBS 7.8 is integrated, verify:

- Approved critical actions create audit records.
- Required action information is stored.
- Secrets are excluded.
- Passwords are excluded.
- JWT values are excluded.
- Unnecessary Student private information is excluded.
- Audit access follows the approved permission model.

## 25. Performance Tests

For normal non-AI API calls, record whether response time stays within the NFR-03 classroom-use target of 2 seconds.

For AI calls, verify:

- Loading state.
- Configured timeout handling.
- Controlled timeout result.

This is not a production load test.

## 26. Security and Privacy Tests

Verify:

- Protected endpoints require authentication.
- Administrator endpoints enforce role permission.
- Cross-student access is rejected.
- Student ownership is resolved by the backend.
- User-controlled text remains untrusted.
- Provider keys stay backend-only.
- API responses expose no credentials, tokens, stack traces, or provider internals.
- Audit records exclude unnecessary sensitive information.

## 27. Accessibility and Compatibility Tests

Check:

- Form labels.
- Keyboard access.
- Focus behaviour.
- Useful validation feedback.
- Readable contrast.
- Desktop layout.
- Tablet layout.
- Mobile layout.
- Chrome.
- Edge.
- Firefox.

## 28. Automation Strategy

Automate where practical:

- Backend unit tests.
- Schema tests.
- API authentication tests.
- Permission tests.
- Response validation.
- Provider failure tests.
- Deterministic regression.
- Django system check.
- Migration drift check.
- Frontend lint.
- Frontend production build.

Use manual or hybrid execution for:

- Visual layout.
- Responsive checks.
- Keyboard checks.
- Browser compatibility.
- Selected end-to-end flows.
- Evidence review.

## 29. Status Rules

| Status | Meaning |
| --- | --- |
| Pass | Expected behaviour was verified |
| Fail | Execution completed but expected behaviour was not met |
| Blocked | A named dependency or required environment prevents execution |
| Not Run | The test is defined and ready but has not been executed |
| Retest | A previous failure was fixed and awaits verification |

A Blocked test is not a Failed test.

Do not mark a test Pass based only on implementation claims.

## 30. Evidence Rules

Each executed case should record:

- Test ID.
- WBS.
- Requirement.
- Test level.
- Test case.
- Preconditions.
- Steps.
- Expected result.
- Owner.
- Status.
- Blocked dependency where applicable.
- Actual result.
- Tester.
- Evidence ID.
- Evidence reference.
- Defect reference.
- Automation classification.
- Notes.

Store evidence under:

`docs/testing/evidence/sprint-4/`

Evidence must not include passwords, API keys, JWT values, database credentials, or unnecessary private Student data.

## 31. Defect Severity

| Severity | Meaning |
| --- | --- |
| Critical | Core flow cannot complete, security or privacy breach, or serious data exposure |
| High | Major Sprint 4 function fails without an acceptable workaround |
| Medium | Partial function or contained integration or usability problem |
| Low | Minor issue which does not block the planned demonstration |

Critical and High defects affecting the core Sprint 4 flow block WBS 7.9 completion unless the team documents and approves a safe exception.

## 32. Retest and Regression Rule

For every fixed defect:

1. Retest the failed case.
2. Record new evidence.
3. Update the defect reference.
4. Run nearby regression cases.
5. Mark Pass only after verification.

## 33. Exit Criteria

WBS 7.9 testing is ready for completion when:

- All required predecessor tasks are integrated.
- Core Job Matching flow passes.
- Core Resume flow passes.
- Core Cover Letter flow passes.
- Core Interview flow passes.
- Core Administration flow passes.
- Student permission rejection passes.
- Required audit-record checks pass.
- AI failure handling passes.
- Sprint 1 to Sprint 3 regression passes.
- Full backend regression passes.
- Django system check passes.
- Migration drift check passes.
- Frontend lint passes.
- Frontend production build passes.
- Required responsive, browser, and accessibility checks are recorded.
- Required evidence is indexed.
- No unresolved Critical or High defect blocks the planned Sprint 4 demonstration.
- The team accepts the integrated Sprint 4 increment.

## 34. Current Plan Status

Planning:

READY

Final WBS 7.9 execution:

DEPENDENCY BLOCKED

The initial Sprint 4 tracker should contain only Not Run and Blocked cases.

No Pass or Fail result should be recorded until the related test is executed.
