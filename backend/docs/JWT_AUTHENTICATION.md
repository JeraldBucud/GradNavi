# GradNavi JWT Authentication Rules

## Purpose

This document defines the shared JWT authentication rules for the
GradNavi REST API. Backend and frontend developers should use it as the
authentication integration reference.

## Authentication Method

GradNavi uses Django REST Framework with SimpleJWT.

-   Login identity: **email + password**
-   Access token: JWT
-   Refresh token: JWT
-   Protected-request header: `Authorization: Bearer <access_token>`
-   Username is not used as the login identity.

## User Roles

V1 supports `student` and `admin`.

Public registration creates a `student`. The frontend must not be able
to self-assign `admin`; administrator access must only be granted
through an authorised backend/admin process.

## Authentication Endpoints

  -------------------------------------------------------------------------------------------
  Method            Endpoint                              Access            Purpose
  ----------------- ------------------------------------- ----------------- -----------------
  POST              `/api/v1/auth/register/`              Public            Create a student
                                                                            account

  POST              `/api/v1/auth/login/`                 Public            Login with
                                                                            email/password
                                                                            and issue JWT
                                                                            tokens

  POST              `/api/v1/auth/token/refresh/`         Refresh token     Obtain new
                                                                            token(s)

  GET               `/api/v1/auth/me/`                    Access token      Get the current
                                                                            authenticated
                                                                            user

  POST              `/api/v1/auth/logout/`                Auth/refresh as   Invalidate the
                                                          implemented       supplied refresh
                                                                            token

  POST              `/api/v1/auth/password/reset/`        Public            Start password
                                                                            recovery

  POST              `/api/v1/auth/password/reset/confirm/` Reset token      Complete password
                                                                            reset
  -------------------------------------------------------------------------------------------

Coordinate any endpoint-path change with the team before changing the
implementation.

## Current JWT Configuration

-   Access-token lifetime: **15 minutes**
-   Refresh-token lifetime: **7 days**
-   Refresh-token rotation: **enabled**
-   Blacklist after rotation: **enabled**
-   Header type: **Bearer**
-   Algorithm: **HS256**
-   User identifier claim: `user_id`
-   `UPDATE_LAST_LOGIN`: disabled

The backend signing secret must never be exposed to React or committed
as a public secret.

## Login

Conceptual request:

``` json
{
  "email": "student@example.com",
  "password": "StrongPassword123!"
}
```

A successful login will return access and refresh tokens according to
the final serializer contract:

``` json
{
  "access": "<jwt-access-token>",
  "refresh": "<jwt-refresh-token>"
}
```

The backend remains the authority for authentication and permissions.
Frontend-decoded JWT data must not be treated as a replacement for
backend authorization.

## Using the Access Token

Send the access token with every protected API request:

``` http
Authorization: Bearer <access_token>
```

Example:

``` http
GET /api/v1/auth/me/
Authorization: Bearer eyJ...
```

Do not put tokens in URLs, GitHub, logs, documentation examples
containing real credentials, or shared screenshots.

## Refresh Token Rules

When the access token expires, the frontend uses the refresh token with:

`POST /api/v1/auth/token/refresh/`

Conceptual body:

``` json
{
  "refresh": "<refresh_token>"
}
```

Because refresh-token rotation is enabled, the frontend must replace its
stored refresh token when a successful refresh response returns a new
one. The previous token may be blacklisted.

If refresh fails because the token is invalid, expired, or blacklisted,
clear the authentication state and require login again.

## Logout

The logout endpoint will blacklist/invalidate the relevant refresh
token.

After successful logout, the frontend must clear its authentication
state.

An already-issued access token normally remains valid until it expires
unless additional revocation logic is introduced. The short 15-minute
access lifetime limits this window.

## Protected API Rules

The backend must enforce:

-   authentication;
-   student/admin role permissions;
-   object ownership;
-   student-data isolation.

Hiding a button or route in React is not an authorization control.

A student must not gain access to another student's private record
simply by changing an ID in a URL or request body.

## Registration Security

Public registration must:

-   create `student` users only;
-   reject/prevent public admin self-assignment;
-   validate unique email;
-   validate passwords;
-   use Django password hashing;
-   never return a password or stored password value.

Passwords must never be stored as plaintext or manually hashed by React.

## Frontend Integration Rules

React developers should:

1.  Use the agreed `/api/v1/auth/...` endpoints.
2.  Login with email + password.
3.  Send access tokens as `Authorization: Bearer <access_token>`.
4.  Refresh when the access token expires.
5.  Replace rotated refresh tokens when returned.
6.  Clear authentication state when refresh fails.
7.  Clear authentication state on logout.
8.  Never put backend signing/API secrets in frontend source or
    environment variables.
9.  Never rely on frontend role checks as the security boundary.
10. Handle `401 Unauthorized` separately from `403 Forbidden`.

The final browser token-storage strategy should be agreed before
production deployment. Convenient development storage must not
automatically be treated as the final security design.

## HTTP Status Guidance

Typical authentication responses:

-   `200 OK` --- successful login, refresh, logout, or authenticated
    retrieval as appropriate
-   `201 Created` --- successful registration
-   `400 Bad Request` --- validation/request failure
-   `401 Unauthorized` --- missing, invalid, expired, or unacceptable
    authentication
-   `403 Forbidden` --- authenticated user lacks permission

Exact response bodies will be defined by the implemented API contract.

## Backend Rules

Backend developers must:

-   keep JWT signing secrets server-side;
-   use DRF authentication and permission mechanisms;
-   enforce role and object-level authorization;
-   avoid logging complete tokens;
-   test invalid, expired, blacklisted, and unauthorized cases;
-   keep authentication paths and token behaviour aligned with this
    document.

## Current Implementation Status

Configured:

-   Custom `accounts.User`
-   Email-based authentication identity
-   Student/Admin roles
-   Django REST Framework
-   SimpleJWT
-   `JWTAuthentication`
-   15-minute access tokens
-   7-day refresh tokens
-   Refresh-token rotation
-   Token blacklist support

Still to implement/test:

-   Registration API
-   Login API
-   Refresh endpoint routing
-   `/api/v1/auth/me/`
-   Logout API
-   Password-reset APIs
-   Full automated authentication tests
-   React authentication integration

## Change Control

This document is the shared GradNavi JWT authentication reference. If
token behaviour, endpoint paths, roles, or authentication flow change,
update this document and communicate the change to the team before
frontend/backend integration.
