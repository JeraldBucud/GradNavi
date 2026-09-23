from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from careers.models import (
    LearningResourceDiscoveryAttempt,
)
from careers.services.learning_resource_discovery import (
    DISCOVERY_COMPLETED_COOLDOWN,
    DISCOVERY_PROVIDER_FAILURE_COOLDOWN,
    DISCOVERY_TARGET_RESOURCE_COUNT,
    get_discovery_eligibility,
    record_discovery_attempt,
)
from profiles.models import Skill


class LearningResourceDiscoveryCooldownTests(
    TestCase
):

    def setUp(
        self,
    ):
        self.skill = (
            Skill.objects.create(
                name=(
                    "Computers and Electronics"
                ),
                concept_type=(
                    Skill
                    .ConceptType
                    .KNOWLEDGE
                ),
            )
        )


    def test_target_resource_count_is_six(
        self,
    ):
        self.assertEqual(
            DISCOVERY_TARGET_RESOURCE_COUNT,
            6,
        )


    def test_skill_without_attempt_is_eligible(
        self,
    ):
        result = (
            get_discovery_eligibility(
                skill_id=(
                    self.skill.id
                ),
            )
        )

        self.assertTrue(
            result.eligible
        )

        self.assertIsNone(
            result.latest_status
        )

        self.assertIsNone(
            result.next_eligible_at
        )


    def test_success_uses_thirty_day_cooldown(
        self,
    ):
        now = timezone.now()

        attempt = (
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .SUCCESS
                ),
                requested_count=6,
                candidate_count=6,
                persisted_count=6,
                at=now,
            )
        )

        self.assertEqual(
            (
                attempt.next_eligible_at
                - now
            ),
            DISCOVERY_COMPLETED_COOLDOWN,
        )

        self.assertEqual(
            DISCOVERY_COMPLETED_COOLDOWN,
            timedelta(
                days=30,
            ),
        )


    def test_partial_uses_one_day_cooldown(
        self,
    ):
        now = timezone.now()

        attempt = (
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .PARTIAL
                ),
                requested_count=6,
                candidate_count=3,
                persisted_count=2,
                at=now,
            )
        )

        self.assertEqual(
            (
                attempt.next_eligible_at
                - now
            ),
            timedelta(
                days=1,
            ),
        )


    def test_zero_results_uses_thirty_day_cooldown(
        self,
    ):
        now = timezone.now()

        attempt = (
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .NO_RESULTS
                ),
                requested_count=6,
                candidate_count=0,
                persisted_count=0,
                at=now,
            )
        )

        self.assertEqual(
            (
                attempt.next_eligible_at
                - now
            ),
            timedelta(
                days=30,
            ),
        )


    def test_provider_failure_uses_twenty_four_hour_cooldown(
        self,
    ):
        now = timezone.now()

        attempt = (
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .PROVIDER_FAILURE
                ),
                requested_count=6,
                candidate_count=0,
                persisted_count=0,
                at=now,
            )
        )

        self.assertEqual(
            (
                attempt.next_eligible_at
                - now
            ),
            (
                DISCOVERY_PROVIDER_FAILURE_COOLDOWN
            ),
        )

        self.assertEqual(
            DISCOVERY_PROVIDER_FAILURE_COOLDOWN,
            timedelta(
                hours=24,
            ),
        )


    def test_recent_partial_attempt_blocks_before_one_day(
        self,
    ):
        now = timezone.now()

        record_discovery_attempt(
            skill_id=(
                self.skill.id
            ),
            status=(
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
            requested_count=6,
            candidate_count=2,
            persisted_count=2,
            at=now,
        )

        result = (
            get_discovery_eligibility(
                skill_id=(
                    self.skill.id
                ),
                at=(
                    now
                    + timedelta(
                        hours=23,
                    )
                ),
            )
        )

        self.assertFalse(
            result.eligible
        )

        self.assertEqual(
            result.latest_status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
        )

    def test_partial_attempt_is_eligible_after_one_day(
        self,
    ):
        now = timezone.now()

        record_discovery_attempt(
            skill_id=(
                self.skill.id
            ),
            status=(
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
            requested_count=6,
            candidate_count=2,
            persisted_count=2,
            at=now,
        )

        result = (
            get_discovery_eligibility(
                skill_id=(
                    self.skill.id
                ),
                at=(
                    now
                    + timedelta(
                        days=1,
                    )
                ),
            )
        )

        self.assertTrue(
            result.eligible
        )

        self.assertEqual(
            result.latest_status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .PARTIAL
            ),
        )


    def test_discovery_is_allowed_after_cooldown(
        self,
    ):
        now = timezone.now()

        record_discovery_attempt(
            skill_id=(
                self.skill.id
            ),
            status=(
                LearningResourceDiscoveryAttempt
                .Status
                .NO_RESULTS
            ),
            requested_count=6,
            candidate_count=0,
            persisted_count=0,
            at=now,
        )

        result = (
            get_discovery_eligibility(
                skill_id=(
                    self.skill.id
                ),
                at=(
                    now
                    + timedelta(
                        days=31,
                    )
                ),
            )
        )

        self.assertTrue(
            result.eligible
        )


    def test_provider_failure_is_allowed_after_one_day(
        self,
    ):
        now = timezone.now()

        record_discovery_attempt(
            skill_id=(
                self.skill.id
            ),
            status=(
                LearningResourceDiscoveryAttempt
                .Status
                .PROVIDER_FAILURE
            ),
            requested_count=6,
            candidate_count=0,
            persisted_count=0,
            at=now,
        )

        result = (
            get_discovery_eligibility(
                skill_id=(
                    self.skill.id
                ),
                at=(
                    now
                    + timedelta(
                        hours=25,
                    )
                ),
            )
        )

        self.assertTrue(
            result.eligible
        )


    def test_attempt_is_global_and_has_no_student_or_access_filter(
        self,
    ):
        field_names = {
            field.name
            for field
            in (
                LearningResourceDiscoveryAttempt
                ._meta
                .fields
            )
        }

        self.assertNotIn(
            "student_profile",
            field_names,
        )

        self.assertNotIn(
            "access_type",
            field_names,
        )

        self.assertIn(
            "skill",
            field_names,
        )


    def test_invalid_requested_count_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .SUCCESS
                ),
                requested_count=7,
                candidate_count=0,
                persisted_count=0,
            )


    def test_persisted_count_cannot_exceed_candidate_count(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .PARTIAL
                ),
                requested_count=6,
                candidate_count=2,
                persisted_count=3,
            )


    def test_latest_attempt_controls_eligibility(
        self,
    ):
        now = timezone.now()

        first = (
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .NO_RESULTS
                ),
                requested_count=6,
                candidate_count=0,
                persisted_count=0,
                at=(
                    now
                    - timedelta(
                        days=60,
                    )
                ),
            )
        )

        second = (
            record_discovery_attempt(
                skill_id=(
                    self.skill.id
                ),
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .PROVIDER_FAILURE
                ),
                requested_count=6,
                candidate_count=0,
                persisted_count=0,
                at=now,
            )
        )

        LearningResourceDiscoveryAttempt.objects.filter(
            id=first.id,
        ).update(
            attempted_at=(
                now
                - timedelta(
                    days=60,
                )
            )
        )

        LearningResourceDiscoveryAttempt.objects.filter(
            id=second.id,
        ).update(
            attempted_at=now
        )

        result = (
            get_discovery_eligibility(
                skill_id=(
                    self.skill.id
                ),
                at=(
                    now
                    + timedelta(
                        hours=1,
                    )
                ),
            )
        )

        self.assertFalse(
            result.eligible
        )

        self.assertEqual(
            result.latest_status,
            (
                LearningResourceDiscoveryAttempt
                .Status
                .PROVIDER_FAILURE
            ),
        )
