# GradNavi

GradNavi is an AI-powered Career Guidance System developed for the COIT20273 / COIT13230 Software Design and Development Project, Term 2 2026.

The responsive web application helps students explore careers, compare their current profile with career requirements, plan skill development, prepare application documents, and practise interviews. Student and administrator workflows are implemented in the React frontend and Django REST Framework backend.

**Repository status (12 October 2026):** The Sprint 5 integration branch was merged into `main` through [PR #101](https://github.com/JeraldBucud/GradNavi/pull/101) on 11 October 2026. The repository contains the feature-complete Sprint 4 baseline, Sprint 5 deployment configuration, and recorded staging and regression evidence. A merge into `main` does not by itself establish that every production verification or project-closeout task has been signed off.

## Project overview

Implemented student-facing capabilities include:

- Student registration, login, password recovery, account settings, and profile-photo management
- Student Profile covering skills, education, interests, experience, projects, and career goals
- Explore Careers and evaluated career selection
- Ranked Career Recommendations, score explanations, Career Readiness, and Skill Gap Analysis
- Learning Resources, recommended development steps, Career Roadmap, and progress tracking
- Job Description Matching against the student's recorded skills
- AI-assisted Resume Builder and Cover Letter Builder with editable drafts and export options
- Text-based Interview Preparation with generated questions and written feedback
- Student Dashboard and a responsive interface

Implemented administrator areas include the Dashboard, User Management, Career Management, Skill Management, Learning Resource Management, resource reports, and audit records. Backend permission enforcement restricts administrator functions.

The local reference dataset documents **36 careers** and source-backed career/skill mappings. Source material includes Australian occupation information, O*NET and ESCO evidence, a reviewed Interest catalogue, and learning-resource data. See [Reference Data](docs/reference-data/README.md) and [Dataset Version](docs/reference-data/DATASET_VERSION.md).

**Scoring and AI:** Competency Fit and Technology Fit use documented rules, while AI-generated embeddings support semantic alignment. A defined weighted formula combines the component scores. The separate generative text provider supplies explanations, editable Resume and Cover Letter drafts, and Interview content. See the detailed [AI architecture](#ai-architecture-status) below.

GradNavi is a student capstone prototype providing decision support rather than verified professional career advice.

## Repository purpose

This repository stores the GradNavi capstone project baseline, implementation work, system design, Sprint planning, testing, and evidence.

The repository currently includes:

- Assessment 1 group project proposal
- Project overview and team documentation
- Functional and non-functional requirements
- Requirement assignment records
- Microsoft Project-aligned Work Breakdown Structure
- Product backlog and Sprint planning records
- Risk and quality planning
- Responsibility and task-lead records
- Delivery roadmap and Microsoft Project schedule
- System architecture documentation
- Entity Relationship diagram
- Use case diagram
- Context diagram
- Django REST Framework backend
- React frontend
- JWT authentication implementation
- Student Profile backend
- Career and skill reference data
- Weighted composite career-recommendation logic, including embedding-based semantic alignment
- Career Recommendation API and Explore Careers API
- Skill-gap and Career Readiness scoring
- Learning Suggestions, Roadmap, and progress APIs
- Shared AI service foundation
- AI prompt templates and safety rules
- AI privacy mapping and structured contracts
- Resume Generation backend
- Cover Letter Generation backend
- Interview Question and Feedback API
- PostgreSQL configuration and migrations
- Student and administrator interface implementations
- Job Description Matching and administration APIs
- Staging and production deployment configuration
- Frontend and backend integration work
- Sprint integration plans
- Sprint testing plans, test cases, and evidence
- Contribution and communication records

## Main assessment and design artefacts

- [Assessment 1 Group Project Proposal](docs/project-management/COIT20273%20Assessment%201.docx)
- [GradNavi System Architecture Diagram](docs/project-management/GradNavi%20architecture%20diagram.png)
- [GradNavi ER Diagram](docs/project-management/GrandNavi%20ER%20diagram.png)
- [GradNavi Use Case Diagram](docs/project-management/Use%20Case%20GradNavi.drawio.png)
- [GradNavi Context Diagram](docs/project-management/Context%20Diagram%20GradNavi.drawio.png)
- [GradNavi Final Microsoft Project Plan](docs/project-management/GradNavi_Final_Project_Plan.mpp)

Note: the current repository filename for the ER diagram is `GrandNavi ER diagram.png`.

## Project documentation

- [Project Overview](docs/01-project-overview.md)
- [Team Members and Roles](docs/02-team-members-and-roles.md)

## Requirements

- [Functional Requirements](docs/requirements/functional-requirements.md)
- [Non-Functional Requirements](docs/requirements/non-functional-requirements.md)
- [Requirements Assignment Matrix](docs/requirements/requirements-assignment-matrix.md)

## Project management

- [Communication Plan](docs/project-management/communication-plan.md)
- [Contribution Log](docs/project-management/contribution-log.md)
- [Leadership Rotation](docs/project-management/leadership-rotation.md)
- [Meeting Minutes Template](docs/project-management/meeting-minutes-template.md)
- [Product Backlog](docs/project-management/product-backlog.md)
- [Quality Plan](docs/project-management/quality-plan.md)
- [Responsibility Matrix](docs/project-management/responsibility-matrix.md)
- [Risk Register](docs/project-management/risk-register.md)
- [Roadmap and Milestones](docs/project-management/roadmap-and-milestones.md)
- [Task Leads](docs/project-management/task-leads.md)
- [Tools and Resources](docs/project-management/tools-and-resources.md)
- [Work Breakdown Structure](docs/project-management/work-breakdown-structure.md)

## System design

- [REST API Design](docs/system-design/rest-api-design.md)
- [Security Architecture](docs/system-design/security-architecture.md)
- [Student Profile Data Design](docs/system-design/student-profile-data-design.md)
- [Student Profile API Model Mapping](docs/system-design/student-profile-api-model-mapping.md)
- [Career and Skill Reference Data Design](docs/system-design/career-skill-reference-data-design.md)
- [Recommendation Scoring Design](docs/system-design/recommendation-scoring-design.md)
- [Readiness Scoring Design](docs/system-design/readiness_scoring_design.md)
- [AI Prompt and Safety Design](docs/system-design/ai-prompt-safety-design.md)
- [Scoring Validation Evidence](docs/system-design/wbs-5.3-scoring-validation.md)

## Integration plans

- [Sprint 1 Integration Plan](docs/system-design/sprint-1-integration-plan.md)
- [Sprint 2 Integration Plan](docs/system-design/sprint-2-integration-plan.md)
- [Sprint 3 Integration Plan](docs/system-design/sprint-3-integration-plan.md)
- [Sprint 4 Integration Plan](docs/system-design/sprint-4-integration-plan.md)

## Testing documentation

### Sprint 1

- [Sprint 1 Test Plan](docs/testing/sprint-1-test-plan.md)
- [Sprint 1 Test Case Tracker](docs/testing/sprint-1-test-cases.xlsx)

### Sprint 2

- [Sprint 2 Test Plan](docs/testing/sprint-2-test-plan.md)
- [Sprint 2 Test Case Tracker](docs/testing/sprint-2-test-cases.xlsx)

### Sprint 3

- [Sprint 3 Test Plan](docs/testing/sprint-3-test-plan.md)
- [Sprint 3 Test Case Tracker](docs/testing/sprint-3-test-cases.xlsx)

### Sprint 4

- [Sprint 4 Test Plan](docs/testing/sprint-4-test-plan.md)
- [Sprint 4 Test Case Tracker](docs/testing/sprint-4-test-cases.xlsx)
- [Sprint 4 Testing Status](docs/testing/sprint-4-testing-status.md)
- [Sprint 4 Postman Collection](docs/testing/postman/GradNavi-Sprint4.postman_collection.json)

### Sprint 5

- [Security and Permission Test Plan](docs/testing/sprint-5-security-permission-test-plan.md)
- [Security and Permission Test Cases](docs/testing/sprint-5-security-permission-test-cases.xlsx)
- [Security Execution Matrix](docs/testing/sprint-5-security-permission-execution-matrix.md)
- [Integration Regression Review](docs/testing/sprint-5-wbs-8.2-integration-regression-review.md)

Testing evidence is stored under:

```text
docs/testing/evidence/
```

## Planning images

- [Risk Matrix](docs/project-management/images/risk-matrix.png)

The previous delivery-roadmap image is not used as the current planning baseline.

The current delivery schedule is documented in:

- [Microsoft Project Plan](docs/project-management/GradNavi_Final_Project_Plan.mpp)
- [Roadmap and Milestones](docs/project-management/roadmap-and-milestones.md)
- [Work Breakdown Structure](docs/project-management/work-breakdown-structure.md)

## System actors and external entities

The current GradNavi requirements identify the following main system actors and external entities:

| Actor or entity | Role |
|---|---|
| Student | Maintains a profile, receives career guidance, analyses skill gaps, prepares application material, practises interviews, and tracks progress |
| System Administrator | Manages users, careers, skills, learning resources, reports, audit records, and reference data |
| OpenAI API | Backend-integrated text generation and semantic embeddings for approved AI features; no direct React-to-OpenAI calls |
| Public Career and Learning Sources | Supply reference information reviewed before entry into GradNavi |

Career Adviser access is outside the current V1 scope.

## High-level student use cases

The project proposal and integrated implementation cover these student use cases:

1. Register and authenticate
2. Manage Student Profile
3. Receive career recommendations
4. View recommendation scores and explanations
5. Perform skill-gap analysis
6. View Career Readiness score
7. Match a job description
8. Generate a resume draft
9. Generate a cover-letter draft
10. Practise interview questions
11. Receive learning suggestions
12. View career path roadmap
13. Track progress
14. Review, edit, and save generated content
15. Manage saved document drafts where supported

**Scope qualification:** FR-17 (data deletion, including a profile-deletion request) is still marked Backlog in the project records. Deleting browser-stored Resume or Cover Letter draft versions is not equivalent to the full FR-17 requirement. FR-16 (AI content review) has related editing and review behaviour, but its formal WBS mapping and final backlog status still require reconciliation. See the [Product Backlog](docs/project-management/product-backlog.md).

The visual use case diagram is stored in the project-management folder.

## Shared team workspace

The team also uses the CQU Microsoft 365 shared workspace for collaborative files, working documents, and supporting project evidence.

[Open the GradNavi OneDrive / SharePoint workspace](https://cqu365-my.sharepoint.com/shared?listurl=https%3A%2F%2Fcqu365%2Dmy%2Esharepoint%2Ecom%2Fpersonal%2Fmdenamul%5Fhaque%5Fcqumail%5Fcom%2FDocuments&id=%2Fpersonal%2Fmdenamul%5Fhaque%5Fcqumail%5Fcom%2FDocuments%2FCOIT20273%20Software%20Design%20and%20Development%20Project%20%28HT2%2C%202026%29&ct=1786405156473&or=Teams%2DHL&shareLink=1&ga=1&LOF=1)

## Team

| Member | Student ID | Primary role |
|---|---:|---|
| Jerald Christopher Yalung Bucud | 12301099 | Full-Stack Developer and Project Management Lead |
| Joyee Chakraborty | 12286715 | Frontend Lead |
| Md Enamul Haque | 12280315 | Backend Lead and Requirements Lead |

## Technology stack

| Area | Technology |
| --- | --- |
| Frontend | React, JavaScript, Vite, React Router, Lucide React |
| Frontend quality | Oxlint, Vite production build |
| Backend | Python, Django, Django REST Framework |
| Authentication | Django authentication, Simple JWT, role-based permissions |
| Database | PostgreSQL through Psycopg |
| CORS | django-cors-headers |
| AI service architecture | Provider-independent service contracts, validated schemas, prompt templates, privacy allowlists, and safety rules |
| Text generation | Backend OpenAI Responses API, with `gpt-5-nano` as the configured default text model |
| Semantic alignment | OpenAI embeddings, `text-embedding-3-small` as the provider default |
| Planning | Scrum, Trello, GitHub, Microsoft Project |
| Communication | Microsoft Teams |
| Deployment configuration | Vercel frontend, Railway Django backend and PostgreSQL; Docker/Gunicorn backend startup |

## AI architecture status

GradNavi uses a **composite Career Recommendation model**. Its documented base weights are:

| Recommendation component | Base weight | Method |
| --- | ---: | --- |
| Competency Fit | 20% | Source-backed, rule-based matching of student skills to career competencies |
| Technology Fit | 20% | Technology-demand evidence and student technology alignment |
| AI Semantic Alignment | 60% | OpenAI text embeddings and cosine-similarity calculations |

Components are min-max normalised within a recommendation run. The Technology Fit component is active only where its specified alignment threshold is met. When applicable components are unavailable, the service redistributes the available weights rather than fabricating missing scores. The backend computes the weighted result and its rank using defined formulas.

AI embeddings therefore **inform numerical recommendations**. This differs from letting a generative text model invent a career score. Skill Gap, Career Readiness, requirement matching, and related priority rules use their documented calculations separately.

Key implementation references:

- [Composite Recommendation Service](backend/careers/services/composite_recommendation.py)
- [AI Semantic Alignment](backend/careers/services/ai_semantic_alignment.py)
- [OpenAI Embedding Provider](backend/ai_services/providers/openai_embeddings.py)
- [Recommendation Scoring Design](docs/system-design/recommendation-scoring-design.md)
- [Readiness Scoring Design](docs/system-design/readiness_scoring_design.md)

The server-side generative AI layer supports Top Match and Skill Gap explanations, Resume drafts, Cover Letter drafts, Interview Questions, and Interview Feedback. The concrete OpenAI integration was completed in WBS 7.3 and uses the provider boundary established during Sprint 3. The shared foundation includes approved operation identifiers, schemas, prompt templates, trusted/untrusted input boundaries, privacy allowlists, provider exceptions, validated outputs, and Student review indicators.

OpenAI credentials stay in the backend environment, not in the browser. The default backend text model is `gpt-5-nano`. AI-generated career documents are editable and require Student review. Numerical career calculations are not delegated to unrestricted text generation.

## Current implementation status

**Code baseline:** Sprint 5 merged into `main` on 11 October 2026 in [PR #101](https://github.com/JeraldBucud/GradNavi/pull/101). Earlier Sprint closeouts were reconciled before this merge. The final production and project-sign-off status must be read from deployment and testing evidence rather than inferred from branch names.

### Sprint 1: Foundation and Student Profile

Completed foundation work includes Django REST Framework, React routing, PostgreSQL migrations, registration, login, logout, access/refresh tokens, password recovery, protected routes, Student Profile creation and updates, and frontend/backend authentication and profile integration.

- [Sprint 1 Closeout](docs/project-management/sprint-1-closeout.md)

### Sprint 2: Career guidance and learning

The integrated application includes career and skill reference data, composite Career Recommendations, recommendation explanations, Skill Gap Analysis, Career Readiness, Explore Careers, Learning Resources, Career Roadmap, and roadmap progress.

- [Sprint 2 Integration Plan](docs/system-design/sprint-2-integration-plan.md)
- [Recommendation Scoring Design](docs/system-design/recommendation-scoring-design.md)

### Sprint 3: Application documents and interviews

Sprint 3 is formally closed. Its completed increment includes AI prompt/safety contracts, Resume Generation, Cover Letter Generation, their interfaces, Interview Question/Feedback APIs, Interview Preparation UI, and integrated Student application workflows.

The final Sprint 3 tracker records **100 passed out of 100 cases**, with zero failed or blocked. Formal closeout reconciled existing and later-Sprint evidence rather than rerunning all 100 cases at closeout.

**Traceability:** The original WBS 6.7 interface PR #63 closed without merging into the historical Sprint 3 branch. The final Interview Preparation interface was integrated later through PR #78 in Sprint 4, as recorded in the closeout.

- [Sprint 3 Closeout](docs/project-management/sprint-3-closeout.md)

### Sprint 4: Job Matching, AI integration, and Administration

Sprint 4 is formally complete and records **129 passed out of 129 test cases**. Its integrated scope includes:

- Deterministic Job Description Matching and Student Job Matching interface
- OpenAI provider integration for Resume, Cover Letter, and Interview operations
- AI response validation, safe error handling, and privacy controls
- Administration APIs, Dashboard, User/Career/Skill/Learning Resource management, reports, permissions, analytics, and audit records
- Student Progress Dashboard
- Cross-Sprint integration and regression testing

- [Sprint 4 Closeout](docs/project-management/sprint-4-closeout.md)
- [Sprint 4 Testing Status](docs/testing/sprint-4-testing-status.md)

### Sprint 5: Final regression, deployment, and delivery

The Sprint 5 branch, staging fixes, backend/database deployment configuration, and frontend deployment preparation were merged to `main` in [PR #101](https://github.com/JeraldBucud/GradNavi/pull/101).

The repository contains local regression, security, frontend verification, and staging smoke-test records. **Do not treat this merge as blanket sign-off** for production security checks, user acceptance testing, documentation finalisation, or every project-closure WBS item.

- [Sprint 5 Plan and Execution Baseline](docs/project-management/sprint-5-plan.md)
- [Sprint 5 Integration Regression Review](docs/testing/sprint-5-wbs-8.2-integration-regression-review.md)

### Outstanding requirement and evidence reconciliation

- **FR-13 Progress Dashboard:** Implemented, but the planning documents note missing dedicated Microsoft Project task mapping.
- **FR-16 AI Content Review:** Student editing and review behaviour exists; formal requirement/WBS status is still Backlog in the Product Backlog.
- **FR-17 Data Deletion:** The complete profile-deletion and generated-document-deletion requirement is not marked complete.
- **Sprint 5 evidence:** Some committed WBS 8.2 and deployment-specific security records retain pending/deferred statuses even after newer staging and release activity. These records require explicit reconciliation before claiming final sign-off.

See the [Product Backlog](docs/project-management/product-backlog.md) and [Sprint 5 Plan](docs/project-management/sprint-5-plan.md) for the planning history.

## Document generation and interview API capabilities

### Resume Generation

The backend includes an authenticated Resume Generation service based on the Student's own profile.

The implementation uses:

- authenticated Student Profile context
- shared privacy mapping
- shared AI prompt contracts
- structured Resume Draft output
- AI-generated content indicators
- Student-review requirements
- controlled provider failure behaviour

### Cover Letter Generation

The backend includes an authenticated Cover Letter Generation service.

The implementation uses:

- validated Job Description input
- authenticated Student Profile context
- privacy-controlled profile mapping
- untrusted Job Description boundaries
- structured Cover Letter Draft output
- AI-generated content indicators
- Student-review requirements
- controlled provider failure behaviour

### Interview Preparation

The backend includes authenticated endpoints for:

```text
POST /api/v1/interviews/questions/
POST /api/v1/interviews/feedback/
```

Interview Question Generation supports:

- target role
- optional Job Description
- controlled question count
- structured question sets
- focus areas
- AI-generated content indicators
- Student-review requirements

Interview Feedback supports:

- target role
- interview question
- typed Student answer
- strengths
- improvement areas
- suggested responses
- feedback summary
- AI-generated content indicators
- Student-review requirements

The Interview API does not provide hiring probability, pass or fail classifications, or guaranteed employment outcomes.

## Latest recorded testing evidence

The most recent **committed full local Django backend regression** reviewed for Sprint 5 records **1,069 passed, zero failures/errors**. This run was executed against commit `b81fa7e` on 11 October 2026 with a dedicated local PostgreSQL 17.11 database. The release PR includes this regression result, but the test log is evidence for the tested commit, not a fresh execution against every later commit.

Other recorded results:

| Verification | Recorded result | Qualification |
| --- | --- | --- |
| Sprint 3 tracker | 100/100 PASS | Final formal closeout reconciliation |
| Sprint 4 tracker | 129/129 PASS | Formal Sprint 4 closeout |
| Sprint 5 local security and permission tests | 30 PASS, 0 FAIL, 2 deferred | Two deployment-specific checks were still deferred in the committed execution matrix |
| Sprint 5 frontend lint | PASS, zero warnings/errors | Recorded in frontend regression evidence and release PR |
| Sprint 5 frontend production build | PASS | Build included a non-blocking Vite large-chunk advisory |
| Staging Student smoke test | PASS reported on 11 October 2026 | Manual tester report for Vercel Staging + Railway Staging; not a substitute for Production verification |

The reported staging Student smoke flow covered login, Job Matching, Resume Builder, Cover Letter Builder, and Interview Preparation. The integration review notes that final committed screenshots/logs for that particular manual smoke run were not yet available.

One non-blocking observation remained in the regression review: Admin User Management displayed `Never` in the Last Login field for listed users. Do not represent this finding as fixed without a verified retest.

- [Sprint 5 Regression Review](docs/testing/sprint-5-wbs-8.2-integration-regression-review.md)
- [Sprint 5 Security Execution Matrix](docs/testing/sprint-5-security-permission-execution-matrix.md)
- [Sprint 4 Closeout](docs/project-management/sprint-4-closeout.md)
- [Sprint 3 Closeout](docs/project-management/sprint-3-closeout.md)

Automated AI tests use mocked provider responses where appropriate. Separate live-provider smoke evidence is recorded in the relevant integration closeouts.

## Delivery planning

GradNavi followed a five-Sprint Scrum implementation schedule. These are the approved **planned dates**, not proof that formal closeout or every deployment check occurred on the scheduled day.

| Sprint | Dates | Main Outcome |
| --- | --- | --- |
| Sprint 1 | 10 August to 21 August 2026 | Foundation, authentication, Student Profile, and initial integration |
| Sprint 2 | 24 August to 4 September 2026 | Career recommendations, skill gaps, readiness scoring, and learning roadmap |
| Sprint 3 | 7 September to 18 September 2026 | Resume, cover-letter, and interview-preparation functions |
| Sprint 4 | 21 September to 2 October 2026 | Job matching, administration, permissions, audit behaviour, and AI integration |
| Sprint 5 | 5 October to 9 October 2026 | Stabilisation, regression testing, deployment, documentation, and closure |
| Final Presentation | 12 October 2026 | Scheduled final demonstration and presentation |

The Microsoft Project schedule is the authoritative planning baseline.

The detailed task-level schedule, dependencies, ownership, resources, milestones, and planning records are documented in:

- [GradNavi Final Microsoft Project Plan](docs/project-management/GradNavi_Final_Project_Plan.mpp)
- [Roadmap and Milestones](docs/project-management/roadmap-and-milestones.md)
- [Work Breakdown Structure](docs/project-management/work-breakdown-structure.md)
- [Task Leads](docs/project-management/task-leads.md)
- [Responsibility Matrix](docs/project-management/responsibility-matrix.md)
- [Product Backlog](docs/project-management/product-backlog.md)
- [Requirements Assignment Matrix](docs/requirements/requirements-assignment-matrix.md)

When Sprint dates, ownership, dependencies, or milestones change, Microsoft Project should be updated first. Related GitHub planning documents should then be updated to match.

## Deployment and release status

- **Frontend:** Vercel SPA rewrite and configurable `VITE_API_BASE_URL` are tracked in [PR #92](https://github.com/JeraldBucud/GradNavi/pull/92) and `frontend/vercel.json`.
- **Backend:** Railway deployment preparation uses a root-level `Dockerfile`, Gunicorn, environment-based Django settings, and PostgreSQL configuration. See [PR #93](https://github.com/JeraldBucud/GradNavi/pull/93) and the staging packaging fixes in PRs #98 through #100.
- **Release:** [PR #101](https://github.com/JeraldBucud/GradNavi/pull/101) merged `feature/sprint-5` into `main` on 11 October 2026 and records a checked Production release checklist, including the production domain and smoke-test tasks.
- **Evidence boundary:** The release PR reports Production checklist completion. The committed WBS 8.2 regression review and WBS 8.3 matrix still distinguish local/Staging checks from Production-specific verification. A current live health or uptime guarantee is **not** established by this README.

Configuration values and credentials belong in the respective service environments. Do not commit real API keys, database passwords, or Django secrets.## Local development

### Backend

Move into the backend directory:

```powershell
cd backend
```

Create and activate a local Python virtual environment if needed:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Alternatively, activate an existing environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies when required:

```powershell
pip install -r requirements.txt
```

Create a local `.env` file from:

```text
backend/.env.example
```

The development environment expects PostgreSQL settings for:

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

For OpenAI-backed features, configure `OPENAI_API_KEY` in `backend/.env`. The optional `OPENAI_TEXT_MODEL` defaults to `gpt-5-nano`. Keep credentials out of Git.

Apply migrations:

```powershell
python manage.py migrate
```

Load the tracked Career Recommendation reference data before first use:

```powershell
python manage.py import_reference_dataset
python manage.py import_onet_demand_snapshot --snapshot-date 2026-09-16
```

Run these imports in this order on a new database. The base reference
dataset creates the Career, Skill, mapping, and O*NET evidence records.
The demand snapshot then adds the employer-demand percentages required
by the Technology Fit component.

Import the reviewed Interest catalogue and curated learning resources when preparing a full local demonstration database:

```powershell
python manage.py import_interest_catalogue
python manage.py import_learning_resources
```

These management commands use tracked files under `data/reference/`. A deployed environment may use a separate import or seed procedure and should not be assumed to contain every local dataset.

Run the Django development server:

```powershell
python manage.py runserver
```

Run the Django system check:

```powershell
python manage.py check
```

Run the backend test suite:

```powershell
python manage.py test
```

### Frontend

Move into the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the Vite development server:

```powershell
npm run dev
```

Run frontend linting:

```powershell
npm run lint
```

Run the production build check:

```powershell
npm run build
```

## Repository structure

```text
GradNavi/
├── backend/
│   ├── accounts/          # Authentication, settings, profile photos
│   ├── administration/    # Admin API, permissions, analytics, audit records
│   ├── ai_services/       # Provider contracts, text and embedding adapters
│   ├── careers/           # Recommendations, skill gaps, job matching, learning
│   ├── documents/         # Resume and cover-letter APIs
│   ├── interviews/        # Interview questions and feedback
│   ├── profiles/          # Student Profile API
│   ├── gradnavi/          # Django project settings and URLs
│   ├── .env.example
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/               # Pages, layouts, components, services
│   ├── .env.example
│   ├── vercel.json
│   └── package.json
├── data/
│   └── reference/         # Curated career, skill, Interest and learning data
├── docs/
│   ├── project-management/
│   ├── reference-data/
│   ├── requirements/
│   ├── system-design/
│   ├── testing/
│   └── meetings/
├── Dockerfile
└── README.md
```

The full Git tree includes additional migrations, design artefacts, test suites, source attribution, import scripts, and evidence files.

## Project scope limits

GradNavi is a student capstone prototype.

The current V1 scope excludes:

- Native mobile applications
- Live job-board or applicant-tracking-system integration
- Video, audio, or webcam interview simulation
- Payments or subscriptions
- Training or hosting a custom machine-learning model
- Automatic job application submission
- University-system or single-sign-on integration
- Formal accessibility certification
- Multilingual support
- Production-scale infrastructure and disaster recovery

GradNavi provides career-guidance decision support.

Students review AI-generated material before saving or using generated content.

## Document status

Last reviewed against the `main` repository baseline: **12 October 2026**.

The repository is a delivered code and evidence workspace with some formal documentation and WBS reconciliation still pending.

Requirements, diagrams, task ownership, architecture decisions, database design, Sprint planning, testing evidence, deployment records, and assessment documents should stay aligned with the latest approved project baseline.

The Microsoft Project schedule remains the authoritative planning source for planned Sprint dates, task dependencies, ownership, and milestones. GitHub closeout, test, and deployment evidence records the implementation outcome; planned dates alone do not certify execution.
