# Non-Functional Requirements

Status: Draft for team review

| ID | Quality area | Requirement | Status |
|---|---|---|---|
| NFR-01 | Usability | A student shall complete the main recommendation flow without specialist training. | Draft for approval |
| NFR-02 | Responsive design | Core pages shall work on current desktop, tablet, and mobile browser widths. | Draft for approval |
| NFR-03 | Performance | Normal non-AI API responses should complete within 2 seconds under expected classroom use. AI responses should show a loading state and use a configured timeout. | Draft for approval |
| NFR-04 | Availability | The deployed demonstration system should be accessible during planned assessment demonstrations, excluding planned maintenance and third-party outages. | Draft for approval |
| NFR-05 | Security | Passwords shall use Django authentication. Protected endpoints shall require authenticated and authorised access. | Draft for approval |
| NFR-06 | Privacy | The system shall collect minimum required personal data and shall not expose one student's records to another user. | Draft for approval |
| NFR-07 | Maintainability | The codebase shall use modular components, coding standards, version control, and documented setup steps. | Draft for approval |
| NFR-08 | Reliability | Scoring functions shall produce repeatable results for the same structured inputs. | Draft for approval |
| NFR-09 | Explainability | Recommendation and readiness scores shall show the factors used in the calculation. | Draft for approval |
| NFR-10 | Accessibility | Forms shall use labels, keyboard access, readable contrast, and meaningful validation messages. | Draft for approval |
| NFR-11 | Compatibility | The application shall support current versions of Chrome, Edge, and Firefox. | Draft for approval |
| NFR-12 | Testability | Priority functions shall have acceptance tests and automated tests where practical. | Draft for approval |
| NFR-13 | Scalability | The design shall separate frontend, backend, database, and AI services so each area can be extended. | Draft for approval |
| NFR-14 | Ethical AI | Generated outputs shall include limitations and shall avoid protected attributes as direct scoring factors. | Draft for approval |
| NFR-15 | Recoverability | Database backup or export procedures shall be documented for the demonstration environment. | Draft for approval |

## Evidence expectations

| Quality area | Planned evidence |
|---|---|
| Usability | Task observations and user-acceptance feedback |
| Responsive design | Screenshots and browser-width checks |
| Performance | API timing records and timeout tests |
| Availability | Deployment smoke-test record |
| Security | Authentication, role, object-permission, and secret-management tests |
| Privacy | Data-field review, access tests, and AI-request inspection |
| Maintainability | Repository structure, code review, and setup documentation |
| Reliability | Fixed-profile repeatability tests |
| Explainability | Score breakdown and interface review |
| Accessibility | Labels, keyboard, contrast, and validation checklist |
| Compatibility | Chrome, Edge, and Firefox test matrix |
| Testability | Acceptance criteria, test cases, and results |
| Scalability | Architecture review |
| Ethical AI | Fairness, limitation, validation, and fallback checks |
| Recoverability | Database export, restoration, and local fallback instructions |
