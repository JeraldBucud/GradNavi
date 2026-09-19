import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router'

import {
  getStoredUser,
} from '../services/authService'

import {
  getCareerRecommendations,
  getLearningSuggestions,
  getTopMatchExplanation,
} from '../services/careerService'

import {
  getStoredCareerSelection,
  saveCareerSelection,
} from '../services/careerSelectionService'

import './CareerGuidancePage.css'


const OTHER_CAREER_COUNT = 6

const TOP_EVIDENCE_COUNT = 2


function formatScore(value) {
  if (
    value === null
    || value === undefined
    || value === ''
  ) {
    return '—'
  }

  const numericValue = Number(
    value,
  )

  if (!Number.isFinite(numericValue)) {
    return '—'
  }

  return `${Math.round(numericValue)}%`
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  return (
    requestError?.data?.error?.message
    || requestError?.message
    || fallbackMessage
  )
}


function getRankedRecommendations(
  recommendations,
) {
  if (!Array.isArray(recommendations)) {
    return []
  }

  return [
    ...recommendations,
  ].sort(
    (first, second) =>
      Number(first.rank || 9999)
      - Number(second.rank || 9999),
  )
}


function normalizeEvidence(items) {
  if (!Array.isArray(items)) {
    return []
  }

  const seen = new Set()

  return items.reduce(
    (normalizedItems, item) => {
      if (typeof item !== 'string') {
        return normalizedItems
      }

      const value = item.trim()

      if (!value) {
        return normalizedItems
      }

      const key = value.toLocaleLowerCase()

      if (seen.has(key)) {
        return normalizedItems
      }

      seen.add(key)

      normalizedItems.push(value)

      return normalizedItems
    },
    [],
  )
}


function getStrongestEvidence(
  recommendation,
) {
  const competencies =
    normalizeEvidence(
      recommendation
        ?.matched_competencies,
    )

  const technologies =
    normalizeEvidence(
      recommendation
        ?.matched_technologies,
    )

  return normalizeEvidence(
    [
      ...competencies,
      ...technologies,
    ],
  ).slice(
    0,
    TOP_EVIDENCE_COUNT,
  )
}


function getPriorityGap(
  recommendation,
) {
  const gaps =
    normalizeEvidence(
      recommendation
        ?.missing_competencies,
    )

  return gaps[0] || null
}


function getMatchExplanation(
  recommendation,
) {
  const explanation =
    recommendation
      ?.match_explanation

  if (
    typeof explanation === 'string'
    && explanation.trim()
  ) {
    return {
      text: explanation.trim(),
      available: true,
    }
  }

  return {
    text: (
      'AI explanation is temporarily unavailable. '
      + 'The strengths and priority gap below '
      + 'come from GradNavi\u2019s calculated '
      + 'recommendation evidence.'
    ),
    available: false,
  }
}


function CareerRecommendationsPage() {
  const navigate = useNavigate()

  const [
    recommendations,
    setRecommendations,
  ] = useState([])

  const [
    recommendationMeta,
    setRecommendationMeta,
  ] = useState(null)

  const [
    readinessByCareer,
    setReadinessByCareer,
  ] = useState({})

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    loadError,
    setLoadError,
  ] = useState('')

  const [
    showScoringDetails,
    setShowScoringDetails,
  ] = useState(false)

  const [
    failedExplanationCareerId,
    setFailedExplanationCareerId,
  ] = useState(null)

  const topExplanationRequestRef =
    useRef(null)


  const currentUser =
    getStoredUser()

  const accountName =
    currentUser?.first_name?.trim()
    || 'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()


  const rankedRecommendations =
    getRankedRecommendations(
      recommendations,
    )


  const topRecommendation =
    rankedRecommendations[0] || null

  const topRecommendationId =
    topRecommendation?.career_id ?? null

  const topRecommendationName =
    topRecommendation?.career_name ?? ''


  const otherRecommendations =
    rankedRecommendations.slice(
      1,
      1 + OTHER_CAREER_COUNT,
    )


  const topReadiness =
    topRecommendation
      ? (
        readinessByCareer[
          topRecommendation.career_id
        ] ?? null
      )
      : null


  const strongestEvidence =
    getStrongestEvidence(
      topRecommendation,
    )


  const priorityGap =
    getPriorityGap(
      topRecommendation,
    )


  const storedMatchExplanation =
    getMatchExplanation(
      topRecommendation,
    )

  const topExplanationFailed =
    failedExplanationCareerId
    === topRecommendationId

  const matchExplanation = {
    ...storedMatchExplanation,
    loading: Boolean(
      topRecommendationId
      && !storedMatchExplanation.available
      && !topExplanationFailed
    ),
    text: (
      topRecommendationId
      && !storedMatchExplanation.available
      && !topExplanationFailed
    )
      ? 'Generating AI explanation...'
      : storedMatchExplanation.text,
  }


  useEffect(
    () => {
      if (
        !topRecommendationId
        || !topRecommendationName
      ) {
        return
      }

      const storedSelection =
        getStoredCareerSelection()

      if (storedSelection) {
        return
      }

      saveCareerSelection(
        {
          career_id:
            topRecommendationId,
          career_name:
            topRecommendationName,
        },
      )
    },
    [
      topRecommendationId,
      topRecommendationName,
    ],
  )


  async function loadReadinessForCareers(
    recommendationItems,
  ) {
    const careersToLoad =
      recommendationItems.slice(
        0,
        1 + OTHER_CAREER_COUNT,
      )

    const readinessResults =
      await Promise.allSettled(
        careersToLoad.map(
          async (recommendation) => {
            const responseData =
              await getLearningSuggestions(
                recommendation.career_id,
              )

            return {
              careerId:
                recommendation.career_id,
              score:
                responseData
                  ?.data
                  ?.readiness_score
                ?? null,
            }
          },
        ),
      )


    const readinessMap = {}


    readinessResults.forEach(
      (result) => {
        if (
          result.status === 'fulfilled'
        ) {
          readinessMap[
            result.value.careerId
          ] = result.value.score
        }
      },
    )


    return readinessMap
  }


  async function fetchPageData() {
    const responseData =
      await getCareerRecommendations()

    const responseRecommendations =
      responseData
        ?.data
        ?.recommendations

    const safeRecommendations =
      Array.isArray(
        responseRecommendations,
      )
        ? responseRecommendations
        : []


    const readinessMap =
      await loadReadinessForCareers(
        getRankedRecommendations(
          safeRecommendations,
        ),
      )


    return {
      recommendations:
        safeRecommendations,
      meta:
        responseData?.data || null,
      readinessMap,
    }
  }


  useEffect(() => {
    let isActive = true


    async function loadInitialData() {
      try {
        const pageData =
          await fetchPageData()

        if (!isActive) {
          return
        }

        setRecommendations(
          pageData.recommendations,
        )

        setRecommendationMeta(
          pageData.meta,
        )

        setReadinessByCareer(
          pageData.readinessMap,
        )
      } catch (requestError) {
        if (!isActive) {
          return
        }

        setLoadError(
          getRequestErrorMessage(
            requestError,
            'Unable to load your career recommendations.',
          ),
        )
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }


    void loadInitialData()


    return () => {
      isActive = false
    }
  }, [])


  async function retryRecommendations() {
    try {
      setIsLoading(true)
      setLoadError('')

      const pageData =
        await fetchPageData()

      setRecommendations(
        pageData.recommendations,
      )

      setRecommendationMeta(
        pageData.meta,
      )

      setReadinessByCareer(
        pageData.readinessMap,
      )
    } catch (requestError) {
      setLoadError(
        getRequestErrorMessage(
          requestError,
          'Unable to load your career recommendations.',
        ),
      )
    } finally {
      setIsLoading(false)
    }
  }


  useEffect(() => {
    if (
      !topRecommendationId
      || storedMatchExplanation.available
      || topExplanationFailed
      || (
        topExplanationRequestRef.current
        === topRecommendationId
      )
    ) {
      return undefined
    }

    topExplanationRequestRef.current =
      topRecommendationId

    let isActive = true

    async function loadTopMatchExplanation() {
      try {
        const responseData =
          await getTopMatchExplanation()

        const explanationData =
          responseData?.data

        const explanation =
          explanationData
            ?.match_explanation

        if (!isActive) {
          return
        }

        if (
          explanationData?.career_id
            !== topRecommendationId
          || typeof explanation !== 'string'
          || !explanation.trim()
        ) {
          setFailedExplanationCareerId(
            topRecommendationId,
          )

          return
        }

        setRecommendations(
          (currentRecommendations) =>
            currentRecommendations.map(
              (recommendation) =>
                recommendation.career_id
                  === explanationData.career_id
                  ? {
                    ...recommendation,
                    match_explanation:
                      explanation.trim(),
                  }
                  : recommendation,
            ),
        )
      } catch {
        if (isActive) {
          setFailedExplanationCareerId(
            topRecommendationId,
          )
        }
      }
    }

    loadTopMatchExplanation()

    return () => {
      isActive = false
    }
  }, [
    storedMatchExplanation.available,
    topExplanationFailed,
    topRecommendationId,
  ])


  function rememberCareerSelection(
    careerId,
  ) {
    const selectedCareer =
      rankedRecommendations.find(
        (recommendation) =>
          Number(
            recommendation
              .career_id,
          )
          === Number(
            careerId,
          ),
      )

    if (!selectedCareer) {
      return null
    }

    return saveCareerSelection(
      {
        career_id:
          selectedCareer.career_id,
        career_name:
          selectedCareer.career_name,
      },
    )
  }


  function openSkillGapAnalysis(
    careerId,
  ) {
    if (
      !rememberCareerSelection(
        careerId,
      )
    ) {
      return
    }

    navigate(
      `/skill-gap-analysis?career_id=${careerId}`,
    )
  }


  function openCareerRoadmap(
    careerId,
  ) {
    if (
      !rememberCareerSelection(
        careerId,
      )
    ) {
      return
    }

    navigate(
      `/career-roadmap?career_id=${careerId}`,
    )
  }


  function openLearningResources(
    careerId,
  ) {
    if (
      !rememberCareerSelection(
        careerId,
      )
    ) {
      return
    }

    navigate(
      `/learning-resources?career_id=${careerId}`,
    )
  }


  function renderWeight(
    key,
  ) {
    const rawWeight =
      recommendationMeta
        ?.base_weights
        ?.[key]

    if (
      rawWeight === null
      || rawWeight === undefined
      || rawWeight === ''
    ) {
      return 'Not available'
    }

    const numericWeight =
      Number(rawWeight)

    if (!Number.isFinite(numericWeight)) {
      return String(rawWeight)
    }

    return `${Math.round(
      numericWeight * 100,
    )}%`
  }


  if (isLoading) {
    return (
      <main className="career-guidance-page career-recommendations-figma">
        <div className="career-recommendations-figma__content">
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
                Finding your career matches
              </h1>

              <p>
                GradNavi is reviewing your
                approved profile evidence,
                calculating career matches,
                and loading readiness scores.
              </p>
            </div>
          </section>
        </div>
      </main>
    )
  }


  return (
    <main className="career-guidance-page career-recommendations-figma">
      <div className="career-recommendations-figma__content">
        <header className="career-recommendations-figma__header">
          <div>
            <h1>
              Career Recommendations
            </h1>

            <p>
              Explore career matches from your
              approved profile. Your top match is
              used as the default career until you
              choose another.
            </p>
          </div>

          <div
            className="career-recommendations-figma__account"
            aria-label={
              `Signed in as ${accountName}`
            }
          >
            <span
              className="career-recommendations-figma__avatar"
              aria-hidden="true"
            >
              {accountInitial}
            </span>

            <span>
              {accountName}
            </span>
          </div>
        </header>


        {loadError ? (
          <section className="career-guidance-state-card">
            <h2>
              Recommendations unavailable
            </h2>

            <p role="alert">
              {loadError}
            </p>

            <button
              className="gn-button gn-button--primary"
              type="button"
              onClick={
                retryRecommendations
              }
            >
              Try Again
            </button>
          </section>
        ) : topRecommendation ? (
          <>
            <section className="career-recommendations-figma__model-summary">
              <h2>
                Why these careers match you
              </h2>

              <p>
                GradNavi compares your skills,
                experience, interests, and goals
                with each career. AI-assisted
                matching helps identify strong
                role fit beyond exact keyword
                matches.
              </p>

              <div className="career-recommendations-figma__model-summary-footer">
                <div className="career-recommendations-figma__summary-badges">
                  <span className="career-recommendations-figma__pill career-recommendations-figma__pill--blue">
                    Uses your profile
                  </span>

                  <span className="career-recommendations-figma__pill career-recommendations-figma__pill--blue">
                    AI-assisted matching
                  </span>
                </div>

                <button
                  className="career-recommendations-figma__scoring-link"
                  type="button"
                  aria-expanded={
                    showScoringDetails
                  }
                  onClick={() =>
                    setShowScoringDetails(
                      (current) => !current,
                    )
                  }
                >
                  How scoring works
                  <span aria-hidden="true">
                    {' '}›
                  </span>
                </button>
              </div>

              {showScoringDetails && (
                <div className="career-recommendations-figma__scoring-details">
                  <strong>
                    Current scoring model
                  </strong>

                  <span>
                    Skills &amp; Knowledge:{' '}
                    {renderWeight('competency')}
                  </span>

                  <span>
                    Technology:{' '}
                    {renderWeight('technology')}
                  </span>

                  <span>
                    Profile Alignment:{' '}
                    {renderWeight('semantic')}
                  </span>
                </div>
              )}
            </section>


            <section className="career-recommendations-figma__section">
              <div className="career-recommendations-figma__section-heading">
                <h2>
                  Top Match
                </h2>

                <p>
                  The strongest recommendation
                  comes first, with match evidence
                  and next action in one place.
                </p>
              </div>

              <article className="career-recommendations-figma__top-card">
                <div className="career-recommendations-figma__top-main">
                  <span className="career-recommendations-figma__rank-pill career-recommendations-figma__rank-pill--primary">
                    #{topRecommendation.rank || 1}
                  </span>

                  <h3>
                    {
                      topRecommendation
                        .career_name
                    }
                  </h3>

                  <div className="career-recommendations-figma__top-metrics">
                    <article className="career-recommendations-figma__metric-card">
                      <span className="career-recommendations-figma__pill career-recommendations-figma__pill--blue">
                        Career match
                      </span>

                      <small>
                        Career Match
                      </small>

                      <strong>
                        {formatScore(
                          topRecommendation
                            .recommendation_score,
                        )}
                      </strong>

                      <p>
                        AI-assisted score
                      </p>
                    </article>

                    <article className="career-recommendations-figma__metric-card">
                      <span className="career-recommendations-figma__pill career-recommendations-figma__pill--blue">
                        Readiness
                      </span>

                      <small>
                        Readiness
                      </small>

                      <strong>
                        {formatScore(
                          topReadiness,
                        )}
                      </strong>

                      <p>
                        Selected career
                      </p>
                    </article>
                  </div>
                </div>


                <div className="career-recommendations-figma__explanation-panel">
                  <h3>
                    Why this career matches
                  </h3>

                  <p className="career-recommendations-figma__explanation">
                    {matchExplanation.text}
                  </p>

                  <span
                    className={
                      matchExplanation.available
                        ? (
                          'career-recommendations-figma__pill '
                          + 'career-recommendations-figma__pill--teal'
                        )
                        : (
                          'career-recommendations-figma__pill '
                          + 'career-recommendations-figma__pill--neutral'
                        )
                    }
                  >
                    AI explanation
                  </span>

                  <div className="career-recommendations-figma__evidence-block">
                    <span className="career-recommendations-figma__evidence-label">
                      Strongest evidence
                    </span>

                    {strongestEvidence.length > 0 ? (
                      <div className="career-recommendations-figma__evidence-chips">
                        {strongestEvidence.map(
                          (item) => (
                            <span
                              key={item}
                              className="career-recommendations-figma__pill career-recommendations-figma__pill--green"
                            >
                              {item}
                            </span>
                          ),
                        )}
                      </div>
                    ) : (
                      <p className="career-recommendations-figma__empty-evidence">
                        No matched evidence
                        available.
                      </p>
                    )}
                  </div>

                  <div className="career-recommendations-figma__priority-gap-section">
                    <span className="career-recommendations-figma__evidence-label">
                      Priority gap
                    </span>

                    <div className="career-recommendations-figma__priority-gap">
                      {priorityGap ? (
                        <span className="career-recommendations-figma__pill career-recommendations-figma__pill--amber">
                          {priorityGap}
                        </span>
                      ) : (
                        <p className="career-recommendations-figma__empty-evidence">
                          No priority gap
                          identified.
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="career-recommendations-figma__top-actions career-recommendations-figma__top-actions--separate">
                    <button
                      className="gn-button gn-button--primary career-recommendations-figma__top-action"
                      type="button"
                      onClick={() =>
                        openSkillGapAnalysis(
                          topRecommendation
                            .career_id,
                        )
                      }
                    >
                      View Skill Gaps
                    </button>

                    <button
                      className="career-recommendations-figma__secondary-button"
                      type="button"
                      onClick={() =>
                        openCareerRoadmap(
                          topRecommendation
                            .career_id,
                        )
                      }
                    >
                      View Roadmap
                    </button>
                  </div>
                </div>
              </article>
            </section>


            <section className="career-recommendations-figma__section">
              <div className="career-recommendations-figma__section-heading">
                <h2>
                  Other Career Matches
                </h2>

                <p>
                  Match shows how closely each
                  career fits your profile.
                  Readiness shows how prepared
                  you are for that career today.
                </p>
              </div>

              <div className="career-recommendations-figma__career-grid">
                {otherRecommendations.map(
                  (recommendation) => {
                    const readiness =
                      readinessByCareer[
                        recommendation
                          .career_id
                      ]

                    const strongestEvidence =
                      getStrongestEvidence(
                        recommendation,
                      )

                    return (
                      <article
                        key={
                          recommendation
                            .career_id
                        }
                        className="career-recommendations-figma__career-card"
                      >
                        <div className="career-recommendations-figma__career-card-heading">
                          <h3>
                            {
                              recommendation
                                .career_name
                            }
                          </h3>

                          <span className="career-recommendations-figma__rank-pill">
                            #{recommendation.rank || '—'}
                          </span>
                        </div>

                        <div className="career-recommendations-figma__career-card-scores">
                          <span className="career-recommendations-figma__pill career-recommendations-figma__pill--blue">
                            Match{' '}
                            {formatScore(
                              recommendation
                                .recommendation_score,
                            )}
                          </span>

                          <span className="career-recommendations-figma__pill career-recommendations-figma__pill--blue">
                            Ready{' '}
                            {formatScore(
                              readiness,
                            )}
                          </span>
                        </div>

                        <div className="career-recommendations-figma__career-card-evidence">
                          <span className="career-recommendations-figma__evidence-label">
                            Strongest evidence
                          </span>

                          {strongestEvidence.length > 0 ? (
                            <div className="career-recommendations-figma__evidence-chips">
                              {strongestEvidence.map(
                                (item) => (
                                  <span
                                    key={item}
                                    className="career-recommendations-figma__pill career-recommendations-figma__pill--green"
                                  >
                                    {item}
                                  </span>
                                ),
                              )}
                            </div>
                          ) : (
                            <p className="career-recommendations-figma__empty-evidence">
                              No matched evidence available.
                            </p>
                          )}
                        </div>

                        <div className="career-recommendations-figma__career-card-actions">
                          <button
                            className="career-recommendations-figma__secondary-button"
                            type="button"
                            onClick={() =>
                              openSkillGapAnalysis(
                                recommendation.career_id,
                              )
                            }
                          >
                            View Skill Gaps
                          </button>

                          <button
                            className="career-recommendations-figma__secondary-button"
                            type="button"
                            onClick={() =>
                              openCareerRoadmap(
                                recommendation.career_id,
                              )
                            }
                          >
                            View Roadmap
                          </button>

                          <button
                            className="career-recommendations-figma__secondary-button career-recommendations-figma__resource-action"
                            type="button"
                            onClick={() =>
                              openLearningResources(
                                recommendation.career_id,
                              )
                            }
                          >
                            Learning Resources
                          </button>
                        </div>
                      </article>
                    )
                  },
                )}
              </div>
            </section>


            <section className="career-recommendations-figma__section career-recommendations-figma__actions-section">
              <div className="career-recommendations-figma__section-heading">
                <h2>
                  Recommended Next Actions
                </h2>

                <p>
                  Move from recommendation to
                  evidence improvement, readiness
                  review, and skill-gap action.
                </p>
              </div>

              <div className="career-recommendations-figma__action-list">
                <article className="career-recommendations-figma__action-row">
                  <strong>
                    Choose a top career to compare
                    skill gaps
                  </strong>

                  <button
                    className="career-recommendations-figma__secondary-button"
                    type="button"
                    onClick={() =>
                      openSkillGapAnalysis(
                        topRecommendation
                          .career_id,
                      )
                    }
                  >
                    View Skill Gaps
                  </button>
                </article>

                <article className="career-recommendations-figma__action-row">
                  <strong>
                    Update missing profile evidence
                  </strong>

                  <button
                    className="career-recommendations-figma__secondary-button"
                    type="button"
                    onClick={() =>
                      navigate('/profile')
                    }
                  >
                    Edit Profile
                  </button>
                </article>

                <article className="career-recommendations-figma__action-row">
                  <strong>
                    Review readiness for your
                    selected career
                  </strong>

                  <button
                    className="career-recommendations-figma__secondary-button"
                    type="button"
                    onClick={() =>
                      openSkillGapAnalysis(
                        topRecommendation
                          .career_id,
                      )
                    }
                  >
                    Open
                  </button>
                </article>

                <article className="career-recommendations-figma__action-row">
                  <strong>
                    Find learning resources for
                    your selected career
                  </strong>

                  <button
                    className="career-recommendations-figma__secondary-button"
                    type="button"
                    onClick={() =>
                      openLearningResources(
                        topRecommendation
                          .career_id,
                      )
                    }
                  >
                    Open Learning Resources
                  </button>
                </article>
              </div>
            </section>
          </>
        ) : (
          <section className="career-guidance-state-card">
            <h2>
              No career recommendations yet
            </h2>

            <p>
              Add information to your Student
              Profile so GradNavi has enough
              evidence to identify career
              matches.
            </p>

            <button
              className="gn-button gn-button--primary"
              type="button"
              onClick={() =>
                navigate('/profile')
              }
            >
              Go to Student Profile
            </button>
          </section>
        )}
      </div>
    </main>
  )
}


export default CareerRecommendationsPage
