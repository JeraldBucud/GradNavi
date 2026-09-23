from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ai_services.schemas.outputs import (
    DiscoveredLearningResourceCandidate,
    LearningResourceDiscoveryResult,
)
from careers.models import (
    LearningResourceDiscoveryAttempt,
)
from careers.services.learning_resource_discovery import (
    DISCOVERY_COMPLETED_COOLDOWN,
    DISCOVERY_PARTIAL_COOLDOWN,
    DISCOVERY_PROVIDER_FAILURE_COOLDOWN,
    REJECTION_MISSING_SOURCE_EVIDENCE,
    LearningResourceDiscoveryEligibility,
    LearningResourceDiscoveryPersistenceResult,
    LearningResourceDiscoveryRunResult,
    PersistedLearningResource,
    RejectedLearningResource,
    discovery_cooldown_for_status,
    ensure_learning_resource_catalogue,
)
from profiles.models import Skill


class FakeDiscoveryProvider:
    last_source_urls = (
        "https://example.com/accepted",
        "https://example.com/rejected",
    )

    def generate(
        self,
        **kwargs,
    ):
        return (
            LearningResourceDiscoveryResult(
                candidates=[
                    DiscoveredLearningResourceCandidate(
                        title="Accepted Resource",
                        provider="Example",
                        url=(
                            "https://example.com/accepted"
                        ),
                        resource_type="course",
                        access_type="free",
                        description="Accepted.",
                    ),
                    DiscoveredLearningResourceCandidate(
                        title="Rejected Resource",
                        provider="Example",
                        url=(
                            "https://example.com/rejected"
                        ),
                        resource_type="course",
                        access_type="free",
                        description="Rejected.",
                    ),
                ],
                is_ai_generated=True,
            )
        )


class LearningResourceDiscoveryPolicyTests(
    TestCase
):
    def setUp(
        self,
    ):
        self.skill = (
            Skill.objects.create(
                name=(
                    "Discovery Policy Test Skill"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

    def test_partial_uses_one_day_retry(
        self,
    ):
        self.assertEqual(
            DISCOVERY_PARTIAL_COOLDOWN,
            timedelta(
                days=1,
            ),
        )

        self.assertEqual(
            discovery_cooldown_for_status(
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
            timedelta(
                days=1,
            ),
        )

    def test_success_keeps_thirty_day_cooldown(
        self,
    ):
        self.assertEqual(
            DISCOVERY_COMPLETED_COOLDOWN,
            timedelta(
                days=30,
            ),
        )

        self.assertEqual(
            discovery_cooldown_for_status(
                LearningResourceDiscoveryAttempt
                .Status
                .SUCCESS
            ),
            timedelta(
                days=30,
            ),
        )

    def test_no_results_keeps_thirty_day_cooldown(
        self,
    ):
        self.assertEqual(
            discovery_cooldown_for_status(
                LearningResourceDiscoveryAttempt
                .Status
                .NO_RESULTS
            ),
            timedelta(
                days=30,
            ),
        )

    def test_provider_failure_keeps_one_day_retry(
        self,
    ):
        self.assertEqual(
            DISCOVERY_PROVIDER_FAILURE_COOLDOWN,
            timedelta(
                days=1,
            ),
        )

        self.assertEqual(
            discovery_cooldown_for_status(
                LearningResourceDiscoveryAttempt
                .Status
                .PROVIDER_FAILURE
            ),
            timedelta(
                days=1,
            ),
        )

    def test_run_result_defaults_rejection_diagnostics(
        self,
    ):
        result = (
            LearningResourceDiscoveryRunResult(
                attempted=False,
                reason="enough_resources",
                status=None,
                resource_count_before=6,
                resource_count_after=6,
                requested_count=0,
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=None,
            )
        )

        self.assertEqual(
            result.rejected_count,
            0,
        )

        self.assertEqual(
            result.rejection_reasons,
            (),
        )

    @patch(
        "careers.services."
        "learning_resource_discovery."
        "persist_source_backed_learning_resources"
    )
    @patch(
        "careers.services."
        "learning_resource_discovery."
        "count_valid_learning_resources"
    )
    @patch(
        "careers.services."
        "learning_resource_discovery."
        "get_discovery_eligibility"
    )
    def test_orchestrator_returns_rejection_diagnostics(
        self,
        eligibility_mock,
        count_mock,
        persistence_mock,
    ):
        now = timezone.now()

        eligibility_mock.return_value = (
            LearningResourceDiscoveryEligibility(
                eligible=True,
                latest_status=None,
                next_eligible_at=None,
            )
        )

        count_mock.side_effect = [
            0,
            1,
        ]

        persistence_mock.return_value = (
            LearningResourceDiscoveryPersistenceResult(
                persisted=(
                    PersistedLearningResource(
                        resource_id=1,
                        url=(
                            "https://example.com/accepted"
                        ),
                        created=True,
                        link_created=True,
                    ),
                ),
                rejected=(
                    RejectedLearningResource(
                        url=(
                            "https://example.com/rejected"
                        ),
                        reason=(
                            REJECTION_MISSING_SOURCE_EVIDENCE
                        ),
                    ),
                ),
            )
        )

        result = (
            ensure_learning_resource_catalogue(
                skill_id=(
                    self.skill.id
                ),
                provider=(
                    FakeDiscoveryProvider()
                ),
                at=now,
            )
        )

        self.assertTrue(
            result.attempted
        )

        self.assertEqual(
            result.status,
            LearningResourceDiscoveryAttempt
            .Status
            .PARTIAL,
        )

        self.assertEqual(
            result.rejected_count,
            1,
        )

        self.assertEqual(
            result.rejection_reasons,
            (
                REJECTION_MISSING_SOURCE_EVIDENCE,
            ),
        )

        self.assertEqual(
            result.candidate_count,
            2,
        )

        self.assertEqual(
            result.persisted_count,
            1,
        )

        self.assertEqual(
            result.next_eligible_at,
            (
                now
                + timedelta(
                    days=1,
                )
            ),
        )
