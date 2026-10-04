"""
Interview preparation service layer for GradNavi.

WBS 6.6 provides two AI-assisted operations:

1. Interview question generation
2. Interview answer feedback

This service layer uses the provider-independent AIProvider contract
defined in WBS 6.2.

WBS 7.3 provides external AI provider integration.

WBS 7.4 adds semantic response validation before generated Interview
Question results leave this service layer.
"""

import re

from ai_services.exceptions import (
    AIResponseValidationError,
)
from ai_services.prompts.interview_feedback import (
    build_interview_feedback_prompt,
    build_interview_feedback_retry_prompt,
)
from ai_services.prompts.interview_questions import (
    build_interview_question_prompt,
)
from ai_services.providers.base import AIProvider
from ai_services.schemas.inputs import (
    DEFAULT_INTERVIEW_QUESTION_COUNT,
    InterviewFeedbackInput,
    InterviewQuestionInput,
)
from ai_services.schemas.outputs import (
    InterviewFeedback,
    InterviewQuestionSet,
)


INTERVIEW_FEEDBACK_PLACEHOLDER_PATTERNS = (
    re.compile(
        r"\b[XYN]\s*%",
        re.IGNORECASE,
    ),
    re.compile(
        (
            r"\b[XYN]\s+"
            r"(?:users?|customers?|clients?|people|"
            r"percent(?:age)?|hours?|days?|weeks?|"
            r"months?|years?)\b"
        ),
        re.IGNORECASE,
    ),
    re.compile(
        (
            r"\[(?:number|percentage|percent|metric|"
            r"result|value)\]"
        ),
        re.IGNORECASE,
    ),
    re.compile(
        (
            r"<(?:number|percentage|percent|metric|"
            r"result|value)>"
        ),
        re.IGNORECASE,
    ),
    re.compile(
        r"\bTBD\b",
        re.IGNORECASE,
    ),
)


INTERVIEW_PERCENT_CLAIM_PATTERN = re.compile(
    (
        r"(?<![\w.])"
        r"(?P<number>\d+(?:\.\d+)?)"
        r"\s*"
        r"(?:%|percent(?:age)?(?:\s+points?)?)"
        r"(?!\w)"
    ),
    re.IGNORECASE,
)


INTERVIEW_DURATION_CLAIM_PATTERN = re.compile(
    (
        r"(?<![\w.])"
        r"(?P<number>\d+(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>"
        r"milliseconds?|ms|"
        r"seconds?|secs?|"
        r"minutes?|mins?|"
        r"hours?|hrs?|"
        r"days?|weeks?|months?|years?"
        r")"
        r"(?!\w)"
    ),
    re.IGNORECASE,
)


INTERVIEW_COUNT_CLAIM_PATTERN = re.compile(
    (
        r"(?<![\w.])"
        r"(?P<number>\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>"
        r"users?|customers?|clients?|people|"
        r"requests?|records?|transactions?|orders?|"
        r"tickets?|incidents?|bugs?|issues?|tests?"
        r")"
        r"(?!\w)"
    ),
    re.IGNORECASE,
)


INTERVIEW_DATA_SIZE_CLAIM_PATTERN = re.compile(
    (
        r"(?<![\w.])"
        r"(?P<number>\d+(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>KB|MB|GB|TB)"
        r"(?!\w)"
    ),
    re.IGNORECASE,
)


INTERVIEW_MULTIPLIER_CLAIM_PATTERN = re.compile(
    (
        r"(?<![\w.])"
        r"(?P<number>\d+(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>x|times)"
        r"(?!\w)"
    ),
    re.IGNORECASE,
)


INTERVIEW_CURRENCY_SYMBOL_CLAIM_PATTERN = re.compile(
    (
        r"(?P<unit>[$£€])"
        r"\s*"
        r"(?P<number>\d+(?:,\d{3})*(?:\.\d+)?)"
    ),
    re.IGNORECASE,
)


INTERVIEW_CURRENCY_PREFIX_CLAIM_PATTERN = re.compile(
    (
        r"\b"
        r"(?P<unit>AUD|USD|GBP|EUR)"
        r"\s*"
        r"(?P<number>\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\b"
    ),
    re.IGNORECASE,
)


INTERVIEW_CURRENCY_SUFFIX_CLAIM_PATTERN = re.compile(
    (
        r"(?<![\w.])"
        r"(?P<number>\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>AUD|USD|GBP|EUR)"
        r"\b"
    ),
    re.IGNORECASE,
)


INTERVIEW_DURATION_UNIT_ALIASES = {
    "millisecond": "millisecond",
    "milliseconds": "millisecond",
    "ms": "millisecond",
    "second": "second",
    "seconds": "second",
    "sec": "second",
    "secs": "second",
    "minute": "minute",
    "minutes": "minute",
    "min": "minute",
    "mins": "minute",
    "hour": "hour",
    "hours": "hour",
    "hr": "hour",
    "hrs": "hour",
    "day": "day",
    "days": "day",
    "week": "week",
    "weeks": "week",
    "month": "month",
    "months": "month",
    "year": "year",
    "years": "year",
}


INTERVIEW_COUNT_UNIT_ALIASES = {
    "user": "user",
    "users": "user",
    "customer": "customer",
    "customers": "customer",
    "client": "client",
    "clients": "client",
    "people": "people",
    "request": "request",
    "requests": "request",
    "record": "record",
    "records": "record",
    "transaction": "transaction",
    "transactions": "transaction",
    "order": "order",
    "orders": "order",
    "ticket": "ticket",
    "tickets": "ticket",
    "incident": "incident",
    "incidents": "incident",
    "bug": "bug",
    "bugs": "bug",
    "issue": "issue",
    "issues": "issue",
    "test": "test",
    "tests": "test",
}


def _normalize_claim_number(
    value: str,
) -> str:
    """
    Normalize one numeric value without changing its meaning.
    """

    normalized = value.replace(
        ",",
        "",
    )

    if "." in normalized:
        normalized = (
            normalized
            .rstrip("0")
            .rstrip(".")
        )

    return normalized


def _extract_measurable_numeric_claims(
    value: str,
) -> set[str]:
    """
    Extract measurable numeric claims which need grounding.

    Plain numbers are intentionally ignored.

    Examples such as React 18, Python 3, Question 2, or a
    three-layer architecture do not represent achievement metrics.

    Percentages, durations, counts, currency values, data sizes,
    and multipliers are treated as measurable claims.
    """

    claims = set()

    for match in (
        INTERVIEW_PERCENT_CLAIM_PATTERN.finditer(
            value
        )
    ):
        number = _normalize_claim_number(
            match.group("number")
        )

        claims.add(
            f"percent:{number}"
        )

    for match in (
        INTERVIEW_DURATION_CLAIM_PATTERN.finditer(
            value
        )
    ):
        number = _normalize_claim_number(
            match.group("number")
        )

        raw_unit = (
            match.group("unit")
            .casefold()
        )

        unit = (
            INTERVIEW_DURATION_UNIT_ALIASES[
                raw_unit
            ]
        )

        claims.add(
            f"duration:{unit}:{number}"
        )

    for match in (
        INTERVIEW_COUNT_CLAIM_PATTERN.finditer(
            value
        )
    ):
        number = _normalize_claim_number(
            match.group("number")
        )

        raw_unit = (
            match.group("unit")
            .casefold()
        )

        unit = (
            INTERVIEW_COUNT_UNIT_ALIASES[
                raw_unit
            ]
        )

        claims.add(
            f"count:{unit}:{number}"
        )

    for match in (
        INTERVIEW_DATA_SIZE_CLAIM_PATTERN.finditer(
            value
        )
    ):
        number = _normalize_claim_number(
            match.group("number")
        )

        unit = (
            match.group("unit")
            .upper()
        )

        claims.add(
            f"data_size:{unit}:{number}"
        )

    for match in (
        INTERVIEW_MULTIPLIER_CLAIM_PATTERN.finditer(
            value
        )
    ):
        number = _normalize_claim_number(
            match.group("number")
        )

        claims.add(
            f"multiplier:{number}"
        )

    currency_patterns = (
        INTERVIEW_CURRENCY_SYMBOL_CLAIM_PATTERN,
        INTERVIEW_CURRENCY_PREFIX_CLAIM_PATTERN,
        INTERVIEW_CURRENCY_SUFFIX_CLAIM_PATTERN,
    )

    for pattern in currency_patterns:
        for match in pattern.finditer(
            value
        ):
            number = _normalize_claim_number(
                match.group("number")
            )

            unit = (
                match.group("unit")
                .upper()
            )

            claims.add(
                f"currency:{unit}:{number}"
            )

    return claims


def _validate_interview_feedback(
    *,
    result: InterviewFeedback,
    target_role: str,
    question: str,
    student_answer: str,
) -> None:
    """
    Enforce WBS 7.4 Interview Feedback grounding rules.

    Suggested responses must not contain obvious placeholder
    metrics or introduce measurable achievement claims which were
    not supplied through the target role, interview question, or
    Student answer.

    Plain numbers which do not represent measurable outcomes are
    allowed.
    """

    suggested_response = (
        result.suggested_response
    )

    for pattern in (
        INTERVIEW_FEEDBACK_PLACEHOLDER_PATTERNS
    ):
        if pattern.search(
            suggested_response
        ):
            raise AIResponseValidationError(
                "Interview AI feedback contains an "
                "unsupported placeholder value."
            )

    supplied_measurable_claims = set()

    for value in (
        target_role,
        question,
        student_answer,
    ):
        supplied_measurable_claims.update(
            _extract_measurable_numeric_claims(
                value
            )
        )

    generated_measurable_claims = (
        _extract_measurable_numeric_claims(
            suggested_response
        )
    )

    unsupported_measurable_claims = (
        generated_measurable_claims
        - supplied_measurable_claims
    )

    if unsupported_measurable_claims:
        raise AIResponseValidationError(
            "Interview AI feedback contains an "
            "unsupported numeric claim."
        )

def _normalize_focus_area(
    value: str,
) -> str:
    """
    Normalize one focus-area value for semantic comparison only.

    The original provider output is never rewritten.
    """

    return (
        value
        .strip()
        .casefold()
    )


def _validate_interview_question_set(
    *,
    result: InterviewQuestionSet,
    requested_question_count: int,
) -> None:
    """
    Enforce WBS 7.4 Interview Question response semantics.

    Structural validation is already performed by InterviewQuestionSet.

    This layer verifies that the external AI result agrees with the
    application request and with its own focus-area summary.

    Invalid provider output is rejected rather than silently corrected.
    """

    if (
        len(
            result.questions
        )
        != requested_question_count
    ):
        raise AIResponseValidationError(
            "Interview AI response question count does not "
            "match the requested count."
        )

    question_focus_areas = []

    for question in result.questions:

        normalized = (
            _normalize_focus_area(
                question.focus_area
            )
        )

        if not normalized:
            raise AIResponseValidationError(
                "Interview AI response contains a blank "
                "question focus area."
            )

        question_focus_areas.append(
            normalized
        )

    declared_focus_areas = []
    declared_seen = set()

    for focus_area in result.focus_areas:

        normalized = (
            _normalize_focus_area(
                focus_area
            )
        )

        if not normalized:
            raise AIResponseValidationError(
                "Interview AI response contains a blank "
                "declared focus area."
            )

        if normalized in declared_seen:
            raise AIResponseValidationError(
                "Interview AI response contains duplicate "
                "declared focus areas."
            )

        declared_seen.add(
            normalized
        )

        declared_focus_areas.append(
            normalized
        )

    expected_focus_areas = set(
        question_focus_areas
    )

    actual_focus_areas = set(
        declared_focus_areas
    )

    if (
        actual_focus_areas
        != expected_focus_areas
    ):
        raise AIResponseValidationError(
            "Interview AI response focus areas do not "
            "match generated questions."
        )


def generate_interview_questions(
    *,
    target_role: str,
    ai_provider: AIProvider,
    job_description: str | None = None,
    question_count: int = DEFAULT_INTERVIEW_QUESTION_COUNT,
) -> InterviewQuestionSet:
    """
    Generate a validated set of interview preparation questions.

    Input validation is delegated to InterviewQuestionInput.

    Prompt construction is delegated to the shared WBS 6.2
    interview-question prompt builder.

    The supplied AI provider must return a validated
    InterviewQuestionSet.
    """

    request = InterviewQuestionInput(
        target_role=target_role,
        job_description=job_description,
        question_count=question_count,
    )

    prompt_package = build_interview_question_prompt(
        request
    )

    result = ai_provider.generate(
        prompt_package=prompt_package,
        output_model=InterviewQuestionSet,
    )

    _validate_interview_question_set(
        result=result,
        requested_question_count=(
            request.question_count
        ),
    )

    return result


INTERVIEW_FEEDBACK_MAX_ATTEMPTS = 2


def generate_interview_feedback(
    *,
    target_role: str,
    question: str,
    student_answer: str,
    ai_provider: AIProvider,
) -> InterviewFeedback:
    """
    Generate validated feedback for one typed interview answer.

    Input validation is delegated to InterviewFeedbackInput.

    Prompt construction is delegated to the shared WBS 6.2
    interview-feedback prompt builder.

    The supplied AI provider must return validated
    InterviewFeedback.
    """

    request = InterviewFeedbackInput(
        target_role=target_role,
        question=question,
        student_answer=student_answer,
    )

    prompt_package = build_interview_feedback_prompt(
        request
    )

    for attempt in range(
        INTERVIEW_FEEDBACK_MAX_ATTEMPTS
    ):
        result = ai_provider.generate(
            prompt_package=prompt_package,
            output_model=InterviewFeedback,
        )

        try:
            _validate_interview_feedback(
                result=result,
                target_role=request.target_role,
                question=request.question,
                student_answer=request.student_answer,
            )

        except AIResponseValidationError:
            if (
                attempt + 1
                < INTERVIEW_FEEDBACK_MAX_ATTEMPTS
            ):
                prompt_package = (
                    build_interview_feedback_retry_prompt(
                        request
                    )
                )

                continue

            raise

        return result

    raise AssertionError(
        "Interview Feedback retry loop ended unexpectedly."
    )
