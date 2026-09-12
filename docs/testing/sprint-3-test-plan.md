# GradNavi Sprint 3 Test Plan

Status: Prepared for WBS 6.8 Document and Interview Integration and WBS 6.9 Sprint 3 Testing. Verified WBS 6.2 and WBS 6.6 component cases are recorded as Pass. Cases depending on WBS 6.4, WBS 6.5, WBS 6.7, the WBS 6.6 merge, or the final WBS 6.8 integration gate stay Blocked until those dependencies are available.

## 1. Purpose

This document defines the team-level Sprint 3 testing approach for the GradNavi Application Documents and Interview Preparation increment.

Sprint 3 testing verifies that the AI safety foundation, Resume generation, Cover Letter generation, document interfaces, Interview Question generation, Interview Feedback, and Interview interface work together as planned.

Detailed execution status is maintained in:

```text
docs/testing/sprint-3-test-cases.xlsx
```

This plan provides the higher-level team testing structure. It does not replace focused implementation tests inside backend or frontend modules.

## 2. WBS Alignment

WBS 6.8 is owned by All Members and depends on WBS 6.3, WBS 6.4, WBS 6.5, WBS 6.6, and WBS 6.7.

WBS 6.9 is owned by All Members and depends on WBS 6.8.

The approved Sprint 3 dates are 7 September to 18 September 2026.

## 3. Sprint 3 Testing Goal

Sprint 3 testing should provide evidence that an authenticated Student is able to:

1. Generate an editable Resume draft from approved Student Profile data.
2. Generate an editable Cover Letter tailored to one selected job description.
3. Review AI-generated document content before use.
4. Generate text-based Interview questions for a target role.
5. Type an answer to a selected Interview question.
6. Receive structured Interview feedback.
7. Receive useful controlled validation and provider-error states.
8. Keep private Student data isolated from another Student.
9. Use document and Interview pages across planned browser widths and current browsers.
10. Complete core Sprint 3 flows without breaking Sprint 1 or Sprint 2 functionality.

Testing should also verify that the WBS 6.2 AI safety and privacy boundaries remain intact after integration.

## 4. Requirements Traceability

| Requirement | Test Focus |
| --- | --- |
| FR-08 | Editable Resume draft from Student Profile data |
| FR-09 | Editable Cover Letter tailored to one selected job description |
| FR-10 | Text-based Interview questions and feedback on typed answers |
| FR-16 | Student review and editing of generated AI content |
| FR-18 | Clear controlled errors when AI or external services fail |
| NFR-01 | Usability of document and Interview flows |
| NFR-02 | Responsive desktop, tablet, and mobile layouts |
| NFR-03 | Normal API performance plus AI loading/timeout behaviour |
| NFR-05 | Authentication and protected endpoints |
| NFR-06 | Privacy and cross-student isolation |
| NFR-07 | Modular and maintainable integration |
| NFR-10 | Labels, keyboard access, readable contrast, validation |
| NFR-11 | Current Chrome, Edge, and Firefox |
| NFR-12 | Automated and acceptance test evidence |
| NFR-13 | Separation of frontend, backend, database, and AI services |
| NFR-14 | Limitations and ethical AI safeguards |

## 5. Testing Scope

Sprint 3 testing covers:

- WBS 6.2 AI operation contracts.
- AI privacy allowlists.
- Trusted and untrusted prompt boundaries.
- Resume Generation Backend.
- Cover Letter Generation Backend.
- Resume and Cover Letter Interface.
- Interview Question API.
- Interview Feedback API.
- Interview Preparation Interface.
- JWT authentication.
- Cross-student privacy isolation.
- Strict request validation.
- Prompt-injection boundary checks.
- Generated-content review requirements.
- Provider unavailable and timeout behaviour.
- Frontend loading and API-error states.
- Responsive layout.
- Accessibility basics.
- Chrome, Edge, and Firefox compatibility.
- WBS 6.8 end-to-end integration.
- Sprint 1 authentication and Student Profile regression.
- Sprint 2 Career Analysis regression.

## 6. Related Testing Documentation

Relevant documentation includes:

- `docs/system-design/sprint-3-integration-plan.md`
- `docs/testing/sprint-3-test-cases.xlsx`
- `docs/testing/evidence/sprint-3/`
- `docs/system-design/rest-api-design.md`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`
- WBS 6.2 closeout and Sprint 3 evidence
- WBS 6.6 closeout and Sprint 3 evidence

The Sprint 3 Test Case Tracker records WBS traceability, requirements, priority, ownership, execution status, actual results, evidence IDs, blocked dependencies, defects, and automation type.

## 7. Testing Levels

### 7.1 Unit and Schema Testing

Verify:

- Strict request types.
- Required fields.
- Length and range limits.
- Extra-field rejection.
- AI output schemas.
- Review-required flags.
- Disallowed hiring prediction fields.
- Shared AI exception types.

### 7.2 Privacy and Safety Testing

Verify:

- Approved Resume profile context only.
- Private profile fields stay excluded.
- Job descriptions remain untrusted.
- Interview target role, question, and typed answer remain untrusted.
- Prompt-injection text cannot become trusted instructions.
- Generated content retains limitations/review requirements.

### 7.3 API Testing

Verify:

- JWT requirements.
- Invalid token behaviour.
- Request validation.
- Response structure.
- HTTP status codes.
- Provider seam behaviour.
- Controlled 503 errors.
- Privacy isolation.
- No client ownership override.

### 7.4 Frontend Testing

Verify:

- Resume Builder.
- Cover Letter Builder.
- Interview Preparation page.
- Loading states.
- Validation states.
- Provider-error states.
- Editable generated content.
- Review-required messaging.
- Responsive layout.
- Keyboard use.
- Browser compatibility.

### 7.5 Integration Testing

Integration testing verifies communication across:

```text
React
  |
  v
Django REST API
  |
  v
Sprint 3 Document / Interview Services
  |
  v
WBS 6.2 AI Prompt, Safety, and Provider Contracts
  |
  v
Future WBS 7.3 Concrete AI Provider
```

During Sprint 3, the provider boundary may remain fail-closed until WBS 7.3 unless an approved test provider or controlled test seam is used.

### 7.6 Regression Testing

Regression testing covers:

- Sprint 1 registration and login.
- JWT behaviour.
- Current-user retrieval.
- Student Profile load/update.
- Student ownership isolation.
- Sprint 2 Career Recommendations.
- Recommendation explanation.
- Skill Gap.
- Career Readiness.
- Learning Suggestions.
- Learning Roadmap.
- PostgreSQL connectivity.
- Django checks.
- Frontend lint/build.

## 8. Test Environment

| Component | Sprint 3 Environment |
| --- | --- |
| Frontend | React and Vite |
| Backend | Django and Django REST Framework |
| Authentication | JWT |
| Database | PostgreSQL |
| AI Contract Layer | WBS 6.2 `ai_services` |
| Resume Backend | WBS 6.3 `documents` |
| Interview Backend | WBS 6.6 `interviews` |
| API Testing | Django automated tests and manual API checks where required |
| Browser Testing | Current Chrome, Edge, and Firefox |
| Version Control | Git and GitHub |
| Integration Branch | `feature/sprint-3` |
| Evidence Folder | `docs/testing/evidence/sprint-3/` |

Secrets and passwords must not appear in test documentation, screenshots, committed files, or evidence.

## 9. Test Data Principles

Use safe development and testing data.

Test data should include:

- A valid Student account.
- A second Student account for privacy testing.
- A Student Profile with Skills, Education, Experience, Projects, and Career Goals.
- A Student Profile with minimal approved Resume context.
- A target role such as Software Developer.
- One valid job description for Cover Letter testing.
- A blank job description.
- An instruction-like job description for trust-boundary testing.
- Valid Interview question counts: 1, 5, and 10.
- Invalid Interview question counts: 0 and 11.
- A typed Interview answer.
- A blank typed Interview answer.
- Instruction-like Interview input for trust-boundary testing.
- Simulated provider unavailable and timeout conditions.
- Safe fake-provider responses for deterministic backend integration tests.

Do not use real passwords, private employment data, access tokens, or API secrets in committed evidence.

## 10. Current Test Execution Status

The Sprint 3 Test Case Tracker contains 100 cases.

At this checkpoint:

- Pass: 26.
- Fail: 0.
- Blocked: 59.
- Retest: 0.
- Not Run: 15.

The 26 recorded Pass cases cover verified WBS 6.2 AI contract/safety checks and WBS 6.6 Interview API component checks.

The 59 Blocked cases depend on WBS 6.4, WBS 6.5, WBS 6.7, WBS 6.6 merge completion, WBS 6.8, or later Sprint 3 integration readiness.

The 15 Not Run cases are integration-ready checks for the shared branch or WBS 6.3 team verification that have not yet been executed under this tracker.

A Blocked test is not a Failed test.

## 11. Entry Criteria

Before full WBS 6.8 execution:

- WBS 6.3 must be merged.
- WBS 6.4 must be merged.
- WBS 6.5 must be available.
- WBS 6.6 must be merged.
- WBS 6.7 must be available.
- Django checks must pass.
- Migration checks must pass.
- Backend automated tests must pass.
- Frontend lint must pass.
- Frontend production build must pass.
- PostgreSQL must be available.
- The tracker must be ready for result and evidence capture.

Before WBS 6.9 starts:

- WBS 6.8 core integration cases must pass.
- No unresolved Critical integration defect may block the main Sprint 3 flow.

## 12. WBS 6.2 AI Foundation Tests

Verify:

- Approved AI operation identifiers.
- Resume privacy mapping.
- Cover Letter prompt trust boundary.
- Interview prompt trust boundary.
- Strict input schemas.
- Strict output schemas.
- Draft/review requirements.
- Hiring prediction exclusion.
- Provider-independent contract.
- Shared exception hierarchy.
- Focused AI service tests.
- Backend regression.

Existing WBS 6.2 evidence is indexed in the workbook Evidence Index.

## 13. WBS 6.3 Resume Backend Tests

Verify:

- Authentication.
- Client ownership-field rejection.
- Authenticated Student Profile context.
- Privacy allowlist.
- WBS 6.2 Resume prompt reuse.
- Structured Resume draft response.
- Draft/review flags.
- Provider unavailable behaviour.
- Provider timeout behaviour.
- Focused and regression tests.

## 14. WBS 6.4 Cover Letter Backend Tests

After WBS 6.4 is available, verify:

- Authentication.
- Job description requirement.
- Blank job-description validation.
- Client ownership/prompt rejection.
- Student Profile ownership.
- Untrusted job-description handling.
- Tailoring without fabricated Student facts.
- Review-required output.
- Provider error behaviour.
- Focused and regression tests.

## 15. WBS 6.5 Document Interface Tests

After WBS 6.5 is available, verify:

- Protected Resume page.
- Resume API call.
- Editable Resume draft.
- Resume loading/error state.
- Job-specific Cover Letter input.
- Cover Letter API call.
- Editable Cover Letter draft.
- AI limitation/review state.
- Responsive layout.
- Accessibility and browser compatibility.

## 16. WBS 6.6 Interview API Tests

Verified component-level checks include:

- JWT authentication.
- Invalid JWT.
- Default question count.
- Question-count boundaries.
- Strict integer validation.
- Extra-field rejection.
- Client prompt rejection.
- Untrusted role and job-description content.
- Approved Interview Question operation/output model.
- Untrusted feedback input.
- Approved Interview Feedback operation/output model.
- Exclusion of hiring probability and pass/fail.
- Controlled provider failure.
- Focused and full backend regression.

Existing WBS 6.6 evidence is indexed in the workbook Evidence Index.

## 17. WBS 6.7 Interview Interface Tests

After WBS 6.7 is available, verify:

- Protected Interview page.
- Question generation request.
- Question rendering.
- Typed-answer input.
- Feedback request.
- Feedback rendering.
- AI limitation/review state.
- Loading/validation/provider-error state.
- Responsive layout.
- Keyboard and browser compatibility.

## 18. WBS 6.8 End-to-End Integration Tests

Run:

### Resume

```text
Login
  -> Resume Builder
  -> Generate Resume
  -> Review Draft
  -> Edit Draft
```

### Cover Letter

```text
Login
  -> Cover Letter Builder
  -> Enter Job Description
  -> Generate Cover Letter
  -> Review Draft
  -> Edit Draft
```

### Interview

```text
Login
  -> Interview Preparation
  -> Generate Questions
  -> Select Question
  -> Type Answer
  -> Generate Feedback
  -> Review Feedback
```

Execute privacy-sensitive flows with a second Student.

## 19. WBS 6.9 Regression Tests

Verify:

- Full backend regression.
- Django system check.
- Migration consistency.
- Frontend lint.
- Frontend production build.
- Sprint 1 authentication regression.
- Student Profile regression.
- Sprint 2 Career Analysis regression.
- Chrome compatibility.
- Edge compatibility.
- Firefox compatibility.
- Responsive layout.
- Accessibility basics.
- AI loading/timeout behaviour.
- Complete evidence and defect tracking.

## 20. Performance Tests

NFR-03 states:

- Normal non-AI API responses should complete within 2 seconds under expected classroom use.
- AI responses should show a loading state and use a configured timeout.

Record:

- Endpoint or action.
- Environment.
- Approximate response time.
- Whether the call uses AI.
- Loading-state behaviour.
- Timeout behaviour where available.

This is a classroom-use observation. It is not a production load test.

## 21. Security and Privacy Tests

Verify:

- Unauthenticated access is rejected.
- Invalid authentication is controlled.
- Cross-student profile-derived data is isolated.
- Client-supplied ownership identifiers are rejected.
- User-controlled text stays untrusted.
- Frontend source exposes no backend secrets.
- API errors expose no sensitive technical details.
- Existing Sprint 1 and Sprint 2 ownership controls remain working.

## 22. Ethical AI Tests

Verify:

- Resume and Cover Letter content is draft/review-required.
- Interview output contains no hiring probability.
- Interview output contains no pass/fail hiring classification.
- Limitations are preserved where required.
- Unsafe or unsupported provider output fails validation.
- Provider unavailable behaviour fails closed.
- Prompt injection stays inside untrusted content.

## 23. Accessibility and Compatibility Tests

Check:

- Form labels.
- Keyboard access.
- Focus behaviour.
- Useful validation feedback.
- Readable contrast.
- Responsive desktop layout.
- Responsive tablet layout.
- Responsive mobile layout.
- Current Chrome.
- Current Edge.
- Current Firefox.

## 24. Automation Strategy

Automate:

- Schema validation.
- API authentication.
- Extra-field rejection.
- Prompt trust-boundary tests.
- Provider seam tests.
- Response-structure tests.
- Backend regression.
- Django checks.
- Frontend lint/build where scripts support automation.

Use manual or hybrid execution for:

- Visual layout.
- Editing generated content.
- Keyboard checks.
- Browser compatibility.
- Responsive layout.
- Selected end-to-end flows.
- Evidence review.

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

Store Sprint 3 evidence under:

```text
docs/testing/evidence/sprint-3/
```

Each executed case should record:

- Test ID.
- Actual result.
- Evidence ID or clear actual-result note.
- Defect reference for Fail.
- Retest evidence where applicable.

Do not capture:

- Real passwords.
- JWT tokens.
- Database credentials.
- AI provider keys.
- Private Student information not required by the test.

## 27. Defect Severity

| Severity | Meaning |
| --- | --- |
| Critical | Core Sprint 3 flow cannot complete, privacy/security breach, or serious data exposure |
| High | Major Sprint 3 function fails with no acceptable workaround |
| Medium | Function works partially or has a contained usability/integration defect |
| Low | Minor issue that does not block the planned demonstration flow |

Critical and High defects affecting the core flow block Sprint 3 exit unless the team documents and approves a safe exception.

## 28. Retest and Regression Rule

For every fixed defect:

1. Retest the failed case.
2. Record new evidence.
3. Update the defect reference.
4. Run affected nearby regression cases.
5. Change status to Pass only after verification.

## 29. Sprint 3 Exit Criteria

Sprint 3 testing is ready for completion when:

- WBS 6.8 integration passes.
- Core Resume flow passes.
- Core Cover Letter flow passes.
- Core Interview Question flow passes.
- Core Interview Feedback flow passes.
- No unresolved Critical or High defect blocks the planned Sprint 3 demonstration.
- Authentication and cross-student privacy tests pass.
- WBS 6.2 AI safety boundaries remain intact.
- Backend regression passes.
- Frontend lint and build pass.
- Browser/responsive/accessibility checks are recorded.
- Required evidence is indexed.
- Deferred issues are documented.
- The team agrees the Sprint 3 increment is ready for review and retrospective.

## 30. Current Plan Status

Prepared and ready for continued execution.

Current tracker snapshot:

```text
Total: 100
Pass: 26
Fail: 0
Blocked: 59
Not Run: 15
Retest: 0
```

WBS 6.8 remains Blocked until all official predecessors are available.

WBS 6.9 remains Blocked until WBS 6.8 integration passes.
