import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "careers",
            "0009_recommendationsnapshot",
        ),
        (
            "profiles",
            "0005_backfill_career_goal_links",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="SkillGapSummarySnapshot",
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
                    "cache_key",
                    models.CharField(
                        max_length=64,
                    ),
                ),
                (
                    "summary_version",
                    models.CharField(
                        max_length=50,
                    ),
                ),
                (
                    "model",
                    models.CharField(
                        max_length=100,
                    ),
                ),
                (
                    "payload",
                    models.JSONField(),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "generated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "career",
                    models.ForeignKey(
                        on_delete=(
                            django.db.models
                            .deletion.CASCADE
                        ),
                        related_name=(
                            "skill_gap_summary_snapshots"
                        ),
                        to="careers.career",
                    ),
                ),
                (
                    "student_profile",
                    models.ForeignKey(
                        on_delete=(
                            django.db.models
                            .deletion.CASCADE
                        ),
                        related_name=(
                            "skill_gap_summary_snapshots"
                        ),
                        to="profiles.studentprofile",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=(
                            "student_profile",
                            "career",
                        ),
                        name=(
                            "unique_skill_gap_summary_"
                            "snapshot"
                        ),
                    ),
                ],
            },
        ),
    ]
