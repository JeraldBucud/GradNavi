# WBS 5.7 Learning Resource Reference Data

This directory contains the controlled learning-resource dataset for WBS 5.7.

`learning_resources.csv` defines curated resources. `resource_key` is a stable file-local identifier used to join rows to skill mappings. It is not a database ID.

`learning_resource_skills.csv` maps each `resource_key` to a Dataset 1.0 `canonical_skill_key` from `data/reference/curated/canonical_skills.csv`.

Numeric database `Skill` IDs must not be used in the learning-resource CSV files. The importer resolves:

```text
canonical_skill_key -> canonical_skills.csv row -> canonical skill name -> profiles.Skill
```

The initial dataset is deliberately small. It covers only canonical skills with clear, official public learning resources.

Run the importer from `backend/`:

```powershell
python manage.py import_learning_resources
```

Run validation and import logic without persisting changes:

```powershell
python manage.py import_learning_resources --dry-run
```
