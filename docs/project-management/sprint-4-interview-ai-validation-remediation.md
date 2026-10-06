# Sprint 4 Interview AI Validation Remediation

Status: Resolved in branch, pending integration

Branch:

`jerald/fix-s4-interview-ai-validation`

Base:

`feature/sprint-4`

## Discovery

The issue was identified during integration review of WBS 6.7 Interview Preparation against the Sprint 4 OpenAI and AI-response-validation backend.

Live GPT-5-nano testing showed intermittent failures with the controlled validation response:

`The generated interview response could not be validated. Please try again.`

The issue affected both Interview Question generation and Interview Feedback.

## Root Causes

### 1. OpenAI output ceiling

The shared OpenAI text provider used:

`MAX_OUTPUT_TOKENS = 500`

This provided insufficient headroom for larger structured outputs.

A controlled live 10-question test later used 619 output tokens, confirming that a 500-token ceiling was too restrictive for the supported Interview Preparation flow.

The ceiling was increased to:

`MAX_OUTPUT_TOKENS = 8000`

The 8,000 value is a maximum per OpenAI request. It is not pre-consumed on every request.

### 2. Interview Question prompt and semantic-validator mismatch

The Interview Question prompt previously requested a non-empty question list and a focus-area list.

WBS 7.4 semantic validation required stricter behaviour:

- Exact requested question count.
- One meaningful focus area per question.
- No blank focus areas.
- No duplicate declared focus areas.
- No missing focus areas.
- No extra focus areas.
- Top-level focus areas must exactly match the distinct focus areas used by the generated questions.

The prompt was updated to state these requirements directly.

The WBS 7.4 validator was not weakened.

### 3. Interview Feedback numeric-grounding scope

The original feedback validator allowed generated numeric claims only when the same value appeared in the Student answer.

This could reject a legitimate value supplied by the interview question or target role.

Numeric grounding now checks:

- Target role.
- Interview question.
- Student answer.

A generated numeric value is still rejected when it appears in none of these supplied fields.

### 4. GPT-5-nano feedback-generation violations

Controlled live diagnostic testing confirmed that some failures were valid safety rejections rather than validator defects.

Observed examples included:

- Invented numeric values `30` and `500`.
- Placeholder value `X%`.

Another live run with a supplied `25%` value generated a valid grounded response.

This confirmed intermittent model-output behaviour.

The feedback validator remains active.

### 5. Feedback prompt hardening

The Interview Feedback prompt was strengthened so GPT-5-nano is explicitly instructed to:

- Use only supplied facts.
- Avoid introducing numeric values absent from supplied interview fields.
- Produce no numeric values when no supplied field contains one.
- Avoid invented, hypothetical, illustrative, benchmark, sample, or estimated metrics.
- Avoid placeholder metrics and template markers.
- Avoid numbered-list formatting in the suggested response.
- Put requests for missing detail in improvement guidance rather than inventing the missing detail.

Literal placeholder examples were removed from the prompt to reduce accidental model echoing.

### 6. Bounded semantic-validation retry

Interview Feedback now supports:

- Initial generation attempt: 1.
- Maximum automatic retry after semantic validation failure: 1.
- Maximum total generation attempts: 2.

The retry applies only when a generated Interview Feedback response fails semantic validation.

Provider failures such as provider timeout remain on the existing provider-error path.

If the second generated response also fails validation, the existing validation exception is raised.

## Safe Diagnostics

Safe validation categories were added for internal logging.

Examples include:

- `output_incomplete`
- `structured_output_invalid`
- `question_count_mismatch`
- `focus_area_mismatch`
- `feedback_placeholder`
- `feedback_unsupported_numeric_claim`

The frontend-facing controlled error contract remains unchanged.

Generated response content, Student answers, job descriptions, prompts, API keys, and other sensitive content are not included in these diagnostic warning messages.

## Automated Verification

Focused automated verification:

- OpenAI provider tests: 12 / 12 passed.
- AI prompt tests: 49 / 49 passed.
- Interview tests: 65 / 65 passed.

Full backend regression:

- 1007 / 1007 tests passed.
- Django system check passed.
- Applied migration check passed.
- `makemigrations --check --dry-run` reported no changes.
- Safe validation warning checks passed.
- No sensitive test markers appeared in validation warning output.

## Live GPT-5-nano Verification

Final controlled live smoke testing used synthetic data only.

Model:

`gpt-5-nano`

Configuration:

- Maximum output tokens: 8,000.
- Maximum Interview Feedback attempts: 2.

Final live results:

| Case | Result | Provider Attempts |
| --- | --- | ---: |
| Generate 1 Interview Question | Pass | 1 |
| Generate 5 Interview Questions | Pass | 1 |
| Generate 10 Interview Questions | Pass | 1 |
| Feedback without numeric context | Pass | 1 |
| Feedback with `5 years` in question | Pass | 1 |
| Feedback with `25%` in Student answer | Pass | 1 |

Final live result:

- Total cases: 6.
- Passed: 6.
- Failed: 0.
- Automatic feedback retries required: 0.

Token usage across the final six-case live run:

- Input tokens: 4,704.
- Output tokens: 2,065.
- Total tokens: 6,769.

## Final Verification Result

The original Interview Preparation validation issue was reproduced, diagnosed, corrected, and retested.

Question generation now supports the tested 1, 5, and 10-question flows.

Interview Feedback successfully handled:

- No numeric context.
- Numeric context supplied by the interview question.
- Numeric context supplied by the Student answer.

WBS 7.4 semantic validation remains enforced.

The branch is ready for final diff review and commit preparation.