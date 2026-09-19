from django.test import TestCase

from ai_services.schemas.outputs import (
    DiscoveredLearningResourceCandidate,
    LearningResourceDiscoveryResult,
)
from careers.models import (
    LearningResource,
    LearningResourceSkill,
)
from careers.services.learning_resource_discovery import (
    REJECTION_ACCESS_FILTER_MISMATCH,
    REJECTION_ALREADY_LINKED_TO_SKILL,
    REJECTION_DUPLICATE_CANDIDATE,
    REJECTION_MISSING_SOURCE_EVIDENCE,
    normalize_resource_url,
    persist_source_backed_learning_resources,
    sanitize_discovered_description,
)
from profiles.models import Skill


class LearningResourceDiscoveryPersistenceTests(
    TestCase
):

    def setUp(
        self,
    ):
        self.skill = (
            Skill.objects.create(
                name=(
                    "Mathematics Knowledge"
                ),
                concept_type=(
                    Skill
                    .ConceptType
                    .KNOWLEDGE
                ),
                description=(
                    "Knowledge of arithmetic, "
                    "algebra, geometry, calculus, "
                    "statistics, and applications."
                ),
            )
        )

        self.other_skill = (
            Skill.objects.create(
                name=(
                    "Judgment and Decision Making"
                ),
                concept_type=(
                    Skill
                    .ConceptType
                    .SKILL
                ),
            )
        )


    def candidate(
        self,
        *,
        url=(
            "https://example.edu/"
            "mathematics"
        ),
        access_type="free",
        title=(
            "Example Mathematics Course"
        ),
    ):
        return (
            DiscoveredLearningResourceCandidate(
                title=title,
                provider=(
                    "Example University"
                ),
                url=url,
                resource_type="course",
                access_type=access_type,
                description=(
                    "A mathematics learning resource."
                ),
            )
        )


    def result(
        self,
        *candidates,
    ):
        return (
            LearningResourceDiscoveryResult(
                candidates=list(
                    candidates
                ),
                is_ai_generated=True,
            )
        )



    def test_description_sanitizer_removes_openai_markdown_citation(
        self,
    ):
        value = (
            "A free mathematics course. "
            "([example.org]"
            "(https://example.org/course"
            "?utm_source=openai))"
        )

        self.assertEqual(
            sanitize_discovered_description(
                value
            ),
            "A free mathematics course.",
        )


    def test_persistence_stores_description_without_openai_citation(
        self,
    ):
        candidate = (
            DiscoveredLearningResourceCandidate(
                title=(
                    "Citation Test Course"
                ),
                provider=(
                    "Example University"
                ),
                url=(
                    "https://example.edu/"
                    "citation-test"
                ),
                resource_type="course",
                access_type="free",
                description=(
                    "A useful mathematics course. "
                    "([example.edu]"
                    "(https://example.edu/"
                    "citation-test"
                    "?utm_source=openai))"
                ),
            )
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )

        resource = (
            LearningResource
            .objects
            .get(
                id=(
                    result
                    .persisted[
                        0
                    ]
                    .resource_id
                )
            )
        )

        self.assertEqual(
            resource.description,
            "A useful mathematics course.",
        )

        self.assertNotIn(
            "utm_source=openai",
            resource.description,
        )


    def test_normalize_url_removes_fragment(
        self,
    ):
        normalized = (
            normalize_resource_url(
                (
                    "HTTPS://Example.EDU/"
                    "mathematics/#overview"
                )
            )
        )

        self.assertEqual(
            normalized,
            (
                "https://example.edu/"
                "mathematics"
            ),
        )


    def test_normalize_url_removes_default_https_port(
        self,
    ):
        normalized = (
            normalize_resource_url(
                (
                    "https://example.edu:"
                    "443/mathematics/"
                )
            )
        )

        self.assertEqual(
            normalized,
            (
                "https://example.edu/"
                "mathematics"
            ),
        )


    def test_source_backed_candidate_is_persisted(
        self,
    ):
        candidate = (
            self.candidate()
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
                requested_access_type="free",
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )

        self.assertEqual(
            result.rejected,
            (),
        )

        resource = (
            LearningResource
            .objects
            .get()
        )

        self.assertEqual(
            resource.source_type,
            (
                LearningResource
                .SourceType
                .DISCOVERED
            ),
        )

        self.assertEqual(
            resource.health_status,
            (
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )

        self.assertEqual(
            resource.access_type,
            (
                LearningResource
                .AccessType
                .FREE
            ),
        )

        self.assertTrue(
            resource.is_active
        )

        self.assertIsNotNone(
            resource.last_checked_at
        )

        self.assertIsNotNone(
            resource.last_verified_at
        )

        self.assertTrue(
            LearningResourceSkill
            .objects
            .filter(
                learning_resource=(
                    resource
                ),
                skill=self.skill,
            )
            .exists()
        )


    def test_candidate_without_source_evidence_is_rejected(
        self,
    ):
        candidate = (
            self.candidate()
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    (
                        "https://different.example/"
                        "resource"
                    )
                ],
            )
        )

        self.assertEqual(
            result.persisted,
            (),
        )

        self.assertEqual(
            result.rejected[
                0
            ].reason,
            (
                REJECTION_MISSING_SOURCE_EVIDENCE
            ),
        )

        self.assertEqual(
            LearningResource
            .objects
            .count(),
            0,
        )


    def test_source_evidence_matches_after_fragment_normalization(
        self,
    ):
        candidate = (
            self.candidate(
                url=(
                    "https://example.edu/"
                    "mathematics#course"
                )
            )
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    (
                        "https://example.edu/"
                        "mathematics#overview"
                    )
                ],
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )


    def test_access_filter_mismatch_is_rejected(
        self,
    ):
        candidate = (
            self.candidate(
                access_type="paid"
            )
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
                requested_access_type="free",
            )
        )

        self.assertEqual(
            result.persisted,
            (),
        )

        self.assertEqual(
            result.rejected[
                0
            ].reason,
            (
                REJECTION_ACCESS_FILTER_MISMATCH
            ),
        )


    def test_all_filter_accepts_unknown_access_type(
        self,
    ):
        candidate = (
            self.candidate(
                access_type="unknown"
            )
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
                requested_access_type="all",
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )


    def test_existing_resource_for_same_skill_is_rejected(
        self,
    ):
        candidate = (
            self.candidate()
        )

        resource = (
            LearningResource
            .objects
            .create(
                resource_key=(
                    "existing-mathematics"
                ),
                title=(
                    "Existing Mathematics"
                ),
                provider=(
                    "Example University"
                ),
                url=(
                    candidate.url
                ),
                resource_type="course",
                access_type="free",
                source_type="curated",
                health_status="active",
                is_active=True,
            )
        )

        LearningResourceSkill.objects.create(
            learning_resource=(
                resource
            ),
            skill=self.skill,
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
            )
        )

        self.assertEqual(
            result.persisted,
            (),
        )

        self.assertEqual(
            result.rejected[
                0
            ].reason,
            (
                REJECTION_ALREADY_LINKED_TO_SKILL
            ),
        )

        self.assertEqual(
            LearningResource
            .objects
            .count(),
            1,
        )


    def test_existing_resource_is_reused_for_new_skill(
        self,
    ):
        candidate = (
            self.candidate()
        )

        resource = (
            LearningResource
            .objects
            .create(
                resource_key=(
                    "curated-mathematics"
                ),
                title=(
                    "Curated Mathematics"
                ),
                provider=(
                    "Trusted Provider"
                ),
                url=(
                    candidate.url
                ),
                resource_type="course",
                description=(
                    "Reviewed description."
                ),
                access_type="free",
                source_type="curated",
                health_status="active",
                is_active=True,
            )
        )

        LearningResourceSkill.objects.create(
            learning_resource=(
                resource
            ),
            skill=self.other_skill,
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )

        self.assertFalse(
            result.persisted[
                0
            ].created
        )

        self.assertTrue(
            result.persisted[
                0
            ].link_created
        )

        resource.refresh_from_db()

        self.assertEqual(
            resource.source_type,
            (
                LearningResource
                .SourceType
                .CURATED
            ),
        )

        self.assertEqual(
            resource.title,
            "Curated Mathematics",
        )

        self.assertEqual(
            LearningResource
            .objects
            .count(),
            1,
        )

        self.assertTrue(
            LearningResourceSkill
            .objects
            .filter(
                learning_resource=(
                    resource
                ),
                skill=self.skill,
            )
            .exists()
        )


    def test_existing_discovered_resource_metadata_is_refreshed(
        self,
    ):
        candidate = (
            self.candidate(
                title=(
                    "Updated Mathematics Course"
                )
            )
        )

        resource = (
            LearningResource
            .objects
            .create(
                resource_key=(
                    "previously-discovered"
                ),
                title=(
                    "Old Mathematics Course"
                ),
                provider=(
                    "Old Provider"
                ),
                url=(
                    candidate.url
                ),
                resource_type="article",
                description=(
                    "Old description."
                ),
                access_type="unknown",
                source_type="discovered",
                health_status="needs_review",
                is_active=False,
            )
        )

        LearningResourceSkill.objects.create(
            learning_resource=(
                resource
            ),
            skill=self.other_skill,
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
                requested_access_type="free",
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )

        resource.refresh_from_db()

        self.assertEqual(
            resource.title,
            (
                "Updated Mathematics Course"
            ),
        )

        self.assertEqual(
            resource.access_type,
            "free",
        )

        self.assertEqual(
            resource.health_status,
            "active",
        )

        self.assertTrue(
            resource.is_active
        )

        self.assertIsNotNone(
            resource.last_verified_at
        )


    def test_normalized_duplicate_candidates_are_rejected(
        self,
    ):
        first = (
            self.candidate(
                url=(
                    "https://example.edu/"
                    "mathematics#one"
                )
            )
        )

        second = (
            self.candidate(
                url=(
                    "https://example.edu/"
                    "mathematics#two"
                ),
                title=(
                    "Duplicate Mathematics"
                ),
            )
        )

        result = (
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        first,
                        second,
                    )
                ),
                source_urls=[
                    (
                        "https://example.edu/"
                        "mathematics"
                    )
                ],
            )
        )

        self.assertEqual(
            len(
                result.persisted
            ),
            1,
        )

        self.assertEqual(
            len(
                result.rejected
            ),
            1,
        )

        self.assertEqual(
            result.rejected[
                0
            ].reason,
            (
                REJECTION_DUPLICATE_CANDIDATE
            ),
        )

        self.assertEqual(
            LearningResource
            .objects
            .count(),
            1,
        )


    def test_new_resource_key_is_stable_hash_based_key(
        self,
    ):
        candidate = (
            self.candidate()
        )

        persist_source_backed_learning_resources(
            skill_id=(
                self.skill.id
            ),
            discovery_result=(
                self.result(
                    candidate
                )
            ),
            source_urls=[
                candidate.url
            ],
        )

        resource = (
            LearningResource
            .objects
            .get()
        )

        self.assertTrue(
            resource
            .resource_key
            .startswith(
                "discovered:"
            )
        )

        self.assertLessEqual(
            len(
                resource.resource_key
            ),
            120,
        )


    def test_invalid_access_filter_is_rejected(
        self,
    ):
        candidate = (
            self.candidate()
        )

        with self.assertRaises(
            ValueError
        ):
            persist_source_backed_learning_resources(
                skill_id=(
                    self.skill.id
                ),
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
                requested_access_type=(
                    "subscription"
                ),
            )


    def test_missing_skill_is_rejected(
        self,
    ):
        candidate = (
            self.candidate()
        )

        with self.assertRaises(
            ValueError
        ):
            persist_source_backed_learning_resources(
                skill_id=999999,
                discovery_result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
            )
