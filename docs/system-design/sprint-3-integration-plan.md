# GradNavi Sprint 3 Integration Plan

Status: Prepared for WBS 6.8 Document and Interview Integration. WBS 6.2 and WBS 6.3 are merged into `feature/sprint-3`. WBS 6.6 is technically complete on PR #38 but is not treated as integrated until merged. Cases depending on WBS 6.4, WBS 6.5, WBS 6.7, or the final WBS 6.6 merge remain Blocked until those components are available.

## 1. Purpose

This document defines the GradNavi Sprint 3 integration approach.

Sprint 3 focuses on AI-assisted application documents and interview preparation. The integrated increment connects the shared AI prompt and safety foundation, Resume Generation Backend, Cover Letter Generation Backend, Resume and Cover Letter Interface, Interview Question and Feedback API, and Interview Preparation Interface.

This plan prepares the team for WBS 6.8. It does not mark WBS 6.8 complete before all required predecessors are available.

Detailed execution status is maintained in:

```text
docs/testing/sprint-3-test-cases.xlsx
```

## 2. WBS Alignment

| WBS | Task | Official Owner | Predecessors |
| --- | --- | --- | --- |
| 6.1 | Sprint 3 Planning | All Members | 5.11 |
| 6.2 | AI Prompt Templates and Safety Rules | Jerald | 6.1, 2.7 |
| 6.3 | Resume Generation Backend | MD | 6.2 |
| 6.4 | Cover Letter Generation Backend | MD | 6.2 |
| 6.5 | Resume and Cover Letter Interface | Joyee | 6.1, 3.8 |
| 6.6 | Interview Question and Feedback API | Jerald | 6.2 |
| 6.7 | Interview Preparation Interface | Joyee | 6.5 |
| 6.8 | Document and Interview Integration | All Members | 6.3, 6.4, 6.5, 6.6, 6.7 |
| 6.9 | Sprint 3 Testing | All Members | 6.8 |
| 6.10 | Sprint 3 Review and Retrospective | All Members | 6.9 |
| 6.11 | Sprint 3 Complete | All Members | 6.10 |

The approved WBS places Sprint 3 from 7 September to 18 September 2026.

## 3. Integration Goal

Sprint 3 integration should prove two coherent Student preparation flows.

### 3.1 Application Document Flow

```text
Authenticated Student
        |
        v
Student Profile
        |
        +----------------------+
        |                      |
        v                      v
Resume Builder          Cover Letter Builder
        |                      |
        v                      v
Resume API             Job Description Input
        |                      |
        |                      v
        |               Cover Letter API
        |                      |
        +----------+-----------+
                   |
                   v
          Editable AI Draft
                   |
                   v
             Student Review
```

### 3.2 Interview Preparation Flow

```text
Authenticated Student
        |
        v
Interview Preparation Interface
        |
        v
Target Role + Optional Job Description
        |
        v
Interview Question API
        |
        v
Generated Question Set
        |
        v
Typed Student Answer
        |
        v
Interview Feedback API
        |
        v
Structured Feedback
        |
        v
Student Review
```

Generated AI content must remain advisory, reviewable, and subject to the safety boundaries established by WBS 6.2.

## 4. Requirements Covered

Sprint 3 integration directly supports:

- FR-08 Resume Builder.
- FR-09 Cover-Letter Builder.
- FR-10 Interview Preparation.
- FR-16 AI Content Review.
- FR-18 Audit and Error Handling where Sprint 3 service failures are involved.

Important quality requirements include:

- NFR-01 Usability.
- NFR-02 Responsive Design.
- NFR-03 Performance and AI loading/timeout behaviour.
- NFR-05 Security.
- NFR-06 Privacy.
- NFR-07 Maintainability.
- NFR-10 Accessibility.
- NFR-11 Compatibility.
- NFR-12 Testability.
- NFR-13 Separation of frontend, backend, database, and AI service layers.
- NFR-14 Ethical AI.

## 5. Current Repository Baseline

Repository and PR review at the preparation checkpoint confirms:

- WBS 6.2 shared AI prompt templates, privacy boundaries, safety rules, provider contract, schemas, and exception hierarchy are merged.
- WBS 6.3 Resume Generation Backend is merged into `feature/sprint-3`.
- WBS 6.6 Interview Question and Feedback API is technically complete on branch `jerald/wbs-6.6-interview-api`.
- PR #38 targets `feature/sprint-3` and is open at this checkpoint.
- WBS 6.6 focused testing recorded 38 passing tests.
- WBS 6.6 full backend regression recorded 343 passing tests.
- WBS 6.4 Cover Letter Generation Backend is not yet treated as integrated.
- WBS 6.5 Resume and Cover Letter Interface is not yet treated as integrated.
- WBS 6.7 Interview Preparation Interface is not yet treated as integrated.

A missing integration dependency is recorded as Blocked in the Sprint 3 Test Case Tracker. A blocked case is not a failed test.

## 6. Integration Branch Strategy

Integration target:

```text
feature/sprint-3
```

Rules:

1. Merge each WBS implementation through a reviewed pull request.
2. Update the local `feature/sprint-3` branch before integration testing.
3. Do not use uncommitted local files as the integration method.
4. Keep producer and consumer API contracts stable before dependent integration.
5. Record integration defects and retests in the Sprint 3 Test Case Tracker.
6. Use GitHub history, pull requests, test output, and screenshots as integration evidence.
7. Do not rewrite shared branch history.
8. A component-level Pass does not equal a WBS 6.8 integration Pass.
9. Do not start full WBS 6.8 execution until all official predecessors are available.

## 7. Integration Entry Criteria

Full WBS 6.8 execution starts when:

- WBS 6.3 is merged.
- WBS 6.4 is merged.
- WBS 6.5 is available on the shared Sprint 3 branch.
- WBS 6.6 is merged.
- WBS 6.7 is available on the shared Sprint 3 branch.
- Django system checks pass.
- Required migrations apply successfully.
- Backend automated tests pass.
- Frontend lint passes.
- Frontend production build passes.
- PostgreSQL connectivity is available.
- Safe Student test accounts and test data are available.
- No unresolved merge conflict exists.
- Secrets stay outside Git and test evidence.

If a prerequisite is missing, affected test cases stay Blocked.

## 8. Integration Sequence

### 8.1 Baseline Verification

1. Fetch the latest remote changes.
2. Check out `feature/sprint-3`.
3. Pull the latest integration branch.
4. Confirm a clean working tree.
5. Verify expected WBS merge commits.
6. Run Django system checks.
7. Check migration consistency.
8. Run backend regression tests.
9. Run frontend lint.
10. Run the frontend production build.
11. Confirm PostgreSQL connectivity.

### 8.2 WBS 6.2 AI Foundation Verification

Verify:

- Approved AI operation identifiers are available.
- Resume, cover letter, interview question, and interview feedback schemas remain strict.
- Private Student Profile fields are excluded from approved AI context.
- User-controlled descriptions, job descriptions, role text, questions, and answers remain untrusted.
- Resume and cover-letter outputs remain draft/review-required content.
- Interview outputs do not include hiring probability or pass/fail decisions.
- Provider-independent `AIProvider` boundaries remain intact.
- Shared AI exceptions remain available for downstream error handling.

### 8.3 WBS 6.3 Resume Generation Backend

Verify:

- JWT authentication is required.
- Client-supplied ownership identifiers are rejected.
- The authenticated Student Profile supplies approved Resume context.
- Private fields do not leak into the provider prompt.
- The service reuses the WBS 6.2 Resume prompt builder.
- Structured `ResumeDraft` output serializes correctly.
- Generated Resume content remains editable/review-required.
- Unconfigured or unavailable providers fail closed.
- Provider errors do not expose stack traces or secrets.

### 8.4 WBS 6.4 Cover Letter Generation Backend

After WBS 6.4 is merged, verify:

- JWT authentication is required.
- One selected job description supplies role-specific Cover Letter context.
- Blank or invalid job descriptions are rejected.
- Job description text remains untrusted content.
- Client-supplied ownership identifiers and prompt overrides are rejected.
- Authenticated Student Profile facts are used without cross-student leakage.
- The Cover Letter draft is tailored to the selected role without inventing Student facts.
- Generated output remains draft/review-required.
- Provider unavailable and timeout behaviour is controlled.

### 8.5 WBS 6.5 Resume and Cover Letter Interface

After WBS 6.5 is available, verify:

- Protected document pages load for authenticated Students.
- Resume generation calls the approved Resume endpoint.
- Cover Letter generation requires specific job context.
- Cover Letter generation calls the approved Cover Letter endpoint.
- Generated Resume content is editable before save/export actions.
- Generated Cover Letter content is editable before save/export actions.
- AI-generated and review-required state is clear.
- Loading, validation, empty, and provider-error states are useful.
- Layout works at desktop, tablet, and mobile widths.
- Keyboard access, labels, validation feedback, and current-browser compatibility are acceptable.

### 8.6 WBS 6.6 Interview Question and Feedback API

After PR #38 is merged, verify:

- Both Interview endpoints require JWT authentication.
- Invalid JWT requests are rejected.
- Question count defaults to 5 and accepts only integers from 1 to 10.
- Unexpected ownership or prompt fields are rejected.
- Target role and optional job description stay untrusted.
- Typed Student answers stay untrusted.
- Question generation uses the approved WBS 6.2 operation and output contract.
- Feedback generation uses the approved WBS 6.2 operation and output contract.
- Hiring probability and pass/fail outputs remain excluded.
- Provider unavailable and timeout errors return controlled 503 responses.

### 8.7 WBS 6.7 Interview Preparation Interface

After WBS 6.7 is available, verify:

- Protected Interview Preparation page loads.
- Question generation sends approved request fields only.
- Generated questions render in API order.
- A Student is able to type an answer for a selected question.
- Feedback requests use the selected question and typed answer.
- Strengths, improvements, summary, suggested response, and limitations render clearly.
- AI-generated and review-required state is visible.
- Loading, validation, and provider-error states are controlled.
- Responsive, keyboard, and browser checks pass.

### 8.8 Full WBS 6.8 Flow

Run these integrated journeys.

#### Resume Journey

```text
Login
  -> Student Profile available
  -> Resume Builder
  -> Generate Resume
  -> Review structured draft
  -> Edit draft
```

#### Cover Letter Journey

```text
Login
  -> Student Profile available
  -> Cover Letter Builder
  -> Enter one job description
  -> Generate Cover Letter
  -> Review tailored draft
  -> Edit draft
```

#### Interview Journey

```text
Login
  -> Interview Preparation
  -> Enter target role / optional job description
  -> Generate questions
  -> Select question
  -> Type answer
  -> Generate feedback
  -> Review feedback
```

Repeat privacy-sensitive flows with a second Student account.

## 9. Integration Contract Matrix

| Handoff | Producer | Consumer | Minimum Contract to Verify |
| --- | --- | --- | --- |
| Student Profile to Resume Service | Student Profile / WBS 6.2 privacy mapper | WBS 6.3 | Approved Resume context only |
| Resume Service to Resume API | WBS 6.3 service | WBS 6.5 | Structured `ResumeDraft` |
| Resume API to Resume UI | WBS 6.3 | WBS 6.5 | Authenticated response and controlled errors |
| Student Profile + Job Description to Cover Letter Service | Student Profile / request boundary | WBS 6.4 | Approved profile facts plus untrusted job description |
| Cover Letter API to Cover Letter UI | WBS 6.4 | WBS 6.5 | Structured editable draft |
| Interview Question Request to Prompt Builder | WBS 6.6 request serializer | WBS 6.2 prompt layer | Role, optional job description, question count |
| Interview Question API to Interview UI | WBS 6.6 | WBS 6.7 | Questions, focus areas, limitations, AI/review flags |
| Interview Feedback Request to Prompt Builder | WBS 6.6 request serializer | WBS 6.2 prompt layer | Role, question, typed answer |
| Interview Feedback API to Interview UI | WBS 6.6 | WBS 6.7 | Strengths, improvements, suggested response, summary, limitations, AI/review flags |
| Shared Provider Seam to Future AI Integration | WBS 6.2 / Sprint 3 services | WBS 7.3 | Provider-independent `AIProvider` contract |

Producer contract changes must be communicated to the consumer owner before integration.

## 10. Database and Persistence Checks

Verify:

- Sprint 3 changes do not corrupt existing Student Profile data.
- No unintended migrations are generated.
- Required migrations apply in a disposable/local test environment.
- Student ownership relationships remain valid.
- Shared reference data from Sprint 2 remains unchanged by Sprint 3 document/interview operations.
- Generated-content persistence is only tested where the implemented Sprint 3 scope provides persistence.
- Read-only generation checks do not modify unrelated Student or reference records.

## 11. Security and Privacy Checks

Verify:

- Protected document and Interview endpoints reject unauthenticated requests.
- Invalid or expired JWTs are controlled.
- Client-supplied `user_id` or `student_profile_id` values do not override authenticated ownership.
- One Student does not receive another Student's protected profile facts.
- User-controlled job descriptions, role text, interview questions, and typed answers remain untrusted.
- Frontend source does not expose backend credentials, JWT signing secrets, database credentials, or AI keys.
- API errors do not expose server paths, stack traces, SQL, secrets, or credentials.

## 12. AI Safety and Ethical Checks

Verify:

- Resume and Cover Letter content is presented as draft content.
- Generated content requires Student review before use.
- Interview output excludes hiring probability.
- Interview output excludes pass/fail hiring decisions.
- Generated output includes limitations where the approved schema requires them.
- Provider failures fail closed rather than returning fabricated production responses.
- User-controlled prompt-injection text cannot become GradNavi system instructions.

## 13. Error and Empty-State Integration

Test:

- Missing authentication.
- Invalid or expired authentication.
- Blank job description.
- Invalid question count.
- Blank typed Interview answer.
- Unexpected request fields.
- Provider unavailable.
- Provider timeout.
- Provider response validation failure when available.
- Frontend loading state.
- Frontend API-error state.
- Empty or missing generated-content state.
- Navigation away from a partially completed flow.

A controlled validation, empty, or unavailable-provider state is not a failed integration if the expected controlled behaviour is verified.

## 14. Performance, Reliability, and User Experience

- Normal non-AI API responses target 2 seconds under expected classroom use.
- AI operations should show a loading state.
- AI operations should use configured timeout/error handling once provider integration is available.
- Repeated structured request validation should remain consistent.
- Generated content should remain readable and editable.
- Core pages should work on current desktop, tablet, and mobile widths.
- Current Chrome, Edge, and Firefox should support the planned flow.

## 15. Defect Process

For each failed test, record:

- Test ID.
- WBS.
- Actual result.
- Defect reference.
- Likely component owner.
- Fix branch or pull request.
- Retest result.
- Affected regression result.
- Evidence ID.

Do not change Fail to Pass until a retest verifies the fix.

## 16. Rollback and Recovery

If a merge breaks `feature/sprint-3`:

1. Stop dependent merges.
2. Identify the regression source.
3. Preserve relevant logs and test results.
4. Prefer a corrective pull request for a contained fix.
5. Revert only with team agreement when correction is not the safer option.
6. Rerun affected focused and regression tests.
7. Update the Sprint 3 Test Case Tracker.
8. Notify the team of the blocker and recovery status.

## 17. Team Responsibilities

### Jerald

- WBS 6.2 regression and safety-boundary support.
- WBS 6.6 Interview API verification.
- Shared WBS 6.8 integration support.
- Sprint 3 evidence and tracker coordination.
- Backend regression support.

### MD

- WBS 6.3 Resume Backend verification.
- WBS 6.4 Cover Letter Backend verification.
- Backend and API defect support.
- Migration and backend integration support.

### Joyee

- WBS 6.5 document interface verification.
- WBS 6.7 Interview interface verification.
- Responsive, accessibility, and browser-compatibility checks.
- Frontend defect support.

### All Members

- WBS 6.8 end-to-end integration.
- WBS 6.9 Sprint 3 testing.
- Defect triage.
- Regression testing.
- Sprint 3 exit review.

## 18. Evidence Management

Store Sprint 3 evidence under:

```text
docs/testing/evidence/sprint-3/
```

Evidence may include:

- Automated test output.
- Sanitised terminal output.
- Screenshots.
- API responses with secrets removed.
- Browser compatibility checks.
- GitHub pull request and merge checks.
- Defect and retest results.
- End-to-end flow evidence.

Record evidence IDs in:

```text
docs/testing/sprint-3-test-cases.xlsx
```

## 19. Integration Exit Criteria

WBS 6.8 is ready for completion when:

- WBS 6.3, 6.4, 6.5, 6.6, and 6.7 are integrated.
- Resume UI-to-API flow passes.
- Cover Letter UI-to-API flow passes.
- Interview Question UI-to-API flow passes.
- Interview Feedback UI-to-API flow passes.
- Authentication and cross-student privacy checks pass.
- WBS 6.2 trust boundaries remain intact.
- Generated-content review requirements are visible.
- No unresolved Critical or High defect blocks the core flow.
- Required integration evidence is recorded.
- The team agrees the integrated Sprint 3 increment is ready for WBS 6.9 testing.

## 20. Repository Verification Basis

This plan is aligned against:

- `docs/project-management/work-breakdown-structure.md`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`
- `docs/system-design/rest-api-design.md`
- WBS 6.2 shared `backend/ai_services/` contracts and tests
- WBS 6.3 `backend/documents/` Resume backend
- WBS 6.6 `backend/interviews/` implementation and PR #38
- `docs/testing/evidence/sprint-3/`

## 21. Current Plan Status

Prepared for WBS 6.8.

Current integration gate:

- WBS 6.2: merged and verified.
- WBS 6.3: merged.
- WBS 6.4: not yet integrated at this checkpoint.
- WBS 6.5: not yet integrated at this checkpoint.
- WBS 6.6: technically complete, PR #38 open.
- WBS 6.7: not yet integrated at this checkpoint.
- WBS 6.8: Blocked.
- WBS 6.9: Blocked until WBS 6.8 passes.
