import {
  useMemo,
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
  JOB_DESCRIPTION_MAX_LENGTH,
  matchJobDescription,
} from '../services/jobMatchingService'

import './CareerGuidancePage.css'
import './JobMatchingPage.css'


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  const details =
    requestError
      ?.data
      ?.error
      ?.details
    || requestError?.data

  if (
    details
    && typeof details === 'object'
  ) {
    const jobDescriptionError =
      details.job_description

    if (
      Array.isArray(
        jobDescriptionError,
      )
      && jobDescriptionError.length > 0
    ) {
      return String(
        jobDescriptionError[0],
      )
    }

    if (
      typeof jobDescriptionError
      === 'string'
      && jobDescriptionError.trim()
    ) {
      return jobDescriptionError.trim()
    }
  }

  return (
    requestError
      ?.data
      ?.error
      ?.message
    || requestError
      ?.data
      ?.detail
    || requestError?.message
    || fallbackMessage
  )
}


function formatConceptType(
  value,
) {
  if (!value) {
    return 'Skill'
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


function RequirementCard({
  requirement,
  matched,
}) {
  const proficiency =
    requirement
      ?.current_proficiency

  return (
    <article
      className={[
        'job-matching-requirement',
        matched
          ? 'job-matching-requirement--matched'
          : 'job-matching-requirement--missing',
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <div className="job-matching-requirement__heading">
        <div>
          <h3>
            {
              requirement?.skill_name
              || 'Recognised requirement'
            }
          </h3>

          <p>
            {
              matched
                ? (
                  'Current proficiency: '
                  + (
                    proficiency
                    || 'Not specified'
                  )
                )
                : (
                  'Not currently listed in '
                  + 'your Student Profile'
                )
            }
          </p>
        </div>

        <span
          className={
            matched
              ? 'gn-badge gn-badge--matched'
              : 'gn-badge gn-badge--missing'
          }
        >
          {
            matched
              ? 'In profile'
              : 'Not in profile'
          }
        </span>
      </div>

      <div className="job-matching-requirement__meta">
        <span>
          {formatConceptType(
            requirement?.concept_type,
          )}
        </span>

        {
          requirement?.match_source
            ? (
              <span>
                {
                  requirement.match_source
                  === 'alias'
                    ? 'Alias match'
                    : 'Canonical match'
                }
              </span>
            )
            : null
        }

        {
          requirement?.matched_term
            ? (
              <span>
                Recognised as “
                {requirement.matched_term}
                ”
              </span>
            )
            : null
        }
      </div>
    </article>
  )
}


function JobMatchingPage() {
  const navigate = useNavigate()
  const inputRef = useRef(null)

  const storedUser = getStoredUser()

  const accountName =
    storedUser?.first_name?.trim()
    || 'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()

  const [
    jobDescription,
    setJobDescription,
  ] = useState('')

  const [
    result,
    setResult,
  ] = useState(null)

  const [
    requestState,
    setRequestState,
  ] = useState('idle')

  const [
    requestError,
    setRequestError,
  ] = useState('')

  const characterCount =
    jobDescription.length

  const remainingCharacters =
    JOB_DESCRIPTION_MAX_LENGTH
    - characterCount

  const isOverLimit =
    remainingCharacters < 0

  const normalizedJobDescription =
    jobDescription.trim()

  const canAnalyze =
    Boolean(
      normalizedJobDescription
      && !isOverLimit
      && requestState !== 'loading'
    )

  const matchedRequirements =
    useMemo(
      () =>
        (
          Array.isArray(
            result
              ?.matched_requirements,
          )
            ? result
              .matched_requirements
            : []
        ),
      [result],
    )

  const missingRequirements =
    useMemo(
      () =>
        (
          Array.isArray(
            result
              ?.missing_requirements,
          )
            ? result
              .missing_requirements
            : []
        ),
      [result],
    )

  const matchedCount =
    Number(
      result
        ?.matched_requirement_count
      ?? matchedRequirements.length,
    )

  const missingCount =
    Number(
      result
        ?.missing_requirement_count
      ?? missingRequirements.length,
    )

  const totalCount =
    Number(
      result
        ?.total_requirement_count
      ?? (
        matchedCount
        + missingCount
      ),
    )


  async function handleAnalyze(
    event,
  ) {
    event.preventDefault()

    setRequestError('')

    if (!normalizedJobDescription) {
      setRequestError(
        'Paste a job description before analyzing it.',
      )

      inputRef.current?.focus()

      return
    }

    if (isOverLimit) {
      setRequestError(
        'Job descriptions are limited to 20,000 characters.',
      )

      inputRef.current?.focus()

      return
    }

    setRequestState('loading')

    try {
      const response =
        await matchJobDescription({
          jobDescription:
            normalizedJobDescription,
        })

      const responseData =
        response?.data

      if (
        !responseData
        || typeof responseData
        !== 'object'
      ) {
        throw new Error(
          'Job Matching returned an invalid response.',
        )
      }

      setResult(
        responseData,
      )

      setRequestState('success')
    }
    catch (error) {
      setResult(null)

      setRequestError(
        getRequestErrorMessage(
          error,
          (
            'GradNavi could not analyze '
            + 'this job description. '
            + 'Please try again.'
          ),
        ),
      )

      setRequestState('error')
    }
  }


  function handleClear() {
    setJobDescription('')
    setResult(null)
    setRequestError('')
    setRequestState('idle')

    requestAnimationFrame(
      () =>
        inputRef.current?.focus(),
    )
  }


  function handleAnalyzeAnother() {
    handleClear()
  }


  function openApplicationBuilder(
    path,
  ) {
    navigate(
      path,
      {
        state: {
          source: 'job-matching',
          jobDescription:
            normalizedJobDescription,
        },
      },
    )
  }


  return (
    <main className="career-guidance-page job-matching-page">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>
            {
              result
                ? 'Job Matching Results'
                : 'Job Matching'
            }
          </h1>

          <p>
            {
              result
                ? (
                  'See which recognised requirements '
                  + 'are already in your profile and '
                  + 'which ones need attention before '
                  + 'you apply.'
                )
                : (
                  'Paste a job description to compare '
                  + 'its recognised requirements with '
                  + 'skills saved in your Student '
                  + 'Profile.'
                )
            }
          </p>
        </div>

        <div
          className="career-guidance-account-pill"
          aria-label={
            'Signed in as '
            + accountName
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


      {
        !result
          ? (
            <>
              <form
                className="job-matching-input-card job-matching-input-card--primary"
                onSubmit={handleAnalyze}
                noValidate
              >
                <div className="job-matching-input-card__heading">
                  <div>
                    <h2>
                      Paste a job description
                    </h2>

                    <p>
                      Paste the role description below.
                      GradNavi compares recognised
                      requirements with skills saved
                      in your Student Profile.
                    </p>
                  </div>
                </div>

                <div className="job-matching-profile-context">
                  <div>
                    <strong>
                      Results use your current Student Profile
                    </strong>

                    <span>
                      Keep your skills up to date for
                      a more accurate comparison.
                    </span>
                  </div>

                  {
                    !jobDescription
                      ? (
                        <button
                          className="gn-button gn-button--secondary job-matching-bordered-button"
                          type="button"
                          onClick={() =>
                            navigate('/profile')
                          }
                        >
                          Review Profile
                        </button>
                      )
                      : null
                  }
                </div>

                <label
                  className="job-matching-field"
                  htmlFor="job-matching-description"
                >
                  <span className="job-matching-field__label">
                    Job description
                  </span>

                  <textarea
                    ref={inputRef}
                    id="job-matching-description"
                    value={jobDescription}
                    placeholder="Paste the full job description here..."
                    rows={10}
                    aria-describedby="job-matching-character-count job-matching-guidance"
                    aria-invalid={
                      Boolean(
                        requestError
                        || isOverLimit,
                      )
                    }
                    onChange={
                      (event) => {
                        setJobDescription(
                          event.target.value,
                        )

                        setRequestError('')

                        if (
                          requestState
                          === 'error'
                        ) {
                          setRequestState(
                            'idle',
                          )
                        }
                      }
                    }
                  />
                </label>

                <div
                  id="job-matching-character-count"
                  className={[
                    'job-matching-character-count',
                    isOverLimit
                      ? 'job-matching-character-count--error'
                      : '',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                >
                  <span>
                    {characterCount}
                    {' / '}
                    {JOB_DESCRIPTION_MAX_LENGTH}
                    {' characters'}
                  </span>

                  <span>
                    {
                      isOverLimit
                        ? (
                          Math.abs(
                            remainingCharacters,
                          )
                          + ' over limit'
                        )
                        : (
                          remainingCharacters
                          + ' remaining'
                        )
                    }
                  </span>
                </div>

                {
                  requestError
                    ? (
                      <div
                        className="gn-notice gn-notice--error"
                        role="alert"
                      >
                        <strong className="gn-notice__title">
                          Job Matching could not continue
                        </strong>

                        <p className="gn-notice__body">
                          {requestError}
                        </p>
                      </div>
                    )
                    : null
                }

                {
                  requestState
                  === 'loading'
                    ? (
                      <div
                        className="job-matching-loading"
                        role="status"
                        aria-live="polite"
                      >
                        <span
                          className="job-matching-spinner"
                          aria-hidden="true"
                        />

                        <div>
                          <strong>
                            Analyzing recognised requirements
                          </strong>

                          <span>
                            Comparing recognised skills
                            with your Student Profile.
                          </span>
                        </div>
                      </div>
                    )
                    : null
                }

                <div className="job-matching-input-card__footer">
                  <div className="job-matching-actions">
                    <button
                      className="gn-button gn-button--primary"
                      type="submit"
                      disabled={!canAnalyze}
                      aria-busy={
                        requestState
                        === 'loading'
                      }
                    >
                      {
                        requestState
                        === 'loading'
                          ? 'Analyzing…'
                          : 'Analyze Job'
                      }
                    </button>

                    <button
                      className="gn-button gn-button--secondary job-matching-bordered-button"
                      type="button"
                      disabled={
                        requestState
                        === 'loading'
                      }
                      onClick={handleClear}
                    >
                      Clear
                    </button>
                  </div>

                  <p
                    id="job-matching-guidance"
                    className="job-matching-tip"
                  >
                    Include responsibilities,
                    requirements, and preferred skills
                    {' • '}Max 20,000 characters
                  </p>
                </div>
              </form>

              <details className="job-matching-how">
                <summary>
                  How Job Matching works
                </summary>

                <div className="job-matching-how__content">
                  <p>
                    <strong>
                      Recognised requirements only.
                    </strong>
                    {' '}
                    GradNavi matches canonical skills
                    and approved aliases.
                  </p>

                  <p>
                    <strong>
                      No guessing.
                    </strong>
                    {' '}
                    Ambiguous or unsupported terms
                    are excluded.
                  </p>

                  <p>
                    <strong>
                      No suitability score.
                    </strong>
                    {' '}
                    Results compare recognised job
                    requirements with evidence saved
                    in your profile.
                  </p>
                </div>
              </details>
            </>
          )
          : (
            <>
              <section className="job-matching-result-header">
                <div>
                  <h2>
                    Your job match
                  </h2>

                  <p>
                    Based on recognised requirements
                    from the job description and skills
                    saved in your Student Profile.
                  </p>
                </div>

                <button
                  className="gn-button gn-button--secondary job-matching-bordered-button"
                  type="button"
                  onClick={handleAnalyzeAnother}
                >
                  Analyze Another Job
                </button>
              </section>

              <section
                className="job-matching-metrics"
                aria-label="Job Matching summary"
              >
                <article>
                  <span>
                    In your profile
                  </span>

                  <strong>
                    {matchedCount}
                    {' of '}
                    {totalCount}
                  </strong>

                  <small>
                    recognised requirements found
                    in your profile
                  </small>
                </article>

                <article>
                  <span>
                    To review
                  </span>

                  <strong>
                    {missingCount}
                  </strong>

                  <small>
                    recognised requirements not
                    listed in your profile
                  </small>
                </article>
              </section>

              <div className="gn-notice gn-notice--info job-matching-meaning">
                <strong className="gn-notice__title">
                  {
                    totalCount > 0
                      ? (
                        'GradNavi recognised '
                        + totalCount
                        + ' requirements in this '
                        + 'job description.'
                      )
                      : (
                        'No supported requirements '
                        + 'were recognised.'
                      )
                  }
                </strong>

                <p className="gn-notice__body">
                  These results compare recognised
                  requirements with your current
                  profile. They are not an employment
                  suitability score. Unrecognised or
                  ambiguous terms are excluded.
                </p>
              </div>

              <section className="job-matching-requirements-grid">
                <div className="job-matching-requirement-section">
                  <div className="job-matching-requirement-section__heading">
                    <h2>
                      Already in your profile
                    </h2>

                    <span className="gn-badge gn-badge--matched">
                      {matchedRequirements.length}
                      {' items'}
                    </span>
                  </div>

                  <div className="job-matching-requirement-list">
                    {
                      matchedRequirements.length
                        ? matchedRequirements.map(
                          (requirement) => (
                            <RequirementCard
                              key={
                                'matched-'
                                + requirement.skill_id
                              }
                              requirement={requirement}
                              matched
                            />
                          ),
                        )
                        : (
                          <p className="job-matching-empty-list">
                            No recognised requirements
                            were found in your profile.
                          </p>
                        )
                    }
                  </div>
                </div>

                <div className="job-matching-requirement-section">
                  <div className="job-matching-requirement-section__heading">
                    <h2>
                      Not listed in your profile
                    </h2>

                    <span className="gn-badge gn-badge--missing">
                      {missingRequirements.length}
                      {' items'}
                    </span>
                  </div>

                  <div className="job-matching-requirement-list">
                    {
                      missingRequirements.length
                        ? missingRequirements.map(
                          (requirement) => (
                            <RequirementCard
                              key={
                                'missing-'
                                + requirement.skill_id
                              }
                              requirement={requirement}
                              matched={false}
                            />
                          ),
                        )
                        : (
                          <p className="job-matching-empty-list">
                            Every recognised requirement
                            is already listed in your profile.
                          </p>
                        )
                    }
                  </div>
                </div>
              </section>

              <section className="job-matching-next-actions">
                <div>
                  <h2>
                    Choose your next step
                  </h2>

                  <p>
                    Review skill gaps if requirements
                    are missing, update incomplete
                    profile evidence, or start tailoring
                    your application.
                  </p>
                </div>

                <div className="job-matching-actions">
                  {
                    missingCount > 0
                      ? (
                        <button
                          className="gn-button gn-button--primary"
                          type="button"
                          onClick={() =>
                            navigate(
                              '/skill-gap-analysis',
                            )
                          }
                        >
                          Review Skill Gaps
                        </button>
                      )
                      : (
                        <button
                          className="gn-button gn-button--primary"
                          type="button"
                          onClick={() =>
                            openApplicationBuilder(
                              '/resume-builder',
                            )
                          }
                        >
                          Tailor Resume
                        </button>
                      )
                  }

                  <button
                    className="gn-button gn-button--secondary job-matching-bordered-button"
                    type="button"
                    onClick={() =>
                      navigate('/profile')
                    }
                  >
                    Update Profile
                  </button>

                  {
                    missingCount > 0
                      ? (
                        <button
                          className="gn-button gn-button--secondary job-matching-bordered-button"
                          type="button"
                          onClick={() =>
                            openApplicationBuilder(
                              '/resume-builder',
                            )
                          }
                        >
                          Tailor Resume
                        </button>
                      )
                      : null
                  }

                  <button
                    className="gn-button gn-button--secondary job-matching-bordered-button"
                    type="button"
                    onClick={() =>
                      openApplicationBuilder(
                        '/cover-letter-builder',
                      )
                    }
                  >
                    Draft Cover Letter
                  </button>
                </div>
              </section>
            </>
          )
      }
    </main>
  )
}


export default JobMatchingPage
