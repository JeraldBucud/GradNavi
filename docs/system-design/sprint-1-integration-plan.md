# GradNavi Sprint 1 Integration Plan

Status: Working plan, pending frontend and backend implementation updates

## 1. Purpose

This document defines the Sprint 1 integration plan for GradNavi.

The plan describes how the React frontend, Django backend, JWT authentication, Student Profile module, and PostgreSQL database are expected to work together during Sprint 1.

This document covers the full team integration flow.

Implementation-specific details will be updated as the authentication backend, Student Profile backend, and frontend components are completed and reviewed.

## 2. Sprint 1 Integration Goal

The Sprint 1 integration goal is to produce a working authenticated Student Profile flow.

The intended end-to-end flow is:

    Student
       |
       v
    React Frontend
       |
       | Login or Registration
       v
    Django Authentication API
       |
       | JWT Access and Refresh Tokens
       v
    Authenticated React Session
       |
       | GET /api/v1/auth/me/
       v
    Current User
       |
       | GET /api/v1/profile/
       v
    Student Profile API
       |
       v
    PostgreSQL
       |
       v
    Student Profile Data
       |
       v
    React Student Profile Interface

The completed flow should allow a student to:

- Register an account.
- Log in.
- Maintain an authenticated session.
- Retrieve the current authenticated user.
- Retrieve their own Student Profile.
- Update their own Student Profile.
- Receive controlled validation and permission errors.
- Avoid access to another student's protected profile information.

## 3. Current Integration Status

At the time of writing:

- The REST API Design is available as the shared API contract.
- The Security Architecture is available for authentication, authorization, ownership, and security rules.
- The Student Profile Data Design and ERD are available.
- The Student Profile API and Model Mapping is available.
- Backend authentication has been reported as implemented on `feature/backend-auth`, but the final merged implementation is still pending review.
- Final Student Profile backend implementation details are not yet confirmed.
- Final React authentication and Student Profile frontend implementation details are not yet confirmed.

This document therefore defines the intended integration contract without assuming unverified implementation details.

## 4. Integration Components

Sprint 1 integration involves the following components:

### 4.1 React Frontend

Planned responsibilities:

- Display registration and login forms.
- Send authentication requests to the Django REST API.
- Store and use authentication state according to the approved implementation.
- Send JWT access credentials with protected requests.
- Retrieve the current authenticated user.
- Retrieve Student Profile information.
- Submit Student Profile updates.
- Display validation, authentication, and permission errors.
- Prevent normal interface access to functions that are unavailable to the current user.

Frontend controls do not replace backend authentication or permission checks.

### 4.2 Django Authentication Backend

Planned responsibilities:

- Register users.
- Authenticate login credentials.
- Issue JWT access and refresh tokens.
- Refresh access tokens.
- Support logout and refresh-token invalidation according to the implemented authentication design.
- Support password recovery.
- Return the current authenticated user through `/api/v1/auth/me/`.
- Return standardised API errors.

Final behaviour should follow the merged authentication implementation.

### 4.3 Student Profile Backend

Planned responsibilities:

- Associate the authenticated User with one StudentProfile.
- Retrieve the authenticated student's profile.
- Validate Student Profile updates.
- Enforce ownership of student-owned records.
- Manage related profile data.
- Return API responses that follow the approved Student Profile contract.

The final model and serializer behaviour should align with the Student Profile Data Design and API Model Mapping.

### 4.4 PostgreSQL

PostgreSQL provides persistent storage for:

- User account data.
- StudentProfile records.
- Student-owned related profile records.
- Shared Skill and Interest reference data.

Frontend code must not connect directly to PostgreSQL.

### 4.5 REST API

The Django REST API acts as the contract between the frontend and backend.

Sprint 1 integration depends on the following confirmed endpoint groups:

    /api/v1/auth/
    /api/v1/profile/

Authentication and profile operations must remain aligned with the shared REST API Design.

## 5. Authentication Integration Flow

The planned login flow is:

    Student
       |
       | Enter credentials
       v
    React Login Form
       |
       | POST /api/v1/auth/login/
       v
    Django Authentication
       |
       | Credentials valid
       v
    JWT Tokens
       |
       v
    React Authentication State
       |
       | Protected API request
       v
    Django REST API

The frontend should treat login success as authenticated only after receiving the expected successful backend response.

The backend remains responsible for validating JWT credentials on protected requests.

## 6. Registration Integration Flow

The planned registration flow is:

    Student
       |
       | Enter account details
       v
    React Registration Form
       |
       | POST /api/v1/auth/register/
       v
    Django Backend
       |
       | Validate account data
       v
    User Account

The final behaviour after registration must follow the implemented authentication contract.

The team should confirm whether successful registration:

- Automatically authenticates the user.
- Redirects the user to login.
- Creates StudentProfile automatically.
- Leaves StudentProfile creation until first profile access or update.

This decision must be confirmed before final frontend integration.

## 7. Current User Integration

The `/api/v1/auth/me/` endpoint should provide the frontend with the authenticated user's approved account information.

Planned flow:

    React
      |
      | Authorization: Bearer <access_token>
      v
    GET /api/v1/auth/me/
      |
      v
    Django JWT Validation
      |
      v
    Authenticated User Response

The frontend may use this response to determine:

- Whether a valid authenticated session exists.
- Basic current-user information.
- Approved role information needed for interface behaviour.

The frontend must not use editable client-side role values as proof of authorization.

## 8. Student Profile Retrieval Flow

The planned profile retrieval flow is:

    React Student Profile Page
          |
          | Authorization: Bearer <access_token>
          v
    GET /api/v1/profile/
          |
          v
    Django Authentication
          |
          v
    Authenticated User
          |
          v
    StudentProfile
          |
          v
    Related Profile Records
          |
          v
    JSON Response
          |
          v
    React Profile Interface

The backend must derive profile ownership from the authenticated User.

The frontend should not need to submit a `user_id` to retrieve the current student's profile.

## 9. Student Profile Update Flow

The planned profile update flow is:

    Student edits profile
          |
          v
    React Form
          |
          | PATCH /api/v1/profile/
          v
    Django REST API
          |
          +---- Authenticate request
          +---- Verify ownership
          +---- Validate submitted data
          +---- Update approved records
          |
          v
    PostgreSQL
          |
          v
    Updated API Response
          |
          v
    React Interface

A PATCH request should update only the submitted profile information.

Unrelated Student Profile data should not be unintentionally replaced.

The exact handling of nested Education, Experience, Project, Skill, Interest, CareerGoal, and PersonalityResponse records is still pending backend confirmation.

## 10. JWT Integration

Protected frontend requests should use the approved JWT access-token format:

    Authorization: Bearer <access_token>

The integration must support:

- Valid access tokens.
- Expired access tokens.
- Refresh-token flow.
- Invalid authentication.
- Logout behaviour.
- Revoked or blacklisted refresh tokens where implemented.

The exact frontend token storage strategy should be reviewed once the React authentication implementation is available.

## 11. Error Handling Integration

Frontend and backend error handling should follow the shared REST API error contract.

The frontend should be prepared to handle:

| Status | Expected Frontend Meaning |
| --- | --- |
| `400 Bad Request` | Submitted data failed validation |
| `401 Unauthorized` | Authentication is missing, invalid, or expired |
| `403 Forbidden` | User is authenticated but lacks permission |
| `404 Not Found` | Requested profile resource does not exist |
| `409 Conflict` | Submitted data conflicts with an existing record |
| `500 Internal Server Error` | Unexpected backend failure |

Error messages shown to users should come from controlled API responses.

Internal stack traces, credentials, and technical debugging details must not be displayed to normal users.

## 12. Ownership and Permission Integration

The backend is the main authorization boundary.

Frontend interface restrictions improve the user experience but must not be treated as security controls.

The backend must reject:

- Student access to another student's profile.
- Client-supplied ownership changes.
- Student access to Administrator-only functions.
- Requests using invalid authentication.

The frontend should not rely on hidden buttons or routes as the only protection.

## 13. CORS and Development Environment

During local development, the React frontend and Django backend may run on different local origins.

The Django backend should allow only the local frontend origins required by the team.

The final local development values should be documented after the frontend development server configuration is confirmed.

Deployed CORS behaviour will be handled separately during deployment work.

## 14. Integration Order

The recommended Sprint 1 integration order is:

1. Authentication backend reviewed and merged.
2. React registration and login interface completed.
3. Authentication frontend connected to backend.
4. `/api/v1/auth/me/` integrated.
5. Student Profile backend implemented and reviewed.
6. Student Profile frontend completed.
7. Profile GET integration completed.
8. Profile PATCH integration completed.
9. Ownership and permission checks verified.
10. Validation and error responses verified.
11. JWT refresh and logout flows verified.
12. Sprint 1 integration tests completed.
13. Regression tests completed.
14. Sprint 1 review evidence collected.

This order reduces integration work against unstable interfaces.

## 15. Team Integration Responsibilities

### Backend Developer

Responsible for:

- Authentication API implementation.
- Student Profile models.
- Student Profile serializers.
- Student Profile API views and URLs.
- Backend validation.
- Backend permission and ownership checks.
- Backend automated tests.

### Frontend Developer

Responsible for:

- Registration interface.
- Login interface.
- Student Profile interface.
- Frontend API calls.
- Form validation for user feedback.
- Authenticated interface state.
- Displaying controlled API errors.

### Integration Work

Integration work should include:

- Confirming frontend requests match backend contracts.
- Confirming backend responses match frontend expectations.
- Resolving field-name mismatches.
- Resolving endpoint mismatches.
- Verifying JWT behaviour.
- Verifying Student Profile ownership.
- Testing complete user flows.

Specific task ownership should remain aligned with the team's current Sprint 1 allocation.

## 16. Integration Dependencies

Sprint 1 integration depends on:

- Authentication backend completion and merge.
- React authentication interface completion.
- Student Profile backend completion.
- Student Profile frontend completion.
- Stable `/api/v1/auth/` contract.
- Stable `/api/v1/profile/` contract.
- PostgreSQL availability.
- Agreed profile field structures.
- Agreed nested versus dedicated related-resource API behaviour.

Integration tasks blocked by unfinished components should be recorded rather than worked around through undocumented temporary behaviour.

## 17. Known Integration Decisions Pending

The following decisions are still pending:

1. Final authentication response fields.
2. Final frontend JWT storage approach.
3. StudentProfile creation timing.
4. Final Student Profile serializer structure.
5. Final Skill JSON structure.
6. Final Interest JSON structure.
7. Final proficiency scale.
8. Nested profile updates versus dedicated related-resource endpoints.
9. Handling deletion of nested Student Profile records.
10. Final frontend form field structure.
11. Final local frontend origin for CORS.
12. Final Student Profile error behaviour where no profile exists.

These items should be updated as implementation information becomes available.

## 18. Integration Completion Criteria

Sprint 1 integration should be treated as complete when:

- A student can register.
- A student can log in.
- Valid authentication provides access to protected Student functions.
- Invalid authentication is rejected.
- The current authenticated user can be retrieved.
- The authenticated student can retrieve their own profile.
- The authenticated student can update their own profile.
- Another student's profile cannot be accessed.
- Validation errors are displayed and handled correctly.
- JWT refresh behaviour works according to the approved implementation.
- Logout behaviour works according to the approved implementation.
- Frontend and backend field names are aligned.
- Automated and manual Sprint 1 integration tests pass.
- Relevant evidence is recorded for Sprint review.

## 19. Documentation Update Rules

This plan should be updated when:

- Authentication implementation changes.
- Student Profile API behaviour changes.
- Frontend request or response expectations change.
- Profile ownership rules change.
- JWT handling changes.
- Sprint 1 integration testing identifies a contract mismatch.

Changes affecting the shared API contract should also be reflected in the GradNavi REST API Design.

## 20. Plan Status

This is a working Sprint 1 integration plan.

The plan defines the intended full-team integration flow while the final frontend and backend implementations are still pending.

Unverified implementation details are intentionally recorded as pending decisions rather than treated as completed behaviour.