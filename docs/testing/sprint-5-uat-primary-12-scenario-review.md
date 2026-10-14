# GradNavi Sprint 5 UAT, Primary Twelve-Scenario Closeout Record

- **WBS:** 8.6, User Acceptance Testing
- **Working decision:** The project lead selected Joyee Chakraborty's twelve-scenario UAT account as the **primary narrative for Sprint 5 closeout** on 14 October 2026.
- **Reported result:** 12/12 PASS, **reported in Joyee's Assessment 3 Section 7**. This is not twelve newly performed tests or twelve independently witnessed test results.
- **Environment claimed in source:** Initial staging verification with Vercel preview/Railway staging, followed by a final production smoke at `https://gradnavi.site`.
- **Tester attribution:** Joyee supplied the report and a named staging check. The draft does not establish a separate named executor/date for each of the twelve production cases.
- **Formal team acceptance:** Pending. This document does not record approval on behalf of Jerald or MD.
- **Original historical case set:** The existing eleven-case WBS 8.6 plan and workbook are retained intact for traceability, not added to twelve as if they were distinct executions.

## 1. Source and evidence hierarchy

**Primary report source:** Joyee's submitted `A3_Joyee_Sections_4_5_7_8_9.docx`, Section 7 (pp. 24–28). This source is supplied for academic consolidation; the private report file is **not** committed to this public repository.

**Directly attributable GitHub staging execution:** [Joyee's PR #92 staging verification on 11 October](https://github.com/JeraldBucud/GradNavi/pull/92#issuecomment-6107719099) and [attached preview/staging screenshots](https://github.com/JeraldBucud/GradNavi/pull/92#issuecomment-6107737018). The comment describes student account/profile/recommendation/skill-gap flows, administrator page loads and a logged test-user role change. **These specifically verify reported staging activities, not the later production repeat.**

**Supplementary production records already in GitHub:** [WBS 8.9 Production Verification folder](evidence/sprint-5/production-verification/) with 21 named screenshots and a workbook recording 21/21 project-lead-reported PASS; [original WBS 8.6 UAT folder](evidence/sprint-5/uat/) with ten additional images, eleven-case workbook and detailed test plan. These are reused for observable product outcomes, not silently reassigned to Joyee as their photographer or executor.

## 2. Joyee's primary twelve-scenario result table

The following expected results and outcomes follow Joyee's Section 7 table. Where the report supplies only a result or an image of a page, the evidence column does **not** claim a persisted mutation or independent execution proof.

| Joyee case | User | Scenario and expected outcome from Section 7 | Joyee-reported result | Independent support or limitation |
| --- | --- | --- | --- | --- |
| UAT-01 | Student | Homepage opens with navigation and Get Started | PASS | S5-PROD-EV-001 visual production page evidence; Joyee's PR #92 preview-home staging image |
| UAT-02 | Student | Create an account, log in, Student Dashboard shown | PASS | PR #92 staging sign-up/login report and screenshots; S5-PROD-EV-002 and 003 show production login/dashboard states, not necessarily registration persistence |
| UAT-03 | Student | Save skills, career goal, interests, education, experience and project; data persists after refresh | PASS | PR #92 staging profile-save report; S5-PROD-EV-004 and S5-UAT-EV-001 show production saved state; all listed field categories and refresh persistence are not individually witnessed |
| UAT-04 | Student | Career Recommendations show ranked careers, match percentage, readiness and AI explanation | PASS after reported data-import fix | Joyee Figure 7.1 and S5-PROD-EV-005 show results; PR #92 staging recommendation and explanatory response |
| UAT-05 | Student | Skill Gap Analysis shows readiness, gaps and AI summary; score responds to evidence change | PASS | Joyee Figure 7.2 and S5-PROD-EV-007; PR #92 staging summary; before/after score mutation not separately captured here |
| UAT-06 | Student | Learning Resources are available for priority skill gap | PASS | S5-PROD-EV-009 and original S5-UAT-04 workflow support resource display |
| UAT-07 | Student | Interview questions, AI feedback and completion summary | PASS | S5-PROD-EV-013, S5-UAT-EV-007 and Joyee's Section 5 Interview figures show question/feedback; completion summary not independently evidenced by these references |
| UAT-08 | Admin | Administrator signs in and sees live dashboard counts | PASS | Joyee Figure 7.3; S5-PROD-EV-015 and PR #92 staging Admin Dashboard count report |
| UAT-09 | Admin | Manage users; own administrator account cannot be deactivated | PASS | S5-PROD-EV-016 shows Users page; blocked self-deactivation requires a separate action/assertion to be fully independently verified |
| UAT-10 | Admin | Career, skill, learning resource and report pages load with correct data | PASS | PR #92 staging page list, production images S5-PROD-EV-017 to 020, UAT form images S5-UAT-EV-008 to 010 |
| UAT-11 | Admin | Change a test user's role; change persists and is recorded in Audit Records | PASS | Joyee Figure 7.4 and PR #92 staging role-change/audit comment; production S5-PROD-EV-021 shows Audit Records, not the entire production mutation sequence |
| UAT-12 | Any | On mobile, menu collapses and content stacks correctly | PASS after reported fix | Joyee Section 4 responsive image, WBS 8.2 mobile frontend regression screenshots; PR #95 fixed Admin Dashboard heading overlap |

### Count and interpretation

- **Primary UAT narrative:** 12/12 PASS **Joyee-reported**, zero failing cases listed in her UAT table.
- **Evidence status:** Mixed support from directly attributed PR #92 staging checks, Joyee's production-screen report figures and previously retained team production evidence. Not every expected result is independently re-enacted or proven by screenshots.
- **Acceptance:** The twelve reported scenario outcomes can be used in the closeout narrative with the attribution above. No new automated run, production test session or member sign-off is claimed.

## 3. Crosswalk to the original eleven-case GitHub record

The original `S5-UAT-01`–`11` dataset is **historical supporting evidence**, rather than a second population of twelve independently additional tests.

| Joyee primary case | Related original GitHub case(s) | Important scope distinction |
| --- | --- | --- |
| UAT-01 | WBS 8.9 S5-PROD-EV-001, S5-UAT-09 navigation | Homepage is explicit in Joyee's list but not its own original eleven-case UAT |
| UAT-02 | S5-UAT-01, WBS 8.9 S5-PROD-EV-002/003 | Joyee separately adds new account creation |
| UAT-03 | S5-UAT-01 | Joyee lists more field categories and refresh persistence |
| UAT-04 | S5-UAT-02 | Career Recommendations, with reported initial reference-data issue |
| UAT-05 | S5-UAT-03 | Skill Gap Analysis |
| UAT-06 | S5-UAT-04 | Learning Resources, but original case also includes roadmap progress |
| UAT-07 | S5-UAT-08 | Interview practice |
| UAT-08 | S5-UAT-11 and S5-PROD-EV-015 | Admin dashboard/login, but original test relates reports and analytics |
| UAT-09 | S5-UAT-10, WBS 8.3 security evidence | Joyee expressly adds self-deactivation prevention |
| UAT-10 | S5-UAT-10 and S5-UAT-11 | Management lists and Reports |
| UAT-11 | S5-UAT-11 and PR #92 staging test | Joyee expressly adds role-change mutation plus audit record |
| UAT-12 | WBS 8.2 frontend mobile regression / PR #95 | Mobile-responsive case is distinct from the old eleven-case UAT |

**Important retained coverage:** The original eleven-case record and production verification also cover **Job Matching, Roadmap progress, Resume/Cover Letter generation and downloads, and Account Settings**. Joyee's twelve UAT scenarios do not expressly list all these as standalone cases. Preserve their approved evidence and outcomes as **supplementary**, rather than dropping that functionality from Sprint 5 verification.

## 4. Reported issues and final dispositions to verify

| Observation | Joyee's Section 7 report | Independent repository evidence / remaining question |
| --- | --- | --- |
| Empty career/skill search after deployment | Missing reference-data import, reported fixed after import | Joyee Figure 7.5 shows before state; source claims retest. Verify import/deployment record before asserting an independent production retest |
| Recommendations unavailable after deployment | Missing O*NET demand snapshot, reported fixed after import | Joyee Figure 7.6 shows before state and Figure 7.1 shows a working view; independent import event not established in this review |
| Admin mobile heading overlap | Fixed under PR #95 | PR #95 and frontend regression screenshots give separate project evidence |
| Skill Gap AI prose says 5.54 versus display 6% | Observed on staging; reported to team | [PR #92 staging comment](https://github.com/JeraldBucud/GradNavi/pull/92#issuecomment-6107719099) corroborates observation, not a confirmed production defect or fix |
| User Management Last Login shows Never | Open, future fix | Existing Sprint 5 closeout `OBS-S5-001`; record a limitation decision or fix with retest |

No failure should be silently marked fixed on the basis of a verbal summary when the available evidence supports only an observed later state.

## 5. Formal closeout decision

**Adopted as the primary WBS 8.6 narrative:** Joyee's twelve scenarios, **12/12 PASS as reported in her submitted Assessment 3 contribution**.

**Historical supporting record:** Previous eleven-case GitHub plan/workbook remains available and labelled as such. Results are not added across different case definitions.

**Formal approval still pending:** Obtain explicit approval of the twelve-case scope and the reconciled evidence from the project team. Do not mark WBS 8.13 project delivery formally Accepted based only on this narrative selection.

**Next review:** Confirm case attribution, note the unverified substeps where screenshots demonstrate page state only, reconcile the non-blocking issues, then record actual member acceptance with dates.
