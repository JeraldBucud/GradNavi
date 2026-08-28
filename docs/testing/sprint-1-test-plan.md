# GradNavi Sprint 1 Test Plan

Status: Active Sprint 1 test plan. Authentication integration, Student Profile backend implementation, frontend Student Profile integration, security verification, PostgreSQL connectivity, migration verification, and core Sprint 1 integration testing have been completed. Remaining negative, ownership, validation, database relationship, and regression test cases are tracked as Not Run in the Sprint 1 Test Case Tracker.

## 1. Purpose

This document defines the testing plan for GradNavi Sprint 1.

The purpose of Sprint 1 testing is to verify that the foundation, authentication, Student Profile, frontend, backend, database, permissions, and integration work together as expected.

The Sprint 1 target is a working authenticated Student Profile flow.

This plan covers the full team testing scope.

Detailed implementation-specific tests may also exist within individual frontend and backend modules. This document provides the higher-level Sprint 1 testing structure and does not replace those module-specific tests.

## 2. Sprint 1 Testing Goal

Sprint 1 testing should provide evidence that a student can:

1. Register an account.
2. Log in with valid credentials.
3. Be rejected when invalid credentials are supplied.
4. Access authenticated Student functions using valid authentication.
5. Retrieve the current authenticated user.
6. Retrieve their own Student Profile.
7. Update their own Student Profile.
8. Receive validation errors for invalid profile data.
9. Be prevented from accessing another student's protected profile information.
10. Refresh authentication according to the implemented JWT design.
11. Log out according to the implemented authentication design.
12. Use the React interface with the Django REST API successfully.

Testing should also confirm that the backend stores and retrieves the required Sprint 1 data through PostgreSQL.

## 3. Testing Scope

Sprint 1 testing covers:

- Backend foundation.
- PostgreSQL connectivity.
- Authentication API.
- JWT authentication.
- Registration.
- Login.
- Logout.
- Token refresh.
- Password-reset behaviour where included in the Sprint 1 authentication implementation.
- Current-user retrieval.
- Student Profile API.
- Student Profile ownership.
- Student Profile validation.
- Student Profile persistence.
- Frontend authentication integration.
- Frontend Student Profile integration.
- API error handling.
- Permission enforcement.
- Integration between React and Django.
- Regression testing of completed Sprint 1 functionality.

Testing outside Sprint 1 functionality is not required by this plan.

## 4. Related Testing Documentation

Detailed authentication API testing has been prepared separately by the backend developer.

The backend authentication documentation is expected at:

    backend/docs/AUTH_API_TESTING.md

That document should remain the detailed reference for authentication request and response examples, JWT flows, password-reset testing, negative authentication cases, and backend authentication test execution.

This Sprint 1 Test Plan should reference those results rather than duplicate every authentication test case.

Other relevant design documents include:

- `docs/system-design/rest-api-design.md`
- `docs/system-design/security-architecture.md`
- `docs/system-design/student-profile-data-design.md`
- `docs/system-design/student-profile-api-model-mapping.md`
- `docs/system-design/sprint-1-integration-plan.md`
- `docs/testing/sprint-1-test-cases.xlsx`
- `docs/testing/evidence/sprint-1/`

The Sprint 1 Test Case Tracker records test ownership, execution status, actual results, testers, evidence IDs, blocked dependencies, and defect references.

Sprint 1 screenshots and supporting test evidence are stored under:

    docs/testing/evidence/sprint-1/

Detailed backend authentication testing remains documented separately under:

    backend/docs/AUTH_API_TESTING.md

## 5. Testing Levels

Sprint 1 uses several testing levels.

### 5.1 Unit Testing

Unit tests verify individual backend functions, models, serializers, validation rules, permissions, and other isolated application logic.

Backend unit tests should be automated where practical.

### 5.2 API Testing

API testing verifies REST endpoints independently from the React interface.

API tests should verify:

- Request structure.
- Response structure.
- HTTP status codes.
- Authentication requirements.
- Validation.
- Permissions.
- Error responses.
- Data persistence.

### 5.3 Permission Testing

Permission testing verifies that authenticated users only access functions and information permitted for their role and ownership.

This is especially important for Student Profile data.

### 5.4 Integration Testing

Integration testing verifies communication between:

    React
      |
      v
    Django REST API
      |
      v
    Django Application Logic
      |
      v
    PostgreSQL

Integration testing should focus on complete user flows rather than isolated components.

### 5.5 Manual Testing

Manual testing may be used to verify:

- Frontend behaviour.
- User flows.
- Form behaviour.
- Error presentation.
- Postman API flows.
- Integration behaviour that is difficult to verify through isolated automated tests.

Manual testing should complement automated testing rather than replace appropriate automated tests.

### 5.6 Regression Testing

Regression testing verifies that new Sprint 1 changes do not break previously working Sprint 1 functionality.

Regression checks should occur after significant integration changes and before the Sprint 1 review.

## 6. Test Environment

The Sprint 1 test environment should reflect the team's approved development stack.

Expected components include:

| Component | Sprint 1 Environment |
| --- | --- |
| Frontend | React |
| Backend | Django and Django REST Framework |
| Authentication | JWT |
| Database | PostgreSQL |
| API Testing | Automated backend tests and Postman where required |
| Version Control | Git and GitHub |

Exact local ports, environment variables, and frontend origins should follow the team's current development configuration.

Secrets and passwords must not be recorded in this test plan or committed to Git.

## 7. Test Data Principles

Test data should be created specifically for development and testing.

Testing should include:

- A valid Student account.
- A second Student account for ownership testing.
- Valid Student Profile data.
- Invalid Student Profile data.
- Valid and invalid login credentials.
- Valid JWT credentials.
- Expired or invalid JWT credentials where supported by the test environment.
- Shared Skill records where required.
- Shared Interest records where required.

Real student passwords or sensitive personal information should not be used as test data.

### 7.1 Current Sprint 1 Test Execution Status

Sprint 1 testing is in progress.

The current Sprint 1 Test Case Tracker contains 61 test cases.

At the current testing checkpoint:

- Pass: 25
- Blocked: 0
- Not Run: 36
- Fail: 0

Completed testing areas include:

- Frontend authentication integration.
- Frontend registration validation.
- Frontend login validation.
- Protected route behaviour.
- Authentication session behaviour.
- Authentication logout behaviour.
- Security verification.
- CORS verification.
- PostgreSQL connectivity.
- Django migration verification.
- Authentication regression testing.
- Student Profile authenticated retrieval.
- Student Profile update integration.
- Student Profile persistence after refresh.
- Student Profile edit persistence.
- Student Profile deletion persistence.
- Frontend Student Profile integration.
- Core end-to-end Sprint 1 happy-path regression.

Remaining Not Run cases include negative Student Profile validation, cross-student ownership checks, selected Skill and Interest validation cases, direct database relationship verification, and remaining detailed regression cases.

Detailed results and evidence IDs are maintained in:

    docs/testing/sprint-1-test-cases.xlsx

## 8. Authentication Test Area

Authentication testing should verify the implemented `/api/v1/auth/` endpoints.

The authentication backend has been implemented and merged.

Detailed backend authentication implementation testing remains maintained separately by the backend developer.

Frontend authentication integration testing has been completed for:

- Registration.
- Login.
- Invalid login handling.
- Current-user integration.
- JWT access-token refresh behaviour.
- Logout.
- Protected routing.
- Authentication session behaviour.

Frontend authentication results and evidence are recorded in the Sprint 1 Test Case Tracker and Evidence Index.

### 8.1 Registration

Verify:

- Valid registration succeeds.
- Required fields are enforced.
- Invalid input is rejected.
- Duplicate account data is handled according to the API contract.
- Password rules are enforced.
- Passwords are not returned in API responses.
- Registration uses the expected HTTP status code.

### 8.2 Login

Verify:

- Valid credentials succeed.
- Invalid credentials fail.
- Missing credentials fail.
- Successful login returns the expected authentication data.
- Authentication failures use the standard error structure.
- Sensitive authentication information is not exposed.

### 8.3 Current User

Verify:

    GET /api/v1/auth/me/

Test:

- Valid access token returns the authenticated user.
- Missing authentication is rejected.
- Invalid authentication is rejected.
- Expired authentication is handled according to the JWT implementation.
- The endpoint does not return another user's information.

### 8.4 Token Refresh

Verify:

- A valid refresh token produces the expected response.
- An invalid refresh token is rejected.
- An expired refresh token is rejected.
- A blacklisted or revoked refresh token is rejected where blacklisting is implemented.
- Refresh behaviour follows the shared REST API contract.

### 8.5 Logout

Verify:

- An authenticated user can complete the implemented logout flow.
- Required refresh-token information is validated.
- A token invalidated by logout cannot be reused where blacklisting is implemented.
- Invalid logout requests return controlled errors.

### 8.6 Password Reset

Where password-reset functionality is included in the merged Sprint 1 authentication implementation, verify:

- Password-reset requests accept approved account data.
- Invalid requests return controlled responses.
- Reset tokens follow the implemented security rules.
- Valid reset operations allow the user to authenticate with the new password.
- Old credentials no longer authenticate after a successful password change where expected.

Detailed password-reset cases should remain in the backend authentication testing documentation.

## 9. Student Profile API Test Area

Student Profile testing focuses on:

    GET /api/v1/profile/
    PATCH /api/v1/profile/

The Student Profile backend has been implemented and integrated with the React Student Profile interface.

Completed testing confirms authenticated profile retrieval, valid profile updates, frontend-to-backend communication, save behaviour, persistence after refresh, edit persistence, and deletion persistence.

Remaining Student Profile test cases focus on negative validation, unauthenticated access, ownership isolation, invalid references, and other detailed cases recorded as Not Run in the Sprint 1 Test Case Tracker.

## 10. Student Profile Retrieval Tests

### PROF-GET-01: Authenticated Student Retrieves Own Profile

Precondition:

- A Student account exists.
- The Student has an associated StudentProfile.
- Valid authentication is available.

Action:

    GET /api/v1/profile/

Expected result:

- Request succeeds.
- Correct Student Profile is returned.
- Response follows the approved API structure.
- Only data owned by the authenticated Student is returned.

Status:

Pass. Authenticated Student Profile retrieval was verified through GET /api/v1/profile/. Evidence: EV-027 and EV-028.

### PROF-GET-02: Profile Request Without Authentication

Action:

    GET /api/v1/profile/

without valid authentication.

Expected result:

- Request is rejected.
- Expected authentication status code is returned.
- Standard error structure is used.
- No protected Student Profile data is returned.

Status:

Not Run. The endpoint is implemented, but the unauthenticated profile request test has not yet been executed as a dedicated test case.

### PROF-GET-03: Profile Response Contains Approved Collections

Where related records exist, verify the profile response correctly represents approved Student Profile areas such as:

- Skills.
- Interests.
- Education.
- Experience.
- Projects.
- Career goals.
- Personality responses where implemented.

Expected result:

- Response structure matches the implemented Student Profile API contract.
- Related records belong to the authenticated Student Profile.

Status:

Pass. The implemented profile collections were returned and displayed through the Student Profile integration flow. Evidence: EV-028, EV-029, and EV-030.

## 11. Student Profile Update Tests

### PROF-PAT-01: Valid Partial Profile Update

Precondition:

- Authenticated Student.
- Existing StudentProfile.

Action:

Submit a valid partial profile update.

Expected result:

- Request succeeds.
- Submitted information is updated.
- Unsubmitted profile information is preserved.

Status:

Pass. A valid authenticated profile update was completed and persisted through the integrated React and Django flow. Evidence: EV-029.

### PROF-PAT-02: Invalid Profile Field Value

Action:

Submit profile data containing an invalid value.

Expected result:

- Request is rejected.
- Validation error is returned.
- Invalid data is not stored.

Status:

Not Run.

### PROF-PAT-03: Empty Partial Request

Action:

Submit an empty PATCH request.

Expected result:

- Behaviour follows the implemented serializer and REST API contract.
- No unintended profile information is removed.

Status:

Not Run.

### PROF-PAT-04: Attempt Ownership-Field Change

Action:

Attempt to modify server-controlled ownership information such as:

    user_id

Expected result:

- Ownership is not changed.
- The backend ignores or rejects unauthorised ownership changes according to the implemented serializer design.

Status:

Not Run.

### PROF-PAT-05: Profile Update Persists

Action:

1. Update valid Student Profile information.
2. Retrieve the Student Profile again.

Expected result:

- Updated values are returned.
- Changes persist in PostgreSQL.

Status:

Pass. Profile changes persisted after successful PATCH requests and subsequent profile retrieval. Evidence: EV-026, EV-028, EV-029, and EV-030.

## 12. Student Profile Ownership Tests

Ownership testing requires at least two Student accounts.

Example:

    Student A
        |
        v
    StudentProfile A

    Student B
        |
        v
    StudentProfile B

### OWN-01: Student A Reads Own Profile

Expected result:

- Student A can retrieve StudentProfile A.
- Student A does not receive Student B's protected profile data.

Status:

Not Run. The Student Profile backend and frontend integration are available, but this dedicated ownership test remains pending execution.

### OWN-02: Student B Reads Own Profile

Expected result:

- Student B can retrieve StudentProfile B.
- Student B does not receive Student A's protected profile data.

Status:

Not Run. The Student Profile backend and frontend integration are available, but this dedicated ownership test remains pending execution.

### OWN-03: Cross-Student Access Blocked

Attempt to access another Student's protected profile through any available client-controlled identifier or route.

Expected result:

- Access is rejected or the API does not expose cross-student profile selection.
- No protected profile information belonging to another Student is returned.

Status:

Not Run. The Student Profile backend and frontend integration are available, but this dedicated ownership test remains pending execution.

### OWN-04: Cross-Student Ownership Modification Blocked

Attempt to submit another Student's identifier as part of a profile update.

Expected result:

- The backend does not transfer Student Profile ownership.
- Student A cannot cause profile information to become owned by Student B through client input.

Status:

Not Run. The Student Profile backend and frontend integration are available, but this dedicated ownership test remains pending execution.

## 13. Skill Validation Tests

The approved Student Skill proficiency values are:

- Foundational.
- Developing.
- Proficient.
- Advanced.

Testing must confirm that approved proficiency values are accepted and values outside the approved set are rejected.

### SKILL-01: Add Valid Student Skill

Expected result:

- Valid Skill reference is accepted.
- Approved proficiency value is accepted.
- StudentSkill belongs to the authenticated StudentProfile.

### SKILL-02: Reject Invalid Skill Reference

Expected result:

- Invalid Skill reference is rejected.
- Invalid StudentSkill data is not stored.

### SKILL-03: Reject Invalid Proficiency Level

Expected result:

- Values outside the approved proficiency set are rejected.
- Invalid proficiency information is not stored.

### SKILL-04: Prevent Duplicate Student Skill

Expected result:

- Duplicate StudentSkill relationships are prevented according to the implemented data rules.

SKILL-01 has been verified through the WBS 4.8 integration flow using the prepared Python Skill reference and an approved proficiency value. Evidence: EV-028.

SKILL-02, SKILL-03, and SKILL-04 remain Not Run and require dedicated negative or duplicate validation testing.

## 14. Interest Validation Tests

StudentInterest behaviour is implemented. Testing should verify:

- Valid Interest references are accepted.
- Invalid Interest references are rejected.
- Duplicate StudentInterest relationships are prevented where required.
- StudentInterest records belong to the authenticated StudentProfile.
- Student Profile operations do not provide unintended permission to modify shared Interest reference data.

INT-01 has passed through WBS 4.8 integration testing. INT-02 and INT-03 remain Not Run.

## 15. Education Tests

Education behaviour is implemented. Testing should verify:

- Valid Education records are accepted.
- Required fields are enforced.
- Invalid dates are rejected.
- Logical date rules are enforced.
- Education records belong to the authenticated StudentProfile.
- Updates do not modify another Student's Education records.
- Deletion behaviour follows the final API contract.

EDU-01 has passed through the WBS 4.8 persistence and edit flow. EDU-02 remains Not Run.

## 16. Experience Tests

Experience behaviour is implemented. Testing should verify:

- Valid Experience records are accepted.
- Required fields are enforced.
- Start and end dates follow approved validation rules.
- Current experience is handled consistently with `is_current`.
- Experience records belong to the authenticated StudentProfile.
- Another Student's Experience records cannot be modified.

EXP-01 has passed through the WBS 4.8 profile flow. EXP-02 remains Not Run because the available evidence does not verify current-role date validation.

## 17. Project Tests

Project behaviour is implemented. Testing should verify:

- Valid Project records are accepted.
- Invalid project URLs are rejected where URL validation applies.
- Required fields are enforced.
- Project dates follow approved validation rules.
- Projects belong to the authenticated StudentProfile.
- Another Student's Project records cannot be modified.

PROJ-01 has passed through the WBS 4.8 profile flow, including persisted deletion. PROJ-02 remains Not Run.

## 18. Career Goal Tests

CareerGoal behaviour is implemented. Testing should verify:

- Valid career goals are accepted.
- Required fields are enforced.
- CareerGoal records belong to the authenticated StudentProfile.
- Another Student's CareerGoal records cannot be modified.

GOAL-01 remains Not Run because the available WBS 4.8 screenshots do not clearly prove a persisted Career Goal record.

## 19. Personality Response Tests

The Sprint 1 personality questionnaire interface and response structure are available.

Testing should verify:

- Approved question identifiers are accepted.
- Approved response values are accepted.
- Invalid response values are rejected where restrictions exist.
- Responses belong to the authenticated StudentProfile.
- Another Student's responses cannot be retrieved or modified through Student operations.

PERS-01 remains Not Run because the available WBS 4.8 evidence does not clearly prove persisted Personality Response values.

## 20. API Error Response Tests

Sprint 1 APIs should follow the standard error-response structure defined by the REST API Design.

Testing should verify appropriate use of:

| HTTP Status | Test Meaning |
| --- | --- |
| `400 Bad Request` | Invalid request data |
| `401 Unauthorized` | Missing, invalid, or expired authentication |
| `403 Forbidden` | Authenticated user lacks required permission |
| `404 Not Found` | Requested resource does not exist |
| `409 Conflict` | Request conflicts with an existing resource where applicable |
| `500 Internal Server Error` | Unexpected backend failure |

Tests should verify both the status code and response structure.

## 21. Frontend Authentication Integration Tests

The React authentication interface is implemented and integrated with the Django authentication API.

### FE-AUTH-01: Frontend Registration Flow

Verify:

- Valid registration through the React interface.
- Backend registration response handling.
- Backend validation feedback.
- Weak-password validation.
- Password-confirmation validation.
- Duplicate-email handling.

Expected result:

- Valid registration succeeds.
- Successful backend response is handled correctly.
- Backend validation messages are displayed.
- Password mismatch is rejected before successful submission.
- Duplicate registration does not produce a false success state.

Execution status:

Pass.

### FE-AUTH-02: Frontend Login Flow

Verify:

- Valid login.
- Authenticated application state.
- Protected routing.
- Current-user retrieval.
- Return to requested route after authentication.
- Session behaviour after browser refresh.

Expected result:

- Valid login succeeds.
- Authenticated state is established.
- Protected Student functions become available.
- Current-user verification succeeds.
- A user redirected from a protected route returns to the requested route after successful login.
- Authentication state survives a normal browser refresh.

Execution status:

Pass.

### FE-AUTH-03: Frontend Invalid Login Error

Verify:

- Wrong password.
- Nonexistent account.
- Missing required login fields.

Expected result:

- Invalid login does not establish authenticated state.
- Controlled error feedback is displayed.
- Wrong-password and nonexistent-account responses do not reveal whether an account exists.
- Required-field validation prevents incomplete submission.

Execution status:

Pass.

### FE-AUTH-04: Frontend Token Refresh Behaviour

Verify:

- Expired access-token behaviour.
- Refresh-token request.
- Replacement access-token handling.
- Protected request retry.
- Failed refresh cleanup.

Expected result:

- Expired access token causes the protected request to return `401 Unauthorized`.
- Frontend submits the stored refresh token.
- Successful refresh stores replacement authentication information.
- Protected current-user request is retried.
- Authenticated Student stays on the protected route after successful refresh.
- Failed refresh clears authentication state and returns the user to Login.

Execution status:

Pass.

### FE-AUTH-05: Frontend Logout Flow

Verify:

- Logout request.
- Frontend authentication cleanup.
- Local authentication storage cleanup.
- Logged-out navigation.
- Protected route behaviour after logout.

Expected result:

- Logout completes the required backend request.
- Frontend authentication state is cleared.
- Stored access token, refresh token, and user information are removed.
- Logged-out navigation is displayed.
- Protected Student functions are no longer available after logout.

Execution status:

Pass.

Frontend authentication evidence is stored under:

    docs/testing/evidence/sprint-1/

Relevant evidence is recorded in the Sprint 1 Evidence Index.

## 22. Frontend Student Profile Integration Tests

The React Student Profile interface is integrated with the Django Student Profile API.

WBS 4.8 integration testing verified authenticated profile loading, successful profile updates, persistence after browser refresh, edit persistence, and deletion persistence.

### FE-PROF-01: Load Profile in UI

Expected result:

- Authenticated Student opens the Student Profile interface.
- Frontend requests `/api/v1/profile/`.
- Correct Student Profile information is displayed.

Status:

Pass. Evidence: EV-028.

### FE-PROF-02: Update Profile in UI

Expected result:

- Student edits approved profile information.
- Frontend submits the expected update request.
- Backend stores the change.
- Updated information appears in the interface.

Status:

Pass. Evidence: EV-026, EV-027, EV-029, and EV-030.

### FE-PROF-03: Display Profile Validation Error

Expected result:

- Invalid profile data is rejected.
- Frontend displays useful validation feedback.
- Invalid information is not presented as successfully saved.

Status:

Not Run. Dedicated invalid-profile frontend validation testing remains pending execution.

### FE-PROF-04: Profile Remains After Reload

Expected result:

- Successful profile updates persist.
- Reloading or refetching the profile returns the updated values.
- Persisted information appears again in the interface.

Status:

Pass. Evidence: EV-028, EV-029, and EV-030.

## 23. Database Verification

Database verification should confirm:

- Django connects to the intended PostgreSQL database.
- Required migrations apply successfully.
- User records persist.
- StudentProfile records persist.
- Related Student Profile records persist.
- Foreign-key relationships behave according to the approved model.
- Student ownership relationships are preserved.
- No frontend component connects directly to PostgreSQL.

DB-03 remains Not Run. The WBS 4.8 screenshots verify persistence through the application flow but do not provide direct database relationship inspection evidence.

### Current Database Test Status

- DB-01: Django connects to PostgreSQL - Pass.
- DB-02: Migrations apply successfully - Pass.
- DB-03: Profile relationships persist - Not Run.

Evidence for completed database checks is recorded in:

- EV-020.
- EV-021.

## 24. Security Verification

Sprint 1 security testing should verify at minimum:

- Protected endpoints require authentication.
- Invalid JWT credentials are rejected.
- Student ownership is enforced by the backend.
- Client-supplied identifiers do not bypass ownership.
- Passwords are not returned through APIs.
- Secrets are not exposed through frontend code.
- API errors do not expose stack traces or credentials to normal users.
- CORS configuration does not permit unnecessary development origins.
- Shared reference-data permissions follow the approved design.

Detailed security controls remain documented in the Security Architecture.

### Current Security Test Status

- SEC-01: Protected endpoint rejects missing JWT - Pass.
- SEC-02: API errors hide internal details - Pass.
- SEC-03: Frontend contains no backend secrets - Pass.
- SEC-04: CORS limited to approved origins - Pass.

Relevant evidence is recorded under:

- EV-016.
- EV-017.
- EV-018.
- EV-019.
- EV-022.
- EV-023.

## 25. Negative Testing

Negative testing should deliberately provide incorrect or unauthorised input.

Examples include:

- Invalid email format.
- Incorrect password.
- Missing required fields.
- Invalid JWT.
- Expired JWT.
- Invalid refresh token.
- Reused blacklisted refresh token where supported.
- Invalid Skill identifier.
- Invalid Interest identifier.
- Invalid date.
- Invalid URL.
- Invalid proficiency value.
- Attempted cross-student access.
- Attempted ownership modification.
- Malformed JSON where appropriate.

Expected failures should return controlled API responses rather than unexpected application errors.

## 26. Regression Test Checklist

### Current Regression Test Status

- REG-01: Authentication regression - Pass.
- REG-02: Student Profile regression - Not Run.
- REG-03: End-to-end Sprint 1 regression - Pass.

REG-03 passed through the core Sprint 1 happy-path flow covering registration, login, current-user retrieval, Student Profile GET, Student Profile PATCH, refresh persistence, and previously verified logout behaviour.

REG-02 remains Not Run because the full Student Profile regression set includes ownership, validation, and negative cases that have not all been executed.

Authentication regression evidence includes:

- EV-024.
- EV-025.

WBS 4.8 integration evidence supporting REG-03 includes:

- EV-027.
- EV-028.
- EV-030.

## 27. Test Evidence

Sprint 1 test evidence should be retained where practical.

Evidence may include:

- Automated test output.
- Test summary counts.
- Postman results.
- Screenshots of successful frontend flows.
- Screenshots of controlled error behaviour.
- Pull request checks.
- Relevant bug fixes linked to failed tests.

Evidence should identify what was tested and whether the test passed or failed.

Sensitive information should be removed from screenshots or other test evidence.

Sprint 1 test evidence is stored under:

    docs/testing/evidence/sprint-1/

The current Evidence Index contains:

    EV-001 through EV-030

WBS 4.8 Student Profile integration evidence includes:

- EV-026: Profile save success.
- EV-027: Authentication and profile API flow.
- EV-028: Profile persistence after refresh.
- EV-029: Profile edit persistence.
- EV-030: Profile deletion persistence.

Evidence IDs, descriptions, test mappings, file paths, testers, and execution dates are maintained in:

    docs/testing/sprint-1-test-cases.xlsx

Evidence should remain free from passwords, database credentials, JWT values, private keys, and other sensitive information.

## 28. Defect Handling

When a test fails because of an implementation defect:

1. Record the failing behaviour.
2. Identify the affected component.
3. Reproduce the failure where possible.
4. Assign or communicate the issue to the responsible team member.
5. Apply the fix through the normal Git branch and review workflow.
6. Rerun the failed test.
7. Run relevant regression tests.
8. Record the final result.

A failed test should not be marked as passed until the expected behaviour has been verified.

## 29. Sprint 1 Exit Criteria

Sprint 1 testing should be considered complete when:

- Required Sprint 1 functionality has been implemented.
- Authentication tests pass.
- Student Profile API tests pass.
- Ownership and permission tests pass.
- Required validation tests pass.
- React authentication integration works.
- React Student Profile integration works.
- PostgreSQL persistence is verified.
- Critical Sprint 1 defects are resolved.
- Relevant regression tests pass.
- Test evidence is available for Sprint review.
- Known incomplete or deferred functionality is documented.

## 30. Pending Test Areas

The Student Profile backend and frontend integration are implemented.

Remaining Sprint 1 testing focuses on test cases that have not yet received dedicated execution evidence.

Pending areas include:

1. Student Profile request without authentication.
2. Invalid Student Profile field validation.
3. Empty PATCH request behaviour.
4. Ownership-field modification protection.
5. Cross-student ownership and access isolation.
6. Invalid Skill reference validation.
7. Invalid Skill proficiency validation.
8. Duplicate Student Skill validation.
9. Invalid Interest reference validation.
10. Shared Interest permission testing.
11. Invalid Education date validation.
12. Current Experience date handling.
13. Invalid Project URL validation.
14. Career Goal persistence verification.
15. Personality Response persistence verification.
16. Direct PostgreSQL relationship inspection.
17. Full Student Profile regression testing.

These items are tracked as Not Run rather than Blocked because the required Student Profile implementation is now available.

## 31. Test Plan Maintenance

This test plan should be updated when:

- Sprint 1 API contracts change.
- Authentication behaviour changes.
- Student Profile models change.
- Frontend integration behaviour changes.
- New Sprint 1 defects reveal missing test coverage.
- Pending design decisions are resolved.

Test cases should stay aligned with the implemented system rather than preserving outdated expected behaviour.

## 32. Test Plan Status

This is a working Sprint 1 Test Plan.

The authentication backend, Student Profile backend, frontend authentication integration, and frontend Student Profile integration are implemented.

The current Sprint 1 Test Case Tracker records 61 test cases:

- Pass: 25
- Fail: 0
- Blocked: 0
- Not Run: 36

WBS 4.8 has verified the core authenticated Student Profile integration flow, including profile loading, successful profile updates, persistence after refresh, edit persistence, and deletion persistence.

Remaining Not Run cases focus on negative validation, ownership isolation, direct database relationship verification, and detailed regression coverage.

Test cases and this plan should continue to be updated as the remaining Sprint 1 tests are executed.