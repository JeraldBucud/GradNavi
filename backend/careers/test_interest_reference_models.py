from decimal import Decimal

from django.db import (
    IntegrityError,
    transaction,
)
from django.test import TestCase

from careers.models import (
    Career,
    CareerInterest,
    CareerRIASECProfile,
    ReferenceDataset,
    ReferenceSource,
    ReviewStatus,
)
from profiles.models import Interest


class CareerInterestModelTests(TestCase):
    def setUp(self):
        self.career = Career.objects.create(
            name="Test Career",
            active=True,
        )

        self.interest = Interest.objects.create(
            name="Test Interest",
            category="Test",
        )

    def test_career_interest_accepts_valid_mapping(self):
        mapping = CareerInterest.objects.create(
            career=self.career,
            interest=self.interest,
            relevance_weight=5,
            review_status=ReviewStatus.APPROVED,
            source_type=(
                CareerInterest
                .SourceType
                .GRADNAVI_REVIEW
            ),
        )

        self.assertEqual(
            mapping.relevance_weight,
            5,
        )

    def test_duplicate_career_interest_is_rejected(self):
        CareerInterest.objects.create(
            career=self.career,
            interest=self.interest,
            relevance_weight=5,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerInterest.objects.create(
                    career=self.career,
                    interest=self.interest,
                    relevance_weight=4,
                )

    def test_relevance_below_one_is_rejected(self):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerInterest.objects.create(
                    career=self.career,
                    interest=self.interest,
                    relevance_weight=0,
                )

    def test_relevance_above_five_is_rejected(self):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerInterest.objects.create(
                    career=self.career,
                    interest=self.interest,
                    relevance_weight=6,
                )


class CareerRIASECProfileModelTests(TestCase):
    def setUp(self):
        self.career = Career.objects.create(
            name="RIASEC Test Career",
            active=True,
        )

        self.source = ReferenceSource.objects.create(
            name="RIASEC Test Source",
        )

        self.dataset = ReferenceDataset.objects.create(
            source=self.source,
            version="test-1",
            retrieved_at="2026-09-17",
        )

    def valid_payload(self):
        return {
            "career": self.career,
            "dataset": self.dataset,
            "realistic_score": Decimal("20.00"),
            "investigative_score": Decimal("80.00"),
            "artistic_score": Decimal("30.00"),
            "social_score": Decimal("40.00"),
            "enterprising_score": Decimal("50.00"),
            "conventional_score": Decimal("60.00"),
            "review_status": ReviewStatus.APPROVED,
        }

    def test_valid_riasec_profile_is_saved(self):
        result = (
            CareerRIASECProfile.objects.create(
                **self.valid_payload()
            )
        )

        self.assertEqual(
            result.investigative_score,
            Decimal("80.00"),
        )

    def test_score_above_100_is_rejected(self):
        payload = self.valid_payload()

        payload[
            "realistic_score"
        ] = Decimal("100.01")

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerRIASECProfile.objects.create(
                    **payload
                )

    def test_duplicate_career_dataset_is_rejected(self):
        CareerRIASECProfile.objects.create(
            **self.valid_payload()
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerRIASECProfile.objects.create(
                    **self.valid_payload()
                )
