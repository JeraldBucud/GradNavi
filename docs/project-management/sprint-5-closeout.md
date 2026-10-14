# GradNavi Sprint 5 Closeout and Project Acceptance Record

- **Document status:** Final closeout draft, pending evidence reconciliation and formal team approval
- **Project:** GradNavi, AI-Powered Career Guidance System
- **Sprint:** Sprint 5, Stabilisation, Deployment and Closure
- **WBS:** 8.1 to 8.15
- **Planned Sprint:** 5 to 9 October 2026
- **Presentation date in approved schedule:** 12 October 2026
- **Actual final presentation (project-lead confirmation):** Delivered on 12 October 2026 at CQU Brisbane and CQU Melbourne
- **Evidence reconciliation date:** 13 October 2026
- **Project schedule:** The project lead reports 100% completion in the revised `GradNavi_Final_Project_Plan.mpp`. This is a schedule-progress statement, distinct from formal acceptance of each deliverable.
- **Release baseline:** `main`, incorporating Sprint 5 PR #101 and README PR #102, prior to this closeout branch
- **Closeout branch:** `jerald/sprint-5-final-acceptance-closeout`
- **Closeout evidence commits (local):** `a33605d`, `0545f25`

## 1. Purpose

This document reconciles Sprint 5 implementation, verification, deployment, documentation and project-delivery evidence. It distinguishes evidence available, testing reported by the team, and approvals not yet independently recorded. Earlier Sprint 5 planning snapshots are preserved as historical checkpoints; this document must not retroactively portray work finished after 9 October as completed on the original planned date.

A repository merge, passing automated tests or a 100% Microsoft Project schedule indicator alone does not establish formal product acceptance. Final closeout requires a recorded disposition for each required deliverable, each accepted limitation, and the team acceptance decision.

## 2. Project and Release Outcome

GradNavi was released to the `main` branch through [PR #101](https://github.com/JeraldBucud/GradNavi/pull/101). [PR #102](https://github.com/JeraldBucud/GradNavi/pull/102) subsequently updated the README. The project lead reported that the deployed frontend at `https://gradnavi.site` and the Railway backend were operational and tested on 13 October 2026.

The evidence provided covers:

- Public landing and login pages.
- Student registration/authentication interface, profile evidence, career recommendations, explore careers, readiness, skill gaps, learning resources, roadmap and dashboard.
- Job matching, editable Resume Builder and Cover Letter Builder, PDF exports, interview questions and feedback.
- Account settings and administrator dashboard, user management, careers, skills, learning resources, resource reports and audit records.
- Production user interaction and UAT results as reported by the project lead.

These statements describe the reported and documented project outcome. They do not assert independent production availability monitoring or independently observed individual UAT sessions.

## 3. Sprint 5 WBS Reconciliation

The following status is **evidence-based closeout status**, not an overwrite of the historical Microsoft Project schedule. “Reported PASS” means the project lead confirmed execution; “document update required” means a prior record has not yet been reconciled.

| WBS | Deliverable | Owner in approved WBS | Closeout finding at 13 October 2026 | Evidence / next action |
| --- | --- | --- | --- | --- |
| 8.1 | Sprint 5 planning and defect triage | All Members | Planning record exists; closeout reconciliation required | Update `docs/project-management/sprint-5-plan.md` with post-release status while preserving the 9 October checkpoint |
| 8.2 | Full regression testing | All Members | Regression evidence recorded and merged; final consolidated sign-off not yet evidenced in the current `main` documents | PR #91; `docs/testing/sprint-5-wbs-8.2-integration-regression-review.md`; backend post-merge 1,069/1,069 PASS; reconcile final frontend, database and integrated smoke execution |
| 8.3 | Security and permission testing | Jerald | **32/32 PASS reported** after two Production deployment checks; previous published documentation still records 30 PASS, 2 Deferred | Update approved security execution workbook and matrix for `S5-SEC-DEP-01`, `S5-SEC-DEP-02` with execution method, result and evidence |
| 8.4 | Performance and usability review | Joyee | Six performance/usability evidence images supplied; performance findings and acceptance still need summary | `docs/testing/evidence/sprint-5/wbs-8.4/performance-usability/`; capture actual Lighthouse measurements from images and review outcome before final mark Complete |
| 8.5 | Bug fixing and final refinement | All Members | Fix work integrated and visual evidence supplied; defect disposition reconciliation required | PR #81, resume correction PR #90 and mobile admin heading PR #95; `docs/testing/evidence/sprint-5/wbs-8.5/`; review non-blocking observations |
| 8.6 | User acceptance testing | All Members | **12/12 PASS reported** in selected primary case register; prior 11/11 team-reported register preserved as historical evidence; formal acceptance pending | `docs/testing/evidence/sprint-5/uat/GradNavi_Sprint5_UAT_12_Scenario_Execution_Results.xlsx`; `12-case/` screenshot index |
| 8.7 | Backend and database deployment | MD | Deployment configuration merged; Production reported operational | PR #93; Railway Production configuration and operational verification; record final backend/database operational evidence |
| 8.8 | Frontend deployment | Joyee | Frontend deployment configuration merged; Production reported operational | PR #92; Vercel Production and `docs/testing/evidence/sprint-5/wbs-8.8/` |
| 8.9 | Production verification | Jerald | **21/21 PASS reported** following interaction testing in Production | `docs/testing/evidence/sprint-5/production-verification/` contains workbook and 21 screenshot records |
| 8.10 | Technical documentation finalisation | MD | Technical material exists, but final handover/document acceptance not established in this record | Confirm final MD technical documentation and setup/recovery instructions, then link the approved files |
| 8.11 | User guide finalisation | Joyee | Final-named DOCX supplied and committed locally; review/acceptance needed | `docs/user-guide/GradNavi-User-Guide-final.docx`; link from README after review |
| 8.12 | Final report and GitHub review | Jerald | GitHub review and final assessment report in progress | Final academic report files are kept outside the GitHub release, by the project lead's decision |
| 8.13 | Project delivery complete | All Members | **Formal delivery decision pending** | Requires accepted 8.9, 8.10, 8.11 and 8.12 deliverables and approved outstanding-scope disposition |
| 8.14 | Final presentation preparation | All Members | Preparation reported complete in connection with the delivered 12 October presentation; supporting slides and rehearsal records not reviewed | Retain final slides or preparation evidence, if available |
| 8.15 | Final presentation | All Members | **COMPLETE, project-lead reported**: delivered 12 October 2026 at two CQU campuses | Jerald Christopher Bucud and Joyee Chakraborty presented at CQU Brisbane; Md Enamul Haque presented at CQU Melbourne. Attendance/delivery confirmed by project lead; independent venue evidence not yet provided |

## 3.1 WBS 8.15 Final Presentation Delivery

**Reported result:** COMPLETE. The project lead confirmed that all three team members delivered their allocated final GradNavi presentations on **12 October 2026**, as follows:

| Team member | Presentation venue | Date | Evidence basis |
| --- | --- | --- | --- |
| Jerald Christopher Bucud | CQU Brisbane | 12 October 2026 | Project-lead confirmation |
| Joyee Chakraborty | CQU Brisbane | 12 October 2026 | Project-lead confirmation |
| Md Enamul Haque | CQU Melbourne | 12 October 2026 | Project-lead confirmation |

The two-campus delivery fulfilled the reported final presentation activity. Presentation slides, assessor acknowledgement, photographs or submission records have not been independently reviewed as part of this closeout. The presentation milestone is separate from formal project acceptance under WBS 8.13.

## 4. Testing and Quality Evidence

### 4.1 WBS 8.2 Regression

The published WBS 8.2 regression review records a **post-merge backend suite of 1,069 passing tests, zero failures**, plus Django system and migration checks. The document also contains targeted PASS results for Resume grounding/export and Job Matching, and Joyee's frontend regression evidence. The latest published review still says that deployed API verification and final integrated smoke sign-off were pending. Reconcile this historical status with later testing only where actual results exist.

- [Regression review](https://github.com/JeraldBucud/GradNavi/blob/main/docs/testing/sprint-5-wbs-8.2-integration-regression-review.md)
- [Sprint 5 integration and regression PR #91](https://github.com/JeraldBucud/GradNavi/pull/91)

**14 October 2026 cross-reference:** WBS 8.2 now maps the reported 21/21 WBS 8.9 Production verification screenshots (`S5-PROD-EV-001`–`021`) to the relevant Student, application and Administrator feature groups. This reuses existing evidence for final integrated smoke coverage review; it does not assert a newly run Sprint 5 smoke test. Explicit combined review and formal sign-off remain pending.

### 4.2 WBS 8.3 Security and Permissions

The published matrix records **30 local PASS and two Deferred** deployment cases. The project lead subsequently confirmed both deferred deployment cases as PASS during Production testing. The final reported total is therefore **32 PASS / 32 planned**. This later result must be entered into the official workbook and execution matrix, with evidence of:

- `S5-SEC-DEP-01`: Production debug/hosts/CORS/HTTPS/secrets/controlled errors.
- `S5-SEC-DEP-02`: No exposed frontend/backend secrets and approved production communication paths.

Do not treat the Production screenshots alone as proof of secret, header, debug or configuration checks. Record how those checks were performed.

- [Published security execution matrix](https://github.com/JeraldBucud/GradNavi/blob/main/docs/testing/sprint-5-security-permission-execution-matrix.md)
- [Published security test plan](https://github.com/JeraldBucud/GradNavi/blob/main/docs/testing/sprint-5-security-permission-test-plan.md)

### 4.2.1 Production screenshot reconciliation preparation (14 October 2026)

After the 13 October project-lead-reported DEP-01/02 PASS follow-up, additional screenshots were supplied showing masked Railway variable names, safe HTTPS HTTP 401 error response, approved/disallowed CORS examples, Vercel's public HTTPS Railway API URL, and an authenticated browser HTTPS HTTP 200 response.

- Evidence index: [Sprint 5 deployment-security evidence](../testing/evidence/sprint-5/deployment-security/README.md).
- Detailed observation boundaries: [security execution matrix, Section 22](../testing/sprint-5-security-permission-execution-matrix.md).
- **Image upload verified:** all six sanitised deployment-security screenshots are committed in closeout-branch commit `070bbb8`. Official case-level workbook reconciliation and complete configuration verification remain pending.
- These screenshots support specified observable checks, **not** full verification of the masked DEBUG/host/secret settings or a complete production secret-exposure scan.
- Retain original 30 local PASS plus two later project-lead-reported PASS totals. Do not convert the two reported results to independently witnessed cases merely because the screenshots were supplied.
- Official workbook case-level evidence reconciliation and formal Sprint 5 sign-off remain pending.

For all outstanding closeout tasks, see the [Sprint 5 formal closeout action register](sprint-5-final-closeout-action-register.md).



### 4.3 WBS 8.6 Internal Team UAT

**Primary twelve-case UAT register (14 October 2026):** The project lead selected the twelve-scenario Student/Administrator checklist for the Sprint 5 closeout narrative. GitHub contains its [Excel execution register](../testing/evidence/sprint-5/uat/GradNavi_Sprint5_UAT_12_Scenario_Execution_Results.xlsx) and [evidence index](../testing/evidence/sprint-5/uat/12-case/evidence-index.csv), plus ten extracted screenshots in `12-case/`, verified on closeout branch at commit `66d7e2f`. All twelve cases are **PASS as reported**, not independently witnessed. The workbook maps steps, expected/actual outcomes, case notes, issue dispositions and screenshot limits; tester names, individual execution dates and formal written acceptance are not supplied for these twelve cases. The earlier eleven-case plan and workbook remain as **historical supporting records**; do not add the two overlapping totals. Final group case-level review and sign-off remain pending.


**Historical eleven-case record:** The project lead confirmed that Jerald Christopher Bucud, Joyee Chakraborty and Md Enamul Haque personally executed their allocated scenarios, with **no blocking issues reported**. That earlier case register records **11 scenarios, 11 team-reported PASS results** and references to the original Production screenshots plus additional UAT screenshots. Screenshots originally captured by one user are reused as product-state evidence, not attributed as a separate tester's capture.

| Tester | Scenarios | Reported outcome |
| --- | --- | --- |
| Jerald Christopher Bucud | S5-UAT-01 to S5-UAT-04 | 4/4 PASS reported |
| Joyee Chakraborty | S5-UAT-05, S5-UAT-07, S5-UAT-08, S5-UAT-09 | 4/4 PASS reported |
| Md Enamul Haque | S5-UAT-06, S5-UAT-10, S5-UAT-11 | 3/3 PASS reported |

**Historical eleven-case UAT records (retained for traceability):**

- `docs/testing/evidence/sprint-5/uat/GradNavi_Sprint5_UAT_Execution_Results.xlsx`
- `docs/testing/evidence/sprint-5/uat/GradNavi_Sprint5_UAT_Test_Plan.md`
- `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-001-Student-Profile-Saved.png` through `S5-UAT-EV-010-Admin-Edit-Learning-Resource-Form.png`
- Reused Production evidence `S5-PROD-EV-001` through `S5-PROD-EV-021`, kept in their original Production verification folder

The provided records do not contain independently supplied handwritten or electronic acceptance signatures from each member. Obtain or record each member's acceptance acknowledgement before describing formal individual sign-off as complete.

### 4.4 WBS 8.9 Production Verification

The project lead confirmed that the visible controls and workflows were exercised after completing a populated Student Profile. The production verification workbook records **21/21 PASS reported**. Twenty-one uniquely named screenshots cover public, Student and Administrator screens, and additional UAT screenshots record save, progress, generation, edit and download states.

- `docs/testing/evidence/sprint-5/production-verification/GradNavi_Sprint5_Production_Product_Verification_Test_Cases_Updated.xlsx`
- `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-001-Landing-Page.png` through `S5-PROD-EV-021-Admin-Audit-Records.png`

**Environment:** Vercel frontend at `https://gradnavi.site` with Railway backend and PostgreSQL, as reported during Production rollout.

## 5. Known Observations, Defects and Scope Decisions

The following are *not* counted as blocking UAT failures without a relevant failed approved case. They require truthful documentation and disposition before the final no-open-issues statement.

| Reference | Observation | Evidence status | Required disposition |
| --- | --- | --- | --- |
| OBS-S5-001 | Admin User Management displayed `Never` under Last Login for accounts shown | Visible in `S5-PROD-EV-016`; root cause and retest not established | Confirm whether documented authentication behaviour or a defect, then resolve or accept with rationale |
| OBS-S5-002 | One learning-resource report was open for a purported broken link | Visible in `S5-PROD-EV-020`; report workflow visible | Normal administrator review, verify external URL and record Resolve/Dismiss decision |
| SCOPE-FR-13 | Progress Dashboard implemented but approved WBS assignment mapping remains outdated | Backlog and assignment matrix show schedule-alignment gap | Confirm approved mapping rather than silently editing WBS ownership |
| SCOPE-FR-16 | Editable AI output is evidenced in Resume and Cover Letter Builder | Requirement still in Backlog in published product backlog | Confirm acceptance criteria, approved WBS mapping and status |
| SCOPE-FR-17 | Data deletion was originally classified as Must | Original backlog retains historical Backlog status | Excluded from Version 1 by project-lead decision on 13 October 2026. Not implemented or tested as an accepted Version 1 requirement. Formal written scope approval and requirements updates remain pending |
| SCOPE-FR-15 | Admin Analytics shown in Production | Published assignment mapping provisional | Approve final mapping and acceptance status |

No unresolved Critical or High defect should be asserted without checking the actual defect register and completed execution logs. Similarly, a resource report still marked Open should not be described as resolved.

## 6. Documentation and Release Handover

### 6.1 User Guide

Joyee's final-named User Guide is included as `docs/user-guide/GradNavi-User-Guide-final.docx`. Review screenshots, navigation, setup assumptions, and Administrator scope against Production before recording WBS 8.11 accepted. Add a README documentation link.

### 6.2 Technical Documentation

The repository includes architecture, security design, API and deployment material. The WBS 8.10 owner is MD. Identify and link the approved final technical handover, including environment variables without values, startup/deployment steps, migrations/reference-data imports, database backup/restore and production media persistence. Do not claim these are reviewed if an authoritative final technical handover is not yet identified.

### 6.3 Final Report and GitHub Review

The project lead keeps the final academic report in a local excluded workspace rather than the public GitHub repository. Final academic report submission and GitHub handover are separate deliverables. Record the external assessment-submission outcome in the project closeout without committing private drafts.

### 6.4 Project Schedule

The project lead confirms that the revised Microsoft Project `.mpp` reports **100% completion**. The file is stored at `docs/project-management/GradNavi_Final_Project_Plan.mpp`. The schedule may be final while individual formal acceptance and source-document reconciliation are still being completed; explain any actual-date variance from the planned 9 October Sprint finish.

## 7. Sprint Review and Retrospective

### Confirmed outcomes

- The feature-complete Sprint 4 baseline entered Sprint 5, followed by final regression and deployment configuration.
- Sprint 5 was merged into `main` using PR #101; the README was updated using PR #102.
- The project lead reported successful Production verification and team UAT after deployment.
- All three members delivered the final presentation on 12 October 2026, with Jerald and Joyee at CQU Brisbane and MD at CQU Melbourne, as confirmed by the project lead.
- Production, usability and UAT evidence were organised into the Sprint 5 closeout branch and committed locally.

### Issues requiring a recorded retrospective decision

- Sprint 5 and some completion evidence extended beyond the planned 9 October end date. Record the actual completion sequence rather than changing historical planned dates.
- Published testing and planning documents retain earlier statuses. Reconcile later verified results while retaining prior checkpoints.
- FR-17 Data Deletion was excluded from Version 1 by the project lead on 13 October 2026. Formal written scope approval and requirements traceability updates remain outstanding.
- Production configuration/security verification should have traceable execution evidence, not only a PASS count.
- Reused screenshots are legitimate supporting evidence but should not be represented as independently captured by every UAT participant.

### Improvement actions

1. Complete formal acceptance and requirements traceability before changing the project-delivery milestone to formally Accepted.
2. Use one evidence index linking WBS, requirement, test case, result, responsible tester and retained screenshot/log.
3. Keep production secrets, real user details and credentials out of public Git history. Review current uploaded evidence for privacy before pushing.
4. Preserve historical schedule and issue-state snapshots rather than overwriting retrospective context.

## 8. Delivery and Acceptance Decision

- **Technical release:** Sprint 5 release merged into `main` and Production reported operational.
- **Automated regression:** Latest documented backend full run: 1,069/1,069 PASS.
- **Security testing:** 32/32 PASS reported; deployment results still need reconciliation into official records.
- **Internal UAT:** Primary 12/12 PASS reported in the uploaded case register; the previous 11/11 team-reported register is retained as historical supporting evidence; individual formal acceptance remains pending.
- **Production verification:** 21/21 PASS reported; screenshot/workbook evidence retained.
- **Schedule:** 100% complete, according to the project lead's updated `.mpp`.
- **Final presentation (WBS 8.15):** Complete, delivered 12 October 2026 at CQU Brisbane and CQU Melbourne, per project-lead confirmation.
**Formal project acceptance:** **Pending final documentation review, scope disposition and member acceptance acknowledgements.**

The final acceptance decision must consider the definition of done and release conditions in `docs/project-management/quality-plan.md`, including documentation, security, required scope and team review.

### Acceptance acknowledgements (complete using actual confirmations)

| Member | Role | UAT reported | Final delivery acceptance | Confirmation reference/date |
| --- | --- | --- | --- | --- |
| Jerald Christopher Bucud | Project lead | 4/4 PASS reported | Awaiting explicit formal acknowledgement | To be recorded |
| Joyee Chakraborty | Team member | 4/4 PASS reported | Awaiting explicit formal acknowledgement | To be recorded |
| Md Enamul Haque | Team member | 3/3 PASS reported | Awaiting explicit formal acknowledgement | To be recorded |

### Final gate checklist

- [x] Sprint 5 feature release merged into `main`.
- [x] Reported UAT PASS results entered into detailed UAT workbook.
- [x] Reported Production verification PASS results entered into Production workbook.
- [x] Production and UAT screenshots retained and named consistently.
- [x] User Guide DOCX supplied to closeout branch.
- [x] Revised Microsoft Project plan supplied; project lead reports 100% schedule completion.
- [ ] Reconcile the two deployment-security PASS results into the official security test records.
- [ ] Reconcile latest full regression and integrated smoke acceptance in the formal WBS 8.2 review.
- [ ] Confirm WBS 8.4 performance/usability final acceptance and WBS 8.5 defect dispositions.
- [ ] Confirm WBS 8.10 final technical documentation is approved.
- [ ] Confirm WBS 8.11 User Guide review and acceptance.
- [ ] Confirm WBS 8.12 final report/GitHub review acceptance, without committing private academic drafts.
- [x] Record project-lead decision to exclude FR-17 Data Deletion from Version 1.
- [ ] Obtain formal written scope approval and reconcile FR-17 in the Product Backlog, Functional Requirements and Requirements Assignment Matrix.
- [ ] Complete remaining requirement-to-WBS mapping and acceptance review.
- [ ] Record final disposition of the Last Login observation and open resource report.
- [ ] Obtain actual formal delivery acceptance acknowledgement from the three members.
- [x] WBS 8.15 final presentation delivered on 12 October 2026 at CQU Brisbane and CQU Melbourne, confirmed by the project lead.
- [ ] File final presentation materials or independent delivery acknowledgement if required for WBS 8.14 evidence.
- [ ] Confirm WBS 8.13 Project Delivery Complete after predecessor acceptance.

**Proposed closeout status:** Ready for final evidence reconciliation and formal team decision. Do not present as fully signed off until the remaining gate items are addressed.

## 9. Source and Evidence Index

### Local closeout files (committed on `jerald/sprint-5-final-acceptance-closeout`)

- `docs/project-management/GradNavi_Final_Project_Plan.mpp`
- `docs/user-guide/GradNavi-User-Guide-final.docx`
- `docs/testing/evidence/sprint-5/production-verification/GradNavi_Sprint5_Production_Product_Verification_Test_Cases_Updated.xlsx`
- `docs/testing/evidence/sprint-5/production-verification/` (21 PNG screenshots)
- `docs/testing/evidence/sprint-5/uat/GradNavi_Sprint5_UAT_Execution_Results.xlsx`
- `docs/testing/evidence/sprint-5/uat/GradNavi_Sprint5_UAT_Test_Plan.md`
- `docs/testing/evidence/sprint-5/uat/` (10 PNG screenshots)
- `docs/testing/evidence/sprint-5/wbs-8.4/`
- `docs/testing/evidence/sprint-5/wbs-8.5/`
- `docs/testing/evidence/sprint-5/wbs-8.8/`

### Repository source documents and merged work

- [Sprint 5 plan](https://github.com/JeraldBucud/GradNavi/blob/main/docs/project-management/sprint-5-plan.md)
- [Work breakdown structure](https://github.com/JeraldBucud/GradNavi/blob/main/docs/project-management/work-breakdown-structure.md)
- [Product backlog](https://github.com/JeraldBucud/GradNavi/blob/main/docs/project-management/product-backlog.md)
- [Requirements assignment matrix](https://github.com/JeraldBucud/GradNavi/blob/main/docs/requirements/requirements-assignment-matrix.md)
- [Quality plan](https://github.com/JeraldBucud/GradNavi/blob/main/docs/project-management/quality-plan.md)
- [Sprint 5 security matrix](https://github.com/JeraldBucud/GradNavi/blob/main/docs/testing/sprint-5-security-permission-execution-matrix.md)
- [Sprint 5 regression review](https://github.com/JeraldBucud/GradNavi/blob/main/docs/testing/sprint-5-wbs-8.2-integration-regression-review.md)
- [PR #101, Sprint 5 to main](https://github.com/JeraldBucud/GradNavi/pull/101)
- [PR #102, README refresh](https://github.com/JeraldBucud/GradNavi/pull/102)
- [PR #91, integration regression](https://github.com/JeraldBucud/GradNavi/pull/91)
- [PR #92, frontend deployment configuration](https://github.com/JeraldBucud/GradNavi/pull/92)
- [PR #93, backend deployment configuration](https://github.com/JeraldBucud/GradNavi/pull/93)

**Change control:** Update this document when new evidence or written acceptance decisions arrive. Do not replace a Pending value with Complete solely to match a schedule percentage.
