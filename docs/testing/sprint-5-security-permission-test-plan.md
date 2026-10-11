# GradNavi Sprint 5 Security and Permission Test Plan

Status: COMPLETE

WBS: 8.3 Security and Permission Testing

Owner: Jerald

Sprint: Sprint 5

Planned execution: 5 October to 6 October 2026

## 1. Purpose

This plan defines the WBS 8.3 security and permission verification for GradNavi.

Tests are derived from the approved GradNavi Security Architecture and current integrated implementation.

No test exists solely to increase the test count.

The plan verifies:

- Authentication.
- Authorization.
- Administrator permissions.
- Student data isolation.
- Object ownership.
- Input protection.
- Secret protection.
- AI privacy boundaries.
- Audit protection.
- Controlled errors.
- Frontend protected routing.
- Deployment-security readiness.

## 2. Source Baseline

Primary test-design source:

- `docs/system-design/security-architecture.md`

Relevant Security Architecture sections:

- 10 API Security
- 11 AI Service Security
- 12 Logging and Audit
- 13 Deployment and Communication Security
- 14 Security Testing and Review

Implementation sources:

- `backend/gradnavi/settings.py`
- `backend/accounts/views.py`
- `backend/accounts/serializers.py`
- `backend/accounts/tests.py`
- `backend/administration/permissions.py`
- `backend/administration/views.py`
- `backend/administration/serializers.py`
- `backend/administration/tests.py`
- `backend/profiles/views.py`
- `backend/profiles/tests.py`
- `backend/careers/views.py`
- `backend/careers/tests.py`
- `backend/documents/views.py`
- `backend/documents/tests.py`
- `backend/ai_services/safety/privacy.py`
- `backend/interviews/views.py`
- `backend/interviews/tests.py`
- `frontend/src/App.jsx`
- `frontend/src/components/auth/ProtectedRoute.jsx`
- `frontend/src/services/apiClient.js`
- `frontend/src/services/authStorage.js`

## 3. Test Status Definitions

`Not Run`

The approved test has not been executed.

`Pass`

Observed behaviour matches the approved security expectation.

`Fail`

Executed behaviour does not match the approved security expectation.

A Fail result requires a defect record.

`Blocked`

The required implementation dependency is not integrated.

`Deferred`

The test belongs to a later deployment or production stage and is not an executable WBS 8.3 local-environment test.

## 4. Current Entry State

WBS 8.1 Sprint 5 Planning is merged.

WBS 7.7 Admin Dashboard Interface is integrated into the current Sprint 5 baseline.

Backend Administrator models, APIs, permissions, analytics, role management, account-status management, audit records, and Administrator frontend routes are integrated.

S5-SEC-FE-01 was executed after WBS 7.7 integration and passed manual browser permission verification.

Deployment-specific security checks stay Deferred until the deployment and production-verification stages.

Final local execution status:

- Pass: 30
- Fail: 0
- Not Run: 0
- Blocked: 0
- Deferred: 2
- Confirmed WBS 8.3 security defects: 0

The tables below preserve the approved Initial status values as planning history. Final results are recorded in Section 20.

## 5. Authentication Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-AUTH-01 | Valid credentials authenticate and return JWT access and refresh tokens with safe user fields only | Automated | Not Run |
| S5-SEC-AUTH-02 | Wrong password and unknown email return the same safe authentication error | Automated | Not Run |
| S5-SEC-AUTH-03 | Protected APIs reject missing, malformed, invalid, or inappropriate authentication tokens | Automated | Not Run |
| S5-SEC-AUTH-04 | Refresh-token rotation works and the previous refresh token is rejected after rotation | Automated | Not Run |
| S5-SEC-AUTH-05 | Logout blacklists the submitted refresh token and follows the documented access-token expiry behaviour | Automated | Not Run |
| S5-SEC-AUTH-06 | Password reset and authenticated password change enforce approved validation without exposing account-sensitive information | Automated | Not Run |

## 6. Authorization and Administrator Permission Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-RBAC-01 | Unauthenticated requests receive 401 for Administrator endpoints | Automated | Not Run |
| S5-SEC-RBAC-02 | Student accounts receive 403 for Administrator list and detail endpoints | Automated | Not Run |
| S5-SEC-RBAC-03 | Student accounts must not perform Administrator create, update, delete, role, status, report-review, analytics, or audit operations | Automated | Not Run |
| S5-SEC-RBAC-04 | General Administrator user editing must not modify role or active status through the general user endpoint | Automated | Not Run |
| S5-SEC-RBAC-05 | Role and active-status changes use dedicated Administrator-only endpoints and reject invalid role values | Automated | Not Run |
| S5-SEC-RBAC-06 | Audit and analytics endpoints are Administrator-only, audit records are read-only, and responses do not expose unnecessary Student information | Automated | Not Run |

## 7. Object Ownership and Student Isolation Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-OWN-01 | Student Profile GET resolves only the authenticated user's profile and does not expose another Student profile | Automated | Not Run |
| S5-SEC-OWN-02 | Student Profile PATCH rejects ownership spoofing through identifiers, nested records, query parameters, or protected fields | Automated | Not Run |
| S5-SEC-OWN-03 | Career Recommendation, Learning Resource, Roadmap, and related Student guidance operations derive Student context from the authenticated user | Automated | Not Run |
| S5-SEC-OWN-04 | Job Description Matching derives the Student Profile from request.user rather than a client-supplied profile identity | Automated | Not Run |
| S5-SEC-OWN-05 | Resume and Cover Letter generation use the authenticated user's profile and reject attempts to select another Student profile or supply protected prompt controls | Automated | Not Run |
| S5-SEC-OWN-06 | Interview History returns only the authenticated user's records and new history records bind ownership to request.user | Automated | Not Run |

## 8. Input and Server-Controlled Field Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-IN-01 | Client requests must not set protected role, ownership, system-prompt, profile-identity, or server-controlled values | Automated | Not Run |
| S5-SEC-IN-02 | Invalid values, invalid identifiers, invalid file content, invalid role values, and unsupported data produce controlled validation responses | Automated | Not Run |

## 9. AI Privacy and External Service Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-AI-01 | AI Student Profile context is restricted to the approved allowlist | Automated and static review | Not Run |
| S5-SEC-AI-02 | User IDs, StudentProfile IDs, email, role, passwords, JWT data, internal identifiers, personality responses, interests, project URLs, and database timestamps are excluded from AI profile context | Automated and static review | Not Run |
| S5-SEC-AI-03 | AI provider failures and invalid generated responses return controlled API errors without provider credentials or internal exception details | Automated | Not Run |
| S5-SEC-AI-04 | User-supplied content stays separate from backend-controlled AI instructions and AI output does not replace backend authorization or deterministic scoring | Automated and static review | Not Run |

## 10. Audit and Error Protection Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-AUD-01 | Administrator mutations create the required audit records for supported audited operations | Automated | Not Run |
| S5-SEC-AUD-02 | Audit responses are Administrator-only, read-only, and exclude unnecessary identity or credential information | Automated | Not Run |
| S5-SEC-AUD-03 | Error and audit handling must not expose passwords, JWT tokens, API keys, credentials, stack traces, internal paths, or unsafe metadata | Automated and static review | Not Run |

## 11. Secret and Configuration Protection Tests

| ID | Security expectation | Method | Initial status |
| --- | --- | --- | --- |
| S5-SEC-SECRET-01 | Repository tracking must not include real `.env` files, database passwords, AI API keys, JWT secrets, or other real credentials | Repository review | Not Run |
| S5-SEC-SECRET-02 | AI provider credentials and backend secrets must not appear in frontend source or browser-facing configuration | Repository review | Not Run |

## 12. Frontend Permission Test

| ID | Security expectation | Method | Initial status | Dependency |
| --- | --- | --- | --- | --- |
| S5-SEC-FE-01 | Administrator frontend routes reject unauthenticated and Student access while allowing the approved Administrator role | Manual and integration | Blocked | WBS 7.7 |

The Initial status above is preserved as planning history.

WBS 7.7 is now integrated. The current `frontend/src/App.jsx` contains the Administrator routes behind `ProtectedRoute` and `AdminRoute`.

Follow-up manual browser verification passed:

- Unauthenticated access to `/admin` and `/admin/users` redirected to `/login`.
- Authenticated Student access to Administrator routes redirected to `/profile`.
- Authenticated Administrator access to `/admin` and `/admin/users` succeeded.

No screenshot was retained. The manual verification result is recorded in the Sprint 5 security-permission test-case workbook.

## 13. Deployment Security Checks

| ID | Security expectation | Method | Initial status | Dependency |
| --- | --- | --- | --- | --- |
| S5-SEC-DEP-01 | Deployed Django configuration uses appropriate Debug, Allowed Hosts, CORS, environment-secret, HTTPS, and production error settings | Deployment review | Deferred | WBS 8.7, WBS 8.8, WBS 8.9 |
| S5-SEC-DEP-02 | Deployed frontend and backend expose no protected secrets and use approved production communication paths | Deployment review | Deferred | WBS 8.7, WBS 8.8, WBS 8.9 |

The current local settings remain development settings.

Deployment-specific configuration is not classified as a WBS 8.3 defect before deployment.

## 14. Test Count

Total WBS 8.3 test cases: 32

Initial status:

- Not Run: 29
- Pass: 0
- Fail: 0
- Blocked: 1
- Deferred: 2

Final status:

- Not Run: 0
- Pass: 30
- Fail: 0
- Blocked: 0
- Deferred: 2

## 15. Automated Test Reuse

Existing automated tests should be reused where they already prove an approved WBS 8.3 security expectation.

Relevant suites include:

- `accounts.tests`
- `profiles.tests`
- `careers.tests`
- `documents.tests`
- `interviews.tests`
- `administration.tests`

New automated tests should only be added where an approved Security Architecture expectation lacks adequate test coverage.

## 16. Defect Rule

A test result becomes Fail only after execution proves expected security behaviour is not met.

Every failed WBS 8.3 test requires:

- Defect ID.
- Test case ID.
- Severity.
- Priority.
- Expected result.
- Actual result.
- Evidence.
- Owner.
- Fix reference.
- Retest result.

An unfinished dependency is Blocked, not Fail.

A deployment-only security check is Deferred, not Fail.

## 17. Evidence Rule

Security evidence must not contain:

- Passwords.
- Access tokens.
- Refresh tokens.
- Password-reset credentials.
- AI API keys.
- Database credentials.
- Django secret values.
- Other real secrets.

Recommended evidence naming:

`S5-SEC-<AREA>-<NUMBER>-<result>`

Examples:

`S5-SEC-AUTH-01-pass`

`S5-SEC-RBAC-02-pass`

`S5-SEC-FE-01-pass`

## 18. Exit Conditions

WBS 8.3 local security and permission testing is ready for completion when:

- All executable WBS 8.3 tests have a recorded result.
- No unresolved Critical security defect remains.
- No unresolved High permission or Student-data-isolation defect remains for required project functionality.
- Failed tests have a defect reference.
- Fixed security defects have a recorded retest.
- Security evidence contains no real credentials.
- Blocked tests identify their dependency.
- Deferred deployment tests identify their later WBS owner or stage.

S5-SEC-FE-01 was executed after WBS 7.7 integration and passed.

S5-SEC-DEP-01 and S5-SEC-DEP-02 continue during deployment and production verification.

Final local exit-condition result: SATISFIED.

All 30 executable local WBS 8.3 cases have recorded Pass results. No Critical or High WBS 8.3 security defect remains unresolved. No failed case requires a defect reference. The two deferred deployment cases retain their approved later execution stages.

## 19. Current Audit Findings

Current integrated controls found during the pre-test audit:

- JWT authentication is configured.
- Refresh rotation and blacklisting are configured.
- Account Settings requires authentication.
- Password Change requires authentication and current-password verification.
- Profile-photo input validates size, type, extension, and actual image content.
- Administrator backend endpoints use the GradNavi Administrator permission.
- General user editing keeps role and active status server-controlled.
- Dedicated Administrator endpoints control role and account-status changes.
- Administrative audit endpoints are read-only.
- Student Profile access derives ownership from request.user.
- Job Description Matching derives profile context from request.user.
- Resume and Cover Letter generation derive profile context from request.user.
- AI document profile context uses an explicit privacy allowlist.
- Interview History derives ownership from request.user.
- Controlled external-service errors exist for AI-supported features.

Final blockers and deferred checks:

- No local WBS 8.3 case remains Blocked.
- S5-SEC-DEP-01 and S5-SEC-DEP-02 remain Deferred until deployment and production verification.

Final local execution findings:

- All 30 executable WBS 8.3 cases passed.
- S5-SEC-FE-01 passed after WBS 7.7 integration using manual browser verification.
- No WBS 8.3 security defect was confirmed.
- Backend and frontend repository secret reviews passed.
- AI privacy, trust-boundary, and controlled-failure reviews passed.
- Audit creation, audit access, read-only behaviour, and safe metadata handling passed.
- Temporary WBS 8.3 test users and temporary report data were cleaned up after evidence collection.
- The normal Student test account used by the project was preserved.

## 20. Final Execution Results

| Area | Cases | Final result |
| --- | --- | --- |
| Authentication | S5-SEC-AUTH-01 to S5-SEC-AUTH-06 | Pass |
| Authorization and Administrator Permission | S5-SEC-RBAC-01 to S5-SEC-RBAC-06 | Pass |
| Object Ownership and Student Isolation | S5-SEC-OWN-01 to S5-SEC-OWN-06 | Pass |
| Input and Server-Controlled Fields | S5-SEC-IN-01 to S5-SEC-IN-02 | Pass |
| AI Privacy and External Service | S5-SEC-AI-01 to S5-SEC-AI-04 | Pass |
| Audit and Error Protection | S5-SEC-AUD-01 to S5-SEC-AUD-03 | Pass |
| Secret and Configuration Protection | S5-SEC-SECRET-01 to S5-SEC-SECRET-02 | Pass |
| Frontend Permission | S5-SEC-FE-01 | Pass |
| Deployment Security | S5-SEC-DEP-01 to S5-SEC-DEP-02 | Deferred to WBS 8.7 to WBS 8.9 |

Final totals:

- Total: 32
- Pass: 30
- Fail: 0
- Not Run: 0
- Blocked: 0
- Deferred: 2

Confirmed WBS 8.3 security defects: 0

Final evidence records are maintained in:

- `sprint-5-security-permission-test-cases.xlsx`
- `wbs-8.3-security-evidence-screenshots-final.zip`
- `wbs-8.3-security-testing-final-package.zip`

The original Initial status values in Sections 5 to 13 remain unchanged to preserve the approved planning baseline.

S5-SEC-FE-01 follow-up evidence is recorded in `sprint-5-security-permission-test-cases.xlsx`. No screenshot was retained for the manual browser verification.
