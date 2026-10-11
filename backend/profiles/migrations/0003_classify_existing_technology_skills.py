from django.db import migrations


TECHNOLOGY_SKILLS = [
    "Python",
    "Django",
    "React",
    "PostgreSQL",
]


def classify_existing_technology_skills(apps, schema_editor):
    Skill = apps.get_model("profiles", "Skill")

    Skill.objects.filter(
        name__in=TECHNOLOGY_SKILLS,
    ).update(
        concept_type="technology",
    )


def reverse_existing_technology_skills(apps, schema_editor):
    Skill = apps.get_model("profiles", "Skill")

    Skill.objects.filter(
        name__in=TECHNOLOGY_SKILLS,
    ).update(
        concept_type="skill",
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "profiles",
            "0002_skill_concept_type_skill_valid_skill_concept_type",
        ),
    ]

    operations = [
        migrations.RunPython(
            classify_existing_technology_skills,
            reverse_existing_technology_skills,
        ),
    ]