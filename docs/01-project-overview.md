# GradNavi Project Overview

Status: Working baseline for team review

## Project name

GradNavi, AI-Powered Career Guidance System

## Project context

University career services provide valuable support, but appointments are limited and demand often increases near graduation. Students also need to interpret job advertisements, skills requirements, qualifications, learning pathways, and application expectations.

GradNavi addresses this problem through a responsive web application. A student creates one structured profile containing skills, interests, education, experience, projects, and career goals. The system reuses this profile across career recommendations, readiness scoring, skill-gap analysis, application preparation, learning suggestions, and career planning.

## Problem statement

Students approaching graduation often lack a reliable way to identify suitable careers, measure their readiness for a target role, recognise missing skills, and decide which development steps to complete first.

Existing tools often focus on one area, such as keyword matching, document formatting, or course recommendations. They do not provide a connected and explainable student journey.

## Project objectives

1. Provide secure student and administrator access.
2. Let students maintain a structured career profile.
3. Generate ranked career recommendations through documented weighted rules.
4. Calculate career-readiness scores and identify missing or partly met skills.
5. Explain recommendations and scores in plain language.
6. Match a student profile against one pasted job description.
7. Generate editable resume and cover-letter drafts.
8. Provide text-based interview preparation and written feedback.
9. Recommend learning resources and ordered career-development steps.
10. Provide basic administration and aggregated reporting.
11. Protect personal information and keep AI processing on the backend.
12. Complete documented testing, deployment, reporting, and presentation work during Term 2 2026.

## Main users

| User | Main needs |
|---|---|
| Student | Profile management, career guidance, readiness results, skill gaps, employment preparation, learning suggestions, and progress tracking |
| Administrator | User management, career and skill data management, learning-resource management, audit records, and basic reports |

## In scope

- Registration, login, password management, JWT access, and role-based permissions
- Student profile management
- Weighted career recommendation scoring
- Recommendation explanations
- Career-readiness scoring
- Skill-gap analysis
- Job-description analysis and matching
- Editable resume and cover-letter drafts
- Text-based interview preparation
- Learning suggestions
- Career-development roadmap
- Progress dashboard
- Basic administration and analytics
- AI content review
- Data deletion
- Audit records and clear error handling
- Responsive React interface
- Django REST backend
- PostgreSQL database
- Unit, component, API, permission, integration, system, usability, and acceptance testing
- Demonstration deployment using Vercel and Railway

## Out of scope

- Native mobile applications
- Live job-board or applicant-tracking-system integration
- Video, audio, or webcam interview simulation
- Payments and subscriptions
- Training or hosting a custom machine-learning model
- Automatic job applications
- University-system or single-sign-on integration
- Formal accessibility certification
- Multilingual support
- Production-scale infrastructure and disaster recovery

## Core design decisions

### Controlled scoring

Documented weighted rules will calculate recommendation and readiness scores. The same structured input should return the same numerical result.

### Limited generative AI role

The AI service will explain scores and generate editable text. It will not independently determine numerical recommendation scores.

### Backend AI processing

AI requests will pass through the Django backend. The backend will minimise unnecessary personal information, protect the API key, apply approved prompts, and validate responses.

### Student control

Generated resumes, cover letters, explanations, interview feedback, and roadmaps will remain editable. Students must review generated content before saving or using it.

## Main constraints

| Constraint | Effect |
|---|---|
| Term length | The team must prioritise the core student journey and control scope |
| Three-member team | Work must be divided clearly across frontend, backend, integration, and project management |
| Limited budget | The project will rely on free, educational, or low-cost service tiers |
| New technologies | Early setup, small prototypes, and shared learning are required |
| Third-party AI service | Rate limits, latency, outages, and service changes require fallback behaviour |
| Data privacy | Personal information must be minimised and protected |
| Data availability | The prototype will use a controlled set of curated career and skill records |
| Academic prototype | Outputs provide decision support and do not replace professional career advice |
