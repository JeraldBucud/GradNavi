import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router'

import CareerSelector from '../components/career/CareerSelector'

import useCareerContext from '../hooks/useCareerContext'

import {
  getStoredUser,
} from '../services/authService'

import {
  completeRoadmapStep,
  getRoadmapOverview,
  startRoadmapStep,
} from '../services/careerService'

import './CareerGuidancePage.css'


const PRIORITY_STEP_COUNT = 3

const REMAINING_PREVIEW_COUNT = 6


function formatPercentage(
  value,
) {
  if (
    value === null
    || value === undefined
    || value === ''
  ) {
    return '—'
  }

  const numericValue =
    Number(
      value,
    )

  if (
    !Number.isFinite(
      numericValue,
    )
  ) {
    return '—'
  }

  const roundedValue =
    Math.round(
      numericValue * 10,
    ) / 10

  return `${roundedValue}%`
}


function formatStepNumber(
  value,
) {
  const numericValue =
    Number(
      value,
    )

  if (
    !Number.isInteger(
      numericValue,
    )
    || numericValue <= 0
  ) {
    return '—'
  }

  return String(
    numericValue,
  ).padStart(
    2,
    '0',
  )
}


function formatStatus(
  value,
) {
  if (!value) {
    return 'Not started'
  }

  return String(
    value,
  )
    .split('_')
    .map(
      (part) =>
        (
          part.charAt(0).toUpperCase()
          + part.slice(1)
        ),
    )
    .join(' ')
}


function getProgressClass(
  value,
) {
  if (
    value === 'completed'
  ) {
    return (
      'career-roadmap-figma__status '
      + 'career-roadmap-figma__status--complete'
    )
  }

  if (
    value === 'in_progress'
  ) {
    return (
      'career-roadmap-figma__status '
      + 'career-roadmap-figma__status--progress'
    )
  }

  return (
    'career-roadmap-figma__status '
    + 'career-roadmap-figma__status--todo'
  )
}


function getCurrentEvidence(
  step,
) {
  const proficiency =
    String(
      step
        ?.current_proficiency
      || '',
    ).trim()

  if (proficiency) {
    return formatStatus(
      proficiency,
    )
  }

  const currentScore =
    Number(
      step
        ?.current_score,
    )

  if (
    Number.isFinite(
      currentScore,
    )
    && currentScore > 0
  ) {
    return formatPercentage(
      currentScore,
    )
  }

  return 'Not yet added'
}


function getProgressActionLabel(
  status,
) {
  if (
    status === 'completed'
  ) {
    return 'Completed'
  }

  if (
    status === 'in_progress'
  ) {
    return 'Mark Complete'
  }

  return 'Start Step'
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
    details
    && typeof details === 'object'
  ) {
    const detailValues =
      Object.values(
        details,
      )

    for (
      const value
      of detailValues
    ) {
      if (
        Array.isArray(
          value,
        )
        && value.length > 0
      ) {
        return String(
          value[0],
        )
      }

      if (
        typeof value === 'string'
        && value.trim()
      ) {
        return value.trim()
      }
    }
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


async function fetchRoadmapData(
  careerId,
) {
  const response =
    await getRoadmapOverview(
      careerId,
    )

  return (
    response?.data
    || null
  )
}


function CareerRoadmapPage() {
  const navigate =
    useNavigate()

  const {
    careerOptions,
    error:
      careerContextError,
    isLoading:
      isCareerContextLoading,
    selectedCareer,
    selectedCareerId,
    selectCareer,
  } = useCareerContext()


  const [
    roadmapState,
    setRoadmapState,
  ] = useState(null)

  const [
    roadmapError,
    setRoadmapError,
  ] = useState(null)

  const [
    actionState,
    setActionState,
  ] = useState(null)

  const [
    showAllRemaining,
    setShowAllRemaining,
  ] = useState(false)


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


  const currentRoadmapData =
    (
      roadmapState
        ?.careerId
      === selectedCareerId
    )
      ? roadmapState.data
      : null


  const currentRoadmapError =
    (
      roadmapError
        ?.careerId
      === selectedCareerId
    )
      ? roadmapError.message
      : ''


  const roadmapSteps =
    useMemo(
      () => {
        const steps =
          currentRoadmapData
            ?.roadmap_steps

        return Array.isArray(
          steps,
        )
          ? steps
          : []
      },
      [
        currentRoadmapData,
      ],
    )


  const prioritySteps =
    roadmapSteps.slice(
      0,
      PRIORITY_STEP_COUNT,
    )


  const remainingSteps =
    roadmapSteps.slice(
      PRIORITY_STEP_COUNT,
    )


  const visibleRemainingSteps =
    showAllRemaining
      ? remainingSteps
      : remainingSteps.slice(
        0,
        REMAINING_PREVIEW_COUNT,
      )


  const progressSummary =
    currentRoadmapData
      ?.progress_summary
    || {
      total: 0,
      completed: 0,
      in_progress: 0,
      not_started: 0,
    }


  const nextStep =
    roadmapSteps.find(
      (step) =>
        step.progress_status
        !== 'completed',
    )
    || null


  const isRoadmapLoading =
    Boolean(
      selectedCareerId
      && !currentRoadmapData
      && !currentRoadmapError,
    )


  useEffect(
    () => {
      if (!selectedCareerId) {
        return undefined
      }

      let isActive = true

      async function loadRoadmap() {
        try {
          const data =
            await fetchRoadmapData(
              selectedCareerId,
            )

          if (!isActive) {
            return
          }

          setRoadmapState(
            {
              careerId:
                selectedCareerId,
              data,
            },
          )

          setRoadmapError(
            null,
          )
        } catch (
          requestError
        ) {
          if (!isActive) {
            return
          }

          setRoadmapError(
            {
              careerId:
                selectedCareerId,
              message:
                getRequestErrorMessage(
                  requestError,
                  (
                    'Unable to load your '
                    + 'Career Roadmap.'
                  ),
                ),
            },
          )
        }
      }

      void loadRoadmap()

      return () => {
        isActive = false
      }
    },
    [
      selectedCareerId,
    ],
  )


  function handleCareerChange(
    careerId,
  ) {
    setShowAllRemaining(
      false,
    )

    setActionState(
      null,
    )

    selectCareer(
      careerId,
    )
  }


  async function retryRoadmap() {
    if (!selectedCareerId) {
      return
    }

    setRoadmapError(
      null,
    )

    try {
      const data =
        await fetchRoadmapData(
          selectedCareerId,
        )

      setRoadmapState(
        {
          careerId:
            selectedCareerId,
          data,
        },
      )
    } catch (
      requestError
    ) {
      setRoadmapError(
        {
          careerId:
            selectedCareerId,
          message:
            getRequestErrorMessage(
              requestError,
              (
                'Unable to load your '
                + 'Career Roadmap.'
              ),
            ),
        },
      )
    }
  }


  async function handleProgressAction(
    step,
  ) {
    if (
      !selectedCareerId
      || !step?.skill_id
      || step.progress_status
        === 'completed'
    ) {
      return
    }

    const operation =
      step.progress_status
        === 'in_progress'
        ? 'complete'
        : 'start'

    setActionState(
      {
        careerId:
          selectedCareerId,
        skillId:
          step.skill_id,
        operation,
        pending: true,
        error: '',
      },
    )

    try {
      if (
        operation
        === 'complete'
      ) {
        await completeRoadmapStep(
          selectedCareerId,
          step.skill_id,
        )
      }
      else {
        await startRoadmapStep(
          selectedCareerId,
          step.skill_id,
        )
      }

      const refreshedData =
        await fetchRoadmapData(
          selectedCareerId,
        )

      setRoadmapState(
        {
          careerId:
            selectedCareerId,
          data:
            refreshedData,
        },
      )

      setRoadmapError(
        null,
      )

      setActionState(
        null,
      )
    } catch (
      requestError
    ) {
      setActionState(
        {
          careerId:
            selectedCareerId,
          skillId:
            step.skill_id,
          operation,
          pending: false,
          error:
            getRequestErrorMessage(
              requestError,
              (
                'Unable to update '
                + 'this roadmap step.'
              ),
            ),
        },
      )
    }
  }


  function openLearningResources(
    step,
  ) {
    if (
      !selectedCareerId
      || !step?.skill_id
    ) {
      return
    }

    navigate(
      (
        '/learning-resources'
        + `?career_id=${selectedCareerId}`
        + `&skill_id=${step.skill_id}`
      ),
    )
  }


  function openNextLearningResources() {
    if (!selectedCareerId) {
      return
    }

    const targetStep =
      nextStep
      || roadmapSteps[0]

    if (
      targetStep
        ?.skill_id
    ) {
      openLearningResources(
        targetStep,
      )

      return
    }

    navigate(
      (
        '/learning-resources'
        + `?career_id=${selectedCareerId}`
      ),
    )
  }


  function openSkillGaps() {
    if (!selectedCareerId) {
      return
    }

    navigate(
      (
        '/skill-gap-analysis'
        + `?career_id=${selectedCareerId}`
      ),
    )
  }


  if (isCareerContextLoading) {
    return (
      <main className="career-guidance-page career-roadmap-figma">
        <section
          className="career-guidance-loading-card"
          aria-live="polite"
          aria-busy="true"
        >
          <div
            className="career-guidance-loading-spinner"
            aria-hidden="true"
          />

          <div>
            <h1>
              Loading your Career Roadmap
            </h1>

            <p>
              GradNavi is opening your saved
              career selection or your top
              recommendation.
            </p>
          </div>
        </section>
      </main>
    )
  }


  if (!selectedCareerId) {
    return (
      <main className="career-guidance-page career-roadmap-figma">
        <header className="career-guidance-heading">
          <div className="career-guidance-heading__copy">
            <h1>
              Career Roadmap
            </h1>

            <p>
              Follow a step-by-step plan for
              your selected career.
            </p>
          </div>
        </header>

        <section className="career-guidance-state-card">
          <h2>
            Career matches are needed first
          </h2>

          <p role="alert">
            {
              careerContextError
              || (
                'Complete your profile and '
                + 'review Career Recommendations.'
              )
            }
          </p>

          <button
            className="gn-button gn-button--primary"
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


  return (
    <main className="career-guidance-page career-roadmap-figma">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>
            Career Roadmap
          </h1>

          <p>
            Follow a step-by-step plan for your
            selected career. Switch careers here
            anytime and keep the same context
            across your guidance pages.
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


      <section className="career-roadmap-figma__plan">
        <div className="career-roadmap-figma__section-heading">
          <h2>
            Your Career Plan
          </h2>

          <p>
            Your top recommendation loads by
            default. Your last career choice
            carries across Skill Gaps,
            Career Roadmap, and Learning Resources.
          </p>
        </div>

        <div className="career-roadmap-figma__plan-grid">
          <div className="career-roadmap-figma__career-card">
            <CareerSelector
              careers={
                careerOptions
              }
              label="Career"
              selectedCareerId={
                selectedCareerId
              }
              selectedCareerName={
                currentRoadmapData
                  ?.career_name
                || selectedCareer
                  ?.career_name
              }
              helperText={
                (
                  'Top match by default. '
                  + 'Change anytime.'
                )
              }
              onChange={
                handleCareerChange
              }
            />
          </div>

          <article className="career-roadmap-figma__metric">
            <span>
              Readiness score
            </span>

            <strong>
              {
                formatPercentage(
                  currentRoadmapData
                    ?.readiness_score,
                )
              }
            </strong>

            <small>
              Current readiness
            </small>
          </article>

          <article className="career-roadmap-figma__metric">
            <span>
              Roadmap progress
            </span>

            <strong>
              {
                `${progressSummary.completed}`
                + ` of ${progressSummary.total}`
              }
            </strong>

            <small>
              Steps completed
            </small>
          </article>

          <article className="career-roadmap-figma__metric">
            <span>
              Next priority
            </span>

            <strong>
              {
                nextStep
                  ? (
                    `Step ${
                      formatStepNumber(
                        nextStep
                          .step_number,
                      )
                    }`
                  )
                  : (
                    progressSummary.total > 0
                      ? 'Complete'
                      : '—'
                  )
              }
            </strong>

            <small>
              {
                nextStep
                  ?.skill_name
                || (
                  progressSummary.total > 0
                    ? 'Roadmap completed'
                    : 'No steps yet'
                )
              }
            </small>
          </article>
        </div>
      </section>


      {isRoadmapLoading && (
        <section
          className="career-guidance-loading-card"
          aria-live="polite"
          aria-busy="true"
        >
          <div
            className="career-guidance-loading-spinner"
            aria-hidden="true"
          />

          <div>
            <h2>
              Building your roadmap
            </h2>

            <p>
              GradNavi is loading readiness,
              progress, priorities, and
              personalised guidance for your
              selected career.
            </p>
          </div>
        </section>
      )}


      {currentRoadmapError && (
        <section className="career-guidance-state-card">
          <h2>
            Career Roadmap unavailable
          </h2>

          <p role="alert">
            {currentRoadmapError}
          </p>

          <div className="career-guidance-actions">
            <button
              className="gn-button gn-button--primary"
              type="button"
              onClick={
                retryRoadmap
              }
            >
              Try Again
            </button>

            <button
              className="gn-button"
              type="button"
              onClick={
                openSkillGaps
              }
            >
              View Skill Gaps
            </button>
          </div>
        </section>
      )}


      {currentRoadmapData && (
        <>
          <section className="career-roadmap-figma__progress">
            <div className="career-roadmap-figma__section-heading">
              <h2>
                Your Progress
              </h2>

              <p>
                Track each step as you work
                through your plan. Readiness
                changes when you add new profile
                evidence and run Skill Gap
                Analysis again.
              </p>
            </div>

            <div className="career-roadmap-figma__progress-pills">
              <span className="career-roadmap-figma__progress-pill career-roadmap-figma__progress-pill--complete">
                {
                  progressSummary
                    .completed
                } completed
              </span>

              <span className="career-roadmap-figma__progress-pill career-roadmap-figma__progress-pill--progress">
                {
                  progressSummary
                    .in_progress
                } in progress
              </span>

              <span className="career-roadmap-figma__progress-pill">
                {
                  progressSummary
                    .not_started
                } to do
              </span>

              <span className="career-roadmap-figma__progress-pill career-roadmap-figma__progress-pill--next">
                {
                  nextStep
                    ? (
                      `Next: Step ${
                        formatStepNumber(
                          nextStep
                            .step_number,
                        )
                      }`
                    )
                    : 'All steps complete'
                }
              </span>
            </div>

            {
              currentRoadmapData
                ?.guidance
                ?.fallback
              && (
                <p className="career-roadmap-figma__guidance-note">
                  Personalised guidance is using
                  standard guidance right now.
                  Your roadmap order, readiness,
                  and progress are unchanged.
                </p>
              )
            }
          </section>


          {roadmapSteps.length === 0 ? (
            <section className="career-guidance-state-card">
              <h2>
                No roadmap steps are available yet
              </h2>

              <p>
                Review Skill Gap Analysis or add
                more profile evidence for this
                career.
              </p>

              <div className="career-guidance-actions">
                <button
                  className="gn-button gn-button--primary"
                  type="button"
                  onClick={
                    openSkillGaps
                  }
                >
                  View Skill Gaps
                </button>

                <button
                  className="gn-button"
                  type="button"
                  onClick={() =>
                    navigate(
                      '/profile',
                    )
                  }
                >
                  Update Profile
                </button>
              </div>
            </section>
          ) : (
            <>
              <section className="career-roadmap-figma__priority-section">
                <div className="career-roadmap-figma__section-heading">
                  <h2>
                    Start with these priorities
                  </h2>

                  <p>
                    Based on your profile and
                    current skill gaps, these are
                    the highest-priority areas to
                    work on first.
                  </p>
                </div>

                <div className="career-roadmap-figma__priority-list">
                  {
                    prioritySteps.map(
                      (step) => {
                        const stepActionState =
                          (
                            actionState
                              ?.careerId
                            === selectedCareerId
                            && actionState
                              ?.skillId
                            === step.skill_id
                          )
                            ? actionState
                            : null

                        const isActionPending =
                          Boolean(
                            stepActionState
                              ?.pending,
                          )

                        const actionLabel =
                          isActionPending
                            ? (
                              stepActionState
                                ?.operation
                              === 'complete'
                                ? 'Completing...'
                                : 'Starting...'
                            )
                            : (
                              getProgressActionLabel(
                                step.progress_status,
                              )
                            )

                        return (
                          <article
                            key={
                              step.skill_id
                            }
                            className="career-roadmap-figma__step-card"
                          >
                            <div className="career-roadmap-figma__step-header">
                              <span className="career-roadmap-figma__step-number">
                                Step {
                                  formatStepNumber(
                                    step.step_number,
                                  )
                                }
                              </span>

                              <h3>
                                {
                                  step
                                    .skill_name
                                }
                              </h3>

                              <span
                                className={
                                  getProgressClass(
                                    step.progress_status,
                                  )
                                }
                              >
                                {
                                  formatStatus(
                                    step.progress_status,
                                  )
                                }
                              </span>
                            </div>

                            <div className="career-roadmap-figma__step-metrics">
                              <div>
                                <span>
                                  Your evidence
                                </span>

                                <strong>
                                  {
                                    getCurrentEvidence(
                                      step,
                                    )
                                  }
                                </strong>
                              </div>

                              <div>
                                <span>
                                  Career target
                                </span>

                                <strong>
                                  {
                                    formatPercentage(
                                      step.required_level,
                                    )
                                  }
                                </strong>
                              </div>

                              <div>
                                <span>
                                  Gap
                                </span>

                                <strong>
                                  {
                                    formatPercentage(
                                      step.gap_amount,
                                    )
                                  }
                                </strong>
                              </div>

                              <div>
                                <span>
                                  Priority
                                </span>

                                <strong>
                                  {
                                    formatPercentage(
                                      step.importance,
                                    )
                                  }
                                </strong>
                              </div>
                            </div>

                            <div className="career-roadmap-figma__guidance-grid">
                              <div>
                                <h4>
                                  Why this matters for you
                                </h4>

                                <p>
                                  {
                                    step
                                      .why_this_matters
                                    || (
                                      'Personalised explanation '
                                      + 'is unavailable for this step.'
                                    )
                                  }
                                </p>
                              </div>

                              <div>
                                <h4>
                                  Your focus
                                </h4>

                                <p>
                                  {
                                    step
                                      .your_focus
                                    || (
                                      'Use the gap, target, and '
                                      + 'learning resources to guide '
                                      + 'your work on this step.'
                                    )
                                  }
                                </p>
                              </div>
                            </div>

                            <div className="career-roadmap-figma__step-actions">
                              <button
                                className="gn-button gn-button--primary"
                                type="button"
                                disabled={
                                  isActionPending
                                  || step
                                    .progress_status
                                    === 'completed'
                                }
                                onClick={() =>
                                  handleProgressAction(
                                    step,
                                  )
                                }
                              >
                                {actionLabel}
                              </button>

                              <button
                                className="gn-button"
                                type="button"
                                onClick={() =>
                                  openLearningResources(
                                    step,
                                  )
                                }
                              >
                                View Learning Resources
                              </button>
                            </div>

                            {
                              stepActionState
                                ?.error
                              && (
                                <p
                                  className="career-roadmap-figma__action-error"
                                  role="alert"
                                >
                                  {
                                    stepActionState
                                      .error
                                  }
                                </p>
                              )
                            }
                          </article>
                        )
                      },
                    )
                  }
                </div>
              </section>


              {remainingSteps.length > 0 && (
                <section className="career-roadmap-figma__remaining-section">
                  <div className="career-roadmap-figma__section-heading">
                    <h2>
                      Coming up next
                    </h2>

                    <p>
                      After your top priorities,
                      continue with these
                      development areas. Start any
                      step when you are ready.
                    </p>
                  </div>

                  <div className="career-roadmap-figma__remaining-list">
                    {
                      visibleRemainingSteps.map(
                        (step) => {
                          const stepActionState =
                            (
                              actionState
                                ?.careerId
                              === selectedCareerId
                              && actionState
                                ?.skillId
                              === step.skill_id
                            )
                              ? actionState
                              : null

                          const isActionPending =
                            Boolean(
                              stepActionState
                                ?.pending,
                            )

                          return (
                            <article
                              key={
                                step.skill_id
                              }
                              className="career-roadmap-figma__remaining-row"
                            >
                              <span className="career-roadmap-figma__remaining-number">
                                {
                                  formatStepNumber(
                                    step.step_number,
                                  )
                                }
                              </span>

                              <div className="career-roadmap-figma__remaining-skill">
                                <strong>
                                  {
                                    step
                                      .skill_name
                                  }
                                </strong>

                                <small>
                                  Target {
                                    formatPercentage(
                                      step.required_level,
                                    )
                                  }
                                </small>
                              </div>

                              <span
                                className={
                                  getProgressClass(
                                    step.progress_status,
                                  )
                                }
                              >
                                {
                                  formatStatus(
                                    step.progress_status,
                                  )
                                }
                              </span>

                              <span className="career-roadmap-figma__remaining-step">
                                Step {
                                  formatStepNumber(
                                    step.step_number,
                                  )
                                }
                              </span>

                              <button
                                className="career-roadmap-figma__compact-action career-roadmap-figma__compact-action--primary"
                                type="button"
                                disabled={
                                  isActionPending
                                  || step
                                    .progress_status
                                    === 'completed'
                                }
                                onClick={() =>
                                  handleProgressAction(
                                    step,
                                  )
                                }
                              >
                                {
                                  isActionPending
                                    ? 'Updating...'
                                    : (
                                      getProgressActionLabel(
                                        step.progress_status,
                                      )
                                    )
                                }
                              </button>

                              <button
                                className="career-roadmap-figma__compact-action"
                                type="button"
                                onClick={() =>
                                  openLearningResources(
                                    step,
                                  )
                                }
                              >
                                Learning Resources
                              </button>

                              {
                                stepActionState
                                  ?.error
                                && (
                                  <p
                                    className="career-roadmap-figma__remaining-error"
                                    role="alert"
                                  >
                                    {
                                      stepActionState
                                        .error
                                    }
                                  </p>
                                )
                              }
                            </article>
                          )
                        },
                      )
                    }
                  </div>

                  {
                    remainingSteps.length
                    > REMAINING_PREVIEW_COUNT
                    && (
                      <div className="career-roadmap-figma__show-more">
                        <button
                          className="gn-button"
                          type="button"
                          onClick={() =>
                            setShowAllRemaining(
                              (current) =>
                                !current,
                            )
                          }
                        >
                          {
                            showAllRemaining
                              ? 'Show fewer steps'
                              : 'Show all remaining steps'
                          }
                        </button>

                        <span>
                          {
                            showAllRemaining
                              ? (
                                `${remainingSteps.length} `
                                + 'remaining steps shown'
                              )
                              : (
                                `${
                                  remainingSteps.length
                                  - visibleRemainingSteps.length
                                } more steps available`
                              )
                          }
                        </span>
                      </div>
                    )
                  }
                </section>
              )}


              <section className="career-roadmap-figma__next-actions">
                <div className="career-roadmap-figma__section-heading">
                  <h2>
                    Keep moving
                  </h2>

                  <p>
                    Continue your priority step,
                    open learning resources for
                    your selected career, or
                    review the underlying
                    Skill Gaps.
                  </p>
                </div>

                <div className="career-roadmap-figma__next-action-row">
                  <button
                    className="gn-button gn-button--primary"
                    type="button"
                    onClick={
                      openNextLearningResources
                    }
                  >
                    Open Learning Resources
                  </button>

                  <button
                    className="gn-button"
                    type="button"
                    onClick={
                      openSkillGaps
                    }
                  >
                    View Skill Gaps
                  </button>

                  <button
                    className="gn-button"
                    type="button"
                    onClick={() =>
                      navigate(
                        '/profile',
                      )
                    }
                  >
                    Update Profile
                  </button>

                  <p>
                    Roadmap progress does not
                    change readiness. New profile
                    evidence does.
                  </p>
                </div>
              </section>
            </>
          )}
        </>
      )}
    </main>
  )
}


export default CareerRoadmapPage
