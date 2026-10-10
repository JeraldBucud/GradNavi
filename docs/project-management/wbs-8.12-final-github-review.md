# WBS 8.12 Final Report and GitHub Review

Status: In Progress

Owner: Jerald Christopher Yalung Bucud

Branch: `jerald/wbs-8.12-final-report-github-review`

Audit baseline: `feature/sprint-5` at `c58076b`

Audit date: 11 October 2026

## 1. Purpose

This record captures the WBS 8.12 repository, documentation, testing, contribution, requirement, deployment, and release-readiness review.

WBS 8.12 starts before every Sprint 5 dependency is complete. Items that still depend on WBS 8.2, WBS 8.4, WBS 8.6, WBS 8.7, WBS 8.8, WBS 8.9, WBS 8.10, or WBS 8.11 stay Pending until evidence is available.

This review does not mark an unfinished task complete and does not change approved Microsoft Project ownership.

## 2. Sprint Completion Baseline

| Sprint | Verified repository state | Test result | Closure state |
| --- | --- | --- | --- |
| Sprint 1 | Formal closeout exists | 61 Pass, 0 Fail, 0 Blocked, 0 Not Run | Complete |
| Sprint 2 | Test plan records all planned cases executed | 80 Pass, 0 Fail, 0 Blocked, 0 Not Run | Testing complete, formal closeout record not found |
| Sprint 3 | Formal closeout exists | 100 Pass, 0 Fail, 0 Blocked, 0 Not Run | Complete |
| Sprint 4 | Formal closeout exists | 129 Pass, 0 Fail, 0 Blocked, 0 Not Run | Complete and Feature Complete reached |
| Sprint 5 | Finalisation in progress | Final regression and production evidence still pending | In Progress |

Sprint 2 requires documentation reconciliation. The repository proves that all 80 planned Sprint 2 tests passed. A dedicated `sprint-2-closeout.md` file was not identified during this audit.

## 3. Current Sprint 5 Pull Request Review

The following PRs were open during the WBS 8.12 audit:

| PR | WBS | Current review state | Baseline relationship | WBS 8.12 treatment |
| --- | --- | --- | --- | --- |
| #91 | 8.2 Full Regression Testing | Draft | 4 commits ahead, 0 behind | In Progress |
| #92 | 8.8 Frontend Deployment | Draft | 2 commits ahead, 0 behind | In Progress |
| #93 | 8.7 Backend and Database Deployment | Open | 3 commits ahead, 0 behind | In Progress, deployment verification required |
| #94 | 8.4 Performance and Usability Review | Draft | 1 commit ahead, 0 behind | In Progress, final review evidence required |
| #95 | 8.5 Bug Fixing and Final Refinement | Open | 1 commit ahead, 0 behind | In Progress |

All five branches were aligned with `feature/sprint-5` at the audit checkpoint and were not behind the baseline.

## 4. WBS 8.2 Review

PR #91 records Jerald's targeted integration regression work.

Verified checkpoint results:

- S4-RESUME-04: Pass after fix and retest.
- S4-JOB-06: Pass.
- Resume grounding issue corrected through PR #90.
- ATS export spacing correction verified.
- AWS and Amazon Web Services canonical matching verified.
- WBS 8.3 local security context recorded as 30 Pass, 0 Fail, 0 Blocked, and 2 deployment-deferred checks.

Pending before WBS 8.2 completion:

- Remaining team regression results.
- Combined regression review.
- Final integrated S4-REG-06 smoke regression.
- Final WBS 8.2 status update.

## 5. WBS 8.3 Review

The local security and permission scope is complete.

Final local result:

- Total cases: 32.
- Pass: 30.
- Fail: 0.
- Not Run: 0.
- Blocked: 0.
- Deferred to deployment: 2.

The deferred deployment checks continue through WBS 8.7 to WBS 8.9.

## 6. WBS 8.4 and WBS 8.5 Review

PR #94 records the landing and authentication image optimisation.

Verified repository changes:

- Eight unique PNG assets were replaced by WebP assets.
- The shared hero asset is used by both the homepage and authentication layout.
- Vercel preview status is successful.
- PR description reports Lighthouse desktop homepage Performance improving from 75 to 96.
- PR description reports Largest Contentful Paint improving from 8.5 seconds to 1.2 seconds.
- PR description reports lint with 0 errors and 0 warnings and a passing production build.

The Lighthouse, lint, and build figures are reported in the PR description. A committed Lighthouse report or WBS 8.4 review record was not present at the audit checkpoint.

PR #95 records the confirmed Admin Dashboard mobile section-heading usability correction identified during the WBS 8.4 review.

## 7. WBS 8.7 and WBS 8.8 Deployment Review

PR #93 contains the backend deployment configuration for Railway and PostgreSQL.

Verified repository-level changes include:

- Gunicorn dependency.
- Environment-driven DEBUG configuration with a production-safe False fallback.
- Environment-driven allowed hosts.
- Environment-driven CORS and CSRF origins.
- Secure cookie behaviour when DEBUG is False.
- Proxy HTTPS header support.
- STATIC_ROOT.
- Deployment environment documentation.

GitHub reports successful Vercel and Railway checks for the PR #93 head commit.

Final WBS 8.7 completion still requires the deployment evidence agreed by the team, including the staging backend response and database/migration verification.

PR #92 contains frontend deployment preparation for Vercel.

Verified repository-level changes include:

- `VITE_API_BASE_URL` configuration.
- Vercel SPA routing through `vercel.json`.
- Frontend environment example.

The PR #92 Vercel Preview is configured for staging integration testing. Full-flow verification remains pending at this checkpoint.

## 8. README Review

The pre-WBS 8.12 README contains stale Sprint 3 status statements.

Examples found during audit:

- GradNavi described as currently in Sprint 3 development.
- WBS 7.3 described as future provider integration.
- Sprint 3 testing described as only partly prepared.
- Sprint 3 Review and Retrospective described as not started.
- Sprint 3 Complete described as not reached.

These statements conflict with the formal Sprint 3 and Sprint 4 closeout records.

README requires reconciliation to the current Sprint 5 finalisation state.

## 9. Requirements Review

The functional and non-functional requirement files still use the formal label `Draft for approval`.

WBS 8.12 does not silently change those approval labels.

Implementation state and formal approval state must stay separate.

The following mapping issues remain documented:

### FR-13 Progress Dashboard

Implementation evidence exists through merged PR #75.

The requirements assignment matrix still lacks a formally approved Microsoft Project WBS mapping for FR-13.

Result: implementation present, planning mapping requires reconciliation.

### FR-15 Admin Analytics

Implementation evidence is associated with WBS 7.6 and WBS 7.7.

The requirements assignment matrix still labels the mapping provisional.

Result: implementation present, mapping confirmation remains required.

### FR-16 AI Content Review

Editable and reviewable generated-content behaviour exists across the Sprint 3 document interfaces and AI service contracts.

The requirements assignment matrix still lacks a dedicated approved WBS mapping.

Result: implementation behaviour present, planning mapping requires reconciliation.

### FR-17 Data Deletion

The audit did not identify a verified Student-facing implementation that satisfies both deletion of saved generated documents and profile-deletion request behaviour.

Result: do not mark FR-17 complete without implementation and acceptance evidence.

## 10. Product Backlog Review

The product backlog contains stale execution statuses for work already verified by later Sprint closeout records.

Reconciliation required:

- Sprint 2 requirements should reflect the 80 of 80 passing test baseline.
- Sprint 3 requirements should reflect the 100 of 100 passing closeout baseline.
- Sprint 4 requirements should reflect the 129 of 129 passing Feature Complete baseline.
- FR-13, FR-15, and FR-16 should remain under mapping review even where implementation evidence exists.
- FR-17 should stay open until verified implementation and acceptance evidence exists.

## 11. Contribution Evidence Review

The contribution log is incomplete for the late project period.

The original record contains a limited subset of Sprint 2 and WBS 5.6 work.

WBS 8.12 adds a reconciliation snapshot covering later verified work while preserving GitHub as the detailed source of commit and PR history.

Open Sprint 5 work must not be labelled Complete until the related PR and WBS close.

## 12. Meeting Evidence Review

Repository meeting folders were identified for Sprint 1, Sprint 2, and Sprint 3.

No Sprint 4 or Sprint 5 meeting folder was identified under `docs/meetings` during this audit.

This does not prove that later meetings did not occur. It records only the repository evidence found.

If later meeting evidence exists outside the repository, the team should decide whether it belongs in the final delivery evidence.

## 13. Release Condition Review

The Quality Plan requires:

- Priority Student and Administrator flows pass.
- No Critical release defect remains open.
- Authentication, permissions, privacy, and secret-management checks pass.
- Scoring repeatability checks pass.
- AI validation and fallback checks pass.
- Data sources and limitations are recorded.
- Major usability barriers are corrected.
- Deployment smoke tests pass.
- Recovery and fallback instructions are available.
- Report, setup, testing, contribution, and presentation evidence is complete.

Current position:

| Release condition | WBS 8.12 audit state |
| --- | --- |
| Sprint 1 to Sprint 4 functional baseline | Verified |
| Local security and permission testing | Verified |
| Sprint 5 final regression | Pending |
| Performance and usability closeout | Pending final WBS 8.4 record and PR disposition |
| UAT | Pending |
| Backend deployment | Pending final WBS 8.7 evidence and PR disposition |
| Frontend deployment | Pending full staging flow and PR disposition |
| Production verification | Pending |
| Technical documentation | Pending WBS 8.10 |
| User guide | Pending WBS 8.11 |
| Contribution reconciliation | In Progress under WBS 8.12 |
| Final GitHub review | In Progress under WBS 8.12 |
| Presentation evidence | Pending final preparation |

## 14. GitHub Review Findings

At the audit checkpoint:

- Open WBS 8.x PRs are based on the current Sprint 5 baseline.
- No audited open WBS 8.x branch is behind `feature/sprint-5`.
- PR #91 and PR #92 are intentionally Draft.
- PR #93, PR #94, and PR #95 still require final WBS-specific disposition before project delivery.
- WBS 8.12 must be updated again after the final Sprint 5 merges.
- Final delivery should not leave unexplained project-delivery PRs open.

## 15. Documentation Reconciliation Completed in This Checkpoint

The following documentation updates were applied on the WBS 8.12 branch:

- `README.md`: removed stale Sprint 3 current-state text and replaced it with the verified Sprint 5 finalisation baseline.
- `docs/project-management/sprint-5-plan.md`: updated WBS 8.2 to WBS 8.15 execution state, current Sprint 5 audit, planning decisions, and immediate actions.
- `docs/project-management/product-backlog.md`: reconciled completed Sprint 2, Sprint 3, and Sprint 4 requirement statuses while keeping unresolved requirement mappings under Review or Backlog.
- `docs/project-management/contribution-log.md`: added a verified late-project contribution reconciliation snapshot.
- `docs/project-management/roadmap-and-milestones.md`: replaced stale current-Sprint text with Sprint 5 finalisation and reconciled the Sprint 2 execution state.
- `docs/requirements/functional-requirements.md`: added implementation reconciliation while preserving formal approval labels.
- `docs/requirements/non-functional-requirements.md`: added evidence reconciliation while preserving formal approval labels.
- `docs/requirements/requirements-assignment-matrix.md`: updated the FR-13, FR-15, FR-16, and FR-17 reconciliation findings without changing the Microsoft Project source-of-truth rule.
- `docs/project-management/wbs-8.12-final-github-review.md`: added this WBS 8.12 audit and closeout checklist.

No application code was changed by this WBS 8.12 documentation checkpoint.

## 16. Items That Must Stay Pending

Do not close WBS 8.12 until final evidence is available for the project-delivery state.

Pending dependencies include:

- WBS 8.2 Full Regression Testing.
- WBS 8.4 Performance and Usability Review.
- WBS 8.6 User Acceptance Testing.
- WBS 8.7 Backend and Database Deployment.
- WBS 8.8 Frontend Deployment.
- WBS 8.9 Production Verification.
- WBS 8.10 Technical Documentation Finalisation.
- WBS 8.11 User Guide Finalisation.

## 17. Current WBS 8.12 Result

WBS 8.12 status: In Progress.

Completed in this checkpoint:

- Repository audit.
- Sprint closeout reconciliation review.
- Open Sprint 5 PR review.
- README reconciliation.
- Sprint 5 planning-status reconciliation.
- Product backlog execution-status reconciliation.
- Late-project contribution reconciliation.
- Functional and non-functional requirement evidence interpretation.
- FR-13, FR-15, FR-16, and FR-17 mapping review.
- Roadmap current-phase reconciliation.
- Release-condition review.

The branch remains documentation-only at this checkpoint.

Final WBS 8.12 closeout remains pending the final Sprint 5 regression, UAT, deployment, production verification, technical documentation, user guide, final PR dispositions, and project-delivery evidence.
