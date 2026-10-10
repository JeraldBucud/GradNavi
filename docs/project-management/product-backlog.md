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
| FR-01 | Account registration and authentication | Students create accounts, sign in, sign out, and recover access | Must | Sprint 1 | Jerald, Joyee | 4.4, 4.5, 4.8, 4.9 | Done |
| FR-02 | Student profile | Students create and update skills, interests, education, experience, projects, goals, and personality responses | Must | Sprint 1 | MD, Joyee, Jerald | 4.6, 4.7, 4.8, 4.9 | Done |
| FR-03 | Career recommendations | Students receive ranked career recommendations from profile data | Must | Sprint 2 | MD, Jerald, Joyee | 5.2, 5.3, 5.4, 5.6, 5.9 | Done |
| FR-04 | Recommendation explanation | Students see recommendation scores and understandable reasons for each result | Must | Sprint 2 | Jerald, MD, Joyee | 5.3, 5.4, 5.6, 5.9 | Done |
| FR-05 | Skill-gap analysis | Students compare current skills with selected career requirements | Must | Sprint 2 | Jerald, Joyee | 5.5, 5.6, 5.9 | Done |
| FR-06 | Career-readiness score | Students receive a readiness score based on documented weighted criteria | Must | Sprint 2 | Jerald, Joyee | 5.5, 5.6, 5.9 | Done |
| FR-07 | Job-description matching | Students paste one job description and see matched and missing requirements | Must | Sprint 4 | Jerald, Joyee | 7.2, 7.5, 7.9 | Done |
| FR-08 | Resume builder | Students generate and edit a resume draft from profile data | Must | Sprint 3 | MD, Joyee | 6.3, 6.5, 6.8, 6.9 | Done |
| FR-09 | Cover-letter builder | Students generate and edit a cover letter for a selected job description | Must | Sprint 3 | MD, Joyee | 6.4, 6.5, 6.8, 6.9 | Done |
| FR-10 | Interview preparation | Students receive interview questions and feedback on typed answers | Must | Sprint 3 | Jerald, Joyee | 6.2, 6.6, 6.7, 6.8, 6.9 | Done |
| FR-11 | Learning suggestions | Students receive learning resources linked to identified skill gaps | Must | Sprint 2 | MD, Joyee | 5.7, 5.8, 5.9 | Done |
| FR-12 | Career roadmap | Students receive ordered development steps for a selected career | Must | Sprint 2 | MD, Joyee | 5.7, 5.8, 5.9 | Done |
| FR-13 | Progress dashboard | Students view saved careers, gaps, readiness, roadmap progress, and interview history | Should | Schedule alignment required | To be confirmed | No dedicated Microsoft Project task identified | Review |
| FR-14 | Basic administration | Authorised administrators manage users, careers, skills, and learning resources | Must | Sprint 4 | MD, Joyee, Jerald | 7.6, 7.7, 7.8, 7.9 | Done |
| FR-15 | Admin analytics | Administrators view aggregated statistics such as popular careers and common skill gaps | Should | Sprint 4, provisional mapping | MD, Joyee | 7.6, 7.7 | Review |
| FR-16 | AI content review | Students review and edit generated AI-supported content before saving | Must | Schedule alignment required | To be confirmed | No dedicated Microsoft Project task identified | Review |
| FR-17 | Data deletion | Students delete saved generated documents and request deletion of their profile | Must | Schedule alignment required | To be confirmed | No dedicated Microsoft Project task identified | Backlog |
| FR-18 | Audit and error handling | The system records critical actions and returns controlled errors for external-service failures | Must | Sprint 4 | Jerald | 7.4, 7.8, 7.9 | Done |

## WBS 8.12 Backlog Reconciliation

The WBS 8.12 review reconciles execution status with later Sprint closeout evidence.

Status changes in the table above use verified implementation and testing evidence. They do not rewrite the approved Microsoft Project task ownership or Sprint allocation.

Reconciliation notes:

- FR-03 through FR-06, FR-11, and FR-12 are marked Done based on the 80 of 80 passing Sprint 2 test baseline.
- FR-08 through FR-10 are marked Done based on the 100 of 100 passing Sprint 3 closeout baseline.
- FR-07, FR-14, and FR-18 are marked Done based on the 129 of 129 passing Sprint 4 Feature Complete baseline.
- FR-13 has merged implementation evidence through PR #75, but its formal Microsoft Project mapping is still unresolved, so its backlog state stays Review.
- FR-15 implementation evidence exists through the Sprint 4 administration work, but its WBS mapping remains provisional, so its backlog state stays Review.
- FR-16 reviewable/editable generated-content behaviour exists across the Sprint 3 document interfaces and AI service contracts, but its formal WBS mapping remains unresolved, so its backlog state stays Review.
- FR-17 stays Backlog because WBS 8.12 did not identify verified Student-facing evidence that satisfies the full deletion requirement.

For the detailed audit, see `docs/project-management/wbs-8.12-final-github-review.md`.

## Sprint 1 Backlog

Sprint 1 focused on the foundation, authentication, Student Profile, and initial integration.

Related requirements:

- FR-01 Account registration and authentication.
- FR-02 Student profile.

Final Sprint 1 closeout status:

- WBS 4.2 Django and PostgreSQL project setup is complete.
- WBS 4.3 React frontend setup and routing is complete.
- WBS 4.4 Authentication backend and JWT is complete.
- WBS 4.5 Login and Registration Interface is complete.
- WBS 4.6 Student Profile models and API is complete.
- WBS 4.7 Student Profile interface is complete.
- WBS 4.8 Authentication and Profile Integration is complete.
- WBS 4.9 Sprint 1 unit and API testing is complete.
- WBS 4.10 Sprint 1 review and retrospective is complete.
- WBS 4.11 Sprint 1 complete is reached.
- The Sprint 1 tracker records 61 Pass, 0 Fail, 0 Blocked, and 0 Not Run.
- The Sprint 1 Evidence Index records EV-001 through EV-070.
- FR-01 is Done for Sprint 1 scope.
- FR-02 is Done for Sprint 1 scope.

Formal closeout is recorded in:

`docs/project-management/sprint-1-closeout.md`

## Sprint 2 Backlog

Sprint 2 runs from 24 August to 4 September 2026.

Related requirements:

- FR-03 Career recommendations.
- FR-04 Recommendation explanation.
- FR-05 Skill-gap analysis.
- FR-06 Career-readiness score.
- FR-11 Learning suggestions.
- FR-12 Career roadmap.

Current Sprint 2 execution update - 20 September 2026:

- WBS 5.2 Career and Skill Reference Data is implemented.
- WBS 5.3 Weighted Recommendation Engine is implemented.
- WBS 5.4 Career Recommendation API is implemented.
- WBS 5.5 Skill Gap and Readiness Scoring Logic is implemented.
- WBS 5.6 Recommendation and Readiness Interface is implemented and integrated.
- WBS 5.7 Learning Suggestions and Roadmap API implementation is present.
- WBS 5.8 Learning Roadmap Interface is implemented and integrated.
- WBS 5.9 Sprint 2 Integration and Testing records 80 Pass cases from 80 planned cases.
- `S2-LEARN-01` through `S2-LEARN-08` were executed successfully and are recorded as Pass.
- No Sprint 2 test case is recorded as Fail, Blocked, or Not Run.
- Sprint 2 test execution is complete. A dedicated formal Sprint 2 closeout record was not identified during the WBS 8.12 audit.

Closeout testing identified and resolved:

- DEF-S2-003: responsive Student navigation and Career Recommendations layout.
- DEF-S2-004: `NaN` displayed in the Learning Resources empty state.
- DEF-S2-005: ranked Career Recommendations returned when Student Skills were empty.

Current closeout position:

- Core Career Analysis integration is working.
- Recommendation, readiness, Skill Gap, roadmap, ownership, responsive, keyboard, and browser checks have been completed in the integrated flow.
- FR-11 and FR-12 have completed their planned Sprint 2 test coverage.
- All 80 planned Sprint 2 cases pass.
- Formal Sprint 2 closeout documentation still requires reconciliation because no dedicated `sprint-2-closeout.md` file was identified.

Sprint 2 retrospective actions carried forward into Sprint 3 include earlier frontend/backend integration, earlier ownership confirmation for test execution, faster documentation updates after merges, and earlier responsive, error-state, empty-state, and browser testing.

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

WBS 8.12 reviewed the remaining requirement-to-schedule differences without changing Microsoft Project ownership or Sprint allocation.

### FR-13 Progress Dashboard

FR-13 remains part of GradNavi V1.

Merged PR #75 provides implementation evidence for the Student Progress Dashboard.

The Microsoft Project schedule still has no dedicated FR-13 implementation task.

Current state:

- Implementation present.
- Backlog status: Review.
- Formal WBS mapping still requires reconciliation.

### FR-16 AI Content Review

FR-16 requires generated content to remain reviewable and editable.

The implemented Sprint 3 document workflows and AI service contracts provide review/edit behaviour.

The Microsoft Project schedule still has no dedicated FR-16 requirement mapping.

Current state:

- Required behaviour present in the document workflows.
- Backlog status: Review.
- Formal WBS mapping still requires reconciliation.

### FR-17 Data Deletion

FR-17 remains part of the functional requirements.

WBS 8.12 did not identify verified Student-facing evidence that satisfies the full deletion requirement.

Current state:

- Backlog status: Backlog.
- Do not mark complete without generated-document deletion and profile-deletion request evidence.
- Any scope or ownership change must follow project change control.

### FR-15 Admin Analytics

FR-15 retains its provisional mapping to:

- WBS 7.6 Admin Models and API.
- WBS 7.7 Admin Dashboard Interface.

Sprint 4 administration implementation exists and Sprint 4 reached Feature Complete.

Current state:

- Implementation evidence present.
- Backlog status: Review.
- Formal mapping confirmation remains required.

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
