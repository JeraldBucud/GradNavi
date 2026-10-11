from datetime import date
from decimal import Decimal

from django.test import TestCase

from careers.models import (
    Career,
    CareerSkill,
    CareerSkillEvidence,
    ReferenceDataset,
    ReferenceSource,
    ReviewStatus,
)

from careers.services.evidence_policy import (
    CORE_COMPETENCY_MINIMUM_IMPORTANCE,
    meets_core_competency_importance,
)

from careers.services.recommendation_scoring import (
    load_weighted_competencies,
)

from careers.services.readiness_scoring import (
    load_career_readiness_requirements,
)

from profiles.models import Skill


class CoreCompetencyEvidencePolicyTests(
    TestCase
):
    def setUp(self):
        self.source = (
            ReferenceSource.objects.create(
                name="O*NET Database",
            )
        )

        self.dataset = (
            ReferenceDataset.objects.create(
                source=self.source,
                version="31.0-policy-test",
                retrieved_at=date(
                    2026,
                    9,
                    17,
                ),
                status=(
                    ReferenceDataset
                    .Status
                    .ACTIVE
                ),
            )
        )

        self.career = (
            Career.objects.create(
                name=(
                    "Evidence Policy Test Career"
                ),
                active=True,
            )
        )

        self.low_skill = (
            self._create_numerical_evidence(
                name="Low Relevance Knowledge",
                concept_type=(
                    Skill.ConceptType.KNOWLEDGE
                ),
                importance=Decimal(
                    "49.99"
                ),
                level=Decimal(
                    "40.00"
                ),
                external_id="LOW",
            )
        )

        self.boundary_skill = (
            self._create_numerical_evidence(
                name="Boundary Knowledge",
                concept_type=(
                    Skill.ConceptType.KNOWLEDGE
                ),
                importance=Decimal(
                    "50.00"
                ),
                level=Decimal(
                    "50.00"
                ),
                external_id="BOUNDARY",
            )
        )

        self.high_skill = (
            self._create_numerical_evidence(
                name="High Importance Skill",
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
                importance=Decimal(
                    "75.00"
                ),
                level=Decimal(
                    "65.00"
                ),
                external_id="HIGH",
            )
        )


    def _create_numerical_evidence(
        self,
        *,
        name,
        concept_type,
        importance,
        level,
        external_id,
    ):
        skill = Skill.objects.create(
            name=name,
            concept_type=concept_type,
        )

        career_skill = (
            CareerSkill.objects.create(
                career=self.career,
                skill=skill,
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=self.dataset,
            external_occupation_id=(
                "99-9999.99"
            ),
            external_skill_id=external_id,
            source_domain=(
                "onet_knowledge"
                if (
                    concept_type
                    == Skill.ConceptType.KNOWLEDGE
                )
                else "onet_essential_skills"
            ),
            normalized_importance=(
                importance
            ),
            normalized_level=level,
            not_relevant=False,
            recommend_suppress=False,
        )

        return skill


    def test_locked_threshold_is_fifty(
        self,
    ):
        self.assertEqual(
            CORE_COMPETENCY_MINIMUM_IMPORTANCE,
            Decimal("50.00"),
        )


    def test_policy_boundary_is_inclusive(
        self,
    ):
        self.assertFalse(
            meets_core_competency_importance(
                Decimal("49.99")
            )
        )

        self.assertTrue(
            meets_core_competency_importance(
                Decimal("50.00")
            )
        )

        self.assertTrue(
            meets_core_competency_importance(
                Decimal("75.00")
            )
        )


    def test_recommendation_loader_excludes_below_threshold(
        self,
    ):
        results = (
            load_weighted_competencies(
                career_id=self.career.id,
            )
        )

        names = tuple(
            result.skill_name
            for result in results
        )

        self.assertNotIn(
            self.low_skill.name,
            names,
        )

        self.assertIn(
            self.boundary_skill.name,
            names,
        )

        self.assertIn(
            self.high_skill.name,
            names,
        )

        self.assertTrue(
            all(
                result.importance
                >= CORE_COMPETENCY_MINIMUM_IMPORTANCE
                for result in results
            )
        )


    def test_readiness_loader_excludes_below_threshold(
        self,
    ):
        results = (
            load_career_readiness_requirements(
                career_id=self.career.id,
            )
        )

        names = tuple(
            result.skill_name
            for result in results
        )

        self.assertNotIn(
            self.low_skill.name,
            names,
        )

        self.assertIn(
            self.boundary_skill.name,
            names,
        )

        self.assertIn(
            self.high_skill.name,
            names,
        )

        self.assertTrue(
            all(
                result.importance
                >= CORE_COMPETENCY_MINIMUM_IMPORTANCE
                for result in results
            )
        )


    def test_career_without_numerical_evidence_returns_empty(
        self,
    ):
        career = Career.objects.create(
            name=(
                "Technology Evidence Only Career"
            ),
            active=True,
        )

        technology = Skill.objects.create(
            name="Technology Only Skill",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        career_skill = (
            CareerSkill.objects.create(
                career=career,
                skill=technology,
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=self.dataset,
            external_occupation_id=(
                "99-9999.98"
            ),
            external_skill_id="TECH",
            source_domain=(
                "onet_software_skills"
            ),
            not_relevant=False,
            recommend_suppress=False,
            in_demand=True,
            in_demand_percentage=(
                Decimal("25.00")
            ),
        )

        self.assertEqual(
            load_weighted_competencies(
                career_id=career.id,
            ),
            (),
        )

        self.assertEqual(
            load_career_readiness_requirements(
                career_id=career.id,
            ),
            (),
        )
