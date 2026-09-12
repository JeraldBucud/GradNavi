# GradNavi WBS 6.6 Closeout Record

Status: Technical implementation and testing complete, pending Pull Request review and merge

WBS: 6.6 Interview Question and Feedback API

Sprint: Sprint 3 - Application Documents and Interview Preparation

Owner: Jerald

Branch: `jerald/wbs-6.6-interview-api`

Target integration branch: `feature/sprint-3`

## 1. Purpose

WBS 6.6 implements the authenticated backend API for GradNavi interview preparation.

The work provides two operations:

1. Interview question generation
2. Interview answer feedback

The implementation reuses the shared WBS 6.2 AI contracts, prompt builders, safety rules, provider contract, and exception hierarchy.

Direct external AI provider integration is intentionally excluded from WBS 6.6 and remains assigned to WBS 7.3.

## 2. Implemented API Endpoints

### Interview Question Generation

```text
POST /api/v1/interviews/questions/
```

Purpose:

Generate a structured set of interview-preparation questions for a supplied target role and optional job description.

Authentication:

JWT authentication required.

Accepted request fields:

- `target_role`
- `job_description`
- `question_count`

The request rejects undeclared fields such as:

- `user_id`
- `student_profile_id`
- `prompt`

### Interview Feedback Generation

```text
POST /api/v1/interviews/feedback/
```

Purpose:

Generate structured feedback for one typed Student interview answer.

Authentication:

JWT authentication required.

Accepted request fields:

- `target_role`
- `question`
- `student_answer`

The request rejects undeclared fields such as:

- `user_id`
- `student_profile_id`
- `prompt`

## 3. WBS 6.6 Application Structure

The WBS 6.6 implementation adds the `interviews` Django app and includes:

- API request serializers
- API response serializers
- Strict request-field validation
- Interview service layer
- Provider dependency seam
- Authenticated API views
- URL routing
- Automated WBS 6.6 tests

No interview database models were added under WBS 6.6.

No migration was required.

## 4. Request Validation

The REST API boundary mirrors the strict WBS 6.2 Pydantic contracts.

### Question Generation

Validated fields:

- `target_role`
- optional `job_description`
- `question_count`

Rules include:

- default question count: `5`
- minimum question count: `1`
- maximum question count: `10`
- string values remain strict strings
- question count remains a strict integer
- undeclared fields are rejected

### Interview Feedback

Validated fields:

- `target_role`
- `question`
- `student_answer`

Blank Student answers are rejected.

Undeclared request fields are rejected before the service layer executes.

## 5. Service Layer

The WBS 6.6 service layer contains:

```text
generate_interview_questions()
generate_interview_feedback()
```

The service layer delegates validation and prompt construction to the existing WBS 6.2 contracts.

### Interview Question Flow

```text
HTTP request
    |
    v
InterviewQuestionRequestSerializer
    |
    v
InterviewQuestionInput
    |
    v
build_interview_question_prompt()
    |
    v
AIProvider
    |
    v
InterviewQuestionSet
    |
    v
InterviewQuestionSetSerializer
    |
    v
HTTP response
```

### Interview Feedback Flow

```text
HTTP request
    |
    v
InterviewFeedbackRequestSerializer
    |
    v
InterviewFeedbackInput
    |
    v
build_interview_feedback_prompt()
    |
    v
AIProvider
    |
    v
InterviewFeedback
    |
    v
InterviewFeedbackSerializer
    |
    v
HTTP response
```

## 6. Trust Boundaries

WBS 6.6 preserves the WBS 6.2 trust model.

### Interview Question Generation

Trusted application context includes:

- validated `question_count`

Untrusted content includes:

- `target_role`
- optional `job_description`

### Interview Feedback

All interview-specific user text stays untrusted:

- `target_role`
- `question`
- `student_answer`

WBS 6.6 does not move user-controlled text into GradNavi-controlled prompt instructions.

## 7. Output Safety

Interview question responses use the existing `InterviewQuestionSet` contract.

Expected fields:

- `questions`
- `focus_areas`
- `limitations`
- `is_ai_generated`
- `requires_user_review`

Interview feedback responses use the existing `InterviewFeedback` contract.

Expected fields:

- `strengths`
- `improvements`
- `suggested_response`
- `feedback_summary`
- `limitations`
- `is_ai_generated`
- `requires_user_review`

The output contracts exclude:

- hiring probability
- pass or fail classifications
- guaranteed employment outcomes

## 8. Authentication

Both WBS 6.6 endpoints require authenticated access through the existing GradNavi JWT authentication configuration.

Unauthenticated requests return the existing GradNavi authentication error response.

Invalid JWT requests use the existing GradNavi token error response.

WBS 6.6 does not accept client-supplied ownership identifiers such as `user_id` or `student_profile_id`.

## 9. Provider Boundary

WBS 6.6 uses the shared provider-independent `AIProvider` contract.

The current interview provider seam fails closed by raising:

```text
AIProviderUnavailableError
```

This prevents production endpoints from returning fabricated AI responses before WBS 7.3 adds the concrete external provider.

Provider failures are translated to a controlled:

```text
503 Service Unavailable
```

response through the Interview API.

## 10. Automated Test Results

### 10.1 Focused WBS 6.6 Test Suite

Command:

```powershell
python manage.py test interviews -v 2
```

Result:

```text
Ran 38 tests in 8.985s

OK
```

Recorded failures: 0

Coverage includes:

- request serializer validation
- default question count
- question count minimum and maximum
- strict question count type validation
- extra-field rejection
- client prompt rejection
- blank Student answer rejection
- question service operation selection
- feedback service operation selection
- WBS 6.2 trusted and untrusted content separation
- expected output model delegation
- provider error propagation
- fail-closed provider seam
- JWT authentication
- invalid JWT handling
- API route resolution
- structured question response
- structured feedback response
- service delegation
- controlled 503 provider failure

### 10.2 Full Backend Regression

Command:

```powershell
python manage.py test -v 2
```

Result:

```text
Ran 343 tests in 144.082s

OK
```

Recorded failures: 0

The temporary PostgreSQL test database was destroyed after the successful regression run.

### 10.3 Django System Check

Command:

```powershell
python manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

## 11. Final Branch Verification

Verified branch:

```text
jerald/wbs-6.6-interview-api
```

Git status:

```text
nothing to commit, working tree clean
```

The branch was up to date with:

```text
origin/jerald/wbs-6.6-interview-api
```

## 12. WBS 6.6 Commits

WBS 6.6 implementation commits:

```text
6143a85 test: add WBS 6.6 interview API tests
6985053 feat: add WBS 6.6 interview API endpoints
c1c6599 fix: enforce strict WBS 6.6 interview request fields
87d5c6b feat: add WBS 6.6 interview service layer
273ffb0 feat: add WBS 6.6 interview API serializers
dc03e51 feat: add WBS 6.6 interview API foundation
```

The branch is based on Sprint 3 after the WBS 6.2 AI foundation and WBS 6.3 Resume Generation Backend were merged.

## 13. Evidence Files

Recommended repository location:

```text
docs/testing/evidence/sprint-3/
```

Evidence files:

```text
S3-EV-002A-wbs-6.6-focused-test-suite-count.png
S3-EV-002B-wbs-6.6-focused-test-suite-pass.png
S3-EV-002C-wbs-6.6-full-backend-regression-count.png
S3-EV-002D-wbs-6.6-full-backend-regression-pass.png
S3-EV-002E-wbs-6.6-django-check-branch-status-commits.png
```

## 14. Integration Handover

WBS 6.6 provides the backend API required for the Sprint 3 interview-preparation feature.

WBS 6.8 Document and Interview Integration should consume these endpoints after all required Sprint 3 predecessors are complete.

The API contract for integration is:

```text
POST /api/v1/interviews/questions/
POST /api/v1/interviews/feedback/
```

WBS 7.3 should later replace the fail-closed provider seam with the approved concrete AI provider implementation.

WBS 7.4 should continue the planned provider-specific error handling, retry, timeout, and response-validation work.

## 15. Remaining Closeout Actions

Technical implementation and testing are complete.

Project-management actions still required:

1. Add the five WBS 6.6 Sprint 3 evidence images.
2. Add this closeout record.
3. Commit and push the closeout evidence.
4. Open a Pull Request from `jerald/wbs-6.6-interview-api` into `feature/sprint-3`.
5. Request team review.
6. Address valid review findings.
7. Merge the Pull Request after approval.
8. Mark WBS 6.6 formally complete after merge.

## 16. Closeout Decision

Technical implementation:

`COMPLETE`

Focused WBS 6.6 tests:

`38 / 38 PASS`

Full backend regression:

`343 / 343 PASS`

Django system check:

`PASS`

Working tree:

`CLEAN`

Team review:

`PENDING`

PR merge:

`PENDING`

Formal WBS 6.6 status:

`PENDING TEAM REVIEW AND MERGE`
