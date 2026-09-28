from django.conf import settings
from django.db import models


class AuditRecord(models.Model):
    """
    Minimal administrative audit record for security-relevant
    WBS 7.8 actions.

    Metadata must contain only small, sanitised operational values.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="administration_audit_records",
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)
    target_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(
                fields=("-created_at", "action"),
                name="admin_audit_time_action_idx",
            ),
            models.Index(
                fields=("area",),
                name="admin_audit_area_idx",
            ),
            models.Index(
                fields=("target_type", "target_id"),
                name="admin_audit_target_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.action} on {self.target_type} "
            f"{self.target_id}"
        )
