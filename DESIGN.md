# GradNavi UI Design

## Design sources

The current student-facing frontend draws from the high-fidelity Figma designs below. They are the visual references for page composition, hierarchy, cards, controls, and interaction states.

- [08 - Full UX](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=482-2): student experience, dashboard, profile, recommendations, exploration, gap analysis, roadmap, learning, resume and cover letter builders, interview preparation, and responsive guidance.
- [09 - Sprint 4 UX](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=670-2): Job Matching, administrative experiences, AI failure/retry states, and access/permission states.
- [00 - Assets](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=731-2): logos and image assets. This is not a substitute for the high-fidelity screen designs.

The Figma desktop frames are design references, not fixed-width requirements for every browser viewport. The responsive implementation must preserve the design language while reflowing to use the available space. Real backend values replace example data shown in Figma.

## Student screen-to-design mapping

| Implemented route | Page | Figma reference |
| --- | --- | --- |
| `/dashboard` | Dashboard | [Student Dashboard - Redesign v2](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=730-2) |
| `/profile` | Student Profile | [Student Profile - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=543-248) |
| `/career-recommendations` | Career Recommendations | [Career Recommendations - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=539-2) |
| `/explore-careers` | Explore Careers | [Explore All Careers - Future Design](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=624-2); use as design direction, not proof of exact implemented parity |
| `/skill-gap-analysis` | Skill Gap Analysis | [Skill Gap Analysis - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=539-189) |
| `/career-roadmap` | Career Roadmap | [Career Roadmap - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=541-2) |
| `/learning-resources` | Learning Resources | [Learning Resources - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=541-111) |
| `/job-matching` | Job Matching | [Input](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=670-3) and [Results](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=670-4) |
| `/resume-builder` | Resume Builder | [Resume Builder - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=552-2) |
| `/cover-letter-builder` | Cover Letter Builder | [Cover Letter Builder - Redesigned](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=552-325) |
| `/interview-preparation` | Interview Preparation | [Setup](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=553-2), [Questions](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=553-218), and [Feedback](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=553-365) |
| `/settings` | Settings | Current implemented UI; no dedicated high-fidelity frame verified in the two referenced Figma pages |

The [Responsive Behaviour](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=545-331) and [Sprint 3 Responsive Patterns](https://www.figma.com/design/4nnlQh6V3YcgnKSvPrizYV/GradNavi---Wireframes?node-id=554-2) frames guide smaller-screen adaptations.

## Shared layout rules

1. Keep the existing `StudentLayout` sidebar and route navigation. Desktop sidebar width is 250px in the current React CSS.
2. Give each student page the remaining width of the main content region. Keep consistent page gutters. Desktop student pages typically use 48px horizontal padding; narrower viewports use their existing responsive padding rules.
3. Do not impose arbitrary 1040px, 1036px, 1100px, 1180px, or 1320px limits on entire student page content wrappers. Content containers must have `width: 100%`, and their grids must allow children to shrink without horizontal overflow.
4. Keep reasonable line lengths for paragraphs, field help, and long prose. Those local text constraints do not restrict the full page or surrounding cards.
5. Use flexible grids for dashboard metrics, recommendation panels, learning cards, profile evidence, and document-building inputs. Reflow columns when space becomes limited. Do not scale fixed desktop columns into unreadable mobile layouts.
6. Align page titles, descriptions, and account controls consistently. Preserve existing visual hierarchy, card treatments, focus styles, navigation states, and branding.
7. At the student shell's existing mobile breakpoint (767px and below), use the existing menu/drawer navigation. Keep controls reachable and visibly labelled.
8. Preserve browser zoom and keyboard usability. Avoid clipped text, hidden actions, overflowing form fields, or unintentional page-level horizontal scrolling.
9. A selected career and learning focus must stay understandable when cards stack. Long generated drafts should use responsive, readable sections rather than fixed desktop composition.
10. Keep feature-specific responsive rules in the owning page stylesheet. Change the shared shell only if its behaviour, rather than a page-specific width cap, is the verified cause.

### Current source locations

- `frontend/src/layouts/StudentLayout.jsx` and `StudentLayout.css`: shared navigation and content region.
- `frontend/src/pages/StudentDashboardPage.css`: Dashboard content width and cards.
- `frontend/src/pages/CareerGuidancePage.css`: Career Recommendations, Explore Careers, Skill Gap Analysis, Career Roadmap, and Learning Resources.
- `frontend/src/pages/ResumeBuilderPage.css`, `CoverLetterBuilderPage.css`, `InterviewPreparationPage.css`: application and interview tools.
- `frontend/src/pages/JobMatchingPage.css`, `SettingsPage.css`, `StudentProfilePage.css`: related student screens.
- `frontend/src/styles/tokens.css` and `frontend/src/styles/components.css`: shared design tokens and components.

## Product and data presentation rules

- Career Match and selected-career Readiness are distinct student-facing percentages.
- Only the top career match requests the AI career-match explanation. Other matches show deterministic evidence without additional AI explanation requests.
- Skill Gap Analysis shows calculated readiness, matched/partially matched/missing requirements, and prioritised gaps. AI explains results without changing scores or priorities.
- Learning resource cards use backend-controlled links and accurate empty states when no suitable resource is linked.
- Student Profile supports several career goals with one Primary Goal, searchable skill/goal/interest editing, structured education/experience/projects, and the approved 16-question personality flow.
- Resume and cover letter drafts reflect actual profile evidence, stay editable, and preserve the application's existing saved-version behaviour.
- Job Matching presents recognised requirements and the limits of its matching. The input and results states follow the Sprint 4 UX screens.
- Keep server response contracts, scoring, identity handling, and privacy safeguards unchanged during visual-only refactors.

## Verification checklist

Run and record the checks below before merging a responsive layout change.

- [ ] Inspect all twelve student navigation routes at wide desktop, standard desktop, tablet, and mobile viewport sizes.
- [ ] Confirm page sections extend through the available content width, with consistent gutters.
- [ ] Confirm browser zoom does not hide information or controls.
- [ ] Verify navigation drawer, focus states, account control, and route transitions.
- [ ] Confirm cards, metric grids, forms, generated drafts, and interview sections reflow without page-level horizontal overflow.
- [ ] Review loading, empty, error, and populated content states where available.
- [ ] Check both Job Matching input and result states.
- [ ] Run frontend lint/build/tests and capture appropriately labelled screenshots.
- [ ] Verify page behaviour is unchanged and document any unrelated existing defects.

This document records the design sources and responsive implementation rules. It does not assert that viewport screenshots, cross-browser testing, or every Figma-to-implementation comparison has already passed.
