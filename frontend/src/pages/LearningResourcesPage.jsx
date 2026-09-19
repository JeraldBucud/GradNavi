import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  useNavigate,
  useSearchParams,
} from 'react-router'

import CareerSelector from '../components/career/CareerSelector'

import useCareerContext from '../hooks/useCareerContext'

import {
  getStoredUser,
} from '../services/authService'

import {
  getLearningResourceRecommendations,
  getRoadmapOverview,
  reportLearningResource,
  setLearningResourceFeedback,
} from '../services/careerService'

import './CareerGuidancePage.css'


const DEFAULT_VISIBLE_RESOURCE_COUNT = 6

const PRIORITY_FOCUS_COUNT = 3


const REPORT_REASONS = [
  {
    value: 'broken_link',
    label: 'Broken link',
  },
  {
    value: 'outdated',
    label: 'Outdated',
  },
  {
    value: 'not_relevant',
    label: 'Not relevant',
  },
  {
    value: 'too_difficult',
    label: 'Too difficult',
  },
  {
    value: 'requires_payment',
    label: 'Unexpected payment',
  },
  {
    value: 'duplicate',
    label: 'Duplicate resource',
  },
  {
    value: 'other',
    label: 'Other',
  },
]


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

  const rounded =
    Math.round(
      numericValue * 10,
    ) / 10

  return `${rounded}%`
}


function formatLabel(
  value,
) {
  if (!value) {
    return 'Unknown'
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


function formatCheckedDate(
  value,
) {
  if (!value) {
    return 'Check status unavailable'
  }

  const date =
    new Date(
      value,
    )

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return 'Check status unavailable'
  }

  return (
    'Checked '
    + new Intl.DateTimeFormat(
      'en-AU',
      {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      },
    ).format(
      date,
    )
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
    details
    && typeof details === 'object'
  ) {
    for (
      const value
      of Object.values(
        details,
      )
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


function getAccessClass(
  accessType,
) {
  if (
    accessType === 'free'
  ) {
    return (
      'learning-resources-figma__badge '
      + 'learning-resources-figma__badge--free'
    )
  }

  if (
    accessType === 'freemium'
  ) {
    return (
      'learning-resources-figma__badge '
      + 'learning-resources-figma__badge--freemium'
    )
  }

  if (
    accessType === 'paid'
  ) {
    return (
      'learning-resources-figma__badge '
      + 'learning-resources-figma__badge--paid'
    )
  }

  return (
    'learning-resources-figma__badge '
    + 'learning-resources-figma__badge--unknown'
  )
}


function LearningResourcesPage() {
  const navigate =
    useNavigate()

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams()

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
    resourceState,
    setResourceState,
  ] = useState(null)

  const [
    resourceError,
    setResourceError,
  ] = useState(null)

  const [
    showAllResources,
    setShowAllResources,
  ] = useState(false)

  const [
    feedbackState,
    setFeedbackState,
  ] = useState(null)

  const [
    reportResource,
    setReportResource,
  ] = useState(null)

  const [
    reportReason,
    setReportReason,
  ] = useState(
    'broken_link',
  )

  const [
    reportComment,
    setReportComment,
  ] = useState('')

  const [
    reportState,
    setReportState,
  ] = useState(null)

  const [
    reportedResourceIds,
    setReportedResourceIds,
  ] = useState([])


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


  const requestedSkillId =
    Number(
      searchParams.get(
        'skill_id',
      ),
    )


  const selectedSkill =
    useMemo(
      () => {
        if (
          Number.isInteger(
            requestedSkillId,
          )
          && requestedSkillId > 0
        ) {
          const requested =
            roadmapSteps.find(
              (step) =>
                Number(
                  step.skill_id,
                )
                === requestedSkillId,
            )

          if (requested) {
            return requested
          }
        }

        return (
          roadmapSteps[0]
          || null
        )
      },
      [
        requestedSkillId,
        roadmapSteps,
      ],
    )


  const selectedSkillId =
    Number(
      selectedSkill
        ?.skill_id,
    )


  const currentResourceData =
    (
      resourceState
        ?.careerId
      === selectedCareerId
      && resourceState
        ?.skillId
      === selectedSkillId
    )
      ? resourceState.data
      : null


  const currentResourceError =
    (
      resourceError
        ?.careerId
      === selectedCareerId
      && resourceError
        ?.skillId
      === selectedSkillId
    )
      ? resourceError.message
      : ''


  const resources =
    useMemo(
      () => {
        const items =
          currentResourceData
            ?.resources

        return Array.isArray(
          items,
        )
          ? items
          : []
      },
      [
        currentResourceData,
      ],
    )


  const initialVisibleCount =
    Math.min(
      Number(
        currentResourceData
          ?.initial_visible_count,
      )
      || DEFAULT_VISIBLE_RESOURCE_COUNT,
      resources.length,
    )


  const visibleResources =
    showAllResources
      ? resources
      : resources.slice(
        0,
        initialVisibleCount,
      )


  const priorityFocuses =
    roadmapSteps.slice(
      0,
      PRIORITY_FOCUS_COUNT,
    )


  const isRoadmapLoading =
    Boolean(
      selectedCareerId
      && !currentRoadmapData
      && !(
        roadmapError
          ?.careerId
        === selectedCareerId
      ),
    )


  const isResourceLoading =
    Boolean(
      selectedCareerId
      && selectedSkillId
      && !currentResourceData
      && !currentResourceError
    )


  useEffect(
    () => {
      if (!selectedCareerId) {
        return undefined
      }

      let isActive = true

      async function loadRoadmap() {
        try {
          const response =
            await getRoadmapOverview(
              selectedCareerId,
            )

          if (!isActive) {
            return
          }

          setRoadmapState(
            {
              careerId:
                selectedCareerId,
              data:
                response?.data
                || null,
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
                    'Unable to load '
                    + 'your learning needs.'
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


  useEffect(
    () => {
      if (
        !selectedCareerId
        || !selectedSkillId
      ) {
        return
      }

      const currentSkillId =
        Number(
          searchParams.get(
            'skill_id',
          ),
        )

      if (
        currentSkillId
        === selectedSkillId
      ) {
        return
      }

      const nextParams =
        new URLSearchParams(
          searchParams,
        )

      nextParams.set(
        'career_id',
        String(
          selectedCareerId,
        ),
      )

      nextParams.set(
        'skill_id',
        String(
          selectedSkillId,
        ),
      )

      setSearchParams(
        nextParams,
        {
          replace: true,
        },
      )
    },
    [
      searchParams,
      selectedCareerId,
      selectedSkillId,
      setSearchParams,
    ],
  )


  useEffect(
    () => {
      if (
        !selectedCareerId
        || !selectedSkillId
      ) {
        return undefined
      }

      let isActive = true

      async function loadResources() {
        try {
          const response =
            await getLearningResourceRecommendations(
              selectedCareerId,
              selectedSkillId,
            )

          if (!isActive) {
            return
          }

          setResourceState(
            {
              careerId:
                selectedCareerId,
              skillId:
                selectedSkillId,
              data:
                response?.data
                || null,
            },
          )

          setResourceError(
            null,
          )

          setShowAllResources(
            false,
          )
        } catch (
          requestError
        ) {
          if (!isActive) {
            return
          }

          setResourceError(
            {
              careerId:
                selectedCareerId,
              skillId:
                selectedSkillId,
              message:
                getRequestErrorMessage(
                  requestError,
                  (
                    'Unable to load '
                    + 'learning resources.'
                  ),
                ),
            },
          )
        }
      }

      void loadResources()

      return () => {
        isActive = false
      }
    },
    [
      selectedCareerId,
      selectedSkillId,
    ],
  )


  function changeCareer(
    careerId,
  ) {
    setResourceState(
      null,
    )

    setResourceError(
      null,
    )

    setShowAllResources(
      false,
    )

    setFeedbackState(
      null,
    )

    setReportResource(
      null,
    )

    selectCareer(
      careerId,
      {
        clearSkillId: true,
      },
    )
  }


  function changeLearningFocus(
    skillId,
  ) {
    const numericSkillId =
      Number(
        skillId,
      )

    if (
      !Number.isInteger(
        numericSkillId,
      )
      || numericSkillId <= 0
    ) {
      return
    }

    const nextParams =
      new URLSearchParams(
        searchParams,
      )

    nextParams.set(
      'career_id',
      String(
        selectedCareerId,
      ),
    )

    nextParams.set(
      'skill_id',
      String(
        numericSkillId,
      ),
    )

    setSearchParams(
      nextParams,
    )

    setShowAllResources(
      false,
    )

    setFeedbackState(
      null,
    )
  }


  async function retryResources() {
    if (
      !selectedCareerId
      || !selectedSkillId
    ) {
      return
    }

    setResourceError(
      null,
    )

    try {
      const response =
        await getLearningResourceRecommendations(
          selectedCareerId,
          selectedSkillId,
        )

      setResourceState(
        {
          careerId:
            selectedCareerId,
          skillId:
            selectedSkillId,
          data:
            response?.data
            || null,
        },
      )
    } catch (
      requestError
    ) {
      setResourceError(
        {
          careerId:
            selectedCareerId,
          skillId:
            selectedSkillId,
          message:
            getRequestErrorMessage(
              requestError,
              (
                'Unable to load '
                + 'learning resources.'
              ),
            ),
        },
      )
    }
  }


  async function submitFeedback(
    resource,
    feedbackType,
  ) {
    if (!resource?.id) {
      return
    }

    setFeedbackState(
      {
        resourceId:
          resource.id,
        pending: true,
        error: '',
      },
    )

    try {
      const response =
        await setLearningResourceFeedback(
          resource.id,
          feedbackType,
        )

      const updated =
        response?.data

      setResourceState(
        (current) => {
          if (
            !current
            || !updated
          ) {
            return current
          }

          return {
            ...current,
            data: {
              ...current.data,
              resources:
                current
                  .data
                  .resources
                  .map(
                    (item) =>
                      (
                        item.id
                        === resource.id
                      )
                        ? {
                          ...item,
                          student_feedback:
                            updated
                              .feedback_type,
                          helpful_count:
                            updated
                              .helpful_count,
                          not_helpful_count:
                            updated
                              .not_helpful_count,
                        }
                        : item,
                  ),
            },
          }
        },
      )

      setFeedbackState(
        null,
      )
    } catch (
      requestError
    ) {
      setFeedbackState(
        {
          resourceId:
            resource.id,
          pending: false,
          error:
            getRequestErrorMessage(
              requestError,
              (
                'Unable to save '
                + 'your feedback.'
              ),
            ),
        },
      )
    }
  }


  function openReport(
    resource,
  ) {
    setReportResource(
      resource,
    )

    setReportReason(
      'broken_link',
    )

    setReportComment('')

    setReportState(
      null,
    )
  }


  function closeReport() {
    setReportResource(
      null,
    )

    setReportReason(
      'broken_link',
    )

    setReportComment('')

    setReportState(
      null,
    )
  }


  async function submitReport(
    event,
  ) {
    event.preventDefault()

    if (!reportResource?.id) {
      return
    }

    setReportState(
      {
        pending: true,
        error: '',
      },
    )

    try {
      await reportLearningResource(
        {
          resourceId:
            reportResource.id,
          reason:
            reportReason,
          comment:
            reportComment.trim(),
        },
      )

      setReportedResourceIds(
        (current) => {
          if (
            current.includes(
              reportResource.id,
            )
          ) {
            return current
          }

          return [
            ...current,
            reportResource.id,
          ]
        },
      )

      setReportState(
        {
          pending: false,
          error: '',
          success: true,
        },
      )
    } catch (
      requestError
    ) {
      setReportState(
        {
          pending: false,
          error:
            getRequestErrorMessage(
              requestError,
              (
                'Unable to submit '
                + 'this report.'
              ),
            ),
          success: false,
        },
      )
    }
  }


  function openSkillGapAnalysis() {
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


  function openCareerRoadmap() {
    if (!selectedCareerId) {
      return
    }

    const skillPart =
      selectedSkillId
        ? (
          `&skill_id=${selectedSkillId}`
        )
        : ''

    navigate(
      (
        '/career-roadmap'
        + `?career_id=${selectedCareerId}`
        + skillPart
      ),
    )
  }


  if (isCareerContextLoading) {
    return (
      <main className="career-guidance-page learning-resources-figma">
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
              Loading Learning Resources
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
      <main className="career-guidance-page learning-resources-figma">
        <header className="career-guidance-heading">
          <div className="career-guidance-heading__copy">
            <h1>
              Learning Resources
            </h1>

            <p>
              Find resources for your selected
              career and current learning focus.
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
    <main className="career-guidance-page learning-resources-figma">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>
            Learning Resources
          </h1>

          <p>
            Find learning resources for your
            selected career and current learning
            focus. Change either here anytime.
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


      <section className="learning-resources-figma__plan">
        <div className="learning-resources-figma__section-heading">
          <h2>
            Your Learning Plan
          </h2>

          <p>
            Your top career match loads by
            default. Learning Focus starts with
            your highest-priority unresolved gap.
          </p>
        </div>

        <div className="learning-resources-figma__selector-grid">
          <div className="learning-resources-figma__selector-card">
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
                changeCareer
              }
            />
          </div>

          <label className="learning-resources-figma__selector-card learning-resources-figma__focus-selector">
            <span>
              Learning Focus
            </span>

            <select
              value={
                selectedSkillId
                || ''
              }
              disabled={
                roadmapSteps.length
                === 0
              }
              onChange={
                (event) =>
                  changeLearningFocus(
                    event.target.value,
                  )
              }
            >
              {
                roadmapSteps.length
                === 0
                  ? (
                    <option value="">
                      No unresolved gaps
                    </option>
                  )
                  : (
                    roadmapSteps.map(
                      (step) => (
                        <option
                          key={
                            step.skill_id
                          }
                          value={
                            step.skill_id
                          }
                        >
                          {
                            step.skill_name
                          }
                        </option>
                      ),
                    )
                  )
              }
            </select>

            <small>
              Highest-priority gap by default.
              Change anytime.
            </small>
          </label>
        </div>

        <div className="learning-resources-figma__plan-metrics">
          <article>
            <span>
              Learning needs
            </span>

            <strong>
              {
                roadmapSteps.length
              }
            </strong>

            <small>
              Unresolved requirements
            </small>
          </article>

          <article>
            <span>
              Recommended now
            </span>

            <strong>
              {
                Math.min(
                  resources.length,
                  DEFAULT_VISIBLE_RESOURCE_COUNT,
                )
              }
            </strong>

            <small>
              Strongest matches shown first
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
              Loading your learning needs
            </h2>

            <p>
              GradNavi is finding the unresolved
              gaps for your selected career.
            </p>
          </div>
        </section>
      )}


      {
        roadmapError
          ?.careerId
        === selectedCareerId
        && (
          <section className="career-guidance-state-card">
            <h2>
              Learning needs unavailable
            </h2>

            <p role="alert">
              {
                roadmapError
                  .message
              }
            </p>

            <button
              className="gn-button"
              type="button"
              onClick={
                openSkillGapAnalysis
              }
            >
              View Skill Gap Analysis
            </button>
          </section>
        )
      }


      {
        currentRoadmapData
        && roadmapSteps.length === 0
        && (
          <section className="career-guidance-state-card">
            <h2>
              No unresolved learning gaps
            </h2>

            <p>
              There are no roadmap learning needs
              available for this career right now.
            </p>

            <div className="career-guidance-actions">
              <button
                className="gn-button gn-button--primary"
                type="button"
                onClick={
                  openSkillGapAnalysis
                }
              >
                Review Skill Gap Analysis
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
        )
      }


      {roadmapSteps.length > 0 && (
        <section className="learning-resources-figma__needs">
          <div className="learning-resources-figma__section-heading">
            <h2>
              Your priority learning needs
            </h2>

            <p>
              Start with your highest-priority
              gap or choose another Learning Focus.
            </p>
          </div>

          <div className="learning-resources-figma__needs-list">
            {
              priorityFocuses.map(
                (
                  step,
                  index,
                ) => {
                  const isSelected =
                    Number(
                      step.skill_id,
                    )
                    === selectedSkillId

                  return (
                    <button
                      key={
                        step.skill_id
                      }
                      className={
                        (
                          'learning-resources-figma__need-row'
                          + (
                            isSelected
                              ? ' learning-resources-figma__need-row--selected'
                              : ''
                          )
                        )
                      }
                      type="button"
                      onClick={() =>
                        changeLearningFocus(
                          step.skill_id,
                        )
                      }
                    >
                      <span className="learning-resources-figma__need-number">
                        {
                          index + 1
                        }
                      </span>

                      <strong>
                        {
                          step
                            .skill_name
                        }
                      </strong>

                      <span>
                        {
                          formatLabel(
                            step
                              .gap_status,
                          )
                        }
                      </span>

                      <span>
                        Target {
                          formatPercentage(
                            step
                              .required_level,
                          )
                        }
                      </span>

                      <span>
                        Gap {
                          formatPercentage(
                            step
                              .gap_amount,
                          )
                        }
                      </span>

                      <span>
                        {
                          isSelected
                            ? (
                              `${resources.length} resource`
                              + (
                                resources.length
                                === 1
                                  ? ''
                                  : 's'
                              )
                            )
                            : 'Select focus'
                        }
                      </span>
                    </button>
                  )
                },
              )
            }
          </div>
        </section>
      )}


      {
        selectedSkillId
        && (
          <section className="learning-resources-figma__resources">
            <div className="learning-resources-figma__section-heading">
              <h2>
                Recommended resources for you
              </h2>

              <p>
                The strongest matches appear
                first. Show more reveals additional
                useful options when available,
                up to 12.
              </p>
            </div>

            <div className="learning-resources-figma__focus-toolbar">
              <span className="learning-resources-figma__focus-label">
                Learning focus:
              </span>

              <div
                className="learning-resources-figma__focus-chips"
                role="group"
                aria-label="Learning focus options"
              >
                {
                  priorityFocuses.map(
                    (step) => {
                      const isActive =
                        Number(
                          step.skill_id,
                        )
                        === selectedSkillId

                      return (
                        <button
                          key={
                            step.skill_id
                          }
                          type="button"
                          className={
                            (
                              'learning-resources-figma__focus-chip'
                              + (
                                isActive
                                  ? ' learning-resources-figma__focus-chip--active'
                                  : ''
                              )
                            )
                          }
                          aria-pressed={
                            isActive
                          }
                          onClick={() =>
                            changeLearningFocus(
                              step.skill_id,
                            )
                          }
                        >
                          {
                            step
                              .skill_name
                          }
                        </button>
                      )
                    },
                  )
                }
              </div>
            </div>


            {isResourceLoading && (
              <div
                className="career-guidance-loading-card"
                aria-live="polite"
                aria-busy="true"
              >
                <div
                  className="career-guidance-loading-spinner"
                  aria-hidden="true"
                />

                <div>
                  <h3>
                    Finding the strongest resources
                  </h3>

                  <p>
                    GradNavi is ranking learning
                    options for your current focus.
                  </p>
                </div>
              </div>
            )}


            {currentResourceError && (
              <div className="career-guidance-inline-state">
                <h3>
                  Resources unavailable
                </h3>

                <p role="alert">
                  {currentResourceError}
                </p>

                <button
                  className="gn-button gn-button--primary"
                  type="button"
                  onClick={
                    retryResources
                  }
                >
                  Try Again
                </button>
              </div>
            )}


            {
              currentResourceData
              && resources.length === 0
              && (
                <div className="career-guidance-inline-state">
                  <h3>
                    No resources are available yet
                  </h3>

                  <p>
                    No suitable learning resources
                    are available for this focus
                    right now. Choose another
                    Learning Focus or report back
                    later.
                  </p>
                </div>
              )
            }


            {
              resources.length > 0
              && (
                <>
                  <div className="learning-resources-figma__resource-grid">
                    {
                      visibleResources.map(
                        (resource) => {
                          const feedback =
                            (
                              feedbackState
                                ?.resourceId
                              === resource.id
                            )
                              ? feedbackState
                              : null

                          const wasReported =
                            reportedResourceIds
                              .includes(
                                resource.id,
                              )

                          return (
                            <article
                              key={
                                resource.id
                              }
                              className="learning-resources-figma__resource-card"
                            >
                              <h3>
                                {
                                  resource
                                    .title
                                }
                              </h3>

                              <p className="learning-resources-figma__provider">
                                {
                                  resource
                                    .provider
                                  || 'Resource provider'
                                }
                              </p>

                              <div className="learning-resources-figma__badges">
                                <span
                                  className={
                                    getAccessClass(
                                      resource
                                        .access_type,
                                    )
                                  }
                                >
                                  {
                                    formatLabel(
                                      resource
                                        .access_type,
                                    )
                                  }
                                </span>

                                <span className="learning-resources-figma__badge">
                                  {
                                    resource
                                      .source_type
                                    === 'discovered'
                                      ? 'Recommended'
                                      : 'Curated source'
                                  }
                                </span>
                              </div>

                              <p className="learning-resources-figma__skill">
                                For: {
                                  currentResourceData
                                    ?.skill
                                    ?.skill_name
                                  || selectedSkill
                                    ?.skill_name
                                }
                              </p>

                              <div className="learning-resources-figma__resource-meta">
                                <span>
                                  Type: {
                                    formatLabel(
                                      resource
                                        .resource_type,
                                    )
                                  }
                                </span>

                                <span>
                                  {
                                    formatCheckedDate(
                                      resource
                                        .last_checked_at,
                                    )
                                  }
                                </span>
                              </div>

                              {
                                resource
                                  .description
                                && (
                                  <p className="learning-resources-figma__description">
                                    {
                                      resource
                                        .description
                                    }
                                  </p>
                                )
                              }

                              <div className="learning-resources-figma__why">
                                <strong>
                                  Why this fits you
                                </strong>

                                <p>
                                  {
                                    resource
                                      .why_this_fits
                                    || (
                                      'This resource matches '
                                      + 'your selected learning focus.'
                                    )
                                  }
                                </p>
                              </div>

                              <div className="learning-resources-figma__resource-actions">
                                <a
                                  className="gn-button gn-button--primary"
                                  href={
                                    resource
                                      .url
                                  }
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  Open Resource
                                </a>

                                <button
                                  className={
                                    (
                                      'learning-resources-figma__feedback-button'
                                      + (
                                        resource
                                          .student_feedback
                                        === 'helpful'
                                          ? ' learning-resources-figma__feedback-button--active'
                                          : ''
                                      )
                                    )
                                  }
                                  type="button"
                                  disabled={
                                    feedback
                                      ?.pending
                                  }
                                  onClick={() =>
                                    submitFeedback(
                                      resource,
                                      'helpful',
                                    )
                                  }
                                >
                                  Helpful
                                </button>

                                <button
                                  className={
                                    (
                                      'learning-resources-figma__feedback-button'
                                      + (
                                        resource
                                          .student_feedback
                                        === 'not_helpful'
                                          ? ' learning-resources-figma__feedback-button--active'
                                          : ''
                                      )
                                    )
                                  }
                                  type="button"
                                  disabled={
                                    feedback
                                      ?.pending
                                  }
                                  onClick={() =>
                                    submitFeedback(
                                      resource,
                                      'not_helpful',
                                    )
                                  }
                                >
                                  Not useful
                                </button>

                                <button
                                  className="learning-resources-figma__report-button"
                                  type="button"
                                  onClick={() =>
                                    openReport(
                                      resource,
                                    )
                                  }
                                >
                                  Report issue
                                </button>
                              </div>

                              {
                                feedback
                                  ?.error
                                && (
                                  <p
                                    className="learning-resources-figma__error"
                                    role="alert"
                                  >
                                    {
                                      feedback
                                        .error
                                    }
                                  </p>
                                )
                              }

                              {
                                wasReported
                                && (
                                  <p className="learning-resources-figma__success">
                                    Thanks. This resource
                                    was sent for review.
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
                    resources.length
                    > initialVisibleCount
                    && (
                      <div className="learning-resources-figma__show-more">
                        <button
                          className="gn-button"
                          type="button"
                          onClick={() =>
                            setShowAllResources(
                              (current) =>
                                !current,
                            )
                          }
                        >
                          {
                            showAllResources
                              ? 'Show fewer resources'
                              : 'Show more resources'
                          }
                        </button>

                        <span>
                          {
                            showAllResources
                              ? (
                                `${resources.length} `
                                + 'resources shown'
                              )
                              : (
                                `${visibleResources.length} shown`
                                + ` of ${resources.length}`
                              )
                          }
                        </span>
                      </div>
                    )
                  }
                </>
              )
            }


            {
              currentResourceData
                ?.guidance
                ?.fallback
              && (
                <p className="learning-resources-figma__guidance-note">
                  Personalised explanations are
                  using standard guidance right
                  now. Resource ranking is
                  unchanged.
                </p>
              )
            }
          </section>
        )
      }


      <section className="learning-resources-figma__after">
        <div className="learning-resources-figma__section-heading">
          <h2>
            After you learn
          </h2>

          <p>
            Learning a skill does not change your
            readiness by itself. Add evidence to
            your profile, then run Skill Gap
            Analysis again to see what improved.
          </p>
        </div>

        <div className="learning-resources-figma__after-actions">
          <button
            className="gn-button gn-button--primary"
            type="button"
            onClick={() =>
              navigate(
                '/profile',
              )
            }
          >
            Update Student Profile
          </button>

          <button
            className="gn-button"
            type="button"
            onClick={
              openSkillGapAnalysis
            }
          >
            Review Skill Gap Analysis
          </button>

          <button
            className="gn-button"
            type="button"
            onClick={
              openCareerRoadmap
            }
          >
            View Career Roadmap
          </button>

          <p>
            Resource pricing and availability can
            change. Report a problem if a link is
            broken, outdated, or no longer matches
            the description.
          </p>
        </div>
      </section>


      {
        reportResource
        && (
          <div
            className="learning-resources-figma__modal-backdrop"
            role="presentation"
            onMouseDown={
              (event) => {
                if (
                  event.target
                  === event.currentTarget
                ) {
                  closeReport()
                }
              }
            }
          >
            <section
              className="learning-resources-figma__report-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="resource-report-title"
            >
              <h2 id="resource-report-title">
                Report a resource problem
              </h2>

              <p>
                Report an issue with {
                  reportResource
                    .title
                }. The resource will be reviewed.
              </p>

              {
                reportState
                  ?.success
                ? (
                  <>
                    <div className="learning-resources-figma__report-success">
                      Report submitted. Thanks for
                      helping keep resources useful.
                    </div>

                    <div className="learning-resources-figma__modal-actions">
                      <button
                        className="gn-button gn-button--primary"
                        type="button"
                        onClick={
                          closeReport
                        }
                      >
                        Close
                      </button>
                    </div>
                  </>
                )
                : (
                  <form
                    onSubmit={
                      submitReport
                    }
                  >
                    <label>
                      <span>
                        What is the problem?
                      </span>

                      <select
                        value={
                          reportReason
                        }
                        onChange={
                          (event) =>
                            setReportReason(
                              event
                                .target
                                .value,
                            )
                        }
                      >
                        {
                          REPORT_REASONS.map(
                            (reason) => (
                              <option
                                key={
                                  reason
                                    .value
                                }
                                value={
                                  reason
                                    .value
                                }
                              >
                                {
                                  reason
                                    .label
                                }
                              </option>
                            ),
                          )
                        }
                      </select>
                    </label>

                    <label>
                      <span>
                        Additional details
                      </span>

                      <textarea
                        value={
                          reportComment
                        }
                        maxLength={1000}
                        rows={4}
                        placeholder="Optional details"
                        onChange={
                          (event) =>
                            setReportComment(
                              event
                                .target
                                .value,
                            )
                        }
                      />
                    </label>

                    {
                      reportState
                        ?.error
                      && (
                        <p
                          className="learning-resources-figma__error"
                          role="alert"
                        >
                          {
                            reportState
                              .error
                          }
                        </p>
                      )
                    }

                    <div className="learning-resources-figma__modal-actions">
                      <button
                        className="gn-button"
                        type="button"
                        disabled={
                          reportState
                            ?.pending
                        }
                        onClick={
                          closeReport
                        }
                      >
                        Cancel
                      </button>

                      <button
                        className="gn-button gn-button--primary"
                        type="submit"
                        disabled={
                          reportState
                            ?.pending
                        }
                      >
                        {
                          reportState
                            ?.pending
                            ? 'Submitting...'
                            : 'Submit Report'
                        }
                      </button>
                    </div>
                  </form>
                )
              }
            </section>
          </div>
        )
      }
    </main>
  )
}


export default LearningResourcesPage
