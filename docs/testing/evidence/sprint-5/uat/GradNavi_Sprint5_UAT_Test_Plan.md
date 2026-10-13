# GradNavi Sprint 5 User Acceptance Testing Plan and Execution Record

- **WBS:** 8.6 User Acceptance Testing
- **Product:** GradNavi, AI-Powered Career Guidance System
- **Environment:** Production, https://gradnavi.site
- **UAT type:** Internal project-team user acceptance testing
- **Evidence date:** 13 October 2026
- **Execution result:** 11 of 11 scenarios reported PASS by the project lead; no blocking issues reported
- **Formal sign-off:** Individual member sign-off not provided in this record
- **Relationship:** Separate from WBS 8.9 Production Verification

## 1. Purpose and evidence basis

Evaluate whether representative Student and Administrator workflows meet the acceptance tasks in the agreed project scope. The project lead reported that Jerald, Joyee and MD personally completed their allocated internal UAT scenarios with no blocking issues. This plan documents those reported results, supported by screenshots. It does not misrepresent reused screenshots as independently captured by each tester or fabricate individual signatures.

The execution date of each team member was not separately supplied. The screenshots available for this record were captured on 13 October 2026. Case results are **PASS (team-reported)**, rather than independently witnessed execution results.

## 2. Participants and allocation

| Participant | Allocated case IDs | Count | Execution source | Acceptance acknowledgement |
| --- | --- | ---: | --- | --- |
| Jerald Christopher Bucud | S5-UAT-01, S5-UAT-02, S5-UAT-03, S5-UAT-04 | 4 | Project lead confirmed personal execution and no blockers | Individual signed confirmation not supplied |
| Joyee Chakraborty | S5-UAT-05, S5-UAT-07, S5-UAT-08, S5-UAT-09 | 4 | Project lead confirmed personal execution and no blockers | Individual signed confirmation not supplied |
| Md Enamul Haque | S5-UAT-06, S5-UAT-10, S5-UAT-11 | 3 | Project lead confirmed personal execution and no blockers | Individual signed confirmation not supplied |

## 3. Acceptance cases and reported answers

### S5-UAT-01: Sign in and save Student Profile

- **Assigned tester:** Jerald Christopher Bucud (Student)
- **Test steps:** Sign in; edit skills or profile evidence; save profile; inspect saved summary.
- **Expected outcome:** Profile saves without an error and saved selections are visible.
- **Actual result:** Team-reported PASS. Captured success banner says "Profile saved successfully"; Skills saved shows 27 with Data Analyst as primary goal.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-01, FR-02
- **Evidence interpretation:** Visible save success; confirmed selected skills, goals and interests.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-002-Login-Page.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-004-Student-Profile.png`
- **Additional UAT evidence:** `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-001-Student-Profile-Saved.png`
- **Blocking issue:** None reported

### S5-UAT-02: Explore ranked career matches

- **Assigned tester:** Jerald Christopher Bucud (Student)
- **Test steps:** Open recommendations; review top career and explanations; browse Explore Careers.
- **Expected outcome:** Ranked matches, meaningful explanation and career browsing are usable.
- **Actual result:** Team-reported PASS. Screens show Data Analyst ranked first, 92% career match, explanation panel and browsable 36-career catalogue.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-03, FR-04
- **Evidence interpretation:** Screens support displayed ranking and explanation; clicking/navigation confirmed by project lead.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-005-Career-Recommendations.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-006-Explore-Careers.png`
- **Blocking issue:** None reported

### S5-UAT-03: Understand readiness and skill gaps

- **Assigned tester:** Jerald Christopher Bucud (Student)
- **Test steps:** Select primary career; view readiness score, evidence statuses and missing skills.
- **Expected outcome:** User understands readiness score, unmet requirements and priorities.
- **Actual result:** Team-reported PASS. Skill Gap Analysis shows readiness of 68%, matched/partial/missing requirements, and actionable suggestions.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-05, FR-06
- **Evidence interpretation:** Visible deterministic score and categorised skill gap results.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-007-Skill-Gap-Analysis.png`
- **Blocking issue:** None reported

### S5-UAT-04: Follow roadmap and learning suggestions

- **Assigned tester:** Jerald Christopher Bucud (Student)
- **Test steps:** Open roadmap; start or complete a step; inspect progress and linked resources.
- **Expected outcome:** Progress updates and recommended resources are meaningful for selected career.
- **Actual result:** Team-reported PASS. New screenshot shows 1 completed, 1 in progress, 10 to do and Next: Step 02; resource screen shows selected focus and six recommendations.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-11, FR-12
- **Evidence interpretation:** Visible progress change relative to original production screenshot with 0 completed.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-008-Career-Roadmap.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-009-Learning-Resources.png`
- **Additional UAT evidence:** `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-002-Career-Roadmap-Progress.png`
- **Blocking issue:** None reported

### S5-UAT-05: Understand dashboard status and next action

- **Assigned tester:** Joyee Chakraborty (Student)
- **Test steps:** Open Student Dashboard; inspect primary goal, readiness, gaps, recent activity and shortcuts.
- **Expected outcome:** Dashboard summarises the current career and gives clear next steps.
- **Actual result:** Team-reported PASS. Production screenshot shows Data Analyst primary goal, readiness of 68%, next best action, skill gaps and preparation links.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-13
- **Evidence interpretation:** Screenshot is reused product-state evidence, not attributed as Joyee's capture.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-003-Student-Dashboard.png`
- **Blocking issue:** None reported

### S5-UAT-06: Interpret job description matching

- **Assigned tester:** Md Enamul Haque (Student)
- **Test steps:** Paste a job description; analyse; inspect skills already in profile and skills needing review.
- **Expected outcome:** The matched and unmatched job requirements are understandable and actionable.
- **Actual result:** Team-reported PASS. Production screenshot shows 31 recognised requirements, 6 in profile and 25 to review; next-step actions are present.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-07
- **Evidence interpretation:** Results screen visible; this reused screenshot is not attributed to MD.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-010-Job-Matching-Results.png`
- **Blocking issue:** None reported

### S5-UAT-07: Generate and edit resume and cover letter

- **Assigned tester:** Joyee Chakraborty (Student)
- **Test steps:** Generate both drafts; review/edit sections; save or export PDF or Word; inspect output status.
- **Expected outcome:** Generated drafts are reviewable/editable and exports complete with clear feedback.
- **Actual result:** Team-reported PASS. Screens show generated resume and cover-letter drafts, editable section controls, PDF downloaded messages and cover-letter edit area.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-08, FR-09, FR-16
- **Evidence interpretation:** Screenshots demonstrate generated content and export success messages; they do not alone prove exported file contents.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-011-Resume-Builder.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-012-Cover-Letter-Builder.png`
- **Additional UAT evidence:** `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-003-Resume-PDF-Downloaded.png`, `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-004-Resume-Draft-Generated.png`, `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-005-Cover-Letter-Draft-Generated.png`, `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-006-Cover-Letter-PDF-Downloaded.png`
- **Blocking issue:** None reported

### S5-UAT-08: Get interview questions and feedback

- **Assigned tester:** Joyee Chakraborty (Student)
- **Test steps:** Open Interview Preparation; answer a question; request revised feedback.
- **Expected outcome:** User can understand generated questions, feedback and next steps.
- **Actual result:** Team-reported PASS. Screens show an AI-generated question, answer text, AI feedback and detailed suggestions.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-10
- **Evidence interpretation:** Visible AI feedback; screenshots do not imply hiring decisions or scores.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-013-Interview-Preparation.png`
- **Additional UAT evidence:** `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-007-Interview-AI-Feedback.png`
- **Blocking issue:** None reported

### S5-UAT-09: Use account settings and navigation

- **Assigned tester:** Joyee Chakraborty (Student)
- **Test steps:** Open account settings; review account/photo/password controls; navigate between major pages.
- **Expected outcome:** Account controls and navigation are understandable to Student users.
- **Actual result:** Team-reported PASS. Production screenshot shows profile photo controls, personal details and password section; lead reports button/navigation testing completed.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-01, FR-02, NFR-01
- **Evidence interpretation:** Settings UI visible; saved password or photo operation not independently evidenced by screenshot.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-003-Student-Dashboard.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-014-Account-Settings.png`
- **Blocking issue:** None reported

### S5-UAT-10: Manage careers, skills and resources

- **Assigned tester:** Md Enamul Haque (Administrator)
- **Test steps:** Access admin pages; inspect user, career, skill, resource records; open Add and Edit forms.
- **Expected outcome:** Authorised Administrator can find records and access management actions.
- **Actual result:** Team-reported PASS. Production screenshots show management lists. UAT images show Add Career, Add Skill and Edit Learning Resource forms opened with editable fields.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-14
- **Evidence interpretation:** New screenshots show forms only; they do not independently prove saved/committed admin mutations.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-015-Admin-Dashboard.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-016-Admin-User-Management.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-017-Admin-Career-Management.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-018-Admin-Skill-Management.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-019-Admin-Learning-Resource-Management.png`
- **Additional UAT evidence:** `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-008-Admin-Add-Career-Form.png`, `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-009-Admin-Add-Skill-Form.png`, `docs/testing/evidence/sprint-5/uat/S5-UAT-EV-010-Admin-Edit-Learning-Resource-Form.png`
- **Blocking issue:** None reported

### S5-UAT-11: Review reports, analytics and audit history

- **Assigned tester:** Md Enamul Haque (Administrator)
- **Test steps:** Inspect admin summary/analytics; inspect open resource reports and audit records.
- **Expected outcome:** Administrator can review reports and recorded administrative activity.
- **Actual result:** Team-reported PASS. Admin Dashboard shows analytics and recent activity; Reports shows one open broken-link report; Audit Records shows two events.
- **Status:** PASS (team-reported)
- **Related requirements:** FR-15, FR-18
- **Evidence interpretation:** The one open resource report is operational content and still needs normal report disposition.
- **Production evidence:** `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-015-Admin-Dashboard.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-020-Admin-Resource-Reports.png`, `docs/testing/evidence/sprint-5/production-verification/S5-PROD-EV-021-Admin-Audit-Records.png`
- **Blocking issue:** None reported

## 4. UAT summary

| Measure | Recorded result |
| --- | --- |
| Scenario count | 11 |
| PASS (team-reported) | 11 |
| FAIL reported | 0 |
| Blocked reported | 0 |
| New UAT screenshots | 10 |
| Reused Production screenshots | 21 available; references by case |
| Individual written sign-offs | Not supplied |
| Overall UAT status | Reported PASS, formal sign-off pending documentation |

## 5. Evidence interpretation and limitations

- The 21 screenshots in `production-verification/` were previously collected for WBS 8.9. They are reused for product-state context, not attributed to an individual UAT participant.
- The 10 files in `uat/` show additional application outcomes or accessible forms, captured/provided during the same finalisation period. The UAT screenshot IDs map to the original uploaded images in `uat/evidence-manifest.csv`.
- Admin Add Career, Add Skill and Edit Learning Resource screenshots display usable forms. They do **not** independently prove that the save action succeeded or persisted in the database.
- Successful PDF download messages appear on the Resume and Cover Letter screens; opening and reviewing the exported PDF contents is not separately evidenced by screenshots.
- Tester involvement and the absence of blocking issues are documented from the project lead's report. Individual written approval has not been supplied.

## 6. Non-blocking observations and final scope actions

| ID | Observation | Evidence | Disposition for closeout |
| --- | --- | --- | --- |
| OBS-UAT-01 | Administrator User Management displays Last Login as Never for users | S5-PROD-EV-016 | Verify display / record accepted limitation or fix with retest |
| OBS-UAT-02 | One broken-link report is open in the Administrator Resource Reports queue | S5-PROD-EV-020 | Treat as open report workflow item until resolved/dismissed and recorded |
| OBS-UAT-03 | Resume screenshot shows a possible stray text fragment in Experience content | S5-UAT-EV-004 | Review generated/exported draft before final closure; capture defect if reproducible |
| SCOPE-UAT-01 | FR-17 Data Deletion has no demonstrated acceptance result in these 11 cases | Requirements document | Obtain approved scope decision or explicit test outcome; do not infer PASS |

These observations did not result in a blocking issue according to the project lead. Their formal disposition belongs in the Sprint 5 closeout and, where applicable, the defect or requirements register.

## 7. UAT acceptance decision

**Execution decision:** 11/11 PASS reported for allocated internal team UAT scenarios. No blockers reported.

**Formal acceptance:** Individual signed approval is not available in the supplied material. This document does not record forged signatures or independent student acceptance. The team can append genuine acknowledgement in the GitHub PR or signed meeting/acceptance record.

| Participant | Execution | Written approval / date |
| --- | --- | --- |
| Jerald Christopher Bucud | Completed, as reported by project lead | Not provided |
| Joyee Chakraborty | Completed, as reported by project lead | Not provided |
| Md Enamul Haque | Completed, as reported by project lead | Not provided |

## 8. Repository placement

- Plan and execution record: `docs/testing/sprint-5-uat-test-plan.md`
- Detailed Excel register: `docs/testing/sprint-5-uat-execution-results.xlsx`
- New UAT evidence: `docs/testing/evidence/sprint-5/uat/`
- Reused Production evidence: `docs/testing/evidence/sprint-5/production-verification/`
- Link the recorded result and open observations from `docs/project-management/sprint-5-closeout.md`.


## 9. Detailed UAT Excel workbook and evidence reuse

The detailed execution workbook is maintained at `docs/testing/sprint-5-uat-execution-results.xlsx`. Its eight worksheets contain the reported execution summary, 11 fully documented acceptance scenarios, 46 numbered procedural checkpoints, a register of all 31 screenshots, requirements traceability, observations, team acceptance records, and record-maintenance notes.

All 21 existing WBS 8.9 Production images are linked through their original `docs/testing/evidence/sprint-5/production-verification/` paths. They are not reassigned to particular UAT photographers. The 10 new UAT images remain in `docs/testing/evidence/sprint-5/uat/`. Both image groups are supporting screenshots. Participant execution is based on project-lead confirmation.

The workbook intentionally omits a deployed Git commit SHA. SHA-256 values in the image register, where present, verify screenshot file integrity only. Formal sign-off by each tester must be added when real approval evidence is received.
