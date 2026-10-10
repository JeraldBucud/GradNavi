# GradNavi Roadmap and Milestones

Status: Approved delivery roadmap aligned with the revised Microsoft Project schedule.

## Source of Truth

The GradNavi Microsoft Project schedule is the authoritative planning baseline for:

- Sprint dates.
- Task sequencing.
- Dependencies.
- Task ownership.
- Project milestones.
- Delivery timing.

This roadmap provides a high-level view of the Microsoft Project schedule.

Detailed WBS tasks are maintained in:

    docs/project-management/work-breakdown-structure.md

Task ownership is maintained in:

    docs/project-management/task-leads.md

Requirement-to-Sprint mapping is maintained in:

    docs/project-management/product-backlog.md

## Delivery Approach

GradNavi uses Scrum with five implementation Sprints.

Sprint 1 establishes the secure application foundation and Student Profile flow.

Sprint 2 implements career recommendations, skill-gap analysis, readiness scoring, and learning roadmap functions.

Sprint 3 implements AI-assisted resume, cover-letter, and interview-preparation functions.

Sprint 4 implements job-description matching, administration, permissions, audit behaviour, and controlled AI integration.

Sprint 5 focuses on stabilisation, regression testing, deployment, documentation, production verification, and project closure.

Each Sprint includes:

- Sprint planning.
- Implementation.
- Integration.
- Testing.
- Sprint review.
- Sprint retrospective.
- Completion milestone.

## Project Schedule

| Phase | Dates | Main Work | Exit Milestone |
| --- | --- | --- | --- |
| Project planning, requirements and design | 13 July to 7 August 2026 | Team setup, scope, requirements, backlog, architecture, ERD, API design, UI design, security design, risk planning and quality planning | Requirements and design baseline approved |
| Sprint 1: Foundation and Student Profile | 10 August to 21 August 2026 | Django and PostgreSQL foundation, React foundation, authentication, JWT, login and registration interface, Student Profile backend and interface, integration and testing | Sprint 1 complete |
| Sprint 2: Career Recommendations and Skill Gaps | 24 August to 4 September 2026 | Career and skill reference data, weighted recommendation engine, recommendation API, skill-gap analysis, readiness scoring, recommendation interface, learning suggestions and roadmap | Sprint 2 complete |
| Sprint 3: Application Documents and Interview Preparation | 7 September to 18 September 2026 | AI prompt and safety rules, resume generation, cover-letter generation, document interface, interview question and feedback API, interview interface and integration | Sprint 3 complete |
| Sprint 4: Job Matching, Admin and AI Integration | 21 September to 2 October 2026 | Job-description extraction and matching, OpenAI service integration, AI response validation, job matching interface, administration, role permissions and audit records | Feature complete |
| Sprint 5: Stabilisation, Deployment and Closure | 5 October to 9 October 2026 | Full regression testing, security and permission testing, usability review, bug fixing, UAT, deployment, production verification, documentation and final report review | Project delivery complete |
| Final presentation preparation | 9 October 2026 | Final presentation preparation and demonstration readiness | Presentation ready |
| Final presentation | 12 October 2026 | Group presentation and demonstration | Final presentation completed |

## Sprint 1 Milestones

Sprint 1 dates:

    10 August to 21 August 2026

Primary outcome:

    Secure foundation and authenticated Student Profile flow.

Key work:

- WBS 4.1 Sprint 1 planning.
- WBS 4.2 Django and PostgreSQL project setup.
- WBS 4.3 React frontend setup and routing.
- WBS 4.4 Authentication backend and JWT.
- WBS 4.5 Login and registration interface.
- WBS 4.6 Student Profile models and API.
- WBS 4.7 Student Profile interface.
- WBS 4.8 Authentication and profile integration.
- WBS 4.9 Sprint 1 unit and API testing.
- WBS 4.10 Sprint 1 review and retrospective.

Exit milestone:

    WBS 4.11 Sprint 1 complete.

## Sprint 2 Milestones

Sprint 2 dates:

    24 August to 4 September 2026

Primary outcome:

    Career recommendations, skill-gap analysis, readiness scoring and learning roadmap.

Key work:

- WBS 5.1 Sprint 2 planning.
- WBS 5.2 Career and skill reference data.
- WBS 5.3 Weighted recommendation engine.
- WBS 5.4 Career recommendation API.
- WBS 5.5 Skill gap and readiness scoring logic.
- WBS 5.6 Recommendation and readiness interface.
- WBS 5.7 Learning suggestions and roadmap API.
- WBS 5.8 Learning roadmap interface.
- WBS 5.9 Sprint 2 integration and testing.
- WBS 5.10 Sprint 2 review and retrospective.

Exit milestone:

    WBS 5.11 Sprint 2 complete.

### Sprint 2 Execution Status Reconciled by WBS 8.12

The planned Sprint 2 dates remain the official Microsoft Project baseline.

Implementation and test execution continued beyond the planned finish date because frontend and integration dependencies closed later.

Current verified execution state:

- WBS 5.1 Sprint 2 Planning: completed.
- WBS 5.2 Career and Skill Reference Data: implemented.
- WBS 5.3 Weighted Recommendation Engine: implemented.
- WBS 5.4 Career Recommendation API: implemented.
- WBS 5.5 Skill Gap and Readiness Scoring Logic: implemented.
- WBS 5.6 Recommendation and Readiness Interface: implemented and integrated.
- WBS 5.7 Learning Suggestions and Roadmap API: implemented and tested.
- WBS 5.8 Learning Roadmap Interface: implemented and integrated.
- WBS 5.9 Sprint 2 Integration and Testing: 80 of 80 planned cases Pass.
- No Sprint 2 case is recorded as Fail, Blocked, or Not Run.

The official Microsoft Project ownership and original Sprint allocation remain unchanged.

A dedicated `sprint-2-closeout.md` record was not identified during the WBS 8.12 audit.

The repository therefore distinguishes:

- Sprint 2 implementation and test execution: complete.
- Formal dedicated Sprint 2 closeout document: not identified and requires documentation reconciliation.

## Sprint 3 Milestones

Sprint 3 dates:

    7 September to 18 September 2026

Primary outcome:

    AI-assisted application documents and interview preparation.

Key work:

- WBS 6.1 Sprint 3 planning.
- WBS 6.2 AI prompt templates and safety rules.
- WBS 6.3 Resume generation backend.
- WBS 6.4 Cover letter generation backend.
- WBS 6.5 Resume and cover letter interface.
- WBS 6.6 Interview question and feedback API.
- WBS 6.7 Interview preparation interface.
- WBS 6.8 Document and interview integration.
- WBS 6.9 Sprint 3 testing.
- WBS 6.10 Sprint 3 review and retrospective.

Exit milestone:

    WBS 6.11 Sprint 3 complete.

## Sprint 4 Milestones

Sprint 4 dates:

    21 September to 2 October 2026

Primary outcome:

    Job matching, administration, permissions, audit behaviour and controlled AI integration.

Key work:

- WBS 7.1 Sprint 4 planning.
- WBS 7.2 Job description extraction and matching.
- WBS 7.3 OpenAI service integration.
- WBS 7.4 AI response validation and error handling.
- WBS 7.5 Job matching interface.
- WBS 7.6 Admin models and API.
- WBS 7.7 Admin dashboard interface.
- WBS 7.8 Role permissions and audit records.
- WBS 7.9 Sprint 4 integration and testing.
- WBS 7.10 Sprint 4 review and retrospective.

Exit milestone:

    WBS 7.11 Feature complete.

## Sprint 5 Milestones

Sprint 5 dates:

    5 October to 9 October 2026

Primary outcome:

    Stable integrated system, deployment, evidence and project closure.

Key work:

- WBS 8.1 Sprint 5 planning and defect triage.
- WBS 8.2 Full regression testing.
- WBS 8.3 Security and permission testing.
- WBS 8.4 Performance and usability review.
- WBS 8.5 Bug fixing and final refinement.
- WBS 8.6 User acceptance testing.
- WBS 8.7 Backend and database deployment.
- WBS 8.8 Frontend deployment.
- WBS 8.9 Production verification.
- WBS 8.10 Technical documentation finalisation.
- WBS 8.11 User guide finalisation.
- WBS 8.12 Final report and GitHub review.

Exit milestone:

    WBS 8.13 Project delivery complete.

Final preparation:

    WBS 8.14 Final presentation preparation.

Final milestone:

    WBS 8.15 Final presentation.

## Major Dependencies

| Dependency | Required Before |
| --- | --- |
| Requirements baseline | Sprint implementation commitments |
| Design baseline | Sprint 1 implementation |
| Django and PostgreSQL foundation | Authentication and Student Profile backend |
| React foundation | Authentication and Student Profile interfaces |
| Authentication backend and frontend | Authentication integration |
| Student Profile backend and frontend | Complete Student Profile integration |
| Career and skill reference data | Weighted recommendation engine |
| Weighted recommendation engine | Career recommendation API and readiness logic |
| Skill-gap and readiness scoring | Learning suggestions and roadmap |
| AI prompt templates and safety rules | Resume, cover-letter and interview AI functions |
| Job-description matching logic | Job matching interface |
| OpenAI service integration | AI response validation |
| Admin models and API | Role permissions and audit records |
| Feature-complete build | Full regression and deployment |
| Regression, UAT and deployment | Production verification |
| Production verification and documentation | Project delivery completion |

## Current Sprint

The active project phase is Sprint 5 finalisation and project closure.

Sprint 5 scheduled dates:

    5 October to 9 October 2026

Final presentation:

    12 October 2026

Current finalisation sequence:

1. Complete WBS 8.2 Full Regression Testing.
2. Complete WBS 8.4 Performance and Usability Review.
3. Complete WBS 8.6 User Acceptance Testing.
4. Complete WBS 8.7 Backend and Database Deployment.
5. Complete WBS 8.8 Frontend Deployment.
6. Execute WBS 8.9 Production Verification.
7. Complete WBS 8.10 Technical Documentation Finalisation.
8. Complete WBS 8.11 User Guide Finalisation.
9. Complete WBS 8.12 Final Report and GitHub Review.
10. Complete WBS 8.13 Project Delivery.
11. Complete WBS 8.14 Final Presentation Preparation.
12. Deliver WBS 8.15 Final Presentation.

Verified earlier Sprint baselines:

- Sprint 1: Complete, 61 of 61 tests Pass.
- Sprint 2: 80 of 80 planned tests Pass; formal closeout documentation requires reconciliation.
- Sprint 3: Complete, 100 of 100 tests Pass.
- Sprint 4: Complete, 129 of 129 tests Pass and WBS 7.11 Feature Complete reached.

Sprint 5 introduces no unapproved core feature expansion. Remaining work focuses on final verification, deployment, documentation, delivery evidence, and presentation readiness.

## Schedule Review

The team reviews:

- Current Sprint progress.
- Task dependencies.
- Blockers.
- Workload.
- Ownership.
- Scope changes.
- Testing status.
- Milestone risk.

Schedule changes should be recorded in Microsoft Project first.

After approval, matching changes should be applied to:

1. `work-breakdown-structure.md`.
2. `task-leads.md`.
3. `product-backlog.md`.
4. `roadmap-and-milestones.md`.
5. Trello.
6. Relevant GitHub records.
7. Meeting minutes where required.

## Alignment Rule

The Microsoft Project schedule remains the authoritative planning baseline.

The GitHub roadmap provides a readable project summary and must stay aligned with the Microsoft Project schedule.
