from django.db import migrations


def forwards(apps, schema_editor):
    CareerGoal = apps.get_model(
        "profiles",
        "CareerGoal",
    )

    Career = apps.get_model(
        "careers",
        "Career",
    )

    profile_ids = (
        CareerGoal.objects
        .order_by()
        .values_list(
            "student_profile_id",
            flat=True,
        )
        .distinct()
    )

    for profile_id in profile_ids:
        goals = (
            CareerGoal.objects
            .filter(
                student_profile_id=profile_id
            )
            .order_by(
                "id"
            )
        )

        primary_assigned = False

        for goal in goals:
            updates = {}

            target_role = (
                goal.target_role
                or ""
            ).strip()

            if target_role:
                career = (
                    Career.objects
                    .filter(
                        name__iexact=target_role
                    )
                    .order_by(
                        "id"
                    )
                    .first()
                )

                if career is not None:
                    updates[
                        "career_id"
                    ] = career.id

            if not primary_assigned:
                updates[
                    "is_primary"
                ] = True

                primary_assigned = True

            if updates:
                (
                    CareerGoal.objects
                    .filter(
                        pk=goal.pk
                    )
                    .update(
                        **updates
                    )
                )


def backwards(apps, schema_editor):
    CareerGoal = apps.get_model(
        "profiles",
        "CareerGoal",
    )

    CareerGoal.objects.update(
        career_id=None,
        is_primary=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "profiles",
            "0004_careergoal_career_careergoal_is_primary_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            forwards,
            backwards,
        ),
    ]
