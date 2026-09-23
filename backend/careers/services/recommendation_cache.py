"""
Database-backed Career Recommendation snapshot cache.

The cache avoids repeated AI embedding requests and repeated
composite scoring when recommendation inputs have not changed.

Validity depends on three values:

1. Student recommendation-input fingerprint.
2. Career reference-data fingerprint.
3. Explicit scoring version.

The service stores the serialized recommendation response.
Raw Student Profile data is not stored in RecommendationSnapshot.
"""

from dataclasses import dataclass
import hashlib
import json

from careers.models import (
    Career,
    CareerSkill,
    CareerSkillEvidence,
    RecommendationSnapshot,
    ReferenceDataset,
)

from profiles.models import StudentProfile


SCORING_VERSION = "composite_v1"


@dataclass(frozen=True)
class RecommendationCacheKey:
    profile_fingerprint: str
    reference_fingerprint: str
    scoring_version: str


def _json_hash(value) -> str:
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def build_profile_fingerprint(
    *,
    student_profile: StudentProfile,
) -> str:
    """
    Hash only Student Profile fields used by the current
    composite Career Recommendation model.

    Included:
    - canonical Skills and proficiency,
    - Education qualification, field, description,
    - Experience role and description,
    - Project name and description,
    - Career Goal Career link, target role, description.

    Excluded because the current recommendation model
    does not consume them:
    - Interests,
    - Personality responses,
    - institution names,
    - company names,
    - dates,
    - project URLs,
    - account identity.
    """

    skills = list(
        student_profile.student_skills
        .select_related("skill")
        .order_by(
            "skill_id",
            "id",
        )
        .values(
            "skill_id",
            "skill__name",
            "skill__concept_type",
            "proficiency_level",
        )
    )

    education = list(
        student_profile.education
        .order_by(
            "qualification",
            "field_of_study",
            "description",
            "id",
        )
        .values(
            "qualification",
            "field_of_study",
            "description",
        )
    )

    experience = list(
        student_profile.experience
        .order_by(
            "job_title",
            "description",
            "id",
        )
        .values(
            "job_title",
            "description",
        )
    )

    projects = list(
        student_profile.projects
        .order_by(
            "name",
            "description",
            "id",
        )
        .values(
            "name",
            "description",
        )
    )

    career_goals = list(
        student_profile.career_goals
        .order_by(
            "career_id",
            "target_role",
            "description",
            "id",
        )
        .values(
            "career_id",
            "target_role",
            "description",
            "is_primary",
        )
    )

    payload = {
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "career_goals": career_goals,
    }

    return _json_hash(
        payload
    )


def build_reference_fingerprint() -> str:
    """
    Hash reference records that affect the current composite
    recommendation model.

    The fingerprint covers:
    - active Career identity,
    - reviewed CareerSkill relationships,
    - Career Skill evidence used by competency, technology,
      and semantic scoring,
    - active source dataset identity.

    Field values are hashed directly instead of relying only
    on timestamps.
    """

    careers = list(
        Career.objects
        .filter(
            active=True,
        )
        .order_by(
            "id",
        )
        .values(
            "id",
            "name",
            "description",
            "category",
            "active",
        )
    )

    active_career_ids = [
        row["id"]
        for row in careers
    ]

    career_skills = list(
        CareerSkill.objects
        .filter(
            career_id__in=active_career_ids,
        )
        .order_by(
            "career_id",
            "skill_id",
            "id",
        )
        .values(
            "id",
            "career_id",
            "skill_id",
            "skill__name",
            "skill__concept_type",
            "importance_score",
            "required_level_score",
            "required_proficiency",
            "requirement_type",
            "review_status",
        )
    )

    evidence = list(
        CareerSkillEvidence.objects
        .filter(
            career_skill__career_id__in=(
                active_career_ids
            ),
        )
        .order_by(
            "career_skill_id",
            "dataset_id",
            "id",
        )
        .values(
            "id",
            "career_skill_id",
            "dataset_id",
            "external_occupation_id",
            "external_skill_id",
            "source_domain",
            "source_relation",
            "normalized_importance",
            "normalized_level",
            "not_relevant",
            "recommend_suppress",
            "hot_technology",
            "in_demand",
            "in_demand_percentage",
        )
    )

    datasets = list(
        ReferenceDataset.objects
        .select_related(
            "source",
        )
        .filter(
            status=(
                ReferenceDataset.Status.ACTIVE
            ),
        )
        .order_by(
            "source__name",
            "version",
            "id",
        )
        .values(
            "id",
            "source_id",
            "source__name",
            "version",
            "checksum",
            "status",
        )
    )

    payload = {
        "careers": careers,
        "career_skills": career_skills,
        "career_skill_evidence": evidence,
        "datasets": datasets,
    }

    return _json_hash(
        payload
    )


def build_recommendation_cache_key(
    *,
    student_profile: StudentProfile,
) -> RecommendationCacheKey:
    return RecommendationCacheKey(
        profile_fingerprint=(
            build_profile_fingerprint(
                student_profile=student_profile,
            )
        ),
        reference_fingerprint=(
            build_reference_fingerprint()
        ),
        scoring_version=SCORING_VERSION,
    )


def get_valid_recommendation_snapshot(
    *,
    student_profile: StudentProfile,
    cache_key: RecommendationCacheKey | None = None,
) -> RecommendationSnapshot | None:
    """
    Return the current snapshot only when all validity keys match.
    """

    if cache_key is None:
        cache_key = (
            build_recommendation_cache_key(
                student_profile=student_profile,
            )
        )

    try:
        snapshot = (
            RecommendationSnapshot.objects.get(
                student_profile=student_profile,
            )
        )
    except RecommendationSnapshot.DoesNotExist:
        return None

    if (
        snapshot.profile_fingerprint
        != cache_key.profile_fingerprint
    ):
        return None

    if (
        snapshot.reference_fingerprint
        != cache_key.reference_fingerprint
    ):
        return None

    if (
        snapshot.scoring_version
        != cache_key.scoring_version
    ):
        return None

    return snapshot


def store_recommendation_snapshot(
    *,
    student_profile: StudentProfile,
    payload: dict,
    embedding_model: str,
    prompt_tokens: int,
    total_tokens: int,
    career_count: int,
    cache_key: RecommendationCacheKey | None = None,
) -> RecommendationSnapshot:
    """
    Create or replace the single recommendation snapshot
    owned by one Student Profile.
    """

    if cache_key is None:
        cache_key = (
            build_recommendation_cache_key(
                student_profile=student_profile,
            )
        )

    snapshot, _ = (
        RecommendationSnapshot.objects.update_or_create(
            student_profile=student_profile,
            defaults={
                "profile_fingerprint": (
                    cache_key.profile_fingerprint
                ),
                "reference_fingerprint": (
                    cache_key.reference_fingerprint
                ),
                "scoring_version": (
                    cache_key.scoring_version
                ),
                "payload": payload,
                "embedding_model": (
                    embedding_model or ""
                ),
                "prompt_tokens": (
                    prompt_tokens
                ),
                "total_tokens": (
                    total_tokens
                ),
                "career_count": (
                    career_count
                ),
            },
        )
    )

    return snapshot
