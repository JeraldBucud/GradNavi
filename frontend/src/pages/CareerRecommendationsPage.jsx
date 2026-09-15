import {
  useEffect,
  useState,
} from 'react'

import { useNavigate } from 'react-router'

import { getStoredUser } from '../services/authService'
import {
  getCareerRecommendations,
} from '../services/careerService'

import './CareerGuidancePage.css'


function formatStatus(value) {
  if (!value) {
    return 'Unknown'
  }

  return value
    .split('_')
    .map((part) =>
      part.charAt(0).toUpperCase()
      + part.slice(1),
    )
    .join(' ')
}


function formatPercentage(value) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return 'Not scored'
  }

  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 'Not scored'
  }

  const formattedValue =
    Number.isInteger(numericValue)
      ? numericValue.toFixed(0)
      : numericValue.toFixed(1)

  return `${formattedValue}%`
}


function joinEvidence(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return 'None returned'
  }

  return items.join(', ')
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  return (
    requestError?.data?.error?.message ||
    requestError?.message ||
    fallbackMessage
  )
}


function getTopRecommendation(recommendations) {
  return (
    recommendations.find(
      (recommendation) =>
        recommendation.rank === 1,
    ) ||
    recommendations.find(
      (recommendation) =>
        recommendation.score_status === 'scored',
    ) ||
    null
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
    isRefreshing,
    setIsRefreshing,
  ] = useState(false)

  const [
    loadError,
    setLoadError,
  ] = useState('')

  const currentUser = getStoredUser()

  const accountName =
    currentUser?.first_name?.trim() ||
    'Student'

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
        recommendation.career_id !==
          topRecommendation?.career_id,
    )

  const scoredCount =
    recommendations.filter(
      (recommendation) =>
        recommendation.score_status === 'scored',
    ).length

  const insufficientProfileCount =
    recommendations.filter(
      (recommendation) =>
        recommendation.score_status ===
          'insufficient_profile',
    ).length

  const insufficientEvidenceCount =
    recommendations.filter(
      (recommendation) =>
        recommendation.score_status ===
          'insufficient_evidence',
    ).length


  async function loadRecommendations(
    { refresh = false } = {},
  ) {
    try {
      if (refresh) {
        setIsRefreshing(true)
      } else {
        setIsLoading(true)
      }

      setLoadError('')

      const responseData =
        await getCareerRecommendations()

      const responseRecommendations =
        responseData?.data?.recommendations

      setRecommendations(
        Array.isArray(responseRecommendations)
          ? responseRecommendations
          : [],
      )
    } catch (requestError) {
      setLoadError(
        getRequestErrorMessage(
          requestError,
          'Unable to load career recommendations.',
        ),
      )
    } finally {
      if (refresh) {
        setIsRefreshing(false)
      } else {
        setIsLoading(false)
      }
    }
  }


  useEffect(() => {
    loadRecommendations()
  }, [])


  function openSkillGapAnalysis(careerId) {
    navigate(
      `/skill-gap-analysis?career_id=${careerId}`,
    )
  }


  if (isLoading) {
    return (
      <main className="career-guidance-page">
        <div className="career-guidance-state-card">
          <p>
            Loading Career Recommendations...
          </p>
        </div>
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
            Explore deterministic career matches calculated from
            profile skills and approved career reference data.
          </p>
        </div>

        <div
          className="career-guidance-account-pill"
          aria-label={`Signed in as ${accountName}`}
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
            onClick={() => loadRecommendations()}
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
                  Recommendation Summary
                </h2>
              </div>
            </div>

            <div className="career-guidance-summary-layout">
              <div className="career-guidance-metrics career-guidance-metrics--summary">
                <article className="career-guidance-metric-card">
                  <span>
                    Career Matches
                  </span>

                  <strong>
                    {recommendations.length}
                  </strong>

                  <small>
                    Available careers
                  </small>
                </article>

                <article className="career-guidance-metric-card">
                  <span>
                    Scored Results
                  </span>

                  <strong>
                    {scoredCount}
                  </strong>

                  <small>
                    Deterministic scores
                  </small>
                </article>

                <article className="career-guidance-metric-card career-guidance-metric-card--wide">
                  <span>
                    Profile Evidence
                  </span>

                  <strong>
                    Skills only
                  </strong>

                  <small>
                    Proficiency belongs to readiness
                  </small>
                </article>
              </div>

              <button
                className="gn-button gn-button--primary career-guidance-refresh-button"
                type="button"
                aria-busy={isRefreshing}
                disabled={isRefreshing}
                onClick={() =>
                  loadRecommendations({
                    refresh: true,
                  })
                }
              >
                {isRefreshing
                  ? 'Refreshing...'
                  : 'Refresh Recommendations'}
              </button>
            </div>
          </section>


          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  How Recommendations Are Calculated
                </h2>

                <p>
                  GradNavi uses deterministic weighted matching.
                  Student proficiency is intentionally excluded from
                  Recommendation Score and is used separately for
                  career-readiness analysis.
                </p>
              </div>
            </div>

            <div className="career-guidance-badges">
              <span className="gn-badge gn-badge--current">
                GradNavi Analysis
              </span>

              <span className="gn-badge gn-badge--inactive">
                No AI scoring
              </span>

              <span className="gn-badge gn-badge--inactive">
                Readiness separate
              </span>

              <span className="gn-badge gn-badge--inactive">
                No selected-career persistence
              </span>
            </div>
          </section>


          {topRecommendation ? (
            <section className="career-guidance-section">
              <div className="career-guidance-section__heading">
                <div>
                  <h2>
                    Top Recommendation
                  </h2>
                </div>
              </div>

              <div className="career-guidance-top-recommendation">
                <div className="career-guidance-top-recommendation__summary">
                  <h3>
                    #{topRecommendation.rank || 1}{' '}
                    {topRecommendation.career_name}
                  </h3>

                  <div className="career-guidance-metrics career-guidance-metrics--compact">
                    <article className="career-guidance-metric-card">
                      <span>
                        Recommendation Score
                      </span>

                      <strong>
                        {formatPercentage(
                          topRecommendation.recommendation_score,
                        )}
                      </strong>

                      <small>
                        {formatStatus(
                          topRecommendation.score_status,
                        )}
                      </small>
                    </article>

                    <article className="career-guidance-metric-card">
                      <span>
                        Rank
                      </span>

                      <strong>
                        {topRecommendation.rank || '—'}
                      </strong>

                      <small>
                        API rank
                      </small>
                    </article>
                  </div>
                </div>

                <article className="career-guidance-evidence-card">
                  <h3>
                    Why This Career Matched
                  </h3>

                  <dl>
                    <div>
                      <dt>
                        Matched Competencies
                      </dt>

                      <dd>
                        {joinEvidence(
                          topRecommendation.matched_competencies,
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt>
                        Missing Competencies
                      </dt>

                      <dd>
                        {joinEvidence(
                          topRecommendation.missing_competencies,
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt>
                        Matched Technologies
                      </dt>

                      <dd>
                        {joinEvidence(
                          topRecommendation.matched_technologies,
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt>
                        ESCO Evidence
                      </dt>

                      <dd>
                        Essential matches:{' '}
                        {topRecommendation.esco_essential_matches || 0}
                        {' · '}
                        Optional matches:{' '}
                        {topRecommendation.esco_optional_matches || 0}
                      </dd>
                    </div>
                  </dl>
                </article>
              </div>

              <div className="career-guidance-actions">
                <button
                  className="gn-button gn-button--primary"
                  type="button"
                  onClick={() =>
                    openSkillGapAnalysis(
                      topRecommendation.career_id,
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
                No scored recommendation yet
              </h2>

              <p>
                Update the Student Profile with skills, then refresh
                recommendations to calculate deterministic matches.
              </p>

              <button
                className="gn-button gn-button--primary"
                type="button"
                onClick={() => navigate('/profile')}
              >
                Update Student Profile
              </button>
            </section>
          )}


          {otherRecommendations.length > 0 && (
            <section className="career-guidance-section">
              <div className="career-guidance-section__heading">
                <div>
                  <h2>
                    Other Career Matches
                  </h2>
                </div>
              </div>

              <div className="career-guidance-career-grid">
                {otherRecommendations.map(
                  (recommendation) => (
                    <article
                      key={recommendation.career_id}
                      className="career-guidance-career-card"
                    >
                      <div className="career-guidance-career-card__heading">
                        <span className="gn-badge gn-badge--current">
                          #{recommendation.rank || '—'}
                        </span>

                        <h3>
                          {recommendation.career_name}
                        </h3>
                      </div>

                      <p className="career-guidance-career-card__score">
                        Recommendation Score:{' '}
                        <strong>
                          {formatPercentage(
                            recommendation.recommendation_score,
                          )}
                        </strong>
                      </p>

                      <p>
                        Matched competencies:{' '}
                        {joinEvidence(
                          recommendation.matched_competencies,
                        )}
                      </p>

                      <p>
                        Missing competencies:{' '}
                        {joinEvidence(
                          recommendation.missing_competencies,
                        )}
                      </p>

                      <button
                        className="gn-button gn-button--secondary career-guidance-bordered-button"
                        type="button"
                        onClick={() =>
                          openSkillGapAnalysis(
                            recommendation.career_id,
                          )
                        }
                      >
                        View Skill Gaps
                      </button>
                    </article>
                  ),
                )}
              </div>
            </section>
          )}


          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  Recommendation Status Coverage
                </h2>

                <p>
                  These counts come directly from the backend
                  recommendation status for the current profile and
                  career evidence.
                </p>
              </div>
            </div>

            <div className="career-guidance-metrics career-guidance-metrics--status">
              <article className="career-guidance-metric-card">
                <span>
                  Insufficient Profile
                </span>

                <strong>
                  {insufficientProfileCount}
                </strong>

                <small>
                  No recommendation score
                </small>
              </article>

              <article className="career-guidance-metric-card">
                <span>
                  Insufficient Evidence
                </span>

                <strong>
                  {insufficientEvidenceCount}
                </strong>

                <small>
                  Career evidence unavailable
                </small>
              </article>

              <article className="career-guidance-metric-card">
                <span>
                  Scored
                </span>

                <strong>
                  {scoredCount}
                </strong>

                <small>
                  Recommendation score shown
                </small>
              </article>
            </div>
          </section>
        </>
      )}
    </main>
  )
}


export default CareerRecommendationsPage
