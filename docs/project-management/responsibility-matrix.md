# GradNavi Responsibility Matrix

Status: Responsibility baseline aligned with the revised Microsoft Project schedule.

R means Responsible.
A means Accountable.
C means Consulted.
I means Informed.

## Source of Truth

The GradNavi Microsoft Project schedule is the authoritative source for implementation ownership.

This matrix provides a high-level RACI view of the detailed WBS assignments.

Detailed task ownership is maintained in:

    docs/project-management/task-leads.md

Detailed scheduling and dependencies are maintained in:

    docs/project-management/work-breakdown-structure.md

## Project Planning and Design

| Deliverable or Activity | Jerald | Joyee | MD |
| --- | --- | --- | --- |
| Project management and coordination | A/R | C | C |
| Requirements and backlog | C | C | A/R |
| Roadmap and Microsoft Project schedule | A/R | C | C |
| Risk management | A/R | C | C |
| Quality management | A/R | R | R |
| Solution architecture | A/R | C | C |
| Use case and context design | C | C | A/R |
| ERD and database schema design | C | I | A/R |
| REST API design | A/R | C | C |
| UI design | C | A/R | C |
| Security architecture | A/R | C | C |

## Sprint 1 Responsibilities

| Deliverable or Activity | Jerald | Joyee | MD |
| --- | --- | --- | --- |
| Django and PostgreSQL foundation | C | I | A/R |
| React frontend foundation | C | A/R | I |
| Authentication backend and JWT | A/R | C | C |
| Login and registration interface | C | A/R | C |
| Student Profile models and API | C | C | A/R |
| Student Profile interface | C | A/R | C |
| Authentication and Profile integration | A/R | R | R |
| Sprint 1 testing | R | R | R |

## Sprint 2 Responsibilities

| Deliverable or Activity | Jerald | Joyee | MD |
| --- | --- | --- | --- |
| Career and skill reference data | C | I | A/R |
| Weighted recommendation engine | A/R | I | C |
| Career recommendation API | C | I | A/R |
| Skill-gap and readiness scoring logic | A/R | C | C |
| Recommendation and readiness interface | C | A/R | C |
| Learning suggestions and roadmap API | C | C | A/R |
| Learning roadmap interface | C | A/R | C |
| Sprint 2 integration and testing | R | R | R |

## Sprint 3 Responsibilities

| Deliverable or Activity | Jerald | Joyee | MD |
| --- | --- | --- | --- |
| AI prompt templates and safety rules | A/R | C | C |
| Resume generation backend | C | C | A/R |
| Cover-letter generation backend | C | C | A/R |
| Resume and cover-letter interface | C | A/R | C |
| Interview question and feedback API | A/R | C | C |
| Interview preparation interface | C | A/R | C |
| Document and interview integration | R | R | R |
| Sprint 3 testing | R | R | R |

## Sprint 4 Responsibilities

| Deliverable or Activity | Jerald | Joyee | MD |
| --- | --- | --- | --- |
| Job-description extraction and matching | A/R | C | C |
| OpenAI service integration | C | I | A/R |
| AI response validation and error handling | A/R | C | C |
| Job matching interface | C | A/R | C |
| Admin models and API | C | C | A/R |
| Admin dashboard interface | C | A/R | C |
| Role permissions and audit records | A/R | C | C |
| Sprint 4 integration and testing | R | R | R |

## Sprint 5 Responsibilities

| Deliverable or Activity | Jerald | Joyee | MD |
| --- | --- | --- | --- |
| Full regression testing | R | R | R |
| Security and permission testing | A/R | C | C |
| Performance and usability review | C | A/R | C |
| Bug fixing and final refinement | R | R | R |
| User acceptance testing | R | R | R |
| Backend and database deployment | C | I | A/R |
| Frontend deployment | C | A/R | I |
| Production verification | A/R | R | R |
| Technical documentation finalisation | C | C | A/R |
| User guide finalisation | C | A/R | C |
| Final report and GitHub review | A/R | R | R |
| Final presentation preparation | R | R | R |
| Final presentation | R | R | R |

## Shared Sprint Activities

Microsoft Project assigns several activities to All Members.

These include:

- Sprint planning.
- Sprint integration.
- Sprint testing.
- Sprint review.
- Sprint retrospective.
- Bug fixing where shared.
- User acceptance testing.
- Final presentation preparation.
- Final presentation.

For these activities, all members are responsible for completing the agreed work.

The team leader or nominated Sprint coordinator coordinates shared activity where a single coordinator is required.

## Accountability Rule

A task with a named owner in Microsoft Project uses that member as the accountable lead.

Other members may be Responsible, Consulted, or Informed depending on integration needs.

A task assigned to All Members remains a shared team responsibility.

## Ownership Change Rule

Any approved ownership change must first be recorded in Microsoft Project.

The team must then update:

1. `work-breakdown-structure.md`
2. `task-leads.md`
3. `responsibility-matrix.md`
4. `product-backlog.md`
5. `roadmap-and-milestones.md`
6. Trello
7. Relevant GitHub records
8. Meeting minutes
9. Contribution records

The Microsoft Project schedule remains the authoritative planning record.