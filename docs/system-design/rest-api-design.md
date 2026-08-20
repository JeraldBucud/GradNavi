# GradNavi REST API Design

Status: Working design for team review

## 1. Purpose

This document defines the REST API design for the GradNavi web application. The API provides the communication layer between the React frontend and the Django backend.

The design defines the planned API structure, endpoint naming, HTTP methods, authentication requirements, request and response formats, permissions, validation behaviour, and HTTP status codes.

The API design supports the functional and non-functional requirements defined for GradNavi and provides a shared contract for frontend, backend, integration, and testing work.

## 2. API Technology

GradNavi uses:

* Django for the backend application.
* Django REST Framework for REST API development.
* PostgreSQL for persistent application data.
* JSON for API request and response bodies.
* JWT for authenticated API access.
* React for the frontend client.

The frontend communicates with GradNavi through the Django REST API. Direct database access from the frontend is not permitted.

## 3. Design Scope

This API design covers the planned V1 GradNavi functionality, including:

* Account registration and authentication.
* Student profile management.
* Career recommendations and explanations.
* Skill-gap analysis.
* Career-readiness scoring.
* Job-description matching.
* Resume and cover-letter generation.
* Interview preparation.
* Learning suggestions.
* Career roadmap management.
* Progress tracking.
* Administration.
* Data deletion.
* Audit and error handling.

Sprint 1 endpoints are defined in greater detail because authentication and student profile functionality form the initial implementation foundation.

## 4. API Conventions

### 4.1 Base Path

All GradNavi V1 REST API endpoints use the following base path:

```text
/api/v1/
```

Using a versioned base path allows later API changes to be introduced without immediately breaking clients that depend on the V1 contract.

### 4.2 Resource Naming

API paths use lowercase resource names and hyphens where multiple words are required.

Examples:

```text
/api/v1/profile/
/api/v1/careers/
/api/v1/skills/
/api/v1/learning-resources/
/api/v1/job-descriptions/
```

Resource-oriented paths are preferred over action-oriented names. The HTTP method identifies the requested operation.

### 4.3 HTTP Methods

GradNavi uses standard HTTP methods according to the requested operation:

| Method | Purpose                                        |
| ------ | ---------------------------------------------- |
| GET    | Retrieve a resource or collection of resources |
| POST   | Create a new resource or start an operation    |
| PUT    | Replace an existing resource                   |
| PATCH  | Update part of an existing resource            |
| DELETE | Delete an existing resource                    |

The API should use the most appropriate HTTP method rather than including actions such as `get`, `create`, or `delete` in endpoint names.

## 5. HTTP Status Codes

GradNavi uses standard HTTP status codes so frontend clients can determine whether a request succeeded, failed validation, lacked authentication, lacked permission, or encountered a server error.

| Status Code               | Meaning                                 | GradNavi Use                                                                 |
| ------------------------- | --------------------------------------- | ---------------------------------------------------------------------------- |
| 200 OK                    | Request completed successfully          | Successful retrieval, update, or operation                                   |
| 201 Created               | New resource created successfully       | Account registration or creation of a new resource                           |
| 204 No Content            | Request completed with no response body | Successful deletion where no response body is required                       |
| 400 Bad Request           | Request data is invalid                 | Missing fields, invalid values, or validation errors                         |
| 401 Unauthorized          | Authentication is missing or invalid    | Missing, expired, or invalid authentication token                            |
| 403 Forbidden             | Authenticated user lacks permission     | Attempt to access an administrator endpoint or another user's protected data |
| 404 Not Found             | Requested resource does not exist       | Missing profile, career, document, or other requested resource               |
| 409 Conflict              | Request conflicts with existing data    | Duplicate email address or another unique-data conflict                      |
| 500 Internal Server Error | Unexpected backend failure              | Unhandled server or service error                                            |

API responses should use the most appropriate status code for the result of the request.

## 6. Request and Response Format

### 6.1 JSON Format

GradNavi API request and response bodies use JSON unless an endpoint requires a different content type.

Example request:

```json
{
  "email": "student@example.com",
  "first_name": "Alex",
  "last_name": "Student"
}
```

API field names use `snake_case` to remain consistent with the Django backend.

### 6.2 Successful Responses

Successful responses should return the requested or created resource in a predictable structure where appropriate.

Example:

```json
{
  "data": {
    "email": "student@example.com",
    "first_name": "Alex",
    "last_name": "Student"
  }
}
```

Endpoints that perform an operation without returning a resource may return a short message when useful.

Example:

```json
{
  "message": "Account created successfully."
}
```

### 6.3 Error Responses

GradNavi should return errors in a consistent structure so the frontend and tests can process failures predictably.

Example:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid data.",
    "details": {
      "email": [
        "Enter a valid email address."
      ]
    }
  }
}
```

The error response structure contains:

* `code`: A stable machine-readable error identifier.
* `message`: A human-readable description of the error.
* `details`: Optional field-specific or contextual information.

Sensitive technical details, database errors, credentials, tokens, stack traces, and internal service information must not be returned to normal API clients.

### 6.4 Date and Time Values

Date and time values should use ISO 8601 format.

Example:

```text
2026-08-13T01:30:00Z
```

This provides a consistent representation for frontend parsing, storage, API testing, and future deployment environments.

## 7. Authentication and Authorization

### 7.1 Authentication

GradNavi uses JWT-based authentication for protected REST API endpoints.

After successful login, the backend issues authentication tokens that the frontend uses for subsequent protected requests.

Public endpoints, such as account registration and login, do not require an authenticated user.

Protected endpoints require a valid authentication token.

### 7.2 Authorization

Authentication identifies the user. Authorization determines which resources and operations the authenticated user is permitted to access.

GradNavi currently defines two application roles:

* Student
* Administrator

Students are permitted to access their own profile, career guidance data, generated documents, interview preparation records, learning suggestions, roadmap data, and other student functions.

Administrators are permitted to access authorised administration functions such as management of users, careers, skills, learning resources, audit records, and reports.

### 7.3 JWT Request Header

Authenticated API requests should send the JWT access token using the HTTP `Authorization` header.

Example:

```http
Authorization: Bearer <access_token>
```

The frontend must not place authentication tokens in URL query parameters.

### 7.4 Protected Resources

Protected endpoints must reject requests without valid authentication.

A missing, invalid, or expired token should return:

```text
401 Unauthorized
```

An authenticated user attempting an operation outside their permissions should return:

```text
403 Forbidden
```

### 7.5 Resource Ownership

Student-owned resources must only be accessible to the student who owns them, unless an authorised administrator has a legitimate administration function requiring access.

The backend is responsible for enforcing ownership rules. The frontend must not be relied upon as the security boundary.

For example, changing a resource identifier in a request must not allow one student to retrieve or modify another student's profile or saved content.

### 7.6 Secrets and Credentials

Passwords, JWT signing secrets, database credentials, AI provider keys, and other sensitive configuration values must not be returned through API responses or stored directly in frontend source code.

Sensitive backend configuration should be stored using environment variables or another approved secret-management approach.

## 8. High-Level Endpoint Catalogue

The GradNavi API is organised into functional resource groups.

| API Area           | Base Endpoint                 | Purpose                                                          |
| ------------------ | ----------------------------- | ---------------------------------------------------------------- |
| Authentication     | `/api/v1/auth/`               | Registration, login, token refresh, logout, and account recovery |
| Student Profile    | `/api/v1/profile/`            | Manage the authenticated student's profile information           |
| Careers            | `/api/v1/careers/`            | Retrieve career reference data                                   |
| Recommendations    | `/api/v1/recommendations/`    | Generate and retrieve ranked career recommendations              |
| Skill Gaps         | `/api/v1/skill-gaps/`         | Compare student skills against career requirements               |
| Readiness          | `/api/v1/readiness/`          | Calculate and retrieve career-readiness results                  |
| Job Descriptions   | `/api/v1/job-descriptions/`   | Analyse pasted job descriptions and compare requirements         |
| Documents          | `/api/v1/documents/`          | Manage generated resume and cover-letter drafts                  |
| Interviews         | `/api/v1/interviews/`         | Manage interview questions, answers, and feedback                |
| Learning Resources | `/api/v1/learning-resources/` | Retrieve learning suggestions linked to skill gaps               |
| Career Roadmaps    | `/api/v1/roadmaps/`           | Manage ordered career-development steps                          |
| Progress           | `/api/v1/progress/`           | Retrieve student progress and saved activity                     |
| Administration     | `/api/v1/admin/`              | Manage authorised administrative resources                       |
| Audit              | `/api/v1/audit/`              | Access permitted audit information and system records            |

These endpoint groups define the planned V1 API structure. Detailed request and response contracts are documented separately for endpoints as implementation work progresses.

## 9. Sprint 1 Detailed API Contracts

This section defines the detailed API contracts for Sprint 1 functionality.

The contracts specify endpoint paths, HTTP methods, authentication requirements, request and response formats, expected status codes, validation behaviour, and permission requirements.

Authentication endpoint details will be aligned with the implementation being completed by MD before this section is finalised.

## 9.1 Authentication API

**Status:** Sprint 1 authentication API contract. Endpoint structure and V1 base path confirmed. Detailed request and response contracts remain subject to team review if implementation identifies a required change.

The Authentication API supports account registration, login, JWT token management, logout, password recovery, and retrieval of the currently authenticated user.

Final request and response fields will be aligned with the implemented authentication model once backend authentication development and testing are complete.

### 9.1.1 Register Account

### 9.1.1 Register Account

**Endpoint**

`POST /api/v1/auth/register/`

**Purpose**

Creates a new GradNavi Student account.

**Authentication**

Not required.

**Request Body**

```json
{
  "email": "student@example.com",
  "password": "ExamplePassword123!",
  "password_confirm": "ExamplePassword123!",
  "first_name": "Test",
  "last_name": "Student"
}
```

**Request Fields**

| Field | Required | Description |
| --- | --- | --- |
| `email` | Yes | Must contain a valid email address and must not already belong to an existing GradNavi account. |
| `password` | Yes | Must satisfy the password validation rules configured by the Django backend. |
| `password_confirm` | Yes | Must match the submitted `password` value. |
| `first_name` | Yes | Student's first name. Must not be blank. |
| `last_name` | Yes | Student's last name. Must not be blank. |

The React frontend may perform basic validation to improve usability, but the Django backend is responsible for authoritative validation.

**Account Role**

Public registration creates a Student account.

The registration request must not accept a client-controlled `role` value. Users must not be able to register themselves as an Administrator or assign other protected permissions.

**Successful Response**

`201 Created`

```json
{
  "id": 1,
  "email": "student@example.com",
  "first_name": "Test",
  "last_name": "Student",
  "role": "student"
}
```

The registration response must not return:

- `password`
- `password_confirm`
- password hashes
- JWT signing information
- password-reset credentials
- authentication secrets
- internal authentication data

A successful registration creates the account but does not automatically return JWT credentials.

Authentication tokens are issued through the Login endpoint unless the approved backend implementation later changes this behaviour.

**Validation Behaviour**

| Scenario | HTTP Status |
| --- | --- |
| Missing required field | `400 Bad Request` |
| First name is blank | `400 Bad Request` |
| Last name is blank | `400 Bad Request` |
| Invalid email format | `400 Bad Request` |
| Passwords do not match | `400 Bad Request` |
| Password fails configured backend password-validation rules | `400 Bad Request` |
| Email already exists | `409 Conflict` |
| Unexpected backend failure | `500 Internal Server Error` |


Validation failures must follow the standard GradNavi API error structure.

**Example Validation Response**

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid data.",
    "details": {
      "password_confirm": [
        "The passwords do not match."
      ]
    }
  }
}
```

**Example Duplicate Email Response**

```json
{
  "error": {
    "code": "conflict",
    "message": "A user with this email already exists.",
    "details": {
      "email": [
        "A user with this email already exists."
      ]
    }
  }
}
```

**Security Requirements**

- Registration data must be treated as untrusted input.
- Passwords must be processed using the approved Django authentication and password-hashing mechanisms.
- Plain-text passwords must never be stored.
- The backend must enforce all registration validation even when the React frontend has already validated the form.
- The backend must control the account role and permissions assigned during registration.
- Registration responses and application logs must not expose passwords, password hashes, secrets, or internal authentication information.

### 9.1.2 Login

Endpoint:

```http
POST /api/v1/auth/login/
```

Purpose:

Authenticates a user and issues JWT access and refresh tokens.

Authentication:

Not required.

Expected success status:

```text
200 OK
```

Expected errors:

```text
400 Bad Request
401 Unauthorized
500 Internal Server Error
```

### 9.1.3 Refresh Access Token

Endpoint:

```http
POST /api/v1/auth/token/refresh/
```

Purpose:

Uses a valid refresh token to obtain a new JWT access token.

Authentication:

A valid refresh token is required.

Expected success status:

```text
200 OK
```

Expected errors:

```text
400 Bad Request
401 Unauthorized
```

### 9.1.4 Logout

Endpoint:

```http
POST /api/v1/auth/logout/
```

Purpose:

Ends the authenticated session and invalidates the submitted refresh token where supported by the authentication implementation.

Authentication:

Required.

Expected success status:

```text
200 OK
```

or:

```text
204 No Content
```

The final response behaviour will be aligned with the backend implementation.

Expected errors:

```text
400 Bad Request
401 Unauthorized
```

### 9.1.5 Request Password Reset

Endpoint:

```http
POST /api/v1/auth/password/reset/
```

Purpose:

Starts the account-recovery process for a user who has forgotten their password.

Authentication:

Not required.

Expected success status:

```text
200 OK
```

The response should not reveal whether a submitted email address belongs to an existing account.

### 9.1.6 Confirm Password Reset

Endpoint:

```http
POST /api/v1/auth/password/reset/confirm/
```

Purpose:

Sets a new password after successful verification of a password-reset request.

Authentication:

Password-reset verification credentials are required.

Expected success status:

```text
200 OK
```

Expected errors:

```text
400 Bad Request
401 Unauthorized
```

### 9.1.7 Retrieve Current User

Endpoint:

```http
GET /api/v1/auth/me/
```

Purpose:

Returns basic account information for the currently authenticated user.

Authentication:

Required.

Expected success status:

```text
200 OK
```

Expected errors:

```text
401 Unauthorized
```

The response must contain only account information required by the frontend and must not expose passwords, password hashes, refresh tokens, secrets, or internal authentication data.




## 9.2 Student Profile API

The Student Profile API manages the authenticated student's profile information.

The profile contains the structured information required by GradNavi, including skills, interests, education, experience, projects, career goals, and personality-related responses. The exact database fields will be aligned with the Student Profile model when that implementation is finalised.

All Student Profile endpoints require authentication.

### Student Skill Representation

Skills in the Student Profile use shared Skill reference data together with the authenticated student's proficiency level.

A Student Profile skill should use the following structure:

```json
{
  "id": 12,
  "name": "Python",
  "category": "Programming",
  "proficiency_level": "proficient"
}
```

The approved `proficiency_level` values are:

| Display Label | API Value |
| --- | --- |
| Foundational | `foundational` |
| Developing | `developing` |
| Proficient | `proficient` |
| Advanced | `advanced` |

The backend must validate `proficiency_level` and reject unsupported values with `400 Bad Request`.

The frontend should display the user-friendly labels while sending and receiving the lowercase API values.

Skill reference information such as `id`, `name`, and `category` comes from shared Skill data. The authenticated student's proficiency is stored through the StudentSkill relationship.

The frontend must not use a client-supplied user identifier to control Student Profile ownership.

### 9.2.1 Retrieve Student Profile

Endpoint:

```http
GET /api/v1/profile/
```

Purpose:

Retrieves the profile belonging to the currently authenticated student.

Authentication:

Required.

Successful response:

```json
{
  "data": {
    "profile": {
      "skills": [
          {
            "id": 12,
            "name": "Python",
            "category": "Programming",
            "proficiency_level": "proficient"
          }
      ]
      "interests": [],
      "education": [],
      "experience": [],
      "projects": [],
      "career_goals": [],
      "personality_responses": []
    }
  }
}
```

Success status:

```text
200 OK
```

Expected errors:

```text
401 Unauthorized
404 Not Found
500 Internal Server Error
```

The backend must retrieve the profile associated with the authenticated user. A student must not be able to retrieve another student's profile by changing a request value or resource identifier.

### 9.2.2 Update Student Profile

Endpoint:

```http
PATCH /api/v1/profile/
```

Purpose:

Updates selected fields in the authenticated student's profile without requiring the entire profile to be replaced.

Authentication:

Required.

Example request:

```json
{
  "career_goals": [
    "Software Engineer"
  ],
  "interests": [
    "Artificial Intelligence",
    "Backend Development"
  ]
}
```

Successful response:

```json
{
  "data": {
    "profile": {
    "skills": [
      {
        "id": 12,
        "name": "Python",
        "category": "Programming",
        "proficiency_level": "proficient"
      }
    ],
"interests": [],
      "education": [],
      "experience": [],
      "projects": [],
      "career_goals": [
        "Software Engineer"
      ],
      "personality_responses": []
    }
  }
}
```

Success status:

```text
200 OK
```

Expected errors:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error
```

The backend must validate supplied profile data before saving changes.

The backend must enforce resource ownership and must not trust the frontend to determine which student's profile is being updated.


## 10. Collection Query Conventions

Some GradNavi API endpoints return collections of resources. Collection endpoints should support consistent pagination, filtering, and sorting where these features are useful.

### 10.1 Pagination

Large collections should use pagination instead of returning every available record in one response.

Example:

```http
GET /api/v1/careers/?page=2
```

A paginated response should include the requested results and enough metadata for the frontend to move between pages.

Example:

```json
{
  "count": 48,
  "next": "/api/v1/careers/?page=3",
  "previous": "/api/v1/careers/?page=1",
  "results": []
}
```

The exact page size will be defined during implementation and should remain consistent unless an endpoint has a documented reason to use a different value.

### 10.2 Filtering

Collection endpoints may support query parameters for narrowing returned results.

Example:

```http
GET /api/v1/careers/?category=technology
```

Filtering rules must use documented fields and must not permit access to resources outside the authenticated user's permissions.

### 10.3 Sorting

Collection endpoints may support sorting when the result order is useful to the user.

Example:

```http
GET /api/v1/careers/?ordering=name
```

Descending order may use a leading hyphen where supported.

Example:

```http
GET /api/v1/careers/?ordering=-created_at
```

### 10.4 Search

Selected reference-data endpoints may support text search where required.

Example:

```http
GET /api/v1/careers/?search=software
```

Search parameters should apply only to approved searchable fields.

### 10.5 Query Parameter Rules

Query parameter names use `snake_case`.

Unsupported or invalid query parameters should not cause the API to expose internal errors.

Where invalid parameter values affect the request, the API should return an appropriate validation response.

## 11. API Validation Rules

GradNavi API endpoints must validate incoming data before performing application logic or storing information in PostgreSQL.

Validation should occur on the backend even when the frontend also performs form validation.

### 11.1 Required Fields

Endpoints must identify required fields and reject requests where required information is missing.

Example:

```json
{
  "email": ""
}
```

If a required value is missing or empty, the API should return:

```text
400 Bad Request
```

The response should identify the affected field where appropriate.

### 11.2 Data Type Validation

Submitted values must match the expected data type.

Examples include:

* Text fields must receive valid string values.
* Numerical scores must use approved numerical formats.
* Lists must use array structures where required.
* Boolean values must use valid boolean values.
* Date and time fields must use the documented format.

Invalid data types should return an appropriate validation error.

### 11.3 Format Validation

Fields with defined formats must be validated before processing.

Examples include:

* Email addresses.
* Password inputs.
* Date values.
* URLs.
* Identifiers.
* Structured AI responses.

Format validation should reject malformed input before the data reaches application logic.

### 11.4 Allowed Values

Fields with a restricted set of values must reject unsupported values.

For example, where an endpoint accepts an approved role, status, category, or other controlled value, the backend should validate the value against the permitted options.

### 11.5 Length and Size Limits

Text and collection inputs should use reasonable limits where required.

Limits may apply to:

* Profile text.
* Career goals.
* Project descriptions.
* Job-description text.
* Interview responses.
* Generated document content.
* Uploaded or submitted collections.

The exact limits should be defined during implementation according to the associated model and functional requirement.

### 11.6 Ownership Validation

The backend must validate that authenticated users are permitted to operate on the requested resource.

A student must not be able to retrieve, update, or delete another student's protected information by modifying a URL, identifier, request body, or query parameter.

Ownership validation must occur on the backend.

### 11.7 Duplicate and Unique Data

Fields that require unique values must be checked before creating or updating a resource.

For example, an account registration request using an email address already associated with an existing account should return an appropriate conflict or validation response.

### 11.8 Business Rule Validation

Requests must also comply with GradNavi business rules.

Examples include:

* Recommendation scores must come from the approved scoring logic rather than client-supplied values.
* Career-readiness scores must be calculated by the backend.
* Students must not assign themselves administrator permissions.
* Generated AI content must be validated before it is returned or stored.
* Job-description analysis must operate on submitted job-description content rather than trusted client-generated results.

### 11.9 Validation Error Response

Validation failures should follow the standard GradNavi error-response structure.

Example:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid data.",
    "details": {
      "email": [
        "Enter a valid email address."
      ]
    }
  }
}
```

Validation responses must not expose stack traces, database errors, credentials, secrets, or internal implementation details.

## 12. API Error Handling

GradNavi API endpoints should handle expected and unexpected failures consistently.

Errors should return an appropriate HTTP status code together with the standard GradNavi error-response structure.

### 12.1 Standard Error Structure

API errors should follow this structure where appropriate:

```json
{
  "error": {
    "code": "error_code",
    "message": "A clear description of the error.",
    "details": {}
  }
}
```

The `code` value provides a stable identifier for frontend logic and automated testing.

The `message` value provides a readable explanation of the failure.

The optional `details` value provides field-specific or contextual information where required.

### 12.2 Validation Errors

Invalid request data should return:

```text
400 Bad Request
```

Example:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid data.",
    "details": {
      "email": [
        "Enter a valid email address."
      ]
    }
  }
}
```

### 12.3 Authentication Errors

Missing, expired, or invalid authentication credentials should return:

```text
401 Unauthorized
```

Example:

```json
{
  "error": {
    "code": "authentication_required",
    "message": "Valid authentication is required."
  }
}
```

### 12.4 Permission Errors

An authenticated user attempting an operation outside their permissions should return:

```text
403 Forbidden
```

Example:

```json
{
  "error": {
    "code": "permission_denied",
    "message": "You do not have permission to perform this operation."
  }
}
```

### 12.5 Resource Not Found

Requests for resources that do not exist or are not accessible to the authenticated user should return an appropriate not-found response.

```text
404 Not Found
```

Example:

```json
{
  "error": {
    "code": "not_found",
    "message": "The requested resource was not found."
  }
}
```

The response must not reveal information about protected resources owned by another user.

### 12.6 External Service Errors

Failures involving external services, including the AI provider, should be handled by the Django backend.

The backend should use configured timeouts, validate external responses, and return a controlled error to the frontend.

Example:

```json
{
  "error": {
    "code": "external_service_unavailable",
    "message": "The requested service is temporarily unavailable. Please try again later."
  }
}
```

External API keys, provider error payloads, prompts containing sensitive information, and internal service details must not be exposed to the frontend.

### 12.7 Database and Internal Errors

Unexpected database or backend failures should return a controlled server-error response.

```text
500 Internal Server Error
```

Example:

```json
{
  "error": {
    "code": "internal_error",
    "message": "An unexpected error occurred."
  }
}
```

Stack traces, SQL queries, database credentials, environment variables, file paths, and other internal implementation details must not be returned to normal API clients.

### 12.8 Error Logging

Critical backend failures should be recorded through the approved logging or audit mechanism.

Logs should contain enough technical information for debugging without unnecessarily recording passwords, JWT tokens, API keys, or sensitive student information.

## 13. API Security Rules

GradNavi REST API endpoints must follow consistent security controls to protect user accounts, student information, system data, authentication credentials, and external service credentials.

Security controls must be enforced by the Django backend. Frontend controls support the user experience but must not serve as the primary security boundary.

### 13.1 HTTPS

Deployed API communication must use HTTPS.

Authentication tokens, personal information, profile data, and other sensitive information must not be transmitted through unencrypted production HTTP connections.

### 13.2 Authentication

Protected API endpoints require valid authentication.

GradNavi uses JWT authentication for protected REST API access.

Public endpoints are limited to functions where unauthenticated access is required, such as:

* Account registration.
* Login.
* Password-reset requests.
* Password-reset confirmation.

Other student and administration functions require authentication unless specifically documented otherwise.

### 13.3 Authorization

Authentication alone does not grant access to every endpoint.

The backend must verify whether the authenticated user has permission to perform the requested operation.

GradNavi currently defines two V1 application roles:

* Student.
* Administrator.

Student accounts must not receive administrator permissions through request data or frontend controls.

Administrator-only endpoints must reject unauthorised student access.

### 13.4 Object-Level Access Control

The backend must enforce ownership rules for student-owned resources.

Student-owned resources may include:

* Student profile information.
* Saved recommendations.
* Skill-gap results.
* Readiness results.
* Generated documents.
* Job-description analyses.
* Interview records.
* Learning suggestions.
* Career roadmaps.
* Progress records.

A student must not gain access to another student's protected resource by modifying a URL, resource identifier, request body, or query parameter.

Where disclosure of resource existence would create a privacy risk, the API should avoid revealing whether another user's protected resource exists.

### 13.5 Password Security

GradNavi passwords must use Django's authentication and password-management mechanisms.

Plain-text passwords must not be stored in the database, logs, API responses, source code, or frontend storage.

Password validation rules should follow the approved Django password-policy configuration.

### 13.6 JWT Security

JWT access and refresh tokens must be treated as sensitive authentication credentials.

Tokens must not be:

* Included in URL query parameters.
* Written to application logs.
* Returned through unrelated API responses.
* Stored in source code.
* Exposed to other users.

Access and refresh token behaviour, expiry settings, and logout invalidation must follow the approved authentication implementation.

### 13.7 Secret Management

Sensitive configuration must remain outside committed source code.

Examples include:

* Database passwords.
* Django secret values.
* JWT signing secrets.
* AI provider API keys.
* Deployment credentials.

Secrets should be supplied through environment variables or the approved deployment secret-management mechanism.

### 13.8 Input Validation

The Django backend must validate external input before using the data in application logic or database operations.

Validation applies to:

* JSON request bodies.
* URL parameters.
* Query parameters.
* Resource identifiers.
* Job-description text.
* Profile information.
* Generated or structured AI responses.
* Administration operations.

The backend must not rely only on frontend validation.

### 13.9 AI Request Security

Requests to the AI provider must pass through the Django backend.

The frontend must not communicate directly with the AI provider or receive the provider API key.

Before sending an external AI request, the backend should remove personal information that is not required for the requested operation.

AI responses must be validated before being returned to the frontend or stored.

### 13.10 Sensitive Response Data

API responses must expose only information required for the requested GradNavi function.

Responses must not expose:

* Passwords or password hashes.
* Refresh tokens except through the approved authentication flow.
* Database credentials.
* Environment variables.
* AI provider API keys.
* Internal stack traces.
* SQL queries.
* Server file paths.
* Unnecessary personal information.

### 13.11 Logging and Audit Protection

Security-relevant and critical actions should be recorded through the approved logging or audit mechanism.

Logs must avoid unnecessary storage of:

* Passwords.
* JWT tokens.
* API keys.
* Full authentication credentials.
* Sensitive student profile information.

Logging should provide enough information to investigate failures and security events without creating an additional source of sensitive-data exposure.

### 13.12 Security Testing

Security behaviour should be verified through tests where practical.

Testing should include:

* Requests without authentication.
* Invalid and expired authentication.
* Student access to administrator endpoints.
* Attempts to access another student's resources.
* Invalid request data.
* Secret-management checks.
* Authentication and permission behaviour.
* Error responses that must not expose internal information.


## 14. API Documentation and Change Control

The GradNavi REST API design should remain aligned with the implemented backend, frontend integration, functional requirements, and approved project scope.

Changes to endpoint contracts should be documented before or alongside implementation changes.

### 14.1 API Documentation

Each implemented endpoint should have enough documentation for frontend development, backend development, integration, and testing.

Where applicable, endpoint documentation should include:

* Endpoint path.
* HTTP method.
* Purpose.
* Authentication requirement.
* Required permissions.
* Request parameters.
* Request body.
* Response structure.
* Success status codes.
* Expected error status codes.
* Validation rules.
* Ownership rules.
* Relevant requirement or WBS reference.

### 14.2 Contract Alignment

The implemented backend endpoint should match the documented API contract.

Frontend code should use the documented endpoint path, HTTP method, request format, and response format.

Where the implementation differs from the current design, the team should review the difference and update either the implementation or the API design so both remain aligned.

### 14.3 API Change Process

When an existing API contract needs to change, the change should record:

1. The affected endpoint.
2. The reason for the change.
3. The previous behaviour.
4. The proposed behaviour.
5. Frontend impact.
6. Backend impact.
7. Testing impact.
8. Requirement or scope impact.
9. Team agreement where the change affects shared work.

Changes that affect approved requirements should follow the project requirement change-control process.

### 14.4 Backward Compatibility

Changes to an implemented endpoint should avoid unnecessarily breaking existing frontend functionality.

Where a breaking API change is required, affected team members should be informed before integration work continues.

The V1 base path should remain:

```text
/api/v1/
```

Breaking changes that cannot remain compatible with the V1 contract should be considered for a future API version rather than silently changing existing behaviour.

### 14.5 Implementation Status

The REST API design describes planned and agreed behaviour.

An endpoint documented in this file must not be treated as implemented until the related backend work has been completed and tested.

Where implementation is still pending, the documentation should clearly identify the endpoint as planned, pending confirmation, or under development.

### 14.6 Review

The REST API design should be reviewed when:

* A new API feature is introduced.
* An endpoint path changes.
* Request or response fields change.
* Authentication or permission behaviour changes.
* Database-model changes affect the API contract.
* Frontend integration identifies a contract mismatch.
* A Sprint review results in an approved API change.
