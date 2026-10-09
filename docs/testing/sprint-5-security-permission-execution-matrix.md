# GradNavi Sprint 5 Security and Permission Execution Matrix

Status: COMPLETE

WBS: 8.3 Security and Permission Testing

Owner: Jerald

Related plan:

`docs/testing/sprint-5-security-permission-test-plan.md`

## 1. Purpose

This matrix maps every approved WBS 8.3 security test case to the strongest available evidence method.

Existing automated tests are reused where they already verify the approved security expectation.

Postman is used as client-facing REST API evidence where direct API behaviour should also be demonstrated.

Postman does not replace existing automated tests.

Tests are not duplicated solely to increase the test count.

## 2. Execution Method Summary

Total WBS 8.3 test cases: 32

Execution groups:

- POSTMAN + AUTOMATED: 21
- AUTOMATED + STATIC: 6
- REPOSITORY REVIEW: 2
- BROWSER / INTEGRATION: 1
- DEPLOYMENT REVIEW: 2

Final execution state:

- Local executable cases completed: 30
- Pass: 30
- Fail: 0
- Not Run: 0
- Blocked: 0
- Deferred to deployment: 2
- Confirmed WBS 8.3 security defects: 0

## 3. Postman Test Identities

Postman API testing should use three security states.

### Unauthenticated

No Authorization header.

### Student

Authenticated GradNavi Student account.

The existing manual Student test account may be used.

Do not store its password, access token, or refresh token in retained screenshots or committed evidence.

### Administrator

Authenticated GradNavi Administrator test account.

Use a dedicated test Administrator identity.

Do not use a real production or personal Administrator credential in committed test evidence.

## 4. Authentication Matrix

| ID | Evidence method | Existing automated coverage | Postman action |
| --- | --- | --- | --- |
| S5-SEC-AUTH-01 | POSTMAN + AUTOMATED | `LoginAPITests.test_successful_login_returns_tokens_and_safe_user_information`; `LoginAPITests.test_successful_login_issues_valid_jwt_tokens` | POST `/api/v1/auth/login/` with valid Student credentials. Verify success, access token, refresh token, and safe user fields. |
| S5-SEC-AUTH-02 | POSTMAN + AUTOMATED | `LoginAPITests.test_wrong_password_is_rejected_with_safe_error`; `LoginAPITests.test_nonexistent_email_is_rejected_with_same_safe_error`; `LoginAPITests.test_wrong_password_and_nonexistent_email_return_same_error` | Submit one wrong-password login and one unknown-email login. Verify both return the same safe authentication error. |
| S5-SEC-AUTH-03 | POSTMAN + AUTOMATED | `CurrentUserAPITests.test_missing_authorization_header_is_rejected`; `CurrentUserAPITests.test_malformed_token_is_rejected`; `CurrentUserAPITests.test_refresh_token_cannot_authenticate_current_user_endpoint` | Call `/api/v1/auth/me/` with no token, malformed token, and refresh token used as Bearer authentication. Verify rejection. |
| S5-SEC-AUTH-04 | POSTMAN + AUTOMATED | `TokenRefreshAPITests.test_valid_refresh_token_succeeds_and_returns_rotated_tokens`; `TokenRefreshAPITests.test_original_refresh_token_cannot_be_reused_after_rotation`; `TokenRefreshAPITests.test_new_rotated_refresh_token_can_be_used_for_another_refresh` | Refresh a valid session. Verify rotated tokens. Reuse the old refresh token and verify rejection. Verify the new refresh token works. |
| S5-SEC-AUTH-05 | POSTMAN + AUTOMATED | `LogoutAPITests.test_successful_logout_blacklists_submitted_refresh_token`; `LogoutAPITests.test_existing_access_token_remains_usable_until_expiry_after_logout` | Logout using the refresh token. Verify the blacklisted refresh token no longer refreshes. Record the documented access-token behaviour. |
| S5-SEC-AUTH-06 | POSTMAN + AUTOMATED | `PasswordResetAPITests.test_unknown_email_request_returns_same_safe_response_and_sends_no_email`; `PasswordResetAPITests.test_reset_request_response_does_not_expose_uid_or_token`; `PasswordChangeAPITests.test_valid_password_change_succeeds`; `PasswordChangeAPITests.test_incorrect_current_password_is_rejected`; `PasswordChangeAPITests.test_weak_new_password_is_rejected` | Verify password-reset request response safety. Verify password change rejects incorrect current password and weak or mismatched new passwords. |

## 5. Role and Administrator Permission Matrix

| ID | Evidence method | Existing automated coverage | Postman action |
| --- | --- | --- | --- |
| S5-SEC-RBAC-01 | POSTMAN + AUTOMATED | `AdministrationPermissionTests.test_unauthenticated_users_cannot_access_admin_endpoints`; `AdministrationPermissionTests.test_non_admins_cannot_access_admin_detail_endpoints` | Call Administrator list and detail endpoints without authentication. Verify 401. |
| S5-SEC-RBAC-02 | POSTMAN + AUTOMATED | `AdministrationPermissionTests.test_students_cannot_access_admin_endpoints`; `AdministrationPermissionTests.test_non_admins_cannot_access_admin_detail_endpoints` | Call Administrator list and detail endpoints using a Student token. Verify 403. |
| S5-SEC-RBAC-03 | POSTMAN + AUTOMATED | `AdministrationPermissionTests.test_student_cannot_create_career`; `AdminUserRoleStatusAuditTests.test_student_cannot_change_role_or_status`; `AdminLearningResourceReportReviewTests.test_student_cannot_access_report_detail_or_update` | Attempt Administrator create, role-change, status-change, report-review, analytics, and audit operations using a Student token. Verify rejection. |
| S5-SEC-RBAC-04 | POSTMAN + AUTOMATED | `AdminUserManagementTests.test_admin_cannot_change_role_or_active_status` | PATCH the general Administrator user-detail endpoint with `role` or `is_active`. Verify those protected fields are not changed. |
| S5-SEC-RBAC-05 | POSTMAN + AUTOMATED | `AdminUserRoleStatusAuditTests.test_admin_can_change_user_role_through_dedicated_endpoint`; `AdminUserRoleStatusAuditTests.test_admin_can_change_user_active_status_through_dedicated_endpoint`; `AdminUserRoleStatusAuditTests.test_invalid_role_change_is_rejected` | Use the dedicated Administrator role and account-status endpoints. Verify valid changes work and invalid role values are rejected. |
| S5-SEC-RBAC-06 | POSTMAN + AUTOMATED | `AdminAuditRecordTests.test_admin_can_list_and_retrieve_audit_records`; `AdminAuditRecordTests.test_audit_records_endpoint_is_read_only`; `AdminAuditRecordTests.test_audit_response_does_not_expose_user_email`; `AdminAnalyticsTests.test_analytics_response_exposes_no_student_data` | As Administrator, retrieve audit and analytics data. Verify audit modification is rejected and unnecessary Student information is absent. |

## 6. Student Ownership Matrix

| ID | Evidence method | Existing automated coverage | Postman or review action |
| --- | --- | --- | --- |
| S5-SEC-OWN-01 | POSTMAN + AUTOMATED | `StudentProfileReadAPITests.test_get_uses_authenticated_user_and_does_not_leak_cross_user_data` | Authenticate as Student A. GET the Student Profile. Verify only Student A data is returned. Repeat using Student B where available. |
| S5-SEC-OWN-02 | POSTMAN + AUTOMATED | `StudentProfilePatchAPITests.test_client_supplied_ownership_identifiers_are_rejected`; `StudentProfilePatchAPITests.test_cross_user_nested_id_is_rejected_without_modifying_other_profile`; `StudentProfilePatchAPITests.test_authenticated_user_cannot_patch_another_profile_with_query_parameters` | Attempt ownership spoofing using identifiers, another Student nested record ID, and query parameters. Verify rejection and no cross-user modification. |
| S5-SEC-OWN-03 | AUTOMATED + STATIC | `RecommendationAPITests.test_authenticated_user_profile_is_used_exclusively`; `LearningRoadmapAPITests.test_student_profile_is_derived_from_request_user` | Review recommendation, learning-resource, and roadmap endpoints to confirm authenticated-user context drives Student data selection. |
| S5-SEC-OWN-04 | POSTMAN + AUTOMATED | `JobDescriptionMatchAPITests.test_authenticated_profile_ownership` | Submit Job Description Matching as a Student and verify the backend uses the authenticated Student Profile without accepting another profile identity. |
| S5-SEC-OWN-05 | POSTMAN + AUTOMATED | `ResumeGenerationAPITests.test_authenticated_user_profile_is_used_exclusively`; `CoverLetterGenerationAPITests.test_authenticated_user_profile_is_used_exclusively`; `CoverLetterGenerationAPITests.test_client_cannot_select_another_student_profile`; `CoverLetterGenerationAPITests.test_student_profile_id_is_rejected` | Attempt Resume or Cover Letter generation with another profile identifier or protected profile-selection field. Verify rejection or authenticated-profile enforcement. |
| S5-SEC-OWN-06 | POSTMAN + AUTOMATED | `InterviewHistoryAPITests.test_post_creates_owned_session_metadata`; `InterviewHistoryAPITests.test_get_returns_only_authenticated_user_history`; `InterviewHistoryAPITests.test_user_id_is_rejected` | Create Interview History as Student A. Verify Student A sees it. Verify client-supplied ownership is rejected and Student B does not receive Student A history. |

## 7. Input Protection Matrix

| ID | Evidence method | Existing automated coverage | Postman action |
| --- | --- | --- | --- |
| S5-SEC-IN-01 | POSTMAN + AUTOMATED | `RegistrationAPITests.test_public_registration_cannot_create_privileged_user`; `AccountSettingsAPITests.test_email_and_role_are_read_only`; `CoverLetterGenerationAPITests.test_user_id_is_rejected`; `CoverLetterGenerationAPITests.test_profile_prompt_and_system_prompt_fields_are_rejected`; `InterviewRequestSerializerTests.test_question_request_rejects_user_id`; `InterviewRequestSerializerTests.test_question_request_rejects_client_prompt` | Submit protected fields such as role, user ID, Student Profile ID, profile prompt, or system prompt where prohibited. Verify server control is preserved. |
| S5-SEC-IN-02 | POSTMAN + AUTOMATED | `AdminUserRoleStatusAuditTests.test_invalid_role_change_is_rejected`; `AccountSettingsAPITests.test_gif_profile_photo_is_rejected`; `AccountSettingsAPITests.test_profile_photo_over_five_mb_is_rejected`; `StudentProfilePatchAPITests.test_invalid_proficiency_and_missing_reference_are_rejected`; `JobDescriptionMatchAPITests.test_unknown_fields_rejected` | Submit invalid role, invalid IDs or references, unsupported fields, and invalid upload/input values. Verify controlled validation errors. |

## 8. AI Privacy and Trust Matrix

| ID | Evidence method | Existing automated coverage | Review action |
| --- | --- | --- | --- |
| S5-SEC-AI-01 | AUTOMATED + STATIC | `ResumeGenerationServiceTests.test_approved_profile_context_reaches_provider_through_privacy_mapper`; `CoverLetterGenerationServiceTests.test_approved_profile_context_reaches_provider_through_privacy_mapper` | Review `AI_PROFILE_ALLOWLIST` and confirm only approved Student Profile areas enter AI context. |
| S5-SEC-AI-02 | AUTOMATED + STATIC | `ResumeGenerationServiceTests.test_private_profile_fields_are_not_exposed_to_provider_prompt`; `CoverLetterGenerationServiceTests.test_private_profile_fields_are_not_exposed_to_provider_prompt` | Verify the privacy mapper excludes IDs, email, role, password data, JWT data, interests, personality responses, project URLs, timestamps, and internal identifiers. |
| S5-SEC-AI-03 | AUTOMATED + STATIC | `ResumeGenerationAPITests.test_shared_ai_service_failure_returns_503`; `ResumeGenerationAPITests.test_response_validation_failure_is_sanitized_503`; `CoverLetterGenerationAPITests.test_provider_unavailable_returns_503`; `InterviewQuestionAPITests.test_provider_timeout_returns_503`; `InterviewQuestionAPITests.test_semantic_validation_failure_returns_controlled_502`; `InterviewFeedbackAPITests.test_provider_timeout_returns_503` | Use deterministic automated provider-failure tests. Review returned errors for secret, stack-trace, prompt, or credential leakage. |
| S5-SEC-AI-04 | AUTOMATED + STATIC | `CoverLetterGenerationServiceTests.test_job_description_instructions_do_not_become_trusted_instructions`; `InterviewQuestionServiceTests.test_question_context_preserves_trust_boundary`; `InterviewFeedbackServiceTests.test_feedback_context_is_untrusted`; `JobDescriptionMatchAPITests.test_job_matching_output_is_independent_of_text_ai_provider` | Review prompt trust boundaries and confirm AI output does not become the authorization authority or replace deterministic matching and scoring behaviour. |

## 9. Audit and Error Protection Matrix

| ID | Evidence method | Existing automated coverage | Postman or review action |
| --- | --- | --- | --- |
| S5-SEC-AUD-01 | POSTMAN + AUTOMATED | `AdminAuditRecordTests.test_career_create_update_and_delete_create_audit_records`; `AdminAuditRecordTests.test_learning_resource_report_status_change_creates_audit_record` | Perform an approved Administrator mutation, then retrieve audit records and verify the expected action is recorded. |
| S5-SEC-AUD-02 | POSTMAN + AUTOMATED | `AdminAuditRecordTests.test_admin_can_list_and_retrieve_audit_records`; `AdminAuditRecordTests.test_audit_records_endpoint_is_read_only`; `AdminAuditRecordTests.test_audit_response_does_not_expose_user_email` | Verify Administrator read access, Student denial, read-only behaviour, and safe audit response fields. |
| S5-SEC-AUD-03 | AUTOMATED + STATIC | `ResumeGenerationAPITests.test_external_service_failure_creates_safe_system_audit_record`; `InterviewQuestionAPITests.test_semantic_validation_failure_logs_safe_category`; `InterviewFeedbackAPITests.test_feedback_validation_failure_logs_safe_category` | Review audit metadata validation and controlled exception handling. Verify passwords, tokens, secrets, credentials, generated Student content, stack traces, and internal paths are not intentionally exposed. |

## 10. Secret Protection Matrix

| ID | Evidence method | Existing automated coverage | Repository review |
| --- | --- | --- | --- |
| S5-SEC-SECRET-01 | REPOSITORY REVIEW | No single automated test currently proves repository-wide secret absence | Review tracked files and source for `.env`, database passwords, API keys, JWT signing secrets, real tokens, and credentials. Do not print secret values if any are found. |
| S5-SEC-SECRET-02 | REPOSITORY REVIEW | No single automated test currently proves frontend-wide secret absence | Review frontend source and browser-facing configuration for backend secrets, AI API keys, database credentials, Django secrets, or administration credentials. |

## 11. Frontend Permission Matrix

| ID | Evidence method | Existing automated coverage | Current action | Status |
| --- | --- | --- | --- | --- |
| S5-SEC-FE-01 | BROWSER / INTEGRATION | Backend role permission tests already exist and the integrated Administrator frontend routes are now present | Verify unauthenticated, Student, and Administrator browser access to Administrator routes | Pass |

WBS 7.7 is integrated.

Manual browser verification passed:

- Unauthenticated access to `/admin` and `/admin/users` redirected to `/login`.
- Authenticated Student access to Administrator routes redirected to `/profile`.
- Authenticated Administrator access to `/admin` and `/admin/users` succeeded.

The result is recorded in the Sprint 5 security-permission test-case workbook. No screenshot was retained.

## 12. Deployment Security Matrix

| ID | Evidence method | Current action | Status |
| --- | --- | --- | --- |
| S5-SEC-DEP-01 | DEPLOYMENT REVIEW | Verify deployed Debug, Allowed Hosts, CORS, HTTPS, environment secrets, and controlled production errors during WBS 8.7 to WBS 8.9 | Deferred |
| S5-SEC-DEP-02 | DEPLOYMENT REVIEW | Verify deployed frontend and backend expose no protected secrets and use approved production communication paths | Deferred |

The current local backend configuration is a development baseline and is not treated as the final deployed configuration.

## 13. Postman Execution Count

Postman-assisted WBS 8.3 cases: 21

Postman cases:

- S5-SEC-AUTH-01
- S5-SEC-AUTH-02
- S5-SEC-AUTH-03
- S5-SEC-AUTH-04
- S5-SEC-AUTH-05
- S5-SEC-AUTH-06
- S5-SEC-RBAC-01
- S5-SEC-RBAC-02
- S5-SEC-RBAC-03
- S5-SEC-RBAC-04
- S5-SEC-RBAC-05
- S5-SEC-RBAC-06
- S5-SEC-OWN-01
- S5-SEC-OWN-02
- S5-SEC-OWN-04
- S5-SEC-OWN-05
- S5-SEC-OWN-06
- S5-SEC-IN-01
- S5-SEC-IN-02
- S5-SEC-AUD-01
- S5-SEC-AUD-02

Postman evidence should supplement automated test evidence.

## 14. Automated and Static Execution Count

Automated plus static-review cases: 6

Cases:

- S5-SEC-OWN-03
- S5-SEC-AI-01
- S5-SEC-AI-02
- S5-SEC-AI-03
- S5-SEC-AI-04
- S5-SEC-AUD-03

## 15. Repository Review Count

Repository-review cases: 2

Cases:

- S5-SEC-SECRET-01
- S5-SEC-SECRET-02

## 16. Evidence Requirements

For automated tests, retain:

- Command used.
- Test suite or targeted test label.
- Number of tests run.
- Pass or Fail result.
- Relevant failure output where applicable.

For Postman tests, retain:

- Test-case ID.
- HTTP method.
- Endpoint.
- Authentication state.
- Sanitised request body where required.
- Expected HTTP status.
- Actual HTTP status.
- Expected security behaviour.
- Actual security behaviour.
- Pass or Fail.
- Screenshot or exported result where required.

Do not preserve real access tokens, refresh tokens, passwords, reset tokens, API keys, or database credentials in screenshots.

For static and repository review, retain:

- Files or commands reviewed.
- Security expectation.
- Result.
- Evidence reference.
- No real secret values.

## 17. Recommended Execution Order

Execute in this order:

1. Existing automated security regression.
2. Repository secret review.
3. Postman authentication tests.
4. Postman Administrator permission tests.
5. Postman Student ownership tests.
6. Postman input-protection tests.
7. Postman audit tests.
8. AI privacy and trust review.
9. WBS 7.7 frontend permission test after integration.
10. Deployment security review during deployment and production verification.

This order uses automated tests first to identify implementation failures before manual API evidence is collected.

## 18. Result Rule

An existing automated test passing does not automatically mark the matching WBS 8.3 case Pass until all evidence methods required by this matrix are complete.

For a `POSTMAN + AUTOMATED` case:

- Automated evidence must pass.
- Postman evidence must pass.

For an `AUTOMATED + STATIC` case:

- Automated evidence must pass.
- Static review must pass.

For a `REPOSITORY REVIEW` case:

- Repository review must pass.

For a Blocked case:

- Record the dependency.
- Do not mark Fail solely because the dependency is unfinished.

For a Deferred case:

- Record the later WBS stage.
- Do not mark Pass or Fail before execution.

## 19. Final Execution State

WBS 8.3 local security and permission testing is complete for every currently executable case.

Final totals:

- Total: 32
- Pass: 30
- Fail: 0
- Not Run: 0
- Blocked: 0
- Deferred: 2

Final case state:

| Area | Cases | Final result |
| --- | --- | --- |
| Authentication | S5-SEC-AUTH-01 to S5-SEC-AUTH-06 | Pass |
| Role and Administrator Permission | S5-SEC-RBAC-01 to S5-SEC-RBAC-06 | Pass |
| Student Ownership | S5-SEC-OWN-01 to S5-SEC-OWN-06 | Pass |
| Input Protection | S5-SEC-IN-01 to S5-SEC-IN-02 | Pass |
| AI Privacy and Trust | S5-SEC-AI-01 to S5-SEC-AI-04 | Pass |
| Audit and Error Protection | S5-SEC-AUD-01 to S5-SEC-AUD-03 | Pass |
| Secret Protection | S5-SEC-SECRET-01 to S5-SEC-SECRET-02 | Pass |
| Frontend Permission | S5-SEC-FE-01 | Pass |
| Deployment Security | S5-SEC-DEP-01 to S5-SEC-DEP-02 | Deferred to WBS 8.7 to WBS 8.9 |

Confirmed WBS 8.3 security defects: 0

S5-SEC-FE-01 passed after WBS 7.7 integration.

The two Deferred deployment cases remain outside the completed local test scope and continue during deployment and production verification.

## 20. Final Evidence References

Detailed case results, evidence references, and execution records are maintained in:

- `sprint-5-security-permission-test-cases.xlsx`
- `wbs-8.3-security-evidence-screenshots-final.zip`
- `wbs-8.3-security-testing-final-package.zip`

Representative final evidence includes:

- Automated and Postman authentication evidence for S5-SEC-AUTH-01 to S5-SEC-AUTH-06.
- Administrator permission evidence for S5-SEC-RBAC-01 to S5-SEC-RBAC-06.
- Student ownership and isolation evidence for S5-SEC-OWN-01 to S5-SEC-OWN-06.
- Input-protection evidence for S5-SEC-IN-01 and S5-SEC-IN-02.
- AI privacy, failure-handling, and trust-boundary evidence for S5-SEC-AI-01 to S5-SEC-AI-04.
- Audit creation, access, read-only behaviour, and safe-error evidence for S5-SEC-AUD-01 to S5-SEC-AUD-03.
- Backend and frontend repository secret-review evidence for S5-SEC-SECRET-01 and S5-SEC-SECRET-02.
- Temporary WBS 8.3 test data cleanup verification.
- S5-SEC-FE-01 manual browser permission verification recorded in `sprint-5-security-permission-test-cases.xlsx`. No screenshot was retained.

Security evidence was retained without real passwords, access tokens, refresh tokens, API keys, database credentials, or Django secret values.
