# GradNavi Sprint 1 Closeout

Status: Complete

Sprint: Sprint 1 - Foundation and Student Profile

Planned sprint dates: 10 August to 21 August 2026

Formal closeout record date: 26 September 2026

WBS ownership: All Members

## 1. Purpose

This record closes Sprint 1 after final reconciliation of implementation, integration, testing, and evidence.

Sprint 1 established the GradNavi application foundation, authentication flow, Student Profile backend, Student Profile interface, and authenticated frontend-to-backend integration.

## 2. WBS Alignment

Sprint 1 closeout covers:

- WBS 4.9 Sprint 1 unit and API testing.
- WBS 4.10 Sprint 1 review and retrospective.
- WBS 4.11 Sprint 1 complete.

The approved WBS records all three tasks as All Members work.

WBS 4.10 depends on WBS 4.9.

WBS 4.11 depends on WBS 4.10.

## 3. Sprint 1 Outcome

The Sprint 1 target was an authenticated Student Profile flow.

The completed increment includes:

- Django and PostgreSQL project foundation.
- React frontend foundation and routing.
- Student registration.
- Student login.
- JWT access and refresh handling.
- Current authenticated-user retrieval.
- Logout and refresh-token invalidation.
- Password-reset behaviour.
- Protected frontend routing.
- Student Profile models.
- Student Profile API.
- Student Profile frontend interface.
- Authenticated Student Profile retrieval.
- Student Profile updates.
- Profile persistence.
- Profile ownership protection.
- Validation and controlled error handling.
- Frontend-to-backend integration.
- PostgreSQL relationship verification.
- Sprint 1 regression testing.

## 4. WBS 4.9 Testing Review

The final Sprint 1 Test Case Tracker records:

- Total test cases: 61.
- Pass: 61.
- Fail: 0.
- Blocked: 0.
- Not Run: 0.

The final 19 Authentication and Student Profile API cases assigned to MD were completed and integrated into the closeout branch.

These cases cover:

- Registration.
- Login.
- Current-user retrieval.
- JWT refresh.
- Logout.
- Password reset.
- Unauthenticated Student Profile retrieval.
- Invalid Student Profile updates.
- Empty partial profile updates.
- Ownership-field protection.

WBS 4.9 test execution is complete.

## 5. Evidence Review

Sprint 1 evidence is stored under:

`docs/testing/evidence/sprint-1/`

The Sprint 1 Evidence Index contains 70 entries.

Evidence IDs are continuous from:

`EV-001` through `EV-070`

The final MD testing evidence occupies:

`EV-048` through `EV-070`

The Evidence Index and tracker references were reconciled during formal closeout.

## 6. FE-AUTH-04 Traceability Note

`FE-AUTH-04` is recorded as Pass in the Sprint 1 Test Case Tracker.

The test covers frontend access-token refresh behaviour, replacement token storage, protected current-user retry, successful protected-route continuation, and failed-refresh cleanup.

The implemented frontend refresh path is present in:

- `frontend/src/components/auth/ProtectedRoute.jsx`
- `frontend/src/services/authService.js`

The tracker row does not contain a direct Evidence ID.

This is recorded as a legacy evidence-link traceability gap.

The Sprint 1 test record still reports the case as executed and passed.

No new test result is introduced by this closeout record.

## 7. Sprint 1 Review

The Sprint 1 review confirms the planned foundation and Student Profile increment was delivered.

Verified areas include:

- Authentication API behaviour.
- Frontend authentication integration.
- JWT handling.
- Student Profile retrieval.
- Student Profile updates.
- Student Profile validation.
- Student Profile persistence.
- Student ownership isolation.
- Database connectivity.
- Database migrations.
- Frontend profile integration.
- Security checks.
- Regression testing.

FR-01 Account Registration and Authentication is complete for Sprint 1 scope.

FR-02 Student Profile is complete for Sprint 1 scope.

## 8. Sprint 1 Retrospective

### 8.1 What Worked

The team established shared API, security, and Student Profile design documents before final integration.

Authentication and Student Profile work used separate implementation areas while the integration task connected the completed components.

Evidence collection covered frontend behaviour, backend behaviour, database behaviour, security, validation, persistence, and regression testing.

The final assigned API test set provided coverage for authentication and negative Student Profile cases that were still open in the earlier tracker.

### 8.2 Issues Observed

Formal Sprint 1 closeout happened later than the planned Sprint 1 dates.

The test tracker, test plan, evidence files, and Evidence Index did not stay fully synchronized during execution.

The final 19 MD test cases existed on a later branch and were missing from the Sprint 4 branch used for the first closeout audit.

Evidence IDs `EV-66` through `EV-70` used inconsistent zero-padding in several tracker rows.

`FE-AUTH-04` is recorded as Pass but has no direct Evidence ID in its tracker row.

Some Sprint 1 status text stayed stale after the underlying implementation and testing had already progressed.

### 8.3 Actions Carried Forward

Future sprint closeout work should:

- Reconcile test tracker status before formal closure.
- Keep the Evidence Index synchronized when evidence files are added.
- Use three-digit evidence IDs consistently.
- Confirm testing branches are merged into the active integration baseline.
- Update integration-plan status after dependent work is merged.
- Update backlog status when sprint acceptance work finishes.
- Confirm test ownership before closeout execution.
- Record evidence links at the same time as test results.
- Separate implementation ownership from shared integration and testing ownership.
- Run closeout audits before the next sprint reaches final review.

## 9. WBS 4.10 Review and Retrospective Status

WBS 4.10 is complete through this closeout review and retrospective.

The review uses the final Sprint 1 implementation state, the 61-case tracker, the Sprint 1 test plan, and the reconciled evidence set.

## 10. WBS 4.11 Completion Criteria

Sprint 1 completion is supported by the following verified state:

- Sprint 1 implementation areas are integrated.
- Authentication flow is implemented.
- Student Profile flow is implemented.
- Frontend and backend integration is present.
- PostgreSQL integration is verified.
- Ownership and validation behaviour is tested.
- 61 of 61 planned Sprint 1 test cases are Pass.
- No Sprint 1 test case is Fail.
- No Sprint 1 test case is Blocked.
- No Sprint 1 test case is Not Run.
- Evidence records exist from EV-001 through EV-070.
- WBS 4.10 review and retrospective is documented.

## 11. Sprint 1 Completion Status

WBS 4.9 Sprint 1 unit and API testing: COMPLETE

WBS 4.10 Sprint 1 review and retrospective: COMPLETE

WBS 4.11 Sprint 1 complete: COMPLETE

Sprint 1 - Foundation and Student Profile: COMPLETE

## 12. Closeout References

Primary closeout references:

- `docs/testing/sprint-1-test-plan.md`
- `docs/testing/sprint-1-test-cases.xlsx`
- `docs/testing/evidence/sprint-1/`
- `docs/system-design/sprint-1-integration-plan.md`
- `docs/project-management/work-breakdown-structure.md`
- `docs/project-management/product-backlog.md`
- `backend/docs/AUTH_API_TESTING.md`
