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

## 2. Schedule Acceleration

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

## 3. Current Sprint 4 Carry-Over

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

## 4. Completed Sprint 4 Implementation Available to Sprint 5

The current Sprint 4 baseline contains integrated implementation for:

- WBS 7.2 Job Description Extraction and Matching.
- WBS 7.3 OpenAI Service Integration.
- WBS 7.4 AI Response Validation and Error Handling.
- WBS 7.5 Job Matching Interface.
- WBS 7.6 Admin Models and API.
- WBS 7.8 Role Permissions and Audit Records.

Additional integrated Sprint 4 work includes:

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

WBS 7.7 Admin Dashboard Interface remains the main unfinished Sprint 4 implementation dependency.

## 5. Sprint 5 Work Breakdown

| WBS | Task | Owner | Planned Dates | Current Readiness |
| --- | --- | --- | --- | --- |
| 8.1 | Sprint 5 planning and defect triage | All Members | 05 Oct | Active |
| 8.2 | Full regression testing | All Members | 05-06 Oct | Partial start allowed on stable integrated features |
| 8.3 | Security and permission testing | Jerald | 05-06 Oct | Ready to start on integrated functionality |
| 8.4 | Performance and usability review | Joyee | 06-07 Oct | Partial start allowed on stable integrated features |
| 8.5 | Bug fixing and final refinement | All Members | 07-08 Oct | Starts when confirmed defects are identified |
| 8.6 | User acceptance testing | All Members | 07-08 Oct | Wait for stable feature-complete test baseline |
| 8.7 | Backend and database deployment | MD | 07-08 Oct | Wait for regression readiness |
| 8.8 | Frontend deployment | Joyee | 07-08 Oct | Wait for regression readiness |
| 8.9 | Production verification | Jerald | 09 Oct | Wait for deployment and final fixes |
| 8.10 | Technical documentation finalisation | MD | 05-08 Oct | Preparation may start now |
| 8.11 | User guide finalisation | Joyee | 05-08 Oct | Preparation may start now |
| 8.12 | Final report and GitHub review | Jerald | 05-09 Oct | Preparation may start now |
| 8.13 | Project delivery complete | All Members | 09 Oct | Blocked by final delivery dependencies |
| 8.14 | Final presentation preparation | All Members | 09 Oct | Preparation material may be developed early |
| 8.15 | Final presentation | All Members | 12 Oct | Scheduled |

## 6. Sprint 5 Execution Priority

Sprint 5 uses the following execution priority.

### Priority 1 - Complete Sprint 4 Carry-Over

- Finish WBS 7.7.
- Complete remaining WBS 7.9 testing.
- Resolve any confirmed blocking defects.
- Complete WBS 7.10.
- Record WBS 7.11.

### Priority 2 - Start Independent Sprint 5 Verification

Work which does not require unfinished WBS 7.7 may proceed.

This includes:

- WBS 8.3 Security and Permission Testing.
- Preparation for WBS 8.2 Full Regression Testing.
- Preparation for WBS 8.10 Technical Documentation.
- Preparation for WBS 8.11 User Guide.
- Preparation for WBS 8.12 Final Report and GitHub Review.

### Priority 3 - Stabilisation

After testing identifies confirmed defects:

- Record each defect.
- Assign severity and priority.
- Assign an owner.
- Correct the defect.
- Perform the required retest.
- Preserve evidence.

### Priority 4 - Deployment and Production Verification

After the application reaches a stable regression baseline:

- Deploy backend and database.
- Deploy frontend.
- Run production smoke testing.
- Verify authentication and permissions.
- Verify primary Student workflows.
- Verify Administrator workflows.
- Verify AI provider behaviour.
- Verify production error handling.

### Priority 5 - Closure and Presentation

Complete:

- UAT.
- Technical documentation.
- User guide.
- Final report.
- GitHub review.
- Contribution evidence.
- Project delivery review.
- Demonstration preparation.
- Presentation rehearsal.

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

Sprint 4 work remains unfinished while the project enters its final scheduled week.

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

Starting WBS 8.1 while Sprint 4 closeout remains active is a controlled schedule acceleration caused by the fixed final presentation date and remaining Sprint 4 delivery delay.

The overlap does not silently change approved task ownership.

It does not mark incomplete Sprint 4 tasks complete.

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

- Sprint 5 planning starts before formal Sprint 4 closeout.
- Sprint 4 remains open.
- Sprint 4 carry-over remains tracked separately.
- Unfinished work is not automatically treated as a defect.
- Stable Sprint 5 work proceeds in parallel.
- WBS 7.7 remains the main Sprint 4 implementation blocker.
- Final Sprint 4 test execution resumes after WBS 7.7 integration.
- WBS 8.3 Security and Permission Testing is the next Jerald-owned Sprint 5 task.
- Sprint 5 introduces no unapproved core feature expansion.
- Final project delivery remains targeted for 9 October 2026.
- Final presentation remains scheduled for 12 October 2026.

## 15. Immediate Actions

### Jerald

- Maintain Sprint 5 planning.
- Prepare WBS 8.3 Security and Permission Testing.
- Resume the five blocked Sprint 4 integration tests after WBS 7.7 integration.
- Prepare WBS 8.12 Final Report and GitHub Review.
- Coordinate final integration where required.

### Joyee

- Complete or hand over WBS 7.7 Admin Dashboard Interface.
- Complete assigned Sprint 4 testing.
- Prepare WBS 8.4 Performance and Usability Review.
- Prepare WBS 8.11 User Guide Finalisation.
- Prepare for WBS 8.8 Frontend Deployment.

### MD

- Complete assigned Sprint 4 testing.
- Prepare WBS 8.7 Backend and Database Deployment.
- Prepare WBS 8.10 Technical Documentation Finalisation.

### All Members

- Complete Sprint 4 carry-over as quickly as possible.
- Participate in WBS 8.2 Full Regression Testing.
- Record defects from executed tests.
- Participate in WBS 8.5 Bug Fixing and Final Refinement.
- Participate in WBS 8.6 User Acceptance Testing.
- Review final delivery evidence.
- Prepare for the final presentation.

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

This plan is an active working Sprint 5 baseline.

Update this document when:

- WBS 7.7 is integrated.
- Sprint 4 testing status changes materially.
- WBS 7.9 completes.
- WBS 7.10 completes.
- WBS 7.11 is reached.
- A confirmed Sprint 5 defect is recorded.
- A task owner changes.
- Deployment status changes.
- Production verification completes.
- Final project-delivery status changes.

All updates should reflect actual project evidence rather than planned dates alone.
