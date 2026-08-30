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
