# Sprint 5 Deployment Security Evidence Register

Status: Six PNG screenshots uploaded and verified on GitHub; case-level acceptance and workbook reconciliation pending.
Date: Screenshot evidence supplied 14 October 2026 (Brisbane local date).
Scope: S5-SEC-DEP-01 and S5-SEC-DEP-02 under WBS 8.3.

## S5-SEC-DEP-01: Railway Django deployment configuration

| File prepared for upload | Observation supported by screenshot |
| --- | --- |
| `S5-SEC-DEP-01A-railway-variable-names-masked.png` | Names of DEBUG, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS, SECRET_KEY, DB_PASSWORD and OPENAI_API_KEY are present; values masked |
| `S5-SEC-DEP-01B-https-unauthenticated-401.png` | HTTPS GET to Railway `/api/v1/auth/me/` returned HTTP 401 with controlled `not_authenticated` JSON |
| `S5-SEC-DEP-01C-approved-origin-cors.png` | Approved `https://gradnavi.site` Origin received a matching Access-Control-Allow-Origin header |
| `S5-SEC-DEP-01D-unapproved-origin-cors-rejected.png` | Unapproved Origin `https://not-approved.example` was not granted Access-Control-Allow-Origin |

Boundaries: Masked variables do **not** prove their actual values. This evidence does not independently verify production DEBUG=False, the full ALLOWED_HOSTS list, HTTPS redirection, all error cases or full secrets protection.

## S5-SEC-DEP-02: Vercel to Railway connection

| File prepared for upload | Observation supported by screenshot |
| --- | --- |
| `S5-SEC-DEP-02A-vercel-public-api-base-url.png` | Production Vercel `VITE_API_BASE_URL` is configured to the Railway HTTPS API at `https://gradnavi-backend-production.up.railway.app/api/v1` |
| `S5-SEC-DEP-02B-production-api-https-200-cropped.png` | Authenticated production browser request to Railway API over HTTPS returned HTTP 200 and a matching allow-origin header for `https://www.gradnavi.site` |

The latter screenshot has been cropped to exclude account emails visible in the original Admin Dashboard screenshot.

Boundaries: Successful HTTPS traffic and visible frontend configuration do **not** independently establish absence of sensitive values in every downloaded JavaScript bundle, API response or production log. Existing repository secret-scan evidence is separate.

## Outcome and submission rule

The approved WBS 8.3 record has 30 locally executed PASS cases and two deployment checks later reported PASS by the project lead. These images support specified observable subchecks only. Do not convert the project-lead report into a claim of full independent verification.

All six PNG files are committed to this closeout branch in commit `070bbb8` (14 October 2026). Each file is available in the same folder as this index. Their presence supports the described observable checks only. Formal case-level reconciliation and full deployment configuration verification are separate.

Avoid committing tokens, passwords, environment-variable values, real account emails or unredacted session headers.

Source records:
- `docs/testing/sprint-5-security-permission-test-plan.md`
- `docs/testing/sprint-5-security-permission-execution-matrix.md`
- `docs/project-management/sprint-5-closeout.md`
