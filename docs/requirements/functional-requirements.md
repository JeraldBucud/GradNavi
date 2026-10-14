# Functional Requirements

Status: Original functional requirements baseline with Version 1 change-control reconciliation

These requirements describe the original proposed V1 behaviour of GradNavi. Subsequent scope decisions are recorded below. The FR-17 Version 1 exclusion has project-lead-reported verbal approval from the team, recorded 14 October 2026. All other baseline requirements retain their individually recorded statuses.

| ID | Requirement | Statement | Priority | Status |
|---|---|---|---|---|
| FR-01 | Account registration and authentication | The system shall let students create accounts, sign in, sign out, and recover access. | Must | Draft for approval |
| FR-02 | Student profile | The system shall let students create and update skills, interests, education, experience, projects, goals, and personality responses. | Must | Draft for approval |
| FR-03 | Career recommendations | The system shall generate ranked career recommendations from profile data. | Must | Draft for approval |
| FR-04 | Recommendation explanation | The system shall display a score and reasons for each recommendation. | Must | Draft for approval |
| FR-05 | Skill-gap analysis | The system shall compare student skills with selected career requirements. | Must | Draft for approval |
| FR-06 | Career-readiness score | The system shall calculate a readiness score from documented weighted criteria. | Must | Draft for approval |
| FR-07 | Job-description matching | The system shall analyse one pasted job description at a time and show matched and missing requirements. | Must | Draft for approval |
| FR-08 | Resume builder | The system shall generate an editable resume draft from profile data. | Must | Draft for approval |
| FR-09 | Cover-letter builder | The system shall generate an editable cover letter tailored to one selected job description. | Must | Draft for approval |
| FR-10 | Interview preparation | The system shall generate text-based interview questions and feedback on typed answers. | Must | Draft for approval |
| FR-11 | Learning suggestions | The system shall recommend learning resources for identified skill gaps. | Must | Draft for approval |
| FR-12 | Career roadmap | The system shall create ordered development steps for a selected career. | Must | Draft for approval |
| FR-13 | Progress dashboard | The system shall show saved careers, gaps, readiness, roadmap progress, and interview history. | Should | Draft for approval |
| FR-14 | Basic administration | The system shall let authorised administrators manage users, careers, skills, and learning resources. | Must | Draft for approval |
| FR-15 | Admin analytics | The system shall show basic aggregated statistics such as popular careers and common skill gaps. | Should | Draft for approval |
| FR-16 | AI content review | The system shall allow users to review and edit generated content before saving. | Must | Draft for approval |
| FR-17 | Data deletion | The system shall let students delete saved generated documents and request deletion of their profile. | Must | Excluded from V1; team verbal approval reported 14 October 2026 |
| FR-18 | Audit and error handling | The system shall record critical system actions and return clear errors when AI or external services fail. | Must | Draft for approval |

## Version 1 Scope Reconciliation

Decision recorded: 13 October 2026

### FR-17 Data Deletion

The project lead confirmed that FR-17 Data Deletion is excluded from the final GradNavi Version 1 scope.

The original requirement statement and Must priority are retained in the requirements table for historical traceability.

The exclusion does not establish that the deletion functionality was implemented, tested, or accepted.

### Change Control Record

| Field | Record |
| --- | --- |
| Requirement ID | FR-17 |
| Original priority | Must |
| Decision | Exclude FR-17 from Version 1 |
| Decision source | Project-lead confirmation, 13 October 2026 |
| Reason for change | Formal reason not recorded; the original project schedule had no dedicated FR-17 implementation task |
| Scope effect | Saved generated-document deletion and profile-deletion requests are outside Version 1 acceptance scope |
| Schedule effect | No FR-17 implementation task is scheduled for Version 1 |
| Risk effect | FR-17 deletion workflows are unavailable under the recorded Version 1 scope |
| Quality effect | No claim of FR-17 implementation or acceptance testing |
| Updated implementation owner | Not assigned |
| Team approval record | Project lead reports verbal approval by Jerald, Joyee and MD; confirmation recorded 14 October 2026, telephone discussion date not separately supplied |
| Written approval | No individually signed or written acknowledgements supplied; verbal approval recorded from project-lead confirmation |

FR-17 implementation in a later version requires a separate scope decision, assigned ownership, implementation tasks, and acceptance criteria.

Related records:

- `docs/project-management/product-backlog.md`
- `docs/requirements/requirements-assignment-matrix.md`
- `docs/project-management/sprint-5-closeout.md`

## Approval rule

A requirement becomes approved after all three members confirm its wording, priority, owner, acceptance criteria, and planned Sprint.

## Change control

Any proposed change must record:

1. Requirement ID
2. Reason for the change
3. Scope effect
4. Schedule effect
5. Risk effect
6. Quality effect
7. Updated owner
8. Team approval date

## Sprint 5 FR-17 Team Approval Reconciliation (recorded 14 October 2026)

The project lead confirmed that **Jerald Christopher Bucud, Joyee Chakraborty and Md Enamul Haque agreed verbally** to exclude FR-17 Data Deletion from GradNavi Version 1. The discussion occurred by telephone, according to the project lead; its exact date was not provided. This is a **project-lead-reported group decision**, not independently verified individual written approval.

The original **Must** priority and requirement wording are retained as historical context. FR-17 was not implemented, tested, or accepted as a delivered Version 1 feature. Future deletion support requires its own scope approval, implementation and tests.
