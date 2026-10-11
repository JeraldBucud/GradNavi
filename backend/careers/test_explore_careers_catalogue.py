from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import (
    Career,
)
from careers.services.explore_careers import (
    EXPLORE_STATUS_EVALUATED,
    EXPLORE_STATUS_NOT_EVALUATED,
    EXPLORE_STATUS_RECOMMENDED,
    RECOMMENDED_CAREER_LIMIT,
    evaluate_career_from_snapshot,
    list_explore_career_categories,
    list_explore_careers,
    list_guidance_careers,
)
from careers.services.recommendation_cache import (
    build_recommendation_cache_key,
    store_recommendation_snapshot,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class ExploreCareersCatalogueTests(
    TestCase
):
    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "explore-catalogue@"
                    "gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user,
            )
        )

        self.careers = []

        for index in range(
            1,
            10,
        ):
            category = (
                "Technology"
                if index <= 6
                else "Business"
            )

            career = (
                Career.objects.create(
                    name=(
                        f"Catalogue Career {index:02d}"
                    ),
                    description=(
                        "Software data systems "
                        f"analysis role {index}."
                    ),
                    category=category,
                    active=True,
                )
            )

            self.careers.append(
                career
            )

        self.inactive_career = (
            Career.objects.create(
                name=(
                    "Catalogue Inactive Career"
                ),
                description=(
                    "Inactive catalogue record."
                ),
                category="Technology",
                active=False,
            )
        )

        self.cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        recommendations = []

        for rank, career in enumerate(
            self.careers,
            start=1,
        ):
            recommendations.append(
                {
                    "career_id": career.id,
                    "career_name": career.name,
                    "recommendation_score": (
                        f"{100 - rank}.00"
                    ),
                    "rank": rank,
                }
            )

        self.snapshot = (
            store_recommendation_snapshot(
                student_profile=self.profile,
                payload={
                    "scoring_model": (
                        self.cache_key
                        .scoring_version
                    ),
                    "career_count": (
                        len(
                            recommendations
                        )
                    ),
                    "recommendations": (
                        recommendations
                    ),
                },
                embedding_model=(
                    "test-embedding-model"
                ),
                prompt_tokens=0,
                total_tokens=0,
                career_count=(
                    len(
                        recommendations
                    )
                ),
                cache_key=self.cache_key,
            )
        )


    def test_catalogue_returns_all_active_careers(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
        )

        self.assertEqual(
            len(items),
            9,
        )

        ids = {
            item.career_id
            for item in items
        }

        self.assertNotIn(
            self.inactive_career.id,
            ids,
        )


    def test_top_seven_are_recommended(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
        )

        recommended = [
            item
            for item in items
            if item.recommended
        ]

        self.assertEqual(
            len(recommended),
            RECOMMENDED_CAREER_LIMIT,
        )

        expected_ids = {
            career.id
            for career in (
                self.careers[
                    :RECOMMENDED_CAREER_LIMIT
                ]
            )
        }

        actual_ids = {
            item.career_id
            for item in recommended
        }

        self.assertEqual(
            actual_ids,
            expected_ids,
        )

        self.assertTrue(
            all(
                item.status
                == EXPLORE_STATUS_RECOMMENDED
                for item in recommended
            )
        )


    def test_non_recommended_career_is_not_evaluated(
        self,
    ):
        target = self.careers[7]

        item = next(
            item
            for item in list_explore_careers(
                student_profile=self.profile,
            )
            if item.career_id
            == target.id
        )

        self.assertEqual(
            item.status,
            EXPLORE_STATUS_NOT_EVALUATED,
        )

        self.assertFalse(
            item.recommended
        )

        self.assertFalse(
            item.evaluated
        )

        self.assertIsNone(
            item.match_score
        )


    def test_explicit_evaluation_changes_catalogue_status(
        self,
    ):
        target = self.careers[7]

        evaluate_career_from_snapshot(
            student_profile=self.profile,
            career_id=target.id,
        )

        item = next(
            item
            for item in list_explore_careers(
                student_profile=self.profile,
            )
            if item.career_id
            == target.id
        )

        self.assertEqual(
            item.status,
            EXPLORE_STATUS_EVALUATED,
        )

        self.assertFalse(
            item.recommended
        )

        self.assertTrue(
            item.evaluated
        )

        self.assertEqual(
            item.match_score,
            "92.00",
        )


    def test_search_matches_career_name(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
            search="Career 09",
        )

        self.assertEqual(
            len(items),
            1,
        )

        self.assertEqual(
            items[0].career_id,
            self.careers[8].id,
        )


    def test_search_matches_description(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
            search="systems",
        )

        self.assertEqual(
            len(items),
            9,
        )


    def test_search_matches_category(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
            search="Business",
        )

        self.assertEqual(
            len(items),
            3,
        )


    def test_category_filter_is_case_insensitive(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
            category="business",
        )

        self.assertEqual(
            len(items),
            3,
        )

        self.assertTrue(
            all(
                item.category
                == "Business"
                for item in items
            )
        )


    def test_category_list_contains_active_categories(
        self,
    ):
        categories = (
            list_explore_career_categories()
        )

        self.assertEqual(
            categories,
            (
                "Business",
                "Technology",
            ),
        )


    def test_recommended_status_filter(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
            status=(
                EXPLORE_STATUS_RECOMMENDED
            ),
        )

        self.assertEqual(
            len(items),
            7,
        )

        self.assertTrue(
            all(
                item.recommended
                for item in items
            )
        )


    def test_not_evaluated_status_filter(
        self,
    ):
        items = list_explore_careers(
            student_profile=self.profile,
            status=(
                EXPLORE_STATUS_NOT_EVALUATED
            ),
        )

        self.assertEqual(
            len(items),
            2,
        )


    def test_evaluated_status_filter(
        self,
    ):
        target = self.careers[7]

        evaluate_career_from_snapshot(
            student_profile=self.profile,
            career_id=target.id,
        )

        items = list_explore_careers(
            student_profile=self.profile,
            status=(
                EXPLORE_STATUS_EVALUATED
            ),
        )

        self.assertEqual(
            len(items),
            1,
        )

        self.assertEqual(
            items[0].career_id,
            target.id,
        )


    def test_guidance_list_contains_top_seven(
        self,
    ):
        items = list_guidance_careers(
            student_profile=self.profile,
        )

        self.assertEqual(
            len(items),
            7,
        )

        self.assertEqual(
            [
                item.career_id
                for item in items
            ],
            [
                career.id
                for career in (
                    self.careers[:7]
                )
            ],
        )


    def test_guidance_list_adds_explicit_evaluation(
        self,
    ):
        target = self.careers[7]

        evaluate_career_from_snapshot(
            student_profile=self.profile,
            career_id=target.id,
        )

        items = list_guidance_careers(
            student_profile=self.profile,
        )

        self.assertEqual(
            len(items),
            8,
        )

        self.assertEqual(
            [
                item.career_id
                for item in items[:7]
            ],
            [
                career.id
                for career in (
                    self.careers[:7]
                )
            ],
        )

        self.assertEqual(
            items[7].career_id,
            target.id,
        )


    def test_stale_evaluation_leaves_guidance_list(
        self,
    ):
        target = self.careers[7]

        evaluate_career_from_snapshot(
            student_profile=self.profile,
            career_id=target.id,
        )

        skill = Skill.objects.create(
            name=(
                "Catalogue Fingerprint Skill"
            ),
            concept_type=(
                Skill.ConceptType.SKILL
            ),
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .DEVELOPING
            ),
        )

        items = list_guidance_careers(
            student_profile=self.profile,
        )

        ids = {
            item.career_id
            for item in items
        }

        self.assertNotIn(
            target.id,
            ids,
        )
