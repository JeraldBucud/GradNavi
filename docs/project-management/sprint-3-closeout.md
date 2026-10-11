# GradNavi Sprint 3 Closeout

Status: Complete

Sprint: Sprint 3 - Application Documents and Interview Preparation

Planned Sprint dates: 7 September to 18 September 2026

Formal closeout record date: 9 October 2026

WBS ownership: All Members

## 1. Purpose

This record formally closes Sprint 3 after reconciliation of implementation, integration, testing, and evidence.

Sprint 3 established the GradNavi AI-assisted application-document and interview-preparation foundation.

The Sprint 3 increment includes the provider-independent prompt and safety layer, Resume generation, Cover Letter generation, document interfaces, Interview Question and Feedback APIs, Interview Preparation interface, and the integrated Student application-preparation flow.

Formal closeout happened after the planned Sprint dates because final frontend integration and successor verification continued into Sprint 4.

## 2. WBS Alignment

Sprint 3 closeout covers:

- WBS 6.8 Document and Interview Integration.
- WBS 6.9 Sprint 3 Testing.
- WBS 6.10 Sprint 3 Review and Retrospective.
- WBS 6.11 Sprint 3 Complete.

WBS 6.10 depends on WBS 6.9.

WBS 6.11 depends on WBS 6.10.

## 3. Sprint 3 Outcome

The Sprint 3 target was an authenticated AI-assisted application-document and interview-preparation flow.

The completed increment includes:

- Provider-independent AI service boundary.
- AI prompt templates.
- AI privacy allowlists.
- AI safety rules.
- Resume Generation Backend.
- Cover Letter Generation Backend.
- Resume Builder interface.
- Cover Letter Builder interface.
- Editable AI-supported document drafts.
- Interview Question generation API.
- Interview Feedback API.
- Interview Preparation interface.
- Typed-answer interview practice.
- Structured AI feedback.
- Review-required AI output states.
- Controlled validation errors.
- Controlled provider-error behaviour.
- Authentication protection.
- Student ownership and privacy controls.
- Responsive Student application workflows.
- Regression protection for earlier Sprint functionality.

## 4. Sprint 3 Testing Review

The final Sprint 3 Test Case Tracker records:

- Total test cases: 100.
- Pass: 100.
- Fail: 0.
- Blocked: 0.
- Not Run: 0.
- Retest: 0.

The tracker previously recorded 48 Pass, 50 Blocked, and 2 Not Run cases.

The other 52 cases were reconciled during formal closeout using verified later implementation and successor integration evidence.

No new rerun was performed during the formal closeout reconciliation.

WBS 6.9 testing is complete.

## 5. Evidence Review

Sprint 3 evidence is stored under:

`docs/testing/evidence/sprint-3/`

Existing component evidence is unchanged.

Formal closeout updates these planned evidence records:

- S3-EV-005, WBS 6.5 document interface and frontend verification.
- S3-EV-006, WBS 6.7 Interview Preparation verification.
- S3-EV-007, WBS 6.8 integrated flow verification.
- S3-EV-008, WBS 6.9 regression and quality verification.

The closeout references verified successor evidence from:

- PR #59, WBS 6.5 Resume and Cover Letter Interface.
- PR #63, original WBS 6.7 Interview Preparation contribution record.
- PR #74, Sprint 4 Interview AI validation remediation.
- PR #78, final integrated Student workflows.
- PR #67, final WBS 7.9 Sprint 4 Integration and Testing.
- `docs/testing/sprint-4-test-cases.xlsx`.

## 6. WBS 6.7 Integration Traceability Note

WBS 6.7 requires a specific historical note.

PR #63 contains Joyee's original WBS 6.7 Interview Preparation interface contribution and targeted `feature/sprint-3`.

PR #63 was closed without merge into the historical Sprint 3 branch.

The final Interview Preparation implementation was later superseded and integrated through PR #78 on `feature/sprint-4`.

PR #78 explicitly retains PR #63 as the original WBS 6.7 contribution record and records the integrated implementation as the final workflow.

Formal Sprint 3 closeout accepts the verified successor implementation for the affected WBS 6.7, WBS 6.8, and WBS 6.9 cases.

This closeout does not state that the historical `feature/sprint-3` branch contained the final WBS 6.7 merge.

## 7. Sprint 3 Review

The Sprint 3 review confirms the intended application-document and Interview increment is available in the final integrated application.

Verified areas include:

- AI prompt and safety contracts.
- Resume generation.
- Cover Letter generation.
- Document UI.
- Interview Question generation.
- Interview Feedback generation.
- Interview Preparation UI.
- Editable and review-required AI output.
- Controlled provider and validation errors.
- Authentication.
- Student privacy and ownership.
- Responsive application workflows.
- Regression of Sprint 1 and Sprint 2 functions.

FR-08 Resume Builder is complete for the Sprint 3 scope.

FR-09 Cover Letter Builder is complete for the Sprint 3 scope.

FR-10 Interview Preparation is complete for the Sprint 3 scope.

## 8. Sprint 3 Retrospective

### 8.1 What Worked

The provider-independent AI boundary separated feature orchestration from the later concrete provider integration.

WBS 6.2 established shared prompt, safety, privacy, and schema contracts before dependent AI feature work matured.

Resume, Cover Letter, and Interview backend work used focused tests before later integration.

WBS 6.5 completed a usable document workflow with successful frontend lint, build, manual UI, required-field, and keyboard-interaction checks.

Later Sprint 4 integration proved the Sprint 3 architecture supported the concrete OpenAI provider without replacing the feature-service design.

Final Sprint 4 regression also provided one integrated baseline for document, Interview, authentication, profile, security, and earlier Sprint regression checks.

### 8.2 Issues Observed

Formal Sprint 3 closeout happened later than the planned Sprint 3 dates.

The Sprint 3 tracker became stale after implementation progressed.

WBS 6.7 did not merge into the historical Sprint 3 branch before the team moved forward.

PR #63 was superseded by later integration work, so contribution history and final integration history existed in different PRs.

WBS 6.8 and WBS 6.9 stayed marked Blocked even after their required behaviour was later demonstrated on the successor Sprint 4 baseline.

The Evidence Index retained placeholder Blocked records S3-EV-005 through S3-EV-008 after later verification existed.

Late Sprint 1 and Sprint 2 evidence commits also stayed on Sprint 3 and were not fully reconciled into Sprint 4 at the time.

### 8.3 Actions Carried Forward

Future Sprint work should:

- Reconcile the test tracker before the next Sprint reaches final review.
- Keep Evidence Index status synchronized with implementation and testing.
- Close integration WBS tasks before relying on successor Sprint work.
- Record superseded PR relationships immediately.
- Distinguish original contribution PRs from final integration PRs.
- Merge late predecessor evidence forward before successor Sprint closeout.
- Keep plan status text synchronized with GitHub integration status.
- Complete Review and Retrospective before the next Sprint reaches its own closeout.
- Preserve strict provider, privacy, and AI validation boundaries during integration.
- Use one final integration baseline for regression and evidence reconciliation.

## 9. WBS 6.10 Review and Retrospective Status

WBS 6.10 is complete through this formal closeout review and retrospective.

The review uses:

- The completed Sprint 3 implementation.
- The final 100-case Sprint 3 tracker.
- Existing Sprint 3 evidence.
- PR #59 WBS 6.5 verification.
- PR #63 contribution history.
- PR #74 Interview AI verification.
- PR #78 final Student workflow integration.
- PR #67 final Sprint 4 WBS 7.9 verification.

## 10. WBS 6.11 Completion Criteria

Sprint 3 completion is supported by the following verified state:

- WBS 6.2 complete.
- WBS 6.3 complete.
- WBS 6.4 complete.
- WBS 6.5 complete.
- WBS 6.6 complete.
- WBS 6.7 complete through accepted final successor integration.
- WBS 6.8 integration complete.
- WBS 6.9 testing complete.
- 100 of 100 planned Sprint 3 test cases are Pass.
- No Sprint 3 test case is Fail.
- No Sprint 3 test case is Blocked.
- No Sprint 3 test case is Not Run.
- No Sprint 3 test case is Retest.
- Core Resume flow is verified.
- Core Cover Letter flow is verified.
- Core Interview Question and Feedback flow is verified.
- Authentication and privacy controls are verified.
- AI safety and review requirements are verified.
- No unresolved Critical or High defect blocks the final integrated Sprint 3 core flow.
- WBS 6.10 review and retrospective is documented.

## 11. Sprint 3 Completion Status

WBS 6.8 Document and Interview Integration: COMPLETE

WBS 6.9 Sprint 3 Testing: COMPLETE

WBS 6.10 Sprint 3 Review and Retrospective: COMPLETE

WBS 6.11 Sprint 3 Complete: COMPLETE

Sprint 3 - Application Documents and Interview Preparation: COMPLETE

## 12. Merge-Forward Decision

The next repository action is to merge the formally closed Sprint 3 history forward into Sprint 4.

Target:

`feature/sprint-4`

Source:

`feature/sprint-3`

The merge must preserve the late Sprint 3 commits that are absent from the current Sprint 4 history.

The merge must also preserve the completed Sprint 4 WBS 7.9 state already present on `feature/sprint-4`.

After Sprint 3 is reconciled into Sprint 4, Sprint 4 formal closeout should finish before the completed Sprint 4 baseline merges forward into Sprint 5.

## 13. Closeout References

Primary references:

- `docs/project-management/sprint-3-plan.md`
- `docs/project-management/sprint-3-closeout.md`
- `docs/testing/sprint-3-test-plan.md`
- `docs/testing/sprint-3-test-cases.xlsx`
- `docs/testing/evidence/sprint-3/`
- `docs/system-design/sprint-3-integration-plan.md`
- `docs/project-management/work-breakdown-structure.md`
- `docs/project-management/product-backlog.md`
- PR #59: https://github.com/JeraldBucud/GradNavi/pull/59
- PR #63: https://github.com/JeraldBucud/GradNavi/pull/63
- PR #74: https://github.com/JeraldBucud/GradNavi/pull/74
- PR #78: https://github.com/JeraldBucud/GradNavi/pull/78
- PR #67: https://github.com/JeraldBucud/GradNavi/pull/67
