# GradNavi Sprint 5 Formal Closeout: Outstanding Action Register

Status: Preparation only. **Formal Sprint 5 closeout and project acceptance are not approved.**
Evidence review: 14 October 2026. Repository base: main at `47bac47c9896a5a71afcabe863bd7f110c83126e`.
Working branch: `jerald/sprint-5-final-acceptance-closeout`.

This record identifies the remaining work without overriding historical sprint statuses, implementation ownership or earlier PASS reports. The approved WBS, security matrix, and Sprint 5 closeout record govern final decisions.

| WBS / requirement | Current recorded position | Remaining evidence or decision | Owner / review |
| --- | --- | --- | --- |
| 8.1 Sprint planning | Final evidence reconciliation appended to the plan | Preserve historical checkpoints; confirm final review | All members |
| 8.2 Regression | Backend 1,069 tests OK at `b81fa7e`; frontend and targeted evidence filed | Combined integration/API/database/frontend evidence review, final integrated smoke and sign-off | All members; Jerald coordinates |
| 8.3 Security | 30 local PASS plus two project-lead-reported deployment PASS | Six production PNG screenshots uploaded in commit `070bbb8`; reconcile case-level method/result into official security workbook and review unverified production settings, retaining reported-versus-observed limitations | Jerald; deployment configuration owner where needed |
| 8.4 Performance/usability | Evidence images retained | Extract measured results and acceptance statement; distinguish measured versus untested targets | Assigned owner and team review |
| 8.5 Defects/refinement | Fix PRs and production observations documented | Confirm disposition/retests for OBS-S5-001 Last Login and OBS-S5-002 learning-resource report | Assigned owners; team review |
| 8.6 UAT | **Primary 12/12 PASS reported**, new workbook, 10 screenshots and case evidence index verified in closeout branch `66d7e2f`; original 11/11 retained as historical | Review 12-case expected/actual steps and evidence limits, reconcile reported issues, collect actual member acceptance and dates | All members |
| 8.7 Backend deployment | Railway production operational, PR #93 | Confirm approved deployment/handover evidence and open configuration items | Assigned owner |
| 8.8 Frontend deployment | Vercel production operational, PR #92 | Confirm final deployment and production-path records | Assigned owner |
| 8.9 Production verification | 21/21 reported PASS and screenshots | Approve actual evidence scope; do not overclaim persistence/export verification | Jerald and team |
| 8.10 Technical handover | Technical documents exist | Owner-approved configuration, migrations/reference-data, backup/restore and operational handover | Assigned owner |
| 8.11 User Guide | Final-named user guide committed | Version/content review, link in README and acceptance | Assigned owner |
| 8.12 Final report and GitHub review | Final academic report remains outside public repository | Academic submission, final repository/evidence review and delivery record | Jerald |
| 8.13 Project delivery complete | **Pending** | Actual group approval after dependent deliverables, scope and limitation decisions | All members |
| 8.14–8.15 Presentation | Presentation delivered 12 October 2026, reported by project lead | Preserve available slides/acknowledgement if desired; do not invent assessor confirmation | All members |
| FR-13 / FR-15 / FR-16 | Features evidenced; traceability or WBS alignment incomplete | Confirm authoritative mapping and acceptance without rewriting history | All members |
| FR-17 | Excluded from Version 1 by project-lead decision | Written group scope approval; retain original Must priority and exclusion traceability | All members |

## Current production-security evidence scope

The project lead supplied masked Railway variable names, HTTPS 401 controlled-authentication response, approved- and unapproved-origin CORS results, Vercel public API base URL, and authenticated production HTTPS 200 browser headers. All six PNG screenshots have been committed to GitHub in commit `070bbb8`. The evidence index is at `docs/testing/evidence/sprint-5/deployment-security/README.md`.

This supports observable DEP-01/02 subchecks. Production DEBUG, allowed-host values, complete secret-exposure review and all deployment criteria are **not** independently verified from the supplied screenshots. The original 30 local PASS and two later reported deployment PASS statuses are retained.

## Closeout decision rule

Before setting this document, Sprint 5, WBS 8.13, or the project as formally Accepted:
1. Verify the required case-level evidence and approved requirements scope.
2. Reconcile outdated plan/closeout statements without deleting historical checkpoints.
3. Record each owner's disposition of documented observations and outstanding requirements.
4. Confirm report, guide and technical handover.
5. Record actual group acceptance and approval dates.

This action register does not itself change any task to Complete.
