# GradNavi Requirements Assignment Matrix

Status: Requirements implementation mapping aligned with the revised Microsoft Project schedule.

## Purpose

This document maps GradNavi functional and non-functional requirements to the implementation responsibilities recorded in the Microsoft Project schedule.

Functional and non-functional requirements define required system behaviour and quality expectations.

The Microsoft Project schedule defines implementation ownership, Sprint placement, sequencing, dependencies, and milestones.

A requirement may involve several implementation leads because backend, frontend, integration, testing, and supporting logic are divided across separate WBS tasks.

## Source of Truth

Planning authority follows this order:

1. Approved functional and non-functional requirements define what GradNavi must deliver.
2. Microsoft Project defines when implementation occurs and who owns each scheduled task.
3. `work-breakdown-structure.md` mirrors the Microsoft Project task structure.
4. `task-leads.md` mirrors task ownership.
5. `product-backlog.md` maps requirements to Sprint implementation.
6. This Requirements Assignment Matrix links requirements to those implementation tasks.

If ownership or Sprint placement changes, Microsoft Project must be updated first.

---

## Functional Requirement Assignments

| Requirement | Planned Sprint | Implementation Leads | WBS Mapping | Assignment Basis |
| --- | --- | --- | --- | --- |
| FR-01 Account registration and authentication | Sprint 1 | Jerald, Joyee | 4.4, 4.5, 4.8, 4.9 | Jerald leads authentication backend and integration. Joyee leads login and registration interface. Testing is shared. |
| FR-02 Student profile | Sprint 1 | MD, Joyee, Jerald | 4.6, 4.7, 4.8, 4.9 | MD leads Student Profile models and API. Joyee leads the interface. Jerald leads integration. Testing is shared. |
| FR-03 Career recommendations | Sprint 2 | MD, Jerald, Joyee | 5.2, 5.3, 5.4, 5.6, 5.9 | MD leads reference data and recommendation API. Jerald leads weighted recommendation logic. Joyee leads recommendation interface. |
| FR-04 Recommendation explanation | Sprint 2 | Jerald, MD, Joyee | 5.3, 5.4, 5.6, 5.9 | Jerald leads weighted scoring logic. MD exposes recommendation results through the API. Joyee presents scores and explanations. |
| FR-05 Skill-gap analysis | Sprint 2 | Jerald, Joyee | 5.5, 5.6, 5.9 | Jerald leads skill-gap logic. Joyee leads presentation of recommendation and readiness results. |
| FR-06 Career-readiness score | Sprint 2 | Jerald, Joyee | 5.5, 5.6, 5.9 | Jerald leads readiness scoring logic. Joyee leads readiness presentation. |
| FR-07 Job-description matching | Sprint 4 | Jerald, Joyee | 7.2, 7.5, 7.9 | Jerald leads job-description extraction and matching. Joyee leads the matching interface. |
| FR-08 Resume builder | Sprint 3 | MD, Joyee | 6.3, 6.5, 6.8, 6.9 | MD leads resume generation backend. Joyee leads the editable document interface. |
| FR-09 Cover-letter builder | Sprint 3 | MD, Joyee | 6.4, 6.5, 6.8, 6.9 | MD leads cover-letter generation backend. Joyee leads the editable document interface. |
| FR-10 Interview preparation | Sprint 3 | Jerald, Joyee | 6.2, 6.6, 6.7, 6.8, 6.9 | Jerald leads AI prompt and safety rules plus interview question and feedback API. Joyee leads the interview interface. |
| FR-11 Learning suggestions | Sprint 2 | MD, Joyee | 5.7, 5.8, 5.9 | MD leads learning suggestions and roadmap API. Joyee leads the learning roadmap interface. WBS 5.5 provides the required skill-gap input. |
| FR-12 Career roadmap | Sprint 2 | MD, Joyee | 5.7, 5.8, 5.9 | MD leads roadmap API. Joyee leads the roadmap interface. |
| FR-13 Progress dashboard | Schedule alignment required | To be confirmed | No dedicated WBS implementation task identified | The requirement remains in V1. The team must map it to an existing task or add an approved Microsoft Project task. |
| FR-14 Basic administration | Sprint 4 | MD, Joyee, Jerald | 7.6, 7.7, 7.8, 7.9 | MD leads admin models and API. Joyee leads the admin dashboard. Jerald leads role permissions and audit records. |
| FR-15 Admin analytics | Sprint 4, provisional | MD, Joyee | 7.6, 7.7 | Current mapping places backend aggregation with admin API work and display with the admin dashboard. The team must confirm this mapping. |
| FR-16 AI content review | Schedule alignment required | To be confirmed | No dedicated WBS implementation task identified | AI generation and interface tasks exist, but the review and edit requirement needs an explicit WBS mapping. |
| FR-17 Data deletion | Schedule alignment required | To be confirmed | No dedicated WBS implementation task identified | The requirement needs explicit backend, interface, permission, and testing tasks in Microsoft Project. |
| FR-18 Audit and error handling | Sprint 4 | Jerald | 7.4, 7.8, 7.9 | Jerald leads AI response validation and error handling plus role permissions and audit records. |

---

## Sprint 1 Requirement Mapping

Sprint 1 dates:

    10 August to 21 August 2026

Requirements:

- FR-01 Account registration and authentication.
- FR-02 Student profile.

Implementation mapping:

    FR-01
      |
      +-- 4.4 Authentication backend and JWT - Jerald
      +-- 4.5 Login and registration interface - Joyee
      +-- 4.8 Authentication and profile integration - Jerald
      +-- 4.9 Sprint 1 unit and API testing - All Members

    FR-02
      |
      +-- 4.6 Student Profile models and API - MD
      +-- 4.7 Student Profile interface - Joyee
      +-- 4.8 Authentication and profile integration - Jerald
      +-- 4.9 Sprint 1 unit and API testing - All Members

---

## Sprint 2 Requirement Mapping

Sprint 2 dates:

    24 August to 4 September 2026

Requirements:

- FR-03 Career recommendations.
- FR-04 Recommendation explanation.
- FR-05 Skill-gap analysis.
- FR-06 Career-readiness score.
- FR-11 Learning suggestions.
- FR-12 Career roadmap.

Implementation sequence:

    5.2 Career and skill reference data - MD
        |
        v
    5.3 Weighted recommendation engine - Jerald
        |
        +-----------------------------+
        |                             |
        v                             v
    5.4 Career recommendation    5.5 Skill gap and
    API - MD                     readiness scoring - Jerald
                                      |
                                      v
                               5.7 Learning suggestions
                               and roadmap API - MD

Frontend implementation:

    5.6 Recommendation and readiness interface - Joyee
    5.8 Learning roadmap interface - Joyee

Integration and testing:

    5.9 Sprint 2 integration and testing - All Members

---

## Sprint 3 Requirement Mapping

Sprint 3 dates:

    7 September to 18 September 2026

Requirements:

- FR-08 Resume builder.
- FR-09 Cover-letter builder.
- FR-10 Interview preparation.

Implementation mapping:

    FR-08
      |
      +-- 6.3 Resume generation backend - MD
      +-- 6.5 Resume and cover-letter interface - Joyee

    FR-09
      |
      +-- 6.4 Cover-letter generation backend - MD
      +-- 6.5 Resume and cover-letter interface - Joyee

    FR-10
      |
      +-- 6.2 AI prompt templates and safety rules - Jerald
      +-- 6.6 Interview question and feedback API - Jerald
      +-- 6.7 Interview preparation interface - Joyee

Shared integration:

    6.8 Document and interview integration - All Members
    6.9 Sprint 3 testing - All Members

---

## Sprint 4 Requirement Mapping

Sprint 4 dates:

    21 September to 2 October 2026

Requirements:

- FR-07 Job-description matching.
- FR-14 Basic administration.
- FR-15 Admin analytics.
- FR-18 Audit and error handling.

Implementation mapping:

    FR-07
      |
      +-- 7.2 Job description extraction and matching - Jerald
      +-- 7.5 Job matching interface - Joyee

    FR-14
      |
      +-- 7.6 Admin models and API - MD
      +-- 7.7 Admin dashboard interface - Joyee
      +-- 7.8 Role permissions and audit records - Jerald

    FR-18
      |
      +-- 7.4 AI response validation and error handling - Jerald
      +-- 7.8 Role permissions and audit records - Jerald

Shared integration:

    7.9 Sprint 4 integration and testing - All Members

---

## Requirements Requiring Schedule Alignment

### FR-13 Progress Dashboard

FR-13 remains part of the functional requirements.

The revised Microsoft Project schedule does not currently identify a dedicated Progress Dashboard task.

Before implementation, the team must decide whether FR-13:

1. Fits within an existing Sprint interface task.
2. Requires a new Sprint 4 task.
3. Requires another approved Sprint placement.
4. Requires an approved scope change.

### FR-15 Admin Analytics

FR-15 currently has a provisional mapping to:

    7.6 Admin models and API
    7.7 Admin dashboard interface

The team must confirm that these tasks include the required aggregated analytics behaviour.

### FR-16 AI Content Review

FR-16 requires users to review and edit generated content before saving.

Related AI and interface work exists in Sprint 3 and Sprint 4, but the revised schedule does not identify a dedicated FR-16 task.

The team must explicitly map this requirement before declaring it complete.

### FR-17 Data Deletion

FR-17 remains part of V1.

The revised schedule does not currently identify dedicated deletion implementation work.

The team must confirm:

- Backend deletion behaviour.
- Profile deletion request behaviour.
- Generated document deletion.
- Required frontend controls.
- Permission rules.
- Audit requirements.
- Acceptance tests.
- Sprint placement.
- Task ownership.

---

## Non-Functional Requirement Assignments

Microsoft Project does not assign every non-functional requirement as a separate WBS task.

The following quality ownership remains the working assignment unless an explicit Microsoft Project task supersedes it.

| Requirement | Quality Lead | Supporting Members | Quality Area |
| --- | --- | --- | --- |
| NFR-01 | Joyee | Jerald | Usability |
| NFR-02 | Joyee | Jerald | Responsive design |
| NFR-03 | Jerald | MD, Joyee | Performance |
| NFR-04 | Jerald | MD | Availability |
| NFR-05 | Jerald | MD, Joyee | Security |
| NFR-06 | MD | Jerald, Joyee | Privacy |
| NFR-07 | Jerald | All Members | Maintainability |
| NFR-08 | Jerald | MD | Reliability |
| NFR-09 | Jerald | MD, Joyee | Explainability |
| NFR-10 | Joyee | All Members | Accessibility |
| NFR-11 | Joyee | Jerald | Compatibility |
| NFR-12 | Jerald | All Members | Testability |
| NFR-13 | Jerald | MD, Joyee | Scalability |
| NFR-14 | Jerald | All Members | Ethical AI |
| NFR-15 | Jerald | MD | Recoverability |

---

## Non-Functional Requirement WBS Links

| Requirement | Relevant WBS Areas |
| --- | --- |
| NFR-01 Usability | 3.8, 5.6, 5.8, 6.5, 6.7, 7.5, 7.7, 8.4, 8.6 |
| NFR-02 Responsive design | 3.7, 3.8, 4.3, 4.5, 4.7, 5.6, 5.8, 6.5, 6.7, 7.5, 7.7 |
| NFR-03 Performance | 5.3, 5.5, 7.2, 7.4, 8.4, 8.9 |
| NFR-04 Availability | 8.7, 8.8, 8.9 |
| NFR-05 Security | 3.9, 4.4, 4.8, 7.8, 8.3, 8.9 |
| NFR-06 Privacy | 2.7, 3.9, 4.6, 7.8, 8.3 |
| NFR-07 Maintainability | 1.4, 3.1, 3.6, 8.10, 8.11, 8.12 |
| NFR-08 Reliability | 5.3, 5.5, 5.9, 8.2 |
| NFR-09 Explainability | 5.3, 5.4, 5.6 |
| NFR-10 Accessibility | 3.7, 3.8, frontend Sprint tasks, 8.4 |
| NFR-11 Compatibility | Frontend Sprint tasks, 8.4, 8.6 |
| NFR-12 Testability | 4.9, 5.9, 6.9, 7.9, 8.2, 8.3, 8.6 |
| NFR-13 Scalability | 3.1, 3.5, 3.6, backend service separation |
| NFR-14 Ethical AI | 2.7, 6.2, 7.3, 7.4 |
| NFR-15 Recoverability | 8.7, 8.9, 8.10 |

---

## Shared Approval

All members review:

- Requirement wording.
- Priority.
- Acceptance criteria.
- Sprint allocation.
- WBS mapping.
- Dependencies.
- Security and privacy effects.
- Testing evidence.
- Changes to approved requirements.

## Assignment Rule

A functional requirement does not need one artificial owner when its implementation spans several WBS tasks.

The named WBS task owner remains accountable for their assigned implementation task.

Requirement completion requires all mapped implementation, integration, and testing work to satisfy the approved acceptance criteria.

## Change Control

When this matrix conflicts with Microsoft Project:

1. Review the Microsoft Project baseline.
2. Confirm the intended ownership or Sprint placement with the team.
3. Update Microsoft Project first where a planning change is approved.
4. Update the Work Breakdown Structure.
5. Update the Task Leads document.
6. Update the Product Backlog.
7. Update this Requirements Assignment Matrix.
8. Update Trello and relevant GitHub records.
9. Record the decision in meeting minutes where required.

The Microsoft Project schedule remains the authoritative implementation-planning record.