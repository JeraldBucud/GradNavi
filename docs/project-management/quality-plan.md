# Quality Plan

Status: Working baseline

## Quality objectives

| Area | Objective |
|---|---|
| Functional correctness | Approved requirements meet their acceptance criteria |
| Usability | Students complete the main flows without specialist training |
| Responsive design | Core pages work across desktop, tablet, and mobile widths |
| Performance | Normal non-AI API responses target two seconds under expected classroom use |
| Security | Protected functions require authenticated and authorised access |
| Privacy | GradNavi stores and sends only the information required for each function |
| Reliable scoring | The same structured inputs produce the same recommendation and readiness scores |
| Explainability | Results show contributing factors, scores, gaps, and explanations |
| Accessibility | Forms support labels, keyboard access, readable contrast, and useful errors |
| Maintainability | Code follows agreed structure, conventions, review, and setup documentation |
| Data quality | Career, skill, qualification, and learning records include source and review details |
| AI quality | AI output follows approved structure, passes validation, and remains editable |
| Recoverability | The team documents database export, restoration, and fallback steps |

## Quality assurance activities

| Activity | Practice | Timing |
|---|---|---|
| Requirements review | Check clarity, feasibility, testability, and acceptance criteria | Before backlog approval |
| Scope review | Check alignment between objectives, scope, requirements, roadmap, and resources | Before Sprint 1 and after approved changes |
| Architecture review | Review frontend, backend, database, authentication, AI, and deployment boundaries | Before dependent development |
| Interface review | Review navigation, forms, responsiveness, accessibility, and error messages | During design and each Sprint |
| Pull-request control | Use branches and peer review before merge | For each change |
| Dependency control | Record package versions and setup steps | During setup and updates |
| Continuous testing | Run automated and recorded manual tests | During every Sprint |
| Defect management | Record severity, owner, status, evidence, fix, and retest | From Sprint 1 |
| AI review | Review prompts, privacy filtering, structured output, unsupported claims, and fallback behaviour | During AI development |
| Release review | Review regression, security, privacy, deployment, recovery, documentation, and demonstration readiness | Finalisation |
| Document review | Check terminology, references, versions, formatting, and consistency | Before submission |

## Testing levels

- Unit testing
- Frontend component testing
- API testing
- Permission testing
- Integration testing
- System testing
- Security and privacy testing
- AI quality testing
- Usability testing
- Accessibility testing
- User acceptance testing
- Deployment smoke testing

## Definition of Done

A feature is complete when:

1. Approved acceptance criteria are met.
2. Changes pass review and merge through the agreed workflow.
3. Automated tests or recorded manual tests pass.
4. No unresolved Critical defect affects the feature.
5. Authentication, permissions, privacy, validation, audit needs, and error handling are checked.
6. AI-supported output passes structure, limitation, privacy, and fallback checks.
7. Relevant documentation is updated.
8. The feature works inside the integrated application.
9. The team accepts the result during Sprint review.

## Release conditions

- Priority student and administrator flows pass.
- No Critical release defect remains open.
- Authentication, permissions, privacy, and secret-management checks pass.
- Scoring repeatability checks pass.
- AI validation and fallback checks pass.
- Data sources and limitations are recorded.
- Major usability barriers are corrected.
- Deployment smoke tests pass.
- Recovery and fallback instructions are available.
- Report, setup, testing, contribution, and presentation evidence is complete.
