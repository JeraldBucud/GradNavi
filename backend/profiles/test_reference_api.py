from django.contrib.auth import (
    get_user_model,
)
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from careers.models import Career
from profiles.models import (
    Interest,
    Skill,
)


User = get_user_model()


class ProfileReferenceAPITests(
    APITestCase
):
    def setUp(self):
        self.user = (
            User.objects.create_user(
                email=(
                    "reference-api"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
                first_name="Reference",
                last_name="Student",
            )
        )

        self.access_token = str(
            RefreshToken.for_user(
                self.user
            ).access_token
        )

        self.skill_url = (
            "/api/v1/profile/"
            "reference/skills/"
        )

        self.interest_url = (
            "/api/v1/profile/"
            "reference/interests/"
        )

        self.career_url = (
            "/api/v1/profile/"
            "reference/careers/"
        )

        Skill.objects.create(
            name="Python",
            category="Programming",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        Skill.objects.create(
            name="Data Analysis",
            category="Analytics",
            concept_type=(
                Skill.ConceptType.SKILL
            ),
        )

        Skill.objects.create(
            name="Cloud Architecture",
            category="Cloud",
            concept_type=(
                Skill.ConceptType.KNOWLEDGE
            ),
        )

        Interest.objects.create(
            name="Artificial Intelligence",
            category="Technology",
        )

        Interest.objects.create(
            name="Data Science",
            category=(
                "Data and "
                "Artificial Intelligence"
            ),
        )

        Interest.objects.create(
            name="Patient Care",
            category="Healthcare",
        )

        Career.objects.create(
            name="Software Engineer",
            category=(
                "Software and "
                "Information Technology"
            ),
            description=(
                "Designs and develops "
                "software systems."
            ),
            active=True,
        )

        Career.objects.create(
            name="Data Scientist",
            category=(
                "Data and "
                "Artificial Intelligence"
            ),
            description=(
                "Builds analytical "
                "and predictive models."
            ),
            active=True,
        )

        Career.objects.create(
            name="Legacy Inactive Career",
            category="Legacy",
            description=(
                "Inactive reference record."
            ),
            active=False,
        )

    def authenticated_get(
        self,
        path,
    ):
        return self.client.get(
            path,
            HTTP_AUTHORIZATION=(
                "Bearer "
                f"{self.access_token}"
            ),
        )

    def test_skill_reference_route_resolves(
        self,
    ):
        self.assertEqual(
            resolve(
                self.skill_url
            ).url_name,
            "profile-reference-skills",
        )

    def test_interest_reference_route_resolves(
        self,
    ):
        self.assertEqual(
            resolve(
                self.interest_url
            ).url_name,
            "profile-reference-interests",
        )

    def test_career_reference_route_resolves(
        self,
    ):
        self.assertEqual(
            resolve(
                self.career_url
            ).url_name,
            "profile-reference-careers",
        )

    def test_reference_apis_require_authentication(
        self,
    ):
        for path in (
            self.skill_url,
            self.interest_url,
            self.career_url,
        ):
            with self.subTest(
                path=path
            ):
                response = (
                    self.client.get(
                        path
                    )
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_skill_search_matches_name_case_insensitively(
        self,
    ):
        response = (
            self.authenticated_get(
                self.skill_url
                + "?search=PYTHON"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data[
                "data"
            ][
                "results"
            ]
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0][
                "name"
            ],
            "Python",
        )

        self.assertEqual(
            results[0][
                "concept_type"
            ],
            "technology",
        )

    def test_skill_search_matches_category(
        self,
    ):
        response = (
            self.authenticated_get(
                self.skill_url
                + "?search=analytics"
            )
        )

        names = {
            item[
                "name"
            ]
            for item
            in response.data[
                "data"
            ][
                "results"
            ]
        }

        self.assertEqual(
            names,
            {
                "Data Analysis",
            },
        )

    def test_interest_search_matches_name(
        self,
    ):
        response = (
            self.authenticated_get(
                self.interest_url
                + "?search=data"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data[
                "data"
            ][
                "results"
            ]
        )

        self.assertEqual(
            [
                item["name"]
                for item
                in results
            ],
            [
                "Data Science",
            ],
        )

    def test_interest_search_matches_category(
        self,
    ):
        response = (
            self.authenticated_get(
                self.interest_url
                + "?search=health"
            )
        )

        results = (
            response.data[
                "data"
            ][
                "results"
            ]
        )

        self.assertEqual(
            [
                item["name"]
                for item
                in results
            ],
            [
                "Patient Care",
            ],
        )

    def test_career_search_returns_active_matches_only(
        self,
    ):
        response = (
            self.authenticated_get(
                self.career_url
                + "?search=software"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = (
            response.data[
                "data"
            ][
                "results"
            ]
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0][
                "name"
            ],
            "Software Engineer",
        )

    def test_inactive_career_is_never_returned(
        self,
    ):
        response = (
            self.authenticated_get(
                self.career_url
                + "?search=legacy"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "total"
            ],
            0,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "results"
            ],
            [],
        )

    def test_career_search_matches_description(
        self,
    ):
        response = (
            self.authenticated_get(
                self.career_url
                + "?search=predictive"
            )
        )

        results = (
            response.data[
                "data"
            ][
                "results"
            ]
        )

        self.assertEqual(
            [
                item["name"]
                for item
                in results
            ],
            [
                "Data Scientist",
            ],
        )

    def test_response_includes_search_metadata(
        self,
    ):
        response = (
            self.authenticated_get(
                self.skill_url
                + "?search=python"
            )
        )

        data = (
            response.data[
                "data"
            ]
        )

        self.assertEqual(
            data[
                "search"
            ],
            "python",
        )

        self.assertEqual(
            data[
                "total"
            ],
            1,
        )

        self.assertIn(
            "results",
            data,
        )

    def test_skill_endpoint_limits_unfiltered_results(
        self,
    ):
        for index in range(
            30
        ):
            Skill.objects.create(
                name=(
                    f"Extra Skill "
                    f"{index:02d}"
                ),
                category="Test",
            )

        response = (
            self.authenticated_get(
                self.skill_url
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(
                response.data[
                    "data"
                ][
                    "results"
                ]
            ),
            25,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "total"
            ],
            33,
        )

    def test_career_endpoint_returns_all_active_test_careers(
        self,
    ):
        response = (
            self.authenticated_get(
                self.career_url
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        names = {
            item[
                "name"
            ]
            for item
            in response.data[
                "data"
            ][
                "results"
            ]
        }

        self.assertEqual(
            names,
            {
                "Software Engineer",
                "Data Scientist",
            },
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "total"
            ],
            2,
        )
