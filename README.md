# GradNavi

GradNavi is an AI-powered Career Guidance System for students.

The responsive web application analyses a student's skills, interests, education, experience, projects, and career goals. GradNavi provides ranked career recommendations, readiness scores, skill-gap analysis, learning suggestions, career roadmaps, application-document support, interview preparation, and administration functions.

## Project overview

GradNavi uses a structured Student Profile containing skills, education, interests, experience, projects, and career goals.

The planned system includes:

- Secure student and administrator authentication
- Student Profile management
- Ranked career recommendations using documented weighted rules
- Recommendation scores and explanations
- Career-readiness scoring
- Skill-gap analysis
- Job-description analysis and matching
- Editable resume drafts
- Job-specific cover-letter drafts
- Text-based interview preparation and written feedback
- Learning suggestions
- Career-development roadmaps
- Progress tracking
- Administrator management of users, careers, skills, learning resources, audit records, and reports

Numerical recommendation and readiness scores come from documented deterministic scoring logic.

Generative AI supports structured explanations, resume drafts, cover-letter drafts, and interview-preparation content. AI-generated content stays subject to Student review and does not independently determine numerical career scores.

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
- Weighted career-recommendation logic
- Career Recommendation API
- Skill-gap and Career Readiness scoring
- Learning Suggestions and Roadmap API
- Shared AI service foundation
- AI prompt templates and safety rules
- AI privacy mapping and structured contracts
- Resume Generation backend
- Cover Letter Generation backend
- Interview Question and Feedback API
- PostgreSQL configuration and migrations
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
- [Sprint 3 Closeout](docs/project-management/sprint-3-closeout.md)

### Sprint 4

- [Sprint 4 Test Plan](docs/testing/sprint-4-test-plan.md)
- [Sprint 4 Test Case Tracker](docs/testing/sprint-4-test-cases.xlsx)
- [Sprint 4 Testing Status](docs/testing/sprint-4-testing-status.md)
- [Sprint 4 Closeout](docs/project-management/sprint-4-closeout.md)

### Sprint 5

- [Sprint 5 Security and Permission Test Plan](docs/testing/sprint-5-security-permission-test-plan.md)
- [Sprint 5 Security and Permission Test Cases](docs/testing/sprint-5-security-permission-test-cases.xlsx)
- [Sprint 5 Security and Permission Execution Matrix](docs/testing/sprint-5-security-permission-execution-matrix.md)
- [WBS 8.12 Final GitHub Review](docs/project-management/wbs-8.12-final-github-review.md)

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
| OpenAI API | External AI provider used through the Django backend for validated explanations and generated application/interview content |
| Public Career and Learning Sources | Supply reference information reviewed before entry into GradNavi |

Career Adviser access is outside the current V1 scope.

## High-level student use cases

The current project proposal identifies these student use cases:

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
15. Delete saved content or request profile deletion

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
| Frontend | React, JavaScript, Vite, React Router |
| Frontend quality | Oxlint |
| Backend | Python, Django, Django REST Framework |
| Authentication | Django authentication and Simple JWT |
| Database | PostgreSQL through Psycopg |
| CORS | django-cors-headers |
| AI architecture | Provider-independent AI service layer, structured schemas, prompt templates, safety rules, privacy mapping, and validated output contracts |
| AI provider status | Provider-independent AI layer with Django-backed OpenAI integration completed during Sprint 4; deterministic scoring remains separate from generated text |
| Planning | Scrum, Trello, GitHub, Microsoft Project |
| Communication | Microsoft Teams |
| Deployment | Vercel frontend, Railway backend and PostgreSQL; Sprint 5 staging and production verification are tracked under WBS 8.7 to WBS 8.9 |

## AI architecture status

GradNavi separates deterministic career-scoring logic from generative AI features.

Deterministic logic handles:

- Career recommendation scores
- Recommendation ranking
- Skill-gap calculations
- Career Readiness scoring
- Learning-gap ordering

The current AI service foundation includes:

- Approved AI operation identifiers
- Shared input schemas
- Shared output schemas
- Prompt templates
- Trusted and untrusted content separation
- Prompt-injection boundaries
- Privacy allowlists
- AI safety rules
- Provider-independent service contracts
- Controlled provider exceptions
- AI-generated content indicators
- Student-review requirements

Resume, Cover Letter, and Interview services continue to use the provider boundary established during Sprint 3.

WBS 5.6 uses a Django-backed OpenAI text provider for the Top Match explanation and AI Gap Summary. Sprint 4 completed the broader OpenAI service integration used by Resume, Cover Letter, and Interview features. Recommendation scoring, ranking, readiness scoring, requirement status, and Fix First priority remain deterministic.

## Current implementation status

GradNavi is in Sprint 5 finalisation.

The repository baseline has formally completed Sprint 1, Sprint 3, and Sprint 4 closeout records. Sprint 2 test execution is complete, with all 80 planned cases passing, but a dedicated Sprint 2 closeout record was not identified during the WBS 8.12 audit.

### Verified Sprint baselines

| Sprint | Verified result | Current repository state |
| --- | --- | --- |
| Sprint 1 | 61 Pass, 0 Fail, 0 Blocked, 0 Not Run | Complete |
| Sprint 2 | 80 Pass, 0 Fail, 0 Blocked, 0 Not Run | Testing complete; formal closeout record pending reconciliation |
| Sprint 3 | 100 Pass, 0 Fail, 0 Blocked, 0 Not Run | Complete |
| Sprint 4 | 129 Pass, 0 Fail, 0 Blocked, 0 Not Run | Complete; WBS 7.11 Feature Complete reached |
| Sprint 5 | Final verification and delivery work in progress | Regression, usability, deployment, UAT, production verification, documentation, and closure remain active |

### Current Sprint 5 work

The WBS 8.12 audit records the active delivery state.

At the 11 October 2026 audit checkpoint:

- WBS 8.2 Full Regression Testing is in progress through PR #91.
- WBS 8.3 local Security and Permission Testing records 30 Pass, 0 Fail, 0 Blocked, and 2 deployment-deferred cases.
- WBS 8.4 Performance and Usability Review is in progress through PR #94.
- WBS 8.5 final refinement includes the Admin Dashboard mobile heading correction in PR #95.
- WBS 8.7 Backend and Database Deployment is in progress through PR #93.
- WBS 8.8 Frontend Deployment is in progress through PR #92.
- WBS 8.9 Production Verification waits for the final deployed baseline.
- WBS 8.10 Technical Documentation Finalisation remains pending.
- WBS 8.11 User Guide Finalisation remains pending.
- WBS 8.12 Final Report and GitHub Review is in progress.

Open Sprint 5 PRs must not be treated as merged implementation until their final review and merge are complete.

### Current testing baseline

Authoritative completed Sprint-level test records are:

- Sprint 1: 61 of 61 Pass.
- Sprint 2: 80 of 80 Pass.
- Sprint 3: 100 of 100 Pass.
- Sprint 4: 129 of 129 Pass.
- Sprint 5 WBS 8.3 local security and permission scope: 30 Pass, 0 Fail, 0 Blocked, 2 Deferred to deployment.

Sprint 5 final regression, UAT, deployment smoke testing, and production verification remain separate completion gates.

Automated AI regression tests use mocked provider calls where external-provider isolation is required. Controlled live validation and Sprint 4 integration evidence cover the configured OpenAI provider path.

For the current delivery audit, see [WBS 8.12 Final GitHub Review](docs/project-management/wbs-8.12-final-github-review.md).

## Delivery planning

GradNavi follows a five-Sprint Scrum implementation schedule.

| Sprint | Dates | Main Outcome |
| --- | --- | --- |
| Sprint 1 | 10 August to 21 August 2026 | Foundation, authentication, Student Profile, and initial integration |
| Sprint 2 | 24 August to 4 September 2026 | Career recommendations, skill gaps, readiness scoring, and learning roadmap |
| Sprint 3 | 7 September to 18 September 2026 | Resume, cover-letter, and interview-preparation functions |
| Sprint 4 | 21 September to 2 October 2026 | Job matching, administration, permissions, audit behaviour, and AI integration |
| Sprint 5 | 5 October to 9 October 2026 | Stabilisation, regression testing, deployment, documentation, and closure |
| Final Presentation | 12 October 2026 | Final demonstration and presentation |

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

## Local development

### Backend

Move into the backend directory:

```powershell
cd backend
```

Activate the Python virtual environment:

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
│   ├── accounts/
│   ├── ai_services/
│   ├── careers/
│   ├── docs/
│   ├── documents/
│   ├── gradnavi/
│   ├── interviews/
│   ├── profiles/
│   ├── .env.example
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .oxlintrc.json
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── 01-project-overview.md
│   ├── 02-team-members-and-roles.md
│   │
│   ├── requirements/
│   │   ├── functional-requirements.md
│   │   ├── non-functional-requirements.md
│   │   └── requirements-assignment-matrix.md
│   │
│   ├── project-management/
│   │   ├── contribution-log.md
│   │   ├── product-backlog.md
│   │   ├── quality-plan.md
│   │   ├── responsibility-matrix.md
│   │   ├── risk-register.md
│   │   ├── roadmap-and-milestones.md
│   │   ├── task-leads.md
│   │   ├── work-breakdown-structure.md
│   │   └── GradNavi_Final_Project_Plan.mpp
│   │
│   ├── system-design/
│   │   ├── ai-prompt-safety-design.md
│   │   ├── career-skill-reference-data-design.md
│   │   ├── readiness_scoring_design.md
│   │   ├── recommendation-scoring-design.md
│   │   ├── rest-api-design.md
│   │   ├── security-architecture.md
│   │   ├── sprint-1-integration-plan.md
│   │   ├── sprint-2-integration-plan.md
│   │   ├── sprint-3-integration-plan.md
│   │   ├── student-profile-api-model-mapping.md
│   │   └── student-profile-data-design.md
│   │
│   └── testing/
│       ├── sprint-1-test-plan.md
│       ├── sprint-1-test-cases.xlsx
│       ├── sprint-2-test-plan.md
│       ├── sprint-2-test-cases.xlsx
│       ├── sprint-3-test-plan.md
│       ├── sprint-3-test-cases.xlsx
│       └── evidence/
│
├── .gitignore
└── README.md
```

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

The repository is an active project workspace.

Requirements, diagrams, task ownership, architecture decisions, database design, Sprint planning, testing evidence, deployment records, and assessment documents should stay aligned with the latest approved project baseline.

The Microsoft Project schedule remains the authoritative planning source for Sprint dates, task dependencies, ownership, and milestones.
