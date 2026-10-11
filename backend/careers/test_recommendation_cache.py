from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import (
    Career,
    CareerSkill,
    CareerSkillEvidence,
    MappingMethod,
    RecommendationSnapshot,
    ReferenceDataset,
    ReferenceSource,
    ReviewStatus,
)

from careers.services.recommendation_cache import (
    RecommendationCacheKey,
    SCORING_VERSION,
    build_profile_fingerprint,
    build_recommendation_cache_key,
    build_reference_fingerprint,
    get_valid_recommendation_snapshot,
    store_recommendation_snapshot,
)

from profiles.models import (
    CareerGoal,
    Education,
    Experience,
    Interest,
    Project,
    Skill,
    StudentInterest,
    StudentProfile,
    StudentSkill,
)


class RecommendationCacheTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            email="cache.student@gradnavi.test",
            password="StrongPassword123!",
        )

        self.profile = StudentProfile.objects.create(
            user=self.user,
        )

        self.python = Skill.objects.create(
            name="Python Cache Test",
            concept_type=Skill.ConceptType.TECHNOLOGY,
        )

        self.critical_thinking = Skill.objects.create(
            name="Critical Thinking Cache Test",
            concept_type=Skill.ConceptType.SKILL,
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.python,
            proficiency_level=(
                StudentSkill.ProficiencyLevel.PROFICIENT
            ),
        )

        self.source = ReferenceSource.objects.create(
            name="Cache Test O*NET",
        )

        self.dataset = ReferenceDataset.objects.create(
            source=self.source,
            version="cache-test-1",
            retrieved_at="2026-09-18",
            status=ReferenceDataset.Status.ACTIVE,
        )

        self.career = Career.objects.create(
            name="Cache Test Software Engineer",
            description="Build software systems.",
            category="Software and Information Technology",
            active=True,
        )

        self.career_skill = CareerSkill.objects.create(
            career=self.career,
            skill=self.critical_thinking,
            importance_score="70.00",
            required_level_score="60.00",
            review_status=ReviewStatus.APPROVED,
        )

        self.evidence = CareerSkillEvidence.objects.create(
            career_skill=self.career_skill,
            dataset=self.dataset,
            external_occupation_id="15-1252.00",
            external_skill_id="2.A.2.a",
            source_domain="onet_essential_skills",
            normalized_importance="70.00",
            normalized_level="60.00",
            not_relevant=False,
            recommend_suppress=False,
        )


    def test_profile_fingerprint_is_deterministic(self):
        first = build_profile_fingerprint(
            student_profile=self.profile,
        )

        second = build_profile_fingerprint(
            student_profile=self.profile,
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            len(first),
            64,
        )


    def test_profile_fingerprint_changes_when_skill_changes(self):
        before = build_profile_fingerprint(
            student_profile=self.profile,
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.critical_thinking,
            proficiency_level=(
                StudentSkill.ProficiencyLevel.DEVELOPING
            ),
        )

        after = build_profile_fingerprint(
            student_profile=self.profile,
        )

        self.assertNotEqual(
            before,
            after,
        )


    def test_profile_fingerprint_changes_when_proficiency_changes(self):
        student_skill = (
            StudentSkill.objects.get(
                student_profile=self.profile,
                skill=self.python,
            )
        )

        before = build_profile_fingerprint(
            student_profile=self.profile,
        )

        student_skill.proficiency_level = (
            StudentSkill.ProficiencyLevel.ADVANCED
        )

        student_skill.save(
            update_fields=[
                "proficiency_level",
                "updated_at",
            ]
        )

        after = build_profile_fingerprint(
            student_profile=self.profile,
        )

        self.assertNotEqual(
            before,
            after,
        )


    def test_profile_fingerprint_changes_for_semantic_profile_fields(self):
        before = build_profile_fingerprint(
            student_profile=self.profile,
        )

        Education.objects.create(
            student_profile=self.profile,
            institution_name="Excluded Institution",
            qualification="Master of IT",
            field_of_study="Software Development",
            start_date="2025-01-01",
            description="Backend and AI study.",
        )

        Experience.objects.create(
            student_profile=self.profile,
            job_title="Software Developer",
            company="Excluded Company",
            start_date="2024-01-01",
            description="Built web applications.",
        )

        Project.objects.create(
            student_profile=self.profile,
            name="GradNavi",
            description="Career guidance project.",
            start_date="2026-01-01",
        )

        CareerGoal.objects.create(
            student_profile=self.profile,
            career=self.career,
            target_role=self.career.name,
            description="Become a software engineer.",
            is_primary=True,
        )

        after = build_profile_fingerprint(
            student_profile=self.profile,
        )

        self.assertNotEqual(
            before,
            after,
        )


    def test_interest_does_not_change_current_profile_fingerprint(self):
        before = build_profile_fingerprint(
            student_profile=self.profile,
        )

        interest = Interest.objects.create(
            name="Cache Test Artificial Intelligence",
            category="Technology",
        )

        StudentInterest.objects.create(
            student_profile=self.profile,
            interest=interest,
        )

        after = build_profile_fingerprint(
            student_profile=self.profile,
        )

        self.assertEqual(
            before,
            after,
        )


    def test_reference_fingerprint_is_deterministic(self):
        first = build_reference_fingerprint()

        second = build_reference_fingerprint()

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            len(first),
            64,
        )


    def test_reference_fingerprint_changes_when_career_changes(self):
        before = build_reference_fingerprint()

        self.career.description = (
            "Build and maintain software systems."
        )

        self.career.save(
            update_fields=[
                "description",
                "updated_at",
            ]
        )

        after = build_reference_fingerprint()

        self.assertNotEqual(
            before,
            after,
        )


    def test_reference_fingerprint_changes_when_evidence_changes(self):
        before = build_reference_fingerprint()

        self.evidence.normalized_importance = "80.00"

        self.evidence.save(
            update_fields=[
                "normalized_importance",
                "updated_at",
            ]
        )

        after = build_reference_fingerprint()

        self.assertNotEqual(
            before,
            after,
        )


    def test_valid_snapshot_is_returned_when_cache_key_matches(self):
        cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        snapshot = store_recommendation_snapshot(
            student_profile=self.profile,
            payload={
                "recommendations": [
                    {
                        "career_id": self.career.id,
                        "career_name": self.career.name,
                    }
                ]
            },
            embedding_model="text-embedding-3-small",
            prompt_tokens=100,
            total_tokens=100,
            career_count=1,
            cache_key=cache_key,
        )

        loaded = get_valid_recommendation_snapshot(
            student_profile=self.profile,
            cache_key=cache_key,
        )

        self.assertEqual(
            loaded.id,
            snapshot.id,
        )


    def test_profile_change_invalidates_existing_snapshot(self):
        cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        store_recommendation_snapshot(
            student_profile=self.profile,
            payload={
                "recommendations": []
            },
            embedding_model="text-embedding-3-small",
            prompt_tokens=0,
            total_tokens=0,
            career_count=0,
            cache_key=cache_key,
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.critical_thinking,
            proficiency_level=(
                StudentSkill.ProficiencyLevel.DEVELOPING
            ),
        )

        loaded = get_valid_recommendation_snapshot(
            student_profile=self.profile,
        )

        self.assertIsNone(
            loaded
        )


    def test_scoring_version_mismatch_invalidates_snapshot(self):
        cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        store_recommendation_snapshot(
            student_profile=self.profile,
            payload={
                "recommendations": []
            },
            embedding_model="text-embedding-3-small",
            prompt_tokens=0,
            total_tokens=0,
            career_count=0,
            cache_key=cache_key,
        )

        mismatched = RecommendationCacheKey(
            profile_fingerprint=(
                cache_key.profile_fingerprint
            ),
            reference_fingerprint=(
                cache_key.reference_fingerprint
            ),
            scoring_version="composite_v2",
        )

        loaded = get_valid_recommendation_snapshot(
            student_profile=self.profile,
            cache_key=mismatched,
        )

        self.assertIsNone(
            loaded
        )


    def test_store_replaces_single_profile_snapshot(self):
        first_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        first = store_recommendation_snapshot(
            student_profile=self.profile,
            payload={
                "value": 1
            },
            embedding_model="model-a",
            prompt_tokens=10,
            total_tokens=10,
            career_count=1,
            cache_key=first_key,
        )

        second = store_recommendation_snapshot(
            student_profile=self.profile,
            payload={
                "value": 2
            },
            embedding_model="model-b",
            prompt_tokens=20,
            total_tokens=20,
            career_count=2,
            cache_key=first_key,
        )

        self.assertEqual(
            first.id,
            second.id,
        )

        self.assertEqual(
            RecommendationSnapshot.objects.filter(
                student_profile=self.profile,
            ).count(),
            1,
        )

        second.refresh_from_db()

        self.assertEqual(
            second.payload,
            {
                "value": 2
            },
        )

        self.assertEqual(
            second.embedding_model,
            "model-b",
        )

        self.assertEqual(
            second.career_count,
            2,
        )


    def test_cache_key_uses_locked_scoring_version(self):
        cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        self.assertEqual(
            cache_key.scoring_version,
            SCORING_VERSION,
        )
