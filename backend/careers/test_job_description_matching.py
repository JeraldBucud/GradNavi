from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ai_services.schemas.inputs import (
    JOB_DESCRIPTION_MAX_LENGTH,
)
from careers.models import SkillAlias
from careers.services.job_description_matching import (
    MATCH_SOURCE_ALIAS,
    MATCH_SOURCE_CANONICAL,
    extract_job_requirements,
    match_job_description,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class JobDescriptionMatchingServiceTests(
    TestCase
):
    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "job-match-service"
                    "@gradnavi.test"
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

        self.python = Skill.objects.create(
            name="Python",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        self.django = Skill.objects.create(
            name="Django",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        self.cpp = Skill.objects.create(
            name="C++",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        self.design = Skill.objects.create(
            name="Design",
            concept_type=(
                Skill.ConceptType.KNOWLEDGE
            ),
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.python,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .PROFICIENT
            ),
        )


    def test_canonical_skill_extraction(self):
        requirements = (
            extract_job_requirements(
                (
                    "Required experience with "
                    "Python, Django and C++."
                )
            )
        )

        self.assertEqual(
            [
                requirement.skill_name
                for requirement
                in requirements
            ],
            [
                "Python",
                "Django",
                "C++",
            ],
        )

        self.assertTrue(
            all(
                requirement.match_source
                == MATCH_SOURCE_CANONICAL
                for requirement
                in requirements
            )
        )


    def test_alias_maps_to_canonical_skill(self):
        SkillAlias.objects.create(
            skill=self.python,
            alias="Py",
        )

        requirements = (
            extract_job_requirements(
                "Strong Py development skills."
            )
        )

        self.assertEqual(
            len(requirements),
            1,
        )

        requirement = requirements[0]

        self.assertEqual(
            requirement.skill_id,
            self.python.id,
        )

        self.assertEqual(
            requirement.skill_name,
            "Python",
        )

        self.assertEqual(
            requirement.matched_term,
            "Py",
        )

        self.assertEqual(
            requirement.match_source,
            MATCH_SOURCE_ALIAS,
        )


    def test_ambiguous_alias_is_not_guessed(self):
        SkillAlias.objects.create(
            skill=self.python,
            alias="Framework",
        )

        SkillAlias.objects.create(
            skill=self.django,
            alias="Framework",
        )

        requirements = (
            extract_job_requirements(
                "Framework experience required."
            )
        )

        self.assertEqual(
            requirements,
            (),
        )


    def test_short_skill_requires_token_boundary(
        self,
    ):
        r_skill = Skill.objects.create(
            name="R",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        requirements = (
            extract_job_requirements(
                "Experience building REST APIs."
            )
        )

        self.assertNotIn(
            r_skill.id,
            {
                requirement.skill_id
                for requirement
                in requirements
            },
        )


    def test_generic_knowledge_verb_context_is_not_requirement(
        self,
    ):
        requirements = (
            extract_job_requirements(
                (
                    "The engineer will design "
                    "features and review code."
                )
            )
        )

        self.assertNotIn(
            self.design.id,
            {
                requirement.skill_id
                for requirement
                in requirements
            },
        )


    def test_generic_knowledge_explicit_context_is_requirement(
        self,
    ):
        requirements = (
            extract_job_requirements(
                (
                    "The engineer will design "
                    "features. Knowledge of "
                    "Design is preferred."
                )
            )
        )

        design_matches = [
            requirement
            for requirement
            in requirements
            if (
                requirement.skill_id
                == self.design.id
            )
        ]

        self.assertEqual(
            len(design_matches),
            1,
        )

        self.assertEqual(
            design_matches[
                0
            ].match_source,
            MATCH_SOURCE_CANONICAL,
        )

        self.assertEqual(
            design_matches[
                0
            ].matched_term,
            "Design",
        )


    def test_related_generic_terms_are_not_guessed(
        self,
    ):
        requirements = (
            extract_job_requirements(
                (
                    "Experience with testing, "
                    "APIs, software development, "
                    "problem solving, and "
                    "communication is required."
                )
            )
        )

        self.assertEqual(
            requirements,
            (),
        )


    def test_student_profile_comparison(self):
        result = match_job_description(
            student_profile=self.profile,
            job_description=(
                "Python and Django experience "
                "are required."
            ),
        )

        self.assertEqual(
            result.matched_requirement_count,
            1,
        )

        self.assertEqual(
            result.missing_requirement_count,
            1,
        )

        self.assertEqual(
            result.total_requirement_count,
            2,
        )

        self.assertEqual(
            result.matched_requirements[
                0
            ].skill_name,
            "Python",
        )

        self.assertEqual(
            result.matched_requirements[
                0
            ].current_proficiency,
            "proficient",
        )

        self.assertEqual(
            result.missing_requirements[
                0
            ].skill_name,
            "Django",
        )

        self.assertIsNone(
            result.missing_requirements[
                0
            ].current_proficiency
        )


    def test_matching_is_deterministic(self):
        description = (
            "Python, Django and C++ "
            "experience required."
        )

        first = match_job_description(
            student_profile=self.profile,
            job_description=description,
        )

        second = match_job_description(
            student_profile=self.profile,
            job_description=description,
        )

        self.assertEqual(
            first,
            second,
        )


class JobDescriptionMatchAPITests(
    APITestCase
):
    def setUp(self):
        user_model = get_user_model()

        self.url = (
            "/api/v1/careers/job-match/"
        )

        self.user = (
            user_model.objects.create_user(
                email=(
                    "job-match-api-a"
                    "@gradnavi.test"
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

        self.other_user = (
            user_model.objects.create_user(
                email=(
                    "job-match-api-b"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.other_profile = (
            StudentProfile.objects.create(
                user=self.other_user,
            )
        )

        self.python = Skill.objects.create(
            name="Python",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        self.django = Skill.objects.create(
            name="Django",
            concept_type=(
                Skill.ConceptType.TECHNOLOGY
            ),
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.python,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .ADVANCED
            ),
        )

        StudentSkill.objects.create(
            student_profile=(
                self.other_profile
            ),
            skill=self.django,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .ADVANCED
            ),
        )

        self.token = str(
            RefreshToken
            .for_user(
                self.user
            )
            .access_token
        )


    def post(
        self,
        payload,
        *,
        authenticated=True,
    ):
        kwargs = {}

        if authenticated:
            kwargs[
                "HTTP_AUTHORIZATION"
            ] = (
                f"Bearer {self.token}"
            )

        return self.client.post(
            self.url,
            payload,
            format="json",
            **kwargs,
        )


    def test_authentication_required(self):
        response = self.post(
            {
                "job_description": (
                    "Python required."
                ),
            },
            authenticated=False,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_blank_job_description_rejected(
        self,
    ):
        response = self.post(
            {
                "job_description": "   ",
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["error"]["code"],
            "validation_error",
        )


    def test_oversized_job_description_rejected(
        self,
    ):
        response = self.post(
            {
                "job_description": (
                    "x"
                    * (
                        JOB_DESCRIPTION_MAX_LENGTH
                        + 1
                    )
                ),
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_unknown_fields_rejected(self):
        response = self.post(
            {
                "job_description": (
                    "Python required."
                ),
                "student_profile_id": (
                    self.other_profile.id
                ),
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data[
                "error"
            ][
                "code"
            ],
            "validation_error",
        )


    def test_authenticated_profile_ownership(
        self,
    ):
        response = self.post(
            {
                "job_description": (
                    "Python and Django required."
                ),
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data["data"]

        self.assertEqual(
            [
                requirement[
                    "skill_name"
                ]
                for requirement
                in data[
                    "matched_requirements"
                ]
            ],
            [
                "Python",
            ],
        )

        self.assertEqual(
            [
                requirement[
                    "skill_name"
                ]
                for requirement
                in data[
                    "missing_requirements"
                ]
            ],
            [
                "Django",
            ],
        )


    def test_complete_response_contract(self):
        response = self.post(
            {
                "job_description": (
                    "Python and Django required."
                ),
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data["data"]

        self.assertEqual(
            set(data),
            {
                "matched_requirement_count",
                "missing_requirement_count",
                "total_requirement_count",
                "canonical_match_count",
                "alias_match_count",
                "matched_requirements",
                "missing_requirements",
            },
        )

        self.assertEqual(
            data[
                "matched_requirement_count"
            ],
            1,
        )

        self.assertEqual(
            data[
                "missing_requirement_count"
            ],
            1,
        )

        self.assertEqual(
            data[
                "total_requirement_count"
            ],
            2,
        )

        requirement_keys = {
            "skill_id",
            "skill_name",
            "concept_type",
            "matched_term",
            "match_source",
            "current_proficiency",
        }

        self.assertEqual(
            set(
                data[
                    "matched_requirements"
                ][0]
            ),
            requirement_keys,
        )


    def test_no_known_requirement_is_valid(
        self,
    ):
        response = self.post(
            {
                "job_description": (
                    "A positive attitude is valued."
                ),
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data["data"]

        self.assertEqual(
            data[
                "total_requirement_count"
            ],
            0,
        )

        self.assertEqual(
            data[
                "matched_requirements"
            ],
            [],
        )

        self.assertEqual(
            data[
                "missing_requirements"
            ],
            [],
        )
