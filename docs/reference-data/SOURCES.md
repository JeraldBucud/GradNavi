# GradNavi Reference Data Sources

Status: Sprint 2 working reference for WBS 5.2 Career and Skill Reference Data

## 1. Purpose

This document records the external occupational and Skill reference sources used to prepare the GradNavi Career and Skill reference dataset.

GradNavi uses external sources during reference-data preparation.

Runtime Career recommendation scoring uses the reviewed GradNavi reference dataset stored locally in PostgreSQL.

Normal student recommendation requests do not depend on live external occupation APIs.

---

## 2. Source Strategy

GradNavi uses different sources for different responsibilities.

| Source | Primary GradNavi Responsibility |
| --- | --- |
| ABS OSCA | Australian occupation identity and classification |
| Jobs and Skills Australia | Australian occupation and labour-market context |
| O*NET Database | Detailed occupational Skills, Knowledge, technologies, Importance, and Level information |
| ESCO | Supplementary Skill terminology, aliases, and occupation-Skill relationships |

External source records do not automatically become approved GradNavi reference records.

External records go through:

```text
Source Dataset
      |
      v
Import
      |
      v
Normalisation
      |
      v
External Mapping
      |
      v
Review
      |
      v
Approved GradNavi Reference Data
      |
      v
PostgreSQL
```

---

## 3. Australian Bureau of Statistics OSCA

### Source Name

Australian Bureau of Statistics

### Classification

OSCA, Occupation Standard Classification for Australia

### Version

2024 Version 1.0

### Release Date

6 December 2024

### Role in GradNavi

OSCA serves as the primary Australian occupation classification for GradNavi.

GradNavi uses OSCA for:

- Australian occupation codes
- Australian occupation titles
- Occupation descriptions
- Occupation hierarchy
- Skill-level classifications
- Principal titles
- Alternative titles
- Specialisations
- OSCA to ANZSCO correspondence
- OSCA to ISCO-08 correspondence

Where an appropriate OSCA occupation exists, an initial GradNavi Career should have a reviewed OSCA mapping.

### Official Classification

https://www.abs.gov.au/statistics/classifications/osca-occupation-standard-classification-australia/2024-version-1-0

### Official Data Downloads

https://www.abs.gov.au/statistics/classifications/osca-occupation-standard-classification-australia/2024-version-1-0/data-downloads

### Relevant Download Files

The OSCA download area provides:

- OSCA structure
- OSCA category descriptions
- OSCA correspondence tables
- Index of principal titles, alternative titles, and specialisations

### GradNavi Use

OSCA occupation identity receives priority when determining the Australian Career represented by a GradNavi Career record.

External occupation identifiers remain stored through GradNavi external mapping records rather than replacing GradNavi database primary keys.

---

## 4. Jobs and Skills Australia

### Source Name

Jobs and Skills Australia

### Source Type

Australian occupation and labour-market information

### Classification Direction

OSCA occupation profiles

### Role in GradNavi

Jobs and Skills Australia supplements OSCA with Australian workforce context.

Relevant information includes:

- Occupation profiles
- Employment information
- Industries
- Workforce demographics
- Occupation context
- Skills information
- Licensing information where published
- Labour-market information
- Employment projections where published

### Official Occupation Profiles

https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles

### OSCA Profile Announcement

https://www.jobsandskills.gov.au/news/explore-australias-occupations-new-osca-occupation-profiles

### OSCA Profile Launch

Jobs and Skills Australia launched its OSCA occupation profiles on 7 August 2026.

### GradNavi Use

JSA information supports Australian Career context and source verification.

Labour-market statistics do not automatically contribute to WBS 5.3 recommendation scores.

Any future numerical use of:

- employment demand
- earnings
- projected growth
- workforce shortages
- labour-market indicators

requires a separately documented scoring decision.

---

## 5. O*NET Database

### Source Name

O*NET Database

### Organisation

U.S. Department of Labor, Employment and Training Administration

### Current GradNavi Source Version

31.0

### Release

August 2026

### Production Status

O*NET Database 31.0 is the current production release selected for the initial GradNavi reference dataset.

### Role in GradNavi

O*NET provides the main detailed quantitative occupational requirement data for WBS 5.2.

Relevant information includes:

- Skills
- Knowledge
- Abilities where later approved
- Technology Skills
- Tools and technologies
- Importance ratings
- Level ratings
- Level scale anchors
- Occupation identifiers
- Occupation titles
- Scale definitions
- Content Model metadata

GradNavi does not automatically use every O*NET data domain.

Only domains approved for the GradNavi reference-data and scoring design enter the curated dataset.

### Official Database

https://www.onetcenter.org/database.html

### Database Releases

https://www.onetcenter.org/db_releases.html

### Database Licence

https://www.onetcenter.org/license_db.html

### Data Dictionary

https://www.onetcenter.org/dictionary/31.0/

### Available Formats

O*NET 31.0 provides downloadable data in formats including:

- Excel
- CSV
- JSON
- SQL
- RDF formats

GradNavi initially prefers structured downloadable files suitable for repeatable local imports.

### Relevant O*NET Data

Initial WBS 5.2 research focuses on:

- occupation identifiers
- occupation titles
- Skills
- Knowledge
- technology-related records
- Importance ratings
- Level ratings
- Scale Reference
- Level Scale Anchors

### Runtime Policy

O*NET Web Services do not sit inside normal authenticated student recommendation requests.

GradNavi imports selected O*NET information into its own reference-data system.

Recommendation scoring reads the reviewed local PostgreSQL snapshot.

### Licence

Most O*NET 31.0 Database content is distributed under Creative Commons Attribution 4.0 International, subject to the exceptions stated by O*NET.

GradNavi must record attribution and identify transformations.

Full GradNavi attribution requirements are documented in:

```text
docs/reference-data/ATTRIBUTION.md
```

---

## 6. ESCO

### Source Name

European Skills, Competences, Qualifications and Occupations

### Organisation

European Commission

### Current GradNavi Source Version

ESCO v1.2.1

### Last Update

10 December 2025

### Role in GradNavi

ESCO supplements GradNavi occupational Skill information.

Relevant ESCO information includes:

- occupations
- Skills
- competences
- Knowledge concepts
- preferred labels
- alternative labels
- occupation-Skill relationships
- essential relationships
- optional relationships
- ISCO relationships
- external concept identifiers

### Official Site

https://esco.ec.europa.eu/

### Download

https://esco.ec.europa.eu/en/use-esco/download

### Classification Information

https://esco.ec.europa.eu/en/classification

### Dataset Structure

https://esco.ec.europa.eu/en/structure-esco-downloadable-datasets

### Version Information

https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-v121

### Relevant Download Formats

ESCO provides formats including:

- CSV
- JSON-LD
- ODS
- RDF
- TTL
- XML

GradNavi initially prefers structured downloadable files suitable for local processing.

### Relevant Files

The downloadable ESCO dataset includes files covering:

- occupations
- Skills
- occupation-Skill relationships
- broader occupation relationships
- broader Skill relationships
- ISCO groups
- terminology and dictionary information
- specialised Skill collections

### GradNavi Use

ESCO primarily supports:

- Skill terminology
- alternative labels
- canonical Skill normalisation
- occupation-Skill relationship evidence
- essential versus optional relationship information
- international occupation mapping support

ESCO does not replace OSCA as GradNavi's Australian Career identity.

### Runtime Policy

Normal student recommendation requests do not depend on the hosted ESCO API.

GradNavi stores reviewed and normalised reference information locally.

---

## 7. Source Responsibility Matrix

| Information | Preferred Source |
| --- | --- |
| Australian Career identity | ABS OSCA |
| Australian occupation code | ABS OSCA |
| Australian occupation title | ABS OSCA |
| Australian classification hierarchy | ABS OSCA |
| OSCA to ISCO correspondence | ABS OSCA |
| Australian labour-market context | Jobs and Skills Australia |
| Quantitative occupational Skill data | O*NET |
| Quantitative Knowledge data | O*NET |
| Skill Importance ratings | O*NET |
| Skill Level ratings | O*NET |
| Level scale metadata | O*NET |
| Technology information | O*NET |
| Skill terminology | ESCO and O*NET |
| Skill aliases | ESCO and reviewed GradNavi mappings |
| Essential relationship evidence | ESCO where supplied |
| Optional relationship evidence | ESCO where supplied |
| Final runtime CareerSkill interpretation | GradNavi reviewed dataset |

---

## 8. Source Conflict Policy

External sources do not silently overwrite each other.

When two sources differ, GradNavi follows this process:

```text
Preserve Source A
        +
Preserve Source B
        |
        v
Compare Context
        |
        v
Review Mapping
        |
        v
Approve GradNavi Interpretation
```

GradNavi retains:

- source name
- dataset version
- external identifier
- source label
- source-native values
- mapping method
- review status

GradNavi does not silently average conflicting source values.

---

## 9. Source Version Policy

Every imported external dataset must have an associated ReferenceDataset record.

Required version information includes:

- ReferenceSource
- version
- retrieval date
- download reference
- checksum where practical
- dataset status

Example:

```text
ReferenceSource:
O*NET

ReferenceDataset:
31.0

Retrieved:
2026-08-29

Status:
active
```

A future source release does not silently replace the current GradNavi reference dataset.

The new release requires:

```text
Download
    |
    v
Import
    |
    v
Comparison
    |
    v
Review
    |
    v
New GradNavi Dataset Version
```

---

## 10. Raw Source File Policy

Downloaded external source files stay outside normal Git history.

Local source files belong under:

```text
data/reference/raw/
```

Planned local structure:

```text
data/
└── reference/
    └── raw/
        ├── osca/
        ├── onet/
        └── esco/
```

The root `.gitignore` excludes:

```text
data/reference/raw/
```

GradNavi-reviewed curated records and mappings stay under version control.

Tracked project data belongs under:

```text
data/reference/curated/
data/reference/mappings/
```

---

## 11. Source Registration in PostgreSQL

Initial ReferenceSource records are expected for:

```text
ABS OSCA
Jobs and Skills Australia
O*NET
ESCO
```

Initial ReferenceDataset records are expected for the source releases used by GradNavi.

Examples include:

```text
ABS OSCA
2024 Version 1.0
```

```text
O*NET
31.0
```

```text
ESCO
1.2.1
```

JSA source records depend on the specific downloaded or reviewed resource used by the import process.

---

## 12. Source Approval Rule

An external source record alone does not make a Career, Skill, or CareerSkill eligible for scoring.

Runtime eligibility requires GradNavi review.

Conceptual process:

```text
External Record
      |
      v
Imported Record
      |
      v
Pending
      |
      +----------------+
      |                |
      v                v
Approved            Rejected
      |
      v
Runtime Reference Data
```

Only approved mappings and CareerSkill relationships participate in normal WBS 5.3 recommendation scoring.

---

## 13. Future Sources

WBS 5.2 does not prevent future addition of other reputable occupational datasets.

Any future source requires review of:

- authority
- relevance
- data quality
- licensing
- update frequency
- identifier stability
- integration value
- mapping compatibility
- privacy implications
- scoring implications

A new source requires a ReferenceSource and ReferenceDataset record before import.

---

## 14. Current Source Baseline

The initial GradNavi WBS 5.2 source baseline is:

```text
Australian Career Classification
ABS OSCA
2024 Version 1.0

Australian Occupation Context
Jobs and Skills Australia
OSCA occupation profiles

Detailed Occupational Requirements
O*NET Database
31.0

Supplementary Skill Taxonomy
ESCO
1.2.1
```

These sources form the reference-data baseline for GradNavi Dataset Version 1.0.

---

## 15. Related GradNavi Documents

This document should stay aligned with:

```text
docs/system-design/career-skill-reference-data-design.md
docs/system-design/recommendation-scoring-design.md
docs/reference-data/MAPPING_RULES.md
docs/reference-data/DATASET_VERSION.md
docs/reference-data/ATTRIBUTION.md
docs/project-management/work-breakdown-structure.md
docs/requirements/functional-requirements.md
backend/docs/BACKEND_ARCHITECTURE.md
```

---

## 16. Source Status

Current status:

```text
WBS 5.2 Source Baseline
Defined for GradNavi Dataset Version 1.0
```

The next reference-data activity is creation of the initial dataset-version record and mapping rules.