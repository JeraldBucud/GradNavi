# WBS 5.3 Recommendation Scoring Validation

## Document Status

Status: Experimental scoring validation checkpoint

Branch:

`jerald/wbs-5.3-scoring-validation`

Purpose:

This document records the investigation, benchmarking, and selection of the competency-scoring candidate intended to replace the original WBS 5.3 Version 1 recommendation formula.

Production recommendation scoring has not yet been replaced at this checkpoint.

---

# 1. Background

During WBS 5.6 frontend integration, the Career Recommendations interface exposed a limitation in the existing WBS 5.3 recommendation model.

A Student Profile containing:

- Python — Foundational
- Django — Developing
- React — Proficient
- PostgreSQL — Advanced

received a Software Engineer recommendation score of `0%`.

Further investigation confirmed that the behaviour was not caused by:

- missing `StudentSkill` records;
- incorrect canonical Skill IDs;
- missing Software Engineer technology relationships;
- stale O*NET evidence;
- incorrect authenticated Student Profile selection;
- serializer failure;
- API response failure.

The existing WBS 5.3 scorer intentionally used only numerical O*NET competency evidence for recommendation scoring.

O*NET software technologies were explanation-only evidence.

The investigation therefore expanded from a frontend integration bug into a review of the recommendation-scoring design.

---

# 2. Version 1 Baseline

The original WBS 5.3 Version 1 formula was:

```text
Recommendation Score
=
Matched O*NET Importance
------------------------
Total O*NET Importance
× 100
```

A competency received its full Importance weight when the Student possessed the canonical Skill.

Student proficiency and O*NET required Level did not affect the recommendation score.

Technologies did not affect the numerical score.

---

# 3. Structural Benchmark

A Track A structural benchmark was created using the existing GradNavi Dataset 1.0.

Active GradNavi Careers:

```text
36
```

Benchmark scenarios:

1. Full competency profile
2. Top-half competency profile

Cases:

```text
36 Careers × 2 scenarios = 72 cases
```

The benchmark uses deterministic synthetic Student profiles derived from approved O*NET numerical career evidence.

This benchmark measures internal structural behaviour.

It is not independent external validation because the benchmark profiles originate from the same reference dataset used by the scoring models.

---

# 4. Ranking Metrics

The following ranking metrics were used consistently across all candidate models:

- Hit@1
- Hit@3
- Hit@5
- Mean Reciprocal Rank (MRR)
- nDCG@5

The same metrics and benchmark profiles were used for:

- WBS 5.3 Version 1;
- Candidate 1;
- Candidate 2.

---

# 5. Version 1 Benchmark Results

## 5.1 Full Competency Profiles

```text
Exact Career

Hit@1:   47.22%
Hit@3:   86.11%
Hit@5:   94.44%
MRR:      0.6799
nDCG@5:   0.7450
```

## 5.2 Top-Half Competency Profiles

```text
Exact Career

Hit@1:   16.67%
Hit@3:   50.00%
Hit@5:   61.11%
MRR:      0.3572
nDCG@5:   0.3969
```

## 5.3 Overall

```text
Exact Career

Hit@1:   31.94%
Hit@3:   68.06%
Hit@5:   77.78%
MRR:      0.5186
nDCG@5:   0.5710
```

These results demonstrated that the Version 1 competency-presence formula was insufficiently discriminative.

---

# 6. Score Saturation Investigation

A perfect Software Engineer competency profile produced the following Version 1 results:

```text
1. DevOps Engineer       100%
2. Software Engineer     100%
3. UI / UX Designer      100%
4. Web Designer          100%
```

The same pattern appeared across other Careers.

Examples:

- Cloud Engineer produced 12 Careers at 100%.
- Supply Chain Analyst produced 12 Careers at 100%.
- Management Consultant produced 11 Careers at 100%.

This demonstrated a score-saturation problem.

The Version 1 formula measured whether the Student covered a Career's competency set but did not sufficiently measure which Career the profile was most characteristic of.

---

# 7. O*NET Evidence Overlap

The diagnostic audit found that many canonical O*NET competencies appear in almost all Careers with numerical evidence.

Examples included:

```text
Active Learning
Active Listening
Administration and Management
Complex Problem Solving
Computers and Electronics
Coordination
Critical Thinking
Judgment and Decision Making
Learning Strategies
Mathematics
```

Many appeared in:

```text
35 of 36 GradNavi Careers
= 97.22%
```

Therefore binary competency presence provides limited occupation discrimination.

---

# 8. O*NET Importance and Level Coverage

For 35 of the 36 active GradNavi Careers:

```text
O*NET Importance coverage: 100%
O*NET Level coverage:      100%
```

The only Career without eligible numerical O*NET competency evidence was:

```text
Health Information Manager
```

This confirmed that GradNavi can use both:

- O*NET Importance;
- O*NET required Level.

---

# 9. Identical O*NET Numerical Career Vectors

Seven GradNavi Career groups were found to have identical O*NET numerical competency vectors.

## Group 1

- Accountant (General)
- Management Accountant
- Taxation Accountant

## Group 2

- Content Creator (Marketing)
- Market Research Analyst
- Marketing Specialist

## Group 3

- Cyber Security Advice and Assessment Specialist
- Cyber Security Analyst

## Group 4

- Cyber Security Architect
- Cyber Security Engineer

## Group 5

- DevOps Engineer
- Software Engineer

## Group 6

- Human Resources Adviser
- Recruitment Consultant

## Group 7

- UI / UX Designer
- Web Designer

Total Careers inside duplicate vectors:

```text
16
```

This is caused by multiple GradNavi Careers mapping to the same O*NET occupation.

---

# 10. O*NET Occupation Groups

The 36 GradNavi Careers map to:

```text
27 distinct O*NET occupations
```

Therefore an O*NET-only scoring model cannot legitimately distinguish all 36 exact GradNavi Career labels.

The theoretical deterministic exact-Career Hit@1 ceiling for an O*NET-only model is:

```text
27 / 36
= 75%
```

For this reason, scoring validation now reports both:

1. Exact GradNavi Career ranking
2. O*NET occupation-group ranking

Role-specific evidence from sources such as ESCO and OSCA will be required later for exact Career differentiation.

---

# 11. Candidate 1

Candidate 1 introduced proficiency-aware requirement attainment.

Student proficiency values:

```text
Missing        0
Foundational  25
Developing    50
Proficient    75
Advanced     100
```

For each competency:

```text
Attainment
=
min(
    Student Proficiency / O*NET Required Level,
    1
)
```

Career Fit:

```text
Σ(Importance × Attainment)
--------------------------
Σ Importance
× 100
```

Candidate 1 preserved the O*NET Importance weighting but added:

- Student proficiency;
- O*NET required Level.

---

# 12. Candidate 1 Results

## 12.1 Full Competency

```text
Exact Career

Hit@1:   72.22%
Hit@3:   97.22%
Hit@5:   97.22%
MRR:      0.8380
nDCG@5:   0.8727
```

```text
O*NET Group

Hit@1:   97.22%
Hit@3:   97.22%
Hit@5:   97.22%
MRR:      0.9722
nDCG@5:   0.9722
```

## 12.2 Top-Half Competency

```text
Exact Career

Hit@1:   19.44%
Hit@3:   55.56%
Hit@5:   63.89%
MRR:      0.3926
nDCG@5:   0.4303
```

```text
O*NET Group

Hit@1:   33.33%
Hit@3:   61.11%
Hit@5:   63.89%
MRR:      0.4775
nDCG@5:   0.4939
```

Candidate 1 substantially improved complete-profile ranking but provided only limited improvement for incomplete profiles.

---

# 13. Candidate 2

Candidate 2 introduced a normalized weighted deficit-distance model.

For competency `i`:

```text
Deficit_i
=
max(
    Required Level_i - Student Proficiency_i,
    0
)
```

Weighted distance:

```text
sqrt(
    Σ(
        Importance_i
        × Deficit_i²
    )
)
```

Maximum Career deficit:

```text
sqrt(
    Σ(
        Importance_i
        × Required Level_i²
    )
)
```

Normalized deficit:

```text
Weighted Distance
-----------------
Maximum Distance
```

Candidate 2 Career Fit:

```text
(
    1 - Normalized Deficit
)
× 100
```

Properties:

- Missing competencies create a deficit.
- Being below the Career requirement creates a proportional deficit.
- Large deficits are penalized more strongly because they are squared.
- Meeting the requirement removes the deficit.
- Exceeding the requirement creates no additional reward.
- Scores remain normalized between 0 and 100.
- Careers with different numbers of requirements remain comparable.

---

# 14. Candidate 2 Results

## 14.1 Full Competency

```text
Exact Career

Hit@1:   72.22%
Hit@3:   97.22%
Hit@5:   97.22%
MRR:      0.8380
nDCG@5:   0.8727
```

```text
O*NET Group

Hit@1:   97.22%
Hit@3:   97.22%
Hit@5:   97.22%
MRR:      0.9722
nDCG@5:   0.9722
```

## 14.2 Top-Half Competency

```text
Exact Career

Hit@1:   30.56%
Hit@3:   80.56%
Hit@5:   94.44%
MRR:      0.5735
nDCG@5:   0.6663
```

```text
O*NET Group

Hit@1:   50.00%
Hit@3:   83.33%
Hit@5:   94.44%
MRR:      0.6869
nDCG@5:   0.7509
```

---

# 15. Overall Model Comparison

## 15.1 Exact Career Ranking

| Model | Hit@1 | Hit@3 | Hit@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Version 1 | 31.94% | 68.06% | 77.78% | 0.5186 | 0.5710 |
| Candidate 1 | 45.83% | 76.39% | 80.56% | 0.6153 | 0.6515 |
| Candidate 2 | **51.39%** | **88.89%** | **95.83%** | **0.7057** | **0.7695** |

## 15.2 O*NET Occupation-Group Ranking

| Model | Hit@1 | Hit@3 | Hit@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Version 1 | 48.61% | 69.44% | 79.17% | 0.6166 | 0.6491 |
| Candidate 1 | 65.28% | 79.17% | 80.56% | 0.7249 | 0.7331 |
| Candidate 2 | **73.61%** | **90.28%** | **95.83%** | **0.8296** | **0.8616** |

---

# 16. Candidate Selection

## 16.1 Version 1

Decision:

```text
Rejected as the final competency-scoring model.
```

Reason:

- Binary Skill presence ignored Student proficiency.
- O*NET required Level was unused.
- High overlap caused score saturation.
- Partial-profile ranking performance was weak.

---

## 16.2 Candidate 1

Decision:

```text
Retained as a research comparator.
Not selected as the final competency candidate.
```

Reason:

- Substantially improved complete-profile performance.
- Introduced source-backed Level and Student proficiency.
- Partial-profile performance remained substantially weaker than Candidate 2.

---

## 16.3 Candidate 2

Decision:

```text
Selected as the competency-component candidate.
```

Reason:

- Matched Candidate 1 on complete profiles.
- Significantly outperformed Candidate 1 on partial profiles.
- Significantly outperformed Version 1 across every overall ranking metric.
- Uses source-backed O*NET Importance and Level.
- Reuses GradNavi Student proficiency.
- Requires no arbitrary tuning coefficient.
- Remains deterministic and explainable.

Candidate 2 is not yet the final complete GradNavi Career Fit formula.

Technology and role-specific evidence still need to be incorporated.

---

# 17. Candidate 2 Automated Behavioural Tests

Candidate 2 currently has 14 automated unit/property tests.

Verified properties include:

- empty Student profile returns `insufficient_profile`;
- missing Career evidence returns `insufficient_evidence`;
- meeting all requirements returns `100%`;
- exceeding requirements does not reduce the score;
- increasing Student proficiency cannot lower Career Fit;
- removing a matched competency cannot improve Career Fit;
- unrelated Skills alone produce `0%`;
- partial profiles produce scores between `0` and `100`;
- scores remain bounded between `0` and `100`;
- identical inputs produce identical results;
- duplicate `CareerSkill` requirements are rejected;
- larger deficits are penalized more strongly;
- stronger Career Fit ranks first;
- identical evidence uses deterministic tie-breaking.

Test result:

```text
Ran 14 tests in 0.003s

OK
```

---

# 18. Dataset 1.0 Validation

Candidate 2 was also validated against the active GradNavi reference dataset.

Validated results:

```text
Active Careers:                         36
Careers with numerical evidence:       35
Careers without numerical evidence:     1
```

Career without numerical evidence:

```text
Health Information Manager
```

Software Engineer:

```text
Numerical requirements: 45
```

DevOps Engineer:

```text
Numerical requirements: 45
```

Their numerical O*NET vectors are identical:

```text
True
```

For a complete Software Engineer synthetic profile:

```text
Software Engineer score: 100.00
DevOps Engineer score:   100.00
```

The identical score is expected because both Careers currently share identical O*NET numerical evidence.

Health Information Manager correctly returns:

```text
insufficient_evidence
```

No fabricated numerical score is produced.

---

# 19. Current Architecture Decision

Candidate 2 is accepted only for the competency component.

The intended final architecture is:

```text
                     CAREER FIT
                         |
          +--------------+--------------+
          |                             |
          v                             v
   COMPETENCY FIT                TECHNOLOGY FIT
     Candidate 2                    Pending
          |                             |
   O*NET Importance              Employer demand
   O*NET Level                   Student proficiency
   Student proficiency
```

Additional role-specific differentiation will later use:

```text
ESCO
OSCA
```

where source evidence is suitable.

---

# 20. Technology Limitation Still Outstanding

The original Software Engineer issue has not yet been completely resolved.

The Student currently has:

```text
Python       Foundational
Django       Developing
React        Proficient
PostgreSQL   Advanced
```

These technologies are associated with Software Developer evidence, but Dataset 1.0 currently treats software technologies as explanation evidence rather than numerical recommendation evidence.

Dataset 1.0 also contains broad O*NET software-technology catalogues that must not be treated as if every technology were required.

For example, Software Engineer currently has hundreds of software technology relationships.

Therefore the technology component must use occupational demand or other source-backed technology relevance rather than simple catalogue membership.

---

# 21. Next Research Phase

The next phase is Dataset 1.1 technology-demand validation.

Planned work:

1. Preserve occupation-specific technology-demand evidence.
2. Identify appropriate O*NET employer-demand signals.
3. Keep technical Skill proficiency in the Student Profile model.
4. Create a separate Technology Fit formula.
5. Benchmark Technology Fit independently.
6. Combine Competency Fit and Technology Fit.
7. Calibrate component weighting through controlled validation rather than arbitrary manual selection.
8. Add ESCO / OSCA differentiation where appropriate.
9. Run regression, monotonicity, noise, and ranking tests.
10. Replace production WBS 5.3 only after final validation.

---

# 22. Production Status

At this checkpoint:

```text
Production recommendation_scoring.py      unchanged
Production recommendation API             unchanged
Dataset 1.0                               unchanged
WBS 5.6 frontend fix                      stashed
Candidate 1                               experimental only
Candidate 2                               experimental only
```

No experimental scoring formula has yet replaced production WBS 5.3.

This separation is intentional so the final production change is made only after the complete Career Fit model has been validated.

---

# 23. Research Basis

The scoring investigation was informed by:

- O*NET Content Model and scale definitions for occupational Skill Importance and Level;
- research on proficiency-to-requirement competency matching;
- deficit-based and distance-based career matching methods;
- occupation/skill recommendation research using ranking metrics;
- occupation-specific technology-demand evidence;
- Australian occupation identity through OSCA;
- role-specific occupation and Skill evidence through ESCO.

The research sources informed candidate design.

The final model selection within GradNavi was based on controlled benchmark results rather than selecting a formula solely because it produced a desirable score for one Student Profile.

---

# 24. Decision Summary

The validation checkpoint concludes:

```text
Version 1
    rejected as final competency model

Candidate 1
    useful improvement
    retained as benchmark comparator

Candidate 2
    selected competency candidate
    validated by:
        72 structural benchmark cases
        exact-Career metrics
        O*NET-group metrics
        14 automated behavioural tests
        Dataset 1.0 validation
```

Candidate 2 will remain isolated from production until Technology Fit and role differentiation are researched and the complete Career Fit model passes final validation.