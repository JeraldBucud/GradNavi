# GradNavi Sprint 2 Closeout Review and Acceptance Record

**Document status:** Proposed formal closeout; **testing reconciled, team review and approval pending**  
**Prepared:** 13 October 2026  
**Sprint:** Sprint 2, Career Recommendations and Skill Gaps  
**Original planned sprint:** 24 August to 4 September 2026  
**WBS review scope:** 5.9 Sprint 2 Integration and Testing, 5.10 Sprint 2 Review and Retrospective, 5.11 Sprint 2 Complete  
**Project:** GradNavi, AI-Powered Career Guidance System  
**Review owner:** All Members  
**Source of planning authority:** Approved Microsoft Project schedule, reflected in the repository WBS

> This document proposes the final Sprint 2 review based on published repository records. It does **not** claim a team review meeting, approval, acceptance signature, or a completed WBS 5.11 milestone where no corresponding evidence has been located. Approval must be recorded by the team before changing the formal closeout status.

## 1. Purpose and historical context

Sprint 2 was intended to integrate career and skill reference data, deterministic career recommendations, readiness and skill-gap scoring, recommendation explanations, learning suggestions, and the Career Roadmap. The related planned requirements are **FR-03, FR-04, FR-05, FR-06, FR-11, and FR-12**.

Sprint 2 integration continued after the planned 4 September end date as frontend integration, backend API cases, defect resolution, and documentation were reconciled. The [20 September integration-plan checkpoint](../system-design/sprint-2-integration-plan.md) recorded **72 Pass, 0 Fail, 8 Blocked** out of 80 cases. Those eight blocked cases belonged to MD's WBS 5.7 Learning Suggestions and Roadmap API verification. This was a historical checkpoint, not the final outcome.

The [Sprint 2 test plan](../testing/sprint-2-test-plan.md) subsequently recorded **80 Pass, 0 Fail, 0 Blocked** as of the 23 September testing checkpoint and stated that final Sprint 2 closure still required the team closeout review. The original plan, historical status snapshots, and test-case identifiers should be preserved.

## 2. Scope and implementation reconciliation

| WBS | Deliverable | Approved task owner | Evidence-based review finding |
| --- | --- | --- | --- |
| 5.2 | Career and Skill Reference Data | MD | Reported implemented in final Sprint 2 test plan |
| 5.3 | Weighted Recommendation Engine | Jerald | Reported implemented; deterministic scoring and associated verification documented |
| 5.4 | Career Recommendation API | MD | Reported implemented and available for integration |
| 5.5 | Skill Gap and Readiness Scoring Logic | Jerald | Reported implemented and verified in integrated flow |
| 5.6 | Recommendation and Readiness Interface | Joyee | Final interface reported integrated; Jerald's recovery/implementation support recorded separately in [contribution log](contribution-log.md) and [PR #44](https://github.com/JeraldBucud/GradNavi/pull/44) |
| 5.7 | Learning Suggestions and Roadmap API | MD | Implemented and eight formerly blocked API cases recorded as Pass |
| 5.8 | Learning Roadmap Interface | Joyee | Reported integrated into the Student flow |
| 5.9 | Sprint 2 Integration and Testing | All Members | **Test-execution evidence reports 80/80 Pass**; formal team review of evidence and acceptance criteria pending |
| 5.10 | Sprint 2 Review and Retrospective | All Members | Preliminary review exists; final team review and actual acceptance record **pending** |
| 5.11 | Sprint 2 Complete | All Members | **Not formally confirmed**; depends on approved completion of WBS 5.9 and WBS 5.10 |

The table distinguishes documented development/testing progress from formal WBS acceptance. It does not retroactively reassign WBS 5.6 or change the approved Microsoft Project schedule.

## 3. Testing reconciliation (WBS 5.9)

### 3.1 Test execution checkpoints

| Checkpoint | Planned cases | Pass | Fail | Blocked | Not Run | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 20 September 2026 integration-plan snapshot | 80 | 72 | 0 | 8 | 0 | Historical record: MD's WBS 5.7 API cases pending |
| 23 September 2026 test-plan update | 80 | 80 | 0 | 0 | 0 | Later recorded testing result; test-execution portion reported complete |

**Source:** [Sprint 2 Test Plan, Sections 10, 28 and 29](../testing/sprint-2-test-plan.md); [Sprint 2 Integration Plan, Sections 20 and 21](../system-design/sprint-2-integration-plan.md). The detailed row-by-row source is the [Sprint 2 Test Case Tracker](../testing/sprint-2-test-cases.xlsx).

The published test plan describes the final tracker result. This review has **not** independently re-executed all 80 cases or audited every tracker row and evidence attachment. Team sign-off should confirm the tracker, case ownership, evidence references, and final results.

### 3.2 Previously blocked WBS 5.7 cases

The test plan records that **S2-LEARN-01 through S2-LEARN-08**, assigned to MD, passed. The recorded evidence identifiers are **S2-EV-038 through S2-EV-045**.

Coverage documented in the plan includes unresolved gaps, missing skills, below-requirement skills, exclusion of met requirements, selected-career context, insufficient-profile handling, invalid-request validation, and repeated-input stability.

The eight cases should not be represented as failed tests during the earlier blocked checkpoint.

### 3.3 Integration verification scope

The recorded Sprint 2 testing addressed:

- Career Recommendations and explanation presentation.
- Skill Gap and Career Readiness results.
- Learning Resources and Career Roadmap navigation.
- Empty-profile and insufficient-evidence behaviour.
- Student ownership isolation.
- Responsive desktop, tablet, and mobile layouts.
- Keyboard interaction and Chrome, Edge, and Firefox checks.
- The WBS 5.7 Learning Suggestions and Roadmap API test set.

These are **documented Sprint 2 test-plan outcomes**, not independent live production verification.

### 3.4 Recorded defect corrections

| Defect | Recorded observation | Recorded disposition | Follow-up |
| --- | --- | --- | --- |
| DEF-S2-003 | Responsive Student navigation and Career Recommendations layout | Fixed and retested successfully | Confirm test-case and screenshot links during team review |
| DEF-S2-004 | `NaN` in the Learning Resources empty state | Fixed and retested successfully | Confirm test-case and screenshot links during team review |
| DEF-S2-005 | Ranked Career Recommendations returned when Student Skills were empty | Fixed and retested successfully | Confirm test-case and screenshot links during team review |

**Source:** [Sprint 2 Test Plan, Section 28](../testing/sprint-2-test-plan.md) and [Sprint 2 Integration Plan, Section 20](../system-design/sprint-2-integration-plan.md).

The cited plans record resolution and successful retesting of these defects. This document does not claim a separate exhaustive search found zero defects across every later release.

## 4. Requirements and exit criteria review

Sprint 2's planned functional requirements were **FR-03, FR-04, FR-05, FR-06, FR-11 and FR-12**.

The integrated testing scope reported by the test plan supports technical review of these functions. The [Product Backlog](product-backlog.md) still contains historical statuses for the 20 September checkpoint. Requirement completion status must follow the approved acceptance process rather than a test count alone.

| Exit criterion from Sprint 2 Test Plan | Review position |
| --- | --- |
| Critical Career Analysis cases pass | 80/80 total test cases reported Pass; confirm critical-case mapping in tracker |
| No unresolved Critical/High blocker in core flow | Named DEF-S2-003 to DEF-S2-005 recorded as fixed and retested; final defect-register review required |
| Security and privacy regression | Test plan reports security and Student ownership checks passed |
| Repeatable recommendation/readiness behaviour | Test plan reports deterministic verification |
| React and Django Career Analysis integration | Reported tested |
| Learning suggestions and roadmap connected to skill gaps | Reported tested |
| Required test evidence retained | Test plan refers to tracker/evidence; final link review required |
| Deferred issues documented | No blocked Sprint 2 test cases reported; confirm any accepted limitations |
| Team agrees readiness for review | **Formal acknowledgement not recorded** |

The testing checkpoint supports conducting the closeout meeting. It does not replace the required team decision.

## 5. Proposed Sprint 2 review and retrospective (WBS 5.10)

The points below consolidate the **preliminary retrospective already present** in [Sprint 2 Integration Plan, Section 21](../system-design/sprint-2-integration-plan.md). They are proposed agenda content and **must not** be described as an already held final team meeting.

### 5.1 Recorded strengths

- Deterministic recommendation and readiness rules supported repeatable testing.
- The shared test tracker supported visibility of ownership, evidence, defects, and retesting.
- End-to-end verification exposed issues not visible during isolated component testing.
- Focused defect fixes and subsequent regression checks supported evidence-based resolution.
- Responsive, keyboard, browser, empty-state, and ownership checks covered the connected Student workflow.

### 5.2 Recorded challenges

- Sprint 2 integration and testing extended beyond the originally scheduled sprint.
- Frontend and API dependencies became available at different times.
- Some planning and testing documents retained outdated statuses after integration moved forward.
- Test ownership needed continued checks so cases were attributed to the assigned tester.
- Cross-component and empty-state defects emerged during final integration.

### 5.3 Proposed follow-up actions

1. Integrate frontend and backend work earlier in future sprint execution.
2. Keep original WBS ownership distinct from recovery work and actual implementation contributions.
3. Update trackers, test plans, evidence indexes, and backlogs after dependency merges.
4. Run empty-state, ownership, accessibility, responsive, browser, and error-state checks earlier.
5. Use focused corrective changes and confirm retests before marking defects resolved.
6. Preserve historical snapshots and record a dated current-state addendum rather than overwriting earlier checkpoints.

**Team decision on retrospective:** Pending. Record participants, date, accepted findings, assigned actions, and confirmation evidence after the actual review.

## 6. Formal WBS 5.9, 5.10 and 5.11 disposition

| Milestone | Proposed review disposition as of 13 October 2026 | Required decision |
| --- | --- | --- |
| WBS 5.9, Sprint 2 Integration and Testing | **Execution recorded complete: 80 Pass / 80 planned**; final evidence/sign-off review pending | Verify tracker and evidence, then explicitly accept WBS 5.9 |
| WBS 5.10, Sprint 2 Review and Retrospective | **Pending formal team review** | Conduct/record review and retrospective; approve actions |
| WBS 5.11, Sprint 2 Complete | **Pending**, not formally closed by this draft | Mark complete only after accepted predecessors and team confirmation |

**Formal Sprint 2 closeout: PENDING TEAM DECISION.** Do not change a milestone to Complete simply because later sprint work was merged or final technical tests report Pass.

### 6.1 Team review and acknowledgement

| Member | Reviewed tracker and evidence | Approved WBS 5.9 | Participated in / approved WBS 5.10 | Approved WBS 5.11 | Confirmation URL / date |
| --- | --- | --- | --- | --- | --- |
| Jerald Christopher Bucud | Pending | Pending | Pending | Pending | Not recorded |
| Md Enamul Haque | Pending | Pending | Pending | Pending | Not recorded |
| Joyee Chakraborty | Pending | Pending | Pending | Pending | Not recorded |

The table is a sign-off template, **not** a representation of actual votes.

## 7. Evidence references

1. [Sprint 2 Test Plan](../testing/sprint-2-test-plan.md), particularly Sections 10, 28 and 29.
2. [Sprint 2 Test Case Tracker](../testing/sprint-2-test-cases.xlsx), detailed test-case source.
3. [Sprint 2 Evidence Directory](../testing/evidence/sprint-2/), retained test evidence.
4. [Sprint 2 Integration Plan](../system-design/sprint-2-integration-plan.md), historical and preliminary retrospective snapshots.
5. [Product Backlog](product-backlog.md), planned requirements and reconciliation context.
6. [Work Breakdown Structure](work-breakdown-structure.md), approved sprint tasks and dependencies.
7. [Contribution Log](contribution-log.md), actual contributions distinct from original task ownership.
8. [PR #58, Sprint 2 integration closeout status update](https://github.com/JeraldBucud/GradNavi/pull/58), historical documentation reconciliation.

## 8. Final actions before approval

- [ ] Confirm 80/80 status and assignment/evidence links directly in the final Sprint 2 workbook.
- [ ] Reconcile the evidence index and the three named defect retests.
- [ ] Confirm absence or documented acceptance of any unresolved Sprint 2 Critical/High blocker.
- [ ] Confirm the requirement-to-WBS mapping and agreed dispositions of FR-03, FR-04, FR-05, FR-06, FR-11 and FR-12.
- [ ] Complete and record the actual team review/retrospective for WBS 5.10.
- [ ] Record individual or documented collective approval of WBS 5.9 and WBS 5.11, with a date.
- [ ] Only then change this document's formal status and the authoritative schedule/backlog milestone statuses through the agreed change-control process.
