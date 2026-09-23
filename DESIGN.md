# UI Design

Current Figma source:

https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes

## Current Implemented Student-Facing Redesigns

| Screen | Figma node | Repository status |
| --- | --- | --- |
| Student Profile - Redesigned | `543:248` | Implemented in the WBS 5.6 working branch |
| Career Recommendations - Redesigned | `493:391` | Implemented in the WBS 5.6 working branch |
| Skill Gap Analysis - Redesigned | `539:189` | Implemented in the WBS 5.6 working branch |

The implemented interfaces use the existing GradNavi student shell and real backend data rather than the sample values shown in Figma.

Current design decisions include:

- Career Recommendations display Career Match and selected-career Readiness as student-facing percentages.
- Only the Top Match requests an AI-generated career-match explanation.
- Other Career Matches use deterministic strongest-evidence data and do not make additional AI requests.
- Skill Gap Analysis displays deterministic Readiness, Matched, Partially Matched, Missing, Requirement Details, and Fix First data.
- The AI Gap Summary explains deterministic results but does not calculate scores or priorities.
- Learning-resource areas only display backend-controlled resources and use an honest empty state when no resource is linked.
- Student Profile supports multiple Career Goals with exactly one Primary Goal.
- Skills, Career Goals, and Interests use compact profile-evidence cards with searchable editors.
- Education, Experience, and Projects use compact structured-evidence rows.
- Personality Assessment uses the approved 16-question one-question-at-a-time flow.

These Figma screens are the current visual source for the implemented WBS 5.6 student-facing interfaces.
