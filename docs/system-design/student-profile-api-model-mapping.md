# GradNavi Student Profile API and Model Mapping

Status: Working design for team review

## 1. Purpose

This document maps the GradNavi Student Profile REST API contract to the planned Student Profile data model.

The mapping provides a shared reference for backend, frontend, integration, and testing work by showing how API fields relate to conceptual entities and student-owned database records.

This document does not replace the GradNavi REST API Design or the Student Profile Data Design. It connects those two design artifacts.

The mapping should remain aligned with:

- `docs/system-design/rest-api-design.md`
- `docs/system-design/student-profile-data-design.md`
- `docs/system-design/security-architecture.md`
- The implemented authentication model.
- The implemented Django Student Profile models and serializers.

## 2. Existing Student Profile ERD

A second ERD is not required for this mapping document because the Student Profile entities and relationships are already documented in the Student Profile Data Design.

The existing ERD should remain the visual source for the Student Profile data structure:

![GradNavi Student Profile ERD](images/gradnavi-student-profile-erd.png)

The editable Draw.io source is stored at:

`docs/system-design/images/gradnavi-student-profile-erd.drawio`

This mapping document focuses on how the REST API reads from and writes to those entities.

## 3. Mapping Overview

The Student Profile API provides an aggregated view of the authenticated student's profile.

The current high-level flow is:

    React Frontend
          |
          | GET /api/v1/profile/
          | PATCH /api/v1/profile/
          v
    Django REST API
          |
          | Authenticated User
          v
    StudentProfile
          |
          +---- Education
          +---- Experience
          +---- Project
          +---- CareerGoal
          +---- PersonalityResponse
          +---- StudentSkill ---- Skill
          +---- StudentInterest ---- Interest

The Django backend is responsible for converting the related Student Profile records into the JSON structure used by the React frontend.

## 4. Student Profile API Endpoints

The current Sprint 1 REST API contract defines two Student Profile endpoints.

| HTTP Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/profile/` | Retrieve the authenticated student's Student Profile |
| `PATCH` | `/api/v1/profile/` | Update selected Student Profile information |

Both endpoints require authentication.

The backend must identify the Student Profile through the authenticated User rather than a client-provided `user_id` or `student_profile_id`.

## 5. GET Profile Mapping

The current REST API contract represents the Student Profile using an aggregated JSON structure.

Conceptual response:

    {
      "data": {
        "profile": {
          "skills": [],
          "interests": [],
          "education": [],
          "experience": [],
          "projects": [],
          "career_goals": [],
          "personality_responses": []
        }
      }
    }

Each collection maps to one or more Student Profile entities.

| API Field | Conceptual Entity or Relationship | Ownership |
| --- | --- | --- |
| `skills` | `StudentSkill` joined with `Skill` | Student-owned relationship with shared Skill data |
| `interests` | `StudentInterest` joined with `Interest` | Student-owned relationship with shared Interest data |
| `education` | `Education` | Student-owned |
| `experience` | `Experience` | Student-owned |
| `projects` | `Project` | Student-owned |
| `career_goals` | `CareerGoal` | Student-owned |
| `personality_responses` | `PersonalityResponse` | Student-owned |

The API response should only include records associated with the authenticated student's StudentProfile.

## 6. PATCH Profile Mapping

The `PATCH /api/v1/profile/` endpoint supports partial Student Profile updates.

A PATCH request should update only the fields included in the request and should not require unrelated profile information to be resubmitted.

Conceptual example:

    {
      "career_goals": [
        "Software Engineer"
      ],
      "interests": [
        "Artificial Intelligence",
        "Backend Development"
      ]
    }

The exact writable JSON structure should be confirmed against the implemented serializers before the Student Profile backend module is finalised.

The backend must validate each supplied collection and apply changes only to the authenticated student's Student Profile.

## 7. StudentProfile Model Mapping

The `StudentProfile` model acts as the parent record for student-owned profile information.

| Conceptual Field | API Exposure | Notes |
| --- | --- | --- |
| `id` | Normally internal | Should not be trusted from frontend input for ownership |
| `user_id` | Internal relationship | Derived from authenticated User |
| `created_at` | Optional response metadata | Not required in the current high-level profile contract |
| `updated_at` | Optional response metadata | May support future profile update tracking |

The frontend should not select profile ownership by sending a `user_id`.

## 8. Skill Mapping

Skills use the `StudentSkill` join entity and shared `Skill` reference data.

### 8.1 Model Relationship

    StudentProfile 1 ----- * StudentSkill * ----- 1 Skill

### 8.2 Planned Mapping

| API Concept | Model Field or Entity |
| --- | --- |
| Skill identifier | `Skill.id` |
| Skill name | `Skill.name` |
| Skill category | `Skill.category` |
| Skill description | `Skill.description` |
| Student proficiency | `StudentSkill.proficiency_level` |

The final API representation for a skill should support more than a plain string if proficiency information is required by readiness and skill-gap calculations.

The Student Profile API should represent a student skill using a structured object so the frontend and later scoring functions receive both the shared Skill information and the student's proficiency level.

Example:

```json
{
  "id": 12,
  "name": "Python",
  "category": "Programming",
  "proficiency_level": "proficient"
}
```

The approved values for `proficiency_level` are:

| Display Label | API Value |
| --- | --- |
| Foundational | `foundational` |
| Developing | `developing` |
| Proficient | `proficient` |
| Advanced | `advanced` |

The backend must reject unsupported proficiency values.

The React frontend should display the user-friendly labels while using the lowercase API values when reading or updating Student Profile skill data.

## 9. Interest Mapping

Interests use the `StudentInterest` join entity and shared `Interest` reference data.

### 9.1 Model Relationship

    StudentProfile 1 ----- * StudentInterest * ----- 1 Interest

### 9.2 Planned Mapping

| API Concept | Model Field or Entity |
| --- | --- |
| Interest identifier | `Interest.id` |
| Interest name | `Interest.name` |
| Interest category | `Interest.category` |

Student-facing profile operations should manage the relationship between the authenticated StudentProfile and shared Interest records.

They should not automatically grant permission to edit shared Interest reference data.

## 10. Education Mapping

Each Education API item maps to one `Education` record.

| API Concept | Planned Model Field |
| --- | --- |
| Education identifier | `Education.id` |
| Institution | `Education.institution_name` |
| Qualification | `Education.qualification` |
| Field of study | `Education.field_of_study` |
| Start date | `Education.start_date` |
| End date | `Education.end_date` |
| Description | `Education.description` |

The backend should associate Education records with the authenticated StudentProfile.

## 11. Experience Mapping

Each Experience API item maps to one `Experience` record.

| API Concept | Planned Model Field |
| --- | --- |
| Experience identifier | `Experience.id` |
| Job title | `Experience.job_title` |
| Company | `Experience.company` |
| Start date | `Experience.start_date` |
| End date | `Experience.end_date` |
| Current role | `Experience.is_current` |
| Description | `Experience.description` |

The final serializer should enforce consistent behaviour between `is_current` and `end_date`.

## 12. Project Mapping

Each Project API item maps to one `Project` record.

| API Concept | Planned Model Field |
| --- | --- |
| Project identifier | `Project.id` |
| Project name | `Project.name` |
| Description | `Project.description` |
| Project URL | `Project.project_url` |
| Start date | `Project.start_date` |
| End date | `Project.end_date` |

The current design does not include a structured Project-to-Skill relationship.

If one is introduced later, both the Student Profile Data Design and this mapping document should be updated.

## 13. Career Goal Mapping

Each Career Goal API item maps to one `CareerGoal` record.

The current API contract supports multiple Career Goals with one Primary Goal.

| API Concept | Implemented Model Field |
| --- | --- |
| Career Goal identifier | `CareerGoal.id` |
| Structured Career identifier | `CareerGoal.career_id` |
| Career name / legacy role text | `CareerGoal.target_role` |
| Description | `CareerGoal.description` |
| Primary Goal flag | `CareerGoal.is_primary` |

The preferred write path uses `career_id`.

A typical structured Career Goal contains:

- `career_id`
- `description`
- `is_primary`

`target_role` remains supported as a compatibility path for older records and clients.

When an approved Career is selected, the backend may synchronize the canonical Career name into `target_role`.

When both `career_id` and `target_role` are supplied, they must identify the same Career.

The backend prevents:

- Duplicate structured Careers in one Student Profile.
- More than one Primary Career Goal.
- Invalid or unavailable structured Career references.

Career Goals may contribute profile direction to recommendation, readiness, skill-gap, learning-resource, and roadmap features.

The scoring behaviour remains outside the scope of this mapping document.

## 14. Personality Response Mapping

Each personality-response API item maps to one `PersonalityResponse` record.

| API Concept | Implemented Model Field |
| --- | --- |
| Response identifier | `PersonalityResponse.id` |
| Question identifier | `PersonalityResponse.question_key` |
| Response value | `PersonalityResponse.response_value` |

The implemented Student Profile frontend uses 16 approved work-style questions.

The student-facing response scale is:

- Strongly Disagree.
- Disagree.
- Neutral.
- Agree.
- Strongly Agree.

The interface presents one question at a time.

Responses are saved through the authenticated Student Profile update contract.

The personality-response structure supports GradNavi career-analysis features and is not defined as a clinical diagnosis.

## 15. Ownership Mapping

The following entities contain student-owned information:

- `StudentProfile`
- `StudentSkill`
- `StudentInterest`
- `Education`
- `Experience`
- `Project`
- `CareerGoal`
- `PersonalityResponse`

Ownership should follow this backend path:

    JWT
     |
     v
    Authenticated User
     |
     v
    StudentProfile
     |
     v
    Related Student-Owned Records

The backend should not use a client-submitted user identifier as proof of ownership.

Shared reference entities such as `Skill` and `Interest` require separate permission rules.

## 16. Validation Mapping

API validation should be applied before Student Profile changes are stored.

| Validation Area | Model or API Concern |
| --- | --- |
| Authentication | Valid JWT required |
| Ownership | Authenticated User must own StudentProfile |
| Skill reference | Referenced Skill must exist |
| Interest reference | Referenced Interest must exist |
| Proficiency | Must be one of `foundational`, `developing`, `proficient`, or `advanced` |
| Duplicate skills | Prevent duplicate StudentSkill relationships where appropriate |
| Duplicate interests | Prevent duplicate StudentInterest relationships where appropriate |
| Dates | Validate format and logical ranges |
| URLs | Validate project URL format |
| Required fields | Enforce serializer and model requirements |
| Permissions | Reject unauthorised Student or Administrator operations |

Validation errors should follow the standard error-response format defined by the GradNavi REST API Design.

## 17. HTTP Status Mapping

The Student Profile API should use the status-code conventions defined by the shared REST API design.

| Status | Student Profile Use |
| --- | --- |
| `200 OK` | Successful profile retrieval or update |
| `400 Bad Request` | Invalid Student Profile input |
| `401 Unauthorized` | Authentication missing, invalid, or expired |
| `403 Forbidden` | Authenticated user lacks permission |
| `404 Not Found` | Required profile or related resource does not exist |
| `500 Internal Server Error` | Unexpected backend failure |

The exact behaviour should remain consistent with the implemented exception handler and backend serializers.

## 18. Frontend Mapping

The React frontend should consume Student Profile information through the REST API rather than storing database-specific knowledge.

The frontend should understand API fields such as:

- `skills`
- `interests`
- `education`
- `experience`
- `projects`
- `career_goals`
- `personality_responses`

The frontend should not need to understand:

- PostgreSQL table names.
- Django migration details.
- Database foreign-key implementation.
- Database credentials.
- Backend ownership-query logic.

This separation keeps the REST API as the contract between frontend and backend.

## 19. Serializer Responsibility

Django REST Framework serializers should provide the translation between API JSON and Student Profile model data.

Serializer responsibilities may include:

- Converting model records into JSON.
- Validating incoming profile data.
- Applying approved field rules.
- Supporting partial updates.
- Preventing writable access to server-controlled fields.
- Coordinating nested or related Student Profile data where required.

The implemented serializers translate the approved nested Student Profile API contract into the current Django model relationships and validation rules.

## 20. Current Implemented Contract

The Student Profile frontend and backend currently use the authenticated nested profile contract:

- `GET /api/v1/profile/`
- `PATCH /api/v1/profile/`

The profile payload includes the related collections required by the current interface:

- `skills`
- `interests`
- `education`
- `experience`
- `projects`
- `career_goals`
- `personality_responses`

Searchable shared-reference endpoints are used for approved Skills, Interests, and Careers.

The redesigned frontend keeps database implementation details behind the REST contract.

Students edit profile sections through the frontend while the backend validates and persists the related Student-owned records.

The current WBS 5.6 Student Profile redesign does not require separate CRUD endpoints for each nested profile collection.

## 21. Implemented Mapping Decisions

The following Student Profile mapping decisions are implemented in the current contract:

1. Skill items use shared Skill references and an approved proficiency level.
2. Interest items use shared Interest references.
3. `proficiency_level` is writable using the approved Student proficiency scale.
4. Student-owned related collections are updated through the nested profile PATCH workflow.
5. Career Goals support structured `career_id` input.
6. Multiple Career Goals are allowed with one Primary Career Goal when goals exist.
7. Legacy `target_role` input remains supported for compatibility.
8. Duplicate structured Career Goals for the same Career are rejected.
9. Student-owned collections are validated against the authenticated Student Profile.
10. The personality contract uses 16 approved work-style questions and the five-choice response scale.
11. Education, Experience, and Project records support their implemented nullable or blank end-date rules.
12. Shared Skills, Interests, and Careers are selected through approved reference-data search flows.
13. The React frontend consumes the REST API contract rather than Django or PostgreSQL implementation details.
14. Server-controlled ownership fields are not accepted as proof of Student ownership.

Future material changes to serializer nesting, related-resource endpoints, shared-reference rules, or Career Goal behaviour must update this mapping document and the REST API Design.

## 22. Implementation Review Checklist

Before the Student Profile API is considered aligned with this design, the team should verify:

- The authenticated User maps to one StudentProfile.
- Student-owned records are restricted to the authenticated Student.
- Skill relationships use StudentSkill.
- Interest relationships use StudentInterest.
- GET profile responses match the approved API structure.
- PATCH behaviour does not unintentionally replace unrelated profile information.
- Server-controlled fields are not writable by normal Student requests.
- Validation follows the REST API conventions.
- Permission failures use the correct status codes.
- The frontend does not require direct database knowledge.
- The model implementation matches the Student Profile ERD.
- API changes are reflected in the REST API Design.

## 23. Design Status

This document is an implementation-aligned mapping artifact for the current Student Profile frontend and backend contract.

It connects the Student Profile REST API contract to the conceptual Student Profile data design.

Current field names, serializer behaviour, nested update behaviour, Career Goal rules, and Personality Response behaviour are aligned with the implemented backend and WBS 5.6 Student Profile frontend. Future contract changes must be reflected here.

Any material API or model change should be reflected in:

- `rest-api-design.md`
- `student-profile-data-design.md`
- This mapping document.
- The Student Profile ERD where relationships change.
