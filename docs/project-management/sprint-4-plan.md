# GradNavi Sprint 4 Plan

Status: Draft for team review

WBS: 7.1 Sprint 4 Planning

Sprint: Sprint 4 - Job Matching, AI Integration, and Administration

Planned Sprint dates: 21 September to 2 October 2026

Official owner of WBS 7.1: All Members

Shared Sprint 4 integration branch:

`feature/sprint-4`

## 1. Purpose

This document defines the GradNavi Sprint 4 implementation plan.

Sprint 4 focuses on completing the remaining core GradNavi functionality before Sprint 5 testing, deployment, documentation, and presentation preparation.

The planned Sprint 4 increment includes:

* Job-description extraction and matching.
* OpenAI service integration.
* AI response validation and controlled error handling.
* Job-matching interface.
* Admin models and API.
* Admin dashboard interface.
* Role permissions and audit records.
* Sprint 4 integration and testing.
* Sprint review and retrospective.
* Feature Complete milestone.

Sprint 4 should produce a feature-complete GradNavi application ready for final regression testing and deployment work in Sprint 5.

## 2. Planning Basis

This Sprint 4 plan aligns with the current GradNavi planning and design documents:

* `docs/project-management/work-breakdown-structure.md`
* `docs/project-management/product-backlog.md`
* `docs/project-management/task-leads.md`
* `docs/project-management/responsibility-matrix.md`
* `docs/project-management/roadmap-and-milestones.md`
* `docs/project-management/sprint-3-plan.md`
* `docs/requirements/functional-requirements.md`
* `docs/requirements/non-functional-requirements.md`
* `docs/system-design/security-architecture.md`
* `docs/system-design/rest-api-design.md`

The Microsoft Project schedule stays the authoritative planning baseline for official task dates, task ownership, dependencies, and milestones.

## 3. Sprint 4 Goal

The primary Sprint 4 outcome is:

> A feature-complete GradNavi application with job-description matching, external AI service integration, administration, role permissions, audit support, and tested integration across the completed core features.

Sprint 4 should complete the major implementation work before Sprint 5 begins.

Sprint 5 should focus on:

* Regression testing.
* Security testing.
* Permission testing.
* User acceptance testing.
* Defect correction.
* Deployment.
* Production verification.
* Documentation.
* Final report preparation.
* Presentation preparation.

Sprint 4 should avoid introducing unrelated new product scope.

## 4. Sprint 3 Handover and Controlled Overlap

The approved WBS lists:

`WBS 6.11 Sprint 3 Complete`

as the predecessor of:

`WBS 7.1 Sprint 4 Planning`

At the current planning checkpoint, Sprint 3 is not formally complete.

Current Sprint 3 work still includes:

* WBS 6.5 Resume and Cover Letter Interface.
* WBS 6.7 Interview Preparation Interface.
* WBS 6.8 Document and Interview Integration.
* WBS 6.9 Sprint 3 Testing.
* WBS 6.10 Sprint 3 Review and Retrospective.
* WBS 6.11 Sprint 3 Complete.

The team is preparing Sprint 4 planning before formal Sprint 3 closure so available team members have a clear next implementation plan.

This early preparation follows these rules:

1. Sprint 3 stays formally open until WBS 6.11 is reached.
2. Remaining Sprint 3 implementation continues through `feature/sprint-3`.
3. Sprint 4 planning work proceeds through `feature/sprint-4`.
4. `feature/sprint-4` was created from the current `feature/sprint-3` baseline.
5. Creation of `feature/sprint-4` does not count as evidence that Sprint 3 is complete.
6. Required Sprint 3 changes made after creation of `feature/sprint-4` must be merged forward into Sprint 4.
7. Regression testing must follow any Sprint 3 merge-forward.
8. Merge conflicts must be resolved before dependent Sprint 4 integration proceeds.
9. Team members should communicate overlapping file ownership through the team group chat.
10. Official Microsoft Project dates stay unchanged unless the team approves a schedule change.

## 5. Sprint 4 WBS Alignment

| WBS  | Task                                                        | Start  | Finish | Days | Official Owner | Predecessors            |
| ---- | ----------------------------------------------------------- | ------ | ------ | ---: | -------------- | ----------------------- |
| 7    | Sprint 4 - Job Matching, AI Integration, and Administration | 21 Sep | 02 Oct |   10 | All Members    |                         |
| 7.1  | Sprint 4 Planning                                           | 21 Sep | 21 Sep |    1 | All Members    | 6.11                    |
| 7.2  | Job Description Extraction and Matching                     | 21 Sep | 25 Sep |    5 | Jerald         | 7.1, 5.5                |
| 7.3  | OpenAI Service Integration                                  | 21 Sep | 24 Sep |    4 | MD             | 7.1, 6.2                |
| 7.4  | AI Response Validation and Error Handling                   | 24 Sep | 28 Sep |    3 | Jerald         | 7.3                     |
| 7.5  | Job Matching Interface                                      | 24 Sep | 29 Sep |    4 | Joyee          | 7.2                     |
| 7.6  | Admin Models and API                                        | 22 Sep | 28 Sep |    5 | MD             | 7.1                     |
| 7.7  | Admin Dashboard Interface                                   | 23 Sep | 29 Sep |    5 | Joyee          | 7.1                     |
| 7.8  | Role Permissions and Audit Records                          | 28 Sep | 30 Sep |    3 | Jerald         | 7.6, 4.4                |
| 7.9  | Sprint 4 Integration and Testing                            | 01 Oct | 02 Oct |    2 | All Members    | 7.4, 7.5, 7.6, 7.7, 7.8 |
| 7.10 | Sprint 4 Review and Retrospective                           | 02 Oct | 02 Oct |    1 | All Members    | 7.9                     |
| 7.11 | Feature Complete                                            | 02 Oct | 02 Oct |    0 | All Members    | 7.10                    |

## 6. Sprint 4 Functional Requirements

Sprint 4 directly supports the following functional requirements.

### FR-07 Job Description Matching

Students should paste one job description and receive a structured comparison showing matched and missing requirements.

Primary implementation tasks:

* WBS 7.2
* WBS 7.5
* WBS 7.9

The job-matching workflow should reuse existing Student Profile, skill, skill-gap, and readiness information where appropriate.

Job matching should preserve deterministic scoring and comparison behaviour.

Generative AI output should not silently replace deterministic matching results.

### FR-14 Basic Administration

Authorised administrators should manage approved GradNavi administrative information.

Primary implementation tasks:

* WBS 7.6
* WBS 7.7
* WBS 7.8
* WBS 7.9

Administrator security must be enforced by the Django backend.

The React frontend must not act as the security boundary.

### FR-15 Admin Analytics

The current Product Backlog provisionally maps Admin Analytics to:

* WBS 7.6 Admin Models and API.
* WBS 7.7 Admin Dashboard Interface.

The team must confirm whether Sprint 4 includes aggregated analytics before implementation begins.

If approved, the team must define:

* Required statistics.
* Backend aggregation behaviour.
* Frontend presentation.
* Ownership.
* Testing requirements.
* Acceptance evidence.

### FR-18 Audit and Error Handling

Sprint 4 supports controlled external-service failures and critical-action audit behaviour.

Primary implementation tasks:

* WBS 7.4
* WBS 7.8
* WBS 7.9

The application should return controlled errors instead of exposing internal exceptions, stack traces, credentials, or sensitive information.

Critical permission-sensitive operations should create appropriate audit evidence according to the approved implementation.

## 7. WBS 7.2 Job Description Extraction and Matching

Owner: Jerald

WBS 7.2 implements the backend logic required for FR-07 Job Description Matching.

The workflow should accept one job description supplied by the authenticated Student.

Expected responsibilities include:

* Authenticate the Student.
* Accept job-description text.
* Validate job-description input.
* Treat job-description text as untrusted user-supplied content.
* Extract relevant skills and requirements.
* Compare extracted requirements with Student Profile information.
* Identify matched requirements.
* Identify missing requirements.
* Return structured matching results.
* Preserve Student ownership rules.
* Return controlled validation errors.
* Keep deterministic matching separate from generative AI output.

WBS 7.2 should reuse existing GradNavi skill, skill-gap, and readiness structures where appropriate instead of creating conflicting scoring models.

Automated tests and evidence should be completed before WBS 7.2 is treated as ready for integration.

## 8. WBS 7.3 OpenAI Service Integration

Owner: MD

WBS 7.3 connects the existing Sprint 3 AI service boundary to the approved external OpenAI service.

Sprint 3 already established:

* Prompt templates.
* Safety rules.
* Resume generation service boundaries.
* Cover-letter generation service boundaries.
* Interview generation service boundaries.
* Interview feedback service boundaries.

WBS 7.3 should connect those services to the external AI provider without tightly coupling feature business logic to provider-specific code.

Expected responsibilities include:

* Configure the backend AI provider.
* Store AI credentials only in backend configuration.
* Keep credentials outside source-controlled frontend files.
* Route AI operations through the Django backend.
* Reuse the Sprint 3 prompt and safety layer.
* Use defined provider timeouts.
* Return provider responses to the application validation layer.
* Prevent direct React-to-provider requests.

The intended flow is:

```text
Authenticated Student
        |
        v
React Frontend
        |
        v
Django REST API
        |
        v
Feature Service
        |
        v
Prompt and Safety Layer
        |
        v
AI Provider Boundary
        |
        v
OpenAI Service
        |
        v
AI Response Validation
        |
        v
Structured Application Result
```

## 9. WBS 7.4 AI Response Validation and Error Handling

Owner: Jerald

WBS 7.4 validates external AI responses before GradNavi returns generated content to the user interface.

Expected responsibilities include:

* Validate expected AI response structure.
* Detect malformed responses.
* Detect incomplete responses.
* Reject responses which do not satisfy required application contracts.
* Return controlled provider failure states.
* Handle timeout conditions.
* Handle unavailable-service conditions.
* Prevent provider errors from exposing internal details.
* Prevent secrets from appearing in frontend error responses.
* Protect personal information in logs.
* Preserve deterministic recommendation and readiness behaviour during AI failure.

AI-provider failure must not modify:

* Career recommendation scores.
* Skill-gap calculations.
* Career-readiness scores.
* Job-matching deterministic results.

Tests should cover valid responses and controlled failure paths.

## 10. WBS 7.5 Job Matching Interface

Owner: Joyee

WBS 7.5 provides the Student-facing interface for FR-07 Job Description Matching.

The interface should support:

* Job-description text input.
* Match request submission.
* Loading state.
* Empty state.
* Validation state.
* Matched requirements.
* Missing requirements.
* Controlled API-error state.
* Responsive layouts.
* Keyboard-accessible controls.

The interface should consume the API contract established by WBS 7.2.

The interface should clearly distinguish information supported by the Student Profile from requirements missing from the current profile.

## 11. WBS 7.6 Admin Models and API

Owner: MD

WBS 7.6 provides the backend foundation for Basic Administration.

Expected responsibilities include:

* Approved administrator data models.
* Administrator APIs.
* Authentication checks.
* Administrator authorisation requirements.
* Validation.
* Controlled API errors.
* Data ownership and integrity controls where applicable.

WBS 7.6 provides the backend dependency required by WBS 7.8 Role Permissions and Audit Records.

The team must confirm whether FR-15 Admin Analytics belongs inside WBS 7.6 before implementation begins.

## 12. WBS 7.7 Admin Dashboard Interface

Owner: Joyee

WBS 7.7 provides the administrator-facing interface.

The interface should support the approved administration workflows exposed by WBS 7.6.

Expected interface states include:

* Loading.
* Empty.
* Validation.
* Permission denied.
* API error.
* Successful administration actions.

The Admin Dashboard should follow the existing GradNavi responsive and accessibility standards.

The team must confirm whether FR-15 Admin Analytics displays belong inside WBS 7.7 before implementation begins.

## 13. WBS 7.8 Role Permissions and Audit Records

Owner: Jerald

WBS 7.8 completes the main Sprint 4 role and audit controls.

Expected responsibilities include:

* Enforce Student and Administrator role boundaries.
* Restrict administrator endpoints to authorised users.
* Reject Student access to administrator-only operations.
* Protect privileged functions from frontend manipulation.
* Verify permissions through direct backend API testing.
* Define critical actions requiring audit records.
* Store required audit information.
* Prevent sensitive information from being stored unnecessarily in audit records.
* Test authorised behaviour.
* Test unauthorised behaviour.
* Test role isolation.
* Test audit-record creation.

Security-sensitive decisions must be enforced by Django rather than React.

## 14. WBS 7.9 Sprint 4 Integration and Testing

Owner: All Members

WBS 7.9 verifies that Sprint 4 components operate together with the existing GradNavi system.

Minimum integrated flows should include:

### Job Matching Flow

```text
Login
  -> Student Profile
  -> Job Matching
  -> Enter Job Description
  -> Submit
  -> Extract Requirements
  -> Compare with Student Profile
  -> Display Matched Requirements
  -> Display Missing Requirements
```

### Resume AI Flow

```text
Login
  -> Student Profile
  -> Resume Builder
  -> Generate Draft
  -> OpenAI Provider
  -> Validate Response
  -> Review/Edit Draft
```

### Cover Letter AI Flow

```text
Login
  -> Student Profile
  -> Cover Letter Builder
  -> Enter Job Description
  -> Generate Draft
  -> OpenAI Provider
  -> Validate Response
  -> Review/Edit Draft
```

### Interview AI Flow

```text
Login
  -> Interview Preparation
  -> Generate Questions
  -> OpenAI Provider
  -> Validate Response
  -> Enter Answer
  -> Submit Answer
  -> Receive Validated Feedback
```

### Administration Flow

```text
Administrator Login
  -> Admin Dashboard
  -> Approved Administration Action
  -> Backend Permission Check
  -> Data Update
  -> Audit Record
```

### Permission Rejection Flow

```text
Student Login
  -> Attempt Administrator Operation
  -> Backend Permission Check
  -> Access Denied
```

Sprint 4 integration testing should also include regression checks for:

* Authentication.
* Student Profile.
* Career recommendations.
* Recommendation explanations.
* Skill-gap analysis.
* Career-readiness scoring.
* Learning suggestions.
* Career roadmap.
* Resume generation.
* Cover-letter generation.
* Interview preparation.

## 15. Sprint 4 Testing Evidence

Sprint 4 should continue the evidence process used during earlier Sprints.

Proposed test tracker:

`docs/testing/sprint-4-test-cases.xlsx`

Proposed evidence directory:

`docs/testing/evidence/sprint-4/`

Testing evidence should distinguish:

* Pass.
* Fail.
* Blocked.
* Not Run.
* Retest where required.

Blocked tests should not be recorded as failed tests.

Evidence should identify the related WBS task and test case.

## 16. Schedule Alignment Items

The current Product Backlog identifies several requirements requiring explicit schedule decisions.

### FR-13 Progress Dashboard

The requirement stays in the GradNavi V1 backlog, but the current Microsoft Project schedule does not identify a dedicated implementation task.

The team should decide whether FR-13:

* Fits inside an existing Sprint 4 interface task.
* Requires a separate approved task.
* Moves to another approved Sprint.
* Requires a documented scope change.

### FR-15 Admin Analytics

FR-15 currently has a provisional mapping to WBS 7.6 and WBS 7.7.

The team should confirm the expected analytics scope before implementation.

### FR-16 AI Content Review

Generated AI-supported content should stay reviewable and editable before final use.

The team should confirm which Sprint 3 and Sprint 4 tasks formally satisfy this requirement.

### FR-17 Data Deletion

The current WBS does not identify a dedicated task for deletion of generated documents or profile-deletion requests.

The team should confirm:

* Sprint.
* Owner.
* Backend work.
* Frontend work where required.
* Permission behaviour.
* Testing.
* Acceptance evidence.

These requirements should not silently enter or leave Sprint 4 scope.

Any approved scheduling change should follow project change control.

## 17. Sprint 4 Risks

### Risk 1 - Sprint 3 Frontend Delay

WBS 6.5 and WBS 6.7 currently block complete Sprint 3 integration.

Control:

* Prioritise remaining Sprint 3 frontend implementation.
* Complete WBS 6.8 integration.
* Complete WBS 6.9 testing.
* Finish Sprint 3 review and retrospective.
* Record Sprint 3 closure evidence.

### Risk 2 - External AI Service Failure

External AI requests may fail, time out, or return invalid responses.

Control:

* Keep provider communication behind the backend service boundary.
* Validate provider responses.
* Implement controlled error states.
* Test provider failures.

### Risk 3 - Administrator Permission Exposure

Incorrect permission controls may expose administrator functions to Student users.

Control:

* Enforce permissions in Django.
* Test direct API access using different roles.
* Do not rely on hidden frontend controls for security.

### Risk 4 - Scope Alignment Gaps

FR-13, FR-15, FR-16, and FR-17 do not all have clear dedicated WBS mapping.

Control:

* Record explicit team decisions.
* Update the Microsoft Project baseline first when approved scheduling changes are required.
* Align WBS, backlog, task leads, roadmap, and GitHub records afterward.

### Risk 5 - Frontend Integration Delay

Incomplete interfaces may block Sprint 4 integration in the same way incomplete frontend work affected previous Sprints.

Control:

* Start approved frontend work once required API contracts and design inputs are stable.
* Team members with available capacity should support frontend implementation where ownership and branch coordination are clearly recorded.
* Avoid multiple members editing the same files without coordination.

## 18. Branch Strategy

Shared Sprint 4 integration branch:

`feature/sprint-4`

WBS 7.1 planning branch:

`jerald/wbs-7.1-sprint-4-planning`

Planning document:

`docs/project-management/sprint-4-plan.md`

Implementation tasks should use separate WBS branches created from the latest `feature/sprint-4`.

Pull requests for Sprint 4 implementation should target:

`feature/sprint-4`

Sprint 4 implementation branches should not target `main` directly.

If required Sprint 3 changes occur after Sprint 4 branch creation:

1. Complete and verify the Sprint 3 change.
2. Merge the approved change into `feature/sprint-3`.
3. Merge the updated Sprint 3 baseline forward into `feature/sprint-4`.
4. Resolve conflicts.
5. Run regression testing.
6. Continue dependent Sprint 4 implementation after verification.

## 19. Definition of Ready

A Sprint 4 WBS task is ready when:

* Requirement scope is understood.
* Acceptance behaviour is clear.
* Official owner is confirmed.
* Dependencies are available.
* Required API contract or design input is available.
* Required previous WBS work has reached an appropriate state.
* Branch ownership is clear.
* The task does not conflict with another member's active implementation work.

## 20. Definition of Done

A Sprint 4 WBS task is done when:

* Required implementation is complete.
* Acceptance behaviour is satisfied.
* Automated or manual testing required by the task passes.
* No unresolved critical defect affects the task.
* Security and permission behaviour has been checked where relevant.
* Validation and error behaviour has been checked.
* Integration with dependent components has been verified.
* Required evidence has been recorded.
* Relevant documentation has been updated.
* The team accepts the completed work.

## 21. Sprint 4 Exit Criteria

Sprint 4 reaches:

`WBS 7.11 Feature Complete`

only after the required Sprint 4 implementation and integration work is complete.

Before Feature Complete:

* WBS 7.2 Job Description Extraction and Matching must be integrated.
* WBS 7.3 OpenAI Service Integration must be integrated.
* WBS 7.4 AI Response Validation and Error Handling must be integrated.
* WBS 7.5 Job Matching Interface must be integrated.
* WBS 7.6 Admin Models and API must be integrated.
* WBS 7.7 Admin Dashboard Interface must be integrated.
* WBS 7.8 Role Permissions and Audit Records must be integrated.
* WBS 7.9 Sprint 4 Integration and Testing must finish.
* Required regression testing must pass.
* No unresolved critical defect should block the core application.
* Required test evidence must be recorded.
* Schedule-alignment decisions for FR-13, FR-15, FR-16, and FR-17 must be documented.
* WBS 7.10 Sprint 4 Review and Retrospective must finish.

Only then should WBS 7.11 Feature Complete be reached.
