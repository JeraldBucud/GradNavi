# GradNavi WBS 5.6 Closeout Record

Status: Technical implementation and regression testing complete, pending Pull Request review and merge

WBS: 5.6 Recommendation and Readiness Interface

Sprint: Sprint 2 - Career Recommendations and Skill Gaps

Official WBS owner: Joyee

Implementation support and recovery: Jerald

Branch: `jerald/wbs-5.6-recommendation-readiness-interface`

Pull Request: `#44`

Current integration target: `feature/sprint-3`

## 1. Purpose

WBS 5.6 delivers the student-facing Recommendation and Readiness interface required to connect the deterministic Sprint 2 backend services to the GradNavi frontend.

The final implementation includes Career Recommendations, selected-career Readiness, Skill Gap Analysis, controlled AI explanations, cache-backed provider usage, and supporting Student Profile interface improvements required for reliable profile evidence.

WBS 5.6 does not replace WBS 5.8 Learning Roadmap Interface.

## 2. Career Recommendations Interface

The implemented Career Recommendations interface includes:

- Deterministic ranked Career Recommendations.
- One Top Match.
- Up to six Other Career Matches.
- Student-facing Career Match percentages.
- Selected-career Readiness percentages.
- Deterministic strongest-evidence display.
- View Skill Gaps navigation.
- Recommended Next Actions.

The implemented Figma source is:

`Career Recommendations - Redesigned`

Figma node: `493:391`

## 3. Top Match AI Explanation

Only the Top Match receives an AI-generated career-match explanation.

Secondary Career matches use deterministic strongest-evidence data and do not request additional AI explanations.

The current explanation contract version is:

`career_match_explanation_v2`

The default text model is:

`gpt-5-nano`

AI does not determine Recommendation Score, rank, Readiness Score, requirement status, or Skill-gap priority.

## 4. Recommendation Cache

Recommendation results use `RecommendationSnapshot`.

The cache stores the latest valid controlled recommendation payload and cache metadata.

When the current cache key remains valid, the backend may reuse the stored recommendation result instead of repeating recommendation generation work.

The cache exists for performance and provider-cost control.

It does not change deterministic Recommendation scoring.

## 5. Selected-Career Readiness API

WBS 5.6 adds the selected-career Readiness contract:

`GET /api/v1/readiness/?career_id=<id>`

The endpoint exposes:

- Readiness Score.
- Readiness status.
- Total requirement count.
- Matched count.
- Partially Matched count.
- Missing count.
- Requirement details.
- Current proficiency.
- Current score.
- Required level.
- Gap amount.
- Attainment percentage.
- Requirement status.

Readiness calculations remain deterministic under WBS 5.5.

## 6. Skill Gap Analysis Interface

The implemented Skill Gap Analysis interface includes:

- Readiness Overview.
- Matched count.
- Partially Matched count.
- Missing count.
- AI Gap Summary.
- Deterministic Fix First priorities.
- Recommended Next Steps.
- Requirement Details.
- Learning Suggestions.

The implemented Figma source is:

`Skill Gap Analysis - Redesigned`

Figma node: `539:189`

## 7. Fix First Ownership

Fix First priority and order remain deterministic.

The governing rule is:

**WBS 5.5 owns priority and order. AI writes wording only.**

The dynamic action-count rule is:

- 1 unresolved gap -> 1 action.
- 2 unresolved gaps -> 2 actions.
- 3 or more unresolved gaps -> deterministic top 3 -> 3 actions.

The backend validates AI action wording and returns the actions in deterministic Fix First order.

## 8. AI Gap Summary

The current Skill Gap Summary contract version is:

`skill_gap_summary_v3`

The AI layer may write:

- Student-facing readiness explanation.
- One next-step sentence for each deterministic Fix First item.

The AI layer does not select or reorder Fix First Skills.

## 9. Skill Gap Summary Cache

Validated AI Gap Summary results are persisted through `SkillGapSummarySnapshot`.

Migration:

`careers.0010_skillgapsummarysnapshot`

A valid cached response may be returned without another OpenAI generation.

Relevant Student, Career, readiness, controlled learning-resource, model, or summary-version changes invalidate the cache.

## 10. Learning Resource Behaviour

WBS 5.6 only displays controlled Learning Resources returned by the backend.

The interface does not fabricate course names, providers, URLs, or resource links.

When no controlled Learning Resource is linked, the interface displays an honest empty state.

The separate WBS 5.8 Learning Roadmap Interface remains outside this closeout.

## 11. Supporting Student Profile Integration Work

The same implementation branch also completed supporting Student Profile interface improvements required for reliable Career Recommendation and Readiness evidence.

These supporting changes include:

- Redesigned Profile Evidence Summary.
- Searchable Skill editing.
- Searchable Interest editing.
- Multiple Career Goals.
- Exactly one Primary Career Goal when goals exist.
- Structured `career_id` support.
- Legacy `target_role` compatibility.
- Compact Education, Experience, and Project evidence rows.
- 16-question work-style Personality Assessment.
- One-question-at-a-time Personality flow.

The implemented Student Profile Figma source is:

`Student Profile - Redesigned`

Figma node: `543:248`

This supporting work does not reassign the official Microsoft Project ownership of the original Student Profile or WBS 5.6 tasks.

## 12. AI Provider Boundary

WBS 5.6 introduces limited backend OpenAI text generation for Career Match and Skill Gap explanations.

Environment configuration includes:

- `OPENAI_API_KEY`
- `OPENAI_TEXT_MODEL`

The default text model is `gpt-5-nano`.

The frontend does not call OpenAI directly.

This limited WBS 5.6 provider integration does not complete or replace WBS 7.3.

WBS 7.3 remains responsible for broader Sprint 4 provider integration for Resume, Cover Letter, Interview Question, Interview Feedback, and other approved AI operations.

## 13. Final Regression Results

The final WBS 5.6 branch regression recorded:

- Full backend regression: `673 / 673 PASS`.
- Student Profile model and API regression: `38 / 38 PASS`.
- Selected-career Readiness API: `8 / 8 PASS`.
- Top Match AI regression: `4 / 4 PASS`.
- AI Gap Summary regression: `7 / 7 PASS`.
- AI services regression: `119 / 119 PASS`.
- Recommendation cache regression: `19 / 19 PASS`.
- Recommendation API regression: `12 / 12 PASS`.
- Readiness and Learning regression: `37 / 37 PASS`.
- Django system check: `PASS`.
- Migration drift check: `No changes detected`.
- Frontend lint: `0 warnings, 0 errors`.
- Frontend production build: `PASS`.
- Git diff check: `PASS`.

Recorded failures: `0`.

## 14. Controlled Live AI Validation

Separate controlled live checks verified real `gpt-5-nano` generation and database-cache reuse.

Top Match validation confirmed:

- First request generated a real AI explanation.
- The explanation was stored for reuse.
- The second request returned the cached explanation.
- The second request did not call the OpenAI provider.

Skill Gap Summary validation confirmed:

- First request generated a real V3 AI Gap Summary.
- Deterministic Fix First order was preserved.
- The summary was stored in `SkillGapSummarySnapshot`.
- The second request returned the cached summary.
- The second request did not call the OpenAI provider.

## 15. Pull Request and Integration

Pull Request:

`#44 WBS 5.6: Recommendation and readiness interface`

Current PR state:

`DRAFT`

Source branch:

`jerald/wbs-5.6-recommendation-readiness-interface`

Current integration target:

`feature/sprint-3`

WBS 5.6 originated in Sprint 2.

Because the delayed WBS 5.6 work was completed after Sprint 3 had already started, the current PR targets the active Sprint 3 integration branch.

This does not change the original WBS Sprint allocation or official ownership.

## 16. Remaining Closeout Actions

Technical implementation and regression testing are complete.

Project-management actions still required:

1. Complete the WBS 5.6 documentation update.
2. Update the Sprint 2 integration and testing records.
3. Update the Product Backlog execution status.
4. Update the Contribution Log.
5. Review the final documentation diff.
6. Commit the documentation update.
7. Push the branch.
8. Update Pull Request #44 description and evidence.
9. Request team review.
10. Address valid review findings.
11. Merge after approval.
12. Mark WBS 5.6 formally complete after merge.

## 17. Closeout Decision

Technical implementation:

`COMPLETE`

Full backend regression:

`673 / 673 PASS`

Frontend lint:

`0 warnings, 0 errors`

Frontend production build:

`PASS`

Django system check:

`PASS`

Migration drift:

`NONE`

Team review:

`PENDING`

PR merge:

`PENDING`

Formal WBS 5.6 status:

`PENDING TEAM REVIEW AND MERGE`
