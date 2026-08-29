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

Initial Career target:

```text
36
```

Skill count:

```text
TBD after source import and normalisation
```

CareerSkill count:

```text
TBD after source import, mapping, and review
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

The initial Sprint 2 reference dataset begins as:

```text
1.0
```

Version 1.0 stays in working status until:

1. The 36 Career records are verified.
2. External Career mappings are reviewed.
3. Canonical Skill records are prepared.
4. External Skill mappings are prepared.
5. CareerSkill relationships are prepared.
6. CareerSkill evidence is stored.
7. Import tests pass.
8. PostgreSQL verification passes.
9. Attribution is complete.
10. WBS 5.2 review is complete.

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

Initial Version 1.0 manifest:

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
Jobs and Skills Australia OSCA occupation profiles

Detailed Occupational Requirements:
O*NET Database

O*NET Version:
31.0

Supplementary Skill Taxonomy:
ESCO

ESCO Version:
1.2.1

Career Target:
36

Career Count:
TBD

Skill Count:
TBD

CareerSkill Count:
TBD

Approved Career Mappings:
TBD

Pending Career Mappings:
TBD

Approved Skill Mappings:
TBD

Pending Skill Mappings:
TBD

Approved CareerSkill Relationships:
TBD

Pending CareerSkill Relationships:
TBD
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

The Skill catalogue is not assigned a fixed total.

The final Skill count depends on:

- Source-backed Skill concepts
- Normalisation
- Alias review
- Duplicate removal
- Career coverage
- Approved concept types

Supported GradNavi concept types are:

```text
skill
knowledge
technology
```

Future changes to these types require schema and design review.

---

## 19. CareerSkill Changes

CareerSkill count is not fixed.

Different Careers might have different numbers of relevant source-backed Skills.

A future dataset version might change CareerSkill counts because of:

- New evidence
- Source updates
- Improved mapping
- Duplicate removal
- Relationship rejection
- Relationship approval
- New Careers
- New canonical Skills

Changes must stay traceable through dataset versioning.

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

Career Target:
36

Career Count:
TBD

Skill Count:
TBD

CareerSkill Count:
TBD

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

Live External API Dependency:
None for normal recommendation scoring
```

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
WBS 5.2 reference-data preparation
```

The next dataset activity is definition of the Career and Skill mapping rules.