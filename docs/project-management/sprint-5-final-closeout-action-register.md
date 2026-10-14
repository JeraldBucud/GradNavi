# GradNavi Sprint 5 Formal Closeout: Outstanding Action Register

Status: **Sprint 5 Version 1 verbally accepted by all three team members, per project-lead report recorded 14 October 2026.** This register now tracks documentary and maintenance follow-ups. Written team signatures were not independently supplied.
Evidence review: 14 October 2026. Repository base: main at `47bac47c9896a5a71afcabe863bd7f110c83126e`.
Working branch: `jerald/sprint-5-final-acceptance-closeout`.

This record identifies the remaining work without overriding historical sprint statuses, implementation ownership or earlier PASS reports. The approved WBS, security matrix, and Sprint 5 closeout record govern final decisions.

| WBS / requirement | Current recorded position | Remaining evidence or decision | Owner / review |
| --- | --- | --- | --- |
| 8.1 Sprint planning | Final evidence reconciliation appended to the plan | Preserve historical checkpoints; confirm final review | All members |
| 8.2 Regression | Backend 1,069 tests OK at `b81fa7e`; frontend and targeted evidence filed | Combined integration/API/database/frontend evidence review, final integrated smoke and sign-off | All members; Jerald coordinates |
| 8.3 Security | 30 local PASS plus two project-lead-reported deployment PASS | Six production PNG screenshots uploaded in commit `070bbb8`; reconcile case-level method/result into official security workbook and review unverified production settings, retaining reported-versus-observed limitations | Jerald; deployment configuration owner where needed |
| 8.4 Performance/usability | Evidence images retained | Extract measured results and acceptance statement; distinguish measured versus untested targets | Assigned owner and team review |
| 8.5 Defects/refinement | Fix PRs and production observations documented; team verbally accepted V1 release with documented exceptions | OBS-S5-001 Last Login display accepted as unresolved release limitation; OBS-S5-002 learning-resource report accepted as still-open operational item, requiring owner action. Staging 5.54 versus 6% wording discrepancy remains observational | Assigned owners; future maintenance |
| 8.6 UAT | **Primary 12/12 PASS reported**, new workbook, 10 screenshots and case index verified in `66d7e2f`; original 11/11 retained as historical. Verbal delivery acceptance reported for all three members | Case-executor sign-offs and timestamps still not independently provided; maintain evidence limitations and operational issue follow-ups | All members |
| 8.7 Backend deployment | Railway production operational, PR #93 | Confirm approved deployment/handover evidence and open configuration items | Assigned owner |
| 8.8 Frontend deployment | Vercel production operational, PR #92 | Confirm final deployment and production-path records | Assigned owner |
| 8.9 Production verification | 21/21 reported PASS and screenshots | Approve actual evidence scope; do not overclaim persistence/export verification | Jerald and team |
| 8.10 Technical handover | Technical documents exist | Owner-approved configuration, migrations/reference-data, backup/restore and operational handover | Assigned owner |
| 8.11 User Guide | Final-named user guide committed | Version/content review, link in README and acceptance | Assigned owner |
| 8.12 Final report and GitHub review | Final academic report remains outside public repository | Academic submission, final repository/evidence review and delivery record | Jerald |
| 8.13 Project delivery complete | **Team-reported verbal acceptance of delivered V1 recorded 14 October 2026** | Complete outstanding administrative evidence reconciliation and external academic submission record separately; no independent written signatures | All members |
| 8.14–8.15 Presentation | Presentation delivered 12 October 2026, reported by project lead | Preserve available slides/acknowledgement if desired; do not invent assessor confirmation | All members |
| FR-13 / FR-15 / FR-16 | Features evidenced; traceability or WBS alignment incomplete | Confirm authoritative mapping and acceptance without rewriting history | All members |
| FR-17 | Excluded from Version 1, verbal approval by Jerald, Joyee and MD reported on 14 October 2026 | Preserve original Must priority and exclusion traceability. No implementation, UAT PASS or separate member signatures are claimed | All members |

## Current production-security evidence scope

The project lead supplied masked Railway variable names, HTTPS 401 controlled-authentication response, approved- and unapproved-origin CORS results, Vercel public API base URL, and authenticated production HTTPS 200 browser headers. All six PNG screenshots have been committed to GitHub in commit `070bbb8`. The evidence index is at `docs/testing/evidence/sprint-5/deployment-security/README.md`.

This supports observable DEP-01/02 subchecks. Production DEBUG, allowed-host values, complete secret-exposure review and all deployment criteria are **not** independently verified from the supplied screenshots. The original 30 local PASS and two later reported deployment PASS statuses are retained.

## Accepted delivery decision and remaining administrative work

**Acceptance recorded 14 October 2026:** The project lead reports that Jerald, Joyee and MD verbally approved the final delivered Version 1 release during a telephone discussion. The exact telephone date and individual written sign-offs were not provided. Team approval includes the FR-17 V1 exclusion and acceptance for release of documented low-priority observations without marking them resolved.

**Status:** WBS 8.13 V1 delivery was verbally accepted according to the project lead. This acceptance is not independently authenticated written approval, proof of every test substep, or evidence that the external academic report was submitted.

Open follow-ups continue under their assigned owners:
1. Reconcile remaining requirement-to-WBS mappings, notably FR-13, FR-15 and FR-16.
2. Finish review and cross-links for technical handover and User Guide, and independently unchecked security settings.
3. Capture the missing case-executor dates and any individual written attestations if the team needs them for audit.
4. Keep OBS-S5-001 and OBS-S5-002 open for maintenance, and confirm whether the staging AI text discrepancy is reproducible.
5. Record the separate final academic report submission outcome outside the public repository.

Do not retroactively mark unperformed tests PASS or overwrite the historical Sprint 5 schedule dates.
