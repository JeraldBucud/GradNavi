"""
Production AI Semantic Alignment service for GradNavi.

Locked WBS 5.3 semantic design:

Career Identity similarity
    60%

Essential ESCO similarity
    40%

When a Career has no approved Essential ESCO evidence,
Career Identity receives the full semantic weight.

Technology evidence is excluded from this score.
O*NET numerical competency evidence is excluded from this score.

Those signals belong to GradNavi's dedicated structured
Career-fit components.

The service depends on GradNavi's provider-independent
EmbeddingProvider boundary.

The service does not import a concrete external AI provider.
"""

from dataclasses import (
    dataclass,
    replace,
)
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from enum import Enum
import math
from typing import Iterable

from ai_services.exceptions import (
    AIInputError,
    AIResponseValidationError,
)

from ai_services.providers.embeddings import (
    EmbeddingProvider,
)

from careers.models import Career

from careers.scoring_validation.ai_semantic_context import (
    CareerSemanticEvidence,
    build_student_semantic_context,
    clean_semantic_text,
    load_career_semantic_evidence,
)

from profiles.models import StudentProfile


IDENTITY_WEIGHT = Decimal("0.60")

ESSENTIAL_ESCO_WEIGHT = Decimal("0.40")

MAX_ESSENTIAL_ESCO_SKILLS = 12

SCORE_MAXIMUM = Decimal("100")

RATIO_QUANTUM = Decimal("0.000001")

SCORE_QUANTUM = Decimal("0.01")


class SemanticAlignmentContextMode(
    str,
    Enum,
):
    """
    Evidence mode used for one Career semantic score.
    """

    IDENTITY_ESCO = "identity_esco"

    IDENTITY_ONLY = "identity_only"


@dataclass(frozen=True)
class CareerSemanticInputs:
    """
    Production semantic text for one Career.
    """

    career_id: int
    career_name: str

    identity_text: str

    essential_esco_text: str | None

    essential_esco_count: int

    context_mode: SemanticAlignmentContextMode


@dataclass(frozen=True)
class SemanticAlignmentResult:
    """
    Production AI Semantic Alignment result.
    """

    career_id: int
    career_name: str

    semantic_alignment_score: Decimal

    semantic_alignment_ratio: Decimal

    identity_similarity: Decimal

    esco_similarity: Decimal | None

    context_mode: SemanticAlignmentContextMode

    essential_esco_count: int

    rank: int | None = None


@dataclass(frozen=True)
class SemanticAlignmentReport:
    """
    One complete semantic scoring operation.
    """

    model: str

    prompt_tokens: int
    total_tokens: int

    career_count: int

    results: tuple[
        SemanticAlignmentResult,
        ...
    ]


def select_essential_esco_evidence(
    *,
    evidence: CareerSemanticEvidence,
) -> tuple:
    """
    Select the compact Essential ESCO evidence used
    by the locked production semantic model.

    Selection rules match the validated A3 design:

    - Essential ESCO relationships only.
    - Deterministic alphabetical ordering.
    - Maximum of 12 relationships.
    """

    essential = [
        item
        for item
        in evidence.esco
        if (
            item.relation
            .strip()
            .casefold()
            == "essential"
        )
    ]

    essential.sort(
        key=lambda item: (
            item.skill_name.casefold(),
            item.concept_type.casefold(),
        )
    )

    return tuple(
        essential[
            :MAX_ESSENTIAL_ESCO_SKILLS
        ]
    )


def build_career_semantic_inputs(
    *,
    career: Career,
) -> CareerSemanticInputs:
    """
    Build production semantic text for one active Career.
    """

    if not career.active:
        raise AIInputError(
            "AI Semantic Alignment requires "
            "an active Career."
        )

    career_name = clean_semantic_text(
        career.name
    )

    if not career_name:
        raise AIInputError(
            "Career name must not be blank."
        )

    identity_lines = [
        "CAREER",
        "- name: "
        + career_name,
    ]

    category = clean_semantic_text(
        career.category
    )

    if category:
        identity_lines.append(
            "- category: "
            + category
        )

    description = clean_semantic_text(
        career.description
    )

    if description:
        identity_lines.append(
            "- description: "
            + description
        )

    identity_text = "\n".join(
        identity_lines
    )

    evidence = (
        load_career_semantic_evidence(
            career=career
        )
    )

    essential_esco = (
        select_essential_esco_evidence(
            evidence=evidence
        )
    )

    essential_esco_text = None

    if essential_esco:
        esco_lines = [
            "ESSENTIAL CAREER SKILLS",
        ]

        for item in essential_esco:
            esco_lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
            )

        essential_esco_text = "\n".join(
            esco_lines
        )

        context_mode = (
            SemanticAlignmentContextMode
            .IDENTITY_ESCO
        )

    else:
        context_mode = (
            SemanticAlignmentContextMode
            .IDENTITY_ONLY
        )

    return CareerSemanticInputs(
        career_id=career.id,
        career_name=career_name,
        identity_text=identity_text,
        essential_esco_text=(
            essential_esco_text
        ),
        essential_esco_count=len(
            essential_esco
        ),
        context_mode=context_mode,
    )


def build_embedding_plan(
    texts: Iterable[str],
) -> tuple[
    tuple[str, ...],
    dict[str, int],
]:
    """
    Deduplicate embedding text while preserving
    deterministic first-seen order.
    """

    unique_texts = []
    text_to_index = {}

    for text in texts:
        normalized = text.strip()

        if not normalized:
            raise AIInputError(
                "Semantic embedding text "
                "must not be blank."
            )

        if normalized in text_to_index:
            continue

        text_to_index[
            normalized
        ] = len(
            unique_texts
        )

        unique_texts.append(
            normalized
        )

    return (
        tuple(
            unique_texts
        ),
        text_to_index,
    )


def calculate_semantic_cosine_similarity(
    *,
    first,
    second,
) -> Decimal:
    """
    Calculate cosine similarity for two embedding vectors.
    """

    if not first or not second:
        raise AIResponseValidationError(
            "Embedding vectors must not be empty."
        )

    if len(first) != len(second):
        raise AIResponseValidationError(
            "Embedding vectors must use "
            "matching dimensions."
        )

    dot_product = sum(
        first_value
        * second_value
        for (
            first_value,
            second_value,
        )
        in zip(
            first,
            second,
        )
    )

    first_norm = math.sqrt(
        sum(
            value
            * value
            for value
            in first
        )
    )

    second_norm = math.sqrt(
        sum(
            value
            * value
            for value
            in second
        )
    )

    if (
        first_norm == 0
        or second_norm == 0
    ):
        raise AIResponseValidationError(
            "Embedding vector norm must "
            "be greater than zero."
        )

    similarity = (
        dot_product
        / (
            first_norm
            * second_norm
        )
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


def clamp_semantic_similarity(
    similarity: Decimal,
) -> Decimal:
    """
    Treat negative cosine similarity as zero alignment.
    """

    if similarity > Decimal("1"):
        raise AIResponseValidationError(
            "Semantic similarity must not "
            "exceed one."
        )

    if similarity < Decimal("-1"):
        raise AIResponseValidationError(
            "Semantic similarity must not "
            "be below negative one."
        )

    return max(
        Decimal("0"),
        similarity,
    )


def combine_semantic_alignment(
    *,
    identity_similarity: Decimal,
    esco_similarity: Decimal | None,
) -> Decimal:
    """
    Apply the locked GradNavi A3-60 formula.

    Identity + ESCO:
        60% Identity
        40% Essential ESCO

    Identity-only fallback:
        100% Identity
    """

    identity_signal = (
        clamp_semantic_similarity(
            identity_similarity
        )
    )

    if esco_similarity is None:
        return identity_signal.quantize(
            RATIO_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

    esco_signal = (
        clamp_semantic_similarity(
            esco_similarity
        )
    )

    combined = (
        identity_signal
        * IDENTITY_WEIGHT
        + esco_signal
        * ESSENTIAL_ESCO_WEIGHT
    )

    return combined.quantize(
        RATIO_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def rank_semantic_alignment_results(
    results: Iterable[
        SemanticAlignmentResult
    ],
) -> tuple[
    SemanticAlignmentResult,
    ...
]:
    """
    Rank semantic results deterministically.

    Rules:

    1. Higher semantic alignment ratio.
    2. Career name alphabetically.
    3. Career ID ascending.
    """

    ordered = list(
        results
    )

    ordered.sort(
        key=lambda result: (
            -result.semantic_alignment_ratio,
            result.career_name.casefold(),
            result.career_id,
        )
    )

    return tuple(
        replace(
            result,
            rank=rank,
        )
        for rank, result
        in enumerate(
            ordered,
            start=1,
        )
    )


def validate_careers(
    careers: Iterable[
        Career
    ],
) -> tuple[
    Career,
    ...
]:
    """
    Validate and freeze Career input.
    """

    career_list = tuple(
        careers
    )

    if not career_list:
        raise AIInputError(
            "AI Semantic Alignment requires "
            "at least one Career."
        )

    seen_ids = set()

    for career in career_list:
        if career.id in seen_ids:
            raise AIInputError(
                "Duplicate Career input "
                "was supplied."
            )

        seen_ids.add(
            career.id
        )

        if not career.active:
            raise AIInputError(
                "AI Semantic Alignment requires "
                "active Careers only."
            )

    return career_list


def score_ai_semantic_alignment(
    *,
    student_profile: StudentProfile,
    careers: Iterable[
        Career
    ],
    embedding_provider: EmbeddingProvider,
) -> SemanticAlignmentReport:
    """
    Score one Student against supplied active Careers.

    One provider batch embeds:

    - Student semantic context.
    - Career Identity contexts.
    - Essential ESCO contexts when available.

    Ranking happens locally after embedding.
    """

    career_list = validate_careers(
        careers
    )

    student_context = (
        build_student_semantic_context(
            student_profile=student_profile
        )
    )

    career_inputs = tuple(
        build_career_semantic_inputs(
            career=career
        )
        for career
        in career_list
    )

    texts = [
        student_context.text,
    ]

    for career_input in career_inputs:
        texts.append(
            career_input.identity_text
        )

        if (
            career_input.essential_esco_text
            is not None
        ):
            texts.append(
                career_input
                .essential_esco_text
            )

    (
        unique_texts,
        text_to_index,
    ) = build_embedding_plan(
        texts
    )

    embedding_batch = (
        embedding_provider.embed_texts(
            texts=unique_texts
        )
    )

    if (
        embedding_batch.vector_count
        != len(
            unique_texts
        )
    ):
        raise AIResponseValidationError(
            "Embedding vector count does not "
            "match semantic input count."
        )

    vectors_by_text = {
        text: (
            embedding_batch.vectors[
                index
            ]
        )
        for text, index
        in text_to_index.items()
    }

    student_vector = (
        vectors_by_text[
            student_context.text.strip()
        ]
    )

    results = []

    for career_input in career_inputs:
        identity_vector = (
            vectors_by_text[
                career_input
                .identity_text
                .strip()
            ]
        )

        identity_similarity = (
            calculate_semantic_cosine_similarity(
                first=student_vector,
                second=identity_vector,
            )
        )

        esco_similarity = None

        if (
            career_input.essential_esco_text
            is not None
        ):
            esco_vector = (
                vectors_by_text[
                    career_input
                    .essential_esco_text
                    .strip()
                ]
            )

            esco_similarity = (
                calculate_semantic_cosine_similarity(
                    first=student_vector,
                    second=esco_vector,
                )
            )

        alignment_ratio = (
            combine_semantic_alignment(
                identity_similarity=(
                    identity_similarity
                ),
                esco_similarity=(
                    esco_similarity
                ),
            )
        )

        alignment_score = (
            alignment_ratio
            * SCORE_MAXIMUM
        ).quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

        results.append(
            SemanticAlignmentResult(
                career_id=(
                    career_input.career_id
                ),
                career_name=(
                    career_input.career_name
                ),
                semantic_alignment_score=(
                    alignment_score
                ),
                semantic_alignment_ratio=(
                    alignment_ratio
                ),
                identity_similarity=(
                    identity_similarity
                ),
                esco_similarity=(
                    esco_similarity
                ),
                context_mode=(
                    career_input.context_mode
                ),
                essential_esco_count=(
                    career_input
                    .essential_esco_count
                ),
            )
        )

    ranked_results = (
        rank_semantic_alignment_results(
            results
        )
    )

    return SemanticAlignmentReport(
        model=embedding_batch.model,
        prompt_tokens=(
            embedding_batch.prompt_tokens
        ),
        total_tokens=(
            embedding_batch.total_tokens
        ),
        career_count=len(
            career_list
        ),
        results=ranked_results,
    )
