# GradNavi Career and Skill Reference Data Design

Status: Sprint 2 working design for WBS 5.2 Career and Skill Reference Data

## 1. Purpose

This document defines the technical design for GradNavi Career and Skill reference data.

The design supports:

- WBS 5.2 Career and Skill Reference Data
- FR-03 Career Recommendations
- FR-04 Recommendation Explanation
- FR-05 Skill-Gap Analysis
- FR-06 Career-Readiness Score
- WBS 5.3 Weighted Recommendation Engine
- WBS 5.5 Skill Gap and Readiness Scoring Logic

WBS 5.2 provides structured, reviewed, source-backed Career and Skill reference data.

WBS 5.3 consumes this reference data for deterministic recommendation scoring.

WBS 5.5 consumes Career Skill requirements for skill-gap and readiness calculations.

Recommendation formulas, ranking logic, factor weights, readiness calculations, and student-to-career scoring rules stay outside WBS 5.2.

---

## 2. WBS Boundary

WBS 5.2 covers:

- Career reference structure
- Skill reference structure
- Career-to-Skill relationships
- External occupation mappings
- External Skill mappings
- Skill aliases
- Source provenance
- Dataset version tracking
- Importance data
- Skill requirement level data
- Essential and optional relationships
- Human review status
- Import and normalisation
- PostgreSQL persistence
- Reference-data integrity tests
- Reference-data documentation
- Attribution

WBS 5.2 does not implement:

- Career recommendation scoring
- Recommendation factor weights
- Student-to-Career ranking
- Recommendation API
- Skill-gap calculations
- Career-readiness calculations
- Learning suggestions
- Frontend recommendation interfaces

Those responsibilities belong to later Sprint 2 WBS tasks.

---

## 3. Design Goals

The WBS 5.2 design must provide:

1. Australian-first Career identification.
2. Source-backed occupational data.
3. Detailed occupation-to-Skill relationships.
4. Stable local runtime data.
5. Repeatable reference-data imports.
6. Deterministic scoring inputs.
7. Skill normalisation.
8. Duplicate prevention.
9. Source traceability.
10. Dataset versioning.
11. Human-reviewed external mappings.
12. Explainable CareerSkill relationships.
13. PostgreSQL persistence.
14. Future dataset expansion.
15. Future administrator maintenance.
16. Clear attribution and licensing records.

The student recommendation request path must not depend on a live third-party occupation service.

---

## 4. Reference Data Architecture

GradNavi follows a hybrid reference-data architecture.

External organisations provide source information.

GradNavi imports, normalises, reviews, versions, and stores the final runtime dataset.

```text
ABS OSCA
    |
    +--------------------+
    |                    |
    v                    v
Australian Career     ISCO-08
Identity                 |
                         |
                         v
                    Crosswalk Layer
                         |
              +----------+----------+
              |                     |
              v                     v
           O*NET                  ESCO
              |                     |
              |                     |
              +----------+----------+
                         |
                         v
              Source Data Import
                         |
                         v
                 Normalisation
                         |
                         v
                 Mapping Review
                         |
                         v
             GradNavi Reference Data
                         |
                         v
                    PostgreSQL
                         |
                         v
              WBS 5.3 Scoring Engine
```

External source data does not directly determine a student's recommendation during runtime.

GradNavi's reviewed PostgreSQL reference dataset serves as the runtime source.

---

## 5. Source Hierarchy

GradNavi uses four main reference sources.

### 5.1 ABS OSCA

Primary responsibility:

Australian occupation identity and classification.

Initial version:

OSCA 2024 Version 1.0.

Relevant OSCA information includes:

- Occupation codes
- Occupation titles
- Occupation descriptions
- Classification hierarchy
- Skill levels
- Alternative titles
- Specialisations
- OSCA to ANZSCO correspondence
- OSCA to ISCO-08 correspondence

OSCA serves as the preferred Australian Career identity where an appropriate occupation exists.

Source reference:

[S1] Australian Bureau of Statistics. OSCA, Occupation Standard Classification for Australia, 2024 Version 1.0.

[S2] Australian Bureau of Statistics. OSCA Data Downloads, 2024 Version 1.0.

---

### 5.2 Jobs and Skills Australia

Primary responsibility:

Australian occupation and labour-market context.

Relevant information includes:

- OSCA occupation profiles
- Employment context
- Industries
- Workforce characteristics
- Occupation descriptions
- Labour-market information
- Future occupation information where published

JSA information does not automatically enter GradNavi's numerical recommendation formula.

Future numerical use of labour-market information requires a separate scoring decision under the relevant WBS task.

Source reference:

[S3] Jobs and Skills Australia. Occupation and Industry Profiles.

---

### 5.3 O*NET Database

Primary responsibility:

Detailed occupational requirements and quantitative occupation data.

Initial version:

O*NET Database 31.0.

Relevant O*NET information includes:

- Essential Skills
- Transferable Skills
- Knowledge
- Software Skills
- Importance ratings
- Level ratings
- Level scale anchors
- Occupation identifiers
- Occupation titles
- Content model metadata
- Source scale definitions

GradNavi uses downloadable O*NET datasets for reference-data preparation.

Live O*NET Web Services requests do not sit inside authenticated student recommendation requests.

O*NET source-native ratings stay stored before GradNavi normalisation.

Source reference:

[S4] O*NET Resource Center. O*NET 31.0 Database.

[S5] O*NET Resource Center. O*NET 31.0 Database Content License.

[S6] O*NET Resource Center. O*NET 31.0 Scales Reference and Level Scale Anchors.

---

### 5.4 ESCO

Primary responsibility:

Supplementary Skill terminology and occupation-to-Skill relationships.

Initial version:

ESCO v1.2.1.

Relevant ESCO information includes:

- Occupations
- Skills
- Competences
- Knowledge concepts
- Preferred labels
- Alternative labels
- Essential relationships
- Optional relationships
- ISCO-08 relationships

GradNavi uses downloadable ESCO data instead of depending on live ESCO requests during recommendation scoring.

Source reference:

[S7] European Commission. ESCO v1.2.1 Classification and Download Dataset.

[S8] European Commission. ESCO Essential Relationship Definition.

[S9] European Commission. ESCO Optional Relationship Definition.

---

## 6. Runtime Rule

An authenticated recommendation request follows this path:

```text
Authenticated Student
        |
        v
Student Profile
        |
        v
GradNavi Backend
        |
        +-- StudentSkill
        +-- StudentInterest
        +-- Education
        +-- Experience
        +-- Projects
        +-- Career Goals
        |
        v
Local Career Reference Data
        |
        +-- Career
        +-- Skill
        +-- CareerSkill
        +-- Approved mappings
        |
        v
Deterministic Recommendation Service
```

The recommendation request does not contact:

- O*NET
- ESCO
- ABS
- Jobs and Skills Australia

External services and datasets belong to the reference-data preparation process.

---

## 7. Dataset Snapshot Strategy

GradNavi stores a local reviewed snapshot of external reference information.

Example:

```text
GradNavi Reference Dataset
Version: 1.0

OSCA:
2024 Version 1.0

O*NET:
31.0

ESCO:
1.2.1

Retrieved:
2026
```

The dataset snapshot provides stable scoring inputs.

A recommendation result should depend on:

```text
Student Profile
+
GradNavi Reference Dataset Version
+
Scoring Configuration Version
```

Identical inputs and versions should produce identical numerical results.

---

## 8. Initial Career Catalogue

The GradNavi V1 target is:

```text
36 Careers
```

The catalogue covers several professional areas.

Planned groups include:

1. Software and Information Technology
2. Data and Artificial Intelligence
3. Cyber Security
4. Business and Finance
5. Engineering
6. Healthcare
7. Marketing and Communications
8. Design and Creative Technology
9. People, Organisation, Operations, and Supply Chain

The exact Career titles require OSCA verification before final import.

The number 36 defines the initial Sprint 2 catalogue.

The data model does not impose a permanent 36-Career product limit.

Future administration functionality under FR-14 supports Career and Skill maintenance.

---

## 9. Career Identity

GradNavi maintains its own Career primary key.

External occupation identifiers remain mappings rather than GradNavi primary keys.

Example:

```text
GradNavi Career
    |
    +-- OSCA identifier
    |
    +-- ISCO-08 identifier
    |
    +-- O*NET identifier
    |
    +-- ESCO identifier
```

This protects GradNavi from external identifier changes.

---

## 10. Canonical Skill Model

The existing `profiles.Skill` model remains GradNavi's canonical Skill entity.

WBS 5.2 must not create a second independent Skill table.

Existing relationship:

```text
StudentProfile
      |
      v
StudentSkill
      |
      v
Skill
```

WBS 5.2 adds:

```text
Career
   |
   v
CareerSkill
   |
   v
Skill
```

Combined model:

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

StudentSkill records what the student has.

CareerSkill records what the Career requires.

Both relationships reference the same Skill concept.

---

## 11. Skill Concept Types

GradNavi uses a small internal concept classification.

Initial concept types:

```text
skill
knowledge
technology
```

Examples:

```text
Python
concept_type: technology
```

```text
Critical Thinking
concept_type: skill
```

```text
Accounting Principles
concept_type: knowledge
```

External source domains stay separately recorded.

For example:

```text
GradNavi concept_type:
skill

O*NET source_domain:
Transferable Skills
```

O*NET "Essential Skills" and ESCO "essential" do not represent the same meaning.

O*NET Essential Skills identifies an O*NET content domain.

ESCO essential identifies an occupation relationship classification.

---

## 12. Skill Normalisation

GradNavi must avoid duplicate Skill concepts caused by different terminology.

Example source labels:

```text
Data Analysis
Data Analytics
Analyse Data
Analysing Data
```

Where source review confirms equivalent meaning, GradNavi maps these labels to one canonical Skill.

Example:

```text
Skill:
Data Analysis

Aliases:
Data Analytics
Analyse Data
Analysing Data
```

StudentSkill and CareerSkill reference the canonical Skill.

Aliases do not receive separate scoring contributions.

---

## 13. SkillAlias

SkillAlias stores an alternative label for a canonical Skill.

Conceptual structure:

```text
SkillAlias

skill
alias
source
created_at
updated_at
```

SkillAlias supports:

- External terminology
- Alternative wording
- Search matching
- Duplicate detection
- Dataset normalisation
- Future student Skill search

Alias creation requires duplicate and normalisation checks.

---

## 14. SkillExternalMapping

SkillExternalMapping connects a GradNavi Skill to an external Skill concept.

Conceptual structure:

```text
SkillExternalMapping

skill
dataset
external_id
external_label
source_domain
mapping_method
review_status
confidence_score
created_at
updated_at
```

Examples:

```text
GradNavi Skill:
Critical Thinking

External source:
O*NET

External ID:
source identifier
```

or:

```text
GradNavi Skill:
Critical Thinking

External source:
ESCO

External ID:
ESCO concept identifier
```

External identifiers do not replace the GradNavi Skill primary key.

---

## 15. ReferenceSource

ReferenceSource represents an external organisation or reference system.

Conceptual structure:

```text
ReferenceSource

name
homepage_reference
licence_name
licence_reference
created_at
updated_at
```

Initial records include:

```text
ABS OSCA
Jobs and Skills Australia
O*NET
ESCO
```

---

## 16. ReferenceDataset

ReferenceDataset represents one imported source release.

Conceptual structure:

```text
ReferenceDataset

source
version
retrieved_at
download_reference
checksum
status
created_at
updated_at
```

Examples:

```text
Source:
ABS OSCA

Version:
2024 Version 1.0
```

```text
Source:
O*NET

Version:
31.0
```

```text
Source:
ESCO

Version:
1.2.1
```

Dataset versions support reproducibility.

---

## 17. Career

Career represents a GradNavi Career.

Recommended fields:

```text
Career

name
description
category
active
created_at
updated_at
```

`name`

Stores the GradNavi Career title.

`description`

Stores a reviewed Career description.

`category`

Stores the broad GradNavi Career group.

`active`

Controls whether the Career participates in normal recommendation processing.

External source codes stay outside Career in CareerExternalMapping.

---

## 18. CareerExternalMapping

CareerExternalMapping connects a GradNavi Career with an external occupation record.

Recommended fields:

```text
CareerExternalMapping

career
dataset
external_id
external_title
mapping_method
review_status
confidence_score
created_at
updated_at
```

One Career might have several mappings.

Example:

```text
Software Engineer
    |
    +-- OSCA
    +-- ISCO-08
    +-- O*NET
    +-- ESCO
```

---

## 19. Mapping Methods

Approved initial mapping methods:

```text
exact_code
official_crosswalk
exact_title
normalized_title
manual
```

### exact_code

A direct external code relationship exists.

### official_crosswalk

An official correspondence table supplies the relationship.

### exact_title

The titles match after basic text normalisation.

### normalized_title

Approved normalisation produces a title match.

### manual

A reviewer confirms the relationship after source comparison.

GradNavi does not invent a confidence percentage for manual mappings.

A numeric confidence score is stored only when an automated method produces a measured score.

---

## 20. Mapping Review Status

Approved review statuses:

```text
pending
approved
rejected
```

Imported mappings start as pending unless an approved deterministic mapping rule states otherwise.

Only approved mappings enter normal runtime scoring.

The initial 36 V1 Careers require approved Career mappings before WBS 5.3 integration testing.

---

## 21. CareerSkill

CareerSkill stores the approved GradNavi relationship between a Career and a canonical Skill.

Recommended fields:

```text
CareerSkill

career
skill
importance_score
required_level_score
required_proficiency
requirement_type
review_status
created_at
updated_at
```

The database must enforce one CareerSkill record per:

```text
career + skill
```

Duplicate Career-to-Skill relationships are invalid.

---

## 22. CareerSkill Importance

CareerSkill stores GradNavi's reviewed importance value.

Range:

```text
0 to 100
```

External source-native values remain in CareerSkillEvidence.

When an external source defines numerical scale limits, GradNavi normalises the source value using:

```text
normalized_value =
(raw_value - scale_minimum)
/
(scale_maximum - scale_minimum)
*
100
```

This preserves proportional position within the original source scale.

GradNavi must use the scale metadata supplied by the source dataset.

The importer must not assume every source uses the same minimum or maximum.

---

## 23. Career Required Level

CareerSkill stores a normalised required-level score.

Range:

```text
0 to 100
```

External raw levels remain preserved in CareerSkillEvidence.

Normalisation follows:

```text
normalized_level =
(raw_level - scale_minimum)
/
(scale_maximum - scale_minimum)
*
100
```

The source scale boundaries come from source metadata.

---

## 24. Student Proficiency Relationship

GradNavi currently stores StudentSkill proficiency as:

```text
foundational
developing
proficient
advanced
```

CareerSkill retains:

```text
required_level_score
```

and an optional reviewed:

```text
required_proficiency
```

The final conversion between student proficiency and Career required level belongs to WBS 5.3 and WBS 5.5.

WBS 5.2 preserves the detailed Career requirement.

This avoids losing source precision before the scoring rule is approved.

---

## 25. Requirement Type

CareerSkill uses:

```text
essential
optional
unspecified
```

### essential

Source evidence supports the Skill or knowledge concept as normally required for the occupation.

### optional

Source evidence supports the relationship as dependent on employer, country, or work context.

### unspecified

No reviewed essential or optional classification exists.

ESCO relationship information serves as one source for this field.

Requirement type does not receive an automatic numerical multiplier in WBS 5.2.

Its numerical treatment belongs to WBS 5.3.

---

## 26. CareerSkillEvidence

CareerSkillEvidence stores the external evidence behind a CareerSkill relationship.

Recommended fields:

```text
CareerSkillEvidence

career_skill
dataset
external_occupation_id
external_skill_id
source_domain
source_relation
raw_importance
normalized_importance
raw_level
normalized_level
scale_minimum
scale_maximum
not_relevant
source_updated_at
created_at
updated_at
```

One CareerSkill relationship might contain evidence from several sources.

Example:

```text
CareerSkill:
Software Engineer -> Critical Thinking

Evidence:
O*NET importance rating
O*NET level rating

Evidence:
ESCO essential relationship
```

GradNavi retains both evidence records.

---

## 27. Source Conflict Rule

External sources do not silently overwrite each other.

When source information differs:

1. Preserve each source record.
2. Preserve each dataset version.
3. Preserve each raw value.
4. Preserve source-specific terminology.
5. Compare occupation mapping context.
6. Review the relationship.
7. Approve the GradNavi runtime interpretation.
8. Record the review result.

GradNavi does not silently average conflicting source ratings.

---

## 28. Source Precedence

Source precedence depends on information type.

### Australian occupation identity

Primary source:

```text
ABS OSCA
```

### Australian labour-market context

Primary source:

```text
Jobs and Skills Australia
```

### Quantitative occupational Skill and knowledge ratings

Primary source:

```text
O*NET
```

### Supplementary Skill terminology and essential or optional relationships

Primary source:

```text
ESCO
```

### Runtime interpretation

Primary source:

```text
GradNavi approved reference dataset
```

---

## 29. CareerSkill Quantity

GradNavi does not impose a fixed number of Skills on every Career.

The system does not enforce:

```text
10 Skills per Career
15 Skills per Career
25 Skills per Career
35 Skills per Career
```

Source evidence and inclusion rules determine the final count.

A Career with 20 approved Skills and a Career with 45 approved Skills both remain valid.

WBS 5.3 must normalise scoring so the number of CareerSkill rows does not by itself increase or decrease a recommendation result.

---

## 30. CareerSkill Inclusion Rules

A source-backed Skill becomes a CareerSkill candidate when:

1. The Career external mapping is approved.
2. The external Skill maps to a canonical GradNavi Skill.
3. The relationship comes from an approved source domain.
4. The source does not identify the relationship as irrelevant.
5. Source evidence exists.
6. The relationship does not duplicate another canonical concept.
7. The relationship is relevant to Career recommendation or skill-gap analysis.

Candidate records stay pending until review.

Only approved CareerSkill records participate in normal recommendation scoring.

---

## 31. Skill Deduplication Rules

Before creating a new canonical Skill, the importer checks:

1. Exact canonical name.
2. Case-normalised canonical name.
3. Existing Skill aliases.
4. Existing external identifiers.
5. Approved terminology mappings.
6. Known source concept relationships.

Example:

```text
Python
python
PYTHON
```

must not produce three separate canonical Skills.

---

## 32. Data Quality Rules

The reference-data process must detect or reject:

- Duplicate Careers
- Duplicate canonical Skills
- Duplicate Skill aliases
- Duplicate CareerSkill relationships
- Duplicate external mappings
- Unsupported concept types
- Invalid importance values
- Invalid level values
- Missing source information
- Missing dataset versions
- Unknown mapping methods
- Unknown review statuses
- Broken foreign keys
- Source records marked not relevant
- Unmapped external Skills
- Ambiguous automatic occupation mappings
- Invalid source scale boundaries
- Required values outside normalized ranges

---

## 33. Proposed Django Domain Structure

```text
backend/
├── accounts/
│
├── profiles/
│   ├── StudentProfile
│   ├── Skill
│   ├── StudentSkill
│   └── other student profile models
│
├── careers/
│   ├── ReferenceSource
│   ├── ReferenceDataset
│   ├── Career
│   ├── CareerExternalMapping
│   ├── SkillAlias
│   ├── SkillExternalMapping
│   ├── CareerSkill
│   └── CareerSkillEvidence
│
└── recommendations/
    └── WBS 5.3 recommendation logic
```

The existing `profiles.Skill` table stays in place.

Moving Skill into another Django application would create unnecessary Sprint 1 schema disruption.

---

## 34. Skill Model Extension

The current Skill model contains:

```text
name
category
description
created_at
updated_at
```

WBS 5.2 should extend the existing Skill model where required.

Recommended addition:

```text
concept_type
```

Initial choices:

```text
skill
knowledge
technology
```

The existing `name` field remains the canonical GradNavi Skill name.

The existing `category` field stays available for more specific grouping.

Example:

```text
name:
Python

concept_type:
technology

category:
Programming
```

Example:

```text
name:
Critical Thinking

concept_type:
skill

category:
Transferable
```

---

## 35. Import Architecture

Reference data must enter GradNavi through a repeatable import process.

Manual PostgreSQL entry is not the primary loading method.

Recommended management command:

```powershell
python backend/manage.py import_reference_data
```

Recommended optional parameters:

```powershell
python backend/manage.py import_reference_data --dry-run
```

```powershell
python backend/manage.py import_reference_data --dataset-version 1.0
```

The import process should perform:

```text
1. Read source manifest.
2. Validate source versions.
3. Validate source checksums where configured.
4. Load curated Career mapping configuration.
5. Load external occupation records.
6. Load external Skill records.
7. Normalise Skill labels.
8. Match existing canonical Skills.
9. Create approved new canonical Skills.
10. Create external Skill mappings.
11. Import CareerSkill source evidence.
12. Apply source scale normalisation.
13. Detect duplicates.
14. Apply mapping methods.
15. Apply review statuses.
16. Persist approved reference records.
17. Produce an import summary.
```

---

## 36. Import Safety

The importer must be idempotent.

Running the same approved dataset twice must not create duplicate records.

The importer should use:

- Stable external identifiers
- Database uniqueness constraints
- `get_or_create` or equivalent controlled operations
- Transactions
- Validation
- Dry-run support
- Import summaries

A failed import should not leave a partially inconsistent reference dataset where transaction boundaries prevent partial persistence.

---

## 37. Raw Data Storage

Large external source datasets should stay outside normal Git history.

Recommended local structure:

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
```

`data/reference/raw/` should be excluded from Git if the downloaded source files are large.

The project repository should track:

```text
data/reference/curated/
data/reference/mappings/
```

when those files contain GradNavi-owned reviewed data of reasonable size.

---

## 38. Repository Documentation

Recommended structure:

```text
docs/
└── reference-data/
    ├── README.md
    ├── SOURCES.md
    ├── MAPPING_RULES.md
    ├── DATASET_VERSION.md
    └── ATTRIBUTION.md
```

### README.md

Explains the GradNavi reference-data system.

### SOURCES.md

Records external sources and versions.

### MAPPING_RULES.md

Documents mapping and normalisation rules.

### DATASET_VERSION.md

Records the active GradNavi reference dataset version.

### ATTRIBUTION.md

Records attribution and licence information.

---

## 39. Dataset Manifest

GradNavi should maintain a dataset manifest.

Example structure:

```text
GradNavi Dataset Version:
1.0

Sources:

OSCA
Version: 2024 Version 1.0

O*NET
Version: 31.0

ESCO
Version: 1.2.1

Career Count:
36

Skill Count:
determined after import

CareerSkill Count:
determined after review
```

The manifest serves as reference for testing and reproducibility.

---

## 40. Attribution Requirements

GradNavi must record external source attribution.

### O*NET

O*NET 31.0 Database content is generally distributed under CC BY 4.0, subject to the exceptions stated by O*NET.

GradNavi attribution must:

- Credit the O*NET 31.0 Database
- Credit the U.S. Department of Labor, Employment and Training Administration
- State the CC BY 4.0 licence
- Identify GradNavi transformations
- Avoid implying O*NET endorsement of GradNavi modifications

### ABS OSCA

GradNavi records:

- ABS as source
- OSCA version
- Retrieval date
- Data transformations

### Jobs and Skills Australia

GradNavi records:

- Jobs and Skills Australia as source
- Dataset or profile source
- Retrieval date
- GradNavi transformations

### ESCO

GradNavi records:

- European Commission ESCO as source
- ESCO version
- Retrieval date
- GradNavi transformations

Full attribution details belong in:

```text
docs/reference-data/ATTRIBUTION.md
```

---

## 41. Review Workflow

Reference-data review follows:

```text
Imported
   |
   v
Pending Mapping
   |
   +----------------+
   |                |
   v                v
Approved         Rejected
   |
   v
Eligible for Runtime Scoring
```

Review should verify:

- Correct occupation identity
- Correct Skill identity
- Correct source mapping
- Duplicate status
- Importance data
- Required-level data
- Requirement type
- External evidence

---

## 42. WBS 5.2 Testing

WBS 5.2 requires focused automated tests.

### Career Tests

Test:

- Career creation
- Career uniqueness
- Career persistence
- Career active status

### Reference Source Tests

Test:

- ReferenceSource creation
- ReferenceDataset creation
- Dataset-to-source relationship
- Dataset version persistence

### Career Mapping Tests

Test:

- CareerExternalMapping creation
- Valid mapping method
- Valid review status
- Duplicate external mapping protection

### Skill Tests

Test:

- Canonical Skill creation
- Valid concept type
- Existing Sprint 1 Skill compatibility

### SkillAlias Tests

Test:

- Alias persistence
- Duplicate protection
- Correct canonical Skill relationship

### SkillExternalMapping Tests

Test:

- Mapping persistence
- Dataset relationship
- External identifier persistence
- Review status

### CareerSkill Tests

Test:

- CareerSkill creation
- CareerSkill uniqueness
- Importance score boundaries
- Required-level score boundaries
- Requirement type validation
- Review status validation
- Career relationship
- Skill relationship

### CareerSkillEvidence Tests

Test:

- Evidence creation
- Dataset relationship
- Raw importance persistence
- Raw level persistence
- Normalized value persistence
- External identifiers
- Source relation

### Import Tests

Test:

- Successful reference-data import
- Dry-run behaviour
- Repeated import idempotency
- Duplicate prevention
- Invalid source version handling
- Invalid mapping handling
- Approved record persistence
- Pending record handling
- Import summary output

---

## 43. PostgreSQL Verification

Final WBS 5.2 verification should record:

```text
ReferenceSource count
ReferenceDataset count
Career count
Skill count
SkillAlias count
CareerExternalMapping count
SkillExternalMapping count
CareerSkill count
CareerSkillEvidence count
Approved mapping count
Pending mapping count
Rejected mapping count
```

The final evidence should also record:

```text
OSCA version
O*NET version
ESCO version
GradNavi dataset version
Import result
Database migration result
Automated test result
```

---

## 44. WBS 5.2 Acceptance Criteria

WBS 5.2 is complete when all required Sprint 2 reference-data work passes review.

Completion criteria:

1. The final Career reference schema exists.
2. The existing Skill schema supports canonical concepts.
3. ReferenceSource exists.
4. ReferenceDataset exists.
5. CareerExternalMapping exists.
6. SkillAlias exists.
7. SkillExternalMapping exists.
8. CareerSkill exists.
9. CareerSkillEvidence exists.
10. The initial 36 Careers have reviewed Australian occupation identities.
11. Canonical Skill records exist.
12. External Skill mappings exist where required.
13. Career-to-Skill relationships exist.
14. Source evidence exists for imported CareerSkill relationships.
15. Importance information is retained where supported.
16. Required-level information is retained where supported.
17. Essential or optional information is retained where supported.
18. Mapping review statuses exist.
19. Only approved mappings enter runtime scoring.
20. Dataset versions are recorded.
21. The reference-data import is repeatable.
22. Repeated imports do not create duplicates.
23. PostgreSQL persistence is verified.
24. Model integrity tests pass.
25. Import tests pass.
26. Source attribution is documented.
27. Dataset version information is documented.
28. WBS 5.2 evidence is recorded.
29. WBS 5.3 receives stable structured reference data.

---

## 45. Deferred to WBS 5.3

WBS 5.3 defines recommendation scoring.

WBS 5.2 does not lock:

- Final recommendation factors
- Final factor weights
- Skill-match formula
- Student proficiency conversion
- CareerSkill importance weighting
- Essential versus optional numerical effect
- Missing Skill treatment
- Missing profile-data treatment
- Interest comparison
- Education comparison
- Experience comparison
- Project comparison
- Career-goal comparison
- Personality inclusion
- Final recommendation score
- Career ranking
- Tie handling
- Factor breakdown
- Explanation inputs

WBS 5.3 must consume WBS 5.2 models rather than create a competing Career or Skill structure.

---

## 46. Deferred to WBS 5.5

WBS 5.5 defines Skill Gap and Readiness Scoring Logic.

WBS 5.5 includes:

- Student current-level conversion
- Career required-level comparison
- Missing Skill gap treatment
- Skill-gap severity
- Readiness contribution
- Overall readiness formula
- Readiness score
- Skill-gap explanations

WBS 5.2 supplies the source-backed Career requirement information.

---

## 47. Future Administration

FR-14 later supports administrator management of:

- Careers
- Skills
- Users
- Learning resources

WBS 5.2 does not build the administrator interface.

The WBS 5.2 data model should support future controlled Career and Skill maintenance without replacing the source evidence model.

---

## 48. Data Governance

Reference-data changes should record:

```text
Changed record
Previous value
New value
Reason
Source
Dataset version
Reviewer
Review date
```

Source evidence should stay historically traceable after an approved CareerSkill interpretation changes.

---

## 49. Security and Privacy

Career and Skill reference data does not store student-owned private information.

Reference-data import processing remains separate from Student Profile processing.

Student Profile ownership remains protected through the existing authentication and authorization controls.

External occupational source data must not receive Student Profile information.

---

## 50. Performance Design

Runtime reference data stays in PostgreSQL.

Recommendation requests should query local Career and Skill information.

External API latency does not affect normal recommendation requests.

Database indexing should follow measured WBS 5.3 query patterns.

Index decisions should be based on actual query requirements rather than speculative optimization.

---

## 51. Current Implementation Impact

The first WBS 5.2 implementation created a simple structure:

```text
Career
CareerSkill
```

with CareerSkill containing:

```text
career
skill
required_proficiency
```

The researched design requires richer source, mapping, evidence, importance, and level information.

The current Career migration has not entered Git history.

The current local Career migration should therefore be rolled back before the final WBS 5.2 schema replaces the temporary design.

The existing `profiles.Skill` model should stay in place and receive only the required WBS 5.2 extension.

---

## 52. Revised Implementation Order

Implementation should proceed in this order:

```text
1. Save and review this WBS 5.2 design.
2. Roll back the temporary careers migration.
3. Remove the temporary careers migration file.
4. Revise Career.
5. Extend the existing Skill model.
6. Add ReferenceSource.
7. Add ReferenceDataset.
8. Add CareerExternalMapping.
9. Add SkillAlias.
10. Add SkillExternalMapping.
11. Revise CareerSkill.
12. Add CareerSkillEvidence.
13. Add model constraints.
14. Run Django system checks.
15. Preview migrations.
16. Generate clean migrations.
17. Inspect generated migrations.
18. Apply migrations.
19. Add model integrity tests.
20. Add reference-data documentation structure.
21. Prepare source dataset manifest.
22. Download OSCA source files.
23. Download O*NET 31.0 source files.
24. Download ESCO 1.2.1 source files.
25. Verify the final 36 OSCA Career identities.
26. Prepare external Career mappings.
27. Prepare canonical Skill mappings.
28. Prepare CareerSkill review mappings.
29. Implement the Django import command.
30. Run import dry-run.
31. Review import summary.
32. Run the approved import.
33. Verify PostgreSQL records.
34. Run WBS 5.2 tests.
35. Record WBS 5.2 evidence.
36. Review Git changes.
37. Commit WBS 5.2.
38. Push the branch.
39. Open a PR into feature/sprint-2.
```

---

## 53. Source Research References

### [S1]

Australian Bureau of Statistics.

OSCA, Occupation Standard Classification for Australia.

Reference period: 2024, Version 1.0.

### [S2]

Australian Bureau of Statistics.

OSCA Data Downloads.

Includes OSCA structure, category descriptions, correspondence tables to ANZSCO and ISCO-08, and occupation-title indexes.

Reference period: 2024, Version 1.0.

### [S3]

Jobs and Skills Australia.

Occupation and Industry Profiles.

JSA has commenced its transition to OSCA-based occupation profiles.

### [S4]

O*NET Resource Center.

O*NET Database 31.0.

Current production release used by this design.

Relevant downloadable domains include Essential Skills, Transferable Skills, Software Skills, Knowledge, scales, and Level Scale Anchors.

### [S5]

O*NET Resource Center.

O*NET Database 31.0 Content License.

Most O*NET 31.0 Database content is distributed under Creative Commons Attribution 4.0, subject to stated exceptions.

### [S6]

O*NET Resource Center.

O*NET Database 31.0 Scales Reference and Level Scale Anchors.

These records define source rating scales and Level anchors used during GradNavi normalisation.

### [S7]

European Commission.

ESCO v1.2.1.

Current classification version used by this design.

### [S8]

European Commission ESCO.

Essential relationship definition.

Essential relationships identify knowledge, Skills, and competences usually required for an occupation independent of employer or work context.

### [S9]

European Commission ESCO.

Optional relationship definition.

Optional relationships identify knowledge, Skills, and competences associated with an occupation depending on employer, country, or work context.

---

## 54. Internal GradNavi References

This design must stay aligned with:

```text
docs/project-management/work-breakdown-structure.md
docs/requirements/functional-requirements.md
docs/requirements/requirements-assignment-matrix.md
docs/system-design/recommendation-scoring-design.md
backend/docs/BACKEND_ARCHITECTURE.md
backend/profiles/models.py
```

---

## 55. Design Decisions

The following WBS 5.2 decisions are approved for implementation:

```text
Australia-first Career identity:
YES

Primary Australian occupation source:
ABS OSCA

Australian labour-market context:
Jobs and Skills Australia

Primary detailed occupational requirements source:
O*NET 31.0 downloadable database

Supplementary Skill taxonomy:
ESCO 1.2.1

Paid external APIs:
NO

Live external API requests during student recommendations:
NO

Local PostgreSQL reference dataset:
YES

Versioned source datasets:
YES

Source provenance:
YES

Canonical GradNavi Skills:
YES

Skill aliases:
YES

External Skill mappings:
YES

External Career mappings:
YES

CareerSkill source evidence:
YES

Importance information:
YES

Required-level information:
YES

Essential and optional relationships:
YES

Human mapping review:
YES

Repeatable import:
YES

Initial Career target:
36

Fixed Skills-per-Career limit:
NO
```

---

## 56. Design Status

Current status:

```text
Sprint 2 Working Design
WBS 5.2 Career and Skill Reference Data
Approved for implementation
```

The next implementation activity is the WBS 5.2 schema redesign.

The temporary Career migration must be rolled back before the final model migration is generated.