# WBS 5.3 Technology Demand Evidence Design

## Document Status

Status: Dataset 1.1 design checkpoint

Branch:

`jerald/wbs-5.3-scoring-validation`

Production status:

Technology-demand evidence is not yet used by production recommendation scoring.

---

# 1. Purpose

This document defines the proposed technology-demand evidence layer for the revised GradNavi Career Fit model.

The design was introduced after WBS 5.6 integration exposed a limitation in the original WBS 5.3 scoring model.

A Student Profile containing:

- Python — Foundational
- Django — Developing
- React — Proficient
- PostgreSQL — Advanced

received a Software Engineer recommendation score of 0%.

Investigation confirmed that the Student technologies were correctly stored and correctly linked to Software Engineer through O*NET Software Skills evidence.

The limitation was that technology relationships did not participate in numerical recommendation scoring.

---

# 2. Existing Dataset 1.0 Technology Evidence

Dataset 1.0 currently preserves broad O*NET Software Skills relationships.

For Software Engineer:

```text
O*NET software evidence rows: 430
```

Examples include:

```text
Python
Django
React
PostgreSQL
Docker
Git
JavaScript
```

The current evidence records preserve:

```text
Career
canonical Skill
external Skill identifier
O*NET source
O*NET dataset version
source domain
```

However, the current evidence does not preserve:

```text
Hot Technology
In Demand
employer-posting percentage
```

The technology records also correctly have no O*NET numerical Importance or required Level because these are not the source semantics for O*NET software examples.

---

# 3. O*NET Software Skills Evidence Types

O*NET provides multiple distinct technology signals.

## 3.1 Software Skill Relationship

Meaning:

```text
This software technology is associated with the occupation.
```

This is broad catalogue evidence.

It must not be interpreted as:

```text
Every worker in this occupation must know this technology.
```

---

## 3.2 Hot Technology

Meaning:

```text
The technology is frequently mentioned across employer job postings.
```

Hot Technology is a market-wide signal.

It is not itself an occupation-specific percentage weight.

---

## 3.3 In Demand

Meaning:

```text
The technology is frequently mentioned in employer postings
for the particular O*NET occupation.
```

O*NET classifies a technology as In Demand when at least 5% of the occupation's postings contain the technology.

This is an occupation-specific threshold flag.

---

## 3.4 Employer-Posting Percentage

Meaning:

```text
percentage of unique job postings for the O*NET occupation
that mention the technology
```

This is the strongest currently identified numerical technology-demand signal for the planned GradNavi Technology Fit component.

---

# 4. Example: O*NET Software Developers

O*NET occupation:

```text
15-1252.00
Software Developers
```

Example employer-demand evidence includes:

```text
Python          29%
React           13%
PostgreSQL       6%
Django           1%
```

Therefore GradNavi must not restrict Technology Fit only to technologies marked `In Demand`.

If GradNavi used only the O*NET 5% In Demand threshold:

```text
Python          included
React           included
PostgreSQL      included
Django          excluded
```

That would discard real employer-posting evidence for technologies below the threshold.

Dataset 1.1 will therefore preserve raw available posting percentages separately from the In Demand flag.

---

# 5. Geographic Limitation

Current O*NET employer-posting technology percentages are based on Lightcast job-posting data for the United States nationwide.

For the current Software Developer evidence, the posting period is:

```text
January 1, 2025
through
December 31, 2025
```

GradNavi must therefore describe this evidence as:

```text
O*NET employer-demand evidence
```

or:

```text
US employer-posting evidence
```

GradNavi must not describe these percentages as Australian employer-demand percentages.

OSCA remains the Australian occupation identity source.

Future Australian labour-market evidence may supplement or replace this market-demand component.

---

# 6. Dataset 1.1 Principle

Dataset 1.1 will not replace the existing broad technology relationships.

Instead it will add a separate market-demand evidence layer.

Conceptually:

```text
CareerSkill
    |
    +-- O*NET Software Skills relationship evidence
    |
    +-- O*NET employer-demand evidence
```

Example:

```text
Software Engineer
    |
    +-- Python
         |
         +-- relationship evidence
         |
         +-- employer demand
             posting percentage = 29
             hot technology = true
             in demand = true
```

---

# 7. Proposed CareerSkillEvidence Extension

The existing `CareerSkillEvidence` model remains the source-native evidence container.

Add:

```text
hot_technology
in_demand
posting_percentage
```

Proposed Django fields:

```python
hot_technology = models.BooleanField(
    blank=True,
    null=True,
)

in_demand = models.BooleanField(
    blank=True,
    null=True,
)

posting_percentage = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    blank=True,
    null=True,
)
```

Constraint:

```text
posting_percentage IS NULL

OR

0 <= posting_percentage <= 100
```

`NULL` has a different meaning from zero.

```text
NULL
= no numerical employer-posting percentage was available

0
= source explicitly reported a zero-equivalent value
  if supported by the source representation
```

The importer must preserve this distinction.

---

# 8. Fields That Must Not Be Reused

Employer-posting percentage must not be stored in:

```text
raw_importance
normalized_importance
raw_level
normalized_level
```

Reason:

```text
O*NET Importance
!=
employer-posting frequency
```

These values represent different concepts.

The scoring model must keep them separate.

---

# 9. Proposed Source Metadata

Technology-demand evidence should use a separate reference-source identity from the static O*NET Database evidence.

Proposed source:

```text
O*NET OnLine Employer Demand
```

Proposed dataset version format:

```text
2026-lightcast-us-2025
```

The reference dataset should preserve:

```text
source
version
retrieved_at
source URL
checksum where applicable
status
```

Proposed evidence source domain:

```text
onet_technology_demand
```

Proposed source relation:

```text
employer_posting
```

---

# 10. Dataset 1.0 Preservation

Dataset 1.0 must remain reproducible.

Existing evidence must not be silently rewritten.

The revision should therefore preserve:

```text
Dataset 1.0
    current relationship evidence

Dataset 1.1
    Dataset 1.0 evidence
    +
    technology-demand evidence
```

This allows:

```text
before/after benchmarking
rollback
source tracing
reproducibility
```

---

# 11. Technology Fit Inputs

The Technology Fit research phase will have two input types.

Career-side evidence:

```text
technology
employer-posting percentage
Hot Technology flag
In Demand flag
occupation
source/version
```

Student-side evidence:

```text
canonical technology Skill
Student proficiency
```

Existing Student proficiency scale:

```text
Missing        0.00
Foundational   0.25
Developing     0.50
Proficient     0.75
Advanced       1.00
```

The existing proficiency model will be reused.

No second technology-specific Student proficiency system will be created.

---

# 12. Initial Technology Formula Candidate

The first research candidate will test:

```text
Technology Fit
=
Σ(
    employer demand
    × Student proficiency factor
)
---------------------------------
Σ employer demand
× 100
```

This is a candidate only.

It is not yet accepted as the final formula.

---

# 13. Technology Formula Variants to Benchmark

The validation phase should compare at least:

## T0 — Relationship Presence Baseline

Purpose:

Measure how poorly broad unweighted catalogue matching performs.

This is a baseline only.

---

## T1 — Employer Demand × Proficiency

Uses all available employer-posting percentages.

```text
Σ(demand × proficiency)
-----------------------
Σ demand
```

---

## T2 — In-Demand-Only × Proficiency

Uses only technologies where:

```text
in_demand = true
```

This tests the effect of O*NET's occupation-specific 5% threshold.

This candidate is expected to omit lower-frequency technologies such as Django for Software Developers.

---

## T3 — Alternative Demand Transformation

If raw posting percentages cause excessive concentration around a small number of technologies, a transformed demand weighting may be investigated.

Examples could include:

```text
sqrt(demand)
```

or another evidence-backed transformation.

No transformation will be adopted without benchmark evidence.

---

# 14. Candidate Selection Rule

Technology Fit will not be selected because one example produces a desirable Software Engineer score.

Technology candidates must be evaluated across the GradNavi Career dataset.

Evaluation should include:

```text
Hit@1
Hit@3
Hit@5
MRR
nDCG@5
```

Additional property checks should include:

```text
higher proficiency cannot lower Technology Fit
adding a matching technology cannot lower Technology Fit
unrelated technologies cannot improve Technology Fit
same evidence produces deterministic results
score remains bounded between 0 and 100
```

---

# 15. Competency + Technology Combination

The selected competency model is Candidate 2.

The future combined model is conceptually:

```text
Career Fit
=
lambda * Competency Fit
+
(1 - lambda) * Technology Fit
```

`lambda` will not be manually guessed.

Candidate weighting will be calibrated through controlled benchmark testing.

Example sweep:

```text
0.00
0.05
0.10
...
0.90
0.95
1.00
```

The winning weight must improve aggregate ranking quality rather than only one Student example.

---

# 16. Shared O*NET Occupation Limitation

Some GradNavi Careers map to the same O*NET occupation.

Example:

```text
DevOps Engineer
Software Engineer
```

both currently map to:

```text
15-1252.00
Software Developers
```

Therefore O*NET occupation-level technology evidence will also be identical for these Careers.

Technology Fit alone cannot distinguish them.

Exact role differentiation will require finer evidence such as:

```text
ESCO
OSCA
```

or another reviewed role-specific source.

---

# 17. Production Boundary

At this design checkpoint:

```text
production WBS 5.3 scorer       unchanged
Candidate 2                     experimental
Technology Fit                  not implemented
database schema                 unchanged
Dataset 1.0                     unchanged
Dataset 1.1                     design only
recommendation API              unchanged
frontend                        unchanged
```

The database migration should not be created until the Dataset 1.1 source contract has been validated.

---

# 18. Next Validation Step

Before modifying Django models:

1. obtain a source-backed employer-demand snapshot;
2. verify exact fields returned by O*NET;
3. verify technology-name matching against canonical GradNavi Skills;
4. identify percentages, missing percentages, and threshold flags;
5. measure coverage across the 27 mapped O*NET occupation groups;
6. validate Dataset 1.1 row counts and duplicates;
7. only then create the migration and importer.

This keeps the data contract evidence-driven and prevents schema changes based on assumptions.