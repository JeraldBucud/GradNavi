# GradNavi

GradNavi is an AI-Powered Career Guidance System for students.

The planned responsive web application will analyse a student's skills, interests, education, experience, projects, and career goals. It will provide ranked career recommendations, readiness scores, skill-gap analysis, learning suggestions, career roadmaps, employment-preparation tools, and basic administration functions.

## Project overview

GradNavi uses a structured student profile containing skills, education, interests, experience, projects, and career goals.

The planned system includes:

- Secure student and administrator authentication
- Student profile management
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

Numerical recommendation and readiness scores are intended to come from documented rule-based logic. Generative AI supports explanations and editable text rather than independently determining numerical scores.

## Repository purpose

This repository stores the GradNavi capstone project baseline and implementation work.

The repository currently includes:

- Assessment 1 group project proposal
- Project overview and team documentation
- Functional and non-functional requirements
- Requirement assignment records
- Work Breakdown Structure and product backlog
- Risk and quality planning
- Responsibility and task-lead records
- Delivery planning and Microsoft Project schedule
- System architecture diagram
- Entity Relationship diagram
- Use case diagram
- Context diagram
- Initial Django backend scaffold
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

## Planning images

- [Delivery Roadmap](docs/project-management/images/delivery-roadmap.png)
- [Risk Matrix](docs/project-management/images/risk-matrix.png)

## System actors and external entities

The current GradNavi requirements identify the following main system actors and external entities:

| Actor or entity | Role |
|---|---|
| Student | Maintains a profile, receives career guidance, analyses skill gaps, prepares application material, practises interviews, and tracks progress |
| System Administrator | Manages users, careers, skills, learning resources, reports, audit records, and reference data |
| OpenAI API | Provides structured explanations and editable generated content through the Django backend |
| Public Career and Learning Sources | Supply reference information that is reviewed before being entered into GradNavi |

Career Adviser access is outside the current V1 scope.

## High-level student use cases

The current project proposal identifies these student use cases:

1. Register and authenticate
2. Manage student profile
3. Receive career recommendations
4. View recommendation scores and explanations
5. Perform skill-gap analysis
6. View career-readiness score
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

## Planned technology stack

| Area | Technology |
|---|---|
| Frontend | React, JavaScript, Vite, Material UI |
| Backend | Python, Django, Django REST Framework |
| Database | PostgreSQL |
| Artificial intelligence | OpenAI API through the Django backend |
| Planning | Scrum, GitHub Projects, Microsoft Project |
| Communication | Microsoft Teams |
| Deployment | Vercel, Railway, Railway PostgreSQL |

## Current implementation status

The repository includes an initial Django backend scaffold under `backend/`.

The current backend is an early development foundation. The planned application database is PostgreSQL. Frontend implementation, full PostgreSQL integration, API integration, AI integration, deployment configuration, and detailed implementation test evidence will be added as development progresses.

## Delivery planning

GradNavi uses iterative Scrum delivery followed by a finalisation and release period.

The detailed task-level schedule, dependencies, resources, milestones, and Gantt planning are stored in:

- [GradNavi Final Microsoft Project Plan](docs/project-management/GradNavi_Final_Project_Plan.mpp)
- [Roadmap and Milestones](docs/project-management/roadmap-and-milestones.md)
- [Work Breakdown Structure](docs/project-management/work-breakdown-structure.md)
- [Product Backlog](docs/project-management/product-backlog.md)

The Microsoft Project schedule and the formal assessment report should be kept aligned whenever sprint dates, milestones, or task dependencies change.

## Repository structure

```text
GradNavi/
├── backend/
│   ├── gradnavi/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── manage.py
├── docs/
│   ├── 01-project-overview.md
│   ├── 02-team-members-and-roles.md
│   ├── requirements/
│   │   ├── functional-requirements.md
│   │   ├── non-functional-requirements.md
│   │   └── requirements-assignment-matrix.md
│   └── project-management/
│       ├── COIT20273 Assessment 1.docx
│       ├── Context Diagram GradNavi.drawio.png
│       ├── GradNavi architecture diagram.png
│       ├── GradNavi_Final_Project_Plan.mpp
│       ├── GrandNavi ER diagram.png
│       ├── Use Case GradNavi.drawio.png
│       ├── communication-plan.md
│       ├── contribution-log.md
│       ├── leadership-rotation.md
│       ├── meeting-minutes-template.md
│       ├── product-backlog.md
│       ├── quality-plan.md
│       ├── responsibility-matrix.md
│       ├── risk-register.md
│       ├── roadmap-and-milestones.md
│       ├── task-leads.md
│       ├── tools-and-resources.md
│       ├── work-breakdown-structure.md
│       └── images/
│           ├── delivery-roadmap.png
│           └── risk-matrix.png
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

Career guidance generated by GradNavi provides decision support. Students review AI-generated material before saving or using it.

## Document status

The repository is an active project workspace.

Requirements, diagrams, task ownership, architecture decisions, database design, sprint planning, testing evidence, deployment records, and assessment documents should stay aligned with the latest approved project baseline.

