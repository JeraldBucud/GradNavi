from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase
from django.utils import timezone

from ai_services.exceptions import (
    AIProviderUnavailableError,
)
from ai_services.schemas.outputs import (
    DiscoveredLearningResourceCandidate,
    LearningResourceDiscoveryResult,
)
from careers.models import (
    LearningResource,
    LearningResourceDiscoveryAttempt,
    LearningResourceSkill,
)
from careers.services.learning_resource_discovery import (
    DISCOVERY_REASON_COMPLETED,
    DISCOVERY_REASON_COOLDOWN,
    DISCOVERY_REASON_ENOUGH_RESOURCES,
    DISCOVERY_REASON_PROVIDER_FAILURE,
    DISCOVERY_TARGET_RESOURCE_COUNT,
    ensure_learning_resource_catalogue,
)
from profiles.models import Skill


class FakeDiscoveryProvider:

    def __init__(
        self,
        *,
        result=None,
        source_urls=(),
        error=None,
    ):
        self.result = result
        self.last_source_urls = tuple(
            source_urls
        )
        self.error = error
        self.calls = []


    def generate(
        self,
        *,
        prompt_package,
        output_model,
    ):
        self.calls.append(
            {
                "prompt_package": (
                    prompt_package
                ),
                "output_model": (
                    output_model
                ),
            }
        )

        if self.error is not None:
            raise self.error

        return self.result


class LearningResourceDiscoveryOrchestratorTests(
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
                    "Knowledge of arithmetic, algebra, "
                    "geometry, calculus, statistics, "
                    "and their applications."
                ),
            )
        )


    def add_existing_resource(
        self,
        number,
    ):
        resource = (
            LearningResource
            .objects
            .create(
                resource_key=(
                    f"existing-{number}"
                ),
                title=(
                    f"Existing Resource {number}"
                ),
                provider=(
                    "Existing Provider"
                ),
                url=(
                    "https://existing.example/"
                    f"resource-{number}"
                ),
                resource_type="course",
                description=(
                    "Existing resource."
                ),
                is_active=True,
                access_type=(
                    "free"
                    if number % 2 == 0
                    else "paid"
                ),
                source_type="curated",
                health_status="active",
            )
        )

        LearningResourceSkill.objects.create(
            learning_resource=(
                resource
            ),
            skill=self.skill,
        )

        return resource


    def candidate(
        self,
        number=1,
        *,
        access_type="free",
    ):
        return (
            DiscoveredLearningResourceCandidate(
                title=(
                    f"Discovered Resource {number}"
                ),
                provider=(
                    "Discovery Provider"
                ),
                url=(
                    "https://discovered.example/"
                    f"resource-{number}"
                ),
                resource_type="course",
                access_type=(
                    access_type
                ),
                description=(
                    "Discovered learning resource."
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


    def test_six_existing_resources_skip_discovery(
        self,
    ):
        for number in range(
            6
        ):
            self.add_existing_resource(
                number
            )

        provider = (
            FakeDiscoveryProvider()
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertFalse(
            result.attempted
        )

        self.assertEqual(
            result.reason,
            (
                DISCOVERY_REASON_ENOUGH_RESOURCES
            ),
        )

        self.assertEqual(
            result.resource_count_after,
            6,
        )

        self.assertEqual(
            provider.calls,
            [],
        )

        self.assertEqual(
            LearningResourceDiscoveryAttempt
            .objects
            .count(),
            0,
        )


    def test_two_existing_resources_request_four(
        self,
    ):
        self.add_existing_resource(
            1
        )

        self.add_existing_resource(
            2
        )

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertTrue(
            result.attempted
        )

        self.assertEqual(
            result.requested_count,
            4,
        )

        package = (
            provider.calls[
                0
            ][
                "prompt_package"
            ]
        )

        self.assertIn(
            '"requested_count": 4',
            package.trusted_context,
        )


    def test_discovery_is_global_and_uses_all_access_types(
        self,
    ):
        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        ensure_learning_resource_catalogue(
            skill_id=(
                self.skill.id
            ),
            provider=provider,
        )

        context = (
            provider.calls[
                0
            ][
                "prompt_package"
            ]
            .trusted_context
        )

        self.assertIn(
            '"access_type": "all"',
            context,
        )

        self.assertIn(
            '"career_name": null',
            context,
        )


    def test_existing_skill_urls_are_sent_to_provider(
        self,
    ):
        existing = (
            self.add_existing_resource(
                1
            )
        )

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        ensure_learning_resource_catalogue(
            skill_id=(
                self.skill.id
            ),
            provider=provider,
        )

        context = (
            provider.calls[
                0
            ][
                "prompt_package"
            ]
            .trusted_context
        )

        self.assertIn(
            existing.url,
            context,
        )


    def test_discovery_reaches_six_and_records_success(
        self,
    ):
        for number in range(
            5
        ):
            self.add_existing_resource(
                number
            )

        candidate = (
            self.candidate(
                99
            )
        )

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertEqual(
            result.reason,
            (
                DISCOVERY_REASON_COMPLETED
            ),
        )

        self.assertEqual(
            result.requested_count,
            1,
        )

        self.assertEqual(
            result.persisted_count,
            1,
        )

        self.assertEqual(
            result.resource_count_after,
            6,
        )

        self.assertEqual(
            result.status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .SUCCESS
            ),
        )


    def test_partial_result_blocks_before_retry_window_and_retries_after_one_day(
        self,
    ):
        now = timezone.now()

        candidate = (
            self.candidate(
                1
            )
        )

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    candidate.url
                ],
            )
        )

        first = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
                at=now,
            )
        )

        self.assertEqual(
            first.status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
        )

        self.assertEqual(
            first.resource_count_after,
            1,
        )

        blocked_provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        blocked = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=blocked_provider,
                at=(
                    now
                    + timedelta(
                        hours=23,
                    )
                ),
            )
        )

        self.assertFalse(
            blocked.attempted
        )

        self.assertEqual(
            blocked.reason,
            (
                DISCOVERY_REASON_COOLDOWN
            ),
        )

        self.assertEqual(
            blocked_provider.calls,
            [],
        )

        retry_provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        retry = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=retry_provider,
                at=(
                    now
                    + timedelta(
                        days=1,
                    )
                ),
            )
        )

        self.assertTrue(
            retry.attempted
        )

        self.assertEqual(
            retry.status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .NO_RESULTS
            ),
        )

        self.assertEqual(
            retry.requested_count,
            5,
        )

        self.assertEqual(
            len(
                retry_provider.calls
            ),
            1,
        )


    def test_zero_candidates_records_no_results(
        self,
    ):
        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertEqual(
            result.candidate_count,
            0,
        )

        self.assertEqual(
            result.persisted_count,
            0,
        )

        self.assertEqual(
            result.status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .NO_RESULTS
            ),
        )


    def test_provider_failure_falls_back_without_raising(
        self,
    ):
        provider = (
            FakeDiscoveryProvider(
                error=(
                    AIProviderUnavailableError(
                        "Provider unavailable."
                    )
                ),
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertTrue(
            result.attempted
        )

        self.assertEqual(
            result.reason,
            (
                DISCOVERY_REASON_PROVIDER_FAILURE
            ),
        )

        self.assertEqual(
            result.status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .PROVIDER_FAILURE
            ),
        )

        self.assertEqual(
            result.resource_count_after,
            0,
        )


    def test_provider_failure_has_twenty_four_hour_retry(
        self,
    ):
        now = timezone.now()

        provider = (
            FakeDiscoveryProvider(
                error=(
                    AIProviderUnavailableError(
                        "Provider unavailable."
                    )
                ),
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
                at=now,
            )
        )

        self.assertEqual(
            (
                result.next_eligible_at
                - now
            ),
            timedelta(
                hours=24,
            ),
        )


    def test_provider_extra_candidates_are_bounded_to_requested_count(
        self,
    ):
        for number in range(
            5
        ):
            self.add_existing_resource(
                number
            )

        candidates = [
            self.candidate(
                100 + number
            )
            for number in range(
                3
            )
        ]

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result(
                        *candidates
                    )
                ),
                source_urls=[
                    item.url
                    for item
                    in candidates
                ],
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertEqual(
            result.requested_count,
            1,
        )

        self.assertEqual(
            result.candidate_count,
            1,
        )

        self.assertEqual(
            result.persisted_count,
            1,
        )

        self.assertEqual(
            result.resource_count_after,
            6,
        )


    def test_invalid_source_candidate_does_not_break_request(
        self,
    ):
        candidate = (
            self.candidate(
                1
            )
        )

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result(
                        candidate
                    )
                ),
                source_urls=[
                    (
                        "https://different.example/"
                        "evidence"
                    )
                ],
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertEqual(
            result.candidate_count,
            1,
        )

        self.assertEqual(
            result.persisted_count,
            0,
        )

        self.assertEqual(
            result.resource_count_after,
            0,
        )

        self.assertEqual(
            result.status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
        )


    def test_mixed_access_candidates_share_one_discovery_run(
        self,
    ):
        free = (
            self.candidate(
                1,
                access_type="free",
            )
        )

        paid = (
            self.candidate(
                2,
                access_type="paid",
            )
        )

        freemium = (
            self.candidate(
                3,
                access_type="freemium",
            )
        )

        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result(
                        free,
                        paid,
                        freemium,
                    )
                ),
                source_urls=[
                    free.url,
                    paid.url,
                    freemium.url,
                ],
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=provider,
            )
        )

        self.assertEqual(
            result.persisted_count,
            3,
        )

        self.assertEqual(
            len(
                provider.calls
            ),
            1,
        )

        access_types = set(
            LearningResource
            .objects
            .values_list(
                "access_type",
                flat=True,
            )
        )

        self.assertEqual(
            access_types,
            {
                "free",
                "paid",
                "freemium",
            },
        )


    def test_missing_skill_is_rejected(
        self,
    ):
        provider = (
            FakeDiscoveryProvider(
                result=(
                    self.result()
                ),
            )
        )

        with self.assertRaises(
            ValueError
        ):
            ensure_learning_resource_catalogue(
                skill_id=999999,
                provider=provider,
            )


    def test_target_constant_stays_six(
        self,
    ):
        self.assertEqual(
            DISCOVERY_TARGET_RESOURCE_COUNT,
            6,
        )
