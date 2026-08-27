# GradNavi Student Profile Data Design

Status: Working design for team review

## 1. Purpose

This document defines the planned data design for the GradNavi Student Profile module.

The Student Profile provides the structured student information used by GradNavi features such as career recommendations, readiness scoring, skill-gap analysis, job-description matching, resume and cover-letter generation, interview preparation, learning suggestions, and career roadmaps.

The design identifies the main profile entities, their relationships, and the information each entity is expected to store.

This document describes the planned data structure only. The final Django models, database migrations, serializers, and API behaviour will remain aligned with the implemented backend and the GradNavi REST API design.

The Student Profile design should support the following profile areas:

- Skills.
- Education.
- Interests.
- Experience.
- Projects.
- Career goals.
- Personality-related responses.

## 2. Student Profile Model Overview

The GradNavi Student Profile data design separates profile information into related entities rather than storing all student information in one database table.

This structure supports multiple records for areas such as education, experience, projects, and career goals while allowing shared reference data such as skills and interests to be reused across students.

The planned high-level relationship structure is:

```text
User
 |
 | One-to-One
 v
StudentProfile
 |
 +---- One-to-Many ---- Education
 |
 +---- One-to-Many ---- Experience
 |
 +---- One-to-Many ---- Project
 |
 +---- One-to-Many ---- CareerGoal
 |
 +---- One-to-Many ---- PersonalityResponse
 |
 +---- Many-to-Many --- Skill
 |        through StudentSkill
 |
 +---- Many-to-Many --- Interest
```

### 2.1 Conceptual ERD

The following ERD shows the planned Student Profile entities and their relationships.

![GradNavi Student Profile ERD](images/gradnavi-student-profile-erd.png)

The editable Draw.io source is stored at:

`docs/system-design/images/gradnavi-student-profile-erd.drawio`


The main concept here is parent entity.

StudentProfile is not where every field lives. It is the central record that owns related profile data.

```text
User
  ↓
StudentProfile
  ↓
Education / Experience / Skills / Projects / Goals
```

## 3. StudentProfile Entity

The `StudentProfile` entity represents the main profile record for a GradNavi student.

It acts as the parent record for student-owned career information such as education, experience, projects, career goals, personality responses, skills, and interests.

### 3.1 Relationship with User

Each Student Profile belongs to one authenticated User.

The planned relationship is:

    User 1 ----- 1 StudentProfile

This is a one-to-one relationship.

The authentication User model is defined by the GradNavi accounts module. This Student Profile design does not redefine authentication fields such as email, password, role, or account status.

The Student Profile should reference the authenticated User through a trusted backend relationship.

### 3.2 Planned Fields

The conceptual StudentProfile fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the Student Profile |
| `user_id` | Links the profile to the authenticated User |
| `created_at` | Records when the profile was created |
| `updated_at` | Records when the profile was last updated |

The exact primary-key type and Django field configuration should remain aligned with the implemented backend.

### 3.3 Responsibilities

The StudentProfile entity should:

- Act as the main owner of student career-profile information.
- Associate profile data with the authenticated User.
- Provide the parent relationship for student-owned profile records.
- Support retrieval of the authenticated student's complete profile.
- Support secure ownership checks in the Django backend.
- Support later career recommendation, readiness, and skill-gap functions.

### 3.4 Data Ownership

Student Profile records contain personal information.

The Django backend must determine profile ownership from the authenticated User rather than trusting a user identifier supplied by the frontend.

For example, the frontend should not be able to select another Student Profile by submitting a different `user_id`.

### 3.5 Profile Creation

The exact profile-creation behaviour should be confirmed during backend implementation.

Possible approaches include:

- Creating a Student Profile automatically when a Student account is created.
- Creating the Student Profile when the student first enters profile information.

The selected approach should remain consistent with the authentication implementation and REST API contract.

## 4. Skill and StudentSkill Entities

Skills are a core part of the GradNavi Student Profile because they support career recommendations, readiness scoring, skill-gap analysis, job-description matching, and later learning suggestions.

The design separates shared Skill reference data from the student-specific relationship to that skill.

### 4.1 Skill Entity

The `Skill` entity represents a reusable skill that may be associated with many students.

Examples may include:

- Python.
- Java.
- React.
- Django.
- PostgreSQL.
- Communication.
- Problem solving.

Using shared Skill records avoids creating duplicate copies of the same skill for every student.

### 4.2 Planned Skill Fields

The conceptual Skill fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the Skill |
| `name` | Name of the skill |
| `category` | Groups related skills where required |
| `description` | Describes the skill where additional context is needed |
| `created_at` | Records when the Skill was created |
| `updated_at` | Records when the Skill was last updated |

Skill names should be managed consistently so equivalent skills are not stored under unnecessary duplicate names.

### 4.3 StudentSkill Join Entity

The `StudentSkill` entity connects a Student Profile to a Skill.

The planned relationship is:

    StudentProfile 1 ----- * StudentSkill * ----- 1 Skill

This allows:

- One student to have many skills.
- One skill to belong to many students.
- Additional information to be stored about the student's relationship with the skill.


### 4.4 Planned StudentSkill Fields

The conceptual StudentSkill fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the StudentSkill record |
| `student_profile_id` | Links the record to the owning Student Profile |
| `skill_id` | Links the record to the shared Skill |
| `proficiency_level` | Represents the student's current skill level |
| `created_at` | Records when the skill was added to the profile |
| `updated_at` | Records when the StudentSkill record was last updated |

The approved GradNavi skill proficiency scale uses four ordered levels:

| Display Label | API Value | Meaning |
| --- | --- | --- |
| Foundational | `foundational` | Introductory knowledge with limited practical experience |
| Developing | `developing` | Working knowledge with some practical experience and occasional guidance |
| Proficient | `proficient` | Able to use the skill independently for typical tasks and projects |
| Advanced | `advanced` | Able to use the skill independently for complex tasks and deeper technical work |

The `proficiency_level` field must use one of these four approved API values.

The frontend should display the user-friendly labels while sending the lowercase API values to the backend.

For later comparison and scoring logic, the proficiency levels may be represented internally as an ordered scale:

| API Value | Internal Ordinal Value |
| --- | ---: |
| `foundational` | 1 |
| `developing` | 2 |
| `proficient` | 3 |
| `advanced` | 4 |

These numeric values are intended for internal comparison and scoring logic. They are not student-facing scores.

The exact scoring weights and career-readiness calculations remain outside the scope of the Student Profile data design.

### 4.5 Why a Join Entity Is Used

A direct many-to-many relationship would only show that a student is associated with a skill.

GradNavi also needs information about the student's current capability because later features compare the student profile against career and job requirements.

For example:

    StudentProfile
          |
          v
    StudentSkill
          |
          +---- Skill: Python
          |
          +---- Proficiency: Intermediate

This structure supports richer skill analysis than storing only a list of skill names.

### 4.6 Ownership and Validation

StudentSkill records are student-owned profile data.

The Django backend should verify that the authenticated student owns the related Student Profile before allowing StudentSkill records to be created, updated, or removed.

The backend should also validate that:

- The referenced Skill exists.
- The submitted proficiency level uses an approved value.
- Duplicate StudentSkill records for the same Student Profile and Skill are prevented where appropriate.

### 4.7 Future Scoring Use

The Skill and StudentSkill structure should support later GradNavi scoring functions.

Possible uses include:

- Matching student skills against career requirements.
- Identifying missing skills.
- Identifying partially met skills.
- Supporting career-readiness calculations.
- Matching extracted job-description skills against the student profile.

The exact scoring rules should remain defined separately from the Student Profile data structure.

## 5. Interest and StudentInterest Entities

Interests represent areas, activities, or career-related topics that a student is interested in.

GradNavi uses student interests as one of the factors supporting career recommendations.

The design separates shared Interest reference data from the student-specific relationship to an interest.

### 5.1 Interest Entity

The `Interest` entity represents a reusable interest that may be associated with many students.

Examples may include:

- Software development.
- Artificial intelligence.
- Cybersecurity.
- Data analysis.
- Cloud computing.
- User experience.
- Project management.

The final set of interests should be based on the career and recommendation data approved by the team.

### 5.2 Planned Interest Fields

The conceptual Interest fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the Interest |
| `name` | Name of the interest |
| `category` | Groups related interests where required |
| `created_at` | Records when the Interest was created |
| `updated_at` | Records when the Interest was last updated |

Interest names should be managed consistently to reduce unnecessary duplicate records.

### 5.3 StudentInterest Join Entity

The `StudentInterest` entity connects a Student Profile to an Interest.

The planned relationship is:

    StudentProfile 1 ----- * StudentInterest * ----- 1 Interest

This structure allows:

- One student to select many interests.
- One interest to be associated with many students.
- Student-specific interest relationships to be managed independently from shared Interest records.

### 5.4 Planned StudentInterest Fields

The conceptual StudentInterest fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the StudentInterest record |
| `student_profile_id` | Links the record to the owning Student Profile |
| `interest_id` | Links the record to the shared Interest |
| `created_at` | Records when the interest was added to the profile |
| `updated_at` | Records when the StudentInterest record was last updated |

### 5.5 Why a Join Entity Is Used

A shared Interest record should not belong directly to one student.

For example, multiple students may select `Artificial Intelligence` as an interest.

The relationship may therefore look like:

    Student A
        |
        v
    StudentInterest
        |
        v
    Artificial Intelligence

    Student B
        |
        v
    StudentInterest
        |
        v
    Artificial Intelligence

Both students reference the same Interest while keeping their profile relationships separate.

### 5.6 Ownership and Validation

StudentInterest records are student-owned profile data.

The Django backend should verify that the authenticated student owns the related Student Profile before allowing StudentInterest records to be created or removed.

The backend should also validate that:

- The referenced Interest exists.
- Duplicate StudentInterest records for the same Student Profile and Interest are prevented where appropriate.
- Students cannot modify the shared Interest reference data through student profile operations unless the API explicitly permits that behaviour.

### 5.7 Recommendation Use

Student interests should support the GradNavi career recommendation process.

The recommendation system may compare a student's selected interests against interest information associated with careers.

The Student Profile data structure should provide the required interest information to the recommendation system without defining the scoring algorithm itself.

The exact weighting and scoring rules should remain separate from this data design.

## 6. Education Entity

The `Education` entity represents a student's education history.

A Student Profile may contain multiple Education records because a student may have completed or be undertaking more than one qualification.

The planned relationship is:

    StudentProfile 1 ----- * Education

Each Education record belongs to one Student Profile.

### 6.1 Planned Education Fields

The conceptual Education fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the Education record |
| `student_profile_id` | Links the record to the owning Student Profile |
| `institution_name` | Name of the educational institution |
| `qualification` | Name or type of qualification |
| `field_of_study` | Main area of study |
| `start_date` | Date the qualification or study period started |
| `end_date` | Date the qualification or study period ended |
| `description` | Optional additional information about the education record |
| `created_at` | Records when the Education record was created |
| `updated_at` | Records when the Education record was last updated |

The final Django field types and rules for incomplete or current study should be confirmed during backend implementation.

### 6.2 Why Education Is Separate

Education should not be stored directly inside StudentProfile because one student may have several education records.

For example:

    StudentProfile
        |
        +---- Graduate Certificate in Information Technology
        |
        +---- Graduate Diploma of Information Technology
        |
        +---- Master of Information Technology

Each qualification can therefore be managed independently.

### 6.3 Ownership and Validation

Education records are student-owned profile data.

The Django backend should verify that the authenticated student owns the related Student Profile before allowing an Education record to be created, updated, or removed.

Validation should also ensure that submitted dates and required fields follow the approved API rules.


## 7. Experience Entity

The `Experience` entity represents employment or other relevant professional experience recorded by a student.

A Student Profile may contain multiple Experience records.

The planned relationship is:

    StudentProfile 1 ----- * Experience

Each Experience record belongs to one Student Profile.

### 7.1 Planned Experience Fields

The conceptual Experience fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the Experience record |
| `student_profile_id` | Links the record to the owning Student Profile |
| `job_title` | Role or position held |
| `company` | Organisation associated with the experience |
| `start_date` | Date the experience started |
| `end_date` | Date the experience ended |
| `is_current` | Indicates whether the experience is ongoing |
| `description` | Describes responsibilities, activities, or achievements |
| `created_at` | Records when the Experience record was created |
| `updated_at` | Records when the Experience record was last updated |

### 7.2 Current Experience

The `is_current` field supports ongoing experience where an end date does not yet exist.

The backend should ensure that the relationship between `is_current` and `end_date` follows consistent validation rules.

For example, an ongoing role may have:

    is_current = true
    end_date = empty

The exact validation behaviour should be defined during backend implementation.

### 7.3 Ownership

Experience records belong to the authenticated student's Student Profile.

Students should only be permitted to create, update, or remove Experience records belonging to their own profile.


## 8. Project Entity

The `Project` entity represents projects that provide evidence of a student's knowledge, skills, or practical experience.

Projects may include academic, personal, portfolio, or other relevant work entered by the student.

A Student Profile may contain multiple Project records.

The planned relationship is:

    StudentProfile 1 ----- * Project

### 8.1 Planned Project Fields

The conceptual Project fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the Project |
| `student_profile_id` | Links the Project to the owning Student Profile |
| `name` | Name of the Project |
| `description` | Describes the Project and the student's work |
| `project_url` | Optional link to the Project or supporting material |
| `start_date` | Date the Project started |
| `end_date` | Date the Project ended |
| `created_at` | Records when the Project was created |
| `updated_at` | Records when the Project was last updated |

### 8.2 Project Evidence

Project information may later support career recommendations, readiness scoring, resumes, cover letters, and other GradNavi functions.

The current Student Profile design does not define a separate Project-to-Skill relationship.

A future design revision may introduce such a relationship if the scoring requirements require structured evidence connecting Projects to Skills.

Any such change should be reviewed by the team before implementation.

### 8.3 Ownership

Project records belong to the authenticated student's Student Profile.

The backend should prevent students from modifying Projects belonging to another Student Profile.


## 9. CareerGoal Entity

The `CareerGoal` entity represents a career direction or target identified by a student.

Career goals provide information about what the student wants to work toward and may support career recommendations and roadmap generation.

A Student Profile may contain multiple CareerGoal records.

The planned relationship is:

    StudentProfile 1 ----- * CareerGoal

### 9.1 Planned CareerGoal Fields

The conceptual CareerGoal fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the CareerGoal |
| `student_profile_id` | Links the CareerGoal to the owning Student Profile |
| `target_role` | Career or role the student wants to pursue |
| `description` | Optional information about the student's career goal |
| `created_at` | Records when the CareerGoal was created |
| `updated_at` | Records when the CareerGoal was last updated |

### 9.2 Recommendation and Roadmap Use

Career goals may provide input to features such as:

- Career recommendations.
- Career-readiness analysis.
- Skill-gap analysis.
- Career roadmaps.
- Learning suggestions.

This entity stores the student's goal information.

It does not define how GradNavi calculates recommendations or readiness scores.

### 9.3 Ownership

CareerGoal records belong to the authenticated student's Student Profile.

Students should only be permitted to manage CareerGoal records associated with their own profile.


## 10. PersonalityResponse Entity

The `PersonalityResponse` entity represents a student's response to a personality-related question used by GradNavi.

The project requirements identify personality-related information as part of the broader student information used by the system.

A Student Profile may contain multiple PersonalityResponse records.

The planned relationship is:

    StudentProfile 1 ----- * PersonalityResponse

### 10.1 Planned PersonalityResponse Fields

The conceptual PersonalityResponse fields are:

| Field | Purpose |
| --- | --- |
| `id` | Primary identifier for the PersonalityResponse |
| `student_profile_id` | Links the response to the owning Student Profile |
| `question_key` | Identifies the personality-related question |
| `response_value` | Stores the student's response |
| `created_at` | Records when the response was created |
| `updated_at` | Records when the response was last updated |

### 10.2 Questionnaire Design

This document does not define the final personality questionnaire, assessment method, or interpretation rules.

Those details require separate agreement before implementation.

The Student Profile design only establishes a structure for storing approved personality-related responses.

### 10.3 Ownership and Privacy

Personality responses are student-owned profile information.

Access should follow the same authentication, authorization, ownership, and privacy controls applied to other Student Profile data.

Personality information should only be collected where required for approved GradNavi functionality.


## 11. Relationship Summary

The planned Student Profile relationships are:

| Parent Entity | Relationship | Related Entity |
| --- | --- | --- |
| User | One-to-One | StudentProfile |
| StudentProfile | One-to-Many | Education |
| StudentProfile | One-to-Many | Experience |
| StudentProfile | One-to-Many | Project |
| StudentProfile | One-to-Many | CareerGoal |
| StudentProfile | One-to-Many | PersonalityResponse |
| StudentProfile | One-to-Many | StudentSkill |
| StudentSkill | Many-to-One | Skill |
| StudentProfile | One-to-Many | StudentInterest |
| StudentInterest | Many-to-One | Interest |

The StudentSkill and StudentInterest join entities allow Skill and Interest reference data to be reused across multiple Student Profiles.


## 12. Data Ownership and Access Control

Student Profile information must be protected by authenticated API access.

Student-owned records include:

- StudentProfile.
- StudentSkill.
- StudentInterest.
- Education.
- Experience.
- Project.
- CareerGoal.
- PersonalityResponse.

The backend should determine the authenticated student's identity from the validated authentication context.

Student-facing API operations should not trust a client-provided user identifier for ownership decisions.

For example, changing a `student_profile_id` or `user_id` in a frontend request must not provide access to another student's information.

Shared reference data such as Skill and Interest should follow separate permissions from student-owned profile records.

Administrator access should follow the role and permission rules defined by the GradNavi security architecture and REST API design.


## 13. Data Validation Principles

The backend should validate Student Profile data before storing changes.

Validation should include, where applicable:

- Required fields.
- Field lengths.
- Valid date formats.
- Logical date ranges.
- Valid foreign-key references.
- Approved proficiency values.
- Duplicate relationship prevention.
- URL format validation.
- Ownership validation.
- Permission validation.

Validation rules should be implemented consistently with the GradNavi REST API contract.

Invalid input should use the standard API error-response structure defined by the REST API design.


## 14. Privacy and Data Minimisation

The Student Profile contains personal information used by GradNavi career-guidance functions.

The system should collect only information required for approved application functionality.

Student Profile information should not be exposed directly to external services unless required for an approved feature.

Where profile information is sent to an external AI provider, unnecessary personal information should be removed before the request is made.

External AI access must occur through the backend rather than directly from the React frontend.

Detailed security controls remain defined in the GradNavi Security Architecture.


## 15. API Alignment

The Student Profile data design should remain aligned with the GradNavi REST API Design.

The API layer is responsible for translating between stored Student Profile data and the JSON structures used by the React frontend.

The frontend should communicate with Student Profile data through authenticated API endpoints.

The frontend should not communicate directly with PostgreSQL.

Changes to the Student Profile data structure that affect request or response formats should also be reflected in the REST API Design.


## 16. Django Implementation Considerations

This document defines the conceptual data design rather than the final Django implementation.

The backend developer should determine the appropriate Django model fields, constraints, related names, deletion behaviour, indexes, and migrations based on the approved design.

Implementation decisions should preserve:

- The one-to-one relationship between User and StudentProfile.
- Student ownership of profile records.
- Shared Skill and Interest reference data.
- StudentSkill and StudentInterest join relationships.
- Required validation rules.
- Secure access controls.
- Compatibility with the REST API contract.

The final implementation should be reviewed against this document before the Student Profile backend module is considered complete.


## 17. Open Design Decisions

The following items require confirmation during implementation or team review:

1. The exact Django primary-key strategy.
2. When a StudentProfile is created.
3. The approved `proficiency_level` values.
4. Whether skill proficiency requires a more detailed scoring scale.
5. Whether Education requires explicit support for current study.
6. Whether Project requires an `is_current` field.
7. Whether Projects should later have structured relationships with Skills.
8. The final personality questionnaire and permitted response values.
9. Whether students select only predefined Skills and Interests or whether custom entries are permitted.
10. Which shared reference records students may create or modify.
11. Final field-length limits and optional-field rules.
12. Final deletion behaviour for Student Profile related records.

These decisions should be recorded before or during backend implementation so the data design, REST API contract, database schema, and frontend remain aligned.


## 18. Design Traceability

The Student Profile data design supports the GradNavi requirement for students to create and maintain a structured profile.

The profile provides data required by later system functions including:

- Career recommendations.
- Career-readiness scoring.
- Skill-gap analysis.
- Job-description matching.
- Resume generation.
- Cover-letter generation.
- Interview preparation.
- Learning suggestions.
- Career roadmap generation.

Scoring algorithms, AI prompts, career reference data, learning-resource data, and generated-document structures are outside the scope of this Student Profile data design.


## 19. Design Status

This document is a working system-design artifact for team review.

The conceptual entities and relationships provide a proposed foundation for the Student Profile backend module.

Final implementation details should be confirmed against:

- The implemented authentication model.
- The GradNavi REST API Design.
- The GradNavi Security Architecture.
- The approved functional and non-functional requirements.
- The implemented Django models and migrations.

Any material change to the Student Profile data structure should be reflected in this document and the associated ERD so the system-design documentation remains aligned with the implementation.