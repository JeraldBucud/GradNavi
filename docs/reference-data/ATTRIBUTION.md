# GradNavi Reference Data Attribution

Status: Sprint 2 working attribution record for WBS 5.2 Career and Skill Reference Data

## 1. Purpose

This document records attribution, licensing, source acknowledgement, and modification disclosure requirements for external Career and Skill reference data used by GradNavi.

GradNavi uses source-backed occupational reference information from:

- Australian Bureau of Statistics
- Jobs and Skills Australia
- O*NET
- ESCO

GradNavi imports, maps, normalises, reviews, and stores selected source information in its own PostgreSQL reference dataset.

External source organisations do not endorse GradNavi unless an organisation explicitly states otherwise.

---

## 2. Attribution Principles

GradNavi follows these attribution rules:

1. Identify the external source.
2. Identify the source dataset version where available.
3. Identify the applicable licence.
4. Provide the official source reference.
5. Identify GradNavi transformations.
6. Avoid implying source endorsement.
7. Preserve source provenance in the reference-data system.
8. Record retrieval dates.
9. Record dataset versions.
10. Record source-native values where GradNavi transforms numerical data.

Attribution applies to:

- source documentation
- imported occupational records
- Career mappings
- Skill mappings
- CareerSkill evidence
- client-facing documentation where source-derived information is displayed

---

## 3. O*NET Attribution

### Source

O*NET 31.0 Database

### Organisation

U.S. Department of Labor, Employment and Training Administration

### Database Version

31.0

### Release

August 2026

### Licence

Creative Commons Attribution 4.0 International

CC BY 4.0

### Official Database

https://www.onetcenter.org/database.html

### Official Database Licence

https://www.onetcenter.org/license_db.html

### Creative Commons Licence

https://creativecommons.org/licenses/by/4.0/

---

## 4. O*NET Required Attribution

GradNavi uses modified and transformed information derived from the O*NET 31.0 Database.

The project attribution should state:

```text
This product includes information derived from the O*NET 31.0 Database
by the U.S. Department of Labor, Employment and Training Administration
(USDOL/ETA).

O*NET Database content is used under the Creative Commons Attribution
4.0 International licence.

GradNavi has modified, mapped, normalised, and supplemented portions of
the source information.

USDOL/ETA has not approved, endorsed, or tested GradNavi's modifications.
```

Where appropriate, the project should also reference:

```text
O*NET® is a trademark of the U.S. Department of Labor,
Employment and Training Administration.
```

---

## 5. O*NET Modification Disclosure

GradNavi does not present imported O*NET data as unchanged source information.

GradNavi transformations include:

- occupation mapping
- Skill mapping
- Skill normalisation
- alias creation
- source-domain mapping
- Importance normalisation
- Level normalisation
- CareerSkill review
- CareerSkill consolidation
- mapping to Australian occupations
- combining O*NET evidence with other reference sources

Where O*NET numerical values are transformed, GradNavi retains:

```text
raw source value
source scale
source scale minimum
source scale maximum
GradNavi normalized value
```

This preserves traceability between the original source rating and the GradNavi representation.

---

## 6. O*NET Endorsement Rule

GradNavi must not state or imply that:

```text
O*NET endorses GradNavi
USDOL/ETA endorses GradNavi
O*NET validated the GradNavi recommendation algorithm
USDOL/ETA validated the GradNavi recommendation algorithm
```

GradNavi's:

- mappings
- normalisation
- scoring
- Career recommendations
- Skill-gap calculations
- readiness calculations

are GradNavi project decisions unless explicitly identified as source-native information.

---

## 7. Australian Bureau of Statistics Attribution

### Source

Australian Bureau of Statistics

### Classification

OSCA, Occupation Standard Classification for Australia

### Version

2024 Version 1.0

### Official Classification

https://www.abs.gov.au/statistics/classifications/osca-occupation-standard-classification-australia/2024-version-1-0

### Official Data Downloads

https://www.abs.gov.au/statistics/classifications/osca-occupation-standard-classification-australia/2024-version-1-0/data-downloads

### ABS Copyright and Licence Information

https://www.abs.gov.au/privacy-and-legals

### General Licence

ABS website material is generally provided under:

Creative Commons Attribution 4.0 International

subject to the exclusions and conditions stated by the ABS.

---

## 8. ABS Attribution

Where GradNavi reproduces unchanged ABS information, attribution should identify the ABS as the source.

Example:

```text
Source: Australian Bureau of Statistics
```

Where GradNavi transforms, maps, derives, or combines ABS information, attribution should identify the information as based on ABS data.

Recommended project wording:

```text
Based on Australian Bureau of Statistics data from the
Occupation Standard Classification for Australia,
2024 Version 1.0.
```

GradNavi should separately identify its own:

- Career grouping
- external mappings
- Skill mappings
- transformations
- recommendation logic

---

## 9. ABS Exclusions

GradNavi must respect exclusions identified by the ABS.

Items outside general CC BY 4.0 website licensing include specified materials such as:

- Commonwealth Coat of Arms
- ABS logo
- trademark-protected material
- third-party material
- identified branding and artwork
- other excluded materials listed by the ABS

GradNavi does not need ABS logos or OSCA branding for the reference-data implementation.

GradNavi should use the occupational data and textual classification information required for the project.

---

## 10. Jobs and Skills Australia Attribution

### Source

Jobs and Skills Australia

### Official Website

https://www.jobsandskills.gov.au/

### Occupation and Industry Profiles

https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles

### Copyright and Disclaimer

https://www.jobsandskills.gov.au/copyright-and-disclaimer

### General Licence

Jobs and Skills Australia website content is generally provided under:

Creative Commons Attribution 4.0 International

subject to the exclusions stated by Jobs and Skills Australia.

---

## 11. Jobs and Skills Australia Attribution

GradNavi should identify Jobs and Skills Australia when using source-derived occupation and labour-market context.

Recommended attribution:

```text
Source: Jobs and Skills Australia,
Commonwealth of Australia.
Used under Creative Commons Attribution 4.0 International,
where applicable.
```

Where GradNavi transforms or combines JSA information, the project should identify the result as a GradNavi transformation rather than source-native JSA information.

---

## 12. Jobs and Skills Australia Exclusions

JSA identifies exclusions from its general CC BY 4.0 website licensing.

Examples include:

- Commonwealth Coat of Arms
- Jobs and Skills Australia branding
- trademark-protected material
- photographs and images
- third-party content
- material identified under another licence

GradNavi should verify the licence of any specific downloaded JSA dataset before importing or redistributing the dataset.

---

## 13. JSA Runtime Use

Jobs and Skills Australia primarily supports:

- Australian occupation context
- labour-market research
- occupation verification
- future presentation information

WBS 5.2 does not automatically convert JSA labour-market statistics into Career recommendation weights.

Any future numerical use requires a separately documented scoring decision.

---

## 14. ESCO Attribution

### Source

European Skills, Competences, Qualifications and Occupations

### Organisation

European Commission

### Version

ESCO v1.2.1

### Current Version Date

10 December 2025

### Official Website

https://esco.ec.europa.eu/

### Download

https://esco.ec.europa.eu/en/use-esco/download

### Classification Information

https://esco.ec.europa.eu/en/classification

---

## 15. ESCO Acknowledgement

For GradNavi application use, the project should acknowledge ESCO using wording based on the European Commission requirement.

Recommended GradNavi acknowledgement:

```text
This service uses the ESCO classification of the European Commission.
```

Where documentation or analysis uses ESCO information, a suitable acknowledgement is:

```text
This publication uses the ESCO classification of the European Commission.
```

---

## 16. ESCO Modification Disclosure

GradNavi modifies and adapts selected ESCO information.

Transformations include:

- occupation mapping
- Skill mapping
- canonical Skill normalisation
- alias mapping
- CareerSkill consolidation
- requirement-type mapping
- combining ESCO evidence with OSCA and O*NET information

GradNavi should clearly identify the resulting data as a modified or adapted representation.

Recommended wording:

```text
GradNavi uses selected information from the ESCO classification of the
European Commission.

GradNavi has mapped, normalized, reviewed, and supplemented portions of
the source information for the GradNavi Career and Skill reference dataset.
```

---

## 17. ESCO Source Integrity

GradNavi should preserve:

- ESCO version
- source identifier
- source label
- source relationship
- external occupation identifier
- external Skill identifier
- essential or optional relationship status where available

The original ESCO identifier remains separate from the GradNavi database primary key.

---

## 18. Cross-Source Attribution

A GradNavi CareerSkill relationship might contain evidence from multiple sources.

Example:

```text
CareerSkill:
Software Engineer -> Critical Thinking

Evidence:
O*NET rating

Evidence:
ESCO occupation-Skill relationship

Career identity:
ABS OSCA
```

GradNavi should retain attribution for each source independently.

One source should not be credited for information originating from another source.

---

## 19. Source Provenance Model

GradNavi preserves attribution through:

```text
ReferenceSource
      |
      v
ReferenceDataset
      |
      +-----------------------+
      |                       |
      v                       v
CareerExternalMapping   SkillExternalMapping
                              |
                              v
                      CareerSkillEvidence
```

This allows individual reference records to identify:

- organisation
- dataset version
- external identifier
- external label
- source-native values
- GradNavi transformations

---

## 20. ReferenceSource Records

Initial ReferenceSource records include:

```text
ABS OSCA
Jobs and Skills Australia
O*NET
ESCO
```

Each source stores available information including:

```text
name
homepage_url
licence_name
licence_url
```

---

## 21. ReferenceDataset Records

Each imported release receives its own ReferenceDataset record.

Examples:

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

ReferenceDataset also stores:

```text
retrieval date
download reference
checksum
status
```

---

## 22. Raw Source Files

Raw downloaded source datasets stay under:

```text
data/reference/raw/
```

This directory is excluded from normal Git history.

External raw files remain governed by their original source licences.

GradNavi does not change the original ownership of external source files.

---

## 23. Curated GradNavi Data

GradNavi-owned reviewed mappings and curated reference files belong under:

```text
data/reference/curated/
data/reference/mappings/
```

These files contain GradNavi decisions derived from external evidence.

Examples include:

- selected Career catalogue
- Career grouping
- Career mapping decisions
- canonical Skill naming
- Skill alias decisions
- CareerSkill review decisions
- source mapping configuration

Such files should preserve external source attribution.

---

## 24. GradNavi Transformations

GradNavi transformations include:

```text
occupation selection
occupation cross-mapping
Skill normalisation
Skill deduplication
alias creation
concept classification
CareerSkill consolidation
Importance normalisation
Level normalisation
mapping review
requirement-type interpretation
dataset integration
```

These transformations belong to GradNavi.

External source organisations do not automatically approve or validate these transformations.

---

## 25. Numerical Transformation Disclosure

Where GradNavi converts an external rating to a normalized 0 to 100 value, documentation should identify the conversion as a GradNavi transformation.

General normalization structure:

```text
normalized_value =
(raw_value - scale_minimum)
/
(scale_maximum - scale_minimum)
*
100
```

This formula is part of the GradNavi reference-data design.

The source-native numerical value remains stored separately.

---

## 26. Recommendation Algorithm Attribution

The GradNavi recommendation algorithm is separate from the external reference datasets.

External sources provide reference evidence.

GradNavi defines:

- scoring factors
- factor weights
- proficiency comparison
- Skill matching
- ranking
- tie handling
- missing-data treatment
- explanation structure

The project should not attribute GradNavi scoring rules to ABS, JSA, O*NET, or ESCO unless a specific rule directly reproduces a cited source methodology.

---

## 27. Client-Facing Attribution

Where GradNavi displays source-backed Career information to students or clients, the interface or supporting documentation should provide access to reference-data attribution.

A future client-facing attribution section might include:

```text
Career and Skill reference information in GradNavi is derived from
public occupational datasets including ABS OSCA, Jobs and Skills
Australia, the O*NET 31.0 Database, and ESCO v1.2.1.

GradNavi maps, normalizes, reviews, and combines selected source
information into its own versioned Career and Skill reference dataset.
```

Detailed licences and source references should point to this document or an equivalent public attribution page.

---

## 28. No Endorsement Statement

Recommended project statement:

```text
GradNavi is an independent software project.

Use of occupational data from ABS, Jobs and Skills Australia, O*NET,
and ESCO does not imply endorsement of GradNavi, its Career mappings,
its recommendation algorithm, or its outputs by those organisations.
```

---

## 29. Dataset Version Attribution

Attribution records should identify the exact source versions used by a GradNavi reference dataset.

For GradNavi Dataset Version 1.0:

```text
ABS OSCA:
2024 Version 1.0

O*NET:
31.0

ESCO:
1.2.1

Jobs and Skills Australia:
OSCA occupation information reviewed during Dataset Version 1.0 preparation
```

Exact retrieval dates are recorded after source files are downloaded.

---

## 30. Future Source Updates

When an external dataset version changes:

```text
New Source Version
      |
      v
Record Licence
      |
      v
Record Attribution
      |
      v
Download
      |
      v
Import
      |
      v
Review
      |
      v
New GradNavi Dataset Version
```

Previous attribution records should remain available for historical dataset versions.

---

## 31. Third-Party Material

External datasets might contain or reference third-party material.

GradNavi should not assume all content inside an external source is covered by the source's general licence.

Before redistributing a specific third-party component:

1. Identify the material.
2. Check the applicable licence.
3. Check attribution requirements.
4. Exclude the material where rights are unclear.

WBS 5.2 focuses on structured occupational data required for GradNavi.

---

## 32. Logos and Branding

GradNavi does not need external organisation logos for WBS 5.2.

The reference-data implementation should rely on textual attribution.

Use of:

- ABS logos
- Australian Government branding
- Jobs and Skills Australia logos
- O*NET branding assets
- European Commission logos

requires separate review of applicable brand and trademark conditions.

---

## 33. Attribution Storage

Reference attribution is documented in:

```text
docs/reference-data/ATTRIBUTION.md
```

Source definitions are documented in:

```text
docs/reference-data/SOURCES.md
```

Dataset versions are documented in:

```text
docs/reference-data/DATASET_VERSION.md
```

Database source records are stored through:

```text
ReferenceSource
ReferenceDataset
```

---

## 34. Attribution Review Checklist

Before WBS 5.2 completion, verify:

```text
[ ] ABS source identified
[ ] ABS OSCA version identified
[ ] ABS attribution recorded
[ ] JSA source identified
[ ] JSA attribution recorded
[ ] O*NET version identified
[ ] O*NET CC BY 4.0 attribution recorded
[ ] O*NET modification disclosure recorded
[ ] O*NET non-endorsement wording recorded
[ ] ESCO version identified
[ ] ESCO acknowledgement recorded
[ ] ESCO modification disclosure recorded
[ ] source retrieval dates recorded
[ ] source licences verified
[ ] source transformations documented
[ ] GradNavi Dataset Version updated
```

---

## 35. Current Attribution Baseline

```text
GradNavi Reference Dataset:
Version 1.0

ABS OSCA:
2024 Version 1.0

Jobs and Skills Australia:
Australian occupation context

O*NET Database:
31.0
CC BY 4.0

ESCO:
1.2.1

GradNavi Transformations:
Yes

External Source Endorsement:
No
```

---

## 36. Related Documents

This document should stay aligned with:

```text
docs/reference-data/SOURCES.md
docs/reference-data/MAPPING_RULES.md
docs/reference-data/DATASET_VERSION.md
docs/reference-data/README.md
docs/system-design/career-skill-reference-data-design.md
docs/system-design/recommendation-scoring-design.md
```

---

## 37. Current Status

```text
WBS 5.2 Attribution Framework:
Defined

Dataset:
GradNavi Reference Dataset Version 1.0

Next Activity:
Reference-data README and schema quality metadata update
```