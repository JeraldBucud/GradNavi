from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(max_length=100),
                ),
                (
                    "area",
                    models.CharField(max_length=100),
                ),
                (
                    "target_type",
                    models.CharField(max_length=100),
                ),
                (
                    "target_id",
                    models.CharField(blank=True, max_length=64),
                ),
                (
                    "metadata",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name=(
                            "administration_audit_records"
                        ),
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at", "-id"),
            },
        ),
        migrations.AddIndex(
            model_name="auditrecord",
            index=models.Index(
                fields=["-created_at", "action"],
                name="admin_audit_time_action_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="auditrecord",
            index=models.Index(
                fields=["area"],
                name="admin_audit_area_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="auditrecord",
            index=models.Index(
                fields=["target_type", "target_id"],
                name="admin_audit_target_idx",
            ),
        ),
    ]
