# GradNavi Reference Dataset Version

Status: Sprint 2 working dataset baseline for WBS 5.2 Career and Skill Reference Data

## 1. Purpose

This document records the version of the GradNavi Career and Skill reference dataset used by the project.

The dataset version identifies the exact combination of:

- External source versions
- GradNavi Career catalogue
- Canonical Skill catalogue
- External mappings
- CareerSkill mappings
- Review decisions
- Normalisation rules

This supports repeatable imports, testing, recommendation scoring, and future dataset updates.

---

## 2. Current GradNavi Dataset Version

```text
GradNavi Reference Dataset Version:
1.0
```

Dataset status:

```text
working
```

Sprint:

```text
Sprint 2
```

Primary WBS:

```text
WBS 5.2 Career and Skill Reference Data
```

Current Dataset 1.0 totals:

```text
Career Count:
36

Career External Mapping Count:
105

Canonical Skill Count:
2873

Skill Alias Count:
6670

Skill External Mapping Count:
2927

CareerSkill Count:
9959

CareerSkillEvidence Count:
10038
```

CareerSkill requirement types:

```text
essential:
1037

optional:
1160

unspecified:
7762
```

Evidence source totals:

```text
O*NET:
7841

ESCO:
2197
```

---

## 3. Dataset Version Meaning

GradNavi Dataset Version 1.0 represents the first structured Career and Skill reference-data baseline for the project.

Version 1.0 includes:

- Australian Career identity
- External occupation mappings
- Canonical Skills
- Skill aliases
- External Skill mappings
- CareerSkill relationships
- CareerSkill source evidence
- Importance information
- Required-level information
- Essential and optional relationship information
- Review statuses
- Dataset provenance

The dataset version is separate from the application version.

A software release does not automatically require a reference dataset version change.

A reference dataset update does not automatically require an application version change.

---

## 4. Source Baseline

GradNavi Dataset Version 1.0 uses the following source baseline.

| Source | Version | Responsibility |
| --- | --- | --- |
| ABS OSCA | 2024 Version 1.0 | Australian occupation identity and classification |
| Jobs and Skills Australia | OSCA occupation profiles | Australian occupation and labour-market context |
| O*NET Database | 31.0 | Detailed occupational Skill, Knowledge, technology, Importance, and Level data |
| ESCO | 1.2.1 | Supplementary Skill terminology, aliases, and occupation-Skill relationships |

Detailed source information is recorded in:

```text
docs/reference-data/SOURCES.md
```

---

## 5. Runtime Dataset Rule

GradNavi recommendation scoring uses the locally stored reviewed reference dataset.

Runtime flow:

```text
GradNavi Dataset Version
          |
          v
PostgreSQL Reference Data
          |
          +-- Career
          +-- Skill
          +-- CareerSkill
          +-- Approved mappings
          |
          v
Recommendation Engine
```

Normal student recommendation requests do not retrieve live occupation or Skill information from external providers.

---

## 6. Reproducibility Rule

A numerical recommendation result depends on:

```text
Student Profile
+
GradNavi Reference Dataset Version
+
Recommendation Scoring Configuration
```

The same approved structured inputs, dataset version, and scoring configuration should produce the same numerical result.

Reference dataset changes must therefore be versioned.

---

## 7. Dataset Version Format

GradNavi uses:

```text
MAJOR.MINOR
```

Example:

```text
1.0
1.1
1.2
2.0
```

### Major Version

Increase the major version when a dataset change significantly changes reference-data meaning or structure.

Examples:

- Large Career catalogue redesign
- Replacement of the primary occupation classification
- Major Skill taxonomy restructuring
- Breaking canonical Skill remapping
- Major source strategy change
- Significant mapping methodology change

Example:

```text
1.4 -> 2.0
```

### Minor Version

Increase the minor version for compatible reference-data improvements.

Examples:

- New Careers
- New Skills
- New aliases
- New CareerSkill relationships
- Updated approved mappings
- Updated source releases
- Corrected source mappings
- Improved evidence
- Additional reviewed source relationships

Example:

```text
1.0 -> 1.1
```

---

## 8. Initial Version

The initial Sprint 2 reference dataset is:

```text
1.0
```

Dataset 1.0 has completed the technical import and reconstruction checks for WBS 5.2.

Verified results include:

```text
36 Careers
105 Career external mappings
2873 canonical Skills
6670 Skill aliases
2927 Skill external mappings
9959 CareerSkill relationships
10038 CareerSkillEvidence records
```

The importer passed:

```text
file validation
source version validation
checksum validation
dry-run rollback
normal transactional import
final database validation
clean-database reconstruction
repeated-import idempotency
preserved Sprint 1 Skill ID validation
```

The project-level dataset status stays:

```text
working
```

until the remaining WBS 5.2 review and team acceptance are complete.

---

## 9. Dataset Status

Reference dataset status uses the following project-level values:

```text
working
review
approved
superseded
```

### working

Dataset preparation is still in progress.

### review

The dataset is ready for team review and verification.

### approved

The dataset is approved for normal recommendation scoring.

### superseded

A newer GradNavi dataset version replaced this version.

Current Dataset Version 1.0 status:

```text
working
```

---

## 10. External Dataset Status

External ReferenceDataset database records use:

```text
active
superseded
```

This differs from the GradNavi project-level dataset status.

Example:

```text
O*NET 31.0
status: active
```

A future O*NET release might result in:

```text
O*NET 31.0
status: superseded

O*NET newer reviewed version
status: active
```

A source release does not automatically become active in GradNavi.

The release first goes through import, comparison, and review.

---

## 11. Dataset Manifest

GradNavi maintains a reference dataset manifest.

Dataset Version 1.0 manifest:

```text
GradNavi Dataset Version:
1.0

Status:
working

Sprint:
Sprint 2

WBS:
5.2 Career and Skill Reference Data

Australian Classification:
ABS OSCA

OSCA Version:
2024 Version 1.0

Australian Occupation Context:
Jobs and Skills Australia

Detailed Occupational Requirements:
O*NET Database

O*NET Version:
31.0

Supplementary Skill Taxonomy:
ESCO

ESCO Version:
1.2.1

Career Count:
36

Canonical Skill Count:
2873

Career External Mappings:
105

Approved Career Mappings:
105

Pending Career Mappings:
0

Skill Alias Count:
6670

Skill External Mappings:
2927

Approved Skill Mappings:
2927

Pending Skill Mappings:
0

CareerSkill Relationships:
9959

Approved CareerSkill Relationships:
9959

Pending CareerSkill Relationships:
0

CareerSkillEvidence Records:
10038
```

---

## 12. Retrieval Dates

Each external ReferenceDataset record stores its own retrieval date.

The exact retrieval date reflects when the source file used by GradNavi was obtained.

Example:

```text
Source:
O*NET

Version:
31.0

Retrieved:
YYYY-MM-DD
```

The retrieval date must not be guessed.

The actual download date should be recorded after downloading the source dataset.

---

## 13. Checksums

Where practical, raw downloaded source files should have a checksum recorded.

Recommended algorithm:

```text
SHA-256
```

Example:

```text
Source File:
onet-source-file

SHA-256:
<recorded checksum>
```

Checksums help verify that the same source file is used during repeated imports.

Raw external files stay outside normal Git history.

---

## 14. GradNavi Curated Data

GradNavi-reviewed reference information stays under version control where file size is reasonable.

Tracked locations include:

```text
data/reference/curated/
data/reference/mappings/
```

Examples include:

```text
careers.csv
career mappings
Skill mappings
CareerSkill review data
```

Raw external source files belong under:

```text
data/reference/raw/
```

The raw directory is excluded from Git.

---

## 15. Version Change Workflow

A future dataset update follows:

```text
New Source Release
        |
        v
Download
        |
        v
Record Source Version
        |
        v
Record Checksum
        |
        v
Import Dry Run
        |
        v
Compare Existing Dataset
        |
        v
Review Changes
        |
        v
Update GradNavi Mappings
        |
        v
Run Tests
        |
        v
Assign New GradNavi Dataset Version
        |
        v
Approve
```

A new external source release does not silently replace an existing GradNavi reference dataset.

---

## 16. Mapping Changes

Changes to approved mappings should record:

- Previous mapping
- New mapping
- Source
- Source version
- Reason
- Review status
- Reviewer
- Review date
- GradNavi dataset version

Examples include:

- Career mapped to a different external occupation
- Skill merged with another canonical Skill
- Alias moved to another Skill
- CareerSkill relationship rejected
- CareerSkill relationship added
- Importance interpretation changed

---

## 17. Career Catalogue Changes

Version 1.0 targets:

```text
36 Careers
```

Future versions might expand the catalogue.

Example:

```text
Version 1.0
36 Careers

Version 1.1
Additional reviewed Careers
```

Career additions require:

1. Valid GradNavi Career record.
2. Australian occupation verification where applicable.
3. External mapping review.
4. Canonical Skill mappings.
5. CareerSkill evidence.
6. Integrity tests.

---

## 18. Skill Catalogue Changes

Dataset 1.0 contains:

```text
2873 canonical Skills
```

Concept type totals are:

```text
skill:
776

knowledge:
554

technology:
1543
```

Four Sprint 1 technology records retain their approved database identities:

```text
Python:
1

Django:
2

React:
3

PostgreSQL:
4
```

Future dataset versions are not required to keep the same total Skill count.

Future Skill catalogue changes depend on:

- source-backed concepts
- normalisation
- alias review
- duplicate resolution
- Career coverage
- approved mapping decisions

Supported GradNavi concept types are:

```text
skill
knowledge
technology
```

Changes to the concept-type model require schema and design review.

---

## 19. CareerSkill Changes

Dataset 1.0 contains:

```text
9959 CareerSkill relationships
```

Requirement type totals are:

```text
essential:
1037

optional:
1160

unspecified:
7762
```

All imported Dataset 1.0 CareerSkill records have approved review status.

Dataset 1.0 does not assign aggregate CareerSkill Importance, aggregate required Level, or required proficiency values during WBS 5.2.

Those scoring interpretations belong to later recommendation and readiness work.

A future dataset version might change CareerSkill totals because of:

- new source evidence
- source updates
- improved mapping
- duplicate resolution
- relationship rejection
- relationship approval
- new Careers
- new canonical Skills

Changes stay traceable through dataset versioning.

---

## 20. Database Source Records

GradNavi stores external source versions using:

```text
ReferenceSource
ReferenceDataset
```

Example:

```text
ReferenceSource:
O*NET

ReferenceDataset:
31.0
```

This allows CareerSkillEvidence and external mappings to reference the exact source version used.

---

## 21. Dataset Approval Checklist

Before a GradNavi reference dataset reaches approved status, verify:

- Source versions documented
- Retrieval dates recorded
- Checksums recorded where practical
- Career catalogue verified
- Career mappings reviewed
- Skill mappings reviewed
- Duplicate Skills resolved
- CareerSkill relationships reviewed
- Source evidence stored
- Importance values validated
- Required-level values validated
- Requirement types validated
- Database constraints pass
- Import process passes
- Repeated import does not duplicate data
- PostgreSQL persistence verified
- Automated tests pass
- Attribution completed
- Dataset manifest updated

---

## 22. Current Version Record

```text
GradNavi Reference Dataset

Version:
1.0

Status:
working

WBS:
5.2 Career and Skill Reference Data

Career Count:
36

Career External Mapping Count:
105

Canonical Skill Count:
2873

Skill Alias Count:
6670

Skill External Mapping Count:
2927

CareerSkill Count:
9959

CareerSkillEvidence Count:
10038

Primary Australian Classification:
OSCA 2024 Version 1.0

Detailed Occupational Requirements:
O*NET 31.0

Supplementary Skill Taxonomy:
ESCO 1.2.1

Australian Occupation Context:
Jobs and Skills Australia

Runtime Storage:
PostgreSQL

Import Command:
python backend/manage.py import_reference_dataset

Dry Run:
python backend/manage.py import_reference_dataset --dry-run

Live External API Dependency:
None for normal recommendation scoring
```

Dataset 1.0 passed clean-database reconstruction and repeated-import idempotency verification.

---

## 23. Related Documents

This document should stay aligned with:

```text
docs/reference-data/SOURCES.md
docs/reference-data/MAPPING_RULES.md
docs/reference-data/ATTRIBUTION.md
docs/reference-data/README.md
docs/system-design/career-skill-reference-data-design.md
docs/system-design/recommendation-scoring-design.md
docs/project-management/work-breakdown-structure.md
```

---

## 24. Current Status

```text
GradNavi Reference Dataset Version:
1.0

Status:
working

Current Activity:
Final WBS 5.2 documentation, commit, push, and pull-request preparation

Technical Import Validation:
PASSED

Dry-Run Rollback:
PASSED

Clean-Database Reconstruction:
PASSED

Repeated Import Idempotency:
PASSED
```

Dataset 1.0 stays in working status until WBS 5.2 review and team acceptance are complete.
