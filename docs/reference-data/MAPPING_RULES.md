# GradNavi Reference Data Mapping Rules

Status: Sprint 2 working mapping specification for WBS 5.2 Career and Skill Reference Data

## 1. Purpose

This document defines how GradNavi maps, normalises, reviews, and stores external Career and Skill reference information.

The mapping process covers:

- ABS OSCA occupations
- Jobs and Skills Australia occupation information
- O*NET occupations
- O*NET Skills
- O*NET Knowledge
- O*NET technologies
- ESCO occupations
- ESCO Skills
- ESCO Knowledge
- Career-to-Skill relationships
- Skill aliases
- source ratings
- review decisions

The goal is a stable GradNavi reference dataset suitable for deterministic Career recommendation, Skill-gap analysis, and readiness calculations.

---

## 2. Core Mapping Principle

External records do not automatically become GradNavi runtime records.

Every external record follows this general process:

```text
External Source Record
        |
        v
Source Validation
        |
        v
Normalisation
        |
        v
Candidate Mapping
        |
        v
Duplicate Detection
        |
        v
Review
        |
        +------------------+
        |                  |
        v                  v
     Approved           Rejected
        |
        v
GradNavi Reference Data
```

Only approved relationships participate in normal runtime recommendation scoring.

---

## 3. Source Responsibilities

GradNavi assigns different responsibilities to each source.

| Information | Preferred Source |
| --- | --- |
| Australian occupation identity | ABS OSCA |
| Australian occupation code | ABS OSCA |
| Australian occupation hierarchy | ABS OSCA |
| OSCA to ISCO-08 correspondence | ABS OSCA |
| Australian occupation context | Jobs and Skills Australia |
| Occupational Skill ratings | O*NET |
| Occupational Knowledge ratings | O*NET |
| Importance ratings | O*NET |
| Level ratings | O*NET |
| Technology records | O*NET |
| Skill terminology | O*NET and ESCO |
| Skill aliases | ESCO and reviewed GradNavi mappings |
| Essential relationship evidence | ESCO |
| Optional relationship evidence | ESCO |
| Final runtime interpretation | GradNavi approved reference dataset |

---

## 4. Career Identity Rule

GradNavi maintains its own Career identity.

External occupation identifiers do not become GradNavi database primary keys.

Example:

```text
GradNavi Career
Software Engineer

External mappings
OSCA occupation
O*NET occupation
ESCO occupation
ISCO-08 group
```

This separation protects GradNavi from future changes to an external classification.

---

## 5. Australian Career Mapping

The preferred Career mapping sequence is:

```text
GradNavi Career
      |
      v
OSCA Occupation
      |
      v
OSCA Correspondence
      |
      v
International Mapping Candidates
```

The initial 36 GradNavi Careers require Australian occupation verification.

Where an exact OSCA occupation exists, GradNavi uses the OSCA occupation as the primary Australian mapping.

---

## 6. OSCA Mapping Rules

OSCA mapping uses the following priority:

```text
1. Exact occupation code
2. Official correspondence
3. Exact principal title
4. Exact alternative title
5. Exact specialisation
6. Normalised title candidate
7. Manual review
```

An automatic mapping should not skip a stronger available mapping method.

Example:

```text
OSCA exact code available
```

Preferred mapping method:

```text
exact_code
```

A title match should not replace an exact code relationship.

---

## 7. OSCA Correspondence

ABS correspondence tables provide official relationships between OSCA and other classification systems, including ISCO-08.

GradNavi records an official correspondence as:

```text
mapping_method:
official_crosswalk
```

Official correspondence receives preference over title-based matching.

One OSCA occupation might correspond to multiple external classifications or categories.

Such mappings require review before GradNavi uses a single external occupation as the detailed Skill source.

---

## 8. Jobs and Skills Australia Mapping

Jobs and Skills Australia supports Australian Career context.

JSA does not replace OSCA as the primary occupation identity.

JSA information should be associated with the verified Australian occupation represented by the Career.

Examples include:

- occupation profile
- employment information
- industry context
- workforce characteristics
- Australian labour-market context

JSA numerical labour-market values do not enter recommendation scoring under WBS 5.2.

---

## 9. O*NET Occupation Mapping

O*NET uses O*NET-SOC occupation identifiers.

A GradNavi Career requires a reviewed O*NET occupation mapping before O*NET occupational Skill ratings become CareerSkill evidence.

Preferred mapping sequence:

```text
Official crosswalk where available
        |
        v
Reviewed classification relationship
        |
        v
Exact occupation title
        |
        v
Normalised occupation title
        |
        v
Manual review
```

A similar occupation title alone is not sufficient for automatic approval when occupational scope differs.

---

## 10. ESCO Occupation Mapping

ESCO occupation mappings support:

- Skill terminology
- occupation-Skill relationships
- essential relationships
- optional relationships
- ISCO relationships

ESCO does not replace OSCA as GradNavi's primary Australian Career identity.

Preferred mapping sequence:

```text
Official classification relationship
        |
        v
ISCO relationship
        |
        v
Exact title
        |
        v
Normalised title
        |
        v
Manual review
```

---

## 11. Mapping Methods

GradNavi uses these mapping methods:

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

An official source correspondence supplies the mapping.

### exact_title

External and GradNavi labels match after safe text normalisation.

### normalized_title

A stronger text-normalisation process identifies a candidate.

### manual

A reviewer explicitly approves the mapping after source comparison.

---

## 12. Mapping Method Priority

Preferred mapping strength:

```text
exact_code
     |
     v
official_crosswalk
     |
     v
exact_title
     |
     v
normalized_title
     |
     v
manual review
```

Manual review remains required when source scope is unclear.

A lower-strength mapping should not replace a higher-strength verified mapping without a documented reason.

---

## 13. Mapping Confidence

GradNavi does not assign invented confidence percentages.

`confidence_score` stays null unless an automated matching process produces a measured numerical confidence value.

Examples:

```text
Manual mapping
confidence_score = null
```

```text
Official crosswalk
confidence_score = null
```

A future similarity algorithm might produce:

```text
confidence_score = measured result
```

Such a score must have a documented formula before use.

Confidence does not replace review status.

---

## 14. Review Status

GradNavi uses:

```text
pending
approved
rejected
```

### pending

The mapping exists but has not passed final review.

### approved

The mapping passed review and is eligible for normal runtime use.

### rejected

The mapping was reviewed and found unsuitable.

Only approved Career mappings and CareerSkill relationships enter normal WBS 5.3 scoring.

---

## 15. Canonical Skill Principle

GradNavi stores one canonical Skill for one approved concept.

Example:

```text
Canonical Skill:
Data Analysis
```

Possible external labels:

```text
Data Analytics
Analyse Data
Analysing Data
```

Equivalent source labels become aliases or external mappings.

They do not automatically become separate canonical Skills.

---

## 16. Skill Normalisation Pipeline

External Skill text follows:

```text
Original Label
      |
      v
Unicode Normalisation
      |
      v
Whitespace Normalisation
      |
      v
Case Comparison
      |
      v
Existing Canonical Name Check
      |
      v
Existing Alias Check
      |
      v
External ID Check
      |
      v
Candidate Match
      |
      v
Review
```

The original external label stays preserved in the external mapping.

---

## 17. Safe Text Normalisation

Safe normalisation includes:

- trim leading whitespace
- trim trailing whitespace
- collapse repeated internal whitespace
- Unicode normalisation
- case-insensitive comparison for matching
- preserve the source label separately

Safe normalisation does not automatically remove meaningful technical symbols.

Examples requiring caution:

```text
C
C++
C#
.NET
Node.js
CI/CD
```

Removing punctuation blindly would corrupt distinct technology concepts.

---

## 18. Canonical Skill Naming

Canonical Skill names should:

- use clear professional terminology
- avoid unnecessary source-specific wording
- represent one concept
- avoid duplicate synonyms
- preserve recognised technology names
- remain understandable to students

Example:

```text
Python
```

not:

```text
Python Programming Language Technology Skill
```

Example:

```text
Critical Thinking
```

not:

```text
Ability to Think Critically
```

when both sources refer to the same reviewed concept.

---

## 19. Skill Concept Types

GradNavi uses:

```text
skill
knowledge
technology
```

### skill

A learned capability applied to work.

Examples:

```text
Critical Thinking
Problem Solving
Data Analysis
Technical Writing
```

### knowledge

A body of subject-matter understanding.

Examples:

```text
Accounting Principles
Cyber Security Principles
Anatomy
Marketing Principles
```

### technology

A named technology, software platform, language, framework, database, or technical product.

Examples:

```text
Python
React
PostgreSQL
Microsoft Excel
```

---

## 20. Source Domain

GradNavi concept type and external source domain stay separate.

Example:

```text
GradNavi concept_type:
skill

O*NET source_domain:
Transferable Skills
```

Another example:

```text
GradNavi concept_type:
skill

O*NET source_domain:
Essential Skills
```

O*NET Essential Skills describes an O*NET domain.

It does not mean the same thing as ESCO essential occupation-Skill relationships.

---

## 21. Skill Alias Rules

An alias is created when review confirms an alternative label represents the same canonical concept.

An alias must not represent:

- a broader concept
- a narrower concept
- a related but separate Skill
- another technology
- a different professional competency

Example:

```text
Canonical Skill:
Structured Query Language

Alias:
SQL
```

Appropriate after review.

Example:

```text
Canonical Skill:
Database Management

Alias:
SQL
```

Not automatically appropriate because Database Management and SQL represent different concepts.

---

## 22. External Skill Mapping

External Skill records remain linked to their source identifier.

Each mapping records:

```text
GradNavi Skill
ReferenceDataset
External ID
External Label
Source Domain
Mapping Method
Review Status
Confidence Score where applicable
```

External identifiers provide stronger duplicate detection than text labels alone.

---

## 23. Duplicate Detection

Before creating a new canonical Skill, check:

```text
1. Exact canonical name
2. Case-insensitive canonical name
3. Existing aliases
4. External source identifier
5. Existing external mapping
6. Normalised label
7. Manual review where ambiguous
```

A new Skill record should be created only when no approved existing canonical concept represents the external concept.

---

## 24. CareerSkill Candidate Creation

A CareerSkill candidate requires:

1. Approved Career mapping.
2. Approved canonical Skill mapping.
3. Source-backed Career-to-Skill evidence.
4. No duplicate CareerSkill relationship.
5. Valid source metadata.
6. Valid dataset version.
7. Relationship relevance.
8. Review status.

Candidate relationships start as:

```text
pending
```

unless an approved deterministic import rule explicitly assigns another status.

---

## 25. CareerSkill Uniqueness

One Career and one canonical Skill produce one GradNavi CareerSkill record.

Example:

```text
Software Engineer + Critical Thinking
```

Only one CareerSkill record is allowed.

Several external evidence records might support the same CareerSkill.

Example:

```text
CareerSkill
Software Engineer + Critical Thinking
        |
        +-- O*NET evidence
        |
        +-- ESCO evidence
```

This avoids duplicate scoring contributions.

---

## 26. CareerSkill Evidence

CareerSkillEvidence preserves source-native evidence.

Evidence should preserve available values such as:

```text
dataset
external occupation identifier
external Skill identifier
source domain
source relationship
raw Importance
normalised Importance
raw Level
normalised Level
scale minimum
scale maximum
Not Relevant
Recommend Suppress
source update date
```

One source evidence row must remain distinguishable from another source evidence row.

---

## 27. O*NET Quality Flags

O*NET occupational rating records include data-quality fields.

Relevant fields include:

```text
Not Relevant
Recommend Suppress
```

### Not Relevant

Where O*NET marks an element as not relevant for an occupation:

```text
not_relevant = true
```

The relationship must not enter approved CareerSkill scoring from that evidence alone.

### Recommend Suppress

Where O*NET marks a rating with:

```text
Recommend Suppress = Y
```

GradNavi should not automatically approve the numerical rating.

The evidence stays preserved for traceability.

The relationship or rating requires manual review before numerical use.

GradNavi should add a `recommend_suppress` field to CareerSkillEvidence before the O*NET import implementation.

---

## 28. O*NET Rating Data

O*NET rating rows include:

```text
Scale ID
Scale Name
Data Value
```

GradNavi preserves:

```text
raw value
source scale
source minimum
source maximum
```

No O*NET Data Value should be interpreted without its corresponding scale metadata.

---

## 29. Importance Normalisation

GradNavi stores CareerSkill Importance on a:

```text
0 to 100
```

internal scale.

For an external numerical scale with source-defined minimum and maximum:

```text
normalized_importance =
(raw_importance - scale_minimum)
/
(scale_maximum - scale_minimum)
*
100
```

The source scale limits come from source metadata.

GradNavi does not hard-code a universal O*NET minimum or maximum.

Example structure:

```text
raw_importance:
source rating

scale_minimum:
source scale minimum

scale_maximum:
source scale maximum

normalized_importance:
0 to 100
```

---

## 30. Importance Validation

Normalised Importance must satisfy:

```text
0 <= normalized_importance <= 100
```

Invalid values block approval.

Missing Importance stays null.

GradNavi does not invent an Importance value when no supported source value exists.

---

## 31. Level Normalisation

GradNavi stores a normalised Career required-level score on:

```text
0 to 100
```

For a source numerical scale:

```text
normalized_level =
(raw_level - scale_minimum)
/
(scale_maximum - scale_minimum)
*
100
```

Source scale metadata determines the minimum and maximum.

Raw Level remains preserved.

---

## 32. O*NET Level Anchors

O*NET publishes element-specific Level Scale Anchors for rating areas using the Level scale.

GradNavi should retain access to the relevant source anchor information during mapping review.

The import process does not replace source anchors with GradNavi proficiency labels automatically.

Anchors support reviewer interpretation of source Level values.

---

## 33. Student Proficiency Conversion

StudentSkill currently uses:

```text
foundational
developing
proficient
advanced
```

WBS 5.2 does not define the final numerical conversion from these four Student levels to Career required-level scores.

CareerSkill retains:

```text
required_level_score
```

and:

```text
required_proficiency
```

`required_proficiency` stays blank unless a reviewed GradNavi rule assigns a supported value.

The scoring relationship belongs to:

```text
WBS 5.3
WBS 5.5
```

---

## 34. ESCO Requirement Type

ESCO distinguishes:

```text
essential
optional
```

GradNavi CareerSkill uses:

```text
essential
optional
unspecified
```

### essential

The reviewed source relationship identifies the Skill or Knowledge as normally required for the occupation.

### optional

The reviewed source relationship identifies the Skill or Knowledge as dependent on employer, country, or work context.

### unspecified

No approved essential or optional relationship exists.

---

## 35. Requirement Type and Scoring

WBS 5.2 stores requirement type.

WBS 5.2 does not assign an arbitrary scoring multiplier.

Example:

```text
essential = stored classification
optional = stored classification
```

The numerical effect belongs to WBS 5.3.

This keeps reference-data facts separate from recommendation algorithm decisions.

---

## 36. Source Conflict Rules

Where multiple sources disagree:

```text
Preserve Source A Evidence
        +
Preserve Source B Evidence
        |
        v
Review Context
        |
        v
Approve GradNavi Interpretation
```

GradNavi does not automatically:

- average conflicting values
- select the highest value
- select the lowest value
- overwrite older evidence
- treat all sources as equivalent

Source responsibility determines initial precedence.

---

## 37. Conflict Precedence

For occupation identity:

```text
ABS OSCA
```

For Australian occupation context:

```text
Jobs and Skills Australia
```

For quantitative occupational Skill and Knowledge ratings:

```text
O*NET
```

For supplementary terminology and essential or optional relationships:

```text
ESCO
```

For runtime use after review:

```text
GradNavi approved reference dataset
```

---

## 38. Missing Source Values

Missing source values stay missing.

Examples:

```text
raw_importance = null
raw_level = null
requirement_type = unspecified
confidence_score = null
```

GradNavi does not create unsupported values to fill gaps.

Later scoring logic must define missing-data treatment.

---

## 39. Not Relevant Relationships

A source relationship explicitly marked not relevant should not contribute positive CareerSkill evidence.

The evidence remains stored.

Example:

```text
not_relevant = true
```

Runtime approval requires another valid source or a documented manual review decision.

---

## 40. CareerSkill Quantity

No fixed Skill count applies to each Career.

Examples:

```text
Career A:
23 approved Skills

Career B:
37 approved Skills

Career C:
46 approved Skills
```

All remain valid.

Source relevance determines CareerSkill count.

WBS 5.3 normalises scoring across different CareerSkill totals.

---

## 41. Inclusion Rule

A CareerSkill relationship is eligible for approval when:

- Career mapping is approved
- canonical Skill mapping is approved
- source evidence exists
- source record is relevant
- source quality flags are acceptable
- relationship is not duplicated
- mapping scope matches the Career
- source version is known
- review is complete

---

## 42. Rejection Rule

Reject a CareerSkill candidate when:

- occupation mapping is wrong
- Skill mapping is wrong
- source concept is unrelated
- source record is explicitly not relevant
- duplicate canonical concept exists
- evidence belongs to another occupation scope
- source data is invalid
- source version is unsupported
- reviewer rejects the relationship

Rejected mappings remain traceable where practical.

---

## 43. Automatic Approval Rule

Automatic approval should be conservative.

Initial WBS 5.2 implementation should prefer:

```text
candidate import
+
review
+
approval
```

rather than broad automatic approval.

A future automatic approval rule requires:

- documented deterministic conditions
- source quality validation
- automated tests
- team approval

---

## 44. Idempotent Import Rule

Running the same source dataset more than once must not create duplicate records.

Stable matching uses:

- source dataset
- external identifiers
- canonical Skill identifiers
- Career identifiers
- CareerSkill uniqueness
- evidence uniqueness

Repeated imports should update or reuse matching records according to documented importer rules.

---

## 45. Import Transaction Rule

Reference-data import should use database transactions.

A failed import should avoid partial persistence where transaction boundaries support rollback.

The importer should report:

```text
records read
records matched
records created
records updated
records skipped
records pending review
records rejected
errors
```

---

## 46. Dry-Run Rule

The importer should support:

```powershell
python backend/manage.py import_reference_data --dry-run
```

Dry-run should:

- read source data
- run validation
- perform mapping logic
- report proposed changes
- avoid permanent database changes

---

## 47. Career Mapping Review Record

Review should verify:

```text
GradNavi Career
OSCA identity
external occupation
mapping method
occupation scope
title
classification relationship
review status
```

For the initial 36 Careers, each Career requires a verified Australian occupation identity before full CareerSkill import.

---

## 48. Skill Mapping Review Record

Review should verify:

```text
canonical Skill
concept type
external label
external identifier
source domain
mapping method
duplicate status
review status
```

---

## 49. CareerSkill Review Record

Review should verify:

```text
Career
Skill
source evidence
Importance
Level
requirement type
Not Relevant status
Recommend Suppress status
review status
```

---

## 50. Auditability

GradNavi should preserve enough information to answer:

```text
Why does this Career contain this Skill?
```

The answer should trace:

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

This supports recommendation explainability and reference-data review.

---

## 51. Mapping Example

Example conceptual mapping:

```text
GradNavi Career:
Software Engineer

OSCA:
Reviewed Australian occupation mapping

O*NET:
Reviewed occupation mapping

GradNavi Skill:
Critical Thinking

O*NET Evidence:
Occupation Skill rating
Importance
Level

ESCO Evidence:
Occupation-Skill relationship
Essential or Optional where present

GradNavi CareerSkill:
Software Engineer + Critical Thinking

Review Status:
approved
```

---

## 52. Technology Mapping Example

Example:

```text
External Label:
Python

Canonical GradNavi Skill:
Python

Concept Type:
technology

Mapping Method:
exact_title

Review Status:
approved
```

Existing Sprint 1 Python Skill should be reused rather than duplicated.

---

## 53. Alias Example

Example:

```text
Canonical Skill:
Structured Query Language

Alias:
SQL
```

External mappings reference the same canonical concept after review.

---

## 54. Ambiguous Mapping Example

Example:

```text
External Skill:
Programming
```

Possible GradNavi records:

```text
Programming
Python
Java
C++
```

The importer must not map the broad Programming concept to Python automatically.

A broader concept remains separate unless source meaning and mapping rules support equivalence.

---

## 55. Source Version Rule

Every mapping must trace to a known ReferenceDataset.

Example:

```text
O*NET
31.0
```

A mapping without a known source dataset version should not enter approved runtime reference data.

---

## 56. Mapping Change Rule

Changing an approved mapping requires:

```text
previous mapping
new mapping
reason
source
source version
review status
reviewer
review date
GradNavi dataset version
```

Future update tooling should preserve change history where practical.

---

## 57. Dataset Version Effect

Mapping changes might require a GradNavi reference dataset version update.

Examples:

```text
new Career
new approved Skill
Career remapping
Skill merge
new CareerSkill
rejected CareerSkill
source version update
```

Version rules are documented in:

```text
docs/reference-data/DATASET_VERSION.md
```

---

## 58. Attribution

Mappings derived from external datasets must preserve source attribution.

Attribution requirements are documented in:

```text
docs/reference-data/ATTRIBUTION.md
```

---

## 59. WBS Boundary

This document defines reference-data mapping.

It does not define:

- final recommendation weights
- final Skill-match score
- final Student proficiency score
- essential Skill multiplier
- optional Skill multiplier
- Career ranking
- readiness score
- missing profile treatment
- final recommendation explanation

Those decisions belong to later WBS tasks.

---

## 60. Current Mapping Baseline

```text
Australian Career Identity:
ABS OSCA

Australian Context:
Jobs and Skills Australia

Detailed Occupational Ratings:
O*NET 31.0

Supplementary Skill Relationships:
ESCO 1.2.1

Runtime Reference Source:
GradNavi PostgreSQL

Initial Career Target:
36

Fixed CareerSkill Count:
No

Automatic Broad Mapping Approval:
No

Human Review:
Yes

Source Provenance:
Required
```

---

## 61. Required Schema Follow-Up

O*NET 31.0 rating records include a Recommend Suppress quality indicator.

The current GradNavi CareerSkillEvidence model already stores:

```text
not_relevant
```

The model should also store:

```text
recommend_suppress
```

before O*NET data import begins.

This preserves source quality metadata used during mapping review.

---

## 62. Related Documents

This document should stay aligned with:

```text
docs/reference-data/SOURCES.md
docs/reference-data/DATASET_VERSION.md
docs/reference-data/ATTRIBUTION.md
docs/reference-data/README.md
docs/system-design/career-skill-reference-data-design.md
docs/system-design/recommendation-scoring-design.md
backend/careers/models.py
backend/profiles/models.py
```

---

## 63. Current Status

```text
WBS 5.2 Mapping Rules:
Defined

GradNavi Dataset:
1.0 working

Next Activity:
Reference-data attribution and schema quality-field update
```