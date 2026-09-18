from django.db import transaction
from rest_framework import serializers

from careers.models import Career

from .models import (
    CareerGoal,
    Education,
    Experience,
    Interest,
    PersonalityResponse,
    Project,
    Skill,
    StudentInterest,
    StudentProfile,
    StudentSkill,
)


class RejectUnknownFieldsMixin:
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected an object.")

        unknown_fields = set(data) - set(self.fields)
        if unknown_fields:
            raise serializers.ValidationError(
                {
                    field: "This field is not allowed."
                    for field in sorted(unknown_fields)
                }
            )

        return super().to_internal_value(data)


class SkillReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = (
            "id",
            "name",
            "category",
            "concept_type",
        )
        read_only_fields = fields


class InterestReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = (
            "id",
            "name",
            "category",
        )
        read_only_fields = fields


class CareerReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = (
            "id",
            "name",
            "category",
            "description",
        )
        read_only_fields = fields


class StudentSkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="skill.id", read_only=True)
    name = serializers.CharField(source="skill.name", read_only=True)
    category = serializers.CharField(source="skill.category", read_only=True)

    class Meta:
        model = StudentSkill
        fields = ("id", "name", "category", "proficiency_level")
        read_only_fields = fields


class StudentInterestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="interest.id", read_only=True)
    name = serializers.CharField(source="interest.name", read_only=True)
    category = serializers.CharField(source="interest.category", read_only=True)

    class Meta:
        model = StudentInterest
        fields = ("id", "name", "category")
        read_only_fields = fields


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            "id",
            "institution_name",
            "qualification",
            "field_of_study",
            "start_date",
            "end_date",
            "description",
        )
        read_only_fields = fields


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = (
            "id",
            "job_title",
            "company",
            "start_date",
            "end_date",
            "is_current",
            "description",
        )
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "project_url",
            "start_date",
            "end_date",
        )
        read_only_fields = fields


class CareerGoalSerializer(serializers.ModelSerializer):
    career_id = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = CareerGoal
        fields = (
            "id",
            "career_id",
            "target_role",
            "description",
            "is_primary",
        )
        read_only_fields = fields


class PersonalityResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalityResponse
        fields = ("id", "question_key", "response_value")
        read_only_fields = fields


class StudentProfileSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    career_goals = serializers.SerializerMethodField()
    personality_responses = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = (
            "skills",
            "interests",
            "education",
            "experience",
            "projects",
            "career_goals",
            "personality_responses",
        )
        read_only_fields = fields

    def get_skills(self, profile):
        student_skills = profile.student_skills.select_related("skill").order_by("id")
        return StudentSkillSerializer(student_skills, many=True).data

    def get_interests(self, profile):
        student_interests = profile.student_interests.select_related("interest").order_by("id")
        return StudentInterestSerializer(student_interests, many=True).data

    def get_education(self, profile):
        return EducationSerializer(profile.education.order_by("id"), many=True).data

    def get_experience(self, profile):
        return ExperienceSerializer(profile.experience.order_by("id"), many=True).data

    def get_projects(self, profile):
        return ProjectSerializer(profile.projects.order_by("id"), many=True).data

    def get_career_goals(self, profile):
        return CareerGoalSerializer(profile.career_goals.order_by("id"), many=True).data

    def get_personality_responses(self, profile):
        return PersonalityResponseSerializer(
            profile.personality_responses.order_by("id"),
            many=True,
        ).data


class StudentSkillWriteSerializer(RejectUnknownFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False, allow_blank=False)
    proficiency_level = serializers.ChoiceField(choices=StudentSkill.ProficiencyLevel.choices)

    def validate(self, attrs):
        skill = self._get_skill(attrs)
        attrs["skill"] = skill
        return attrs

    def _get_skill(self, attrs):
        if "id" in attrs:
            try:
                return Skill.objects.get(pk=attrs["id"])
            except Skill.DoesNotExist:
                raise serializers.ValidationError({"id": "Skill does not exist."})

        if "name" in attrs:
            try:
                return Skill.objects.get(name__iexact=attrs["name"])
            except Skill.DoesNotExist:
                raise serializers.ValidationError({"name": "Skill does not exist."})

        raise serializers.ValidationError({"id": "Provide an existing skill id or name."})


class StudentInterestWriteSerializer(RejectUnknownFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False, allow_blank=False)

    def validate(self, attrs):
        interest = self._get_interest(attrs)
        attrs["interest"] = interest
        return attrs

    def _get_interest(self, attrs):
        if "id" in attrs:
            try:
                return Interest.objects.get(pk=attrs["id"])
            except Interest.DoesNotExist:
                raise serializers.ValidationError({"id": "Interest does not exist."})

        if "name" in attrs:
            try:
                return Interest.objects.get(name__iexact=attrs["name"])
            except Interest.DoesNotExist:
                raise serializers.ValidationError({"name": "Interest does not exist."})

        raise serializers.ValidationError({"id": "Provide an existing interest id or name."})


class OwnedModelWriteSerializer(RejectUnknownFieldsMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    def validate_id(self, value):
        profile = self.context["profile"]
        model = self.Meta.model

        if not model.objects.filter(pk=value, student_profile=profile).exists():
            raise serializers.ValidationError(
                f"{model.__name__} does not belong to the authenticated profile."
            )

        return value

    def validate(self, attrs):
        instance = self._get_existing_instance(attrs)
        start_date = attrs.get(
            "start_date",
            getattr(instance, "start_date", None),
        )
        end_date = attrs.get(
            "end_date",
            getattr(instance, "end_date", None),
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must not precede start date."}
            )

        return attrs

    def _get_existing_instance(self, attrs):
        item_id = attrs.get("id")
        if item_id is None:
            return None

        return self.Meta.model.objects.get(
            pk=item_id,
            student_profile=self.context["profile"],
        )


class EducationWriteSerializer(OwnedModelWriteSerializer):
    class Meta:
        model = Education
        fields = (
            "id",
            "institution_name",
            "qualification",
            "field_of_study",
            "start_date",
            "end_date",
            "description",
        )
        extra_kwargs = {
            "end_date": {"required": False, "allow_null": True},
            "description": {"required": False, "allow_blank": True},
        }


class ExperienceWriteSerializer(OwnedModelWriteSerializer):
    class Meta:
        model = Experience
        fields = (
            "id",
            "job_title",
            "company",
            "start_date",
            "end_date",
            "is_current",
            "description",
        )
        extra_kwargs = {
            "end_date": {"required": False, "allow_null": True},
            "is_current": {"required": False},
            "description": {"required": False, "allow_blank": True},
        }


class ProjectWriteSerializer(OwnedModelWriteSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "project_url",
            "start_date",
            "end_date",
        )
        extra_kwargs = {
            "description": {"required": False, "allow_blank": True},
            "project_url": {"required": False, "allow_blank": True},
            "end_date": {"required": False, "allow_null": True},
        }


class CareerGoalWriteSerializer(
    RejectUnknownFieldsMixin,
    serializers.Serializer,
):
    """
    Structured Career Goal input.

    Preferred input:
    - career_id
    - description
    - is_primary

    target_role stays accepted as a legacy compatibility path.
    When target_role matches an active Career, the goal is linked
    to that Career automatically.
    """

    id = serializers.IntegerField(
        required=False,
    )

    career_id = serializers.IntegerField(
        required=False,
    )

    target_role = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=255,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    is_primary = serializers.BooleanField(
        required=False,
    )

    class Meta:
        model = CareerGoal

    def validate_id(
        self,
        value,
    ):
        profile = self.context[
            "profile"
        ]

        if not (
            CareerGoal.objects
            .filter(
                pk=value,
                student_profile=profile,
            )
            .exists()
        ):
            raise serializers.ValidationError(
                "CareerGoal does not belong "
                "to the authenticated profile."
            )

        return value

    def validate(
        self,
        attrs,
    ):
        instance = (
            self._get_existing_instance(
                attrs
            )
        )

        has_career_id = (
            "career_id"
            in attrs
        )

        has_target_role = (
            "target_role"
            in attrs
        )

        career = None

        if has_career_id:
            career = (
                self._get_active_career(
                    attrs[
                        "career_id"
                    ]
                )
            )

        if (
            has_career_id
            and has_target_role
        ):
            supplied_role = (
                attrs[
                    "target_role"
                ].strip()
            )

            if (
                supplied_role.casefold()
                != career.name.casefold()
            ):
                raise serializers.ValidationError(
                    {
                        "target_role": (
                            "target_role must match "
                            "the selected career_id."
                        )
                    }
                )

        if career is not None:
            attrs[
                "career"
            ] = career

            attrs[
                "target_role"
            ] = career.name

            return attrs

        if has_target_role:
            target_role = (
                attrs[
                    "target_role"
                ].strip()
            )

            matched_career = (
                Career.objects
                .filter(
                    active=True,
                    name__iexact=target_role,
                )
                .order_by(
                    "id"
                )
                .first()
            )

            if (
                matched_career
                is not None
            ):
                attrs[
                    "career"
                ] = matched_career

                attrs[
                    "target_role"
                ] = (
                    matched_career.name
                )

            elif instance is not None:
                attrs[
                    "career"
                ] = None

                attrs[
                    "target_role"
                ] = target_role

            else:
                # Legacy compatibility for older clients.
                # New frontend code uses career_id.
                attrs[
                    "target_role"
                ] = target_role

            return attrs

        if instance is not None:
            if (
                instance.career_id
                is not None
            ):
                attrs[
                    "career"
                ] = instance.career

                attrs[
                    "target_role"
                ] = (
                    instance.career.name
                )

            else:
                attrs[
                    "target_role"
                ] = (
                    instance.target_role
                )

            return attrs

        raise serializers.ValidationError(
            {
                "career_id": (
                    "Provide an active career_id."
                )
            }
        )

    def _get_active_career(
        self,
        career_id,
    ):
        try:
            return Career.objects.get(
                pk=career_id,
                active=True,
            )

        except Career.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "career_id": (
                        "Active Career does not exist."
                    )
                }
            )

    def _get_existing_instance(
        self,
        attrs,
    ):
        item_id = attrs.get(
            "id"
        )

        if item_id is None:
            return None

        return (
            CareerGoal.objects
            .select_related(
                "career"
            )
            .get(
                pk=item_id,
                student_profile=self.context[
                    "profile"
                ],
            )
        )


class PersonalityResponseWriteSerializer(OwnedModelWriteSerializer):
    class Meta:
        model = PersonalityResponse
        fields = ("id", "question_key", "response_value")


class StudentProfileUpdateSerializer(RejectUnknownFieldsMixin, serializers.Serializer):
    skills = serializers.ListField(child=serializers.JSONField(), required=False)
    interests = serializers.ListField(child=serializers.JSONField(), required=False)
    education = serializers.ListField(child=serializers.DictField(), required=False)
    experience = serializers.ListField(child=serializers.DictField(), required=False)
    projects = serializers.ListField(child=serializers.DictField(), required=False)
    career_goals = serializers.ListField(child=serializers.JSONField(), required=False)
    personality_responses = serializers.ListField(
        child=serializers.DictField(),
        required=False,
    )

    def validate(self, attrs):
        profile = self.context["profile"]
        validators = {
            "skills": self._validate_skills,
            "interests": self._validate_interests,
            "education": lambda items: self._validate_model_items(
                items,
                EducationWriteSerializer,
                profile,
            ),
            "experience": lambda items: self._validate_model_items(
                items,
                ExperienceWriteSerializer,
                profile,
            ),
            "projects": lambda items: self._validate_model_items(
                items,
                ProjectWriteSerializer,
                profile,
            ),
            "career_goals": self._validate_career_goals,
            "personality_responses": lambda items: self._validate_model_items(
                items,
                PersonalityResponseWriteSerializer,
                profile,
            ),
        }

        for field, validator in validators.items():
            if field in attrs:
                attrs[field] = validator(attrs[field])

        return attrs

    def save(self, **kwargs):
        profile = self.context["profile"]

        with transaction.atomic():
            if "skills" in self.validated_data:
                self._replace_skills(profile, self.validated_data["skills"])
            if "interests" in self.validated_data:
                self._replace_interests(profile, self.validated_data["interests"])
            if "education" in self.validated_data:
                self._replace_owned_collection(
                    profile,
                    Education,
                    self.validated_data["education"],
                )
            if "experience" in self.validated_data:
                self._replace_owned_collection(
                    profile,
                    Experience,
                    self.validated_data["experience"],
                )
            if "projects" in self.validated_data:
                self._replace_owned_collection(
                    profile,
                    Project,
                    self.validated_data["projects"],
                )
            if "career_goals" in self.validated_data:
                self._replace_career_goals(
                    profile,
                    self.validated_data[
                        "career_goals"
                    ],
                )
            if "personality_responses" in self.validated_data:
                self._replace_owned_collection(
                    profile,
                    PersonalityResponse,
                    self.validated_data["personality_responses"],
                )

        profile.refresh_from_db()
        return profile

    def _validate_skills(self, items):
        serializer = StudentSkillWriteSerializer(data=items, many=True)
        serializer.is_valid(raise_exception=True)
        validated_items = serializer.validated_data
        self._validate_unique_related_ids(
            [item["skill"].id for item in validated_items],
            "skills",
        )
        return validated_items

    def _validate_interests(self, items):
        normalized_items = [
            {"name": item} if isinstance(item, str) else item
            for item in items
        ]
        serializer = StudentInterestWriteSerializer(data=normalized_items, many=True)
        serializer.is_valid(raise_exception=True)
        validated_items = serializer.validated_data
        self._validate_unique_related_ids(
            [item["interest"].id for item in validated_items],
            "interests",
        )
        return validated_items

    def _validate_career_goals(
        self,
        items,
    ):
        normalized_items = [
            {
                "target_role": item
            }
            if isinstance(
                item,
                str,
            )
            else item
            for item
            in items
        ]

        validated_items = (
            self._validate_model_items(
                normalized_items,
                CareerGoalWriteSerializer,
                self.context[
                    "profile"
                ],
            )
        )

        seen_career_ids = set()
        seen_legacy_roles = set()

        for item in validated_items:
            career = item.get(
                "career"
            )

            if career is not None:
                if (
                    career.id
                    in seen_career_ids
                ):
                    raise serializers.ValidationError(
                        {
                            "career_goals": (
                                "Duplicate Careers "
                                "are not allowed."
                            )
                        }
                    )

                seen_career_ids.add(
                    career.id
                )

            else:
                legacy_role = (
                    item[
                        "target_role"
                    ]
                    .strip()
                    .casefold()
                )

                if (
                    legacy_role
                    in seen_legacy_roles
                ):
                    raise serializers.ValidationError(
                        {
                            "career_goals": (
                                "Duplicate Career Goals "
                                "are not allowed."
                            )
                        }
                    )

                seen_legacy_roles.add(
                    legacy_role
                )

        for item in validated_items:
            if (
                "is_primary"
                in item
            ):
                continue

            item_id = item.get(
                "id"
            )

            if item_id is None:
                item[
                    "is_primary"
                ] = False

                continue

            existing = (
                CareerGoal.objects
                .only(
                    "is_primary"
                )
                .get(
                    pk=item_id,
                    student_profile=(
                        self.context[
                            "profile"
                        ]
                    ),
                )
            )

            item[
                "is_primary"
            ] = (
                existing.is_primary
            )

        primary_count = sum(
            1
            for item
            in validated_items
            if item[
                "is_primary"
            ]
        )

        if (
            validated_items
            and primary_count == 0
        ):
            validated_items[
                0
            ][
                "is_primary"
            ] = True

            primary_count = 1

        if primary_count > 1:
            raise serializers.ValidationError(
                {
                    "career_goals": (
                        "Only one Career Goal "
                        "may be primary."
                    )
                }
            )

        return validated_items

    def _validate_model_items(self, items, serializer_class, profile):
        validated_items = []

        for item in items:
            serializer = serializer_class(
                data=item,
                context={"profile": profile},
                partial="id" in item,
            )
            serializer.is_valid(raise_exception=True)
            validated_items.append(serializer.validated_data)

        self._validate_unique_item_ids(validated_items, serializer_class.Meta.model.__name__)
        return validated_items

    def _validate_unique_related_ids(self, values, field):
        if len(values) != len(set(values)):
            raise serializers.ValidationError({field: "Duplicate values are not allowed."})

    def _validate_unique_item_ids(self, items, model_name):
        item_ids = [item["id"] for item in items if "id" in item]
        if len(item_ids) != len(set(item_ids)):
            raise serializers.ValidationError(
                {model_name: "Duplicate item ids are not allowed."}
            )

    def _replace_skills(self, profile, items):
        profile.student_skills.all().delete()
        StudentSkill.objects.bulk_create(
            [
                StudentSkill(
                    student_profile=profile,
                    skill=item["skill"],
                    proficiency_level=item["proficiency_level"],
                )
                for item in items
            ]
        )

    def _replace_interests(self, profile, items):
        profile.student_interests.all().delete()
        StudentInterest.objects.bulk_create(
            [
                StudentInterest(
                    student_profile=profile,
                    interest=item["interest"],
                )
                for item in items
            ]
        )

    def _replace_career_goals(
        self,
        profile,
        items,
    ):
        supplied_ids = [
            item[
                "id"
            ]
            for item
            in items
            if "id"
            in item
        ]

        (
            CareerGoal.objects
            .filter(
                student_profile=profile
            )
            .exclude(
                id__in=supplied_ids
            )
            .delete()
        )

        # Clear constrained values first.
        # This makes Career swaps and primary-goal
        # changes safe inside the transaction.
        (
            CareerGoal.objects
            .filter(
                student_profile=profile,
                id__in=supplied_ids,
            )
            .update(
                career=None,
                is_primary=False,
            )
        )

        for item in items:
            values = dict(
                item
            )

            item_id = values.pop(
                "id",
                None,
            )

            # career_id is an API input field.
            # Validation resolves it to the Career
            # model instance stored in "career".
            #
            # Keeping both "career_id" and "career"
            # would assign the same database column
            # twice during QuerySet.update().
            values.pop(
                "career_id",
                None,
            )

            if item_id is None:
                CareerGoal.objects.create(
                    student_profile=profile,
                    **values,
                )

            else:
                (
                    CareerGoal.objects
                    .filter(
                        id=item_id,
                        student_profile=profile,
                    )
                    .update(
                        **values
                    )
                )

    def _replace_owned_collection(self, profile, model, items):
        supplied_ids = [item["id"] for item in items if "id" in item]
        model.objects.filter(student_profile=profile).exclude(id__in=supplied_ids).delete()

        for item in items:
            item = dict(item)
            item_id = item.pop("id", None)
            if item_id is None:
                model.objects.create(student_profile=profile, **item)
            else:
                model.objects.filter(id=item_id, student_profile=profile).update(**item)
