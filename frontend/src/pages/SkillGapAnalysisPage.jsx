import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router'

import {
  getStoredUser,
} from '../services/authService'

import CareerSelector from '../components/career/CareerSelector'

import useCareerContext from '../hooks/useCareerContext'

import {
  getCareerReadiness,
  getLearningSuggestions,
  getSkillGapSummary,
} from '../services/careerService'

import './CareerGuidancePage.css'


function formatStatus(value) {
  if (!value) {
    return 'Unknown'
  }

  return value
    .split('_')
    .map(
      (part) =>
        part.charAt(0).toUpperCase()
        + part.slice(1),
    )
    .join(' ')
}


function formatNumber(value) {
  if (
    value === null
    || value === undefined
    || value === ''
  ) {
    return '—'
  }

  const numericValue =
    Number(value)

  if (
    !Number.isFinite(
      numericValue,
    )
  ) {
    return String(value)
  }

  if (
    Number.isInteger(
      numericValue,
    )
  ) {
    return String(
      numericValue,
    )
  }

  return numericValue
    .toFixed(1)
    .replace(
      /\.0$/,
      '',
    )
}


function formatPercentage(value) {
  const numericValue =
    Number(value)

  if (
    !Number.isFinite(
      numericValue,
    )
  ) {
    return 'Not scored'
  }

  return `${
    Math.round(
      numericValue,
    )
  }%`
}


function formatProficiency(value) {
  if (!value) {
    return 'No profile evidence'
  }

  return formatStatus(
    value,
  )
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  const details =
    requestError
      ?.data
      ?.error
      ?.details

  if (
    Array.isArray(
      details?.career_id,
    )
    && details.career_id.length > 0
  ) {
    return details
      .career_id[0]
  }

  return (
    requestError
      ?.data
      ?.error
      ?.message
    || requestError?.message
    || fallbackMessage
  )
}


function getUniqueResources(
  suggestions,
) {
  const resourcesById =
    new Map()

  suggestions.forEach(
    (suggestion) => {
      const resources =
        Array.isArray(
          suggestion.resources,
        )
          ? suggestion.resources
          : []

      resources.forEach(
        (resource) => {
          const existing =
            resourcesById.get(
              resource.id,
            )

          if (existing) {
            if (
              !existing
                .linked_skills
                .includes(
                  suggestion.skill_name,
                )
            ) {
              existing
                .linked_skills
                .push(
                  suggestion.skill_name,
                )
            }

            return
          }

          resourcesById.set(
            resource.id,
            {
              ...resource,
              linked_skills: [
                suggestion.skill_name,
              ],
            },
          )
        },
      )
    },
  )

  return Array.from(
    resourcesById.values(),
  )
}


function getRequirementStatusClass(
  status,
) {
  if (
    status
    === 'meets_requirement'
  ) {
    return (
      'skill-gap-figma__status '
      + 'skill-gap-figma__status--met'
    )
  }

  if (
    status
    === 'below_requirement'
  ) {
    return (
      'skill-gap-figma__status '
      + 'skill-gap-figma__status--partial'
    )
  }

  return (
    'skill-gap-figma__status '
    + 'skill-gap-figma__status--missing'
  )
}


function getRequirementActionLabel(
  requirement,
  skillsWithResources,
) {
  if (
    skillsWithResources.has(
      requirement.skill_id,
    )
  ) {
    return 'View resources'
  }

  if (
    requirement.status
    === 'meets_requirement'
  ) {
    return 'Review evidence'
  }

  if (
    requirement.status
    === 'below_requirement'
  ) {
    return 'Improve evidence'
  }

  return 'Add evidence'
}


function SkillGapAnalysisPage() {
  const navigate =
    useNavigate()

  const {
    careerOptions,
    error:
      careerContextError,
    isLoading:
      isCareerContextLoading,
    selectedCareerId:
      careerId,
    selectCareer,
  } = useCareerContext()

  const hasValidCareerId =
    Number.isInteger(
      careerId,
    )
    && careerId > 0


  const [
    coreState,
    setCoreState,
  ] = useState(null)

  const [
    coreError,
    setCoreError,
  ] = useState(null)

  const [
    aiState,
    setAiState,
  ] = useState(null)


  const currentUser =
    getStoredUser()

  const accountName =
    currentUser
      ?.first_name
      ?.trim()
    || 'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()


  const currentCoreState =
    (
      coreState?.careerId
      === careerId
    )
      ? coreState
      : null

  const currentCoreError =
    (
      coreError?.careerId
      === careerId
    )
      ? coreError.message
      : ''

  const currentAIState =
    (
      aiState?.careerId
      === careerId
    )
      ? aiState
      : null


  const readinessData =
    currentCoreState
      ?.readiness
    || null

  const learningData =
    currentCoreState
      ?.learning
    || null

  const aiSummary =
    currentAIState
      ?.data
    || null


  const isLoading =
    isCareerContextLoading
    || (
      hasValidCareerId
      && !currentCoreState
      && !currentCoreError
    )

  const isAILoading =
    Boolean(
      currentCoreState
      && !currentAIState,
    )


  const requirements =
    Array.isArray(
      readinessData
        ?.requirements,
    )
      ? readinessData.requirements
      : []

  const suggestions =
    Array.isArray(
      learningData
        ?.learning_suggestions,
    )
      ? learningData
        .learning_suggestions
      : []

  const uniqueResources =
    getUniqueResources(
      suggestions,
    )

  const previewResources =
    uniqueResources.slice(
      0,
      3,
    )

  const skillsWithResources =
    new Set(
      suggestions
        .filter(
          (suggestion) =>
            Array.isArray(
              suggestion.resources,
            )
            && suggestion
              .resources
              .length > 0,
        )
        .map(
          (suggestion) =>
            suggestion.skill_id,
        ),
    )


  const matchedCount =
    Number(
      readinessData
        ?.meets_requirement_count
      || 0,
    )

  const partialCount =
    Number(
      readinessData
        ?.below_requirement_count
      || 0,
    )

  const missingCount =
    Number(
      readinessData
        ?.missing_requirement_count
      || 0,
    )

  const unresolvedCount =
    partialCount
    + missingCount


  const fixFirst =
    Array.isArray(
      aiSummary?.fix_first,
    )
      ? aiSummary.fix_first
      : []

  const recommendedSteps =
    Array.isArray(
      aiSummary
        ?.recommended_next_steps,
    )
      ? aiSummary
        .recommended_next_steps
      : []


  useEffect(() => {
    if (
      !hasValidCareerId
    ) {
      return undefined
    }

    let isActive = true

    async function loadCoreData() {
      try {
        const [
          readinessResponse,
          learningResponse,
        ] = await Promise.all([
          getCareerReadiness(
            careerId,
          ),
          getLearningSuggestions(
            careerId,
          ),
        ])

        if (!isActive) {
          return
        }

        setCoreState(
          {
            careerId,
            readiness:
              readinessResponse
                ?.data
              || null,
            learning:
              learningResponse
                ?.data
              || null,
          },
        )
      } catch (
        requestError
      ) {
        if (!isActive) {
          return
        }

        setCoreError(
          {
            careerId,
            message:
              getRequestErrorMessage(
                requestError,
                (
                  'Unable to load '
                  + 'Skill Gap Analysis.'
                ),
              ),
          },
        )
      }
    }

    loadCoreData()

    return () => {
      isActive = false
    }
  }, [
    careerId,
    hasValidCareerId,
  ])


  useEffect(() => {
    if (
      !hasValidCareerId
      || !currentCoreState
    ) {
      return undefined
    }

    let isActive = true

    async function loadAISummary() {
      try {
        const response =
          await getSkillGapSummary(
            careerId,
          )

        if (!isActive) {
          return
        }

        setAiState(
          {
            careerId,
            data:
              response?.data
              || null,
            error: '',
          },
        )
      } catch (
        requestError
      ) {
        if (!isActive) {
          return
        }

        setAiState(
          {
            careerId,
            data: null,
            error:
              getRequestErrorMessage(
                requestError,
                (
                  'AI Gap Summary is '
                  + 'temporarily unavailable.'
                ),
              ),
          },
        )
      }
    }

    loadAISummary()

    return () => {
      isActive = false
    }
  }, [
    careerId,
    hasValidCareerId,
    currentCoreState,
  ])


  function openLearningSuggestions() {
    document
      .getElementById(
        'skill-gap-learning-suggestions',
      )
      ?.scrollIntoView(
        {
          behavior: 'smooth',
          block: 'start',
        },
      )
  }


  function handleRequirementAction(
    requirement,
  ) {
    if (
      skillsWithResources.has(
        requirement.skill_id,
      )
    ) {
      openLearningSuggestions()
      return
    }

    navigate(
      '/profile',
    )
  }


  if (isCareerContextLoading) {
    return (
      <main className="career-guidance-page skill-gap-figma">
        <header className="career-guidance-heading">
          <div className="career-guidance-heading__copy">
            <h1>
              Skill Gap Analysis
            </h1>

            <p>
              Compare readiness and skill gaps
              for your selected career.
            </p>
          </div>
        </header>

        <section className="skill-gap-figma__state-card">
          <span className="skill-gap-figma__pill skill-gap-figma__pill--neutral">
            Loading career
          </span>

          <h2>
            Loading your career focus
          </h2>

          <p>
            GradNavi is opening your saved career
            selection or your top recommendation.
          </p>
        </section>
      </main>
    )
  }


  if (!hasValidCareerId) {
    return (
      <main className="career-guidance-page skill-gap-figma">
        <header className="career-guidance-heading">
          <div className="career-guidance-heading__copy">
            <h1>
              Skill Gap Analysis
            </h1>

            <p>
              Compare readiness and skill gaps
              for your selected career.
            </p>
          </div>
        </header>

        <section className="skill-gap-figma__state-card">
          <span className="skill-gap-figma__pill skill-gap-figma__pill--amber">
            Career matches needed
          </span>

          <h2>
            No career match is available yet
          </h2>

          <p role="alert">
            {
              careerContextError
              || (
                'Complete your profile and review '
                + 'Career Recommendations first.'
              )
            }
          </p>

          <button
            className="skill-gap-figma__button skill-gap-figma__button--primary"
            type="button"
            onClick={() =>
              navigate(
                '/career-recommendations',
              )
            }
          >
            Open Career Recommendations
          </button>
        </section>
      </main>
    )
  }


  if (isLoading) {
    return (
      <main className="career-guidance-page skill-gap-figma">
        <header className="career-guidance-heading">
          <div className="career-guidance-heading__copy">
            <h1>
              Skill Gap Analysis
            </h1>

            <p>
              Compare readiness and skill gaps
              for your selected career. Change
              careers here anytime.
            </p>
          </div>
        </header>

        <section className="skill-gap-figma__state-card">
          <span className="skill-gap-figma__pill skill-gap-figma__pill--neutral">
            Loading readiness
          </span>

          <h2>
            Analysing your selected career
          </h2>

          <p>
            GradNavi is loading the deterministic
            readiness calculation and learning data.
          </p>
        </section>
      </main>
    )
  }


  if (
    currentCoreError
  ) {
    return (
      <main className="career-guidance-page skill-gap-figma">
        <header className="career-guidance-heading">
          <div className="career-guidance-heading__copy">
            <h1>
              Skill Gap Analysis
            </h1>

            <p>
              Compare readiness and skill gaps
              for your selected career. Change
              careers here anytime.
            </p>
          </div>
        </header>

        <section className="skill-gap-figma__state-card">
          <span className="skill-gap-figma__pill skill-gap-figma__pill--red">
            Readiness unavailable
          </span>

          <h2>
            Skill Gap Analysis could not be loaded
          </h2>

          <p role="alert">
            {currentCoreError}
          </p>

          <div className="skill-gap-figma__button-row">
            <button
              className="skill-gap-figma__button skill-gap-figma__button--primary"
              type="button"
              onClick={() =>
                window.location.reload()
              }
            >
              Try Again
            </button>

            <button
              className="skill-gap-figma__button"
              type="button"
              onClick={() =>
                navigate(
                  '/career-recommendations',
                )
              }
            >
              Change Career
            </button>
          </div>
        </section>
      </main>
    )
  }


  if (!readinessData) {
    return null
  }


  return (
    <main className="career-guidance-page skill-gap-figma">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>
            Skill Gap Analysis
          </h1>

          <p>
            Review selected-career readiness,
            unresolved requirements, and
            backend-linked learning suggestions.
          </p>
        </div>

        <div
          className="career-guidance-account-pill"
          aria-label={
            `Signed in as ${accountName}`
          }
        >
          <span
            className="career-guidance-account-pill__avatar"
            aria-hidden="true"
          >
            {accountInitial}
          </span>

          <span>
            {accountName}
          </span>
        </div>
      </header>


      <section className="skill-gap-figma__section">
        <div className="skill-gap-figma__section-heading">
          <div>
            <h2>
              Career Focus
            </h2>

            <p>
              Your top recommendation is used by
              default. Your career choice stays
              consistent across guidance pages.
            </p>
          </div>
        </div>

        <CareerSelector
          careers={
            careerOptions
          }
          selectedCareerId={
            careerId
          }
          selectedCareerName={
            readinessData
              .career_name
          }
          helperText={
            (
              'Changing your career refreshes '
              + 'this Skill Gap Analysis.'
            )
          }
          onChange={
            selectCareer
          }
        />
      </section>


      <section className="skill-gap-figma__section">
        <div className="skill-gap-figma__section-heading">
          <div>
            <h2>
              Readiness Overview
            </h2>

            <p>
              Readiness compares your profile evidence
              with source-backed career requirements.
              It is separate from Career Match %.
            </p>
          </div>
        </div>

        <div className="skill-gap-figma__metrics">
          <article className="skill-gap-figma__metric">
            <span className="skill-gap-figma__pill skill-gap-figma__pill--teal">
              Readiness
            </span>

            <span className="skill-gap-figma__metric-label">
              Readiness Score
            </span>

            <strong>
              {
                formatPercentage(
                  readinessData
                    .readiness_score,
                )
              }
            </strong>

            <small>
              Deterministic career readiness
            </small>
          </article>

          <article className="skill-gap-figma__metric">
            <span className="skill-gap-figma__pill skill-gap-figma__pill--green">
              Evidence
            </span>

            <span className="skill-gap-figma__metric-label">
              Matched
            </span>

            <strong>
              {matchedCount}
            </strong>

            <small>
              Meets requirement
            </small>
          </article>

          <article className="skill-gap-figma__metric">
            <span className="skill-gap-figma__pill skill-gap-figma__pill--amber">
              Development
            </span>

            <span className="skill-gap-figma__metric-label">
              Partially Matched
            </span>

            <strong>
              {partialCount}
            </strong>

            <small>
              Below requirement
            </small>
          </article>

          <article className="skill-gap-figma__metric">
            <span className="skill-gap-figma__pill skill-gap-figma__pill--red">
              Gap
            </span>

            <span className="skill-gap-figma__metric-label">
              Missing
            </span>

            <strong>
              {missingCount}
            </strong>

            <small>
              No profile evidence
            </small>
          </article>
        </div>

        <div className="skill-gap-figma__overview-meta">
          <span>
            {
              readinessData
                .total_requirement_count
            } total requirements
          </span>

          <span>
            {unresolvedCount} unresolved
          </span>

          <span>
            Status: {
              formatStatus(
                readinessData
                  .score_status,
              )
            }
          </span>
        </div>
      </section>


      <section className="skill-gap-figma__section skill-gap-figma__ai-section">
        <div className="skill-gap-figma__section-heading skill-gap-figma__section-heading--with-badge">
          <div>
            <h2>
              AI Gap Summary
            </h2>

            <p>
              AI explains the deterministic readiness
              result. It does not calculate or alter
              scores, requirement statuses, or priorities.
            </p>
          </div>

          <span className="skill-gap-figma__pill skill-gap-figma__pill--blue">
            AI explanation
          </span>
        </div>

        {isAILoading ? (
          <div className="skill-gap-figma__ai-loading">
            Generating AI Gap Summary...
          </div>
        ) : currentAIState?.error ? (
          <div className="skill-gap-figma__ai-unavailable">
            <strong>
              AI summary temporarily unavailable
            </strong>

            <p>
              {currentAIState.error}
              {' '}
              Your deterministic readiness details
              remain available below.
            </p>
          </div>
        ) : aiSummary ? (
          <div className="skill-gap-figma__ai-grid">
            <div className="skill-gap-figma__ai-explanation">
              <h3>
                Why your readiness is at this level
              </h3>

              <p>
                {
                  aiSummary
                    .readiness_explanation
                }
              </p>
            </div>

            <div className="skill-gap-figma__ai-subsection">
              <h3>
                Fix first
              </h3>

              <div className="skill-gap-figma__chip-row">
                {fixFirst.map(
                  (item) => (
                    <span
                      key={item.skill_id}
                      className="skill-gap-figma__pill skill-gap-figma__pill--amber"
                    >
                      {item.skill_name}
                    </span>
                  ),
                )}
              </div>
            </div>

            <div className="skill-gap-figma__ai-subsection">
              <h3>
                Recommended next steps
              </h3>

              {recommendedSteps.length > 0 ? (
                <ol className="skill-gap-figma__next-steps">
                  {recommendedSteps.map(
                    (step, index) => (
                      <li key={`${index}-${step}`}>
                        <span>
                          {index + 1}
                        </span>

                        <p>
                          {step}
                        </p>
                      </li>
                    ),
                  )}
                </ol>
              ) : (
                <p className="skill-gap-figma__muted">
                  No development actions are currently required.
                </p>
              )}
            </div>

            <div className="skill-gap-figma__ai-subsection">
              <div className="skill-gap-figma__ai-resource-heading">
                <div>
                  <h3>
                    Suggested learning resources
                  </h3>

                  <p>
                    Only controlled resources linked by
                    the GradNavi backend are shown.
                  </p>
                </div>

                <button
                  className="skill-gap-figma__button"
                  type="button"
                  onClick={
                    openLearningSuggestions
                  }
                >
                  View Learning Suggestions
                </button>
              </div>

              {previewResources.length > 0 ? (
                <div className="skill-gap-figma__compact-resource-list">
                  {previewResources.map(
                    (resource) => (
                      <span
                        key={resource.id}
                        className="skill-gap-figma__resource-chip"
                      >
                        {resource.title}
                      </span>
                    ),
                  )}
                </div>
              ) : (
                <p className="skill-gap-figma__empty-copy">
                  No controlled learning resources
                  are currently linked to these gaps.
                </p>
              )}
            </div>
          </div>
        ) : null}
      </section>


      <section className="skill-gap-figma__section">
        <div className="skill-gap-figma__section-heading">
          <div>
            <h2>
              Requirement Details
            </h2>

            <p>
              Review the complete source-backed requirement
              set used by the deterministic readiness calculation.
            </p>
          </div>
        </div>

        {requirements.length > 0 ? (
          <div className="skill-gap-figma__table-wrap">
            <table className="skill-gap-figma__table">
              <thead>
                <tr>
                  <th>
                    Requirement
                  </th>

                  <th>
                    Current evidence
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Required
                  </th>

                  <th>
                    Gap
                  </th>

                  <th>
                    Action
                  </th>
                </tr>
              </thead>

              <tbody>
                {requirements.map(
                  (requirement) => (
                    <tr
                      key={
                        requirement
                          .career_skill_id
                      }
                    >
                      <td>
                        <strong>
                          {
                            requirement
                              .skill_name
                          }
                        </strong>

                        <small>
                          {
                            formatStatus(
                              requirement
                                .concept_type,
                            )
                          }
                        </small>
                      </td>

                      <td>
                        <span>
                          {
                            formatProficiency(
                              requirement
                                .current_proficiency,
                            )
                          }
                        </span>

                        {
                          requirement
                            .current_proficiency
                        ? (
                          <small>
                            Score {
                              formatNumber(
                                requirement
                                  .current_score,
                              )
                            }
                          </small>
                        )
                        : null
                        }
                      </td>

                      <td>
                        <span
                          className={
                            getRequirementStatusClass(
                              requirement
                                .status,
                            )
                          }
                        >
                          {
                            formatStatus(
                              requirement
                                .status,
                            )
                          }
                        </span>
                      </td>

                      <td>
                        {
                          formatNumber(
                            requirement
                              .required_level,
                          )
                        }
                      </td>

                      <td>
                        {
                          formatNumber(
                            requirement
                              .gap_amount,
                          )
                        }
                      </td>

                      <td>
                        <button
                          className="skill-gap-figma__table-action"
                          type="button"
                          onClick={() =>
                            handleRequirementAction(
                              requirement,
                            )
                          }
                        >
                          {
                            getRequirementActionLabel(
                              requirement,
                              skillsWithResources,
                            )
                          }
                        </button>
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="skill-gap-figma__empty-state">
            <span className="skill-gap-figma__pill skill-gap-figma__pill--green">
              No unresolved gaps
            </span>

            <p>
              No source-backed requirements were returned
              for this selected career.
            </p>
          </div>
        )}
      </section>


      <section
        id="skill-gap-learning-suggestions"
        className="skill-gap-figma__section"
      >
        <div className="skill-gap-figma__section-heading">
          <div>
            <h2>
              Learning Suggestions
            </h2>

            <p>
              Resources are backend-linked to unresolved
              skills. GradNavi does not infer completion,
              rating, cost, or duration.
            </p>
          </div>
        </div>

        {previewResources.length > 0 ? (
          <div className="skill-gap-figma__resource-grid">
            {previewResources.map(
              (resource) => (
                <article
                  key={resource.id}
                  className="skill-gap-figma__resource-card"
                >
                  <h3>
                    {resource.title}
                  </h3>

                  <div className="skill-gap-figma__chip-row">
                    {
                      resource
                        .linked_skills
                        .slice(0, 2)
                        .map(
                          (skillName) => (
                            <span
                              key={skillName}
                              className="skill-gap-figma__pill skill-gap-figma__pill--neutral"
                            >
                              {skillName}
                            </span>
                          ),
                        )
                    }
                  </div>

                  <p>
                    {
                      resource.provider
                        ? `${resource.provider} · `
                        : ''
                    }
                    {
                      formatStatus(
                        resource
                          .resource_type,
                      )
                    }
                  </p>

                  {
                    resource.description
                    ? (
                      <p>
                        {
                          resource
                            .description
                        }
                      </p>
                    )
                    : null
                  }

                  <a
                    className="skill-gap-figma__button"
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open Resource
                  </a>
                </article>
              ),
            )}
          </div>
        ) : (
          <div className="skill-gap-figma__empty-state">
            <span className="skill-gap-figma__pill skill-gap-figma__pill--neutral">
              No linked resources
            </span>

            <h3>
              Learning resources are not available yet
            </h3>

            <p>
              No active controlled learning resources are
              currently linked to this career's unresolved
              requirements. GradNavi will not invent resource
              recommendations.
            </p>
          </div>
        )}
      </section>
    </main>
  )
}


export default SkillGapAnalysisPage
