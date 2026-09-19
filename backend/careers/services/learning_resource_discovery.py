"""
Learning Resource discovery validation and persistence.

Only web-source-backed candidates are eligible for persistence.

This service performs no external network request and no AI call.
It validates output already returned by the dedicated discovery
provider and persists accepted resources into the controlled
LearningResource catalogue.
"""

from dataclasses import dataclass
from datetime import timedelta
from hashlib import sha256
import re
from typing import Iterable
from urllib.parse import (
    urlsplit,
    urlunsplit,
)

from django.core.exceptions import (
    ValidationError,
)
from django.core.validators import (
    URLValidator,
)
from django.db import transaction
from django.utils import timezone

from ai_services.exceptions import (
    AIProviderError,
)
from ai_services.prompts.learning_resource_discovery import (
    build_learning_resource_discovery_prompt,
)
from ai_services.providers.openai_web_search import (
    OpenAIWebSearchProvider,
)
from ai_services.schemas.inputs import (
    LearningResourceDiscoveryInput,
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
from profiles.models import Skill


SUPPORTED_DISCOVERY_ACCESS_TYPES = {
    "all",
    LearningResource.AccessType.FREE,
    LearningResource.AccessType.FREEMIUM,
    LearningResource.AccessType.PAID,
}


REJECTION_MISSING_SOURCE_EVIDENCE = (
    "missing_source_evidence"
)

REJECTION_ACCESS_FILTER_MISMATCH = (
    "access_filter_mismatch"
)

REJECTION_ALREADY_LINKED_TO_SKILL = (
    "already_linked_to_skill"
)

REJECTION_DUPLICATE_CANDIDATE = (
    "duplicate_candidate"
)

REJECTION_INVALID_URL = (
    "invalid_url"
)


@dataclass(
    frozen=True,
)
class PersistedLearningResource:
    resource_id: int
    url: str
    created: bool
    link_created: bool


@dataclass(
    frozen=True,
)
class RejectedLearningResource:
    url: str
    reason: str


@dataclass(
    frozen=True,
)
class LearningResourceDiscoveryPersistenceResult:
    persisted: tuple[
        PersistedLearningResource,
        ...,
    ]

    rejected: tuple[
        RejectedLearningResource,
        ...,
    ]




_OPENAI_MARKDOWN_CITATION_PATTERN = re.compile(
    r"""
    \s*
    \(
        \[
            [^\]]+
        \]
        \(
            https?://
            [^)]+
            utm_source=openai
            [^)]*
        \)
    \)
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)


_OPENAI_INLINE_CITATION_PATTERN = re.compile(
    r"""
    \s*
    \[
        [^\]]+
    \]
    \(
        https?://
        [^)]+
        utm_source=openai
        [^)]*
    \)
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)


def sanitize_discovered_description(
    value,
) -> str:
    """
    Remove OpenAI web-search citation markup before persistence.

    The canonical resource URL is stored separately in
    LearningResource.url.
    """

    text = str(
        value
        or ""
    ).strip()

    text = (
        _OPENAI_MARKDOWN_CITATION_PATTERN
        .sub(
            "",
            text,
        )
    )

    text = (
        _OPENAI_INLINE_CITATION_PATTERN
        .sub(
            "",
            text,
        )
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def normalize_resource_url(
    value,
) -> str:
    """
    Normalize one external Learning Resource URL.

    Rules:

    - HTTP and HTTPS only
    - lower-case scheme and hostname
    - reject embedded credentials
    - remove URL fragments
    - remove trailing slash except for root
    - preserve query strings
    """

    raw = str(
        value
        or ""
    ).strip()

    if not raw:
        raise ValueError(
            "Resource URL must not be blank."
        )

    parsed = urlsplit(
        raw
    )

    scheme = (
        parsed.scheme
        .lower()
    )

    if scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Resource URL must use HTTP or HTTPS."
        )

    if not parsed.hostname:
        raise ValueError(
            "Resource URL must contain a hostname."
        )

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "Resource URL must not contain credentials."
        )

    hostname = (
        parsed.hostname
        .lower()
    )

    port = (
        parsed.port
    )

    if (
        port is None
        or (
            scheme == "http"
            and port == 80
        )
        or (
            scheme == "https"
            and port == 443
        )
    ):
        netloc = hostname

    else:
        netloc = (
            f"{hostname}:{port}"
        )

    path = (
        parsed.path
        or "/"
    )

    if (
        path != "/"
        and path.endswith(
            "/"
        )
    ):
        path = path.rstrip(
            "/"
        )

    normalized = urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            "",
        )
    )

    validate_url = URLValidator(
        schemes=[
            "http",
            "https",
        ]
    )

    try:
        validate_url(
            normalized
        )

    except ValidationError as error:
        raise ValueError(
            "Resource URL failed URL validation."
        ) from error

    return normalized


def _normalize_source_urls(
    source_urls: Iterable[str],
) -> set[str]:
    normalized = set()

    for url in source_urls:

        try:
            value = (
                normalize_resource_url(
                    url
                )
            )

        except ValueError:
            continue

        normalized.add(
            value
        )

    return normalized


def _resource_key_for_url(
    normalized_url: str,
) -> str:
    digest = (
        sha256(
            normalized_url.encode(
                "utf-8"
            )
        )
        .hexdigest()
    )

    return (
        f"discovered:{digest}"
    )


def _load_existing_resources_by_url():
    resources_by_url = {}

    queryset = (
        LearningResource
        .objects
        .all()
        .only(
            "id",
            "resource_key",
            "title",
            "provider",
            "url",
            "resource_type",
            "description",
            "is_active",
            "access_type",
            "source_type",
            "health_status",
            "last_checked_at",
            "last_verified_at",
        )
        .order_by(
            "id"
        )
    )

    for resource in queryset:

        try:
            normalized = (
                normalize_resource_url(
                    resource.url
                )
            )

        except ValueError:
            continue

        resources_by_url.setdefault(
            normalized,
            resource,
        )

    return resources_by_url


def _candidate_matches_access_filter(
    *,
    candidate: DiscoveredLearningResourceCandidate,
    requested_access_type: str,
) -> bool:

    if requested_access_type == "all":
        return True

    return (
        candidate.access_type
        == requested_access_type
    )


def _update_existing_discovered_resource(
    *,
    resource: LearningResource,
    candidate: DiscoveredLearningResourceCandidate,
    normalized_url: str,
    checked_at,
):
    """
    Refresh metadata only for previously discovered records.

    Curated records keep their reviewed metadata.
    """

    if (
        resource.source_type
        != LearningResource
        .SourceType
        .DISCOVERED
    ):
        return

    resource.title = (
        candidate.title
    )

    resource.provider = (
        candidate.provider
    )

    resource.url = (
        normalized_url
    )

    resource.resource_type = (
        candidate.resource_type
    )

    resource.description = (
        sanitize_discovered_description(
            candidate.description
        )
    )

    resource.is_active = True

    resource.access_type = (
        candidate.access_type
    )

    resource.health_status = (
        LearningResource
        .HealthStatus
        .ACTIVE
    )

    resource.last_checked_at = (
        checked_at
    )

    resource.last_verified_at = (
        checked_at
    )

    resource.save(
        update_fields=[
            "title",
            "provider",
            "url",
            "resource_type",
            "description",
            "is_active",
            "access_type",
            "health_status",
            "last_checked_at",
            "last_verified_at",
            "updated_at",
        ]
    )


@transaction.atomic
def persist_source_backed_learning_resources(
    *,
    skill_id: int,
    discovery_result: (
        LearningResourceDiscoveryResult
    ),
    source_urls: Iterable[str],
    requested_access_type: str = "all",
) -> (
    LearningResourceDiscoveryPersistenceResult
):
    """
    Persist source-backed Learning Resource candidates.

    Candidate URLs must appear in the web-search source set
    after normalization.

    A resource already linked to the requested Skill is not
    persisted again.

    An existing resource linked elsewhere is reused instead
    of creating a duplicate LearningResource record.
    """

    if (
        requested_access_type
        not in SUPPORTED_DISCOVERY_ACCESS_TYPES
    ):
        raise ValueError(
            "Unsupported discovery access type."
        )

    try:
        skill = (
            Skill.objects.get(
                id=skill_id
            )
        )

    except Skill.DoesNotExist as error:
        raise ValueError(
            "Skill was not found."
        ) from error

    normalized_sources = (
        _normalize_source_urls(
            source_urls
        )
    )

    resources_by_url = (
        _load_existing_resources_by_url()
    )

    checked_at = (
        timezone.now()
    )

    seen_candidate_urls = set()

    persisted = []

    rejected = []

    for candidate in (
        discovery_result
        .candidates
    ):

        try:
            normalized_url = (
                normalize_resource_url(
                    candidate.url
                )
            )

        except ValueError:
            rejected.append(
                RejectedLearningResource(
                    url=(
                        str(
                            candidate.url
                        )
                    ),
                    reason=(
                        REJECTION_INVALID_URL
                    ),
                )
            )

            continue

        if (
            normalized_url
            in seen_candidate_urls
        ):
            rejected.append(
                RejectedLearningResource(
                    url=normalized_url,
                    reason=(
                        REJECTION_DUPLICATE_CANDIDATE
                    ),
                )
            )

            continue

        seen_candidate_urls.add(
            normalized_url
        )

        if (
            normalized_url
            not in normalized_sources
        ):
            rejected.append(
                RejectedLearningResource(
                    url=normalized_url,
                    reason=(
                        REJECTION_MISSING_SOURCE_EVIDENCE
                    ),
                )
            )

            continue

        if not (
            _candidate_matches_access_filter(
                candidate=candidate,
                requested_access_type=(
                    requested_access_type
                ),
            )
        ):
            rejected.append(
                RejectedLearningResource(
                    url=normalized_url,
                    reason=(
                        REJECTION_ACCESS_FILTER_MISMATCH
                    ),
                )
            )

            continue

        existing_resource = (
            resources_by_url.get(
                normalized_url
            )
        )

        if (
            existing_resource
            is not None
            and
            LearningResourceSkill
            .objects
            .filter(
                learning_resource=(
                    existing_resource
                ),
                skill=skill,
            )
            .exists()
        ):
            rejected.append(
                RejectedLearningResource(
                    url=normalized_url,
                    reason=(
                        REJECTION_ALREADY_LINKED_TO_SKILL
                    ),
                )
            )

            continue

        created = False

        if existing_resource is None:

            resource = (
                LearningResource
                .objects
                .create(
                    resource_key=(
                        _resource_key_for_url(
                            normalized_url
                        )
                    ),
                    title=(
                        candidate.title
                    ),
                    provider=(
                        candidate.provider
                    ),
                    url=normalized_url,
                    resource_type=(
                        candidate
                        .resource_type
                    ),
                    description=(
                        sanitize_discovered_description(
                            candidate.description
                        )
                    ),
                    is_active=True,
                    access_type=(
                        candidate
                        .access_type
                    ),
                    source_type=(
                        LearningResource
                        .SourceType
                        .DISCOVERED
                    ),
                    health_status=(
                        LearningResource
                        .HealthStatus
                        .ACTIVE
                    ),
                    last_checked_at=(
                        checked_at
                    ),
                    last_verified_at=(
                        checked_at
                    ),
                )
            )

            resources_by_url[
                normalized_url
            ] = resource

            created = True

        else:
            resource = (
                existing_resource
            )

            _update_existing_discovered_resource(
                resource=resource,
                candidate=candidate,
                normalized_url=(
                    normalized_url
                ),
                checked_at=(
                    checked_at
                ),
            )

        (
            _link,
            link_created,
        ) = (
            LearningResourceSkill
            .objects
            .get_or_create(
                learning_resource=(
                    resource
                ),
                skill=skill,
            )
        )

        persisted.append(
            PersistedLearningResource(
                resource_id=(
                    resource.id
                ),
                url=(
                    normalized_url
                ),
                created=created,
                link_created=(
                    link_created
                ),
            )
        )

    return (
        LearningResourceDiscoveryPersistenceResult(
            persisted=tuple(
                persisted
            ),
            rejected=tuple(
                rejected
            ),
        )
    )


DISCOVERY_TARGET_RESOURCE_COUNT = 6

DISCOVERY_COMPLETED_COOLDOWN = (
    timedelta(
        days=30,
    )
)

DISCOVERY_PARTIAL_COOLDOWN = (
    timedelta(
        days=1,
    )
)

DISCOVERY_PROVIDER_FAILURE_COOLDOWN = (
    timedelta(
        hours=24,
    )
)


@dataclass(
    frozen=True,
)
class LearningResourceDiscoveryEligibility:
    eligible: bool
    latest_status: str | None
    next_eligible_at: object | None


def discovery_cooldown_for_status(
    status: str,
):
    if (
        status
        ==
        LearningResourceDiscoveryAttempt
        .Status
        .SUCCESS
    ):
        return (
            DISCOVERY_COMPLETED_COOLDOWN
        )

    if (
        status
        ==
        LearningResourceDiscoveryAttempt
        .Status
        .NO_RESULTS
    ):
        return (
            DISCOVERY_COMPLETED_COOLDOWN
        )

    if (
        status
        ==
        LearningResourceDiscoveryAttempt
        .Status
        .PARTIAL
    ):
        return (
            DISCOVERY_PARTIAL_COOLDOWN
        )

    if (
        status
        ==
        LearningResourceDiscoveryAttempt
        .Status
        .PROVIDER_FAILURE
    ):
        return (
            DISCOVERY_PROVIDER_FAILURE_COOLDOWN
        )

    raise ValueError(
        "Unsupported discovery attempt status."
    )


def get_latest_discovery_attempt(
    *,
    skill_id: int,
):
    return (
        LearningResourceDiscoveryAttempt
        .objects
        .filter(
            skill_id=skill_id,
        )
        .order_by(
            "-attempted_at",
            "-id",
        )
        .first()
    )


def get_discovery_eligibility(
    *,
    skill_id: int,
    at=None,
) -> LearningResourceDiscoveryEligibility:
    resolved_at = (
        at
        or timezone.now()
    )

    latest = (
        get_latest_discovery_attempt(
            skill_id=skill_id,
        )
    )

    if latest is None:
        return (
            LearningResourceDiscoveryEligibility(
                eligible=True,
                latest_status=None,
                next_eligible_at=None,
            )
        )

    return (
        LearningResourceDiscoveryEligibility(
            eligible=(
                latest.next_eligible_at
                <= resolved_at
            ),
            latest_status=(
                latest.status
            ),
            next_eligible_at=(
                latest.next_eligible_at
            ),
        )
    )


def record_discovery_attempt(
    *,
    skill_id: int,
    status: str,
    requested_count: int,
    candidate_count: int,
    persisted_count: int,
    at=None,
):
    resolved_at = (
        at
        or timezone.now()
    )

    try:
        resolved_requested_count = int(
            requested_count
        )

        resolved_candidate_count = int(
            candidate_count
        )

        resolved_persisted_count = int(
            persisted_count
        )

    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "Discovery counts must be integers."
        ) from error

    if not (
        1
        <= resolved_requested_count
        <= DISCOVERY_TARGET_RESOURCE_COUNT
    ):
        raise ValueError(
            "requested_count must be between 1 and 6."
        )

    if not (
        0
        <= resolved_candidate_count
        <= resolved_requested_count
    ):
        raise ValueError(
            "candidate_count must be between 0 "
            "and requested_count."
        )

    if not (
        0
        <= resolved_persisted_count
        <= resolved_candidate_count
    ):
        raise ValueError(
            "persisted_count must be between 0 "
            "and candidate_count."
        )

    cooldown = (
        discovery_cooldown_for_status(
            status
        )
    )

    next_eligible_at = (
        resolved_at
        + cooldown
    )

    try:
        skill = (
            Skill.objects.get(
                id=skill_id
            )
        )

    except Skill.DoesNotExist as error:
        raise ValueError(
            "Skill was not found."
        ) from error

    attempt = (
        LearningResourceDiscoveryAttempt(
            skill=skill,
            status=status,
            requested_count=(
                resolved_requested_count
            ),
            candidate_count=(
                resolved_candidate_count
            ),
            persisted_count=(
                resolved_persisted_count
            ),
            next_eligible_at=(
                next_eligible_at
            ),
        )
    )

    attempt.full_clean()

    attempt.save()

    return attempt


DISCOVERY_REASON_ENOUGH_RESOURCES = (
    "enough_resources"
)

DISCOVERY_REASON_COOLDOWN = (
    "cooldown"
)

DISCOVERY_REASON_COMPLETED = (
    "completed"
)

DISCOVERY_REASON_PROVIDER_FAILURE = (
    "provider_failure"
)


@dataclass(
    frozen=True,
)
class LearningResourceDiscoveryRunResult:
    attempted: bool
    reason: str
    status: str | None
    resource_count_before: int
    resource_count_after: int
    requested_count: int
    candidate_count: int
    persisted_count: int
    next_eligible_at: object | None
    rejected_count: int = 0
    rejection_reasons: tuple[str, ...] = ()


def count_valid_learning_resources(
    *,
    skill_id: int,
) -> int:
    """
    Count globally stored usable Learning Resources
    linked to one canonical Skill.

    Access type is intentionally ignored.
    """

    return (
        LearningResource
        .objects
        .filter(
            skill_links__skill_id=skill_id,
            is_active=True,
            health_status=(
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )
        .distinct()
        .count()
    )


def load_valid_learning_resource_urls(
    *,
    skill_id: int,
) -> tuple[str, ...]:
    """
    Return URLs already usable for this Skill.

    These URLs are supplied to discovery to reduce
    same-Skill duplicate suggestions.
    """

    urls = (
        LearningResource
        .objects
        .filter(
            skill_links__skill_id=skill_id,
            is_active=True,
            health_status=(
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )
        .order_by(
            "id"
        )
        .values_list(
            "url",
            flat=True,
        )
        .distinct()
    )

    return tuple(
        str(
            url
        )
        for url
        in urls
    )


def _bounded_discovery_result(
    *,
    discovery_result: (
        LearningResourceDiscoveryResult
    ),
    requested_count: int,
) -> LearningResourceDiscoveryResult:
    """
    Enforce the application request limit even when
    an external provider returns extra candidates.
    """

    bounded_candidates = (
        discovery_result
        .candidates[
            :requested_count
        ]
    )

    if (
        len(
            bounded_candidates
        )
        ==
        len(
            discovery_result
            .candidates
        )
    ):
        return discovery_result

    return (
        LearningResourceDiscoveryResult(
            candidates=list(
                bounded_candidates
            ),
            is_ai_generated=True,
        )
    )


def _status_after_discovery(
    *,
    resource_count_after: int,
    candidate_count: int,
) -> str:
    if candidate_count == 0:
        return (
            LearningResourceDiscoveryAttempt
            .Status
            .NO_RESULTS
        )

    if (
        resource_count_after
        >= DISCOVERY_TARGET_RESOURCE_COUNT
    ):
        return (
            LearningResourceDiscoveryAttempt
            .Status
            .SUCCESS
        )

    return (
        LearningResourceDiscoveryAttempt
        .Status
        .PARTIAL
    )


def ensure_learning_resource_catalogue(
    *,
    skill_id: int,
    provider=None,
    at=None,
) -> LearningResourceDiscoveryRunResult:
    """
    Demand-driven global Learning Resource discovery.

    Rules:

    - discovery key is Skill only
    - discovery ignores Student identity
    - discovery ignores access filters
    - six valid resources is the minimum target
    - existing resources are reused across Students
    - recent discovery attempts respect the cooldown
    - provider failure returns existing catalogue data
      rather than breaking Learning Resources
    """

    resolved_at = (
        at
        or timezone.now()
    )

    try:
        skill = (
            Skill.objects.get(
                id=skill_id
            )
        )

    except Skill.DoesNotExist as error:
        raise ValueError(
            "Skill was not found."
        ) from error

    resource_count_before = (
        count_valid_learning_resources(
            skill_id=skill.id,
        )
    )

    if (
        resource_count_before
        >= DISCOVERY_TARGET_RESOURCE_COUNT
    ):
        return (
            LearningResourceDiscoveryRunResult(
                attempted=False,
                reason=(
                    DISCOVERY_REASON_ENOUGH_RESOURCES
                ),
                status=None,
                resource_count_before=(
                    resource_count_before
                ),
                resource_count_after=(
                    resource_count_before
                ),
                requested_count=0,
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=None,
            )
        )

    eligibility = (
        get_discovery_eligibility(
            skill_id=skill.id,
            at=resolved_at,
        )
    )

    if not eligibility.eligible:
        return (
            LearningResourceDiscoveryRunResult(
                attempted=False,
                reason=(
                    DISCOVERY_REASON_COOLDOWN
                ),
                status=(
                    eligibility.latest_status
                ),
                resource_count_before=(
                    resource_count_before
                ),
                resource_count_after=(
                    resource_count_before
                ),
                requested_count=0,
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=(
                    eligibility.next_eligible_at
                ),
            )
        )

    requested_count = (
        DISCOVERY_TARGET_RESOURCE_COUNT
        - resource_count_before
    )

    request = (
        LearningResourceDiscoveryInput(
            skill_name=(
                skill.name
            ),
            skill_description=(
                skill.description
                or ""
            ),
            career_name=None,
            access_type="all",
            requested_count=(
                requested_count
            ),
            existing_urls=list(
                load_valid_learning_resource_urls(
                    skill_id=skill.id,
                )
            ),
        )
    )

    try:
        resolved_provider = (
            provider
            or OpenAIWebSearchProvider()
        )

        discovery_result = (
            resolved_provider.generate(
                prompt_package=(
                    build_learning_resource_discovery_prompt(
                        request
                    )
                ),
                output_model=(
                    LearningResourceDiscoveryResult
                ),
            )
        )

    except AIProviderError:
        attempt = (
            record_discovery_attempt(
                skill_id=skill.id,
                status=(
                    LearningResourceDiscoveryAttempt
                    .Status
                    .PROVIDER_FAILURE
                ),
                requested_count=(
                    requested_count
                ),
                candidate_count=0,
                persisted_count=0,
                at=resolved_at,
            )
        )

        return (
            LearningResourceDiscoveryRunResult(
                attempted=True,
                reason=(
                    DISCOVERY_REASON_PROVIDER_FAILURE
                ),
                status=(
                    attempt.status
                ),
                resource_count_before=(
                    resource_count_before
                ),
                resource_count_after=(
                    resource_count_before
                ),
                requested_count=(
                    requested_count
                ),
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=(
                    attempt.next_eligible_at
                ),
            )
        )

    bounded_result = (
        _bounded_discovery_result(
            discovery_result=(
                discovery_result
            ),
            requested_count=(
                requested_count
            ),
        )
    )

    candidate_count = len(
        bounded_result.candidates
    )

    persistence_result = (
        persist_source_backed_learning_resources(
            skill_id=skill.id,
            discovery_result=(
                bounded_result
            ),
            source_urls=(
                getattr(
                    resolved_provider,
                    "last_source_urls",
                    (),
                )
            ),
            requested_access_type="all",
        )
    )

    persisted_count = len(
        persistence_result.persisted
    )

    rejected_count = len(
        persistence_result.rejected
    )

    rejection_reasons = tuple(
        rejected.reason
        for rejected
        in persistence_result.rejected
    )

    resource_count_after = (
        count_valid_learning_resources(
            skill_id=skill.id,
        )
    )

    status = (
        _status_after_discovery(
            resource_count_after=(
                resource_count_after
            ),
            candidate_count=(
                candidate_count
            ),
        )
    )

    attempt = (
        record_discovery_attempt(
            skill_id=skill.id,
            status=status,
            requested_count=(
                requested_count
            ),
            candidate_count=(
                candidate_count
            ),
            persisted_count=(
                persisted_count
            ),
            at=resolved_at,
        )
    )

    return (
        LearningResourceDiscoveryRunResult(
            attempted=True,
            reason=(
                DISCOVERY_REASON_COMPLETED
            ),
            status=(
                attempt.status
            ),
            resource_count_before=(
                resource_count_before
            ),
            resource_count_after=(
                resource_count_after
            ),
            requested_count=(
                requested_count
            ),
            candidate_count=(
                candidate_count
            ),
            persisted_count=(
                persisted_count
            ),
            next_eligible_at=(
                attempt.next_eligible_at
            ),
            rejected_count=(
                rejected_count
            ),
            rejection_reasons=(
                rejection_reasons
            ),
        )
    )
