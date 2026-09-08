# GradNavi Sprint 3 Plan

Status: Draft for team review

WBS: 6.1 Sprint 3 Planning

Sprint: Sprint 3 - Application Documents and Interview Preparation

Planned Sprint dates: 7 September to 18 September 2026

Official owner of WBS 6.1: All Members

Shared Sprint 3 integration branch:

`feature/sprint-3`

## 1. Purpose

This document defines the GradNavi Sprint 3 implementation plan.

Sprint 3 focuses on AI-assisted application-document generation and interview preparation.

The planned Sprint 3 increment includes:

- AI prompt templates and safety rules.
- Resume generation backend.
- Cover-letter generation backend.
- Resume and cover-letter interface.
- Interview question and feedback API.
- Interview preparation interface.
- Document and interview integration.
- Sprint 3 testing.
- Sprint review and retrospective.

This document prepares the team for Sprint 3 implementation and integration.

WBS 6.1 stays under team review until all members agree on the plan.

## 2. Planning Basis

This Sprint 3 plan aligns with the current repository planning and design documents:

- `docs/project-management/work-breakdown-structure.md`
- `docs/project-management/product-backlog.md`
- `docs/project-management/task-leads.md`
- `docs/project-management/responsibility-matrix.md`
- `docs/project-management/roadmap-and-milestones.md`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`
- `docs/system-design/security-architecture.md`
- `docs/system-design/rest-api-design.md`

The Microsoft Project schedule stays the authoritative planning baseline for official task dates, task ownership, dependencies, and milestones.

## 3. Sprint 3 Goal

The primary Sprint 3 outcome is:

> AI-assisted resume, cover-letter, and interview-preparation functions.

Sprint 3 should establish one coherent user flow where an authenticated Student uses approved GradNavi profile information to receive editable AI-supported application content and interview-preparation support.

Generated content must support Student review before final use.

Sprint 3 must keep deterministic career recommendation and readiness calculations separate from generative AI content.

## 4. Controlled Early-Start Decision

Sprint 3 starts under a controlled early-start arrangement.

The approved WBS lists:

`WBS 5.11 Sprint 2 Complete`

as the predecessor of:

`WBS 6.1 Sprint 3 Planning`

At the current planning checkpoint, Sprint 2 is not formally closed because remaining teammate-owned work, integration testing, review, retrospective, and the Sprint 2 completion milestone are still pending.

The team is using an early-start overlap so members who completed their current Sprint 2 responsibilities do not stay idle.

This early start follows these rules:

1. Sprint 2 stays formally open.
2. Sprint 2 work continues through `feature/sprint-2`.
3. Sprint 3 work proceeds through `feature/sprint-3`.
4. `feature/sprint-3` was created from the current shared Sprint 2 baseline.
5. Creation of `feature/sprint-3` does not count as evidence that WBS 5.11 is complete.
6. When Sprint 2 reaches WBS 5.11, the final `feature/sprint-2` state must merge into `feature/sprint-3`.
7. Full regression testing must follow that merge.
8. Any merge conflict must be resolved before further dependent Sprint 3 integration.
9. Team members should communicate file ownership and overlapping work in the group chat.
10. Official Microsoft Project dates stay unchanged unless the team approves a schedule change.

## 5. Sprint 3 WBS Alignment

| WBS | Task | Start | Finish | Days | Official Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 6 | Sprint 3 - Application Documents and Interview Preparation | 07 Sep | 18 Sep | 10 | All Members | |
| 6.1 | Sprint 3 Planning | 07 Sep | 07 Sep | 1 | All Members | 5.11 |
| 6.2 | AI Prompt Templates and Safety Rules | 07 Sep | 09 Sep | 3 | Jerald | 6.1, 2.7 |
| 6.3 | Resume Generation Backend | 09 Sep | 14 Sep | 4 | MD | 6.2 |
| 6.4 | Cover Letter Generation Backend | 09 Sep | 14 Sep | 4 | MD | 6.2 |
| 6.5 | Resume and Cover Letter Interface | 09 Sep | 15 Sep | 5 | Joyee | 6.1, 3.8 |
| 6.6 | Interview Question and Feedback API | 14 Sep | 17 Sep | 4 | Jerald | 6.2 |
| 6.7 | Interview Preparation Interface | 14 Sep | 17 Sep | 4 | Joyee | 6.5 |
| 6.8 | Document and Interview Integration | 17 Sep | 18 Sep | 2 | All Members | 6.3, 6.4, 6.5, 6.6, 6.7 |
| 6.9 | Sprint 3 Testing | 17 Sep | 18 Sep | 2 | All Members | 6.8 |
| 6.10 | Sprint 3 Review and Retrospective | 18 Sep | 18 Sep | 1 | All Members | 6.9 |
| 6.11 | Sprint 3 Complete | 18 Sep | 18 Sep | 0 | All Members | 6.10 |

## 6. Sprint 3 Functional Requirements

Sprint 3 directly supports these functional requirements.

### FR-08 Resume Builder

The Student should receive an editable resume draft generated from approved Student Profile information.

Primary implementation tasks:

- WBS 6.2
- WBS 6.3
- WBS 6.5
- WBS 6.8
- WBS 6.9

### FR-09 Cover-Letter Builder

The Student should receive an editable cover letter tailored to one selected job description.

Primary implementation tasks:

- WBS 6.2
- WBS 6.4
- WBS 6.5
- WBS 6.8
- WBS 6.9

Sprint 3 cover-letter generation must not implement the separate FR-07 job-description matching feature.

FR-07 stays planned for Sprint 4.

Sprint 3 may use one supplied job description as generation context without implementing job-matching scores or matched and missing requirement analysis.

### FR-10 Interview Preparation

The Student should receive text-based interview questions and feedback on typed answers.

Primary implementation tasks:

- WBS 6.2
- WBS 6.6
- WBS 6.7
- WBS 6.8
- WBS 6.9

## 7. Supporting Requirements Requiring Team Attention

### FR-16 AI Content Review

FR-16 states that users should review and edit generated AI-supported content before saving.

The current Product Backlog does not map FR-16 to a dedicated Microsoft Project task.

For Sprint 3 planning, editable generated content is treated as an important cross-cutting requirement.

The team must confirm whether persistence and final save behaviour belong to Sprint 3 or require a formal schedule update.

### FR-17 Data Deletion

FR-17 includes deletion of saved generated documents.

The current Product Backlog does not map FR-17 to a dedicated Microsoft Project task.

Sprint 3 must not silently add document-storage and deletion scope without team approval.

If generated-document persistence is added during Sprint 3, the team must first confirm:

- Data model impact.
- API impact.
- Privacy impact.
- Testing impact.
- Schedule impact.
- WBS ownership.

## 8. Sprint 3 AI Architecture Decision

Sprint 3 and Sprint 4 have separate AI responsibilities.

Sprint 3 includes:

- Prompt-template design.
- Safety rules.
- Structured AI input preparation.
- Resume-generation orchestration.
- Cover-letter-generation orchestration.
- Interview-question orchestration.
- Interview-feedback orchestration.
- AI-facing service boundaries.
- API contracts.
- Frontend workflows.
- Test doubles or controlled development substitutes where required.

Sprint 4 includes:

`WBS 7.3 OpenAI Service Integration`

and:

`WBS 7.4 AI Response Validation and Error Handling`

The Sprint 3 implementation should avoid tightly coupling application features directly to one AI provider.

Sprint 3 backend code should define clear service boundaries so the OpenAI provider implementation introduced in Sprint 4 plugs into the existing application flow without rewriting Resume, Cover Letter, or Interview features.

The intended GradNavi AI flow is:

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
Validated Generated Result
        |
        v
Editable Frontend Draft
```

Direct React-to-AI-provider communication is outside the GradNavi architecture.

## 9. WBS 6.2 AI Prompt Templates and Safety Rules

Owner: Jerald

WBS 6.2 establishes the shared AI behaviour required by WBS 6.3, WBS 6.4, and WBS 6.6.

The implementation should define separate prompt contracts for:

- Resume generation.
- Cover-letter generation.
- Interview-question generation.
- Interview-answer feedback.

The prompt layer should separate:

- System instructions.
- Trusted GradNavi application context.
- Structured Student Profile data.
- User-supplied text.
- Job-description text.
- Output-format requirements.

### 9.1 Safety Baseline

The Sprint 3 AI safety baseline should include:

- Do not invent Student qualifications.
- Do not invent employment history.
- Do not invent education.
- Do not invent projects.
- Do not invent certifications.
- Do not invent technical skills.
- Do not claim achievements absent from Student Profile data.
- Generated content must be presented as a draft.
- Student review must occur before final use.
- Unnecessary personal information must not be sent to an external AI provider.
- AI credentials must stay in backend configuration.
- Frontend code must not contain AI API keys.
- User-supplied job descriptions must be treated as untrusted input data.
- Job-description text must not override GradNavi system or safety instructions.
- Generated responses must use defined output expectations.
- AI-service failure must result in a controlled application state.
- Logs must not contain passwords, JWTs, API keys, or unnecessary personal information.
- Protected attributes must not become direct scoring factors.
- AI-generated content must not alter deterministic recommendation or readiness scores.

These rules require team review before WBS 6.2 is marked complete.

## 10. WBS 6.3 Resume Generation Backend

Owner: MD

The Resume Generation Backend should consume approved Student Profile information through a defined backend service boundary.

Expected responsibilities:

- Authenticate the Student.
- Retrieve only the authenticated Student's profile information.
- Build approved structured resume input.
- Pass input through the WBS 6.2 prompt and safety layer.
- Request resume-draft generation through the AI service boundary.
- Return a structured editable draft.
- Handle missing profile information.
- Return controlled validation and service errors.
- Avoid changing deterministic recommendation or readiness results.

The backend must not fabricate missing Student information to make a resume appear more complete.

## 11. WBS 6.4 Cover Letter Generation Backend

Owner: MD

The Cover Letter Generation Backend should combine:

- Approved Student Profile information.
- One selected or pasted job description.
- WBS 6.2 prompt rules.
- WBS 6.2 safety rules.

Expected responsibilities:

- Authenticate the Student.
- Validate the job-description input.
- Retrieve only the authenticated Student's profile information.
- Minimise unnecessary personal data.
- Treat job-description content as untrusted user-supplied data.
- Generate an editable cover-letter draft through the AI service boundary.
- Avoid inventing qualifications or experience.
- Return controlled validation and service errors.

WBS 6.4 does not implement FR-07 Job Description Matching.

## 12. WBS 6.5 Resume and Cover Letter Interface

Owner: Joyee

The interface should support:

- Resume generation request.
- Cover-letter generation request.
- Job-description input for cover-letter context.
- Loading states.
- Controlled validation states.
- Empty states.
- AI-service error states.
- Editable generated content.
- Clear distinction between generated draft and final Student-edited content.
- Keyboard-accessible forms and controls.
- Responsive layouts.

WBS 6.5 depends on WBS 3.8 High-Fidelity UI Design.

Any design dependency that stays incomplete should be communicated before implementation.

## 13. WBS 6.6 Interview Question and Feedback API

Owner: Jerald

The Interview Preparation API should provide text-based interview preparation.

Expected functions:

- Generate interview questions.
- Accept one typed Student answer.
- Generate structured feedback on the typed answer.
- Return controlled validation errors.
- Return controlled AI-service errors.
- Enforce Student authentication and ownership rules where stored Student data is used.
- Pass AI operations through the WBS 6.2 prompt and safety layer.

Interview feedback should support improvement and preparation.

The API must not represent AI feedback as a guaranteed hiring outcome or professional certification of interview ability.

## 14. WBS 6.7 Interview Preparation Interface

Owner: Joyee

The interface should support:

- Displaying generated interview questions.
- Selecting or progressing through questions.
- Entering typed answers.
- Submitting an answer for feedback.
- Displaying structured feedback.
- Loading states.
- Empty states.
- Validation errors.
- AI-service errors.
- Keyboard navigation.
- Responsive layouts.

## 15. WBS 6.8 Document and Interview Integration

Owner: All Members

WBS 6.8 should prove that Sprint 3 components work together through the shared application architecture.

Minimum integrated flows:

### Resume Flow

```text
Login
  -> Student Profile
  -> Resume Builder
  -> Generate Draft
  -> Review/Edit Draft
```

### Cover-Letter Flow

```text
Login
  -> Student Profile
  -> Cover Letter Builder
  -> Enter Job Description
  -> Generate Draft
  -> Review/Edit Draft
```

### Interview Flow

```text
Login
  -> Interview Preparation
  -> Generate Questions
  -> Enter Typed Answer
  -> Submit Answer
  -> Receive Feedback
```

Integration must preserve authentication, Student ownership, validation, privacy, and controlled error behaviour.

## 16. Sprint 3 AI Feature Integration Diagram

Sprint 3 will include one dedicated integration diagram.

Planned diagram title:

`GradNavi Sprint 3 AI Feature Integration Flow`

Planned source file:

`docs/system-design/images/sprint-3-ai-feature-integration-flow.drawio`

Planned exported image:

`docs/system-design/images/sprint-3-ai-feature-integration-flow.png`

The diagram should show:

```text
Student
   |
   v
React Frontend
   |
   v
Django REST API
   |
   +----------------------+----------------------+
   |                      |                      |
   v                      v                      v
Resume Service      Cover Letter Service   Interview Service
   |                      |                      |
   +----------------------+----------------------+
                          |
                          v
                 Prompt + Safety Layer
                          |
                          v
                 AI Service Boundary
                          |
                          v
                Structured AI Result
                          |
                          v
                 Django Validation
                          |
                          v
                  React Interface
                          |
                          v
                   Student Review
```

The final visual diagram will be reviewed separately from this planning document.

## 17. Security and Privacy Requirements

Sprint 3 AI functions must follow the existing GradNavi security architecture.

Required controls include:

- Authentication through the Django backend.
- Backend ownership enforcement.
- No direct frontend database access.
- No direct frontend AI-provider access.
- AI provider credentials stored only in backend configuration.
- Minimum required personal data sent to external services.
- Removal of unnecessary personal information before AI requests.
- Controlled API errors.
- No stack traces or secrets returned to the frontend.
- AI responses treated as external input.
- Security-sensitive decisions enforced by Django rather than React.
- Protected Student information isolated between users.

## 18. Non-Functional Requirements

Sprint 3 should consider the existing GradNavi quality requirements.

### Usability

Students should use the main workflow without specialist training.

### Responsive Design

Core Sprint 3 interfaces should support current desktop, tablet, and mobile browser widths.

### Performance

Normal non-AI API requests target the documented response expectation.

AI requests should show a loading state and use a configured timeout.

### Security

Protected functions require authenticated and authorised access.

### Privacy

Only required personal information should be processed.

### Maintainability

AI, backend, frontend, and database responsibilities should stay separated.

### Accessibility

Forms should use labels, keyboard access, readable contrast, and meaningful validation messages.

### Compatibility

Sprint 3 core pages should support current Chrome, Edge, and Firefox versions.

### Testability

Priority Sprint 3 functions should have acceptance tests and automated tests where practical.

### Ethical AI

Generated content should communicate appropriate limitations and avoid using protected attributes as direct scoring factors.

## 19. Branch Strategy

Shared Sprint 3 integration branch:

`feature/sprint-3`

Nobody should implement a WBS task directly on `feature/sprint-3`.

Each implementation task should use a separate branch.

Recommended branches:

```text
jerald/wbs-6.1-sprint-3-planning
jerald/wbs-6.2-ai-prompt-safety
enamul/wbs-6.3-resume-generation-backend
enamul/wbs-6.4-cover-letter-generation-backend
joyee/wbs-6.5-document-interface
jerald/wbs-6.6-interview-api
joyee/wbs-6.7-interview-interface
```

Each completed branch should use a pull request targeting:

`feature/sprint-3`

Before creating a task branch:

1. Switch to `feature/sprint-3`.
2. Pull the latest remote state.
3. Confirm the working tree is clean.
4. Create the WBS branch.
5. Push the WBS branch early.
6. Communicate the branch name to the team.

## 20. Sprint 2 to Sprint 3 Merge-Forward Strategy

Sprint 2 continues separately on:

`feature/sprint-2`

When WBS 5.11 is formally complete:

1. Update local `feature/sprint-2`.
2. Confirm the final Sprint 2 state.
3. Update local `feature/sprint-3`.
4. Merge the final `feature/sprint-2` into `feature/sprint-3`.
5. Resolve conflicts through team review.
6. Run Django checks.
7. Apply required migrations.
8. Run backend regression tests.
9. Run frontend lint.
10. Run the frontend production build.
11. Verify Sprint 2 functionality stays available.
12. Verify Sprint 3 work stays functional.
13. Push the integrated `feature/sprint-3`.

Sprint 3 feature work should stop temporarily if the merge reveals a critical regression.

## 21. Integration Order

The planned Sprint 3 integration sequence is:

```text
6.1 Sprint 3 Planning
        |
        v
6.2 AI Prompt Templates and Safety Rules
        |
        +-----------------------+
        |                       |
        v                       v
6.3 Resume Backend       6.4 Cover Letter Backend
        |                       |
        +-----------+-----------+
                    |
                    v
        6.5 Document Interface

6.2 AI Prompt Templates and Safety Rules
        |
        v
6.6 Interview Question and Feedback API
        |
        v
6.7 Interview Preparation Interface

6.3 + 6.4 + 6.5 + 6.6 + 6.7
                    |
                    v
        6.8 Document and Interview Integration
                    |
                    v
              6.9 Sprint 3 Testing
                    |
                    v
        6.10 Review and Retrospective
                    |
                    v
              6.11 Sprint 3 Complete
```

## 22. Integration Contracts

| Producer | Consumer | Contract to agree |
| --- | --- | --- |
| Student Profile | Resume Backend | Approved Student profile fields |
| Student Profile | Cover Letter Backend | Approved Student profile fields |
| WBS 6.2 | Resume Backend | Resume prompt and safety contract |
| WBS 6.2 | Cover Letter Backend | Cover-letter prompt and safety contract |
| WBS 6.2 | Interview API | Interview prompt and safety contract |
| Resume Backend | Document Interface | Resume generation response structure |
| Cover Letter Backend | Document Interface | Cover-letter generation response structure |
| Interview API | Interview Interface | Question and feedback response structure |
| AI Service Boundary | Feature Services | Provider-independent request/result contract |

Producer contract changes must be communicated to the consumer owner before integration.

## 23. Sprint 3 Testing Strategy

Formal Sprint 3 testing belongs to WBS 6.9 after WBS 6.8 integration.

Implementation tasks should still include automated tests before their pull requests merge.

Testing should include:

- Unit testing.
- API testing.
- Authentication testing.
- Student ownership testing.
- Prompt construction testing.
- Safety-rule testing.
- Missing-profile testing.
- Invalid-input testing.
- AI-service failure testing.
- Resume generation flow.
- Cover-letter generation flow.
- Interview-question flow.
- Interview-feedback flow.
- Frontend loading states.
- Frontend validation states.
- Frontend error states.
- Responsive layout checks.
- Accessibility checks.
- Browser checks.
- Regression testing after the final Sprint 2 merge-forward.

A Sprint 3 test plan and test tracker should be prepared before formal WBS 6.9 execution.

Suggested files:

```text
docs/testing/sprint-3-test-plan.md
docs/testing/sprint-3-test-cases.xlsx
docs/testing/evidence/sprint-3/
```

## 24. AI Safety Test Areas

WBS 6.2 and later Sprint 3 testing should verify:

- Missing Student data is not invented.
- Prompt templates preserve trusted instructions.
- Job-description text stays treated as user data.
- User input does not override system safety instructions.
- AI requests exclude unnecessary personal information.
- API keys do not appear in frontend code.
- API keys do not appear in logs or evidence.
- Generated outputs are identified as drafts.
- Controlled behaviour occurs when the AI service is unavailable.
- Malformed AI results do not reach the frontend as trusted application data.
- Deterministic career and readiness scores stay unchanged by generated AI content.

## 25. Current Dependencies and Blockers

### Sprint 2 Completion

Status: Pending

Impact:

The approved predecessor of WBS 6.1 has not reached formal completion.

Response:

Use the controlled early-start process and merge final Sprint 2 changes forward once WBS 5.11 is complete.

### WBS 3.8 High-Fidelity UI Design

Status: In progress at the current planning checkpoint.

Impact:

WBS 6.5 depends on WBS 3.8.

Response:

Joyee should complete or agree on the required UI design baseline before WBS 6.5 is treated as fully ready.

### WBS 2.7 Security, Privacy and Ethical Requirements

Impact:

WBS 6.2 depends on WBS 2.7.

Response:

WBS 6.2 must review and align with the existing security architecture, privacy requirements, ethical AI requirement, and approved team decisions before implementation is marked complete.

### OpenAI Provider Integration

Status:

Planned under WBS 7.3 in Sprint 4.

Impact:

Sprint 3 must avoid provider-specific coupling.

Response:

Use a clear AI service boundary so Sprint 4 OpenAI integration plugs into the Sprint 3 feature services.

## 26. Risk Register for Sprint 3

| Risk | Effect | Response |
| --- | --- | --- |
| Sprint 2 work finishes late | Merge conflicts or regression risk | Merge final Sprint 2 into Sprint 3 and run regression tests |
| Prompt contracts change after dependent coding starts | Rework in WBS 6.3, 6.4, or 6.6 | Approve WBS 6.2 contracts before dependent implementation |
| Resume or cover letter invents Student information | Misleading generated content | Restrict generation to approved profile facts and test fabrication cases |
| Job description contains hostile or irrelevant instructions | Prompt-safety failure | Treat job-description content as untrusted data |
| AI provider outage or timeout | Generation flow unavailable | Use controlled error and retry behaviour |
| Sensitive information enters AI request | Privacy risk | Minimise external request data |
| AI key appears in frontend or Git | Credential exposure | Keep credentials server-side and outside Git |
| Frontend and backend contracts diverge | Integration failure | Agree response schemas before implementation |
| UI design is incomplete | WBS 6.5 delay | Finalise required design states and communicate blockers |
| Sprint 3 work overlaps Sprint 2 files | Merge conflict | Communicate file ownership and merge carefully |

## 27. Team Responsibilities

### Jerald

Primary Sprint 3 responsibilities:

- WBS 6.2 AI Prompt Templates and Safety Rules.
- WBS 6.6 Interview Question and Feedback API.
- Shared WBS 6.8 integration.
- Shared WBS 6.9 testing.
- Shared Sprint review and retrospective.

Additional support:

- AI security and privacy alignment.
- Backend integration support.
- Regression support.
- Team support when another member reports a blocker.

### MD

Primary Sprint 3 responsibilities:

- WBS 6.3 Resume Generation Backend.
- WBS 6.4 Cover Letter Generation Backend.
- Shared WBS 6.8 integration.
- Shared WBS 6.9 testing.
- Shared Sprint review and retrospective.

### Joyee

Primary Sprint 3 responsibilities:

- WBS 6.5 Resume and Cover Letter Interface.
- WBS 6.7 Interview Preparation Interface.
- Shared WBS 6.8 integration.
- Shared WBS 6.9 testing.
- Shared Sprint review and retrospective.

### All Members

All members are responsible for:

- WBS 6.1 planning review.
- Contract communication.
- Integration.
- Test evidence for owned features.
- Defect communication.
- WBS 6.8.
- WBS 6.9.
- WBS 6.10.
- WBS 6.11.

Helping another member does not change official WBS ownership.

Support work should be recorded separately in the contribution log and GitHub evidence.

## 28. Team Communication Rules

During Sprint 3:

1. Announce when starting a WBS task.
2. Announce the branch name being used.
3. Push work regularly.
4. Communicate blockers as soon as they affect another task.
5. Communicate API or response-schema changes before dependent work continues.
6. Do not wait until a task deadline to report a blocker.
7. Use pull requests for integration.
8. Keep WBS ownership unchanged when another member provides support.
9. Record testing evidence for owned work.
10. Communicate before editing shared binary files such as Excel test trackers.
11. Pull the latest shared Sprint branch before starting dependent work.
12. Do not rewrite shared branch history.

## 29. Definition of Ready for Sprint 3 Implementation

A Sprint 3 implementation task is ready when:

- Its required predecessor is available or the team has documented an approved overlap.
- The task owner is confirmed.
- Expected input and output contracts are understood.
- Required design documents are available.
- Security and privacy requirements are understood.
- The task branch is based on the latest `feature/sprint-3`.
- Known blockers are recorded.
- Required test approach is understood.

For WBS 6.3, WBS 6.4, and WBS 6.6, the WBS 6.2 prompt and safety contracts should be agreed before dependent AI-generation logic is treated as ready.

## 30. Definition of Done for WBS 6.1

WBS 6.1 Sprint 3 Planning is complete when:

- Sprint 3 objective is confirmed.
- Official WBS ownership is confirmed.
- WBS dependencies are reviewed.
- Early-start overlap is recorded and accepted by the team.
- `feature/sprint-3` is established as the shared Sprint 3 integration branch.
- Branch strategy is agreed.
- Sprint 2 merge-forward process is agreed.
- Sprint 3 AI architecture boundary is agreed.
- WBS 6.2 safety direction is agreed.
- Integration contracts requiring early agreement are identified.
- Testing strategy is recorded.
- Current blockers are recorded.
- Team communication rules are agreed.
- Sprint 3 AI Feature Integration Flow diagram is reviewed.
- This planning document is reviewed by all members.
- Required planning changes are incorporated.
- The WBS 6.1 planning pull request is merged into `feature/sprint-3`.

## 31. Sprint 3 Exit Criteria

Sprint 3 is ready for WBS 6.11 completion when:

- WBS 6.3 is complete.
- WBS 6.4 is complete.
- WBS 6.5 is complete.
- WBS 6.6 is complete.
- WBS 6.7 is complete.
- WBS 6.8 integration is complete.
- WBS 6.9 testing is complete.
- No unresolved Critical or High defect blocks the Sprint 3 core flow.
- Required authentication and ownership checks pass.
- AI safety tests pass.
- Required privacy checks pass.
- Resume generation flow works through the approved Sprint 3 service boundary.
- Cover-letter generation flow works through the approved Sprint 3 service boundary.
- Interview-question and feedback flow works through the approved Sprint 3 service boundary.
- Generated content is editable.
- Required test evidence is recorded.
- Deferred scope is documented.
- WBS 6.10 review and retrospective is complete.
- The team agrees the Sprint 3 increment is ready for completion.

## 32. Current Planning Status

Sprint 3 planning preparation is in progress.

The shared Sprint 3 branch has been created from the current Sprint 2 baseline.

Sprint 2 stays formally open.

The team is using a controlled early-start overlap so available members proceed with Sprint 3 while remaining Sprint 2 work continues.

WBS 6.1 should stay in review until all members confirm the plan.

After WBS 6.1 approval, Jerald's next planned task is:

`WBS 6.2 AI Prompt Templates and Safety Rules`

Dependent Sprint 3 implementation should follow the contracts approved during WBS 6.1 and WBS 6.2.
