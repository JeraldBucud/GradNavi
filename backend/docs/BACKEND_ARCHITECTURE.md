# GradNavi Backend Architecture

## 1. Purpose

GradNavi is an AI-powered career guidance web application for students
approaching graduation. The backend provides secure REST APIs for
profile management, deterministic career recommendations and readiness
scoring, skill-gap analysis, job-description matching, AI-assisted
content generation, administration, deletion, audit records, and
reporting.

The backend is implemented with Django REST Framework and PostgreSQL and
is consumed by a separate React frontend.

## 2. Architectural Principles

1.  **REST-first backend** --- Django returns JSON APIs; React owns the
    user interface.
2.  **PostgreSQL persistence** --- application data is stored through
    Django ORM.
3.  **JWT authentication** --- protected APIs require authenticated
    access and appropriate permissions.
4.  **Deterministic scoring** --- recommendation and readiness scores
    use documented weighted rules. The same structured input must
    produce the same numerical result.
5.  **Limited AI role** --- generative AI explains results and generates
    editable text; it does not independently determine numerical
    recommendation/readiness scores.
6.  **Backend-only AI integration** --- AI API keys, prompts,
    validation, timeouts, and error handling remain server-side.
7.  **Privacy by design** --- collect and process only required personal
    information and enforce object-level ownership.
8.  **Modularity** --- separate authentication, profiles, career data,
    scoring, matching, AI services, administration, and audit concerns.
9.  **Testability** --- priority behaviour must be testable through
    unit, API, permission, integration, and acceptance tests.

## 3. High-Level Architecture

``` text
Student / Administrator
          |
          v
     Web Browser
          |
          v
    React Frontend
     (Vercel)
          |
       HTTPS/JSON
          |
          v
Django REST Framework
          |
          +-- Authentication / JWT / Permissions
          +-- Student Profile APIs
          +-- Career & Skill APIs
          +-- Recommendation Engine
          +-- Readiness & Skill-Gap Engine
          +-- Job Matching
          +-- AI Service
          +-- Resume / Cover Letter
          +-- Interview Preparation
          +-- Learning / Roadmap
          +-- Administration / Analytics
          +-- Audit / Error Handling
          |
          +--------------------+
          |                    |
          v                    v
     PostgreSQL            OpenAI API
   Local / Railway      controlled backend calls
```

## 4. Backend Project Structure

The exact app split may evolve during implementation, but business
domains should remain separated.

``` text
backend/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── gradnavi/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
├── profiles/
├── careers/
├── recommendations/
├── jobs/
├── documents/
├── interviews/
├── roadmaps/
├── audit/
└── docs/
```

Do not create empty Django apps merely to match this diagram. Create an
app when its domain is ready to be implemented.

## 5. Layer Responsibilities

### API Layer

DRF views/viewsets receive HTTP requests, enforce
authentication/permissions, call serializers/services, and return JSON
responses with appropriate status codes.

### Serialization and Validation Layer

Serializers convert between JSON and Python/model objects, validate
input, and control which fields can be returned or changed.

### Service / Business Logic Layer

Non-trivial business rules belong in focused services rather than
oversized views. This includes recommendation scoring, readiness
scoring, skill-gap calculations, job matching, AI orchestration, and
document-generation workflows.

### Domain / ORM Layer

Django models define persisted entities and relationships. PostgreSQL
schema changes are made using Django migrations.

### External Service Layer

AI calls are made only from backend services. The service layer controls
prompts, data minimisation, timeout/failure behaviour, validation, and
logging.

## 6. Data Model and ERD Status

The ERD submitted in Assessment 1 is a **first-level conceptual draft**,
not the final implementation schema. It is useful for understanding the
original domain concepts, but Django models and the final PostgreSQL
schema must not be forced to reproduce it exactly.

The final implementation model should be driven primarily by: 1.
functional requirements; 2. non-functional requirements; 3. agreed REST
API contracts; 4. normalization and data integrity; 5. Django
authentication/ORM conventions; 6. security, privacy, maintainability,
and testability.

The Assessment 1 ERD currently identifies concepts such as:

-   User
-   StudentProfile
-   Skill
-   StudentSkill
-   Recommendation
-   SkillGap
-   JobDescription
-   Resume
-   CoverLetter
-   InterviewSession
-   InterviewQuestion
-   Roadmap
-   RoadmapStep
-   AuditLog

### Important model guidance

The ERD is a design baseline, not permission to duplicate Django
authentication internals. The implementation should use Django's
authentication framework and a custom user model only where required.

The intended core relationships are:

``` text
User
  1
  |
  1
StudentProfile
  |
  +-- many StudentSkill --> Skill
  +-- many Recommendation
  |       |
  |       +-- many SkillGap --> Skill
  |
  +-- many JobDescription
  +-- many Resume
  +-- many CoverLetter
  +-- many InterviewSession
  |       |
  |       +-- many InterviewQuestion
  |
  +-- many Roadmap
  |       |
  |       +-- many RoadmapStep
  |
  +-- many AuditLog
```

Relationships and cardinalities must be checked against the latest
approved ERD before migrations are finalised.

## 7. Authentication and Authorization

### Roles

V1 supports: - Student - Administrator

### Authentication API Contract

  Method   Endpoint                              Purpose
  -------- ------------------------------------- ------------------------------------
  POST     `/api/v1/auth/register/`                 Register student account
  POST     `/api/v1/auth/login/`                    Authenticate and issue JWT tokens
  POST     `/api/v1/auth/token/refresh/`            Obtain a new access token
  POST     `/api/v1/auth/logout/`                   Invalidate/blacklist refresh token
  POST     `/api/v1/auth/password/reset/`           Start password recovery
  POST     `/api/v1/auth/password/reset/confirm/`   Complete password reset
  GET      `/api/v1/auth/me/`                       Return current authenticated user

Passwords use Django's password hashing mechanisms and are never stored
or returned as plaintext.

Protected endpoints require JWT authentication. Administrative endpoints
require administrator permissions. Student-owned resources require
object-level ownership checks.

## 8. Student Profile

FR-02 requires structured profile data covering: - skills; -
interests; - education; - experience; - projects; - career goals; -
personality responses.

The ERD currently shows only part of this information in
`StudentProfile`. Before implementing FR-02 fully, the team should
reconcile the ERD with the functional requirement and decide which
fields require separate normalized models.

Avoid adding speculative fields before that review.

## 9. Recommendation Engine

FR-03 and FR-04 require ranked career recommendations with scores and
explanations.

The numerical score must be calculated from documented weighted rules.

``` text
Structured Student Profile
          |
          v
Deterministic Scoring Service
          |
          +--> numerical score / factor breakdown
          |
          v
Ranked Recommendations
          |
          v
Optional AI Explanation Service
```

AI may explain why a result was produced but must not replace the
deterministic scoring calculation.

## 10. Skill-Gap and Readiness

FR-05 and FR-06 compare the student's current skills with selected
career requirements.

The backend should produce structured results such as: - current
level; - required level; - gap; - weighted readiness contribution; -
overall readiness score; - explanation factors.

The calculation must be repeatable for identical structured input.

## 11. Job-Description Matching

FR-07 analyses one pasted job description at a time and returns matched
and missing requirements.

V1 explicitly excludes live job-board/ATS integration.

Job matching should be separated from career recommendation scoring so
that a pasted job description does not silently change the deterministic
career recommendation algorithm.

## 12. AI-Assisted Features

AI-supported backend features include: - recommendation explanations; -
resume draft generation; - cover-letter draft generation; - interview
questions and feedback; - roadmap/explanatory text where approved.

Rules: - API key remains server-side. - Send minimum necessary personal
data. - Use approved prompts. - Validate AI responses before
returning/saving them. - Configure timeout/failure behaviour. - Return
clear errors when the service is unavailable. - Generated content
remains editable/reviewable. - AI must not use protected attributes as
direct scoring factors.

## 13. Administration

FR-14 requires authorised administrators to manage: - users; -
careers; - skills; - learning resources.

Administrative endpoints must use explicit role permissions.

FR-15 requires aggregated statistics such as popular careers and common
skill gaps. Analytics responses should avoid exposing individual student
private information.

## 14. Audit and Error Handling

FR-18 requires critical actions and external-service failures to be
recorded.

Audit records should capture only useful operational metadata and avoid
secrets or unnecessary sensitive content.

Examples: - important administrative changes; - deletion actions; -
critical AI-service failures; - security-relevant actions where
appropriate.

API errors should use consistent JSON responses and suitable HTTP status
codes.

## 15. Database and Migrations

Environment variables:

``` text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

`.env` is local/secret and must not be committed.

Django models and migrations are the source of truth for application
schema changes:

``` bash
python manage.py makemigrations
python manage.py migrate
```

Migration files are committed so teammates and deployment environments
can reproduce the schema.

## 16. Deployment

Demonstration deployment target: - React frontend: Vercel - Django
backend: Railway - PostgreSQL: Railway-hosted PostgreSQL or approved
deployment database

Local development may use local PostgreSQL.

Environment-specific secrets must be supplied through environment
variables, not source control.

## 17. Non-Functional Requirements

Backend implementation must particularly support:

-   NFR-03: normal non-AI API responses target under 2 seconds for
    expected classroom use;
-   NFR-05: secure Django authentication and protected endpoints;
-   NFR-06: privacy and isolation of student records;
-   NFR-07: modular, maintainable source and documented setup;
-   NFR-08: repeatable deterministic scoring;
-   NFR-09: explainable score factors;
-   NFR-12: automated/acceptance testing where practical;
-   NFR-13: separation of frontend, backend, database, and AI services;
-   NFR-14: ethical AI constraints;
-   NFR-15: documented database export/restore procedure.

## 18. Testing Strategy

Backend testing should cover: - model and service unit tests; -
serializer validation; - registration/login/JWT flows; - role
permissions; - object ownership/privacy; - API success and failure
responses; - deterministic scoring repeatability; - AI
timeout/error/fallback behaviour; - deletion behaviour; - admin
restrictions; - integration with PostgreSQL.

Postman can be used for manual API verification, but important backend
behaviour should also have automated tests.

## 19. Source-of-Truth Rule

Implementation priority is: 1. team-approved functional/non-functional
requirements; 2. approved API contract; 3. approved ERD/architecture
decisions; 4. this backend architecture document; 5. implementation
plan/tasks.

When these disagree, do not silently choose one. Record the conflict and
resolve it with the team before implementing a schema/API decision that
affects integration.
