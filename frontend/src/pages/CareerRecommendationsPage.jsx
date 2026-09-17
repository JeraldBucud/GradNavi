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

import {
  getCareerRecommendations,
} from '../services/careerService'

import './CareerGuidancePage.css'


const DEFAULT_OTHER_CAREER_COUNT = 5

const DEFAULT_EVIDENCE_COUNT = 5


function formatPercentage(value) {
  if (
    value === null
    || value === undefined
    || value === ''
  ) {
    return 'Not available'
  }

  const numericValue = Number(
    value,
  )

  if (
    !Number.isFinite(
      numericValue,
    )
  ) {
    return 'Not available'
  }

  const formattedValue =
    Number.isInteger(
      numericValue,
    )
      ? numericValue.toFixed(0)
      : numericValue.toFixed(1)

  return `${formattedValue}%`
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


function getTopRecommendation(
  recommendations,
) {
  return (
    recommendations.find(
      (recommendation) =>
        recommendation.rank === 1,
    )
    || recommendations[0]
    || null
  )
}


function getVisibleEvidence(
  items,
  showAll,
) {
  if (
    !Array.isArray(
      items,
    )
  ) {
    return []
  }

  if (showAll) {
    return items
  }

  return items.slice(
    0,
    DEFAULT_EVIDENCE_COUNT,
  )
}


function EvidenceGroup({
  title,
  items,
  showAll,
  onToggle,
  emptyMessage,
}) {
  const safeItems =
    Array.isArray(
      items,
    )
      ? items
      : []

  const visibleItems =
    getVisibleEvidence(
      safeItems,
      showAll,
    )

  return (
    <div className="career-guidance-evidence-group">
      <div className="career-guidance-evidence-group__heading">
        <dt>
          {title}
        </dt>

        <span>
          {safeItems.length}
        </span>
      </div>

      <dd>
        {visibleItems.length > 0 ? (
          <ul className="career-guidance-evidence-list">
            {visibleItems.map(
              (item) => (
                <li key={item}>
                  {item}
                </li>
              ),
            )}
          </ul>
        ) : (
          <p className="career-guidance-evidence-empty">
            {emptyMessage}
          </p>
        )}

        {safeItems.length >
          DEFAULT_EVIDENCE_COUNT && (
          <button
            className="career-guidance-link-button"
            type="button"
            onClick={onToggle}
          >
            {showAll
              ? 'Show top 5'
              : `View all ${safeItems.length}`}
          </button>
        )}
      </dd>
    </div>
  )
}


function CareerRecommendationsPage() {
  const navigate = useNavigate()

  const [
    recommendations,
    setRecommendations,
  ] = useState([])

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    loadError,
    setLoadError,
  ] = useState('')

  const [
    showAllCareers,
    setShowAllCareers,
  ] = useState(false)

  const [
    showAllMatchedCompetencies,
    setShowAllMatchedCompetencies,
  ] = useState(false)

  const [
    showAllMissingCompetencies,
    setShowAllMissingCompetencies,
  ] = useState(false)

  const [
    showAllMatchedTechnologies,
    setShowAllMatchedTechnologies,
  ] = useState(false)


  const currentUser =
    getStoredUser()

  const accountName =
    currentUser?.first_name?.trim()
    || 'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()


  const topRecommendation =
    getTopRecommendation(
      recommendations,
    )


  const otherRecommendations =
    recommendations.filter(
      (recommendation) =>
        recommendation.career_id
        !== topRecommendation?.career_id,
    )


  const visibleOtherRecommendations =
    showAllCareers
      ? otherRecommendations
      : otherRecommendations.slice(
          0,
          DEFAULT_OTHER_CAREER_COUNT,
        )


  useEffect(() => {
    let isActive = true

    async function loadInitialRecommendations() {
      try {
        const responseData =
          await getCareerRecommendations()

        if (!isActive) {
          return
        }

        const responseRecommendations =
          responseData
            ?.data
            ?.recommendations

        setRecommendations(
          Array.isArray(
            responseRecommendations,
          )
            ? responseRecommendations
            : [],
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
          setIsLoading(
            false,
          )
        }
      }
    }

    void loadInitialRecommendations()

    return () => {
      isActive = false
    }
  }, [])


  async function retryRecommendations() {
    try {
      setIsLoading(
        true,
      )

      setLoadError(
        '',
      )

      const responseData =
        await getCareerRecommendations()

      const responseRecommendations =
        responseData
          ?.data
          ?.recommendations

      setRecommendations(
        Array.isArray(
          responseRecommendations,
        )
          ? responseRecommendations
          : [],
      )
    } catch (requestError) {
      setLoadError(
        getRequestErrorMessage(
          requestError,
          'Unable to load your career recommendations.',
        ),
      )
    } finally {
      setIsLoading(
        false,
      )
    }
  }


  function openSkillGapAnalysis(
    careerId,
  ) {
    navigate(
      `/skill-gap-analysis?career_id=${careerId}`,
    )
  }


  if (isLoading) {
    return (
      <main className="career-guidance-page">
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
              GradNavi is reviewing your profile
              and comparing it with career
              requirements and role information.
            </p>

            <div className="career-guidance-loading-steps">
              <span>
                Reviewing your profile
              </span>

              <span>
                Comparing skills and knowledge
              </span>

              <span>
                Checking technology match
              </span>

              <span>
                Comparing your broader profile
              </span>
            </div>
          </div>
        </section>
      </main>
    )
  }


  return (
    <main className="career-guidance-page">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>
            Career Recommendations
          </h1>

          <p>
            Explore careers matched to your
            skills, experience, education,
            projects, and career goals.
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


      {loadError ? (
        <section
          className="career-guidance-state-card"
          aria-live="polite"
        >
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
      ) : (
        <>
          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  How GradNavi Finds Your Career Matches
                </h2>

                <p>
                  GradNavi compares different parts
                  of your profile with career
                  requirements and role information
                  to identify careers aligned with
                  your current background.
                </p>
              </div>
            </div>

            <div className="career-guidance-model-grid">
              <article className="career-guidance-model-card">
                <span>
                  Skills and Knowledge Match
                </span>

                <small>
                  How closely your current skills
                  and knowledge match the core
                  requirements of each career.
                </small>
              </article>

              <article className="career-guidance-model-card">
                <span>
                  Technology Match
                </span>

                <small>
                  How your technology skills compare
                  with tools and technologies linked
                  to each career.
                </small>
              </article>

              <article className="career-guidance-model-card">
                <span>
                  Profile Alignment
                </span>

                <small>
                  How your education, experience,
                  projects, skills, and goals align
                  with the career.
                </small>
              </article>
            </div>
          </section>


          {topRecommendation ? (
            <section className="career-guidance-section">
              <div className="career-guidance-section__heading">
                <div>
                  <h2>
                    Top Recommendation
                  </h2>

                  <p>
                    The career currently most
                    aligned with your profile.
                  </p>
                </div>
              </div>

              <div className="career-guidance-top-recommendation">
                <div className="career-guidance-top-recommendation__summary">
                  <div className="career-guidance-top-title">
                    <span className="gn-badge gn-badge--current">
                      #{topRecommendation.rank || 1}
                    </span>

                    <h3>
                      {
                        topRecommendation
                          .career_name
                      }
                    </h3>
                  </div>

                  <article className="career-guidance-final-score-card">
                    <span>
                      Career Match
                    </span>

                    <strong>
                      {formatPercentage(
                        topRecommendation
                          .recommendation_score,
                      )}
                    </strong>

                    <small>
                      Overall alignment with
                      your profile
                    </small>
                  </article>

                  <div className="career-guidance-component-grid">
                    <article className="career-guidance-component-card">
                      <span>
                        Skills and Knowledge
                      </span>

                      <strong>
                        {formatPercentage(
                          topRecommendation
                            .competency_score,
                        )}
                      </strong>

                      <small>
                        Based on core career
                        requirements
                      </small>
                    </article>

                    <article className="career-guidance-component-card">
                      <span>
                        Technology Match
                      </span>

                      <strong>
                        {formatPercentage(
                          topRecommendation
                            .technology_score,
                        )}
                      </strong>

                      <small>
                        {topRecommendation
                          .technology_active
                          ? (
                            'Technology evidence available'
                          )
                          : (
                            'Limited technology evidence'
                          )}
                      </small>
                    </article>

                    <article className="career-guidance-component-card">
                      <span>
                        Profile Alignment
                      </span>

                      <strong>
                        {formatPercentage(
                          topRecommendation
                            .semantic_alignment_score,
                        )}
                      </strong>

                      <small>
                        Based on your broader
                        profile
                      </small>
                    </article>
                  </div>
                </div>


                <article className="career-guidance-evidence-card">
                  <h3>
                    Why This Career Fits Your Profile
                  </h3>

                  <dl>
                    <EvidenceGroup
                      title={
                        'Skills and Knowledge You Already Match'
                      }
                      items={
                        topRecommendation
                          .matched_competencies
                      }
                      showAll={
                        showAllMatchedCompetencies
                      }
                      onToggle={() =>
                        setShowAllMatchedCompetencies(
                          (current) =>
                            !current,
                        )
                      }
                      emptyMessage={
                        'No matching core skills identified yet.'
                      }
                    />

                    <EvidenceGroup
                      title={
                        'Skills and Knowledge to Develop'
                      }
                      items={
                        topRecommendation
                          .missing_competencies
                      }
                      showAll={
                        showAllMissingCompetencies
                      }
                      onToggle={() =>
                        setShowAllMissingCompetencies(
                          (current) =>
                            !current,
                        )
                      }
                      emptyMessage={
                        'No development gaps were identified from the current evidence.'
                      }
                    />

                    <EvidenceGroup
                      title={
                        'Technologies You Already Match'
                      }
                      items={
                        topRecommendation
                          .matched_technologies
                      }
                      showAll={
                        showAllMatchedTechnologies
                      }
                      onToggle={() =>
                        setShowAllMatchedTechnologies(
                          (current) =>
                            !current,
                        )
                      }
                      emptyMessage={
                        'No matching technologies identified yet.'
                      }
                    />
                  </dl>
                </article>
              </div>

              <div className="career-guidance-actions">
                <button
                  className="gn-button gn-button--primary"
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
                  className="gn-button gn-button--secondary career-guidance-bordered-button"
                  type="button"
                  disabled
                  title="Available in WBS 5.8."
                >
                  View Learning Resources
                </button>

                <button
                  className="gn-button gn-button--secondary career-guidance-bordered-button"
                  type="button"
                  disabled
                  title="Available in WBS 5.8."
                >
                  View Career Roadmap
                </button>
              </div>
            </section>
          ) : (
            <section className="career-guidance-state-card">
              <h2>
                No career recommendations yet
              </h2>

              <p>
                Add information to your Student
                Profile so GradNavi has enough
                context to identify career matches.
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


          {visibleOtherRecommendations.length > 0 && (
            <section className="career-guidance-section">
              <div className="career-guidance-section__heading career-guidance-section__heading--with-action">
                <div>
                  <h2>
                    Other Career Matches
                  </h2>

                  <p>
                    Explore other careers that
                    align with your profile and
                    compare where you stand for
                    each option.
                  </p>
                </div>

                {otherRecommendations.length >
                  DEFAULT_OTHER_CAREER_COUNT && (
                  <button
                    className="gn-button gn-button--secondary career-guidance-bordered-button"
                    type="button"
                    onClick={() =>
                      setShowAllCareers(
                        (current) =>
                          !current,
                      )
                    }
                  >
                    {showAllCareers
                      ? 'Show top matches'
                      : (
                        `View all ${recommendations.length} careers`
                      )}
                  </button>
                )}
              </div>

              <div className="career-guidance-career-grid">
                {visibleOtherRecommendations.map(
                  (recommendation) => {
                    const developmentNeeds =
                      getVisibleEvidence(
                        recommendation
                          .missing_competencies,
                        false,
                      )

                    return (
                      <article
                        key={
                          recommendation
                            .career_id
                        }
                        className="career-guidance-career-card"
                      >
                        <div className="career-guidance-career-card__heading">
                          <span className="gn-badge gn-badge--current">
                            #{recommendation.rank || '—'}
                          </span>

                          <h3>
                            {
                              recommendation
                                .career_name
                            }
                          </h3>
                        </div>

                        <p className="career-guidance-career-card__score">
                          Career Match:{' '}
                          <strong>
                            {formatPercentage(
                              recommendation
                                .recommendation_score,
                            )}
                          </strong>
                        </p>

                        <div className="career-guidance-career-card__components">
                          <span>
                            Skills and Knowledge

                            <strong>
                              {formatPercentage(
                                recommendation
                                  .competency_score,
                              )}
                            </strong>
                          </span>

                          <span>
                            Technology Match

                            <strong>
                              {formatPercentage(
                                recommendation
                                  .technology_score,
                              )}
                            </strong>
                          </span>

                          <span>
                            Profile Alignment

                            <strong>
                              {formatPercentage(
                                recommendation
                                  .semantic_alignment_score,
                              )}
                            </strong>
                          </span>
                        </div>

                        <p>
                          Skills and knowledge
                          to develop:{' '}

                          {developmentNeeds.length > 0
                            ? developmentNeeds.join(
                                ', ',
                              )
                            : 'None identified'}
                        </p>

                        <button
                          className="gn-button gn-button--secondary career-guidance-bordered-button"
                          type="button"
                          onClick={() =>
                            openSkillGapAnalysis(
                              recommendation
                                .career_id,
                            )
                          }
                        >
                          View Skill Gaps
                        </button>
                      </article>
                    )
                  },
                )}
              </div>

              {otherRecommendations.length >
                DEFAULT_OTHER_CAREER_COUNT && (
                <div className="career-guidance-view-all-row">
                  <button
                    className="gn-button gn-button--secondary career-guidance-bordered-button"
                    type="button"
                    onClick={() =>
                      setShowAllCareers(
                        (current) =>
                          !current,
                      )
                    }
                  >
                    {showAllCareers
                      ? 'Show top matches'
                      : (
                        `View all ${recommendations.length} careers`
                      )}
                  </button>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </main>
  )
}


export default CareerRecommendationsPage
