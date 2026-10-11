SENSITIVE_METADATA_KEYS = (
    "authorization",
    "password",
    "token",
    "refresh",
    "access",
    "secret",
    "api_key",
    "apikey",
    "jwt",
    "credential",
)


AUDIT_AREAS_BY_TARGET_TYPE = {
    "Career": "careers",
    "Skill": "skills",
    "LearningResource": "learning_resources",
    "LearningResourceReport": "learning_resource_reports",
    "User": "users",
}


class UnsafeAuditMetadataError(ValueError):
    pass


def create_audit_record(
    *,
    actor,
    action,
    target,
    area=None,
    metadata=None,
):
    from .models import AuditRecord

    metadata = metadata or {}
    _validate_metadata(metadata)

    return AuditRecord.objects.create(
        actor=(
            actor
            if getattr(actor, "is_authenticated", False)
            else None
        ),
        action=action,
        area=(
            area
            or _area_for_target(target)
        ),
        target_type=target.__class__.__name__,
        target_id=str(getattr(target, "id", "")),
        metadata=metadata,
    )


def _area_for_target(target):
    return (
        AUDIT_AREAS_BY_TARGET_TYPE
        .get(
            target.__class__.__name__,
            "administration",
        )
    )


def _validate_metadata(metadata):
    for key, value in metadata.items():
        normalized_key = str(key).casefold()

        if any(
            sensitive_key in normalized_key
            for sensitive_key in SENSITIVE_METADATA_KEYS
        ):
            raise UnsafeAuditMetadataError(
                "Audit metadata contains a sensitive key."
            )

        if isinstance(value, dict):
            _validate_metadata(value)
