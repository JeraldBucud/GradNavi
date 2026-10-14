# WBS 8.2 Integration Regression Review

Status: In Progress
Owner: Jerald
Sprint: 5
WBS: 8.2 Full Regression Testing
Branch: `jerald/wbs-8.2-integration-regression-review`

## Scope

This record covers Jerald's assigned WBS 8.2 integration and security-critical regression review.

It does not replace the backend/API and database regression assigned to MD or the frontend regression assigned to Joyee.

## Completed Integration Regression

### S4-RESUME-04 Targeted Retest

Result: PASS after fix and retest.

The regression retest verified that Resume generation remains grounded in the authenticated Student Profile.

A temporary local WBS 8.2 Student profile was created from the standard test Student while excluding:

- Docker
- Kubernetes
- Amazon Web Services AWS software

The generated Resume initially exposed an integration issue where unsupported technologies were removed from the Skills section but Docker still appeared in the Professional Summary.

The issue was corrected on child PR #90 and merged into this WBS 8.2 branch.

Final verification confirmed:

- unsupported Docker, Kubernetes, and AWS claims are absent from the Professional Summary
- unsupported Docker, Kubernetes, and AWS entries are absent from the Skills section
- supported Student Profile evidence remains available
- the approved unsupported-skill limitation is displayed
- exported Resume spacing after `:` and around `|` is correct
- Resume section spacing is visually acceptable

Evidence:

- `docs/testing/evidence/sprint-5/wbs-8.2/integration-regression/resume/S5-EV-WBS82-RESUME-01-profile-grounded-resume-pass.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/integration-regression/resume/S5-EV-WBS82-RESUME-02-ats-export-spacing-pass.png`

Implementation reference:

- PR #90
- Merge commit `f67993b`

### S4-JOB-06 Targeted Retest

Result: PASS.

The Job Matching regression verified the Sprint 4 AWS matching correction through the Student UI.

Amazon Web Services input:

- recognised requirement: `Amazon Web Services AWS software`
- profile status: In profile
- recognised term: `Amazon Web Services`
- match type: Canonical match
- recognised requirement count: 1
- no separate generic `web services` requirement appeared

AWS acronym input:

- recognised requirement: `Amazon Web Services AWS software`
- profile status: In profile
- recognised term: `AWS`
- match type: Canonical match
- recognised requirement count: 1
- no separate generic `web services` requirement appeared

Evidence:

- `docs/testing/evidence/sprint-5/wbs-8.2/integration-regression/job-matching/S5-EV-WBS82-JOB-01-amazon-web-services-canonical-match-pass.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/integration-regression/job-matching/S5-EV-WBS82-JOB-02-aws-acronym-canonical-match-pass.png`

## Security-Critical Regression Context

The separate WBS 8.3 local security and permission testing completed with:

- Total: 32
- Pass: 30
- Fail: 0
- Not Run: 0
- Blocked: 0
- Deferred: 2

The two deferred checks are deployment-specific and continue during deployment and production verification.

## Remaining WBS 8.2 Work

The following work stays pending before WBS 8.2 final review:

- MD backend/API and database regression results
- Joyee frontend regression results
- combined review of all WBS 8.2 failures, fixes, retests, and evidence
- final integrated S4-REG-06 smoke regression after the other WBS 8.2 portions are ready

## Current Result

Jerald's targeted Sprint 4 integration regressions are complete.

- S4-RESUME-04: PASS after fix and retest
- S4-JOB-06: PASS
- S4-REG-06: PENDING final combined regression stage

WBS 8.2 remains In Progress until the team regression portions are combined and the final integrated smoke regression is completed.

## Joyee Frontend Regression Evidence

Tester: Joyee Chakraborty
WBS: 8.2 Full Regression Testing
Source: Joyee's Sprint 5 frontend regression evidence submission
Evidence received: 11 October 2026

### Reported Execution

Joyee reported retesting Student and Administrator pages
on desktop and mobile.

Her submission states that the tested pages loaded and
functioned as expected, with no new issues identified
apart from the Administrator Dashboard mobile heading,
which was addressed in PR #95.

The evidence package includes:

- Desktop and mobile landing-page screenshots.
- Student workflow screenshots.
- Administrator Dashboard and audit-page screenshots.
- Frontend lint output.
- Frontend production-build output.

### Evidence Files

- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-admin-dashboard.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-admin-pages.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-build.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-desktop-home.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-lint.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-mobile-admin.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-mobile-home.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-mobile-student.png`
- `docs/testing/evidence/sprint-5/wbs-8.2/frontend-regression/S5-REG-FE-student-smoke.png`

### Verification Boundary

The screenshots support the documented frontend checks.

They do not independently establish that every approved
frontend regression case was executed.

A complete WBS 8.2 sign-off also requires the final
backend/API regression results, database regression,
combined evidence review, and integrated smoke test.

Frontend evidence: Received and organised.
Formal WBS 8.2 completion: Pending final consolidation.

## Latest Sprint 5 Backend Regression

Execution date: 11 October 2026
Executor: Jerald
Branch: jerald/wbs-8.2-integration-regression-review
Environment: Local Django backend, PostgreSQL 17.11
Database: Dedicated local gradnavi_db on port 5433

### Execution Results

| Check | Result |
| --- | --- |
| Django system check | PASS, zero issues |
| Migration file consistency | PASS, no changes detected |
| Initial database migrations | PASS |
| Pending migrations after setup | None |
| Full Django backend test suite | PASS, 1,065 tests |
| Test failures and errors | 0 |
| Test runner exit code | 0 |
| Test database cleanup | Completed |

The full backend regression suite completed in 435.247 seconds.

Two expected AI validation log messages appeared during
execution, but the test runner reported OK.

### Evidence

- `docs/testing/evidence/sprint-5/wbs-8.2/backend-regression/S5-REG-BE-full-suite.log`

### Attribution and Scope

MD previously completed backend regression checks
against an earlier Sprint 5 baseline.

Jerald performed this additional local backend regression
run following subsequent Sprint 5 integration and
deployment changes.

These results verify the checked-out WBS 8.2 branch
against the dedicated local PostgreSQL environment.

They do not establish successful deployed API regression,
Railway staging verification, or final integrated smoke
testing.

Final WBS 8.2 sign-off remains pending.

## Post-Merge Sprint 5 Backend Regression

Execution date: 11 October 2026
Executor: Jerald
Branch: jerald/wbs-8.2-integration-regression-review
Verified commit: b81fa7e
Environment: Local Django backend, PostgreSQL 17.11
Database: Dedicated local gradnavi_db on port 5433

### Baseline Update

Merged origin/feature/sprint-5 into the WBS 8.2
regression branch using merge commit b81fa7e.

The merged baseline includes the profile photo
serving changes from PR #96 and the Administrator
Dashboard mobile heading fix from PR #95.

### Execution Results

| Check | Result |
| --- | --- |
| Django system check | PASS, zero issues |
| Migration consistency | PASS, no changes detected |
| Full backend test suite | PASS, 1,069 tests |
| Failures and errors | 0 |
| Test runner exit code | 0 |
| Test database cleanup | Completed |

Execution duration: 446.061 seconds.

The post-merge run includes four additional passing
tests compared with the earlier 1,065-test baseline.

### Evidence

- `docs/testing/evidence/sprint-5/wbs-8.2/backend-regression/S5-REG-BE-post-merge-full-suite.log`

### Verification Boundary

The local backend regression passed against commit b81fa7e.

Deployed API verification, final integrated smoke testing,
and complete WBS 8.2 sign-off are still pending.

## Sprint 4 smoke historical reconciliation and Sprint 5 sign-off boundary (14 October 2026)

The approved Sprint 4 test plan's final execution record states **S4-REG-06 PASS**, as part of Jerald's 46/46 passing Sprint 4 cases and 129/129 Sprint 4 total. That completed Sprint 4 smoke included Student Job Matching, Resume, Cover Letter, Interview Preparation, and Administrator workflows. The earlier `S4-REG-06: PENDING` in this WBS 8.2 review is a retained historical checkpoint, not the latest Sprint 4 result.

The later **Sprint 5 final combined smoke and team WBS 8.2 sign-off** remain separate requirements. The recorded post-merge backend full suite (1,069 PASS, commit `b81fa7e`), Joyee's frontend checks, targeted integration retests, reported UAT (11/11 PASS) and reported production verification (21/21 PASS) support the review, but those records do not by themselves document a newly executed final Sprint 5 integrated smoke or a signed team consolidation. Do not rerun the already completed Sprint 4 S4-REG-06 merely to correct this record.

Before claiming WBS 8.2 formally complete, identify an existing Sprint 5 integrated smoke execution record that maps to the approved workflows, or execute and document one, then obtain the team's consolidated review. No additional execution is claimed by this documentary reconciliation.
