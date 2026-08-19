# GradNavi Sprint 1 Test Plan

Status: Working test plan, pending frontend and Student Profile backend implementation updates

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

## 8. Authentication Test Area

Authentication testing should verify the implemented `/api/v1/auth/` endpoints.

The backend developer has reported implementation of seven authentication endpoints with automated and manual testing.

Final test evidence should be taken from the reviewed and merged backend implementation rather than relying only on the reported development status.

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

Student Profile testing should focus on:

    GET /api/v1/profile/
    PATCH /api/v1/profile/

The exact related-resource behaviour should be updated once the Student Profile backend implementation is confirmed.

## 10. Student Profile Retrieval Tests

### SP-GET-01: Authenticated Profile Retrieval

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

### SP-GET-02: Missing Authentication

Action:

    GET /api/v1/profile/

without valid authentication.

Expected result:

- Request is rejected.
- Expected authentication status code is returned.
- Standard error structure is used.

### SP-GET-03: Invalid Authentication

Action:

Send the profile request using invalid authentication.

Expected result:

- Request is rejected.
- No Student Profile data is returned.

### SP-GET-04: Profile Relationship Data

Where related records exist, verify the response correctly represents approved profile areas such as:

- Skills.
- Interests.
- Education.
- Experience.
- Projects.
- Career goals.
- Personality responses where implemented.

The expected structure should match the final Student Profile API contract.

## 11. Student Profile Update Tests

### SP-PATCH-01: Valid Partial Update

Precondition:

- Authenticated Student.
- Existing StudentProfile.

Action:

Submit a valid partial update.

Expected result:

- Request succeeds.
- Submitted information is updated.
- Unsubmitted profile information is preserved.
- Updated data persists in PostgreSQL.

### SP-PATCH-02: Invalid Field Value

Action:

Submit profile data containing an invalid value.

Expected result:

- Request is rejected.
- Validation error is returned.
- Invalid data is not stored.

### SP-PATCH-03: Empty Partial Request

Action:

Submit an empty PATCH request.

Expected result:

- Behaviour follows the approved serializer and REST API contract.
- No unintended profile data is removed.

### SP-PATCH-04: Server-Controlled Fields

Action:

Attempt to change server-controlled ownership information such as:

    user_id

Expected result:

- Ownership is not changed.
- The backend ignores or rejects unauthorised ownership changes according to the final serializer design.

### SP-PATCH-05: Persistence

Action:

1. Update valid Student Profile information.
2. Retrieve the profile again.

Expected result:

- The new values are returned.
- Changes persist in PostgreSQL.

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

### SP-OWN-01: Student A Reads Own Profile

Expected result:

- Access succeeds.

### SP-OWN-02: Student B Reads Own Profile

Expected result:

- Access succeeds.

### SP-OWN-03: Cross-Student Access

Attempt to access another student's protected profile through any available client-controlled identifier or route.

Expected result:

- Access is rejected or the route does not expose cross-student selection.
- No other Student's protected profile information is returned.

### SP-OWN-04: Ownership Modification

Attempt to submit another user's identifier as part of an update.

Expected result:

- The backend does not transfer profile ownership.
- Student A cannot cause data to become owned by Student B through client input.

## 13. Skill Validation Tests

Once StudentSkill behaviour is implemented, verify:

- Valid Skill references are accepted.
- Invalid Skill references are rejected.
- Approved proficiency values are accepted.
- Invalid proficiency values are rejected.
- Duplicate StudentSkill relationships are prevented where required.
- StudentSkill records belong to the authenticated StudentProfile.

Final proficiency tests depend on team confirmation of the proficiency scale.

## 14. Interest Validation Tests

Once StudentInterest behaviour is implemented, verify:

- Valid Interest references are accepted.
- Invalid Interest references are rejected.
- Duplicate StudentInterest relationships are prevented where required.
- StudentInterest records belong to the authenticated StudentProfile.
- Student Profile operations do not provide unintended permission to modify shared Interest reference data.

## 15. Education Tests

Once Education behaviour is implemented, verify:

- Valid Education records are accepted.
- Required fields are enforced.
- Invalid dates are rejected.
- Logical date rules are enforced.
- Education records belong to the authenticated StudentProfile.
- Updates do not modify another Student's Education records.
- Deletion behaviour follows the final API contract.

## 16. Experience Tests

Once Experience behaviour is implemented, verify:

- Valid Experience records are accepted.
- Required fields are enforced.
- Start and end dates follow approved validation rules.
- Current experience is handled consistently with `is_current`.
- Experience records belong to the authenticated StudentProfile.
- Another Student's Experience records cannot be modified.

## 17. Project Tests

Once Project behaviour is implemented, verify:

- Valid Project records are accepted.
- Invalid project URLs are rejected where URL validation applies.
- Required fields are enforced.
- Project dates follow approved validation rules.
- Projects belong to the authenticated StudentProfile.
- Another Student's Project records cannot be modified.

## 18. Career Goal Tests

Once CareerGoal behaviour is implemented, verify:

- Valid career goals are accepted.
- Required fields are enforced.
- CareerGoal records belong to the authenticated StudentProfile.
- Another Student's CareerGoal records cannot be modified.

## 19. Personality Response Tests

PersonalityResponse testing depends on the final questionnaire design.

Once implemented, verify:

- Approved question identifiers are accepted.
- Approved response values are accepted.
- Invalid response values are rejected where restrictions exist.
- Responses belong to the authenticated StudentProfile.
- Another Student's responses cannot be retrieved or modified through Student operations.

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

Once the React authentication interface is available, verify the complete frontend flow.

### FE-AUTH-01: Registration

Expected result:

- Student submits valid registration information.
- Frontend sends the expected API request.
- Backend response is handled correctly.
- Student receives appropriate success or next-step behaviour.

### FE-AUTH-02: Invalid Registration

Expected result:

- Backend validation errors are displayed appropriately.
- The interface does not report success.

### FE-AUTH-03: Login

Expected result:

- Valid login succeeds.
- Frontend receives the expected authentication response.
- Authenticated interface state is established.

### FE-AUTH-04: Invalid Login

Expected result:

- Login fails.
- Controlled error information is displayed.
- User is not treated as authenticated.

### FE-AUTH-05: Current User

Expected result:

- Frontend retrieves current-user information through `/api/v1/auth/me/`.
- Correct authenticated user information is displayed or stored in application state.

### FE-AUTH-06: Expired Access Token

Expected result:

- Behaviour follows the approved frontend JWT strategy.
- The application either performs the approved refresh flow or returns the user to an unauthenticated state.

### FE-AUTH-07: Logout

Expected result:

- Backend logout behaviour is completed where required.
- Frontend authentication state is cleared.
- Protected Student functions are no longer available through the authenticated interface.

## 22. Frontend Student Profile Integration Tests

Once the React Student Profile interface is available, verify:

### FE-PROFILE-01: Load Profile

Expected result:

- Authenticated Student opens the Student Profile interface.
- Frontend requests `/api/v1/profile/`.
- Correct Student data is displayed.

### FE-PROFILE-02: Update Profile

Expected result:

- Student edits approved profile information.
- Frontend sends the expected PATCH request.
- Backend validates and stores the update.
- Updated information appears in the interface.

### FE-PROFILE-03: Validation Error

Expected result:

- Invalid data is rejected by the backend.
- Frontend displays useful validation feedback.
- Invalid data is not presented as successfully saved.

### FE-PROFILE-04: Authentication Failure

Expected result:

- Protected profile requests fail when authentication is invalid.
- Protected Student Profile information is not displayed.

### FE-PROFILE-05: Refresh After Update

Expected result:

- Updated profile data persists after the page or profile data is reloaded.

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

Database passwords and connection secrets must not be committed to the repository.

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

Before Sprint 1 review, rerun the completed tests for:

- Registration.
- Login.
- Token refresh.
- Logout.
- Current-user retrieval.
- Student Profile retrieval.
- Student Profile update.
- Student Profile validation.
- Student Profile ownership.
- React authentication integration.
- React Student Profile integration.

Previously passing functionality should continue to pass after integration changes.

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

The following test details are pending implementation confirmation:

1. Final Student Profile serializer structure.
2. Final proficiency values.
3. Final Skill API representation.
4. Final Interest API representation.
5. Nested profile updates versus dedicated related-resource endpoints.
6. StudentProfile creation timing.
7. Final frontend JWT storage and refresh strategy.
8. Final frontend form structure.
9. Final personality questionnaire.
10. Final deletion behaviour for related Student Profile records.
11. Final local CORS origins.
12. Final behaviour when an authenticated Student has no StudentProfile.

These items should be updated when the relevant implementation is available.

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

Authentication implementation has been reported as completed by the backend developer, but final results should be confirmed against the reviewed and merged implementation.

Student Profile backend and frontend implementation details are still pending.

Test areas depending on unfinished implementation are therefore defined as planned tests and should be updated when those components become available.