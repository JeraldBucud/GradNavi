# GradNavi Work Breakdown Structure

Status: Approved implementation WBS aligned with the revised Microsoft Project schedule.

## Source of Truth

The GradNavi Microsoft Project schedule is the planning baseline for:

- WBS numbering.
- Task sequencing.
- Sprint dates.
- Task ownership.
- Predecessors and dependencies.
- Project milestones.

This document mirrors the approved Microsoft Project WBS so that GitHub project documentation remains aligned with the project schedule.

If task dates, dependencies, ownership, or scope change, the Microsoft Project schedule should be updated first and this document should then be updated to match.

## 1. Project Management

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 1 | Project Management | 13 Jul | 09 Oct | 65 | Jerald | |
| 1.1 | Team formation and role confirmation | 13 Jul | 14 Jul | 2 | All Members | |
| 1.2 | Project charter and objectives | 15 Jul | 16 Jul | 2 | Jerald | 1.1 |
| 1.3 | Communication and meeting plan | 15 Jul | 15 Jul | 1 | Jerald | 1.1 |
| 1.4 | GitHub repository and branching setup | 16 Jul | 17 Jul | 2 | Jerald | 1.1 |
| 1.5 | Tool and environment confirmation | 16 Jul | 17 Jul | 2 | All Members | 1.1 |
| 1.6 | Risk register creation | 20 Jul | 21 Jul | 2 | Jerald | 1.2 |
| 1.7 | Quality management plan | 22 Jul | 23 Jul | 2 | Jerald | 1.2 |
| 1.8 | Resource plan | 24 Jul | 24 Jul | 1 | Jerald | 1.2 |
| 1.9 | Weekly progress monitoring | 20 Jul | 09 Oct | 60 | Jerald | |
| 1.10 | Weekly team meetings | 20 Jul | 09 Oct | 60 | All Members | |
| 1.11 | Stakeholder communication | 27 Jul | 02 Oct | 50 | Jerald | |

## 2. Requirements and Analysis

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 2 | Requirements and Analysis | 20 Jul | 07 Aug | 15 | MD | |
| 2.1 | Project background and business need | 20 Jul | 22 Jul | 3 | Joyee | |
| 2.2 | Problem statement and objectives | 20 Jul | 22 Jul | 3 | Joyee | |
| 2.3 | Scope, assumptions and constraints | 23 Jul | 27 Jul | 3 | Joyee | 2.1, 2.2 |
| 2.4 | Stakeholder analysis | 23 Jul | 24 Jul | 2 | Joyee | |
| 2.5 | Functional requirements | 27 Jul | 30 Jul | 4 | MD | 2.3 |
| 2.6 | Non-functional requirements | 27 Jul | 29 Jul | 3 | MD | 2.3 |
| 2.7 | Security, privacy and ethical requirements | 30 Jul | 03 Aug | 3 | MD | 2.6 |
| 2.8 | User stories and acceptance criteria | 30 Jul | 04 Aug | 4 | MD | 2.5 |
| 2.9 | Initial product backlog | 03 Aug | 05 Aug | 3 | MD | 2.8 |
| 2.10 | Requirements validation workshop | 06 Aug | 06 Aug | 1 | All Members | 2.5, 2.6, 2.7, 2.8, 2.9 |
| 2.11 | Requirements baseline approved | 07 Aug | 07 Aug | 0 | All Members | 2.10 |

## 3. System Design

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 3 | System Design | 27 Jul | 07 Aug | 10 | All Members | |
| 3.1 | Solution architecture | 27 Jul | 29 Jul | 3 | Jerald | 2.3 |
| 3.2 | Use case diagram | 27 Jul | 28 Jul | 2 | MD | 2.5 |
| 3.3 | Context diagram | 29 Jul | 30 Jul | 2 | MD | 3.2 |
| 3.4 | Database ER diagram | 30 Jul | 03 Aug | 3 | MD | 3.1, 2.5 |
| 3.5 | Database schema and data dictionary | 03 Aug | 05 Aug | 3 | MD | 3.4 |
| 3.6 | REST API design | 03 Aug | 05 Aug | 3 | Jerald | 3.1, 2.5 |
| 3.7 | Low-fidelity wireframes | 27 Jul | 30 Jul | 4 | Joyee | 2.3 |
| 3.8 | High-fidelity UI design | 03 Aug | 06 Aug | 4 | Joyee | 3.7 |
| 3.9 | Security architecture | 05 Aug | 06 Aug | 2 | Jerald | 3.1, 2.7 |
| 3.10 | Design review and baseline | 07 Aug | 07 Aug | 0 | All Members | 3.5, 3.6, 3.8, 3.9 |

## 4. Sprint 1 - Foundation and Student Profile

Sprint dates: 10 August to 21 August 2026.

Primary outcome: Authentication, Student Profile, and frontend foundation.

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 4 | Sprint 1 - Foundation and Student Profile | 10 Aug | 21 Aug | 10 | All Members | |
| 4.1 | Sprint 1 planning | 10 Aug | 10 Aug | 1 | All Members | 2.11, 3.10 |
| 4.2 | Django and PostgreSQL project setup | 10 Aug | 12 Aug | 3 | MD | 4.1 |
| 4.3 | React frontend setup and routing | 10 Aug | 12 Aug | 3 | Joyee | 4.1 |
| 4.4 | Authentication backend and JWT | 13 Aug | 18 Aug | 4 | Jerald | 4.2 |
| 4.5 | Login and registration interface | 13 Aug | 18 Aug | 4 | Joyee | 4.3 |
| 4.6 | Student Profile models and API | 17 Aug | 20 Aug | 4 | MD | 4.2, 3.5 |
| 4.7 | Student Profile interface | 17 Aug | 20 Aug | 4 | Joyee | 4.3, 3.8 |
| 4.8 | Authentication and profile integration | 20 Aug | 21 Aug | 2 | Jerald | 4.4, 4.5, 4.6, 4.7 |
| 4.9 | Sprint 1 unit and API testing | 20 Aug | 21 Aug | 2 | All Members | 4.8 |
| 4.10 | Sprint 1 review and retrospective | 21 Aug | 21 Aug | 1 | All Members | 4.9 |
| 4.11 | Sprint 1 complete | 21 Aug | 21 Aug | 0 | All Members | 4.10 |

## 5. Sprint 2 - Career Recommendations and Skill Gaps

Sprint dates: 24 August to 4 September 2026.

Primary outcome: Career recommendations, readiness scoring, skill-gap analysis, and learning roadmap.

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 5 | Sprint 2 - Career Recommendations and Skill Gaps | 24 Aug | 04 Sep | 10 | All Members | |
| 5.1 | Sprint 2 planning | 24 Aug | 24 Aug | 1 | All Members | 4.11 |
| 5.2 | Career and skill reference data | 24 Aug | 26 Aug | 3 | MD | 5.1 |
| 5.3 | Weighted recommendation engine | 25 Aug | 31 Aug | 5 | Jerald | 5.1, 5.2 |
| 5.4 | Career recommendation API | 28 Aug | 02 Sep | 4 | MD | 5.3 |
| 5.5 | Skill gap and readiness scoring logic | 31 Aug | 03 Sep | 4 | Jerald | 5.3 |
| 5.6 | Recommendation and readiness interface | 27 Aug | 02 Sep | 5 | Joyee | 5.1, 3.8 |
| 5.7 | Learning suggestions and roadmap API | 01 Sep | 03 Sep | 3 | MD | 5.5 |
| 5.8 | Learning roadmap interface | 01 Sep | 03 Sep | 3 | Joyee | 5.6 |
| 5.9 | Sprint 2 integration and testing | 03 Sep | 04 Sep | 2 | All Members | 5.4, 5.5, 5.7, 5.8 |
| 5.10 | Sprint 2 review and retrospective | 04 Sep | 04 Sep | 1 | All Members | 5.9 |
| 5.11 | Sprint 2 complete | 04 Sep | 04 Sep | 0 | All Members | 5.10 |

## 6. Sprint 3 - Application Documents and Interview Preparation

Sprint dates: 7 September to 18 September 2026.

Primary outcome: AI-assisted resume, cover-letter, and interview-preparation functions.

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 6 | Sprint 3 - Application Documents and Interview Preparation | 07 Sep | 18 Sep | 10 | All Members | |
| 6.1 | Sprint 3 planning | 07 Sep | 07 Sep | 1 | All Members | 5.11 |
| 6.2 | AI prompt templates and safety rules | 07 Sep | 09 Sep | 3 | Jerald | 6.1, 2.7 |
| 6.3 | Resume generation backend | 09 Sep | 14 Sep | 4 | MD | 6.2 |
| 6.4 | Cover letter generation backend | 09 Sep | 14 Sep | 4 | MD | 6.2 |
| 6.5 | Resume and cover letter interface | 09 Sep | 15 Sep | 5 | Joyee | 6.1, 3.8 |
| 6.6 | Interview question and feedback API | 14 Sep | 17 Sep | 4 | Jerald | 6.2 |
| 6.7 | Interview preparation interface | 14 Sep | 17 Sep | 4 | Joyee | 6.5 |
| 6.8 | Document and interview integration | 17 Sep | 18 Sep | 2 | All Members | 6.3, 6.4, 6.5, 6.6, 6.7 |
| 6.9 | Sprint 3 testing | 17 Sep | 18 Sep | 2 | All Members | 6.8 |
| 6.10 | Sprint 3 review and retrospective | 18 Sep | 18 Sep | 1 | All Members | 6.9 |
| 6.11 | Sprint 3 complete | 18 Sep | 18 Sep | 0 | All Members | 6.10 |

## 7. Sprint 4 - Job Matching, Admin and AI Integration

Sprint dates: 21 September to 2 October 2026.

Primary outcome: Job-description matching, administration, permissions, and controlled AI integration.

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 7 | Sprint 4 - Job Matching, Admin and AI Integration | 21 Sep | 02 Oct | 10 | All Members | |
| 7.1 | Sprint 4 planning | 21 Sep | 21 Sep | 1 | All Members | 6.11 |
| 7.2 | Job description extraction and matching | 21 Sep | 25 Sep | 5 | Jerald | 7.1, 5.5 |
| 7.3 | OpenAI service integration | 21 Sep | 24 Sep | 4 | MD | 7.1, 6.2 |
| 7.4 | AI response validation and error handling | 24 Sep | 28 Sep | 3 | Jerald | 7.3 |
| 7.5 | Job matching interface | 24 Sep | 29 Sep | 4 | Joyee | 7.2 |
| 7.6 | Admin models and API | 22 Sep | 28 Sep | 5 | MD | 7.1 |
| 7.7 | Admin dashboard interface | 23 Sep | 29 Sep | 5 | Joyee | 7.1 |
| 7.8 | Role permissions and audit records | 28 Sep | 30 Sep | 3 | Jerald | 7.6, 4.4 |
| 7.9 | Sprint 4 integration and testing | 01 Oct | 02 Oct | 2 | All Members | 7.4, 7.5, 7.6, 7.7, 7.8 |
| 7.10 | Sprint 4 review and retrospective | 02 Oct | 02 Oct | 1 | All Members | 7.9 |
| 7.11 | Feature complete | 02 Oct | 02 Oct | 0 | All Members | 7.10 |

## 8. Sprint 5 - Stabilisation, Deployment and Closure

Sprint dates: 5 October to 9 October 2026.

Primary outcome: Regression testing, deployment, documentation, project closure, and presentation preparation.

| WBS | Task | Start | Finish | Days | Owner | Predecessors |
| --- | --- | --- | --- | ---: | --- | --- |
| 8 | Sprint 5 - Stabilisation, Deployment and Closure | 05 Oct | 09 Oct | 5 | All Members | |
| 8.1 | Sprint 5 planning and defect triage | 05 Oct | 05 Oct | 1 | All Members | 7.11 |
| 8.2 | Full regression testing | 05 Oct | 06 Oct | 2 | All Members | 8.1 |
| 8.3 | Security and permission testing | 05 Oct | 06 Oct | 2 | Jerald | 8.1 |
| 8.4 | Performance and usability review | 06 Oct | 07 Oct | 2 | Joyee | 8.1 |
| 8.5 | Bug fixing and final refinement | 07 Oct | 08 Oct | 2 | All Members | 8.2, 8.3, 8.4 |
| 8.6 | User acceptance testing | 07 Oct | 08 Oct | 2 | All Members | 8.2 |
| 8.7 | Backend and database deployment | 07 Oct | 08 Oct | 2 | MD | 8.2 |
| 8.8 | Frontend deployment | 07 Oct | 08 Oct | 2 | Joyee | 8.2 |
| 8.9 | Production verification | 09 Oct | 09 Oct | 1 | Jerald | 8.5, 8.6, 8.7, 8.8 |
| 8.10 | Technical documentation finalisation | 05 Oct | 08 Oct | 4 | MD | 7.11 |
| 8.11 | User guide finalisation | 05 Oct | 08 Oct | 4 | Joyee | 7.11 |
| 8.12 | Final report and GitHub review | 05 Oct | 09 Oct | 5 | Jerald | 7.11 |
| 8.13 | Project delivery complete | 09 Oct | 09 Oct | 0 | All Members | 8.9, 8.10, 8.11, 8.12 |
| 8.14 | Final presentation preparation | 09 Oct | 09 Oct | 1 | All Members | 8.13 |
| 8.15 | Final presentation | 12 Oct | 12 Oct | 0 | All Members | 8.14 |

## WBS Dictionary

| WBS | Deliverable | Acceptance Evidence | Owner |
| --- | --- | --- | --- |
| 1 | Project Management | Plans, meeting records, risk register, quality records and project monitoring evidence | Jerald |
| 2 | Requirements and Analysis | Approved requirements baseline, user stories and product backlog | MD |
| 3 | System Design | Architecture, ERD, API specification, security design and approved UI designs | All Members |
| 4 | Sprint 1 - Foundation and Student Profile | Authentication, Student Profile foundation, integrated flow and Sprint test evidence | All Members |
| 5 | Sprint 2 - Career Recommendations and Skill Gaps | Career recommendation results, repeatable scoring tests, readiness and learning roadmap output | All Members |
| 6 | Sprint 3 - Application Documents and Interview Preparation | Editable generated documents and interview preparation evidence | All Members |
| 7 | Sprint 4 - Job Matching, Admin and AI Integration | Integrated job matching, administration, AI controls and permission evidence | All Members |
| 8 | Sprint 5 - Stabilisation, Deployment and Closure | Regression evidence, deployed system, UAT, documentation and presentation | All Members |

## Alignment Rule

The Microsoft Project schedule is the authoritative project-planning baseline.

GitHub WBS documentation, task-lead documentation, Trello cards, Sprint planning records, and contribution records should remain aligned with the Microsoft Project schedule.

Changes to task ownership, predecessors, timing, or scope should be agreed by the team and reflected across all affected project-management records.