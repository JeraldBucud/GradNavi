"""
AI Candidate 1 for GradNavi Career Recommendation validation.

A1 measures semantic alignment between:

- one privacy-minimised Student career context
- one or more approved Career semantic contexts

The embedding provider stays provider-independent.

Scoring:

    cosine_similarity(student, career)

Negative similarity is treated as zero alignment.

Semantic Alignment:

    max(0, cosine_similarity) * 100

Important status behaviour:

    Empty Student semantic context
        -> INSUFFICIENT_PROFILE

    Career semantic context is empty
        -> INSUFFICIENT_EVIDENCE

    Valid embeddings
        -> SCORED

This module is experimental validation code only.
Production WBS 5.3 scoring is not modified.
"""

from dataclasses import (
    dataclass,
    replace,
)
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from math import (
    isfinite,
    sqrt,
)
from typing import (
    Iterable,
    Sequence,
)

from ai_services.exceptions import (
    AIInputError,
    AIResponseValidationError,
)
from ai_services.providers.embeddings import (
    EmbeddingProvider,
)

from careers.services.recommendation_scoring import (
    ScoreStatus,
)


SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")

SCORE_QUANTUM = Decimal("0.01")

COSINE_MINIMUM = Decimal("-1")
COSINE_MAXIMUM = Decimal("1")

COSINE_QUANTUM = Decimal("0.000001")


@dataclass(frozen=True)
class SemanticCareerInput:
    """
    One Career semantic context supplied to A1.
    """

    career_id: int
    career_name: str
    semantic_text: str


@dataclass(frozen=True)
class AICandidate1Result:
    """
    One AI Candidate A1 Career result.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    semantic_alignment_score: (
        Decimal | None
    ) = None

    rank: int | None = None

    semantic_alignment_ratio: (
        Decimal | None
    ) = None

    cosine_similarity: (
        Decimal | None
    ) = None


@dataclass(frozen=True)
class AICandidate1BatchResult:
    """
    One complete A1 scoring execution.

    Token usage belongs to the embedding batch,
    rather than individual Careers.
    """

    model: str | None

    prompt_tokens: int
    total_tokens: int

    results: tuple[
        AICandidate1Result,
        ...
    ]


def calculate_cosine_similarity(
    *,
    first: Sequence[float],
    second: Sequence[float],
) -> Decimal:
    """
    Calculate validated cosine similarity.

    The result stays within -1 to 1.
    """

    if not first or not second:
        raise AIResponseValidationError(
            "Embedding vectors must not be empty."
        )

    if len(first) != len(second):
        raise AIResponseValidationError(
            "Embedding vectors must have "
            "matching dimensions."
        )

    try:
        first_values = tuple(
            float(value)
            for value in first
        )

        second_values = tuple(
            float(value)
            for value in second
        )

    except (
        TypeError,
        ValueError,
    ) as error:
        raise AIResponseValidationError(
            "Embedding vectors must contain "
            "numeric values."
        ) from error

    if not all(
        isfinite(value)
        for value
        in (
            *first_values,
            *second_values,
        )
    ):
        raise AIResponseValidationError(
            "Embedding vectors must contain "
            "finite values."
        )

    dot_product = sum(
        first_value
        * second_value
        for (
            first_value,
            second_value,
        )
        in zip(
            first_values,
            second_values,
        )
    )

    first_norm = sqrt(
        sum(
            value * value
            for value
            in first_values
        )
    )

    second_norm = sqrt(
        sum(
            value * value
            for value
            in second_values
        )
    )

    if (
        first_norm <= 0
        or second_norm <= 0
    ):
        raise AIResponseValidationError(
            "Embedding vector norm must be "
            "greater than zero."
        )

    similarity = (
        dot_product
        / (
            first_norm
            * second_norm
        )
    )

    if not isfinite(
        similarity
    ):
        raise AIResponseValidationError(
            "Cosine similarity is not finite."
        )

    similarity = max(
        -1.0,
        min(
            1.0,
            similarity,
        ),
    )

    return Decimal(
        str(
            similarity
        )
    )


def calculate_semantic_alignment(
    *,
    cosine_similarity: Decimal,
) -> tuple[
    Decimal,
    Decimal,
]:
    """
    Convert cosine similarity into GradNavi's
    0 to 100 Semantic Alignment scale.

    Negative similarity represents no alignment
    and therefore maps to zero.
    """

    if not (
        COSINE_MINIMUM
        <= cosine_similarity
        <= COSINE_MAXIMUM
    ):
        raise ValueError(
            "cosine_similarity must stay "
            "within -1 to 1."
        )

    alignment_ratio = max(
        Decimal("0"),
        cosine_similarity,
    )

    alignment_score = (
        alignment_ratio
        * SCORE_MAXIMUM
    ).quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )

    return (
        alignment_ratio,
        alignment_score,
    )


def validate_career_inputs(
    careers: Iterable[
        SemanticCareerInput
    ],
) -> tuple[
    SemanticCareerInput,
    ...
]:
    """
    Validate and freeze Career inputs.
    """

    career_list = tuple(
        careers
    )

    seen_ids = set()

    for career in career_list:
        if career.career_id <= 0:
            raise AIInputError(
                "career_id must be greater "
                "than zero."
            )

        if not career.career_name.strip():
            raise AIInputError(
                "career_name must not be blank."
            )

        if career.career_id in seen_ids:
            raise AIInputError(
                "Duplicate Career input was supplied."
            )

        seen_ids.add(
            career.career_id
        )

    return career_list


def rank_ai_candidate_1_results(
    results: Iterable[
        AICandidate1Result
    ],
) -> tuple[
    AICandidate1Result,
    ...
]:
    """
    Rank scored A1 results deterministically.

    Tie breakers:

    1. Higher exact Semantic Alignment ratio.
    2. Career name alphabetically.
    3. Career ID ascending.

    Unscored Careers appear after scored Careers
    and receive no rank.
    """

    result_list = tuple(
        results
    )

    scored = []
    unscored = []

    for result in result_list:
        if (
            result.score_status
            == ScoreStatus.SCORED
        ):
            if (
                result.semantic_alignment_ratio
                is None
            ):
                raise ValueError(
                    "A scored A1 result must have "
                    "semantic_alignment_ratio."
                )

            if (
                result.semantic_alignment_score
                is None
            ):
                raise ValueError(
                    "A scored A1 result must have "
                    "semantic_alignment_score."
                )

            if (
                result.cosine_similarity
                is None
            ):
                raise ValueError(
                    "A scored A1 result must have "
                    "cosine_similarity."
                )

            scored.append(
                result
            )

        else:
            unscored.append(
                result
            )

    scored.sort(
        key=lambda result: (
            -result.semantic_alignment_ratio,
            result.career_name.casefold(),
            result.career_id,
        )
    )

    ranked = tuple(
        replace(
            result,
            rank=index,
        )
        for index, result
        in enumerate(
            scored,
            start=1,
        )
    )

    unscored.sort(
        key=lambda result: (
            result.career_name.casefold(),
            result.career_id,
        )
    )

    return (
        ranked
        + tuple(
            unscored
        )
    )


def score_ai_candidate_1(
    *,
    student_semantic_text: str,
    careers: Iterable[
        SemanticCareerInput
    ],
    embedding_provider: EmbeddingProvider,
) -> AICandidate1BatchResult:
    """
    Score semantic Career alignment with one
    batched embedding-provider request.
    """

    career_list = validate_career_inputs(
        careers
    )

    if not career_list:
        return AICandidate1BatchResult(
            model=None,
            prompt_tokens=0,
            total_tokens=0,
            results=(),
        )

    student_text = (
        student_semantic_text.strip()
    )

    if not student_text:
        results = tuple(
            AICandidate1Result(
                career_id=career.career_id,
                career_name=career.career_name,
                score_status=(
                    ScoreStatus.INSUFFICIENT_PROFILE
                ),
            )
            for career in career_list
        )

        return AICandidate1BatchResult(
            model=None,
            prompt_tokens=0,
            total_tokens=0,
            results=(
                rank_ai_candidate_1_results(
                    results
                )
            ),
        )

    supported_careers = []
    result_by_career_id = {}

    for career in career_list:
        semantic_text = (
            career.semantic_text.strip()
        )

        if not semantic_text:
            result_by_career_id[
                career.career_id
            ] = AICandidate1Result(
                career_id=career.career_id,
                career_name=career.career_name,
                score_status=(
                    ScoreStatus.INSUFFICIENT_EVIDENCE
                ),
            )

            continue

        supported_careers.append(
            SemanticCareerInput(
                career_id=career.career_id,
                career_name=career.career_name,
                semantic_text=semantic_text,
            )
        )

    if not supported_careers:
        results = tuple(
            result_by_career_id[
                career.career_id
            ]
            for career in career_list
        )

        return AICandidate1BatchResult(
            model=None,
            prompt_tokens=0,
            total_tokens=0,
            results=(
                rank_ai_candidate_1_results(
                    results
                )
            ),
        )

    embedding_texts = [
        student_text,
    ]

    embedding_texts.extend(
        career.semantic_text
        for career
        in supported_careers
    )

    embedding_batch = (
        embedding_provider.embed_texts(
            texts=tuple(
                embedding_texts
            )
        )
    )

    expected_vector_count = (
        1
        + len(
            supported_careers
        )
    )

    if (
        embedding_batch.vector_count
        != expected_vector_count
    ):
        raise AIResponseValidationError(
            "Embedding vector count does not "
            "match A1 input count."
        )

    student_vector = (
        embedding_batch.vectors[0]
    )

    for (
        career,
        career_vector,
    ) in zip(
        supported_careers,
        embedding_batch.vectors[1:],
    ):
        cosine = (
            calculate_cosine_similarity(
                first=student_vector,
                second=career_vector,
            )
        )

        (
            alignment_ratio,
            alignment_score,
        ) = calculate_semantic_alignment(
            cosine_similarity=cosine
        )

        result_by_career_id[
            career.career_id
        ] = AICandidate1Result(
            career_id=career.career_id,
            career_name=career.career_name,
            score_status=(
                ScoreStatus.SCORED
            ),
            semantic_alignment_score=(
                alignment_score
            ),
            semantic_alignment_ratio=(
                alignment_ratio
            ),
            cosine_similarity=(
                cosine.quantize(
                    COSINE_QUANTUM,
                    rounding=ROUND_HALF_UP,
                )
            ),
        )

    results = tuple(
        result_by_career_id[
            career.career_id
        ]
        for career in career_list
    )

    ranked_results = (
        rank_ai_candidate_1_results(
            results
        )
    )

    return AICandidate1BatchResult(
        model=embedding_batch.model,
        prompt_tokens=(
            embedding_batch.prompt_tokens
        ),
        total_tokens=(
            embedding_batch.total_tokens
        ),
        results=ranked_results,
    )
