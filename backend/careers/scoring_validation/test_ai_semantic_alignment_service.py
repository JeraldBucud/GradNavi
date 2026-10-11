"""
Tests for the production GradNavi AI Semantic Alignment service.

No external AI provider is contacted.
"""

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ai_services.exceptions import (
    AIInputError,
    AIResponseValidationError,
)

from ai_services.providers.embeddings import (
    EmbeddingBatchResult,
)

from careers.scoring_validation.ai_semantic_context import (
    CareerEscoSemanticEvidence,
    CareerNumericalSemanticEvidence,
    CareerSemanticEvidence,
    CareerTechnologySemanticEvidence,
    StudentSemanticContext,
)

from careers.services.ai_semantic_alignment import (
    ESSENTIAL_ESCO_WEIGHT,
    IDENTITY_WEIGHT,
    MAX_ESSENTIAL_ESCO_SKILLS,
    SemanticAlignmentContextMode,
    build_career_semantic_inputs,
    combine_semantic_alignment,
    score_ai_semantic_alignment,
    select_essential_esco_evidence,
)


class RecordingEmbeddingProvider:
    """
    Deterministic provider stub for local tests.
    """

    def __init__(
        self,
        *,
        vectors_by_text,
    ):
        self.vectors_by_text = (
            vectors_by_text
        )

        self.calls = []

    def embed_texts(
        self,
        *,
        texts,
    ):
        self.calls.append(
            tuple(
                texts
            )
        )

        vectors = tuple(
            self.vectors_by_text[
                text
            ]
            for text
            in texts
        )

        return EmbeddingBatchResult(
            vectors=vectors,
            model="test-embedding-model",
            prompt_tokens=len(
                texts
            ),
            total_tokens=len(
                texts
            ),
        )


class InvalidCountEmbeddingProvider:
    """
    Provider stub returning an invalid vector count.
    """

    def embed_texts(
        self,
        *,
        texts,
    ):
        return EmbeddingBatchResult(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
            ),
            model="invalid-test-model",
            prompt_tokens=1,
            total_tokens=1,
        )


def make_career(
    *,
    career_id,
    name,
    active=True,
    category="Technology",
    description="Career description.",
):
    return SimpleNamespace(
        id=career_id,
        name=name,
        active=active,
        category=category,
        description=description,
    )


def make_evidence(
    *,
    essential_names=(),
    optional_names=(),
):
    esco = []

    for name in essential_names:
        esco.append(
            CareerEscoSemanticEvidence(
                skill_name=name,
                concept_type="skill",
                relation="essential",
            )
        )

    for name in optional_names:
        esco.append(
            CareerEscoSemanticEvidence(
                skill_name=name,
                concept_type="skill",
                relation="optional",
            )
        )

    return CareerSemanticEvidence(
        numerical=(
            CareerNumericalSemanticEvidence(
                skill_name="NUMERICAL SHOULD NOT APPEAR",
                concept_type="skill",
                normalized_importance=(
                    Decimal("90")
                ),
                normalized_level=(
                    Decimal("80")
                ),
            ),
        ),
        technologies=(
            CareerTechnologySemanticEvidence(
                skill_name="TECHNOLOGY SHOULD NOT APPEAR",
                concept_type="technology",
                in_demand_percentage=(
                    Decimal("50")
                ),
            ),
        ),
        esco=tuple(
            esco
        ),
    )


class ProductionSemanticAlignmentTests(
    SimpleTestCase
):
    def test_locked_weights_are_60_40(
        self,
    ):
        self.assertEqual(
            IDENTITY_WEIGHT,
            Decimal("0.60"),
        )

        self.assertEqual(
            ESSENTIAL_ESCO_WEIGHT,
            Decimal("0.40"),
        )

        self.assertEqual(
            MAX_ESSENTIAL_ESCO_SKILLS,
            12,
        )

    def test_locked_formula_combines_identity_and_esco(
        self,
    ):
        result = (
            combine_semantic_alignment(
                identity_similarity=(
                    Decimal("0.80")
                ),
                esco_similarity=(
                    Decimal("0.60")
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.720000"),
        )

    def test_missing_esco_uses_identity_only(
        self,
    ):
        result = (
            combine_semantic_alignment(
                identity_similarity=(
                    Decimal("0.63")
                ),
                esco_similarity=None,
            )
        )

        self.assertEqual(
            result,
            Decimal("0.630000"),
        )

    def test_essential_esco_selection_is_filtered_sorted_and_limited(
        self,
    ):
        essential_names = tuple(
            f"Skill {index:02}"
            for index
            in range(
                15,
                0,
                -1,
            )
        )

        evidence = make_evidence(
            essential_names=(
                essential_names
            ),
            optional_names=(
                "Optional Skill",
            ),
        )

        selected = (
            select_essential_esco_evidence(
                evidence=evidence
            )
        )

        self.assertEqual(
            len(
                selected
            ),
            12,
        )

        self.assertEqual(
            selected[0].skill_name,
            "Skill 01",
        )

        self.assertEqual(
            selected[-1].skill_name,
            "Skill 12",
        )

        self.assertNotIn(
            "Optional Skill",
            tuple(
                item.skill_name
                for item
                in selected
            ),
        )

    @patch(
        "careers.services."
        "ai_semantic_alignment."
        "load_career_semantic_evidence"
    )
    def test_career_context_excludes_technology_and_numerical_evidence(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence(
                essential_names=(
                    "Develop software",
                )
            )
        )

        result = (
            build_career_semantic_inputs(
                career=make_career(
                    career_id=1,
                    name="Software Engineer",
                )
            )
        )

        combined_text = (
            result.identity_text
            + "\n"
            + (
                result.essential_esco_text
                or ""
            )
        )

        self.assertIn(
            "Software Engineer",
            combined_text,
        )

        self.assertIn(
            "Develop software",
            combined_text,
        )

        self.assertNotIn(
            "TECHNOLOGY SHOULD NOT APPEAR",
            combined_text,
        )

        self.assertNotIn(
            "NUMERICAL SHOULD NOT APPEAR",
            combined_text,
        )

        self.assertEqual(
            result.context_mode,
            SemanticAlignmentContextMode
            .IDENTITY_ESCO,
        )

    @patch(
        "careers.services."
        "ai_semantic_alignment."
        "load_career_semantic_evidence"
    )
    def test_missing_esco_sets_identity_only_mode(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        result = (
            build_career_semantic_inputs(
                career=make_career(
                    career_id=1,
                    name="Cyber Security Architect",
                )
            )
        )

        self.assertEqual(
            result.context_mode,
            SemanticAlignmentContextMode
            .IDENTITY_ONLY,
        )

        self.assertIsNone(
            result.essential_esco_text
        )

        self.assertEqual(
            result.essential_esco_count,
            0,
        )

    @patch(
        "careers.services."
        "ai_semantic_alignment."
        "load_career_semantic_evidence"
    )
    @patch(
        "careers.services."
        "ai_semantic_alignment."
        "build_student_semantic_context"
    )
    def test_service_batches_once_scores_and_ranks(
        self,
        mocked_student_context,
        mocked_evidence,
    ):
        mocked_student_context.return_value = (
            StudentSemanticContext(
                text="STUDENT",
                skill_count=1,
                education_count=0,
                experience_count=0,
                project_count=0,
                career_goal_count=1,
            )
        )

        career_a = make_career(
            career_id=1,
            name="Career A",
            description="Career A description.",
        )

        career_b = make_career(
            career_id=2,
            name="Career B",
            description="Career B description.",
        )

        evidence_by_id = {
            1: make_evidence(
                essential_names=(
                    "Skill A",
                )
            ),
            2: make_evidence(),
        }

        mocked_evidence.side_effect = (
            lambda *,
            career: evidence_by_id[
                career.id
            ]
        )

        career_a_identity = (
            "CAREER\n"
            "- name: Career A\n"
            "- category: Technology\n"
            "- description: Career A description."
        )

        career_a_esco = (
            "ESSENTIAL CAREER SKILLS\n"
            "- Skill A"
        )

        career_b_identity = (
            "CAREER\n"
            "- name: Career B\n"
            "- category: Technology\n"
            "- description: Career B description."
        )

        provider = (
            RecordingEmbeddingProvider(
                vectors_by_text={
                    "STUDENT": (
                        1.0,
                        0.0,
                    ),
                    career_a_identity: (
                        1.0,
                        0.0,
                    ),
                    career_a_esco: (
                        0.0,
                        1.0,
                    ),
                    career_b_identity: (
                        0.5,
                        0.8660254038,
                    ),
                }
            )
        )

        report = (
            score_ai_semantic_alignment(
                student_profile=(
                    SimpleNamespace()
                ),
                careers=(
                    career_a,
                    career_b,
                ),
                embedding_provider=(
                    provider
                ),
            )
        )

        self.assertEqual(
            len(
                provider.calls
            ),
            1,
        )

        self.assertEqual(
            report.model,
            "test-embedding-model",
        )

        self.assertEqual(
            report.career_count,
            2,
        )

        self.assertEqual(
            report.results[0].career_id,
            1,
        )

        self.assertEqual(
            report.results[0].rank,
            1,
        )

        self.assertEqual(
            report.results[0]
            .semantic_alignment_score,
            Decimal("60.00"),
        )

        self.assertEqual(
            report.results[0]
            .context_mode,
            SemanticAlignmentContextMode
            .IDENTITY_ESCO,
        )

        self.assertEqual(
            report.results[1]
            .context_mode,
            SemanticAlignmentContextMode
            .IDENTITY_ONLY,
        )

    def test_empty_career_input_is_rejected(
        self,
    ):
        provider = (
            RecordingEmbeddingProvider(
                vectors_by_text={}
            )
        )

        with self.assertRaises(
            AIInputError
        ):
            score_ai_semantic_alignment(
                student_profile=(
                    SimpleNamespace()
                ),
                careers=(),
                embedding_provider=(
                    provider
                ),
            )

    def test_duplicate_career_input_is_rejected(
        self,
    ):
        career = make_career(
            career_id=1,
            name="Career",
        )

        provider = (
            RecordingEmbeddingProvider(
                vectors_by_text={}
            )
        )

        with self.assertRaises(
            AIInputError
        ):
            score_ai_semantic_alignment(
                student_profile=(
                    SimpleNamespace()
                ),
                careers=(
                    career,
                    career,
                ),
                embedding_provider=(
                    provider
                ),
            )

    def test_inactive_career_is_rejected(
        self,
    ):
        career = make_career(
            career_id=1,
            name="Inactive Career",
            active=False,
        )

        provider = (
            RecordingEmbeddingProvider(
                vectors_by_text={}
            )
        )

        with self.assertRaises(
            AIInputError
        ):
            score_ai_semantic_alignment(
                student_profile=(
                    SimpleNamespace()
                ),
                careers=(
                    career,
                ),
                embedding_provider=(
                    provider
                ),
            )

    @patch(
        "careers.services."
        "ai_semantic_alignment."
        "load_career_semantic_evidence"
    )
    @patch(
        "careers.services."
        "ai_semantic_alignment."
        "build_student_semantic_context"
    )
    def test_invalid_embedding_count_is_rejected(
        self,
        mocked_student_context,
        mocked_evidence,
    ):
        mocked_student_context.return_value = (
            StudentSemanticContext(
                text="STUDENT",
                skill_count=1,
                education_count=0,
                experience_count=0,
                project_count=0,
                career_goal_count=0,
            )
        )

        mocked_evidence.return_value = (
            make_evidence()
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            score_ai_semantic_alignment(
                student_profile=(
                    SimpleNamespace()
                ),
                careers=(
                    make_career(
                        career_id=1,
                        name="Career",
                    ),
                ),
                embedding_provider=(
                    InvalidCountEmbeddingProvider()
                ),
            )

    def test_production_service_does_not_import_openai(
        self,
    ):
        service_path = (
            Path(__file__)
            .resolve()
            .parents[1]
            / "services"
            / "ai_semantic_alignment.py"
        )

        source = (
            service_path
            .read_text(
                encoding="utf-8-sig"
            )
            .casefold()
        )

        self.assertNotIn(
            "import openai",
            source,
        )

        self.assertNotIn(
            "from openai",
            source,
        )
