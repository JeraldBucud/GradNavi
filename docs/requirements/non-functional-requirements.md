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

## WBS 8.12 Implementation Reconciliation

The `Draft for approval` labels remain the formal approval state from the requirements record.

WBS 8.12 records evidence separately and does not silently convert requirement approval status.

Current reconciliation findings:

- NFR-05 Security and NFR-06 Privacy have strong local evidence through WBS 8.3 security, permission, ownership, input-protection, secret, audit, and AI-security testing.
- NFR-07 Maintainability is directly supported by WBS 8.12 repository review, modular project structure, version control, and setup documentation.
- NFR-08 Reliability and NFR-09 Explainability are supported by deterministic scoring design and completed Sprint regression evidence.
- NFR-10 Accessibility and NFR-11 Compatibility have Sprint-level manual and browser evidence, with final Sprint 5 usability work still being closed.
- NFR-03 Performance is under final Sprint 5 review through WBS 8.4.
- NFR-04 Availability remains pending final deployment and WBS 8.9 production verification.
- NFR-15 Recoverability remains pending final WBS 8.7, WBS 8.9, and WBS 8.10 evidence.

Formal approval changes require a recorded team decision.

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
