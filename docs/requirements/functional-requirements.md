# Functional Requirements

Status: Draft for team review

These requirements describe the planned V1 behaviour of GradNavi.

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
| FR-17 | Data deletion | The system shall let students delete saved generated documents and request deletion of their profile. | Must | Draft for approval |
| FR-18 | Audit and error handling | The system shall record critical system actions and return clear errors when AI or external services fail. | Must | Draft for approval |

## Approval rule

A requirement becomes approved after all three members confirm its wording, priority, owner, acceptance criteria, and planned Sprint.

## WBS 8.12 Implementation Reconciliation

The `Draft for approval` values above are formal requirement-approval labels from the original requirements record.

WBS 8.12 does not replace those labels with implementation status.

Implementation and testing state is tracked separately in the Product Backlog, Sprint closeout records, test plans, and the WBS 8.12 final GitHub review.

Current reconciliation findings:

- FR-01 and FR-02 have completed Sprint 1 implementation and testing evidence.
- FR-03 through FR-06, FR-11, and FR-12 have completed the 80 of 80 passing Sprint 2 test baseline.
- FR-08 through FR-10 have completed the 100 of 100 passing Sprint 3 closeout baseline.
- FR-07, FR-14, and FR-18 are covered by the 129 of 129 passing Sprint 4 Feature Complete baseline.
- FR-13 has merged implementation evidence through PR #75, but its formal Microsoft Project WBS mapping remains unresolved.
- FR-15 has implementation evidence in the Sprint 4 administration work, but its mapping remains provisional.
- FR-16 reviewable and editable generated-content behaviour exists across the document interfaces and AI service contracts, but its formal WBS mapping remains unresolved.
- FR-17 must stay open because WBS 8.12 did not identify verified Student-facing evidence satisfying the full deletion requirement.

Formal requirement approval should only change after the team records the required approval decision.

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
