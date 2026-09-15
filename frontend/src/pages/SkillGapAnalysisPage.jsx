import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
  useSearchParams,
} from 'react-router'

import { getStoredUser } from '../services/authService'
import {
  getLearningSuggestions,
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


function formatNumber(value) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return '—'
  }

  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return String(value)
  }

  return Number.isInteger(numericValue)
    ? numericValue.toFixed(0)
    : numericValue.toFixed(1)
}


function formatPercentage(value) {
  const formattedValue = formatNumber(value)

  return formattedValue === '—'
    ? 'Not scored'
    : `${formattedValue}%`
}


function formatProficiency(value) {
  if (!value) {
    return 'None'
  }

  return formatStatus(value)
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  const details =
    requestError?.data?.error?.details

  if (details?.career_id) {
    const careerErrors = details.career_id

    if (Array.isArray(careerErrors)) {
      return careerErrors[0]
    }
  }

  return (
    requestError?.data?.error?.message ||
    requestError?.message ||
    fallbackMessage
  )
}


function getUniqueResources(suggestions) {
  const resourcesById = new Map()

  suggestions.forEach((suggestion) => {
    const resources =
      Array.isArray(suggestion.resources)
        ? suggestion.resources
        : []

    resources.forEach((resource) => {
      resourcesById.set(
        resource.id,
        resource,
      )
    })
  })

  return Array.from(
    resourcesById.values(),
  )
}


function SkillGapAnalysisPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const rawCareerId =
    searchParams.get('career_id')

  const careerId = Number(rawCareerId)

  const hasValidCareerId =
    Number.isInteger(careerId) &&
    careerId > 0

  const [
    readinessData,
    setReadinessData,
  ] = useState(null)

  const [
    isLoading,
    setIsLoading,
  ] = useState(hasValidCareerId)

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

  const suggestions =
    Array.isArray(
      readinessData?.learning_suggestions,
    )
      ? readinessData.learning_suggestions
      : []

  const uniqueResources =
    getUniqueResources(suggestions)

  const previewResources =
    uniqueResources.slice(0, 3)


  useEffect(() => {
    if (!hasValidCareerId) {
      setReadinessData(null)
      setLoadError('')
      setIsLoading(false)
      return
    }


    async function loadReadiness() {
      try {
        setIsLoading(true)
        setLoadError('')

        const responseData =
          await getLearningSuggestions(
            careerId,
          )

        setReadinessData(
          responseData?.data || null,
        )
      } catch (requestError) {
        setReadinessData(null)

        setLoadError(
          getRequestErrorMessage(
            requestError,
            'Unable to load career-readiness analysis.',
          ),
        )
      } finally {
        setIsLoading(false)
      }
    }


    loadReadiness()
  }, [careerId, hasValidCareerId])


  if (isLoading) {
    return (
      <main className="career-guidance-page">
        <div className="career-guidance-state-card">
          <p>
            Loading Skill Gap Analysis...
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
            Skill Gap Analysis
          </h1>

          <p>
            Review selected-career readiness and unresolved skill
            gaps calculated from the implemented readiness and
            learning-suggestion services.
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


      {!hasValidCareerId ? (
        <section className="career-guidance-state-card">
          <h2>
            Select a career first
          </h2>

          <p>
            Skill-gap and readiness analysis requires a selected
            career. Open Career Recommendations and choose a career
            to analyse.
          </p>

          <button
            className="gn-button gn-button--primary"
            type="button"
            onClick={() =>
              navigate('/career-recommendations')
            }
          >
            Open Career Recommendations
          </button>
        </section>
      ) : loadError ? (
        <section className="career-guidance-state-card">
          <h2>
            Readiness analysis unavailable
          </h2>

          <p role="alert">
            {loadError}
          </p>

          <div className="career-guidance-actions">
            <button
              className="gn-button gn-button--primary"
              type="button"
              onClick={() =>
                navigate('/career-recommendations')
              }
            >
              Choose Another Career
            </button>

            <button
              className="gn-button gn-button--secondary career-guidance-bordered-button"
              type="button"
              onClick={() =>
                window.location.reload()
              }
            >
              Try Again
            </button>
          </div>
        </section>
      ) : readinessData ? (
        <>
          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  Selected Career
                </h2>
              </div>
            </div>

            <div className="career-guidance-metrics career-guidance-metrics--selected-career">
              <article className="career-guidance-metric-card">
                <span>
                  Career ID
                </span>

                <strong>
                  {readinessData.career_id}
                </strong>

                <small>
                  Selected query value
                </small>
              </article>

              <article className="career-guidance-metric-card career-guidance-metric-card--wide">
                <span>
                  Career
                </span>

                <strong>
                  {readinessData.career_name}
                </strong>

                <small>
                  API career name
                </small>
              </article>

              <article className="career-guidance-metric-card">
                <span>
                  Score Status
                </span>

                <strong>
                  {formatStatus(
                    readinessData.score_status,
                  )}
                </strong>

                <small>
                  Readiness status
                </small>
              </article>
            </div>
          </section>


          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  Career Readiness Summary
                </h2>

                <p>
                  Readiness compares Student proficiency with
                  source-backed required levels. It is separate from
                  Recommendation Score.
                </p>
              </div>
            </div>

            <div className="career-guidance-metrics career-guidance-metrics--status">
              <article className="career-guidance-metric-card">
                <span>
                  Readiness Score
                </span>

                <strong>
                  {formatPercentage(
                    readinessData.readiness_score,
                  )}
                </strong>

                <small>
                  Deterministic analysis
                </small>
              </article>

              <article className="career-guidance-metric-card">
                <span>
                  Unresolved
                </span>

                <strong>
                  {suggestions.length}
                </strong>

                <small>
                  Missing or below requirement
                </small>
              </article>

              <article className="career-guidance-metric-card">
                <span>
                  Score Status
                </span>

                <strong>
                  {formatStatus(
                    readinessData.score_status,
                  )}
                </strong>

                <small>
                  API readiness status
                </small>
              </article>
            </div>
          </section>


          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  Development Needs
                </h2>

                <p>
                  Priority follows backend order. GradNavi does not
                  invent High, Medium, or Low thresholds in the
                  frontend.
                </p>
              </div>
            </div>

            {suggestions.length > 0 ? (
              <div className="career-guidance-table-wrap">
                <table className="career-guidance-table">
                  <thead>
                    <tr>
                      <th>
                        Priority
                      </th>
                      <th>
                        Skill
                      </th>
                      <th>
                        Gap Status
                      </th>
                      <th>
                        Current
                      </th>
                      <th>
                        Score
                      </th>
                      <th>
                        Required
                      </th>
                      <th>
                        Gap
                      </th>
                      <th>
                        Importance
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {suggestions.map(
                      (suggestion) => (
                        <tr key={suggestion.skill_id}>
                          <td>
                            <strong>
                              {suggestion.priority}
                            </strong>
                          </td>

                          <td>
                            {suggestion.skill_name}
                          </td>

                          <td>
                            {formatStatus(
                              suggestion.gap_status,
                            )}
                          </td>

                          <td>
                            {formatProficiency(
                              suggestion.current_proficiency,
                            )}
                          </td>

                          <td>
                            {formatNumber(
                              suggestion.current_score,
                            )}
                          </td>

                          <td>
                            {formatNumber(
                              suggestion.required_level,
                            )}
                          </td>

                          <td>
                            {formatNumber(
                              suggestion.gap_amount,
                            )}
                          </td>

                          <td>
                            {formatNumber(
                              suggestion.importance,
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="career-guidance-inline-state">
                <h3>
                  No unresolved development needs
                </h3>

                <p>
                  The current API returned no missing or
                  below-requirement skills for this career.
                </p>
              </div>
            )}
          </section>


          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  Learning Resources
                </h2>

                <p>
                  Preview of controlled external resources already
                  linked by the backend to unresolved skill gaps.
                </p>
              </div>
            </div>

            {previewResources.length > 0 ? (
              <div className="career-guidance-resource-grid">
                {previewResources.map(
                  (resource) => (
                    <article
                      key={resource.id}
                      className="career-guidance-resource-card"
                    >
                      <h3>
                        {resource.title}
                      </h3>

                      <p>
                        Provider: {resource.provider}
                      </p>

                      <p>
                        Type:{' '}
                        {formatStatus(
                          resource.resource_type,
                        )}
                      </p>

                      <a
                        className="gn-button gn-button--secondary career-guidance-bordered-button"
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
              <div className="career-guidance-inline-state">
                <p>
                  No active learning resources are currently linked
                  to these unresolved skills.
                </p>
              </div>
            )}
          </section>


          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <div>
                <h2>
                  Next Actions
                </h2>
              </div>
            </div>

            <div className="career-guidance-actions">
              <button
                className="gn-button gn-button--primary"
                type="button"
                disabled
                title="Full Learning Resources page is implemented in WBS 5.8."
              >
                Open Learning Resources
              </button>

              <button
                className="gn-button gn-button--secondary career-guidance-bordered-button"
                type="button"
                disabled
                title="Career Roadmap page is implemented in WBS 5.8."
              >
                Open Career Roadmap
              </button>

              <button
                className="gn-button gn-button--secondary career-guidance-bordered-button"
                type="button"
                onClick={() => navigate('/profile')}
              >
                Update Student Profile
              </button>

              <button
                className="gn-button gn-button--secondary career-guidance-bordered-button"
                type="button"
                onClick={() =>
                  navigate('/career-recommendations')
                }
              >
                Back to Recommendations
              </button>
            </div>
          </section>
        </>
      ) : null}
    </main>
  )
}


export default SkillGapAnalysisPage
