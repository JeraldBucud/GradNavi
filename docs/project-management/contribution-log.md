# Contribution Log

Status: Active project record

Use this log with GitHub commits, issues, pull requests, reviews, meeting records, test evidence, and document version history.

## Contribution entries

| Date | Member | Contribution | Type | Requirement or deliverable | Evidence link | Reviewed by | Status |
|---|---|---|---|---|---|---|---|
| 2026-08-30 | Jerald | Implemented WBS 5.3 Weighted Recommendation Engine, including deterministic career-fit scoring, weighted O*NET competency matching, ranking, explanation evidence, automated tests, and scoring design documentation. | Backend development | WBS 5.3 Weighted Recommendation Engine | https://github.com/JeraldBucud/GradNavi/pull/27 | | Complete |
| 2026-08-31 | Jerald | Implemented WBS 5.5 Skill Gap and Career Readiness Scoring, including proficiency mapping, weighted readiness calculation, skill-gap classification, database-backed validation, automated tests, and readiness scoring documentation. | Backend development | WBS 5.5 Skill Gap and Readiness Scoring Logic | https://github.com/JeraldBucud/GradNavi/pull/28 | | Complete |
| 2026-09-04 | Jerald | Prepared the Sprint 2 integration plan, Sprint 2 test plan, and 80-case Sprint 2 test tracker to support integration and testing across WBS 5.2 to WBS 5.9. | Documentation | WBS 5.9 Sprint 2 Integration and Testing | https://github.com/JeraldBucud/GradNavi/pull/30 | | Complete |
| 2026-09-05 | Jerald | Reviewed the WBS 5.4 Career Recommendation API integration, corrected the pull request target to `feature/sprint-2`, and coordinated its merge into the Sprint 2 integration branch. | Code review | WBS 5.4 Career Recommendation API / WBS 5.9 Integration | https://github.com/JeraldBucud/GradNavi/pull/29 | | Complete |
| 2026-09-05 | Jerald | Executed and documented Sprint 2 integration and regression testing, added testing evidence, and updated the central Sprint 2 test tracker. Verified 30 WBS 5.3 tests, 39 WBS 5.5 tests, 84 careers regression tests, and 185 full backend tests with no recorded failures. | Testing | WBS 5.9 Sprint 2 Integration and Testing | https://github.com/JeraldBucud/GradNavi/pull/31 | | Complete |

| 2026-09-18 | Jerald | WBS 5.6 delayed interface recovery and implementation support: implemented the Figma-aligned Career Recommendations and Skill Gap Analysis interfaces, selected-career Readiness API, Top Match AI explanation, AI Gap Summary, deterministic Fix First integration, database-backed AI caching, Student Profile redesign support, multiple Career Goals, personality-assessment flow, documentation alignment, and full regression validation. | Frontend development, backend development, AI integration, testing, design, documentation | WBS 5.6 Recommendation and Readiness Interface | https://github.com/JeraldBucud/GradNavi/pull/44 | | Pending review |

WBS 5.6 ownership note:

- The Microsoft Project plan continues to record Joyee as the official owner of WBS 5.6.
- This contribution entry records Jerald's actual implementation support and recovery work after the delayed interface became an integration blocker.
- The contribution record does not reassign the official WBS ownership.
- Supporting evidence includes Pull Request #44, `docs/project-management/wbs-5.6-closeout.md`, Git history, and the final WBS 5.6 regression results.
## WBS 8.12 Late-Project Contribution Reconciliation

This section adds a verified late-project snapshot without replacing detailed GitHub history.

Official WBS ownership remains defined by Microsoft Project and the project-management ownership records. Supporting work does not transfer official task ownership.

| Sprint or period | Member | Verified contribution | Evidence | Status |
| --- | --- | --- | --- | --- |
| Sprint 3 | Jerald | WBS 6.2 AI Prompt Templates and Safety Rules | PR #36 | Complete |
| Sprint 3 | Jerald | WBS 6.6 Interview Question and Feedback API | PR #38 | Complete |
| Sprint 3 | Jerald | Resume and Cover Letter interface implementation support on the delayed WBS 6.5 work | PR #59 | Complete |
| Sprint 3 closeout | Jerald | Sprint 3 testing reconciliation, review, retrospective, and closeout evidence | PR #83 and `sprint-3-closeout.md` | Complete |
| Sprint 3 | MD | WBS 6.3 Resume Generation Backend | PR #37 | Complete |
| Sprint 3 | MD | WBS 6.4 Cover Letter Generation Backend | PR #40 | Complete |
| Sprint 4 | Jerald | WBS 7.1 Sprint 4 planning | PR #43 | Complete |
| Sprint 4 | Jerald | WBS 7.2 Job Description Extraction and Matching | PR #60 | Complete |
| Sprint 4 | Jerald | WBS 7.4 AI Response Validation and Error Handling | PR #66 | Complete |
| Sprint 4 | Jerald | WBS 7.8 Role Permissions and Audit Records | PR #70 | Complete |
| Sprint 4 | Jerald | Sprint 4 integration/testing and final closeout coordination | PR #67, PR #73, PR #85 | Complete |
| Sprint 4 | Jerald | FR-13 Student Progress Dashboard implementation | PR #75 | Complete |
| Sprint 4 | Joyee | WBS 7.5 Job Matching Interface | PR #61 | Complete |
| Sprint 4 | Joyee | WBS 7.7 Admin Dashboard Interface | PR #64 | Complete |
| Sprint 4 | MD | WBS 7.3 OpenAI Service Integration | PR #65 | Complete |
| Sprint 4 | MD | WBS 7.6 Admin Models and API | PR #62 | Complete |
| Sprint 5 | Jerald | WBS 8.3 Security and Permission Testing | PR #80 and PR #89 | Complete for local scope, 2 deployment checks deferred |
| Sprint 5 | Jerald | Resume grounding and ATS export correction found during WBS 8.2 regression | PR #90 | Complete |
| Sprint 5 | Jerald | WBS 8.2 integration regression review checkpoint | PR #91 | In Progress |
| Sprint 5 | Jerald | WBS 8.12 Final Report and GitHub Review | `jerald/wbs-8.12-final-report-github-review` | In Progress |
| Sprint 5 | Joyee | WBS 8.4 Performance and Usability Review and WebP optimisation | PR #94 | In Progress |
| Sprint 5 | Joyee | WBS 8.5 Admin Dashboard mobile heading correction | PR #95 | In Progress |
| Sprint 5 | Joyee | WBS 8.8 Frontend Deployment preparation and Vercel preview | PR #92 | In Progress |
| Sprint 5 | MD | WBS 8.7 Backend and Database Deployment configuration and Railway work | PR #93 | In Progress |

### Reconciliation rule

- A merged PR or formal closeout record supports a Complete contribution entry.
- An open PR remains In Progress until its WBS closeout is verified.
- Contribution evidence records actual work and support.
- Contribution evidence does not silently reassign Microsoft Project ownership.
- Final WBS 8.12 closeout should add any remaining WBS 8.6, 8.9, 8.10, 8.11, 8.13, and presentation contributions after evidence exists.

## Contribution types

- Project management
- Requirement analysis
- Documentation
- Frontend development
- Backend development
- Database development
- AI integration
- Testing
- Code review
- Design
- Data preparation
- Deployment
- Presentation
- Meeting leadership
- Meeting participation

## Member summary

| Member | Main expected evidence |
|---|---|
| Jerald | Roadmap, risk register, quality plan, tools and resources, repository setup, integration, deployment, testing coordination, pull-request reviews |
| Joyee | Project background and scope, frontend branch, interface components, responsive design, accessibility, validation, frontend tests, usability evidence |
| Md Enamul | Requirements, WBS, backlog, task leads, backend branch, database branch, authentication, permissions, scoring, matching, AI services, backend tests |

## Evidence rule

Each completed item should reference at least one source:

- GitHub commit
- GitHub issue
- Pull request
- Pull-request review
- Meeting minute
- Test result
- Diagram or design file
- Document version
- Deployment record
- Presentation file

## Review schedule

The current Team Leader will review the contribution log during the weekly meeting and before each assessment submission.
