# GradNavi Authentication API Testing Guide

## 1. Purpose

This guide explains how to manually test the completed GradNavi V1 authentication API using tools such as Postman, curl, or a React frontend client.

It is intended for backend developers, frontend developers, reviewers, and team members performing regression testing. It documents the current implemented behaviour and the API contract used by the authentication test suite.

## 2. Prerequisites

Before testing, ensure:

- The Django backend is running locally.
- The database has been migrated.
- The authentication migrations, including SimpleJWT blacklist migrations, have been applied.
- Test users use safe fictional addresses such as `student1@gradnavi.test`.
- No real credentials, production secrets, or personal information are used in manual tests.

Example local base URL:

```text
http://127.0.0.1:8000
```

## 3. Base URL and API Conventions

All implemented authentication endpoints use the GradNavi V1 API base path:

```text
/api/v1/auth/
```

Requests and responses use JSON. Protected endpoints use JWT access tokens in the `Authorization` header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Do not send JWTs in query parameters.

## 4. Authentication API Summary

| Method | Endpoint | Purpose | Authentication | Success status |
| ------ | -------- | ------- | -------------- | -------------- |
| POST | `/api/v1/auth/register/` | Create a student account | Not required | `201 Created` |
| POST | `/api/v1/auth/login/` | Authenticate and issue JWTs | Not required | `200 OK` |
| POST | `/api/v1/auth/token/refresh/` | Rotate refresh token and issue a new access token | Refresh token in body | `200 OK` |
| GET | `/api/v1/auth/me/` | Return the authenticated user's safe account details | Bearer access token required | `200 OK` |
| POST | `/api/v1/auth/logout/` | Blacklist the submitted refresh token | Bearer access token required | `200 OK` |
| POST | `/api/v1/auth/password/reset/` | Request password reset email | Not required | `200 OK` |
| POST | `/api/v1/auth/password/reset/confirm/` | Confirm password reset and set a new password | Reset UID and token in body | `200 OK` |

Legacy `/api/auth/...` routes are not registered.

## 5. Test Data Setup

Use a unique email for each manual run to avoid duplicate-email conflicts:

```text
student1@gradnavi.test
student2@gradnavi.test
reset@gradnavi.test
```

Use strong test passwords that satisfy Django password validators:

```text
RiverStone#8462Cloud
MountainLake#7391
```

Do not use real passwords.

## 6. Registration Tests

Purpose: create a new public student account.

```http
POST /api/v1/auth/register/
Content-Type: application/json
```

Example request:

```json
{
  "email": "student1@gradnavi.test",
  "password": "RiverStone#8462Cloud",
  "password_confirm": "RiverStone#8462Cloud",
  "first_name": "Test",
  "last_name": "Student"
}
```

Expected success: `201 Created`

Example success response:

```json
{
  "id": 1,
  "email": "student1@gradnavi.test",
  "first_name": "Test",
  "last_name": "Student",
  "role": "student"
}
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Valid registration | `201 Created`; safe user fields returned |
| Password storage | Password is hashed by Django; plaintext password is never returned |
| Default role | Created user has `role: "student"` |
| Duplicate email | `409 Conflict` |
| Case-insensitive duplicate email | `409 Conflict` |
| Missing `email`, `password`, `password_confirm`, `first_name`, or `last_name` | `400 Bad Request` |
| Password mismatch | `400 Bad Request` |
| Weak password | `400 Bad Request` |
| Request includes `role: "admin"`, `is_staff: true`, or `is_superuser: true` | Public registration must not create privileged accounts; current implementation ignores privileged escalation and creates a normal student |

Security expectation: public registration cannot create staff, superuser, or admin privileges.

## 7. Login Tests

Purpose: authenticate with email and password and receive SimpleJWT tokens.

```http
POST /api/v1/auth/login/
Content-Type: application/json
```

Example request:

```json
{
  "email": "student1@gradnavi.test",
  "password": "RiverStone#8462Cloud"
}
```

Expected success: `200 OK`

Example success response:

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>",
  "user": {
    "id": 1,
    "email": "student1@gradnavi.test",
    "first_name": "Test",
    "last_name": "Student",
    "role": "student"
  }
}
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Correct email and password | `200 OK`; access token, refresh token, and safe user object returned |
| Email case differs from stored email | Login succeeds case-insensitively |
| Wrong password | `401 Unauthorized` |
| Nonexistent email | `401 Unauthorized` |
| Wrong password vs nonexistent email | Same generic failure style; response must not reveal whether the email exists |
| Missing `email` or `password` | `400 Bad Request` |
| Inactive user | `401 Unauthorized` |
| Response leakage check | No password, password hash, `is_staff`, or `is_superuser` in response |

## 8. Token Refresh Tests

Purpose: use a valid refresh token to obtain a new access token and rotated refresh token.

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json
```

Example request:

```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

Expected success: `200 OK`

Example success response:

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

Refresh rotation workflow:

```text
Refresh A
   |
   v
POST /api/v1/auth/token/refresh/
   |
   v
Access B + Refresh B
   |
   v
Refresh A becomes invalid
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Valid refresh token | `200 OK`; new access token returned |
| Refresh rotation | New refresh token returned |
| Compare old and new refresh tokens | Rotated refresh token differs from original |
| Reuse original refresh token after rotation | `401 Unauthorized` |
| Use rotated refresh token for another refresh | `200 OK` |
| Malformed refresh token | `401 Unauthorized` |
| Access token submitted as `refresh` | `401 Unauthorized` |
| Missing `refresh` field | `400 Bad Request` |

Current JWT settings:

- Access token lifetime: 15 minutes.
- Refresh token lifetime: 7 days.
- Refresh token rotation: enabled.
- Blacklist after rotation: enabled.

## 9. Current User (`/me/`) Tests

Purpose: retrieve the authenticated user's safe account details.

```http
GET /api/v1/auth/me/
Authorization: Bearer <ACCESS_TOKEN>
```

In Postman:

1. Open the Authorization tab.
2. Select `Bearer Token`.
3. Paste `<ACCESS_TOKEN>` into the token field.

Expected success: `200 OK`

Example success response:

```json
{
  "id": 1,
  "email": "student1@gradnavi.test",
  "first_name": "Test",
  "last_name": "Student",
  "role": "student"
}
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Valid access token | `200 OK`; safe current-user fields returned |
| Missing Authorization header | `401 Unauthorized` |
| Malformed access token | `401 Unauthorized` |
| Refresh token used as Bearer token | `401 Unauthorized` |
| Different user's access token | Response represents that authenticated user |
| Response leakage check | No password, refresh token, `is_staff`, `is_superuser`, groups, or permissions |

Email/password JSON in the body of this GET request does not authenticate `/me/`. Authentication comes only from DRF/SimpleJWT processing the Bearer access token.

## 10. Logout Tests

Purpose: end the refresh-token session by blacklisting the submitted refresh token.

```http
POST /api/v1/auth/logout/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Example request:

```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

Expected success: `200 OK`

Example success response:

```json
{
  "message": "Logged out successfully."
}
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Valid Bearer access token and valid refresh token | `200 OK`; submitted refresh token is blacklisted |
| Use logged-out refresh token at `/token/refresh/` | `401 Unauthorized` |
| Missing Bearer authentication | `401 Unauthorized` |
| Malformed Bearer token | `401 Unauthorized` |
| Missing `refresh` field | `400 Bad Request` |
| Malformed refresh token | `401 Unauthorized` |
| Access token supplied in `refresh` field | `401 Unauthorized` |
| Already-blacklisted refresh token submitted again | `401 Unauthorized` |

Important JWT behaviour:

```text
Logout
  |-- refresh token -> blacklisted
  `-- existing access token -> remains usable until normal expiry
```

The existing access token remaining valid until its 15-minute expiry is expected under the current stateless JWT architecture. This is not a logout defect.

## 11. Password Reset Request Tests

Purpose: start account recovery without revealing whether the email belongs to an account.

```http
POST /api/v1/auth/password/reset/
Content-Type: application/json
```

Example request:

```json
{
  "email": "student1@gradnavi.test"
}
```

Expected success: `200 OK`

Example success response:

```json
{
  "message": "If the email is registered, a password reset email has been sent."
}
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Registered active email | `200 OK`; one password reset email is sent |
| Unknown email | Same `200 OK` response; no email is sent |
| Compare registered vs unknown response | Same public response; no account enumeration |
| Missing email | `400 Bad Request` |
| Malformed email | `400 Bad Request` |
| API response leakage check | Response does not expose UID or reset token |

The UID and reset token are delivered through Django's email infrastructure, not through the API response.

Current development email behaviour uses Django email configuration. Production SMTP/provider configuration is not defined in this task.

## 12. Password Reset Confirm Tests

Purpose: verify password reset credentials and set a new password.

```http
POST /api/v1/auth/password/reset/confirm/
Content-Type: application/json
```

Implemented request fields:

```json
{
  "uid": "<RESET_UID>",
  "token": "<RESET_TOKEN>",
  "password": "<NEW_STRONG_PASSWORD>",
  "password_confirm": "<NEW_STRONG_PASSWORD>"
}
```

Expected success: `200 OK`

Example success response:

```json
{
  "message": "Password has been reset successfully."
}
```

Manual checks:

| Case | Expected result |
| ---- | --------------- |
| Valid UID, token, and strong matching password | `200 OK`; password is changed |
| Weak password | `400 Bad Request` |
| Password mismatch | `400 Bad Request` |
| Missing `uid`, `token`, `password`, or `password_confirm` | `400 Bad Request` |
| Malformed UID | `401 Unauthorized` |
| Invalid token | `401 Unauthorized` |
| Expired token | `401 Unauthorized` |
| Reuse token after successful reset | `401 Unauthorized` |

Verification sequence:

```text
Request reset
    |
    v
Receive UID + reset token
    |
    v
Confirm new password
    |
    v
Old password login -> rejected
New password login -> succeeds
Same reset token -> rejected
```

Django password validators apply to the new password. The backend saves the password using Django password hashing, not by assigning plaintext directly.

## 13. Complete End-to-End Authentication Flow

Recommended manual flow:

```text
Register
   |
   v
Login
   |
   v
/me/
   |
   v
Token Refresh
   |
   v
Logout
   |
   v
Confirm old refresh token rejected

Password Reset Request
   |
   v
Reset Confirm
   |
   v
Old password rejected
   |
   v
New password accepted
   |
   v
Reset token reuse rejected
```

Use the access token from login for `/me/` and logout. Use the refresh token from login for refresh and logout tests.

## 14. Standard Error Response

Authentication errors use the GradNavi reusable DRF error envelope:

```json
{
  "error": {
    "code": "<ERROR_CODE>",
    "message": "<SAFE_MESSAGE>",
    "details": {}
  }
}
```

Representative implemented examples:

Validation error:

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

Duplicate email:

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

Invalid login credentials:

```json
{
  "error": {
    "code": "invalid_credentials",
    "message": "Unable to log in with the provided credentials.",
    "details": {}
  }
}
```

Authentication required:

```json
{
  "error": {
    "code": "not_authenticated",
    "message": "Authentication credentials were not provided.",
    "details": {}
  }
}
```

Invalid JWT:

```json
{
  "error": {
    "code": "token_not_valid",
    "message": "Token is invalid or expired",
    "details": {}
  }
}
```

Invalid or expired password reset token:

```json
{
  "error": {
    "code": "invalid_reset_token",
    "message": "Password reset credentials are invalid or expired.",
    "details": {}
  }
}
```

## 15. Security Test Checklist

Use this checklist during manual review:

- Passwords are hashed and never returned.
- Password hashes are never returned.
- Public registration cannot create privileged users.
- Public registration defaults to `student`.
- Login does not reveal whether an account exists.
- Password reset request does not reveal whether an email exists.
- Password reset UID/token are not returned by the API response.
- Password reset token cannot be reused after password change.
- Django password validators reject weak passwords.
- JWT access tokens are required for `/me/`.
- Refresh token rotation is enabled.
- Old refresh tokens are blacklisted after rotation.
- Logout blacklists the submitted refresh token.
- Existing access token remains valid only until normal expiry after logout.
- Error responses use the standard safe GradNavi envelope.

## 16. Automated Test Suite

At the Task 9 checkpoint, the accounts authentication suite contains 60 passing tests.

Useful commands:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test accounts
```

What they verify:

- `python manage.py check`: Django configuration and system checks.
- `python manage.py makemigrations --check`: confirms no model changes require migrations.
- `python manage.py test accounts`: runs the authentication account tests, including registration, login, refresh, `/me/`, logout, and password reset.

These commands were not rerun for this documentation-only task.

## 17. Postman Testing Tips

- Set a collection variable for the local base URL, for example `base_url = http://127.0.0.1:8000`.
- Use `{{base_url}}/api/v1/auth/register/` style URLs.
- Store returned `access` and `refresh` values in Postman variables.
- For `/me/` and logout, use Postman's Authorization tab:
  - Type: `Bearer Token`
  - Token: `<ACCESS_TOKEN>`
- Do not place tokens in query parameters.
- For token refresh and logout, send the refresh token in the JSON request body.
- When testing password reset, retrieve the UID/token from the development email output, not from the API response.

## 18. Development vs Production Notes

Current development behaviour:

- Password reset email is sent through Django's configured email infrastructure.
- The current settings use a development-compatible console mail backend configuration.
- Password reset emails include UID/token information and a development reset path.
- The production frontend password-reset URL/page is not yet defined in the API contract.

Production follow-up:

- Configure a production email backend/provider through environment-based settings.
- Define the frontend password-reset page and final reset-link format.
- Keep JWT signing keys, database credentials, email credentials, and other secrets out of source control.
- Do not commit `.env` values or real tokens.

## 19. Quick Regression Checklist

Before handing off authentication changes, verify:

- `POST /api/v1/auth/register/` creates a student and rejects duplicates.
- `POST /api/v1/auth/login/` returns access, refresh, and safe user information.
- Wrong password and nonexistent email return the same safe login failure style.
- `POST /api/v1/auth/token/refresh/` rotates refresh tokens and blacklists the old token.
- `GET /api/v1/auth/me/` requires a Bearer access token and returns safe user fields only.
- `POST /api/v1/auth/logout/` requires Bearer authentication and blacklists the submitted refresh token.
- `POST /api/v1/auth/password/reset/` prevents account enumeration.
- `POST /api/v1/auth/password/reset/confirm/` changes the password and prevents reset-token reuse.
- Legacy `/api/auth/...` routes are not registered.

## 20. Known Notes / Contract Differences

- `docs/system-design/rest-api-design.md` defines the authentication endpoint paths and expected statuses but leaves some response bodies and detailed request fields to implementation.
- Password reset confirm currently uses `uid`, `token`, `password`, and `password_confirm`.
- Logout success is implemented as `200 OK` with `{ "message": "Logged out successfully." }`, which is allowed by the REST design because it permits `200 OK` or `204 No Content`.
- The production password-reset frontend URL and email provider are not yet specified.
