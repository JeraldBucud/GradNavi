# GradNavi Reference Data

Status: Sprint 2 working documentation for WBS 5.2 Career and Skill Reference Data

## 1. Overview

This directory documents the GradNavi Career and Skill reference-data system.

GradNavi uses a reviewed local reference dataset to support:

- Career recommendations
- Recommendation explanations
- Skill-gap analysis
- Career-readiness analysis
- Future learning recommendations

The reference-data system combines selected information from recognised occupational sources and converts the information into GradNavi's internal Career and Skill structure.

The final reviewed data is stored in PostgreSQL.

Normal student recommendation requests read the local GradNavi dataset.

External occupational services do not sit inside the normal recommendation request path.

---

## 2. WBS Alignment

Primary task:

```text
WBS 5.2
Career and Skill Reference Data
```

WBS 5.2 prepares the structured Career and Skill data required by later Sprint 2 work.

Related work includes:

```text
WBS 5.3
Weighted Recommendation Engine

WBS 5.4
Career Recommendation API

WBS 5.5
Skill Gap and Readiness Scoring Logic

WBS 5.9
Sprint 2 Integration and Testing
```

WBS 5.2 defines reference data.

WBS 5.3 defines recommendation scoring.

WBS 5.5 defines Skill-gap and readiness calculations.

---

## 3. Functional Requirement Support

The reference-data system supports these GradNavi functional requirements:

```text
FR-03
Career Recommendations

FR-04
Recommendation Explanation

FR-05
Skill-Gap Analysis

FR-06
Career-Readiness Score
```

The reference dataset provides structured Career requirements that later services compare against Student Profile information.

---

## 4. Reference Data Strategy

GradNavi follows a source-backed local dataset model.

```text
External Occupational Sources
            |
            v
      Source Download
            |
            v
          Import
            |
            v
      Normalisation
            |
            v
      Mapping Review
            |
            v
 GradNavi Reference Dataset
            |
            v
        PostgreSQL
            |
            v
 Recommendation Services
```

External source information does not automatically become approved GradNavi runtime data.

Imported mappings go through review first.

---

## 5. Initial Source Baseline

GradNavi Reference Dataset Version 1.0 uses:

```text
ABS OSCA
2024 Version 1.0

Jobs and Skills Australia
OSCA occupation information

O*NET Database
31.0

ESCO
1.2.1
```

Source responsibilities are documented in:

```text
docs/reference-data/SOURCES.md
```

---

## 6. Source Responsibilities

### ABS OSCA

Primary use:

```text
Australian Career identity
Australian occupation classification
Occupation codes
Occupation titles
Classification correspondence
```

### Jobs and Skills Australia

Primary use:

```text
Australian occupation context
Australian labour-market context
Occupation verification
```

### O*NET

Primary use:

```text
Detailed occupational Skills
Knowledge
Technology information
Importance ratings
Level ratings
Source scale information
```

### ESCO

Primary use:

```text
Skill terminology
Skill aliases
Occupation-Skill relationships
Essential relationships
Optional relationships
International mapping support
```

---

## 7. Runtime Rule

Student recommendation requests use local PostgreSQL reference data.

Runtime flow:

```text
Authenticated Student
        |
        v
Student Profile
        |
        v
GradNavi Backend
        |
        v
Local Career and Skill Data
        |
        v
Recommendation Service
```

The normal runtime flow does not require live requests to:

```text
ABS
Jobs and Skills Australia
O*NET
ESCO
```

This supports stable and repeatable recommendation inputs.

---

## 8. Dataset Version

Current working dataset:

```text
GradNavi Reference Dataset
Version 1.0
```

Current project-level status:

```text
working
```

Dataset 1.0 currently contains:

```text
Careers:
36

Canonical Skills:
2873

Career external mappings:
105

Skill aliases:
6670

Skill external mappings:
2927

CareerSkill relationships:
9959

CareerSkillEvidence records:
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

Evidence sources:

```text
O*NET:
7841

ESCO:
2197
```

Detailed version information is stored in:

```text
docs/reference-data/DATASET_VERSION.md
```

---

## 9. Repository Structure

Reference-data files use this structure:

```text
data/
└── reference/
    ├── raw/
    │   ├── osca/
    │   ├── onet/
    │   └── esco/
    │
    ├── curated/
    │
    └── mappings/

docs/
└── reference-data/
    ├── README.md
    ├── SOURCES.md
    ├── MAPPING_RULES.md
    ├── DATASET_VERSION.md
    └── ATTRIBUTION.md
```

---

## 10. Raw Data

External downloaded source files belong under:

```text
data/reference/raw/
```

Subdirectories:

```text
data/reference/raw/osca/
data/reference/raw/onet/
data/reference/raw/esco/
```

The raw directory is excluded from Git.

The root `.gitignore` contains:

```text
data/reference/raw/
```

Large external source files should not enter normal repository history.

---

## 11. Curated Data

GradNavi-reviewed project data belongs under:

```text
data/reference/curated/
```

Dataset 1.0 includes tracked curated files such as:

```text
careers.csv
canonical_skills.csv
source_skill_concepts.csv
skill_aliases.csv
onet_rating_evidence.csv
onet_software_evidence.csv
esco_skill_evidence.csv
```

Additional curated candidate and evidence files support the mapping and review process.

These files contain GradNavi-reviewed or processed project data rather than untouched external source downloads.

Curated files stay under version control when their file size is suitable for normal repository history.

---

## 12. Mapping Data

External mapping decisions belong under:

```text
data/reference/mappings/
```

Dataset 1.0 includes mapping files such as:

```text
osca_mappings.csv
onet_mappings.csv
esco_mappings.csv
skill_external_mappings.csv
skill_normalization_exact_matches.csv
skill_normalization_manual_decisions.csv
```

Supporting review and candidate files also remain in this directory.

Mapping files record how GradNavi Careers and canonical Skills connect to external occupation and Skill concepts.

Approved runtime mappings are imported into PostgreSQL through the Dataset 1.0 management command.

---

## 13. Documentation Files

### SOURCES.md

Records:

- external source organisations
- source versions
- source responsibilities
- download locations
- runtime source policy

### MAPPING_RULES.md

Records:

- Career mapping rules
- Skill mapping rules
- Skill normalisation
- mapping methods
- review statuses
- Importance normalisation
- Level normalisation
- source conflict rules
- evidence handling

### DATASET_VERSION.md

Records:

- GradNavi dataset version
- external source versions
- dataset status
- Career count
- Skill count
- CareerSkill count
- version-change rules

### ATTRIBUTION.md

Records:

- source acknowledgement
- licensing information
- modification disclosure
- source attribution
- non-endorsement wording

---

## 14. Django Domain Structure

The WBS 5.2 backend structure uses:

```text
backend/
├── profiles/
│   ├── StudentProfile
│   ├── Skill
│   └── StudentSkill
│
└── careers/
    ├── ReferenceSource
    ├── ReferenceDataset
    ├── Career
    ├── CareerExternalMapping
    ├── SkillAlias
    ├── SkillExternalMapping
    ├── CareerSkill
    └── CareerSkillEvidence
```

The existing `profiles.Skill` model remains the canonical GradNavi Skill entity.

WBS 5.2 does not create a second Skill table.

---

## 15. Canonical Skill Model

Both student and Career Skill information reference the same canonical Skill.

```text
StudentProfile
      |
      v
StudentSkill
      |
      v
    Skill
      ^
      |
 CareerSkill
      ^
      |
    Career
```

StudentSkill represents:

```text
What the student has
```

CareerSkill represents:

```text
What the Career requires
```

---

## 16. Skill Concept Types

GradNavi uses these Skill concept types:

```text
skill
knowledge
technology
```

Examples:

```text
Critical Thinking
skill
```

```text
Accounting Principles
knowledge
```

```text
Python
technology
```

The concept type does not replace more specific Skill categories.

---

## 17. Existing Sprint 1 Skills

The existing Sprint 1 Skill records are retained.

Current records include:

```text
Python
Django
React
PostgreSQL
```

These records are classified as:

```text
technology
```

WBS 5.2 extends the shared Skill structure rather than replacing the Sprint 1 data.

---

## 18. Career Mapping

GradNavi Careers keep their own database identity.

External occupation codes remain external mappings.

Example:

```text
GradNavi Career
Software Engineer
      |
      +-- OSCA mapping
      +-- O*NET mapping
      +-- ESCO mapping
      +-- international classification mapping
```

This separation protects GradNavi from changes to external classification identifiers.

---

## 19. Skill Mapping

Canonical GradNavi Skills also keep their own identity.

External Skill concepts use:

```text
SkillExternalMapping
```

Example:

```text
GradNavi Skill
Critical Thinking
      |
      +-- O*NET concept
      +-- ESCO concept
```

---

## 20. Skill Aliases

Alternative labels use:

```text
SkillAlias
```

Example:

```text
Canonical Skill:
Structured Query Language

Alias:
SQL
```

Aliases do not receive separate scoring contributions.

The canonical Skill receives the relationship.

---

## 21. CareerSkill

CareerSkill represents GradNavi's reviewed Career-to-Skill relationship.

CareerSkill stores information including:

```text
career
skill
importance_score
required_level_score
required_proficiency
requirement_type
review_status
```

One Career and one canonical Skill produce one CareerSkill record.

---

## 22. CareerSkill Evidence

CareerSkillEvidence records the external evidence supporting a CareerSkill relationship.

Evidence preserves available source information including:

```text
source dataset
external occupation identifier
external Skill identifier
source domain
source relationship
raw Importance
normalised Importance
raw Level
normalised Level
Importance scale boundaries
Level scale boundaries
Not Relevant
Recommend Suppress
source update date
```

Dataset 1.0 imports only eligible reviewed evidence.

Current evidence totals are:

```text
O*NET:
7841

ESCO:
2197

Total:
10038
```

The imported Dataset 1.0 evidence contains:

```text
Not Relevant = true:
0

Recommend Suppress = true:
0
```

O*NET evidence contains no source timestamp in the current Dataset 1.0 import.

ESCO evidence contains the required source timestamps.

---

## 23. Review Status

Reference mappings use:

```text
pending
approved
rejected
```

Only approved runtime relationships participate in normal recommendation processing.

Imported candidate records should not receive broad automatic approval.

---

## 24. Mapping Methods

GradNavi supports:

```text
exact_code
official_crosswalk
exact_title
normalized_title
manual
```

The strongest verified mapping method should receive preference.

Mapping rules are documented in:

```text
docs/reference-data/MAPPING_RULES.md
```

---

## 25. Skill Normalisation

External Skill names go through normalisation before new canonical Skills are created.

The process checks:

```text
canonical Skill name
existing aliases
external identifiers
existing external mappings
normalised labels
manual review where needed
```

Equivalent labels should map to one canonical concept.

Related but different concepts should stay separate.

---

## 26. Importance Information

GradNavi stores source-native and normalised Importance information.

Normalised internal range:

```text
0 to 100
```

Source-native values remain preserved in CareerSkillEvidence.

GradNavi does not invent missing Importance values.

---

## 27. Required Level Information

CareerSkill stores a normalised required-level score.

Internal range:

```text
0 to 100
```

Source-native Level information remains preserved in CareerSkillEvidence.

Student proficiency comparison belongs to later scoring work.

---

## 28. Requirement Type

CareerSkill uses:

```text
essential
optional
unspecified
```

Requirement type records reference information.

WBS 5.2 does not assign the final numerical scoring effect.

The numerical effect belongs to WBS 5.3.

---

## 29. Number of Skills Per Career

GradNavi does not require the same Skill count for every Career.

A Career might have:

```text
20 approved Skills
```

while another might have:

```text
40 approved Skills
```

Source relevance and review determine the final count.

WBS 5.3 must normalise scoring so CareerSkill count alone does not affect ranking.

---

## 30. Reference Data Import

GradNavi implements the Django management command:

```powershell
python backend/manage.py import_reference_dataset
```

A full validation run with rollback uses:

```powershell
python backend/manage.py import_reference_dataset --dry-run
```

The command performs these operations:

```text
validate Dataset 1.0 files
validate row totals
validate source versions
validate source checksums
validate evidence eligibility
validate approved mapping files
import ReferenceSource records
import ReferenceDataset records
import Career records
import Career external mappings
import canonical Skills
import Skill aliases
import Skill external mappings
construct CareerSkill relationships
import CareerSkillEvidence
validate final database totals
validate duplicate constraints
validate review state
```

The command runs database work inside one outer transaction.

The dry-run option executes the complete import and validation process, then rolls back all database changes.

---

## 31. Import Idempotency

The Dataset 1.0 importer is safe to run repeatedly against the same reviewed dataset.

The clean-database reconstruction test created:

```text
ReferenceSource:
4

ReferenceDataset:
3

Career:
36

CareerExternalMapping:
105

Skill:
2873

SkillAlias:
6670

SkillExternalMapping:
2927

CareerSkill:
9959

CareerSkillEvidence:
10038
```

A second import against the reconstructed database produced:

```text
created:
0

updated:
0
```

for every imported model.

The second run retained the same final database totals and passed all final validation checks.

Database uniqueness constraints provide another layer of duplicate protection.

---

## 32. Import Transactions

The Dataset 1.0 importer runs database work inside a single outer transaction.

If an import or final validation fails, the transaction does not leave a partially imported Dataset 1.0 state.

The command also supports:

```powershell
python backend/manage.py import_reference_dataset --dry-run
```

Dry-run behaviour:

```text
validate files
run the complete import
run final database validation
mark the transaction for rollback
leave the database unchanged
```

The dry-run test passed against the populated GradNavi database.

---

## 33. Import Workflow

Dataset 1.0 follows this implemented workflow:

```text
Download Source Data
        |
        v
Record Versions and Checksums
        |
        v
Prepare Curated Files
        |
        v
Prepare Mapping Files
        |
        v
Review Mapping Decisions
        |
        v
Run Dataset Validation
        |
        v
Run Dry-Run Import
        |
        v
Run Transactional Import
        |
        v
Verify PostgreSQL
        |
        v
Test Clean-Database Reconstruction
        |
        v
Run Import Again
        |
        v
Verify Idempotency
```

The clean reconstruction and repeated-import tests both passed for Dataset 1.0.

---

## 34. Initial Career Catalogue

The initial WBS 5.2 Career target is:

```text
36
```

The Careers cover several broad professional areas.

The exact Career records belong in:

```text
data/reference/curated/careers.csv
```

Each Career requires Australian occupation verification before full CareerSkill preparation.

---

## 35. Career Catalogue Review

Each initial Career should record:

```text
GradNavi Career name
Career category
Career description
active status
OSCA mapping status
review status
```

External mappings belong in mapping files rather than being embedded permanently into the Career CSV structure where separate mapping data provides better traceability.

---

## 36. Source Provenance

GradNavi preserves enough information to answer:

```text
Where did this Career requirement come from?
```

Traceability path:

```text
CareerSkill
      |
      v
CareerSkillEvidence
      |
      v
ReferenceDataset
      |
      v
ReferenceSource
```

---

## 37. WBS 5.2 Testing

Reference-data validation covers:

- Career persistence
- Career uniqueness
- Skill compatibility
- concept type validation
- preserved Sprint 1 Skill IDs
- CareerSkill uniqueness
- numerical range validation
- requirement type validation
- review status validation
- external mapping persistence
- alias persistence
- evidence persistence
- dataset relationships
- source-version validation
- checksum validation
- evidence eligibility totals
- dry-run rollback
- full transaction validation
- clean-database reconstruction
- repeated-import idempotency
- duplicate CareerSkill detection
- duplicate CareerSkillEvidence detection

The clean-database test rebuilt Dataset 1.0 from migrations plus the tracked curated and mapping files.

A second import against the rebuilt database produced no new or updated Dataset 1.0 records.

---

## 38. WBS 5.2 Completion

WBS 5.2 is complete after:

```text
reference schema complete
source baseline complete
36 Careers reviewed
canonical Skill catalogue prepared
external mappings prepared
CareerSkill relationships prepared
source evidence stored
import command working
PostgreSQL persistence verified
tests passing
attribution complete
dataset version documented
evidence recorded
```

---

## 39. WBS 5.3 Boundary

WBS 5.3 consumes WBS 5.2 reference data.

WBS 5.3 defines:

```text
recommendation factors
factor weights
Skill-match calculation
proficiency comparison
requirement-type numerical treatment
ranking
tie handling
missing-data behaviour
factor breakdown
```

WBS 5.2 does not implement these calculations.

---

## 40. Reference Data Update Workflow

Future updates follow:

```text
New Source Release
      |
      v
Download
      |
      v
Version Record
      |
      v
Import Comparison
      |
      v
Mapping Review
      |
      v
Testing
      |
      v
New GradNavi Dataset Version
```

External source updates do not silently change existing recommendation results.

---

## 41. Current Reference Data Status

```text
WBS:
5.2 Career and Skill Reference Data

GradNavi Dataset:
1.0

Dataset Status:
working

Careers:
36

Career External Mappings:
105

Canonical Skills:
2873

Skill Aliases:
6670

Skill External Mappings:
2927

CareerSkill Relationships:
9959

CareerSkillEvidence Records:
10038

Runtime Database:
PostgreSQL

External Runtime API Dependency:
None
```

Dataset 1.0 has passed file validation, transactional import validation, dry-run rollback validation, clean-database reconstruction, and repeated-import idempotency testing.

---

## 42. Related Documentation

Read these documents together:

```text
docs/system-design/career-skill-reference-data-design.md

docs/reference-data/SOURCES.md

docs/reference-data/MAPPING_RULES.md

docs/reference-data/DATASET_VERSION.md

docs/reference-data/ATTRIBUTION.md

docs/system-design/recommendation-scoring-design.md
```

---

## 43. Current Next Steps

The remaining WBS 5.2 delivery sequence is:

```text
1. Review the final management-command diff.
2. Review the updated Dataset 1.0 documentation.
3. Stage the management command and documentation.
4. Commit the completed WBS 5.2 import work.
5. Push the branch.
6. Prepare the WBS 5.2 pull request.
7. Complete team review.
8. Move to WBS 5.3 recommendation scoring work after WBS 5.2 acceptance.
```

Dataset preparation and PostgreSQL reconstruction are no longer pending activities.

---

## 44. Current Status

```text
GradNavi Reference Data Documentation:
Dataset 1.0 implementation record updated

Current Dataset:
Version 1.0 working

Career Records:
36

Canonical Skills:
2873

CareerSkill Relationships:
9959

CareerSkillEvidence Records:
10038

Import Command:
python backend/manage.py import_reference_dataset

Dry Run:
python backend/manage.py import_reference_dataset --dry-run

Clean Reconstruction:
PASSED

Repeated Import:
PASSED

Next Technical Activity:
Final WBS 5.2 review, commit, push, and pull request
```
