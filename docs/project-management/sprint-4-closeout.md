# GradNavi Sprint 4 Closeout

Status: Complete

Sprint: Sprint 4 - Job Matching, AI Integration, and Administration

Planned Sprint dates: 21 September to 2 October 2026

Formal closeout record date: 9 October 2026

WBS ownership: All Members

## 1. Purpose

This record formally closes Sprint 4 after final reconciliation of implementation, integration, testing, predecessor history, and evidence.

Sprint 4 completes the main feature-development phase before Sprint 5 final regression, deployment, documentation, project delivery, and presentation work.

## 2. WBS Alignment

Sprint 4 closeout covers:

- WBS 7.9 Sprint 4 Integration and Testing.
- WBS 7.10 Sprint 4 Review and Retrospective.
- WBS 7.11 Feature Complete.

WBS 7.10 depends on WBS 7.9.

WBS 7.11 depends on WBS 7.10.

## 3. Sprint 4 Outcome

The completed Sprint 4 increment includes:

- Job Description Matching backend.
- Job Matching Student interface.
- OpenAI Service Integration.
- AI Response Validation and Error Handling.
- Resume AI provider integration.
- Cover Letter AI provider integration.
- Interview AI provider integration.
- Admin Models and API.
- Admin Dashboard.
- User Management.
- Career Management.
- Skill Management.
- Learning Resource Management.
- Resource Reports.
- Role Permissions.
- Audit Records.
- Admin Analytics.
- Student Progress Dashboard as additional implemented scope.
- Cross-Sprint regression verification.

## 4. WBS 7.9 Testing Review

The final Sprint 4 Test Case Tracker records:

- Total: 129.
- Pass: 129.
- Fail: 0.
- Blocked: 0.
- Not Run: 0.
- Retest: 0.

Team execution:

- Jerald: 46 of 46 Pass.
- MD: 38 of 38 Pass.
- Joyee: 45 of 45 Pass.

Final testing verified:

- Authentication.
- Student Profile.
- Career Recommendations.
- Skill Gap.
- Career Readiness.
- Learning Resources.
- Career Roadmap.
- Job Matching.
- Resume generation.
- Cover Letter generation.
- Interview Questions.
- Interview Feedback.
- AI response validation.
- AI provider failure behaviour.
- Admin APIs.
- Admin Dashboard.
- User Management.
- Career Management.
- Skill Management.
- Learning Resource Management.
- Resource Reports.
- Role Permissions.
- Audit Records.
- Security and privacy controls.
- Cross-Sprint regression.
- Feature-complete end-to-end smoke flow.

No unresolved Critical or High blocking defect was observed during the final integration smoke run.

## 5. Evidence Review

Sprint 4 evidence is stored under:

docs/testing/evidence/sprint-4/

The final evidence set includes automated, API, regression, frontend, integration, permission, audit, AI validation, and end-to-end evidence.

The Sprint 4 Postman collection is stored at:

docs/testing/postman/GradNavi-Sprint4.postman_collection.json

The final tracker and Evidence Index provide per-test traceability.

## 6. Sprint 3 Reconciliation

Sprint 3 formally closed before Sprint 4 formal closeout.

PR #84 reconciled the completed Sprint 3 history into feature/sprint-4.

The reconciliation preserved:

- Sprint 4 WBS 7.9 completion.
- Sprint 3 formal closeout.
- Late Sprint 2 evidence.
- The newer Sprint 4 version of the Sprint 1 evidence workbook.

This resolved the predecessor-history gap before Sprint 4 closure.

## 7. Sprint 4 Review

The Sprint 4 review confirms the planned core Sprint 4 implementation is integrated.

Verified areas include:

- FR-07 Job Description Matching.
- External AI provider integration.
- AI response validation.
- Controlled provider failure handling.
- Basic Administration.
- Admin Analytics.
- Role enforcement.
- Audit behaviour.
- Student and Administrator integrated flows.
- Regression across Sprint 1, Sprint 2, and Sprint 3 functionality.

FR-13 Progress Dashboard was also implemented and merged through PR #75.

## 8. Sprint 4 Retrospective

### 8.1 What Worked

The provider-independent AI boundary created during Sprint 3 supported Sprint 4 OpenAI integration without replacing feature-service architecture.

The final test allocation separated ownership by technical responsibility rather than forcing equal numerical distribution.

The team completed a 129-case Sprint 4 tracker with all planned cases passing.

Admin permission and audit behaviour received direct backend verification instead of relying on frontend visibility.

Final end-to-end testing covered Student and Administrator flows.

Late Sprint 3 history was reconciled before formal Sprint 4 closure.

### 8.2 Issues Observed

Formal Sprint 4 closeout occurred after the planned 2 October finish date.

Sprint 3 remained formally open after Sprint 4 work had already started.

WBS 7.7 integration delayed the final WBS 7.9 regression and end-to-end cases.

Sprint 5 planning started before Sprint 4 formal closure because of the fixed final project schedule.

Implementation ownership changed for several WBS tasks during delivery.

Planning and testing status documents required later reconciliation after implementation moved ahead.

Several requirements lacked dedicated Microsoft Project task mapping.

### 8.3 Actions Carried Forward

Sprint 5 should:

- Preserve the final Sprint 4 test and evidence baseline.
- Reconcile Sprint 4 into Sprint 5 before final project closure.
- Keep actual implementer records separate from official WBS ownership.
- Update testing records when dependencies merge.
- Keep deployment evidence synchronized with final regression results.
- Record production verification separately from local verification.
- Preserve security and permission evidence.
- Finalise planning alignment for FR-13.
- Finalise planning alignment for FR-16.
- Decide the final project treatment of FR-17.
- Avoid unrelated feature expansion during finalisation.
- Complete deployment, documentation, report, and presentation work against the reconciled Sprint 5 baseline.

## 9. Schedule Alignment

### FR-13 Progress Dashboard

FR-13 is implemented and merged through PR #75.

The Product Backlog still records schedule alignment as required because the Microsoft Project schedule has no dedicated task.

Sprint 5 tracks formal alignment as ALIGN-S5-001.

### FR-15 Admin Analytics

FR-15 is included within Sprint 4 through WBS 7.6, WBS 7.7, and WBS 7.9.

The final integrated administration flow verifies the Sprint 4 implementation.

### FR-16 AI Content Review

Document-generation flows support Student review and editing.

The Product Backlog still records FR-16 as Backlog with no dedicated Microsoft Project task.

Sprint 5 tracks formal alignment as ALIGN-S5-002.

This closeout does not mark FR-16 Done.

### FR-17 Data Deletion

The Product Backlog records FR-17 as Backlog.

No dedicated Microsoft Project task exists.

Sprint 5 tracks formal alignment as ALIGN-S5-003.

This closeout does not claim FR-17 implementation.

## 10. WBS 7.10 Review and Retrospective Status

WBS 7.10 is complete through this formal Sprint 4 review and retrospective.

The review uses the completed implementation state, 129-case tracker, Sprint 4 test plan, Sprint 4 testing status, evidence records, PR #67, and PR #84.

## 11. WBS 7.11 Feature Complete Criteria

WBS 7.11 is supported by the following state:

- WBS 7.2 is integrated.
- WBS 7.3 is integrated.
- WBS 7.4 is integrated.
- WBS 7.5 is integrated.
- WBS 7.6 is integrated.
- WBS 7.7 is integrated.
- WBS 7.8 is integrated.
- WBS 7.9 is complete.
- 129 of 129 Sprint 4 test cases are Pass.
- No Sprint 4 test case is Fail.
- No Sprint 4 test case is Blocked.
- No Sprint 4 test case is Not Run.
- Required regression testing passes.
- Required test evidence is recorded.
- No unresolved Critical or High defect blocks the integrated Sprint 4 core flow.
- Sprint 3 predecessor history is reconciled.
- Schedule-alignment items are documented.
- WBS 7.10 review and retrospective is complete.

WBS 7.11 Feature Complete applies to the scheduled Sprint 4 scope and recorded Sprint 4 completion criteria.

## 12. Sprint 4 Completion Status

WBS 7.9 Sprint 4 Integration and Testing: COMPLETE

WBS 7.10 Sprint 4 Review and Retrospective: COMPLETE

WBS 7.11 Feature Complete: COMPLETE

Sprint 4 - Job Matching, AI Integration, and Administration: COMPLETE

## 13. Merge-Forward Decision

The completed Sprint 4 baseline will merge forward into:

feature/sprint-5

Sprint 5 already contains work started under the documented controlled-overlap process.

The merge-forward must preserve both completed Sprint 4 history and newer Sprint 5 work.

After reconciliation, Sprint 5 becomes the active finalisation baseline.

## 14. Closeout References

Primary closeout references:

- docs/project-management/sprint-4-plan.md
- docs/testing/sprint-4-test-plan.md
- docs/testing/sprint-4-test-cases.xlsx
- docs/testing/sprint-4-testing-status.md
- docs/testing/evidence/sprint-4/
- docs/testing/postman/GradNavi-Sprint4.postman_collection.json
- docs/project-management/sprint-3-closeout.md
- docs/project-management/product-backlog.md
- docs/requirements/functional-requirements.md
- PR #67
- PR #75
- PR #84