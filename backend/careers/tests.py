from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from careers.models import (
    Career,
    CareerSkill,
    CareerSkillEvidence,
    ReferenceDataset,
    ReferenceSource,
    ReviewStatus,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)

from careers.services.recommendation_scoring import (
    RecommendationResult,
    ScoreStatus,
    WeightedCompetency,
    calculate_career_fit,
    generate_recommendations,
    load_explanation_evidence_by_career,
    load_student_skill_ids,
    load_weighted_competencies,
    load_weighted_competencies_by_career,
    rank_recommendation_results,
)

from careers.services.readiness_scoring import (
    CareerNotAvailableError,
    CareerNotFoundError,
    CareerReadinessRequirement,
    GapStatus,
    ReadinessStatus,
    calculate_career_readiness,
    calculate_selected_career_readiness,
    calculate_skill_gap,
    load_career_readiness_requirements,
    load_student_proficiencies,
    map_student_proficiency,
    order_skill_gaps,
)


class CalculateCareerFitTests(SimpleTestCase):
    """
    Tests the pure WBS 5.3 Career-fit calculation.

    These tests do not use the database.

    Database integration tests will be added after the core
    numerical behaviour is verified.
    """

    def setUp(self):
        self.competencies = (
            WeightedCompetency(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance=Decimal("80"),
            ),
            WeightedCompetency(
                career_skill_id=102,
                skill_id=2,
                skill_name="Critical Thinking",
                importance=Decimal("60"),
            ),
            WeightedCompetency(
                career_skill_id=103,
                skill_id=3,
                skill_name="Systems Analysis",
                importance=Decimal("40"),
            ),
        )

    def test_full_match_returns_100_percent(self):
        """
        Matching every weighted competency should return 100.00.
        """

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[
                1,
                2,
                3,
            ],
            weighted_competencies=(
                self.competencies
            ),
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.recommendation_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.matched_weight,
            Decimal("180"),
        )

        self.assertEqual(
            result.total_weight,
            Decimal("180"),
        )

        self.assertEqual(
            result.missing_competencies,
            (),
        )

    def test_partial_match_uses_weighted_coverage(self):
        """
        Matching 140 of 180 total weight should return 77.78.
        """

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[
                1,
                2,
            ],
            weighted_competencies=(
                self.competencies
            ),
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.matched_weight,
            Decimal("140"),
        )

        self.assertEqual(
            result.total_weight,
            Decimal("180"),
        )

        self.assertEqual(
            result.recommendation_score,
            Decimal("77.78"),
        )

        self.assertEqual(
            result.matched_competencies,
            (
                "Critical Thinking",
                "Programming",
            ),
        )

        self.assertEqual(
            result.missing_competencies,
            (
                "Systems Analysis",
            ),
        )

    def test_no_matching_skills_returns_zero(self):
        """
        A valid Career with no Student matches should score 0.00.
        """

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[
                999,
            ],
            weighted_competencies=(
                self.competencies
            ),
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.matched_weight,
            Decimal("0"),
        )

        self.assertEqual(
            result.total_weight,
            Decimal("180"),
        )

        self.assertEqual(
            result.recommendation_score,
            Decimal("0.00"),
        )

    def test_no_student_skills_returns_insufficient_profile(self):
        """
        An empty Student Skill set should not produce zero rankings.
        """

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[],
            weighted_competencies=(
                self.competencies
            ),
        )

        self.assertEqual(
            result,
            RecommendationResult(
                career_id=1,
                career_name="Software Engineer",
                score_status=(
                    ScoreStatus.INSUFFICIENT_PROFILE
                ),
            ),
        )

    def test_no_numerical_evidence_returns_insufficient_evidence(self):
        """
        A Career without numerical evidence should receive null score.
        """

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[
                1,
            ],
            weighted_competencies=[],
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.recommendation_score
        )

    def test_zero_total_weight_returns_insufficient_evidence(self):
        """
        Zero-weight evidence cannot produce a meaningful ratio.
        """

        competencies = (
            WeightedCompetency(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance=Decimal("0"),
            ),
        )

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[
                1,
            ],
            weighted_competencies=competencies,
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.recommendation_score
        )

    def test_duplicate_career_skill_evidence_is_rejected(self):
        """
        The same CareerSkill must not contribute weight twice.
        """

        competencies = (
            WeightedCompetency(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance=Decimal("80"),
            ),
            WeightedCompetency(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance=Decimal("80"),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate numerical CareerSkill evidence",
        ):
            calculate_career_fit(
                career_id=1,
                career_name="Software Engineer",
                student_skill_ids=[
                    1,
                ],
                weighted_competencies=(
                    competencies
                ),
            )

    def test_importance_above_100_is_rejected(self):
        """
        Normalized Importance must stay within 0 to 100.
        """

        competencies = (
            WeightedCompetency(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance=Decimal("100.01"),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Importance must be between 0 and 100",
        ):
            calculate_career_fit(
                career_id=1,
                career_name="Software Engineer",
                student_skill_ids=[
                    1,
                ],
                weighted_competencies=(
                    competencies
                ),
            )

    def test_negative_importance_is_rejected(self):
        """
        Negative normalized Importance must be rejected.
        """

        competencies = (
            WeightedCompetency(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance=Decimal("-0.01"),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Importance must be between 0 and 100",
        ):
            calculate_career_fit(
                career_id=1,
                career_name="Software Engineer",
                student_skill_ids=[
                    1,
                ],
                weighted_competencies=(
                    competencies
                ),
            )

    def test_duplicate_student_skill_ids_do_not_double_count(self):
        """
        Duplicate Student Skill IDs must not increase matched weight.
        """

        result = calculate_career_fit(
            career_id=1,
            career_name="Software Engineer",
            student_skill_ids=[
                1,
                1,
                1,
            ],
            weighted_competencies=(
                self.competencies
            ),
        )

        self.assertEqual(
            result.matched_weight,
            Decimal("80"),
        )

        self.assertEqual(
            result.recommendation_score,
            Decimal("44.44"),
        )


class RecommendationScoringDatabaseFixtureMixin:
    """
    Shared Django database fixtures for WBS 5.3 tests.

    This class contains setup and helper methods only.

    It does not contain test methods, so Django does not
    execute duplicate tests through inheritance.
    """

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "wbs53-integration"
                    "@example.com"
                ),
                password="test-password",
            )
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user
            )
        )

        self.student_skill = (
            Skill.objects.create(
                name="Database Integration Skill",
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        self.student_knowledge = (
            Skill.objects.create(
                name="Database Integration Knowledge",
                concept_type=(
                    Skill.ConceptType.KNOWLEDGE
                ),
            )
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.student_skill,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .FOUNDATIONAL
            ),
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.student_knowledge,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .ADVANCED
            ),
        )

        self.onet_source = (
            ReferenceSource.objects.create(
                name="O*NET Database"
            )
        )

        self.onet_dataset = (
            ReferenceDataset.objects.create(
                source=self.onet_source,
                version="31.0-test",
                retrieved_at=date(
                    2026,
                    8,
                    30,
                ),
                status=(
                    ReferenceDataset
                    .Status
                    .ACTIVE
                ),
            )
        )

        self.superseded_onet_dataset = (
            ReferenceDataset.objects.create(
                source=self.onet_source,
                version="30.0-test",
                retrieved_at=date(
                    2026,
                    8,
                    30,
                ),
                status=(
                    ReferenceDataset
                    .Status
                    .SUPERSEDED
                ),
            )
        )

        self.esco_source = (
            ReferenceSource.objects.create(
                name="ESCO"
            )
        )

        self.esco_dataset = (
            ReferenceDataset.objects.create(
                source=self.esco_source,
                version="1.2.1-test",
                retrieved_at=date(
                    2026,
                    8,
                    30,
                ),
                status=(
                    ReferenceDataset
                    .Status
                    .ACTIVE
                ),
            )
        )

        self.career = Career.objects.create(
            name="Integration Test Career"
        )

    def _create_skill(
        self,
        name,
        concept_type=Skill.ConceptType.SKILL,
    ):
        return Skill.objects.create(
            name=name,
            concept_type=concept_type,
        )

    def _create_evidence(
        self,
        *,
        skill,
        importance=Decimal("80"),
        source_domain=(
            "onet_essential_skills"
        ),
        dataset=None,
        review_status=ReviewStatus.APPROVED,
        not_relevant=False,
        recommend_suppress=None,
    ):
        if dataset is None:
            dataset = self.onet_dataset

        career_skill = (
            CareerSkill.objects.create(
                career=self.career,
                skill=skill,
                review_status=review_status,
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=dataset,
            source_domain=source_domain,
            normalized_importance=importance,
            not_relevant=not_relevant,
            recommend_suppress=(
                recommend_suppress
            ),
        )

        return career_skill



class RecommendationScoringDatabaseTests(
    RecommendationScoringDatabaseFixtureMixin,
    TestCase,
):
    """
    Database integration tests for WBS 5.3 scoring loaders.

    These tests verify the connection between Django models
    and the pure recommendation calculation.
    """

    def test_load_student_skill_ids_returns_canonical_ids(self):
        """
        StudentSkill loader returns canonical Skill IDs
        in deterministic order.
        """

        result = load_student_skill_ids(
            student_profile_id=(
                self.profile.id
            )
        )

        self.assertEqual(
            result,
            tuple(
                sorted(
                    (
                        self.student_skill.id,
                        self.student_knowledge.id,
                    )
                )
            ),
        )

    def test_loader_accepts_only_numerical_onet_domains(self):
        """
        Essential, Knowledge, and Transferable Skills
        enter numerical scoring.

        O*NET software technology evidence stays outside
        the numerical Career-fit score.
        """

        essential_skill = self._create_skill(
            "Essential Skill"
        )

        knowledge_skill = self._create_skill(
            "Knowledge Skill",
            Skill.ConceptType.KNOWLEDGE,
        )

        transferable_skill = self._create_skill(
            "Transferable Skill"
        )

        software_skill = self._create_skill(
            "Software Technology",
            Skill.ConceptType.TECHNOLOGY,
        )

        self._create_evidence(
            skill=essential_skill,
            importance=Decimal("80"),
            source_domain=(
                "onet_essential_skills"
            ),
        )

        self._create_evidence(
            skill=knowledge_skill,
            importance=Decimal("70"),
            source_domain="onet_knowledge",
        )

        self._create_evidence(
            skill=transferable_skill,
            importance=Decimal("60"),
            source_domain=(
                "onet_transferable_skills"
            ),
        )

        # A synthetic numerical value is supplied here
        # to prove the loader still excludes software
        # from the Version 1 numerical formula.
        self._create_evidence(
            skill=software_skill,
            importance=Decimal("100"),
            source_domain=(
                "onet_software_skills"
            ),
        )

        result = load_weighted_competencies(
            career_id=self.career.id
        )

        self.assertEqual(
            tuple(
                item.skill_id
                for item in result
            ),
            (
                essential_skill.id,
                knowledge_skill.id,
                transferable_skill.id,
            ),
        )

        self.assertEqual(
            tuple(
                item.importance
                for item in result
            ),
            (
                Decimal("80"),
                Decimal("70"),
                Decimal("60"),
            ),
        )

    def test_loader_excludes_ineligible_evidence(self):
        """
        Only active, approved, relevant numerical
        O*NET evidence enters Version 1 scoring.
        """

        eligible_skill = self._create_skill(
            "Eligible Skill"
        )

        pending_skill = self._create_skill(
            "Pending Skill"
        )

        esco_skill = self._create_skill(
            "ESCO Skill"
        )

        superseded_skill = self._create_skill(
            "Superseded Skill"
        )

        not_relevant_skill = self._create_skill(
            "Not Relevant Skill"
        )

        suppressed_skill = self._create_skill(
            "Suppressed Skill"
        )

        no_importance_skill = self._create_skill(
            "No Importance Skill"
        )

        self._create_evidence(
            skill=eligible_skill,
            importance=Decimal("75"),
        )

        self._create_evidence(
            skill=pending_skill,
            importance=Decimal("90"),
            review_status=(
                ReviewStatus.PENDING
            ),
        )

        self._create_evidence(
            skill=esco_skill,
            importance=Decimal("95"),
            dataset=self.esco_dataset,
        )

        self._create_evidence(
            skill=superseded_skill,
            importance=Decimal("85"),
            dataset=(
                self.superseded_onet_dataset
            ),
        )

        self._create_evidence(
            skill=not_relevant_skill,
            importance=Decimal("80"),
            not_relevant=True,
        )

        self._create_evidence(
            skill=suppressed_skill,
            importance=Decimal("80"),
            recommend_suppress=True,
        )

        self._create_evidence(
            skill=no_importance_skill,
            importance=None,
        )

        result = load_weighted_competencies(
            career_id=self.career.id
        )

        self.assertEqual(
            len(result),
            1,
        )

        self.assertEqual(
            result[0].skill_id,
            eligible_skill.id,
        )

        self.assertEqual(
            result[0].importance,
            Decimal("75"),
        )

    def test_database_loaders_feed_pure_scoring_function(self):
        """
        Real Django model records feed the tested pure
        scoring function without changing its formula.
        """

        unmatched_skill = self._create_skill(
            "Unmatched Integration Skill"
        )

        self._create_evidence(
            skill=self.student_skill,
            importance=Decimal("70"),
        )

        self._create_evidence(
            skill=self.student_knowledge,
            importance=Decimal("20"),
            source_domain="onet_knowledge",
        )

        self._create_evidence(
            skill=unmatched_skill,
            importance=Decimal("10"),
            source_domain=(
                "onet_transferable_skills"
            ),
        )

        student_skill_ids = (
            load_student_skill_ids(
                student_profile_id=(
                    self.profile.id
                )
            )
        )

        competencies = (
            load_weighted_competencies(
                career_id=self.career.id
            )
        )

        result = calculate_career_fit(
            career_id=self.career.id,
            career_name=self.career.name,
            student_skill_ids=(
                student_skill_ids
            ),
            weighted_competencies=(
                competencies
            ),
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.matched_weight,
            Decimal("90"),
        )

        self.assertEqual(
            result.total_weight,
            Decimal("100"),
        )

        self.assertEqual(
            result.recommendation_score,
            Decimal("90.00"),
        )


class RecommendationRankingTests(SimpleTestCase):
    """
    Tests deterministic WBS 5.3 Career ranking.

    Ranking uses the unrounded weighted ratio rather than
    the displayed two-decimal recommendation score.
    """

    def _result(
        self,
        *,
        career_id,
        career_name,
        matched_weight,
        total_weight,
        displayed_score,
    ):
        return RecommendationResult(
            career_id=career_id,
            career_name=career_name,
            score_status=ScoreStatus.SCORED,
            recommendation_score=Decimal(
                displayed_score
            ),
            matched_weight=Decimal(
                matched_weight
            ),
            total_weight=Decimal(
                total_weight
            ),
        )

    def test_higher_score_ranks_first(self):
        """
        Higher weighted Career-fit coverage receives
        the better rank.
        """

        lower = self._result(
            career_id=1,
            career_name="Career A",
            matched_weight="50",
            total_weight="100",
            displayed_score="50.00",
        )

        higher = self._result(
            career_id=2,
            career_name="Career B",
            matched_weight="80",
            total_weight="100",
            displayed_score="80.00",
        )

        ranked = rank_recommendation_results(
            (
                lower,
                higher,
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            2,
        )

        self.assertEqual(
            ranked[0].rank,
            1,
        )

        self.assertEqual(
            ranked[1].career_id,
            1,
        )

        self.assertEqual(
            ranked[1].rank,
            2,
        )

    def test_unrounded_ratio_controls_ranking(self):
        """
        Two displayed scores can be equal after rounding.

        The higher unrounded ratio must rank first.
        """

        first = self._result(
            career_id=1,
            career_name="Career A",
            matched_weight="1",
            total_weight="3",
            displayed_score="33.33",
        )

        second = self._result(
            career_id=2,
            career_name="Career B",
            matched_weight="33334",
            total_weight="100000",
            displayed_score="33.33",
        )

        ranked = rank_recommendation_results(
            (
                first,
                second,
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            2,
        )

        self.assertEqual(
            ranked[1].career_id,
            1,
        )

    def test_equal_ratio_uses_career_name(self):
        """
        Exact score ties use Career name alphabetically.
        """

        beta = self._result(
            career_id=1,
            career_name="Beta Career",
            matched_weight="50",
            total_weight="100",
            displayed_score="50.00",
        )

        alpha = self._result(
            career_id=2,
            career_name="Alpha Career",
            matched_weight="1",
            total_weight="2",
            displayed_score="50.00",
        )

        ranked = rank_recommendation_results(
            (
                beta,
                alpha,
            )
        )

        self.assertEqual(
            ranked[0].career_name,
            "Alpha Career",
        )

        self.assertEqual(
            ranked[1].career_name,
            "Beta Career",
        )

    def test_equal_ratio_and_name_uses_career_id(self):
        """
        Career ID resolves a tie after score and name.
        """

        higher_id = self._result(
            career_id=20,
            career_name="Same Career",
            matched_weight="50",
            total_weight="100",
            displayed_score="50.00",
        )

        lower_id = self._result(
            career_id=10,
            career_name="Same Career",
            matched_weight="1",
            total_weight="2",
            displayed_score="50.00",
        )

        ranked = rank_recommendation_results(
            (
                higher_id,
                lower_id,
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            10,
        )

        self.assertEqual(
            ranked[1].career_id,
            20,
        )

    def test_insufficient_evidence_is_not_ranked(self):
        """
        A Career without numerical evidence stays
        outside the numerical ranking.
        """

        scored = self._result(
            career_id=1,
            career_name="Scored Career",
            matched_weight="50",
            total_weight="100",
            displayed_score="50.00",
        )

        insufficient = RecommendationResult(
            career_id=2,
            career_name="Unscored Career",
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

        ranked = rank_recommendation_results(
            (
                insufficient,
                scored,
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            1,
        )

        self.assertEqual(
            ranked[0].rank,
            1,
        )

        self.assertEqual(
            ranked[1].career_id,
            2,
        )

        self.assertIsNone(
            ranked[1].rank
        )

    def test_invalid_scored_result_is_rejected(self):
        """
        A result marked scored must contain valid
        numerical ranking information.
        """

        invalid = RecommendationResult(
            career_id=1,
            career_name="Invalid Career",
            score_status=ScoreStatus.SCORED,
            recommendation_score=Decimal(
                "0.00"
            ),
            matched_weight=Decimal(
                "0"
            ),
            total_weight=Decimal(
                "0"
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "total_weight greater than zero",
        ):
            rank_recommendation_results(
                (
                    invalid,
                )
            )


class RecommendationOrchestrationTests(
    RecommendationScoringDatabaseFixtureMixin,
    TestCase,
):
    """
    Integration tests for complete WBS 5.3 recommendation generation.
    """

    def test_multi_career_loader_groups_evidence(self):
        """
        Numerical evidence is grouped under the correct Career.
        """

        second_career = Career.objects.create(
            name="Second Integration Career"
        )

        first_skill = self._create_skill(
            "First Grouped Skill"
        )

        second_skill = self._create_skill(
            "Second Grouped Skill"
        )

        self._create_evidence(
            skill=first_skill,
            importance=Decimal("80"),
        )

        second_career_skill = (
            CareerSkill.objects.create(
                career=second_career,
                skill=second_skill,
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=second_career_skill,
            dataset=self.onet_dataset,
            source_domain=(
                "onet_essential_skills"
            ),
            normalized_importance=(
                Decimal("70")
            ),
        )

        grouped = (
            load_weighted_competencies_by_career(
                career_ids=(
                    self.career.id,
                    second_career.id,
                )
            )
        )

        self.assertEqual(
            len(
                grouped[
                    self.career.id
                ]
            ),
            1,
        )

        self.assertEqual(
            grouped[
                self.career.id
            ][0].skill_id,
            first_skill.id,
        )

        self.assertEqual(
            len(
                grouped[
                    second_career.id
                ]
            ),
            1,
        )

        self.assertEqual(
            grouped[
                second_career.id
            ][0].skill_id,
            second_skill.id,
        )

    def test_generate_recommendations_ranks_active_careers(self):
        """
        Active Careers are scored and ranked by weighted coverage.
        """

        second_career = Career.objects.create(
            name="Higher Match Career"
        )

        first_missing_skill = self._create_skill(
            "First Missing Skill"
        )

        second_matched_skill = (
            self.student_skill
        )

        self._create_evidence(
            skill=first_missing_skill,
            importance=Decimal("100"),
        )

        second_career_skill = (
            CareerSkill.objects.create(
                career=second_career,
                skill=second_matched_skill,
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=second_career_skill,
            dataset=self.onet_dataset,
            source_domain=(
                "onet_essential_skills"
            ),
            normalized_importance=(
                Decimal("100")
            ),
        )

        results = generate_recommendations(
            student_profile_id=(
                self.profile.id
            )
        )

        self.assertEqual(
            len(results),
            2,
        )

        self.assertEqual(
            results[0].career_id,
            second_career.id,
        )

        self.assertEqual(
            results[0].recommendation_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            results[0].rank,
            1,
        )

        self.assertEqual(
            results[1].career_id,
            self.career.id,
        )

        self.assertEqual(
            results[1].recommendation_score,
            Decimal("0.00"),
        )

        self.assertEqual(
            results[1].rank,
            2,
        )

    def test_inactive_career_is_excluded(self):
        """
        Inactive Careers do not enter recommendation results.
        """

        inactive = Career.objects.create(
            name="Inactive Career",
            active=False,
        )

        inactive_skill = self._create_skill(
            "Inactive Career Skill"
        )

        inactive_career_skill = (
            CareerSkill.objects.create(
                career=inactive,
                skill=inactive_skill,
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=inactive_career_skill,
            dataset=self.onet_dataset,
            source_domain=(
                "onet_essential_skills"
            ),
            normalized_importance=(
                Decimal("100")
            ),
        )

        results = generate_recommendations(
            student_profile_id=(
                self.profile.id
            )
        )

        result_ids = {
            result.career_id
            for result in results
        }

        self.assertNotIn(
            inactive.id,
            result_ids,
        )

    def test_career_without_evidence_is_unranked(self):
        """
        An active Career without numerical evidence stays visible
        with insufficient-evidence status and no rank.
        """

        scored_career = Career.objects.create(
            name="Scored Career"
        )

        scored_career_skill = (
            CareerSkill.objects.create(
                career=scored_career,
                skill=self.student_skill,
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=scored_career_skill,
            dataset=self.onet_dataset,
            source_domain=(
                "onet_essential_skills"
            ),
            normalized_importance=(
                Decimal("100")
            ),
        )

        results = generate_recommendations(
            student_profile_id=(
                self.profile.id
            )
        )

        result_by_id = {
            result.career_id: result
            for result in results
        }

        self.assertEqual(
            result_by_id[
                scored_career.id
            ].rank,
            1,
        )

        self.assertEqual(
            result_by_id[
                self.career.id
            ].score_status,
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result_by_id[
                self.career.id
            ].recommendation_score
        )

        self.assertIsNone(
            result_by_id[
                self.career.id
            ].rank
        )

    def test_no_student_skills_marks_all_active_careers_insufficient(self):
        """
        Empty Student Skills produce insufficient-profile results,
        not misleading zero-score rankings.
        """

        StudentSkill.objects.filter(
            student_profile=self.profile
        ).delete()

        Career.objects.create(
            name="Another Active Career"
        )

        results = generate_recommendations(
            student_profile_id=(
                self.profile.id
            )
        )

        self.assertEqual(
            len(results),
            2,
        )

        for result in results:
            self.assertEqual(
                result.score_status,
                ScoreStatus.INSUFFICIENT_PROFILE,
            )

            self.assertIsNone(
                result.recommendation_score
            )

            self.assertIsNone(
                result.rank
            )

    def test_no_active_careers_returns_empty_tuple(self):
        """
        No active Careers produces an empty deterministic result.
        """

        Career.objects.update(
            active=False
        )

        results = generate_recommendations(
            student_profile_id=(
                self.profile.id
            )
        )

        self.assertEqual(
            results,
            (),
        )


class RecommendationExplanationTests(
    RecommendationScoringDatabaseFixtureMixin,
    TestCase,
):
    """
    Tests WBS 5.3 non-numerical explanation evidence.
    """

    def _add_student_skill(
        self,
        *,
        skill,
    ):
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .FOUNDATIONAL
            ),
        )

    def _create_career_skill(
        self,
        *,
        skill,
    ):
        return CareerSkill.objects.create(
            career=self.career,
            skill=skill,
            review_status=(
                ReviewStatus.APPROVED
            ),
        )

    def test_matched_onet_technology_is_returned(self):
        """
        Matched O*NET software evidence appears as
        explanation data.
        """

        technology = self._create_skill(
            "Integration Python",
            Skill.ConceptType.TECHNOLOGY,
        )

        self._add_student_skill(
            skill=technology
        )

        career_skill = (
            self._create_career_skill(
                skill=technology
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=self.onet_dataset,
            source_domain=(
                "onet_software_skills"
            ),
        )

        result = (
            load_explanation_evidence_by_career(
                career_ids=(
                    self.career.id,
                ),
                student_skill_ids=(
                    technology.id,
                ),
            )
        )

        self.assertEqual(
            result[
                self.career.id
            ].matched_technologies,
            (
                "Integration Python",
            ),
        )

    def test_esco_essential_and_optional_matches_are_separated(self):
        """
        ESCO essential and optional matches stay
        separate in explanation data.
        """

        essential = self._create_skill(
            "Essential Explanation Skill"
        )

        optional = self._create_skill(
            "Optional Explanation Skill"
        )

        self._add_student_skill(
            skill=essential
        )

        self._add_student_skill(
            skill=optional
        )

        essential_career_skill = (
            self._create_career_skill(
                skill=essential
            )
        )

        optional_career_skill = (
            self._create_career_skill(
                skill=optional
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=(
                essential_career_skill
            ),
            dataset=self.esco_dataset,
            source_relation="essential",
        )

        CareerSkillEvidence.objects.create(
            career_skill=(
                optional_career_skill
            ),
            dataset=self.esco_dataset,
            source_relation="optional",
        )

        result = (
            load_explanation_evidence_by_career(
                career_ids=(
                    self.career.id,
                ),
                student_skill_ids=(
                    essential.id,
                    optional.id,
                ),
            )[
                self.career.id
            ]
        )

        self.assertEqual(
            result.esco_essential_skills,
            (
                "Essential Explanation Skill",
            ),
        )

        self.assertEqual(
            result.esco_optional_skills,
            (
                "Optional Explanation Skill",
            ),
        )

    def test_unmatched_explanation_skill_is_not_returned(self):
        """
        Career evidence does not count as a match unless
        the Student owns the same canonical Skill.
        """

        technology = self._create_skill(
            "Unmatched Technology",
            Skill.ConceptType.TECHNOLOGY,
        )

        career_skill = (
            self._create_career_skill(
                skill=technology
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=self.onet_dataset,
            source_domain=(
                "onet_software_skills"
            ),
        )

        result = (
            load_explanation_evidence_by_career(
                career_ids=(
                    self.career.id,
                ),
                student_skill_ids=(
                    self.student_skill.id,
                ),
            )[
                self.career.id
            ]
        )

        self.assertEqual(
            result.matched_technologies,
            (),
        )

    def test_explanation_evidence_does_not_change_score_or_rank(self):
        """
        Technology and ESCO evidence enrich explanations
        without changing WBS 5.3 numerical scoring.
        """

        numerical_career_skill = (
            self._create_career_skill(
                skill=self.student_skill
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=(
                numerical_career_skill
            ),
            dataset=self.onet_dataset,
            source_domain=(
                "onet_essential_skills"
            ),
            normalized_importance=(
                Decimal("100")
            ),
        )

        technology = self._create_skill(
            "Explanation Technology",
            Skill.ConceptType.TECHNOLOGY,
        )

        self._add_student_skill(
            skill=technology
        )

        technology_career_skill = (
            self._create_career_skill(
                skill=technology
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=(
                technology_career_skill
            ),
            dataset=self.onet_dataset,
            source_domain=(
                "onet_software_skills"
            ),
        )

        CareerSkillEvidence.objects.create(
            career_skill=(
                technology_career_skill
            ),
            dataset=self.esco_dataset,
            source_relation="essential",
        )

        results = generate_recommendations(
            student_profile_id=(
                self.profile.id
            )
        )

        result = next(
            item
            for item in results
            if item.career_id
            == self.career.id
        )

        self.assertEqual(
            result.recommendation_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.rank,
            1,
        )

        self.assertEqual(
            result.matched_technologies,
            (
                "Explanation Technology",
            ),
        )

        self.assertEqual(
            result.esco_essential_skills,
            (
                "Explanation Technology",
            ),
        )

        self.assertEqual(
            result.esco_essential_matches,
            1,
        )

        self.assertEqual(
            result.esco_optional_matches,
            0,
        )


class CalculateSkillGapTests(SimpleTestCase):
    """
    Tests the pure WBS 5.5 per-Skill readiness calculation.

    These tests do not use the database.
    """

    def make_requirement(
        self,
        *,
        career_skill_id=201,
        skill_id=21,
        skill_name="Systems Analysis",
        concept_type="skill",
        source_domain="onet_transferable_skills",
        importance=Decimal("80"),
        required_level=Decimal("80"),
    ):
        return CareerReadinessRequirement(
            career_skill_id=career_skill_id,
            skill_id=skill_id,
            skill_name=skill_name,
            concept_type=concept_type,
            source_domain=source_domain,
            importance=importance,
            required_level=required_level,
        )

    def test_foundational_maps_to_25(self):
        self.assertEqual(
            map_student_proficiency(
                "foundational"
            ),
            Decimal("25"),
        )

    def test_developing_maps_to_50(self):
        self.assertEqual(
            map_student_proficiency(
                "developing"
            ),
            Decimal("50"),
        )

    def test_proficient_maps_to_75(self):
        self.assertEqual(
            map_student_proficiency(
                "proficient"
            ),
            Decimal("75"),
        )

    def test_advanced_maps_to_100(self):
        self.assertEqual(
            map_student_proficiency(
                "advanced"
            ),
            Decimal("100"),
        )

    def test_missing_skill_maps_to_zero(self):
        self.assertEqual(
            map_student_proficiency(
                None
            ),
            Decimal("0"),
        )

    def test_invalid_proficiency_is_rejected(self):
        with self.assertRaises(
            ValueError
        ):
            map_student_proficiency(
                "expert"
            )

    def test_missing_skill_returns_missing_gap(self):
        requirement = self.make_requirement(
            required_level=Decimal("60"),
        )

        result = calculate_skill_gap(
            requirement=requirement,
            student_proficiency_level=None,
        )

        self.assertEqual(
            result.gap_status,
            GapStatus.MISSING,
        )

        self.assertEqual(
            result.student_proficiency_score,
            Decimal("0"),
        )

        self.assertEqual(
            result.gap_amount,
            Decimal("60.00"),
        )

        self.assertEqual(
            result.attainment_ratio,
            Decimal("0"),
        )

        self.assertEqual(
            result.attainment_percentage,
            Decimal("0.00"),
        )

        self.assertEqual(
            result.weighted_contribution,
            Decimal("0"),
        )

    def test_below_requirement_receives_partial_attainment(self):
        requirement = self.make_requirement(
            importance=Decimal("80"),
            required_level=Decimal("80"),
        )

        result = calculate_skill_gap(
            requirement=requirement,
            student_proficiency_level=(
                "developing"
            ),
        )

        self.assertEqual(
            result.gap_status,
            GapStatus.BELOW_REQUIREMENT,
        )

        self.assertEqual(
            result.student_proficiency_score,
            Decimal("50"),
        )

        self.assertEqual(
            result.gap_amount,
            Decimal("30.00"),
        )

        self.assertEqual(
            result.attainment_ratio,
            Decimal("0.625"),
        )

        self.assertEqual(
            result.attainment_percentage,
            Decimal("62.50"),
        )

        self.assertEqual(
            result.weighted_contribution,
            Decimal("50.000"),
        )

    def test_exact_requirement_is_met(self):
        requirement = self.make_requirement(
            importance=Decimal("70"),
            required_level=Decimal("50"),
        )

        result = calculate_skill_gap(
            requirement=requirement,
            student_proficiency_level=(
                "developing"
            ),
        )

        self.assertEqual(
            result.gap_status,
            GapStatus.MEETS_REQUIREMENT,
        )

        self.assertEqual(
            result.gap_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            result.attainment_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.attainment_percentage,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.weighted_contribution,
            Decimal("70"),
        )

    def test_attainment_is_capped_at_one(self):
        requirement = self.make_requirement(
            importance=Decimal("60"),
            required_level=Decimal("50"),
        )

        result = calculate_skill_gap(
            requirement=requirement,
            student_proficiency_level=(
                "proficient"
            ),
        )

        self.assertEqual(
            result.gap_status,
            GapStatus.MEETS_REQUIREMENT,
        )

        self.assertEqual(
            result.attainment_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.attainment_percentage,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.weighted_contribution,
            Decimal("60"),
        )

    def test_negative_importance_is_rejected(self):
        requirement = self.make_requirement(
            importance=Decimal("-1"),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )

    def test_importance_above_100_is_rejected(self):
        requirement = self.make_requirement(
            importance=Decimal("100.01"),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )

    def test_zero_required_level_is_rejected(self):
        requirement = self.make_requirement(
            required_level=Decimal("0"),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )

    def test_required_level_above_100_is_rejected(self):
        requirement = self.make_requirement(
            required_level=Decimal("100.01"),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )

    def test_technology_requirement_is_rejected(self):
        requirement = self.make_requirement(
            concept_type="technology",
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )

    def test_unsupported_source_domain_is_rejected(self):
        requirement = self.make_requirement(
            source_domain=(
                "onet_software_skills"
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )

    def test_blank_skill_name_is_rejected(self):
        requirement = self.make_requirement(
            skill_name="   ",
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    "developing"
                ),
            )


class CalculateCareerReadinessTests(SimpleTestCase):
    """
    Tests the pure WBS 5.5 Career-level readiness logic.

    These tests perform no database operations.
    """

    def make_requirement(
        self,
        *,
        career_skill_id,
        skill_id,
        skill_name,
        importance,
        required_level,
        concept_type="skill",
        source_domain="onet_transferable_skills",
    ):
        return CareerReadinessRequirement(
            career_skill_id=career_skill_id,
            skill_id=skill_id,
            skill_name=skill_name,
            concept_type=concept_type,
            source_domain=source_domain,
            importance=importance,
            required_level=required_level,
        )

    def test_full_readiness_returns_100_percent(self):
        requirements = (
            self.make_requirement(
                career_skill_id=301,
                skill_id=31,
                skill_name="Skill A",
                importance=Decimal("80"),
                required_level=Decimal("50"),
            ),
            self.make_requirement(
                career_skill_id=302,
                skill_id=32,
                skill_name="Skill B",
                importance=Decimal("20"),
                required_level=Decimal("75"),
            ),
        )

        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={
                31: "advanced",
                32: "advanced",
            },
            requirements=requirements,
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.SCORED,
        )

        self.assertEqual(
            result.readiness_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.meets_requirement_count,
            2,
        )

        self.assertEqual(
            result.missing_requirement_count,
            0,
        )

    def test_partial_readiness_uses_importance_weighting(self):
        requirements = (
            self.make_requirement(
                career_skill_id=311,
                skill_id=41,
                skill_name="Skill A",
                importance=Decimal("80"),
                required_level=Decimal("80"),
            ),
            self.make_requirement(
                career_skill_id=312,
                skill_id=42,
                skill_name="Skill B",
                importance=Decimal("20"),
                required_level=Decimal("50"),
            ),
        )

        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={
                41: "developing",
                42: "proficient",
            },
            requirements=requirements,
        )

        self.assertEqual(
            result.readiness_score,
            Decimal("70.00"),
        )

        self.assertEqual(
            result.total_importance_weight,
            Decimal("100"),
        )

        self.assertEqual(
            result.weighted_attainment,
            Decimal("70.000"),
        )

        self.assertEqual(
            result.below_requirement_count,
            1,
        )

        self.assertEqual(
            result.meets_requirement_count,
            1,
        )

    def test_documented_unrelated_skills_return_zero(self):
        requirements = (
            self.make_requirement(
                career_skill_id=321,
                skill_id=51,
                skill_name="Career Skill",
                importance=Decimal("80"),
                required_level=Decimal("50"),
            ),
        )

        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={
                999: "advanced",
            },
            requirements=requirements,
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.SCORED,
        )

        self.assertEqual(
            result.readiness_score,
            Decimal("0.00"),
        )

        self.assertEqual(
            result.missing_requirement_count,
            1,
        )

    def test_empty_student_profile_is_insufficient(self):
        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={},
            requirements=(
                self.make_requirement(
                    career_skill_id=331,
                    skill_id=61,
                    skill_name="Skill A",
                    importance=Decimal("80"),
                    required_level=Decimal("50"),
                ),
            ),
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.INSUFFICIENT_PROFILE,
        )

        self.assertIsNone(
            result.readiness_score
        )

        self.assertEqual(
            result.skill_gaps,
            (),
        )

    def test_career_without_evidence_is_insufficient(self):
        result = calculate_career_readiness(
            career_id=1,
            career_name="Health Information Manager",
            student_proficiencies={
                1: "proficient",
            },
            requirements=(),
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.readiness_score
        )

    def test_zero_total_importance_is_insufficient(self):
        requirements = (
            self.make_requirement(
                career_skill_id=341,
                skill_id=71,
                skill_name="Zero Weight",
                importance=Decimal("0"),
                required_level=Decimal("50"),
            ),
        )

        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={
                71: "developing",
            },
            requirements=requirements,
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.readiness_score
        )

    def test_duplicate_career_skill_is_rejected(self):
        requirements = (
            self.make_requirement(
                career_skill_id=351,
                skill_id=81,
                skill_name="Skill A",
                importance=Decimal("70"),
                required_level=Decimal("50"),
            ),
            self.make_requirement(
                career_skill_id=351,
                skill_id=82,
                skill_name="Skill B",
                importance=Decimal("60"),
                required_level=Decimal("50"),
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_career_readiness(
                career_id=1,
                career_name="Software Engineer",
                student_proficiencies={
                    81: "proficient",
                },
                requirements=requirements,
            )

    def test_gap_order_is_deterministic(self):
        requirements = (
            self.make_requirement(
                career_skill_id=361,
                skill_id=91,
                skill_name="Met Skill",
                importance=Decimal("100"),
                required_level=Decimal("50"),
            ),
            self.make_requirement(
                career_skill_id=362,
                skill_id=92,
                skill_name="Lower Missing",
                importance=Decimal("40"),
                required_level=Decimal("80"),
            ),
            self.make_requirement(
                career_skill_id=363,
                skill_id=93,
                skill_name="Higher Missing",
                importance=Decimal("90"),
                required_level=Decimal("60"),
            ),
            self.make_requirement(
                career_skill_id=364,
                skill_id=94,
                skill_name="Below Skill",
                importance=Decimal("95"),
                required_level=Decimal("80"),
            ),
        )

        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={
                91: "advanced",
                94: "developing",
                999: "foundational",
            },
            requirements=requirements,
        )

        self.assertEqual(
            tuple(
                gap.skill_name
                for gap in result.skill_gaps
            ),
            (
                "Higher Missing",
                "Lower Missing",
                "Below Skill",
                "Met Skill",
            ),
        )

    def test_readiness_score_rounds_to_two_decimals(self):
        requirements = (
            self.make_requirement(
                career_skill_id=371,
                skill_id=101,
                skill_name="Rounded Skill",
                importance=Decimal("100"),
                required_level=Decimal("60"),
            ),
        )

        result = calculate_career_readiness(
            career_id=1,
            career_name="Software Engineer",
            student_proficiencies={
                101: "developing",
            },
            requirements=requirements,
        )

        self.assertEqual(
            result.readiness_score,
            Decimal("83.33"),
        )

    def test_invalid_career_identity_is_rejected(self):
        requirement = self.make_requirement(
            career_skill_id=381,
            skill_id=111,
            skill_name="Skill A",
            importance=Decimal("80"),
            required_level=Decimal("50"),
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_career_readiness(
                career_id=0,
                career_name="Software Engineer",
                student_proficiencies={
                    111: "proficient",
                },
                requirements=(
                    requirement,
                ),
            )

        with self.assertRaises(
            ValueError
        ):
            calculate_career_readiness(
                career_id=1,
                career_name="   ",
                student_proficiencies={
                    111: "proficient",
                },
                requirements=(
                    requirement,
                ),
            )


class ReadinessScoringDatabaseTests(
    RecommendationScoringDatabaseFixtureMixin,
    TestCase,
):
    """
    Database integration tests for WBS 5.5 readiness loaders.
    """

    def _create_readiness_evidence(
        self,
        *,
        skill,
        importance=Decimal("80"),
        required_level=Decimal("60"),
        source_domain="onet_essential_skills",
        dataset=None,
        review_status=ReviewStatus.APPROVED,
        not_relevant=False,
        recommend_suppress=None,
        career_skill=None,
        source_relation="",
        external_occupation_id="",
        external_skill_id="",
    ):
        if dataset is None:
            dataset = self.onet_dataset

        if career_skill is None:
            career_skill = (
                CareerSkill.objects.create(
                    career=self.career,
                    skill=skill,
                    review_status=(
                        review_status
                    ),
                )
            )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=dataset,
            external_occupation_id=(
                external_occupation_id
            ),
            external_skill_id=(
                external_skill_id
            ),
            source_domain=(
                source_domain
            ),
            source_relation=(
                source_relation
            ),
            normalized_importance=(
                importance
            ),
            normalized_level=(
                required_level
            ),
            not_relevant=(
                not_relevant
            ),
            recommend_suppress=(
                recommend_suppress
            ),
        )

        return career_skill

    def test_load_student_proficiencies_returns_canonical_mapping(
        self,
    ):
        result = load_student_proficiencies(
            student_profile_id=(
                self.profile.id
            )
        )

        self.assertEqual(
            result,
            {
                self.student_skill.id:
                    StudentSkill
                    .ProficiencyLevel
                    .FOUNDATIONAL,

                self.student_knowledge.id:
                    StudentSkill
                    .ProficiencyLevel
                    .ADVANCED,
            },
        )

    def test_readiness_loader_returns_importance_and_level(
        self,
    ):
        skill = self._create_skill(
            "Readiness Source Skill"
        )

        career_skill = (
            self._create_readiness_evidence(
                skill=skill,
                importance=Decimal("72.00"),
                required_level=Decimal("58.86"),
                source_domain=(
                    "onet_essential_skills"
                ),
            )
        )

        result = (
            load_career_readiness_requirements(
                career_id=self.career.id
            )
        )

        self.assertEqual(
            len(result),
            1,
        )

        self.assertEqual(
            result[0].career_skill_id,
            career_skill.id,
        )

        self.assertEqual(
            result[0].skill_id,
            skill.id,
        )

        self.assertEqual(
            result[0].importance,
            Decimal("72.00"),
        )

        self.assertEqual(
            result[0].required_level,
            Decimal("58.86"),
        )

    def test_readiness_loader_accepts_only_approved_domains_and_concepts(
        self,
    ):
        skill = self._create_skill(
            "Readiness Essential Skill"
        )

        knowledge = self._create_skill(
            "Readiness Knowledge",
            Skill.ConceptType.KNOWLEDGE,
        )

        transferable = self._create_skill(
            "Readiness Transferable Skill"
        )

        software_domain_skill = (
            self._create_skill(
                "Readiness Software Domain Skill"
            )
        )

        technology = self._create_skill(
            "Readiness Technology",
            Skill.ConceptType.TECHNOLOGY,
        )

        self._create_readiness_evidence(
            skill=skill,
            source_domain=(
                "onet_essential_skills"
            ),
        )

        self._create_readiness_evidence(
            skill=knowledge,
            source_domain=(
                "onet_knowledge"
            ),
        )

        self._create_readiness_evidence(
            skill=transferable,
            source_domain=(
                "onet_transferable_skills"
            ),
        )

        self._create_readiness_evidence(
            skill=software_domain_skill,
            source_domain=(
                "onet_software_skills"
            ),
        )

        # Synthetic numerical evidence is supplied to prove
        # technology concepts remain outside WBS 5.5 even
        # when the source-domain name is numerical.
        self._create_readiness_evidence(
            skill=technology,
            source_domain=(
                "onet_knowledge"
            ),
        )

        result = (
            load_career_readiness_requirements(
                career_id=self.career.id
            )
        )

        self.assertEqual(
            tuple(
                item.skill_id
                for item in result
            ),
            (
                skill.id,
                knowledge.id,
                transferable.id,
            ),
        )

    def test_readiness_loader_excludes_ineligible_evidence(
        self,
    ):
        eligible = self._create_skill(
            "Readiness Eligible"
        )

        pending = self._create_skill(
            "Readiness Pending"
        )

        esco = self._create_skill(
            "Readiness ESCO"
        )

        superseded = self._create_skill(
            "Readiness Superseded"
        )

        no_importance = self._create_skill(
            "Readiness No Importance"
        )

        no_level = self._create_skill(
            "Readiness No Level"
        )

        not_relevant = self._create_skill(
            "Readiness Not Relevant"
        )

        suppressed = self._create_skill(
            "Readiness Suppressed"
        )

        self._create_readiness_evidence(
            skill=eligible,
            importance=Decimal("75"),
            required_level=Decimal("60"),
        )

        self._create_readiness_evidence(
            skill=pending,
            review_status=(
                ReviewStatus.PENDING
            ),
        )

        self._create_readiness_evidence(
            skill=esco,
            dataset=self.esco_dataset,
        )

        self._create_readiness_evidence(
            skill=superseded,
            dataset=(
                self.superseded_onet_dataset
            ),
        )

        self._create_readiness_evidence(
            skill=no_importance,
            importance=None,
        )

        self._create_readiness_evidence(
            skill=no_level,
            required_level=None,
        )

        self._create_readiness_evidence(
            skill=not_relevant,
            not_relevant=True,
        )

        self._create_readiness_evidence(
            skill=suppressed,
            recommend_suppress=True,
        )

        result = (
            load_career_readiness_requirements(
                career_id=self.career.id
            )
        )

        self.assertEqual(
            tuple(
                item.skill_id
                for item in result
            ),
            (
                eligible.id,
            ),
        )

    def test_duplicate_career_skill_evidence_remains_visible(
        self,
    ):
        skill = self._create_skill(
            "Duplicate Readiness Evidence"
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

        self._create_readiness_evidence(
            skill=skill,
            career_skill=career_skill,
            importance=Decimal("80"),
            required_level=Decimal("60"),
            source_relation="first",
        )

        self._create_readiness_evidence(
            skill=skill,
            career_skill=career_skill,
            importance=Decimal("70"),
            required_level=Decimal("50"),
            source_relation="second",
        )

        result = (
            load_career_readiness_requirements(
                career_id=self.career.id
            )
        )

        self.assertEqual(
            len(result),
            2,
        )

        self.assertEqual(
            result[0].career_skill_id,
            result[1].career_skill_id,
        )

        with self.assertRaises(
            ValueError
        ):
            calculate_career_readiness(
                career_id=self.career.id,
                career_name=self.career.name,
                student_proficiencies={
                    skill.id: "proficient",
                },
                requirements=result,
            )

    def test_database_loaders_feed_pure_readiness_calculation(
        self,
    ):
        first_skill = self.student_skill

        second_skill = (
            self.student_knowledge
        )

        self._create_readiness_evidence(
            skill=first_skill,
            importance=Decimal("80"),
            required_level=Decimal("50"),
            source_domain=(
                "onet_essential_skills"
            ),
        )

        self._create_readiness_evidence(
            skill=second_skill,
            importance=Decimal("20"),
            required_level=Decimal("75"),
            source_domain=(
                "onet_knowledge"
            ),
        )

        student_proficiencies = (
            load_student_proficiencies(
                student_profile_id=(
                    self.profile.id
                )
            )
        )

        requirements = (
            load_career_readiness_requirements(
                career_id=self.career.id
            )
        )

        result = calculate_career_readiness(
            career_id=self.career.id,
            career_name=self.career.name,
            student_proficiencies=(
                student_proficiencies
            ),
            requirements=requirements,
        )

        # Foundational = 25 against Level 50:
        # 50 percent attainment on weight 80 = 40.
        #
        # Advanced = 100 against Level 75:
        # full attainment on weight 20 = 20.
        #
        # Total achieved weight = 60 of 100.
        self.assertEqual(
            result.readiness_score,
            Decimal("60.00"),
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.SCORED,
        )

        self.assertEqual(
            result.below_requirement_count,
            1,
        )

        self.assertEqual(
            result.meets_requirement_count,
            1,
        )


class ReadinessOrchestrationTests(
    RecommendationScoringDatabaseFixtureMixin,
    TestCase,
):
    """
    Tests the WBS 5.5 selected-Career orchestration layer.
    """

    def _create_readiness_evidence(
        self,
        *,
        skill,
        importance,
        required_level,
        source_domain="onet_essential_skills",
    ):
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
            dataset=self.onet_dataset,
            source_domain=source_domain,
            normalized_importance=(
                importance
            ),
            normalized_level=(
                required_level
            ),
            not_relevant=False,
        )

        return career_skill

    def test_selected_active_career_returns_readiness_result(
        self,
    ):
        self._create_readiness_evidence(
            skill=self.student_skill,
            importance=Decimal("80"),
            required_level=Decimal("50"),
        )

        self._create_readiness_evidence(
            skill=self.student_knowledge,
            importance=Decimal("20"),
            required_level=Decimal("75"),
            source_domain="onet_knowledge",
        )

        result = (
            calculate_selected_career_readiness(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=self.career.id,
            )
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.SCORED,
        )

        self.assertEqual(
            result.readiness_score,
            Decimal("60.00"),
        )

        self.assertEqual(
            result.career_id,
            self.career.id,
        )

        self.assertEqual(
            result.career_name,
            self.career.name,
        )

    def test_selected_career_without_evidence_is_insufficient(
        self,
    ):
        result = (
            calculate_selected_career_readiness(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=self.career.id,
            )
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.readiness_score
        )

    def test_empty_student_profile_is_insufficient(
        self,
    ):
        user_model = get_user_model()

        empty_user = (
            user_model.objects.create_user(
                email=(
                    "wbs55-empty-profile"
                    "@example.com"
                ),
                password="test-password",
            )
        )

        empty_profile = (
            StudentProfile.objects.create(
                user=empty_user
            )
        )

        self._create_readiness_evidence(
            skill=self.student_skill,
            importance=Decimal("80"),
            required_level=Decimal("50"),
        )

        result = (
            calculate_selected_career_readiness(
                student_profile_id=(
                    empty_profile.id
                ),
                career_id=self.career.id,
            )
        )

        self.assertEqual(
            result.score_status,
            ReadinessStatus.INSUFFICIENT_PROFILE,
        )

        self.assertIsNone(
            result.readiness_score
        )

    def test_nonexistent_career_raises_domain_error(
        self,
    ):
        missing_career_id = (
            Career.objects
            .order_by("-id")
            .first()
            .id
            + 1000
        )

        with self.assertRaises(
            CareerNotFoundError
        ):
            calculate_selected_career_readiness(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    missing_career_id
                ),
            )

    def test_inactive_career_raises_domain_error(
        self,
    ):
        inactive_career = (
            Career.objects.create(
                name="Inactive Readiness Career",
                active=False,
            )
        )

        with self.assertRaises(
            CareerNotAvailableError
        ):
            calculate_selected_career_readiness(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    inactive_career.id
                ),
            )

    def test_invalid_identifiers_are_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            calculate_selected_career_readiness(
                student_profile_id=0,
                career_id=self.career.id,
            )

        with self.assertRaises(
            ValueError
        ):
            calculate_selected_career_readiness(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=0,
            )
