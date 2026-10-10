# GradNavi Sprint 5 Plan

Status: ACTIVE

WBS: 8.1 Sprint 5 Planning and Defect Triage

Sprint dates: 5 October to 9 October 2026

Final presentation: 12 October 2026

## 1. Purpose

Sprint 5 is the final stabilisation, deployment, documentation, verification, and project-closure Sprint for GradNavi.

The Sprint focuses on:

- Full regression testing.
- Security and permission testing.
- Performance and usability review.
- Defect correction.
- User acceptance testing.
- Backend and database deployment.
- Frontend deployment.
- Production verification.
- Technical documentation.
- User-guide completion.
- Final report and GitHub review.
- Project delivery.
- Final presentation preparation.

Sprint 5 does not introduce new core functional requirements unless the team approves a formal scope change.

## 2. Schedule Acceleration Historical Context

The following section preserves the project state recorded when Sprint 5 planning began.

Sprint 4 was still open at that planning checkpoint.

Sprint 4 is now formally complete and reconciled into Sprint 5.

Section 18 records the current authoritative execution baseline.

Sprint 5 planning has started before formal Sprint 4 closeout because the project has a fixed final presentation date of 12 October 2026 and only one scheduled week for Sprint 5.

The approved project schedule records WBS 7.11 Feature Complete as the predecessor of WBS 8.1.

The team is using a controlled overlap between Sprint 4 closeout and Sprint 5 finalisation to reduce further schedule delay.

This controlled overlap does not mark Sprint 4 as complete.

Sprint 4 implementation, integration, testing, review, and closeout work that is still incomplete remains tracked under Sprint 4.

Sprint 5 work may proceed where the required implementation dependency is already complete and integrated.

Sprint 5 work that depends on unfinished Sprint 4 functionality remains blocked until the required dependency is integrated.

The Sprint 5 plan will be updated after WBS 7.9, WBS 7.10, and WBS 7.11 are completed.

The final update will record:

- Final Sprint 4 testing results.
- Final Sprint 4 carry-over status.
- Confirmed defects.
- Final regression baseline.
- Sprint 4 review outcome.
- Sprint 4 feature-complete status.

## 3. Historical Sprint 4 Carry-Over at Sprint 5 Planning Start

The carry-over records below preserve the original Sprint 5 planning checkpoint.

They no longer describe the current repository state.

The resolved Sprint 4 state is recorded in Section 18.

Unfinished Sprint 4 work is recorded as carry-over or a blocker.

An unfinished feature is not automatically classified as a defect.

A defect is recorded only when documented expected behaviour is executed and the actual result fails the expected behaviour.

### CARRY-S4-001 - WBS 7.7 Admin Dashboard Interface

Type: Sprint 4 carry-over / blocker

Official owner: Joyee

GitHub record: PR #64

Current repository status:

- PR #64 remains open.
- PR #64 remains a Draft PR.
- WBS 7.7 is not integrated into the Sprint 4 baseline.
- The branch requires further integration work before Sprint 4 closeout.

Remaining work recorded in PR #64 includes:

- Connect FR-15 Popular Careers analytics.
- Connect FR-15 Common Skill Gaps analytics.
- Connect Pending Resource Reports to the LearningResourceReport review workflow.
- Complete User Management interface.
- Complete Career Management interface.
- Complete Skill Management interface.
- Complete Learning Resource Management interface.
- Add User Management role-change confirmation.
- Connect Recent Activity to WBS 7.8 audit records.

The published GitHub record does not confirm whether newer unpublished local work exists.

Required action:

The assigned member should complete and push the remaining implementation.

If the assigned member cannot complete the work within the remaining project schedule, the current work should be pushed with a clear handover so another team member can continue it.

### CARRY-S4-002 - Jerald Final Sprint 4 Integration Tests

Type: Sprint 4 testing blocker

Owner: Jerald

Current recorded result:

- Assigned tests: 46
- Completed: 41
- Passed: 41
- Failed: 0
- Blocked: 5

Blocked tests:

- S4-ENV-07 - Shared branch baseline verification.
- S4-REG-01 - Sprint 1 authentication regression.
- S4-REG-03 - Sprint 2 career-analysis regression.
- S4-REG-05 - Sprint 3 Interview regression.
- S4-REG-06 - Feature-complete Sprint 4 end-to-end smoke.

Current dependency:

WBS 7.7 Admin Dashboard Interface must be integrated before the final Jerald-owned Sprint 4 integration tests are executed.

Required action after WBS 7.7 integration:

1. Update the WBS 7.9 test execution branch from the latest Sprint 4 baseline.
2. Execute the five remaining tests.
3. Capture required evidence.
4. Update the Sprint 4 tracker.
5. Update the Sprint 4 testing-status document.
6. Complete the final evidence review.

### CARRY-S4-003 - Remaining WBS 7.9 Test Execution

Type: Sprint 4 testing carry-over

Current recorded Sprint 4 tracker checkpoint:

- Total test cases: 129
- Pass: 41
- Fail: 0
- Blocked: 20
- Not Run: 68
- Retest: 0

The exact dependency and owner of every remaining Blocked or Not Run test must continue to come from the approved Sprint 4 test tracker.

Do not assume every remaining test is blocked by WBS 7.7.

Required action:

Each team member completes the Sprint 4 test cases assigned to them and records:

- Actual result.
- Tester.
- Evidence.
- Dependency where blocked.
- Defect reference where failed.
- Retest result where required.

### CARRY-S4-004 - Sprint 4 Closeout

Type: Project-management dependency

Current state:

- WBS 7.9 Sprint 4 Integration and Testing: Open.
- WBS 7.10 Sprint 4 Review and Retrospective: Waiting for WBS 7.9.
- WBS 7.11 Feature Complete: Waiting for WBS 7.10.

Required action:

Complete the remaining Sprint 4 implementation and testing, perform the Sprint 4 review, and record WBS 7.11 when the approved completion conditions are met.

## 4. Reconciled Sprint 4 Baseline Available to Sprint 5

Sprint 4 is formally complete.

The reconciled Sprint 5 baseline contains:

- WBS 7.2 Job Description Extraction and Matching.
- WBS 7.3 OpenAI Service Integration.
- WBS 7.4 AI Response Validation and Error Handling.
- WBS 7.5 Job Matching Interface.
- WBS 7.6 Admin Models and API.
- WBS 7.7 Admin Dashboard Interface.
- WBS 7.8 Role Permissions and Audit Records.
- WBS 7.9 Sprint 4 Integration and Testing.
- WBS 7.10 Sprint 4 Review and Retrospective.
- WBS 7.11 Feature Complete.

Additional integrated work includes:

- Interview AI validation stabilisation.
- FR-13 Student Progress Dashboard.
- Global Student UI redesign.
- Account Settings and profile-first onboarding.
- Final Student Dashboard integration.
- Resume Builder integration.
- Cover Letter Builder integration.
- Interview Preparation integration.
- Document export improvements.
- Target Job Title support.
- Student Dashboard Recent Interview Activity.

Final Sprint 4 testing records:

- Total: 129.
- Pass: 129.
- Fail: 0.
- Blocked: 0.
- Not Run: 0.
- Retest: 0.

PR #85 completed the formal Sprint 4 closeout.

PR #86 reconciled the completed Sprint 4 baseline into feature/sprint-5.

## 5. Sprint 5 Work Breakdown

| WBS | Task | Owner | Planned Dates | Current Status |
| --- | --- | --- | --- | --- |
| 8.1 | Sprint 5 planning and defect triage | All Members | 05 Oct | Complete for reconciled baseline through PR #87; ongoing status maintenance continues |
| 8.2 | Full regression testing | All Members | 05-06 Oct | In Progress - Jerald checkpoint recorded in Draft PR #91; remaining team regression and final smoke review pending |
| 8.3 | Security and permission testing | Jerald | 05-06 Oct | Local scope complete through PR #80 and PR #89 - 30 Pass, 0 Fail, 0 Blocked, 2 deployment checks deferred |
| 8.4 | Performance and usability review | Joyee | 06-07 Oct | In Progress - PR #94 contains WebP optimisation and reported Lighthouse improvement; final WBS 8.4 review record pending |
| 8.5 | Bug fixing and final refinement | All Members | 07-08 Oct | In Progress - PR #81 merged earlier correction batch; PR #95 addresses confirmed Admin Dashboard mobile heading issue |
| 8.6 | User acceptance testing | All Members | 07-08 Oct | Ready - no completed UAT evidence identified |
| 8.7 | Backend and database deployment | MD | 07-08 Oct | In Progress - PR #93 aligned with Sprint 5; Railway staging and final deployment evidence pending |
| 8.8 | Frontend deployment | Joyee | 07-08 Oct | In Progress - Draft PR #92 aligned with Sprint 5; Vercel Preview configured for staging integration verification |
| 8.9 | Production verification | Jerald | 09 Oct | Blocked by final regression/UAT and completed backend/frontend deployment |
| 8.10 | Technical documentation finalisation | MD | 05-08 Oct | No completion evidence identified |
| 8.11 | User guide finalisation | Joyee | 05-08 Oct | In Progress by team status update; final repository evidence pending |
| 8.12 | Final report and GitHub review | Jerald | 05-09 Oct | In Progress - WBS 8.12 audit branch and final GitHub review baseline created |
| 8.13 | Project delivery complete | All Members | 09 Oct | Blocked by WBS 8.9, 8.10, 8.11, and 8.12 |
| 8.14 | Final presentation preparation | All Members | 09 Oct | Preparation may proceed |
| 8.15 | Final presentation | All Members | 12 Oct | Scheduled |

## 6. Sprint 5 Execution Priority

Sprint 4 carry-over is resolved.

Sprint 5 now uses the reconciled feature-complete baseline.

### Priority 1 - Final Verification

Complete:

- WBS 8.2 Full Regression Testing.
- WBS 8.3 Administrator frontend-route security follow-up.
- WBS 8.4 Performance and Usability Review.
- WBS 8.6 User Acceptance Testing.

### Priority 2 - Stabilisation

Where executed tests identify confirmed defects:

- Record the defect.
- Assign severity and priority.
- Assign an owner.
- Correct the defect.
- Perform the required retest.
- Preserve evidence.

WBS 8.5 remains active only for confirmed defects and required final refinement.

### Priority 3 - Deployment

Complete:

- WBS 8.7 Backend and Database Deployment.
- WBS 8.8 Frontend Deployment.

Deployment branches must first align with the current reconciled Sprint 5 baseline.

### Priority 4 - Production Verification

After backend and frontend deployment:

- Execute WBS 8.9 Production Verification.
- Verify authentication.
- Verify permissions.
- Verify primary Student workflows.
- Verify Administrator workflows.
- Verify AI provider behaviour.
- Verify production error handling.
- Complete deferred deployment-security checks.

### Priority 5 - Documentation, Delivery, and Presentation

Complete:

- WBS 8.10 Technical Documentation.
- WBS 8.11 User Guide.
- WBS 8.12 Final Report and GitHub Review.
- WBS 8.13 Project Delivery.
- WBS 8.14 Final Presentation Preparation.
- WBS 8.15 Final Presentation.

## 7. Defect Triage Baseline

Confirmed open Sprint 5 defects at Sprint 5 planning start: 0

No Sprint 4 test case in the current recorded WBS 7.9 checkpoint is marked Fail.

This does not mean the application is defect-free.

It means no unresolved Sprint 4 defect is currently supported by a recorded failed WBS 7.9 test in the available testing checkpoint.

New defects must be based on executed expected behaviour.

Each confirmed defect must record:

- Defect ID.
- Related Sprint.
- Related WBS.
- Related requirement.
- Related test case.
- Severity.
- Priority.
- Owner.
- Expected result.
- Actual result.
- Evidence reference.
- Status.
- Fix branch or commit.
- Retest status.
- Retest evidence.

## 8. Defect Severity

### Critical

A defect which:

- Prevents use of a core application flow.
- Causes serious security or privacy exposure.
- Causes data corruption or loss.
- Prevents deployment or production use.
- Has no acceptable workaround.

Critical defects block project release.

### High

A defect which:

- Breaks an important feature.
- Produces materially incorrect results.
- Breaks permissions or ownership behaviour.
- Causes significant AI validation failure.
- Has a limited or impractical workaround.

High defects should be corrected before project delivery where they affect required functionality.

### Medium

A defect which:

- Causes incorrect secondary behaviour.
- Creates a significant usability issue.
- Has a reasonable workaround.
- Does not block the primary project flow.

### Low

A defect which:

- Is cosmetic.
- Has minor wording or spacing impact.
- Does not materially affect expected behaviour.

## 9. Sprint 5 Testing Strategy

Sprint 5 testing should reuse approved earlier Sprint test cases where those tests remain valid.

Tests should not be invented solely to increase test counts.

Sprint 5 regression testing should verify:

- Authentication.
- Student Profile.
- Career Recommendations.
- Recommendation explanations.
- Skill Gap Analysis.
- Career Readiness.
- Learning Resources.
- Career Roadmap.
- Job Matching.
- Resume Builder.
- Cover Letter Builder.
- Interview Preparation.
- Student Dashboard.
- Account Settings.
- Administrator functions.
- Role permissions.
- Audit records.
- AI provider integration.
- AI validation.
- Privacy behaviour.
- Error handling.
- Responsive behaviour.
- Browser behaviour.
- Production deployment behaviour.

WBS 8.3 will provide dedicated security and permission verification.

WBS 8.4 will provide dedicated performance and usability review.

WBS 8.6 will provide final user acceptance evidence.

## 10. Sprint 5 Quality Gates

Project delivery requires:

- Priority Student flows pass.
- Priority Administrator flows pass.
- No unresolved Critical release defect remains.
- Authentication checks pass.
- Permission checks pass.
- Privacy checks pass.
- Secret-management checks pass.
- AI validation checks pass.
- AI fallback behaviour passes.
- Scoring repeatability checks pass.
- Major usability barriers are corrected.
- Deployment smoke tests pass.
- Recovery and fallback instructions are available.
- Required technical documentation is complete.
- Required testing evidence is complete.
- Contribution records are preserved.
- Final presentation material is ready.

## 11. Current Planning Risks

### R02 - Team Delivery

Risk:

Assigned work is completed later than agreed internal dates.

Current relevance:

High.

Sprint 4 is complete. The current delivery risk is concentrated in remaining Sprint 5 verification, deployment, documentation, and project-delivery work.

Current response:

- Request immediate status updates.
- Require unfinished work to be pushed.
- Allow handover where the assigned owner cannot complete the work.
- Continue independent finalisation tasks in parallel.

### R11 - Testing and Deployment

Risk:

Testing begins late, Critical defects remain open, or deployment fails.

Current relevance:

High.

Current response:

- Continue testing completed features.
- Prepare full regression testing early.
- Start security and permission testing early.
- Protect time for deployment and production verification.
- Stop unnecessary feature expansion.

### R13 - Evidence and Final Delivery

Risk:

Testing evidence, contribution evidence, reports, or presentation material is incomplete.

Current relevance:

Medium.

Current response:

- Preserve GitHub history.
- Preserve testing evidence.
- Maintain contribution records.
- Complete documentation during Sprint 5 rather than after development ends.
- Prepare presentation evidence throughout finalisation.

## 12. Schedule Control

The Microsoft Project schedule remains the authoritative planning baseline.

WBS 8.1 started while Sprint 4 closeout was still active. This was a controlled schedule acceleration caused by the fixed final presentation date and the remaining Sprint 4 delivery delay at that time.

The overlap did not silently change approved task ownership.

The overlap did not mark incomplete Sprint 4 tasks complete. Sprint 4 completion was recorded later through the formal closeout process.

Any permanent change to:

- WBS ownership.
- WBS dependencies.
- Sprint allocation.
- Project scope.
- Planned dates.

must be agreed by the team and reflected in the affected project-management records.

## 13. Team Handover Rule

If a member cannot complete an assigned task within the remaining project schedule:

1. Push the latest work.
2. Confirm the branch name.
3. State what is complete.
4. State what remains incomplete.
5. State known issues or blockers.
6. State any setup or test requirements.
7. Notify the team.
8. Allow another member to continue the work.

Unfinished implementation should not remain only on a local development machine.

## 14. Sprint 5 Planning Decisions

Current decisions:

- Sprint 5 originally started before formal Sprint 4 closeout under the controlled-overlap process.
- Sprint 4 is formally closed.
- WBS 7.7 Admin Dashboard Interface is integrated.
- WBS 7.9 Sprint 4 Integration and Testing is complete.
- The final Sprint 4 tracker records 129 of 129 test cases as Pass.
- WBS 7.10 Sprint 4 Review and Retrospective is complete.
- WBS 7.11 Feature Complete is reached.
- PR #86 reconciled the completed Sprint 4 baseline into Sprint 5.
- WBS 8.3 local security and permission testing is complete through PR #80 and PR #89.
- Two WBS 8.3 deployment-security checks remain deferred to WBS 8.7 through WBS 8.9.
- WBS 8.2 remains in progress through Draft PR #91.
- WBS 8.4 remains in progress through Draft PR #94.
- WBS 8.5 includes merged Sprint 5 corrections and the open PR #95 usability fix.
- WBS 8.7 remains in progress through PR #93.
- WBS 8.8 remains in progress through Draft PR #92.
- WBS 8.12 is in progress on `jerald/wbs-8.12-final-report-github-review`.
- Sprint 5 introduces no unapproved core feature expansion.
- Remaining work focuses on final regression, usability closeout, UAT, deployment, production verification, documentation, delivery, and presentation preparation.
- Final presentation remains scheduled for 12 October 2026.

## 15. Immediate Actions

### Jerald

- Continue WBS 8.12 Final Report and GitHub Review.
- Resume the final WBS 8.2 combined regression review when the remaining team results are available.
- Run the final integrated S4-REG-06 smoke regression at the WBS 8.2 closeout stage.
- Execute WBS 8.9 Production Verification after WBS 8.7 and WBS 8.8 reach the required deployed state.
- Complete the two deployment-deferred WBS 8.3 security checks during production verification.
- Coordinate final integration and WBS 8.13 delivery review where required.

### Joyee

- Complete the WBS 8.4 review record and final PR #94 disposition.
- Complete the confirmed WBS 8.5 mobile usability correction in PR #95.
- Complete WBS 8.8 staging/full-flow verification and final PR #92 disposition.
- Finalise WBS 8.11 User Guide evidence.
- Complete assigned WBS 8.2 regression work.
- Participate in WBS 8.6 User Acceptance Testing.

### MD

- Complete WBS 8.7 Railway staging/deployment evidence and final PR #93 disposition.
- Complete WBS 8.10 Technical Documentation Finalisation.
- Complete assigned WBS 8.2 regression work.
- Participate in WBS 8.6 User Acceptance Testing.

### All Members

- Complete WBS 8.2 Full Regression Testing.
- Complete WBS 8.6 User Acceptance Testing.
- Record and retest only confirmed defects under WBS 8.5.
- Review final deployment and production evidence.
- Review final documentation and contribution evidence.
- Complete WBS 8.13 Project Delivery.
- Complete WBS 8.14 Final Presentation Preparation.
- Preserve final assessment evidence.

## 16. Planning Alignment Items

### ALIGN-S5-001 - FR-13 Progress Dashboard

Current implementation state:

- FR-13 implementation is present in the Sprint 4 baseline.
- PR #75 added the Student Progress Dashboard.
- The Product Backlog execution status is updated from Backlog to Testing.

Current planning discrepancy:

- Planned Sprint remains recorded as Schedule alignment required.
- Implementation Leads remain recorded as To be confirmed.
- No dedicated Microsoft Project task is currently identified.
- The Functional Requirements document records FR-13 as Draft for approval.

Required planning action:

The team should confirm the approved schedule and WBS mapping for FR-13 before final project closeout.

The execution-status update does not silently create a new Microsoft Project task or alter the approved WBS.

### ALIGN-S5-002 - FR-16 AI Content Review

Current planning state:

- Functional requirement status remains Draft for approval.
- Product Backlog status remains Backlog.
- Planned Sprint remains Schedule alignment required.
- No dedicated Microsoft Project task is currently identified.

Required planning action:

Confirm whether existing Resume Builder, Cover Letter Builder, AI generation, document editing, and review behaviour fully satisfy FR-16.

If FR-16 is accepted as implemented through existing work, record the approved WBS mapping before changing its final backlog status.

Do not mark FR-16 complete solely from related implementation.

### ALIGN-S5-003 - FR-17 Data Deletion

Current planning state:

- Functional requirement status remains Draft for approval.
- Product Backlog status remains Backlog.
- Planned Sprint remains Schedule alignment required.
- No dedicated Microsoft Project task is currently identified.

Required planning action:

Confirm whether FR-17 remains required for GradNavi V1 and assign an approved implementation and testing path if required.

Do not mark FR-17 complete without verified profile-deletion and generated-document-deletion behaviour.

## 17. Plan Update Rule

This plan is the active Sprint 5 execution baseline.

Update this document when:

- WBS 8.2 Full Regression Testing changes status.
- WBS 8.3 follow-up security checks change status.
- WBS 8.4 Performance and Usability Review changes status.
- A confirmed Sprint 5 defect is recorded.
- WBS 8.5 corrective work changes status.
- WBS 8.6 User Acceptance Testing changes status.
- Backend deployment changes status.
- Frontend deployment changes status.
- Production verification changes status.
- Technical documentation changes status.
- User-guide status changes.
- Final report status changes.
- Project-delivery status changes.
- Presentation preparation changes status.

All updates must reflect repository, testing, deployment, or approved project-management evidence.

## 18. Reconciled Sprint 5 Baseline Update - 9 October 2026

This section records the authoritative Sprint 5 execution baseline after formal Sprint 4 closure and reconciliation.

The original controlled-overlap and Sprint 4 carry-over records are retained as historical planning evidence.

Where an earlier historical section conflicts with this section, this reconciled section records the current project state.

### 18.1 Sprint 4 Closure

Sprint 4 is formally complete.

Final Sprint 4 tracker:

- Total: 129.
- Pass: 129.
- Fail: 0.
- Blocked: 0.
- Not Run: 0.
- Retest: 0.

Final Sprint 4 WBS state:

- WBS 7.7 Admin Dashboard Interface: Complete.
- WBS 7.9 Sprint 4 Integration and Testing: Complete.
- WBS 7.10 Sprint 4 Review and Retrospective: Complete.
- WBS 7.11 Feature Complete: Complete.

PR #85 completed the formal Sprint 4 closeout.

PR #86 reconciled the completed Sprint 4 baseline into feature/sprint-5.

### 18.2 Reconciled Technical Baseline

PR #86 validation recorded:

- Merge conflicts: 0.
- Django system check: Pass.
- Full backend regression: 1065 of 1065 tests Pass.
- Frontend lint: 0 warnings and 0 errors.
- Frontend production build: Pass.
- Staged diff check: Pass.

The first backend regression attempt was blocked because the local PostgreSQL service was not running.

After PostgreSQL was started, all 1065 backend tests passed.

### 18.3 Current Sprint 5 Audit

#### WBS 8.1 Sprint 5 Planning and Defect Triage

Status: Reconciled baseline complete.

PR #87 reconciled the Sprint 5 planning baseline after Sprint 4 closeout.

Ongoing status maintenance continues as Sprint 5 evidence changes.

#### WBS 8.2 Full Regression Testing

Status: In Progress.

Draft PR #91 records Jerald's integration and security-critical regression checkpoint.

Verified checkpoint results include:

- S4-RESUME-04: Pass after fix and retest.
- S4-JOB-06: Pass.
- PR #90 corrected Resume grounding and ATS export spacing.

Remaining work includes:

- Remaining team regression results.
- Combined regression review.
- Final S4-REG-06 integrated smoke regression.
- Final WBS 8.2 status update.

#### WBS 8.3 Security and Permission Testing

Status: Local scope complete.

PR #80 and PR #89 together record the final local checkpoint:

- Total: 32.
- Pass: 30.
- Fail: 0.
- Blocked: 0.
- Deferred: 2.

S5-SEC-FE-01 passed after WBS 7.7 integration.

S5-SEC-DEP-01 and S5-SEC-DEP-02 remain deployment-stage checks for WBS 8.7 through WBS 8.9.

#### WBS 8.4 Performance and Usability Review

Status: In Progress.

Draft PR #94 contains the landing/authentication WebP optimisation.

The PR description reports:

- image payload reduced from about 17.8 MB to about 1 MB.
- Lighthouse desktop homepage Performance improved from 75 to 96.
- Largest Contentful Paint improved from 8.5 seconds to 1.2 seconds.
- lint completed with 0 errors and 0 warnings.
- production build passed.

A dedicated WBS 8.4 review record is still required before formal completion.

#### WBS 8.5 Bug Fixing and Final Refinement

Status: In Progress.

PR #81 merged the earlier Sprint 5 correction batch.

PR #95 addresses the confirmed Admin Dashboard mobile section-heading usability issue found during final review.

Further WBS 8.5 work must relate to confirmed defects or required final refinement.

#### WBS 8.6 User Acceptance Testing

Status: Ready.

No completed UAT evidence has been identified.

#### WBS 8.7 Backend and Database Deployment

Status: In Progress.

PR #93 is aligned with the current Sprint 5 baseline.

The branch contains:

- Gunicorn production dependency.
- environment-driven DEBUG configuration with a False fallback.
- allowed-host configuration.
- CORS and CSRF configuration.
- secure cookie behaviour for production.
- proxy HTTPS support.
- STATIC_ROOT.
- deployment environment documentation.

GitHub reports successful Railway and Vercel checks for the PR head commit.

Final WBS 8.7 closeout still requires the agreed Railway staging/deployment evidence.

#### WBS 8.8 Frontend Deployment

Status: In Progress.

Draft PR #92 is aligned with the current Sprint 5 baseline.

The branch contains:

- configurable frontend API base URL.
- Vercel SPA rewrites.
- frontend environment example.

The Vercel Preview has been configured for Railway staging integration testing.

Full staging flow verification remains pending.

#### WBS 8.9 Production Verification

Status: Blocked.

Dependencies include:

- final WBS 8.2 regression state.
- WBS 8.6 UAT.
- WBS 8.7 deployment.
- WBS 8.8 deployment.
- required WBS 8.5 fixes.

#### WBS 8.10 Technical Documentation Finalisation

Status: No completion evidence identified.

#### WBS 8.11 User Guide Finalisation

Status: In Progress by team status update.

Joyee reported that the Student features, Administrator guide, troubleshooting, and screenshots are substantially prepared.

Final repository evidence is still required before WBS 8.11 is marked complete.

#### WBS 8.12 Final Report and GitHub Review

Status: In Progress.

Branch:

`jerald/wbs-8.12-final-report-github-review`

Current checkpoint includes:

- final GitHub review baseline.
- README reconciliation.
- product backlog reconciliation.
- contribution reconciliation.
- functional and non-functional requirement status interpretation.
- requirements mapping review.

WBS 8.12 must be reviewed again after the remaining Sprint 5 delivery PRs and evidence are final.

#### WBS 8.13 Project Delivery Complete

Status: Blocked.

Dependencies include:

- WBS 8.9.
- WBS 8.10.
- WBS 8.11.
- WBS 8.12.

#### WBS 8.14 Final Presentation Preparation

Status: Preparation may proceed.

Formal completion evidence has not yet been identified.

#### WBS 8.15 Final Presentation

Status: Scheduled for 12 October 2026.

### 18.4 Current Execution Order

The current execution order is:

1. Complete the WBS 8.3 frontend permission follow-up.
2. Complete WBS 8.2 Full Regression Testing.
3. Complete WBS 8.4 Performance and Usability Review.
4. Complete WBS 8.6 User Acceptance Testing.
5. Reconcile and complete WBS 8.7 Backend and Database Deployment.
6. Reconcile and complete WBS 8.8 Frontend Deployment.
7. Complete WBS 8.9 Production Verification.
8. Complete WBS 8.10 Technical Documentation.
9. Complete WBS 8.11 User Guide.
10. Complete WBS 8.12 Final Report and GitHub Review.
11. Complete WBS 8.13 Project Delivery.
12. Complete WBS 8.14 Final Presentation Preparation.
13. Deliver WBS 8.15 Final Presentation.
