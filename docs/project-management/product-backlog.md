# GradNavi Product Backlog

Status: Product backlog aligned with the revised Microsoft Project schedule.

## Source of Truth

The GradNavi Microsoft Project schedule is the authoritative planning baseline for:

- Sprint allocation.
- Task ownership.
- Task sequencing.
- Dependencies.
- Start and finish dates.
- Milestones.

This Product Backlog maps functional requirements to the implementation tasks recorded in Microsoft Project.

A requirement may involve more than one implementation lead because frontend, backend, integration, and testing work may belong to different team members.

Execution status should reflect actual team progress. Planned dates alone do not change a backlog item's execution status.

## Product Backlog

| ID | Backlog Item | User Outcome | Priority | Planned Sprint | Implementation Leads | Main WBS Tasks | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR-01 | Account registration and authentication | Students create accounts, sign in, sign out, and recover access | Must | Sprint 1 | Jerald, Joyee | 4.4, 4.5, 4.8, 4.9 | Testing |
| FR-02 | Student profile | Students create and update skills, interests, education, experience, projects, goals, and personality responses | Must | Sprint 1 | MD, Joyee, Jerald | 4.6, 4.7, 4.8, 4.9 | Blocked |
| FR-03 | Career recommendations | Students receive ranked career recommendations from profile data | Must | Sprint 2 | MD, Jerald, Joyee | 5.2, 5.3, 5.4, 5.6, 5.9 | Backlog |
| FR-04 | Recommendation explanation | Students see recommendation scores and understandable reasons for each result | Must | Sprint 2 | Jerald, MD, Joyee | 5.3, 5.4, 5.6, 5.9 | Backlog |
| FR-05 | Skill-gap analysis | Students compare current skills with selected career requirements | Must | Sprint 2 | Jerald, Joyee | 5.5, 5.6, 5.9 | Backlog |
| FR-06 | Career-readiness score | Students receive a readiness score based on documented weighted criteria | Must | Sprint 2 | Jerald, Joyee | 5.5, 5.6, 5.9 | Backlog |
| FR-07 | Job-description matching | Students paste one job description and see matched and missing requirements | Must | Sprint 4 | Jerald, Joyee | 7.2, 7.5, 7.9 | Backlog |
| FR-08 | Resume builder | Students generate and edit a resume draft from profile data | Must | Sprint 3 | MD, Joyee | 6.3, 6.5, 6.8, 6.9 | Backlog |
| FR-09 | Cover-letter builder | Students generate and edit a cover letter for a selected job description | Must | Sprint 3 | MD, Joyee | 6.4, 6.5, 6.8, 6.9 | Backlog |
| FR-10 | Interview preparation | Students receive interview questions and feedback on typed answers | Must | Sprint 3 | Jerald, Joyee | 6.2, 6.6, 6.7, 6.8, 6.9 | Backlog |
| FR-11 | Learning suggestions | Students receive learning resources linked to identified skill gaps | Must | Sprint 2 | MD, Joyee | 5.7, 5.8, 5.9 | Backlog |
| FR-12 | Career roadmap | Students receive ordered development steps for a selected career | Must | Sprint 2 | MD, Joyee | 5.7, 5.8, 5.9 | Backlog |
| FR-13 | Progress dashboard | Students view saved careers, gaps, readiness, roadmap progress, and interview history | Should | Schedule alignment required | To be confirmed | No dedicated Microsoft Project task identified | Backlog |
| FR-14 | Basic administration | Authorised administrators manage users, careers, skills, and learning resources | Must | Sprint 4 | MD, Joyee, Jerald | 7.6, 7.7, 7.8, 7.9 | Backlog |
| FR-15 | Admin analytics | Administrators view aggregated statistics such as popular careers and common skill gaps | Should | Sprint 4, provisional mapping | MD, Joyee | 7.6, 7.7 | Backlog |
| FR-16 | AI content review | Students review and edit generated AI-supported content before saving | Must | Schedule alignment required | To be confirmed | No dedicated Microsoft Project task identified | Backlog |
| FR-17 | Data deletion | Students delete saved generated documents and request deletion of their profile | Must | Schedule alignment required | To be confirmed | No dedicated Microsoft Project task identified | Backlog |
| FR-18 | Audit and error handling | The system records critical actions and returns controlled errors for external-service failures | Must | Sprint 4 | Jerald | 7.4, 7.8, 7.9 | Backlog |

## Sprint 1 Backlog

Sprint 1 focuses on the foundation, authentication, Student Profile, and initial integration.

Related requirements:

- FR-01 Account registration and authentication.
- FR-02 Student profile.

Current planning status:

- Authentication frontend and integration testing has progressed through Sprint 1.
- Student Profile integration remains dependent on the Student Profile backend implementation.
- Final Sprint 1 closure depends on remaining Student Profile work and related testing.

## Sprint 2 Backlog

Sprint 2 runs from 24 August to 4 September 2026.

Related requirements:

- FR-03 Career recommendations.
- FR-04 Recommendation explanation.
- FR-05 Skill-gap analysis.
- FR-06 Career-readiness score.
- FR-11 Learning suggestions.
- FR-12 Career roadmap.

Main implementation sequence:

1. WBS 5.1 Sprint 2 planning.
2. WBS 5.2 Career and skill reference data.
3. WBS 5.3 Weighted recommendation engine.
4. WBS 5.4 Career recommendation API.
5. WBS 5.5 Skill gap and readiness scoring logic.
6. WBS 5.6 Recommendation and readiness interface.
7. WBS 5.7 Learning suggestions and roadmap API.
8. WBS 5.8 Learning roadmap interface.
9. WBS 5.9 Sprint 2 integration and testing.
10. WBS 5.10 Sprint 2 review and retrospective.
11. WBS 5.11 Sprint 2 complete.

## Sprint 3 Backlog

Sprint 3 runs from 7 September to 18 September 2026.

Related requirements:

- FR-08 Resume builder.
- FR-09 Cover-letter builder.
- FR-10 Interview preparation.

Main implementation sequence:

1. WBS 6.1 Sprint 3 planning.
2. WBS 6.2 AI prompt templates and safety rules.
3. WBS 6.3 Resume generation backend.
4. WBS 6.4 Cover letter generation backend.
5. WBS 6.5 Resume and cover letter interface.
6. WBS 6.6 Interview question and feedback API.
7. WBS 6.7 Interview preparation interface.
8. WBS 6.8 Document and interview integration.
9. WBS 6.9 Sprint 3 testing.
10. WBS 6.10 Sprint 3 review and retrospective.
11. WBS 6.11 Sprint 3 complete.

## Sprint 4 Backlog

Sprint 4 runs from 21 September to 2 October 2026.

Related requirements:

- FR-07 Job-description matching.
- FR-14 Basic administration.
- FR-15 Admin analytics.
- FR-18 Audit and error handling.

Sprint 4 also includes controlled AI service integration and validation.

Main implementation sequence:

1. WBS 7.1 Sprint 4 planning.
2. WBS 7.2 Job description extraction and matching.
3. WBS 7.3 OpenAI service integration.
4. WBS 7.4 AI response validation and error handling.
5. WBS 7.5 Job matching interface.
6. WBS 7.6 Admin models and API.
7. WBS 7.7 Admin dashboard interface.
8. WBS 7.8 Role permissions and audit records.
9. WBS 7.9 Sprint 4 integration and testing.
10. WBS 7.10 Sprint 4 review and retrospective.
11. WBS 7.11 Feature complete.

## Sprint 5 Backlog

Sprint 5 runs from 5 October to 9 October 2026, followed by final presentation preparation.

Sprint 5 focuses on:

- Regression testing.
- Security and permission testing.
- Performance and usability review.
- Defect correction.
- User acceptance testing.
- Deployment.
- Production verification.
- Documentation.
- Final report review.
- Presentation preparation.

Sprint 5 does not introduce new core functional requirements unless an approved change request modifies project scope.

## Schedule Alignment Items

The following functional requirements do not currently have a dedicated task in the revised Microsoft Project schedule:

### FR-13 Progress Dashboard

The functional requirement remains part of GradNavi V1, but the revised Microsoft Project WBS does not identify a dedicated Progress Dashboard implementation task.

The team should decide whether FR-13:

- Fits within an existing interface task.
- Requires a new Sprint 4 task.
- Moves to another approved Sprint.
- Requires a documented scope change.

### FR-16 AI Content Review

The functional requirement requires generated content to remain reviewable and editable.

The Microsoft Project schedule contains AI prompt, generation, interface, and validation work, but does not identify FR-16 as a dedicated implementation task.

The team should explicitly map FR-16 to the appropriate Sprint 3 and Sprint 4 tasks or add a separate task.

### FR-17 Data Deletion

The functional requirement remains in the approved requirements list, but the revised Microsoft Project schedule does not identify a dedicated deletion implementation task.

The team should assign:

- Sprint.
- Owner.
- Backend task.
- Frontend task where required.
- Permission testing.
- Acceptance evidence.

### FR-15 Admin Analytics

FR-15 is provisionally mapped to:

- WBS 7.6 Admin models and API.
- WBS 7.7 Admin dashboard interface.

The team should confirm whether those tasks include aggregated analytics or whether a separate task is required.

## Backlog Fields

GitHub Projects or Trello should track:

- Status.
- Implementation lead.
- Supporting member.
- Priority.
- Sprint.
- Estimate.
- Start date.
- Target date.
- Requirement ID.
- WBS task.
- Dependency.
- Evidence link.
- Blocker.
- Pull request where applicable.

## Workflow

1. Backlog.
2. Ready.
3. In Progress.
4. Review.
5. Testing.
6. Blocked.
7. Done.

## Definition of Ready

A backlog item is Ready when:

- The requirement is approved.
- Acceptance criteria are clear.
- Sprint allocation is confirmed.
- WBS mapping is recorded.
- Dependencies are recorded.
- Implementation leads are confirmed.
- Required design or data inputs are available.
- The task does not conflict with another member's active implementation work.

## Definition of Done

A backlog item is Done when:

- Acceptance criteria are met.
- Required implementation work is complete.
- Code or documentation has been reviewed.
- Required tests pass.
- No unresolved critical defect affects the requirement.
- Security, privacy, validation, and error handling have been checked where relevant.
- Integration with dependent components has been verified.
- Required evidence has been recorded.
- Relevant documentation has been updated.
- The team accepts the completed work during the appropriate Sprint review.

## Change Control

When Microsoft Project, this Product Backlog, Trello, or GitHub assignments disagree:

1. Stop implementation where the conflict affects ownership or dependencies.
2. Review the Microsoft Project baseline.
3. Discuss the conflict with the team.
4. Record the approved decision.
5. Update Microsoft Project first.
6. Update the Work Breakdown Structure.
7. Update the Task Leads document.
8. Update this Product Backlog.
9. Update Trello and related GitHub records.
10. Continue implementation after the planning records agree.