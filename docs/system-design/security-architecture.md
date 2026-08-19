# GradNavi Security Architecture

Status: Working design for team review

## 1. Purpose

This document defines the security architecture for the GradNavi web application.

The security architecture describes how GradNavi protects user accounts, student information, application data, authentication credentials, external service credentials, and communication between system components.

The design defines the planned security controls for authentication, authorization, resource ownership, data privacy, secret management, API access, AI service integration, logging, deployment, and security testing.

Security controls are primarily enforced by the Django backend. Frontend security controls support the user experience but are not treated as the main security boundary.

This document should remain aligned with the GradNavi functional requirements, non-functional requirements, REST API design, system architecture, database design, and implemented application behaviour.

## 2. Security Objectives

The GradNavi security architecture is designed to protect the confidentiality, integrity, availability, privacy, and accountability of the system and its data.

### 2.1 Confidentiality

Sensitive information must only be accessible to authorised users and system components.

Examples include:

* Student profile information.
* Authentication credentials.
* Generated documents.
* Interview records.
* Career guidance results.
* Database credentials.
* JWT secrets.
* AI provider API keys.

The system must prevent unauthorised users from viewing another student's protected information.

### 2.2 Integrity

GradNavi must protect application data from unauthorised or invalid modification.

The backend must validate submitted data before storing or processing it.

Examples include:

* Students must not assign themselves administrator privileges.
* Recommendation and readiness scores must come from approved backend logic.
* Protected records must only be changed by users with the required permission.
* AI responses must be validated before being stored or displayed.

### 2.3 Availability

GradNavi should remain accessible during expected project demonstrations and normal use where the selected hosting platforms and external services are available.

The system should handle service failures in a controlled way, including:

* Database connection failures.
* AI provider outages.
* External API timeouts.
* Authentication failures.

Failures should not expose sensitive technical information to users.

### 2.4 Authentication

The system must verify the identity of users before allowing access to protected functionality.

GradNavi uses Django authentication with JWT-based API access for authenticated requests.

### 2.5 Authorization

Authenticated users must only perform operations allowed by their role and permissions.

GradNavi currently defines two V1 application roles:

* Student.
* Administrator.

Authorization checks must be enforced by the Django backend.

### 2.6 Privacy

GradNavi should collect and process only the personal information required for the intended career-guidance functions.

Personal information sent to external services should be minimised.

AI requests should remove unnecessary personal information before leaving the GradNavi backend.

### 2.7 Accountability

Security-relevant and critical actions should be recorded through appropriate logging or audit mechanisms.

Audit information should support investigation and testing without unnecessarily storing passwords, JWT tokens, API keys, or sensitive personal information.

## 3. System Security Context

GradNavi uses multiple application components that communicate across defined security boundaries.

The main components are:

* React frontend.
* Django REST API backend.
* PostgreSQL database.
* Third-party AI provider.
* Vercel frontend hosting.
* Railway backend and database hosting.
* Student and Administrator users.

### 3.1 React Frontend

The React frontend provides the user interface for GradNavi.

The frontend is responsible for:

* Collecting user input.
* Sending requests to the Django REST API.
* Displaying authorised application data.
* Presenting validation and error messages.
* Providing Student and Administrator interface functions according to the authenticated user's role.

The frontend must not directly access PostgreSQL or communicate directly with the AI provider.

Frontend controls must not be treated as the primary security boundary.

### 3.2 Django Backend

The Django backend acts as the main application and security boundary.

The backend is responsible for:

* Authenticating users.
* Validating JWT credentials.
* Enforcing authorization and permissions.
* Enforcing resource ownership.
* Validating request data.
* Applying business rules.
* Communicating with PostgreSQL.
* Preparing requests for the AI provider.
* Removing unnecessary personal information from AI requests.
* Validating AI responses.
* Protecting server-side secrets.
* Returning controlled API responses.

Security-sensitive decisions must be enforced by the backend rather than relying on the frontend.

### 3.3 PostgreSQL Database

PostgreSQL provides persistent storage for GradNavi application data.

Database access must occur through the Django backend.

The frontend and external AI provider must not receive direct database access.

Database credentials must remain in protected backend configuration and must not be committed to the repository or exposed to the frontend.

### 3.4 Third-Party AI Provider

The AI provider supports approved GradNavi AI functions such as explanations and editable generated content.

AI requests must pass through the Django backend.

Before sending a request externally, the backend should remove personal information that is not required for the requested operation.

AI responses must be treated as external input and validated before being stored or returned to the frontend.

The AI provider must not receive direct database access or application credentials.

### 3.5 Primary Communication Paths

The intended application flow is:

```text
Student / Administrator
        |
        v
React Frontend
        |
        | HTTPS REST API
        v
Django Backend
      /       \
     v         v
PostgreSQL   AI Provider
 Database     API
```

The React frontend communicates with the Django backend through the documented REST API.

The Django backend communicates with PostgreSQL for persistent application data and with the approved AI provider for supported AI operations.

Direct communication between the React frontend and PostgreSQL or between the React frontend and the AI provider is not part of the GradNavi architecture.

### 3.6 Security Enforcement

Security controls should be applied at the component responsible for enforcing them.

Examples include:

* React may hide Administrator controls, but Django must enforce Administrator permissions.
* React may validate form input, but Django must validate submitted API data.
* React may identify the logged-in interface state, but Django must validate the JWT.
* Django must enforce ownership before accessing student-owned database records.
* Django must protect database and AI credentials from frontend access.
* Django must validate external AI responses before application use.

## 4. Assets to Protect

GradNavi processes and stores information with different security and privacy requirements.

Security controls should protect these assets against unauthorised access, modification, disclosure, deletion, or misuse.

### 4.1 User Account Data

User account information includes data required to identify and authenticate GradNavi users.

Examples include:

* Email addresses.
* User identifiers.
* Password hashes.
* Account roles.
* Account status information.
* Password-reset information.

Passwords and authentication credentials require stronger protection than normal application data.

Plain-text passwords must not be stored.

### 4.2 Student Profile Data

Student profiles contain personal information used by GradNavi's career-guidance functions.

Profile information may include:

* Skills.
* Education.
* Interests.
* Experience.
* Projects.
* Career goals.
* Personality-related responses.

Students must only access their own protected profile information unless an authorised Administrator function has a legitimate requirement for access.

### 4.3 Career Guidance Data

GradNavi creates and stores information derived from student profiles.

Examples include:

* Career recommendations.
* Recommendation scores.
* Recommendation explanations.
* Career-readiness scores.
* Skill-gap results.
* Career roadmaps.
* Progress information.
* Learning suggestions.

These records must remain associated with the correct student and must be protected from unauthorised modification.

### 4.4 Generated and Submitted Content

GradNavi processes user-submitted and system-generated content.

Examples include:

* Pasted job descriptions.
* Resume drafts.
* Cover-letter drafts.
* Interview questions.
* Student interview answers.
* Written interview feedback.
* AI-generated explanations.

Generated content should be treated as user-related application data where it contains information derived from a student's profile.

### 4.5 Administrative Data

Administrative functions manage shared GradNavi resources and system information.

Protected administrative data may include:

* User management information.
* Career reference data.
* Skill reference data.
* Learning resources.
* Audit records.
* Reports.

Modification of administrative resources must be restricted to authorised users.

### 4.6 Authentication Tokens

JWT access tokens and refresh tokens represent authenticated sessions and must be treated as sensitive credentials.

Unauthorised access to a valid token could allow another party to act as the authenticated user until the token expires or is invalidated.

Tokens must not be exposed through URLs, logs, source code, or unrelated API responses.

### 4.7 Application Secrets

Application secrets provide access to protected systems or services.

Examples include:

* Django secret values.
* Database credentials.
* JWT signing secrets.
* AI provider API keys.
* Deployment credentials.

Application secrets must not be committed to the Git repository or exposed through frontend code.

### 4.8 Database Content

The PostgreSQL database contains persistent GradNavi application data.

Database access must be restricted to authorised backend and administration processes.

Users, frontend code, and the external AI provider must not receive direct database credentials or unrestricted database access.

### 4.9 Source Code and Configuration

GradNavi source code and configuration files are project assets.

Configuration containing sensitive values must be separated from source code where appropriate.

Environment-specific secrets should be provided through environment variables or an approved deployment configuration mechanism.

### 4.10 Audit and Log Data

Logs and audit records support debugging, testing, accountability, and investigation of security-relevant events.

Logs themselves require protection because poorly designed logging could expose sensitive information.

Passwords, JWT tokens, API keys, and unnecessary personal information must not be recorded in application logs.

## 5. Trust Boundaries

GradNavi contains several trust boundaries where data moves between users, application components, storage, and external services.

Data crossing a trust boundary must be validated, authenticated, authorised, or otherwise checked by the receiving component before it is trusted.

### 5.1 User to Frontend Boundary

Students and Administrators interact with GradNavi through the React frontend.

User input must be treated as untrusted.

Examples include:

* Login credentials.
* Registration data.
* Profile information.
* Career goals.
* Job-description text.
* Interview answers.
* Administration input.

Frontend validation may improve usability, but it does not replace backend validation.

### 5.2 Frontend to Backend Boundary

Requests sent from the React frontend to the Django REST API cross the main application trust boundary.

The Django backend must validate:

* JWT authentication.
* User permissions.
* Resource ownership.
* Request structure.
* Field values.
* Query parameters.
* Resource identifiers.
* Business rules.

The backend must not trust role information, ownership information, calculated scores, or protected identifiers supplied by the frontend without validation.

### 5.3 Backend to Database Boundary

The Django backend communicates with PostgreSQL for persistent application data.

Database access must occur through approved backend logic.

The backend is responsible for:

* Applying validated queries.
* Enforcing application permissions before database access.
* Associating protected records with the correct user.
* Preventing unrestricted client-controlled database operations.

Database credentials must only be available to authorised backend and deployment processes.

### 5.4 Backend to AI Provider Boundary

The third-party AI provider is outside the GradNavi application trust boundary.

Data returned by the AI provider must be treated as external input.

Before sending a request, the Django backend should:

* Validate the user request.
* Confirm the user has permission to perform the operation.
* Remove personal information that is not required.
* Apply the approved prompt or request structure.
* Protect the AI provider API key.

After receiving a response, the backend should:

* Validate the returned content.
* Apply required application rules.
* Reject unusable or invalid responses.
* Return only approved information to the frontend.

The AI provider must not be trusted to perform GradNavi authorization, scoring, database access, or resource ownership checks.

### 5.5 Deployment and Secret Boundary

Application secrets are supplied through protected deployment or local environment configuration.

The source-code repository must not be treated as a secret store.

Sensitive configuration should cross into the application through approved environment variables or deployment-secret mechanisms.

Examples include:

* Database credentials.
* Django secret values.
* JWT signing secrets.
* AI provider API keys.

### 5.6 Trust Boundary Summary

The main GradNavi trust flow is:

```text
User Input
    |
    v
React Frontend
    |
    | Untrusted API request
    v
Django Backend
    |
    | Validated and authorised operations
    +-------------------+
    |                   |
    v                   v
PostgreSQL          AI Provider
Database            External Service
```

The Django backend acts as the central enforcement point between untrusted client input, protected application data, and external services.

## 6. Authentication Architecture

GradNavi uses Django authentication together with JWT-based API authentication for protected REST API access.

Authentication verifies the identity of the user before protected application functions are accessed.

### 6.1 Account Authentication

User credentials are processed by the Django backend.

The frontend sends authentication requests through the documented REST API.

The Django backend is responsible for:

* Validating submitted credentials.
* Applying the configured password-validation rules.
* Using Django password hashing and authentication mechanisms.
* Issuing authentication tokens after successful login.
* Rejecting invalid authentication attempts.
* Supporting approved password-recovery processes.

Plain-text passwords must not be stored.

### 6.2 JWT Authentication

After successful login, the backend issues JWT credentials according to the approved authentication implementation.

The authentication flow is:

```text"
User
  |
  | Login credentials
  v
React Frontend
  |
  | HTTPS request
  v
Django Authentication
  |
  | Credentials valid
  v
JWT Access and Refresh Tokens
```

The access token is used to authenticate protected API requests.

The refresh token is used to obtain a new access token according to the approved authentication configuration.

### 6.3 Protected API Requests

Protected requests include the access token in the HTTP Authorization header.

Example:

```http
Authorization: Bearer <access_token>
```

For each protected request, the backend should:

1. Verify that authentication credentials are present.
2. Validate the JWT.
3. Identify the authenticated user.
4. Confirm the account is permitted to access the application.
5. Continue to authorization and resource-level permission checks.

An authenticated token does not automatically grant access to every GradNavi resource.

### 6.4 Token Expiry and Refresh

Access tokens should use a limited lifetime.

When an access token expires, the frontend may use the approved refresh-token process to request a replacement access token.

Expired, invalid, revoked, or otherwise unacceptable tokens must not provide access to protected resources.

Final token lifetimes and refresh behaviour should remain aligned with the backend authentication implementation.

### 6.5 Logout

Logout should follow the approved backend authentication implementation.

Where refresh-token invalidation or blacklisting is supported, the backend should invalidate the relevant refresh token during logout.

Frontend removal of a token alone must not be treated as the only security control where server-side invalidation is required by the selected JWT approach.

### 6.6 Password Recovery

GradNavi supports an approved password-recovery process for users who lose account access.

Password-recovery responses should avoid revealing whether a submitted email address belongs to an existing GradNavi account.

Reset credentials must be validated before a new password is accepted.

### 6.7 Current User Identification

The backend should determine the current authenticated user from the validated authentication credentials.

Frontend-supplied user identifiers must not replace backend authentication when determining ownership of protected student data.

For example, the frontend should not be trusted to declare:

```json
{
  "user_id": 25
}
```

as proof that the requesting user owns user 25's profile.

Ownership must be based on the user identified by the validated authentication context.

### 6.8 Authentication Failure Behaviour

Missing, invalid, or expired authentication credentials should produce a controlled authentication error.

Authentication failures must not expose:

* Password hashes.
* Authentication secrets.
* JWT signing secrets.
* Internal stack traces.
* Database queries.
* Detailed information that helps identify valid user accounts.

## 7. Authorization and Access Control

GradNavi uses backend-enforced authorization to control which resources and operations authenticated users are permitted to access.

Authentication identifies the user. Authorization determines what the authenticated user is permitted to do.

### 7.1 Application Roles

GradNavi currently defines two V1 application roles:

* Student.
* Administrator.

The Django backend must enforce role permissions for protected operations.

Frontend interface controls may hide unavailable functions, but they must not replace backend permission checks.

### 7.2 Student Access

Student accounts are permitted to access functions intended for their own career-guidance activities.

These functions may include:

* Viewing and updating their own student profile.
* Viewing their own career recommendations.
* Viewing their own readiness and skill-gap results.
* Managing their own generated documents.
* Managing their own job-description analyses.
* Accessing their own interview preparation records.
* Viewing their own learning suggestions.
* Managing their own career roadmap.
* Viewing their own progress information.

Students must not receive access to Administrator-only operations.

### 7.3 Administrator Access

Administrator accounts are permitted to access approved administration functions.

These functions may include:

* Managing users.
* Managing career reference data.
* Managing skill reference data.
* Managing learning resources.
* Viewing permitted audit information.
* Accessing approved reports.

Administrator permissions must be enforced by the Django backend.

Administrator access should only expose information required for the approved administration function.

### 7.4 Role Enforcement

The backend must determine the authenticated user's role from trusted server-side account information.

Role information supplied by the frontend must not be trusted as proof of authorization.

For example, a request such as:

```json
{
  "role": "administrator"
}
```

must not grant Administrator access.

The backend must use the authenticated user's stored permissions or role information when evaluating access.

### 7.5 Object-Level Permissions

Role authorization alone is not enough for student-owned resources.

The backend must also verify whether the authenticated user is permitted to access the specific requested record.

For example:

```text
Student A
    |
    v
GET /api/v1/documents/42/
```

If document `42` belongs to Student B, the request must not succeed even when Student A has valid authentication.

Object-level permission checks apply to protected student-owned data such as:

* Profiles.
* Recommendations.
* Readiness results.
* Skill-gap results.
* Generated documents.
* Job-description analyses.
* Interview records.
* Learning suggestions.
* Career roadmaps.
* Progress records.

### 7.6 Ownership Determination

Ownership must be determined using trusted backend relationships between the authenticated user and the requested resource.

The backend must not rely on frontend-submitted ownership values.

For example, a client-supplied value such as:

```json
{
  "user_id": 15
}
```

must not be accepted as proof that the requesting user owns resources belonging to user `15`.

The authenticated backend user context should determine ownership.

### 7.7 Administrator Endpoint Protection

Administrator endpoints must require:

1. Valid authentication.
2. An active authorised account.
3. Administrator permission for the requested operation.

A Student attempting to access an Administrator-only endpoint should receive:

```text
403 Forbidden
```

### 7.8 Unauthenticated Access

Requests to protected resources without valid authentication should receive:

```text
401 Unauthorized
```

The distinction between `401 Unauthorized` and `403 Forbidden` must remain consistent across the GradNavi API.

### 7.9 Least Privilege

Users and system components should receive only the permissions required for their approved functions.

Student accounts should not receive administration privileges.

Application components should not receive unrestricted access where narrower access is sufficient.

### 7.10 Access Control Testing

Authorization behaviour should be tested for both permitted and denied access.

Testing should include:

* Student access to their own resources.
* Student attempts to access another student's resources.
* Student attempts to access Administrator endpoints.
* Administrator access to approved administration functions.
* Requests without authentication.
* Requests using invalid or expired authentication.
* Attempts to change role or ownership information through request data.


## 8. Data Protection and Privacy

GradNavi processes personal student information and must protect that information throughout collection, storage, processing, transmission, and deletion.

Privacy controls should follow the principle of data minimisation. The system should collect, store, and share only the information required for approved GradNavi functions.

### 8.1 Personal Information

GradNavi personal information may include:

* Email address.
* Education information.
* Skills.
* Interests.
* Experience.
* Projects.
* Career goals.
* Personality-related responses.
* Job-description submissions.
* Generated documents.
* Interview answers and feedback.
* Career recommendations and readiness results.

Personal information must only be accessed for approved application functions.

### 8.2 Data Minimisation

GradNavi should avoid collecting information that is not required for its defined career-guidance functions.

Where a feature does not require a particular personal attribute, that information should not be requested or processed.

The same principle applies to external AI requests.

### 8.3 Backend Data Access

Persistent student data is stored through the Django backend and PostgreSQL database.

Frontend clients must not receive direct database access.

The backend must apply authentication, authorization, ownership checks, and validation before protected data is retrieved or changed.

### 8.4 Student Data Isolation

A student's protected information must remain isolated from other student accounts.

Backend queries for student-owned resources should be restricted using the authenticated user's trusted identity and ownership relationships.

Changing a resource identifier, request body, or query parameter must not allow access to another student's protected information.

### 8.5 External AI Data Sharing

Before personal information is sent to an external AI provider, the Django backend should remove information that is not required for the requested AI operation.

Examples of information that should not be sent unless required include:

* Authentication credentials.
* Password information.
* JWT tokens.
* Database identifiers unrelated to the task.
* Internal account metadata.
* Unnecessary personal identifiers.

Only the minimum information required to produce the requested AI output should be included.

### 8.6 Data in Transit

Deployed communication carrying authentication information or personal data must use HTTPS.

This includes communication between:

* User browser and frontend.
* Frontend and Django REST API.
* Django backend and external AI services.

### 8.7 Data at Rest

Persistent application data is stored in PostgreSQL.

Database access must be limited to authorised application and administration processes.

Database credentials must remain outside frontend code and committed source files.

The project should rely on the selected hosting platform's approved storage and access controls for the demonstration environment.

### 8.8 Generated Content

Generated resumes, cover letters, recommendation explanations, interview feedback, and other outputs may contain information derived from a student's personal profile.

Generated content must therefore receive appropriate access protection and ownership checks.

AI-generated content should remain reviewable by the student before it is treated as approved saved content.

### 8.9 Logs and Privacy

Application logs and audit records should avoid unnecessary personal information.

Sensitive content should not be logged where the same operational or debugging purpose can be achieved using less sensitive information.

Passwords, tokens, API keys, and authentication secrets must not be logged.

### 8.10 Data Deletion

Where GradNavi supports deletion of student-owned records or profile-deletion requests, the backend must confirm that the requesting user has the required permission before performing the operation.

Deletion behaviour should remain aligned with the approved functional requirements and implemented data model.

### 8.11 Privacy Review

Privacy controls should be reviewed when:

* New personal data fields are introduced.
* New external services are added.
* AI request content changes.
* New reporting or analytics functions are introduced.
* Access-control rules change.
* Data-retention or deletion behaviour changes.

### 8.12 Consent and User Control

GradNavi should obtain clear user consent before processing personal information for career-guidance functions.

Users should be informed about the purpose of the information being collected and how it supports GradNavi functionality.

Where personal information is sent to an external AI provider, only the information required for the requested function should be processed.

Students should retain access to supported controls for updating their information, deleting saved generated content, and requesting deletion of their profile according to the implemented data-management process.

## 9. Secret and Credential Management

GradNavi uses sensitive credentials and configuration values that must be protected from unauthorised access and accidental disclosure.

Secrets must not be stored directly in committed source code.

### 9.1 Protected Secrets

Sensitive GradNavi configuration may include:

* Django secret values.
* PostgreSQL database credentials.
* JWT signing secrets or related authentication configuration.
* AI provider API keys.
* Deployment credentials.
* Other external service credentials introduced during development.

These values must be treated as confidential application secrets.

### 9.2 Environment Variables

Backend secrets should be supplied through environment variables or the approved deployment secret-management mechanism.

During local development, environment-specific values may be loaded from a local `.env` file.

Example:

```text
DJANGO_SECRET_KEY=<secret-value>
DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
AI_API_KEY=<provider-api-key>
```

Real secret values must not appear in documentation examples.

### 9.3 Git Repository Protection

Files containing real secrets must not be committed to the Git repository.

The repository `.gitignore` should exclude local secret files such as:

```text
.env
backend/.env
```

Before committing backend configuration changes, developers should verify that secret files are not staged.

### 9.4 Source Code

Application code should retrieve sensitive configuration from the environment rather than containing hard-coded secret values.

Conceptually:

```text
Django application
        |
        v
Environment configuration
        |
        +---- Database credentials
        |
        +---- Django secret
        |
        +---- AI provider key
```

This separates application logic from environment-specific credentials.

### 9.5 Frontend Secret Protection

Backend secrets must not be included in React source code, frontend configuration delivered to the browser, API responses, or client-side storage.

The AI provider API key and database credentials must remain server-side.

The frontend should communicate with protected services through the Django backend rather than receiving service credentials.

### 9.6 Deployment Secrets

Production or demonstration deployment secrets should be configured through the selected hosting platform's protected environment configuration.

Secrets should not be copied into repository files solely to support deployment.

Local development credentials and deployed credentials should be managed separately where appropriate.

### 9.7 Logging

Secrets must not be written to normal application logs.

Logging should avoid recording:

* Passwords.
* JWT access tokens.
* JWT refresh tokens.
* Database passwords.
* AI provider API keys.
* Django secret values.

### 9.8 Secret Exposure

If a secret is accidentally committed, published, logged, or otherwise exposed, removing the visible value alone should not be treated as sufficient remediation.

The affected credential should be revoked, rotated, or replaced where supported.

Repository history and affected environments should also be reviewed to determine the extent of the exposure.

### 9.9 Development Practices

Before committing configuration-related work, developers should check:

1. Secret files are excluded from Git.
2. No real credentials appear in source code.
3. No real credentials appear in documentation.
4. Environment-variable names are documented where required.
5. Frontend code does not contain backend service credentials.
6. Staged changes do not contain accidental secret values.

## 10. API and Input Security

GradNavi must treat data received through the REST API as untrusted until the Django backend validates and authorizes the request.

Frontend validation improves usability but does not replace backend security controls.

### 10.1 Request Authentication

Protected API endpoints must require valid authentication according to the GradNavi authentication architecture.

The backend must validate the authentication context before processing protected operations.

Missing, invalid, or expired authentication credentials must not provide access to protected resources.

### 10.2 Authorization and Ownership

After authentication, the backend must verify that the user has permission to perform the requested operation.

For student-owned resources, the backend must also verify resource ownership.

Client-supplied user identifiers, roles, or ownership values must not be trusted as proof of access.

### 10.3 Request Body Validation

JSON request bodies must be validated before application logic or database operations are performed.

Validation should include, where applicable:

* Required fields.
* Data types.
* Allowed values.
* String formats.
* Length limits.
* Collection limits.
* Business rules.

Django REST Framework serializers or equivalent backend validation mechanisms should enforce these rules during implementation.

### 10.4 URL and Query Parameter Validation

URL parameters and query parameters must also be treated as untrusted input.

The backend should validate:

* Resource identifiers.
* Pagination values.
* Search values.
* Filtering values.
* Sorting parameters.

Unsupported input must not provide access to unintended application behaviour or protected data.

### 10.5 Server-Controlled Values

Security-sensitive and calculated values should be controlled by the backend.

Examples include:

* User roles.
* Resource ownership.
* Recommendation scores.
* Career-readiness scores.
* Permission decisions.
* Audit information.

The backend must not accept a client-supplied value as authoritative where GradNavi is responsible for calculating or controlling that value.

### 10.6 Database Query Safety

Database operations should use Django's approved database access mechanisms and validated application data.

Raw database queries should be avoided unless there is a documented implementation requirement and appropriate parameter handling is applied.

Frontend clients must not submit executable database commands.

### 10.7 Error Responses

Invalid or rejected requests should return controlled API errors using the documented GradNavi error-response format.

API responses must not expose:

* Stack traces.
* SQL queries.
* Database credentials.
* Environment variables.
* Authentication secrets.
* AI provider credentials.
* Internal server paths.

### 10.8 Request Size and Resource Limits

Endpoints that accept potentially large user input should apply reasonable limits during implementation.

Relevant GradNavi inputs include:

* Job descriptions.
* Profile descriptions.
* Project information.
* Interview answers.
* Generated document content.

Limits should reduce accidental or abusive resource consumption while still supporting the approved feature requirements.

### 10.9 Cross-Origin Access

Cross-origin access to the Django REST API should be limited to approved frontend origins in deployed environments.

Development configuration may permit local frontend origins required by the team.

Production or demonstration configuration should not allow unrestricted origins unless a documented requirement exists.

### 10.10 HTTP Methods

Endpoints should only accept HTTP methods required by their documented function.

For example, an endpoint designed only to retrieve information should not accept modification methods unless those operations are explicitly part of the API contract.

Unsupported methods should be rejected by the backend.

### 10.11 API Security Testing

API security testing should include:

* Requests without authentication.
* Requests with invalid or expired authentication.
* Student attempts to access another student's records.
* Student attempts to access Administrator functions.
* Invalid request bodies.
* Invalid resource identifiers.
* Unsupported HTTP methods.
* Invalid query parameters.
* Attempts to submit protected server-controlled values.
* Checks that error responses do not expose sensitive implementation information.

## 11. AI Service Security

GradNavi uses a third-party AI provider for approved generative functions.

The AI provider is treated as an external service and must not act as the authority for authentication, authorization, resource ownership, database access, or deterministic scoring.

### 11.1 Backend-Only AI Integration

All communication with the AI provider must pass through the Django backend.

The React frontend must not communicate directly with the AI provider.

The intended flow is:

```text
Student
   |
   v
React Frontend
   |
   v
Django Backend
   |
   | Validated and minimised request
   v
AI Provider
   |
   | External response
   v
Django Validation
   |
   v
React Frontend
```

This keeps AI service credentials and security controls on the server side.

### 11.2 AI Credential Protection

AI provider credentials must be stored as protected backend configuration.

The AI API key must not be:

* Included in React source code.
* Returned through API responses.
* Stored in client-side application code.
* Included in URLs.
* Written to normal application logs.
* Committed to the Git repository.

### 11.3 Data Minimisation

Before sending information to the AI provider, the Django backend should determine what information is required for the requested function.

Unnecessary personal information should be removed before the external request is made.

Authentication credentials, JWT tokens, passwords, internal database identifiers, and application secrets must not be included in AI prompts.

### 11.4 Separation of Scoring and AI Generation

The AI provider must not determine GradNavi's numerical career recommendation or career-readiness scores.

Approved backend scoring logic is responsible for deterministic scoring.

The intended separation is:

```text
Student Profile
      |
      v
Backend Scoring Logic
      |
      +---- Numerical score
      |
      v
Approved result
      |
      v
AI Provider
      |
      v
Plain-language explanation
```

This keeps numerical results repeatable and testable while allowing AI to explain approved results.

### 11.5 AI-Generated Content

AI-generated content may support:

* Recommendation explanations.
* Readiness explanations.
* Resume drafts.
* Cover-letter drafts.
* Interview questions.
* Written interview feedback.

Generated content should be presented as editable output for student review where applicable.

AI-generated content must not be represented as verified professional career advice.

### 11.6 AI Response Validation

Responses from the AI provider must be treated as untrusted external input.

Before returning or storing an AI response, the backend should check that the response:

* Was received successfully.
* Uses the expected structure where structured output is required.
* Contains the information required by the requested GradNavi function.
* Does not replace backend-controlled scoring or permission decisions.
* Is suitable for the application operation before further processing.

Invalid or unusable responses should be rejected or handled through the approved error process.

### 11.7 Prompt and Instruction Control

AI requests should use approved backend-controlled prompts or request structures.

User input included in an AI request must not be treated as trusted system instructions.

The backend should keep application instructions separate from user-provided content where supported by the selected AI integration.

### 11.8 AI Service Failure

GradNavi must handle AI provider failures without causing uncontrolled backend errors.

Possible failures include:

* Request timeout.
* Provider unavailability.
* Rate limits.
* Invalid responses.
* Network failures.

Where AI functionality is unavailable, the backend should return a controlled error response.

Failure responses must not expose the AI API key, internal prompts containing sensitive information, stack traces, or provider credentials.

### 11.9 AI Output and User Responsibility

AI-generated resumes, cover letters, explanations, interview feedback, and similar outputs should remain reviewable by the student.

The student should review generated material before relying on or using the content externally.

GradNavi outputs are advisory and must not be presented as guaranteed employment outcomes or verified professional career advice.

### 11.10 AI Security Testing

AI integration testing should include:

* Requests without required authorization.
* Requests containing invalid input.
* AI provider timeout behaviour.
* Invalid or unexpected AI responses.
* Checks that unnecessary personal information is not intentionally included in AI requests.
* Checks that AI credentials are not exposed to the frontend.
* Checks that AI output cannot override backend authorization or scoring decisions.
* Controlled handling of unavailable AI services.
* Checks for unsupported claims in generated outputs.
* Checks for unfair bias in generated outputs.
* Checks that protected attributes are not used as direct scoring factors.

## 12. Logging and Audit

GradNavi should maintain appropriate application logging and audit records to support debugging, security investigation, testing, and accountability.

Logging and audit mechanisms must avoid unnecessary collection of sensitive information.

### 12.1 Application Logging

The Django backend should record relevant technical events required to operate and troubleshoot the application.

Examples may include:

- Application errors.
- Database connection failures.
- AI provider failures.
- External service timeouts.
- Authentication failures.
- Unexpected backend exceptions.
- Important service startup or configuration failures.

Logs should provide enough context for investigation without exposing protected credentials or unnecessary personal information.

### 12.2 Security-Relevant Events

Security-relevant events should be recorded where appropriate.

Examples may include:

- Failed authentication attempts.
- Rejected authorization attempts.
- Administrator actions.
- Password-related security events.
- Rejected access to protected resources.
- Significant account-security changes.

The exact events recorded should remain aligned with the implemented authentication, administration, and audit models.

### 12.3 Administrative Audit Records

Important Administrator operations should create appropriate audit records where required by the implemented administration design.

Relevant actions may include:

- User-management changes.
- Career reference-data changes.
- Skill reference-data changes.
- Learning-resource changes.
- Other security-relevant administration operations.

Audit records should provide enough information to identify the action, responsible account, affected resource, and time of the event where appropriate.

### 12.4 Protected Information in Logs

Application logs and audit records must not intentionally store sensitive credentials.

The following information must not be written to normal logs:

- Plain-text passwords.
- Password hashes.
- JWT access tokens.
- JWT refresh tokens.
- Database passwords.
- AI provider API keys.
- Django secret values.
- Password-reset credentials.

Unnecessary student profile information should also be excluded from logs.

### 12.5 Error Logging

Detailed technical errors should be recorded on the backend where required for debugging.

Normal API clients should receive controlled error responses rather than internal exception details.

For example:

```text
Internal backend log:
AI provider request timed out during document generation.

API response:
503 Service Unavailable
```
### 12.6 Audit Record Protection

Audit records must be protected from unauthorised access and modification.

Student accounts must not receive unrestricted access to administrative audit information.

Access to audit records should follow the approved Administrator permissions.

### 12.7 Logging and Privacy

Logging should follow the same data-minimisation principles used elsewhere in GradNavi.

Where an event can be investigated without recording personal content, the less sensitive representation should be preferred.

For example, recording a resource identifier and event type may be more appropriate than recording the full contents of a student's resume or interview response.

### 12.8 Log and Audit Review

Logging and audit behaviour should be reviewed when:

- New authentication functions are introduced.
- New Administrator operations are added.
- New external services are integrated.
- AI processing changes.
- New sensitive data is introduced.
- Security testing identifies missing or excessive logging.

## 13. Deployment and Communication Security

GradNavi deployment should protect application communication, backend services, database access, and environment-specific configuration.

The planned deployment architecture uses Vercel for the React frontend and Railway for the Django backend and PostgreSQL database.

### 13.1 Deployment Architecture

The planned deployed application flow is:

    Student / Administrator
            |
            | HTTPS
            v
    React Frontend
         Vercel
            |
            | HTTPS REST API
            v
    Django Backend
         Railway
          /     \
         v       v
    PostgreSQL   AI Provider
     Railway     External API

Security controls must remain enforced by the Django backend regardless of where the frontend is hosted.

### 13.2 HTTPS

Deployed communication carrying authentication information, personal information, or application data must use HTTPS.

HTTPS should protect communication between:

- User browsers and the deployed frontend.
- React frontend and Django REST API.
- Django backend and supported external services.

Authentication tokens and sensitive student information must not be intentionally transmitted through unencrypted production HTTP connections.

### 13.3 Frontend Deployment

The deployed React frontend must contain only configuration intended for browser access.

Backend secrets must not be included in frontend source code or browser-accessible environment configuration.

The frontend must not contain:

- Database credentials.
- Django secret values.
- JWT signing secrets.
- AI provider API keys.
- Backend administration credentials.

### 13.4 Backend Deployment

The Django backend should use environment-specific deployment configuration.

Deployed secrets should be supplied through Railway's protected environment configuration or another approved deployment-secret mechanism.

Production or demonstration configuration should not depend on local `.env` files being committed to the repository.

### 13.5 Database Access

The PostgreSQL database must not be exposed to frontend clients.

Application database access should occur through the Django backend.

Database credentials should only be available to authorised backend and deployment processes.

Where the hosting environment provides private or restricted database connectivity, the deployment should use the appropriate supported configuration.

### 13.6 Cross-Origin Configuration

The deployed Django API should allow cross-origin requests only from approved frontend origins required by GradNavi.

Development environments may allow approved local development origins such as the React development server.

Deployed configuration should identify the intended GradNavi frontend origin rather than allowing unrestricted origins without a documented requirement.

### 13.7 Django Deployment Configuration

Django deployment settings should be reviewed before the deployed environment is treated as ready for demonstration or testing.

Relevant configuration includes:

- Debug mode.
- Allowed hosts.
- Cross-origin configuration.
- Secret management.
- Database configuration.
- Authentication configuration.
- HTTPS-related security settings where supported by the deployment environment.

Detailed values should remain environment-specific rather than being hard-coded into the security architecture.

### 13.8 Debug Information

Debug information intended for development must not be exposed through the deployed application.

Production or demonstration API responses must not reveal:

- Stack traces.
- Environment variables.
- Database configuration.
- Secret values.
- Internal file paths.
- Detailed framework debugging pages.

### 13.9 Environment Separation

Local development and deployed environments should use separate environment-specific configuration where appropriate.

#### Local Development

- Local environment variables.
- Local frontend origin.
- Development database configuration.

#### Deployed Environment

- Railway environment variables.
- Approved Vercel origin.
- Deployed PostgreSQL configuration.

Local credentials should not automatically become deployed credentials.

### 13.10 External Service Communication

Requests from Django to the AI provider should use the provider's supported secure HTTPS interface.

External service credentials must remain on the backend.

External service failures should use the controlled error-handling behaviour defined by the GradNavi REST API design.

### 13.11 Deployment Review

Before deployment, the team should verify:

1. Debug mode is configured appropriately.
2. Secrets are not committed to Git.
3. Required environment variables are configured.
4. Database credentials are protected.
5. The frontend does not contain backend secrets.
6. Approved frontend origins are configured.
7. Protected API endpoints require authentication.
8. HTTPS is used for deployed application communication.
9. Error responses do not expose internal debugging information.
10. AI provider credentials remain server-side.


## 14. Security Testing and Review

GradNavi security controls should be tested throughout development and reviewed before the system is treated as ready for demonstration or deployment.

Security testing should verify both successful access and rejected access.

### 14.1 Authentication Testing

Authentication testing should verify:

- Valid users are able to authenticate successfully.
- Invalid credentials are rejected.
- Protected endpoints reject unauthenticated requests.
- Invalid JWT access tokens are rejected.
- Expired JWT access tokens are rejected.
- Refresh-token behaviour follows the approved authentication implementation.
- Logout behaviour follows the approved authentication implementation.
- Password-reset processes reject invalid reset credentials.
- Authentication errors do not expose sensitive account information.

### 14.2 Authorization Testing

Authorization testing should verify:

- Students access permitted Student functions.
- Students cannot access Administrator-only endpoints.
- Administrator functions require the appropriate permissions.
- Frontend-supplied role values cannot grant additional permissions.
- Protected operations enforce backend authorization.

### 14.3 Object-Level Permission Testing

Student-owned resources require specific ownership tests.

Testing should verify:

- A student can access their own permitted resources.
- A student cannot access another student's protected resources.
- Changing a resource identifier does not bypass ownership controls.
- Changing a user identifier in a request does not transfer resource ownership.
- Backend queries use the authenticated user context where ownership applies.

These tests should cover applicable resources such as profiles, generated documents, recommendations, interview records, roadmaps, and progress information.

### 14.4 Input Validation Testing

API input testing should include:

- Missing required fields.
- Incorrect data types.
- Invalid field formats.
- Unsupported values.
- Excessively long input where limits apply.
- Invalid resource identifiers.
- Invalid pagination parameters.
- Invalid filtering and sorting parameters.
- Attempts to submit backend-controlled values.
- Unexpected request fields where relevant.

Invalid input should produce controlled API responses and must not cause unintended database or application behaviour.

### 14.5 Secret Protection Testing

Before commits and deployment, the team should verify:

- `.env` files containing real secrets are excluded from Git.
- Database credentials are not present in committed source code.
- AI provider API keys are not present in frontend code.
- JWT secrets are not exposed to clients.
- Secret values are not included in documentation.
- Application logs do not expose protected credentials.

### 14.6 AI Integration Testing

AI security testing should verify:

- AI requests pass through the Django backend.
- AI credentials are not exposed to the frontend.
- Unnecessary personal information is excluded from AI requests.
- Invalid AI responses are handled safely.
- AI provider failures return controlled errors.
- AI-generated content does not override backend authorization.
- AI-generated content does not replace deterministic backend scoring.
- Generated outputs remain reviewable by the student where applicable.

### 14.7 Error Handling Testing

Testing should verify that unexpected failures do not expose sensitive implementation information.

API clients must not receive:

- Stack traces.
- Database credentials.
- SQL queries.
- Environment variables.
- Secret values.
- AI provider credentials.
- Internal server file paths.

Controlled error responses should follow the GradNavi REST API design.

### 14.8 Deployment Security Review

Before deployment or project demonstration, the team should review:

1. Django debug configuration.
2. Allowed hosts.
3. Cross-origin configuration.
4. HTTPS configuration.
5. Environment variables.
6. Database access.
7. Authentication configuration.
8. Administrator permissions.
9. AI provider credentials.
10. Error handling.
11. Logging behaviour.
12. Frontend configuration for exposed secrets.

### 14.9 Security Regression Testing

Security tests should be repeated when changes affect:

- Authentication.
- Authorization.
- User roles.
- Student-owned resources.
- Database models.
- REST API endpoints.
- AI integration.
- External services.
- Deployment configuration.
- Secret management.

A previously tested security control should not be assumed to remain valid after related implementation changes.

### 14.10 Security Review and Change Control

The Security Architecture should be reviewed when a development change introduces a new security requirement, trust boundary, protected asset, external service, user role, or sensitive data type.

Where implementation differs from this design, the team should review the difference and update either the implementation or this document so both remain aligned.

Security-related changes that affect approved project requirements should follow the project's requirement change-control process.

### 14.11 Security Evidence

Where practical, the team should retain evidence of important security testing for project verification and reporting.

Evidence may include:

- Automated test results.
- API test results.
- Permission test results.
- Screenshots of approved test outcomes.
- Test-case documentation.
- Pull request reviews.
- Relevant issue or task records.

Sensitive credentials or personal information must not be included in retained testing evidence.