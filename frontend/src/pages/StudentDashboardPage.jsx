import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  ArrowRight,
  BriefcaseBusiness,
  FileText,
  GraduationCap,
  MessageSquare,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router'

import useCareerContext from '../hooks/useCareerContext'

import {
  getCareerReadiness,
  getRoadmapOverview,
  getSkillGapSummary,
} from '../services/careerService'

import {
  getStoredUser,
} from '../services/authService'

import {
  getInterviewHistory,
} from '../services/interviewHistoryService'

import {
  getStudentProfile,
} from '../services/profileService'

import './StudentDashboardPage.css'


const MAX_VISIBLE_GAPS = 3
const MAX_VISIBLE_HISTORY = 5


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  return (
    requestError
      ?.data
      ?.error
      ?.message
    || requestError?.message
    || fallbackMessage
  )
}


function getProfileEvidenceSummary(
  profile,
) {
  const collections = [
    profile?.skills,
    profile?.interests,
    profile?.education,
    profile?.experience,
    profile?.projects,
    profile?.career_goals,
    profile?.personality_responses,
  ]

  return collections.reduce(
    (
      summary,
      collection,
    ) => {
      const count =
        Array.isArray(
          collection,
        )
          ? collection.length
          : 0

      return {
        itemCount:
          summary.itemCount
          + count,
        areaCount:
          summary.areaCount
          + (
            count > 0
              ? 1
              : 0
          ),
      }
    },
    {
      itemCount: 0,
      areaCount: 0,
    },
  )
}


function getNumericPercentage(
  value,
) {
  const numericValue =
    Number(
      value,
    )

  if (
    !Number.isFinite(
      numericValue,
    )
  ) {
    return null
  }

  return Math.max(
    0,
    Math.min(
      100,
      numericValue,
    ),
  )
}


function formatPercentage(
  value,
) {
  const numericValue =
    getNumericPercentage(
      value,
    )

  if (numericValue === null) {
    return 'Not scored'
  }

  return `${Math.round(numericValue)}%`
}


function formatInterviewDate(
  value,
) {
  if (!value) {
    return 'Unknown date'
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
    return 'Unknown date'
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    },
  ).format(
    date,
  )
}


function formatGapStatus(
  value,
) {
  if (
    value === 'missing'
    || value === 'missing_requirement'
  ) {
    return 'Missing evidence'
  }

  if (
    value === 'below'
    || value === 'below_requirement'
  ) {
    return 'Below target'
  }

  if (
    value === 'meets'
    || value === 'meets_requirement'
  ) {
    return 'Meets target'
  }

  return 'Needs attention'
}


function getUnresolvedRequirements(
  readiness,
) {
  const requirements =
    readiness
      ?.requirements

  if (!Array.isArray(requirements)) {
    return []
  }

  return requirements.filter(
    (requirement) => (
      requirement?.status
      !== 'meets_requirement'
      && requirement?.status
      !== 'meets'
    ),
  )
}


function PreparationTool({
  icon: Icon,
  title,
  status,
  onClick,
  disabled = false,
}) {
  return (
    <button
      className="student-dashboard-v2__tool"
      type="button"
      disabled={disabled}
      onClick={onClick}
    >
      <span className="student-dashboard-v2__tool-icon">
        <Icon
          size={18}
          strokeWidth={1.8}
          aria-hidden="true"
        />
      </span>

      <span className="student-dashboard-v2__tool-copy">
        <strong>
          {title}
        </strong>

        <small>
          {status}
        </small>
      </span>

      {!disabled && (
        <ArrowRight
          className="student-dashboard-v2__tool-arrow"
          size={16}
          strokeWidth={1.8}
          aria-hidden="true"
        />
      )}
    </button>
  )
}


function StudentDashboardPage() {
  const navigate =
    useNavigate()

  const {
    error:
      careerContextError,
    isLoading:
      isCareerContextLoading,
    primaryCareer,
    selectedCareer,
    selectedCareerId,
    topCareer,
  } = useCareerContext()

  const [
    profile,
    setProfile,
  ] = useState(null)

  const [
    profileLoading,
    setProfileLoading,
  ] = useState(true)

  const [
    profileError,
    setProfileError,
  ] = useState('')

  const [
    interviewHistory,
    setInterviewHistory,
  ] = useState([])

  const [
    historyLoading,
    setHistoryLoading,
  ] = useState(true)

  const [
    historyError,
    setHistoryError,
  ] = useState('')

  const [
    careerState,
    setCareerState,
  ] = useState(
    {
      careerId: null,
      readiness: null,
      roadmap: null,
      skillGapSummary: null,
      isLoading: false,
      error: '',
    },
  )


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

  const primaryCareerId =
    Number(
      primaryCareer
        ?.career_id,
    )

  const dashboardCareerId =
    Number.isInteger(
      primaryCareerId,
    )
    && primaryCareerId > 0
      ? primaryCareerId
      : selectedCareerId


  useEffect(
    () => {
      let isActive = true

      async function loadProfile() {
        try {
          setProfileError('')

          const response =
            await getStudentProfile()

          if (!isActive) {
            return
          }

          setProfile(
            response
              ?.data
              ?.profile
            || null,
          )
        } catch (
          requestError
        ) {
          if (!isActive) {
            return
          }

          setProfileError(
            getRequestErrorMessage(
              requestError,
              'Unable to load your profile.',
            ),
          )
        } finally {
          if (isActive) {
            setProfileLoading(
              false,
            )
          }
        }
      }

      void loadProfile()

      return () => {
        isActive = false
      }
    },
    [],
  )


  useEffect(
    () => {
      let isActive = true

      async function loadHistory() {
        try {
          setHistoryError('')

          const response =
            await getInterviewHistory()

          if (!isActive) {
            return
          }

          const history =
            response
              ?.data
              ?.history

          setInterviewHistory(
            Array.isArray(
              history,
            )
              ? history
              : [],
          )
        } catch (
          requestError
        ) {
          if (!isActive) {
            return
          }

          setHistoryError(
            getRequestErrorMessage(
              requestError,
              (
                'Unable to load '
                + 'Interview History.'
              ),
            ),
          )
        } finally {
          if (isActive) {
            setHistoryLoading(
              false,
            )
          }
        }
      }

      void loadHistory()

      return () => {
        isActive = false
      }
    },
    [],
  )


  useEffect(
    () => {
      if (!dashboardCareerId) {
        return undefined
      }

      let isActive = true

      async function loadCareerData() {
        const [
          readinessResult,
          roadmapResult,
          skillGapSummaryResult,
        ] = await Promise.allSettled(
          [
            getCareerReadiness(
              dashboardCareerId,
            ),
            getRoadmapOverview(
              dashboardCareerId,
            ),
            getSkillGapSummary(
              dashboardCareerId,
            ),
          ],
        )

        if (!isActive) {
          return
        }

        const readiness =
          readinessResult.status
          === 'fulfilled'
            ? (
              readinessResult
                .value
                ?.data
              || null
            )
            : null

        const roadmap =
          roadmapResult.status
          === 'fulfilled'
            ? (
              roadmapResult
                .value
                ?.data
              || null
            )
            : null

        const skillGapSummary =
          skillGapSummaryResult.status
          === 'fulfilled'
            ? (
              skillGapSummaryResult
                .value
                ?.data
              || null
            )
            : null

        let errorMessage = ''

        if (
          readinessResult.status
          === 'rejected'
        ) {
          errorMessage =
            getRequestErrorMessage(
              readinessResult.reason,
              (
                'Unable to load '
                + 'career readiness.'
              ),
            )
        } else if (
          roadmapResult.status
          === 'rejected'
        ) {
          errorMessage =
            getRequestErrorMessage(
              roadmapResult.reason,
              (
                'Unable to load '
                + 'roadmap progress.'
              ),
            )
        }

        setCareerState(
          {
            careerId:
              dashboardCareerId,
            readiness,
            roadmap,
            skillGapSummary,
            isLoading: false,
            error:
              errorMessage,
          },
        )
      }

      void loadCareerData()

      return () => {
        isActive = false
      }
    },
    [
      dashboardCareerId,
    ],
  )


  const currentCareerState =
    careerState.careerId
    === dashboardCareerId
      ? careerState
      : {
        readiness: null,
        roadmap: null,
        skillGapSummary: null,
        isLoading:
          Boolean(
            dashboardCareerId,
          ),
        error: '',
      }


  const readiness =
    currentCareerState
      .readiness

  const roadmap =
    currentCareerState
      .roadmap

  const skillGapSummary =
    currentCareerState
      .skillGapSummary

  const profileEvidence =
    getProfileEvidenceSummary(
      profile,
    )

  const primaryCareerName =
    String(
      primaryCareer
        ?.career_name
      || roadmap
        ?.career_name
      || readiness
        ?.career_name
      || selectedCareer
        ?.career_name
      || '',
    ).trim()

  const topCareerName =
    String(
      topCareer
        ?.career_name
      || '',
    ).trim()

  const topCareerScore =
    formatPercentage(
      topCareer
        ?.recommendation_score,
    )

  const readinessValue =
    readiness
      ?.readiness_score
    ?? roadmap
      ?.readiness_score

  const readinessScore =
    formatPercentage(
      readinessValue,
    )

  const readinessProgress =
    getNumericPercentage(
      readinessValue,
    )
    ?? 0

  const unresolvedGapCount =
    Number(
      readiness
        ?.below_requirement_count
      || 0,
    )
    + Number(
      readiness
        ?.missing_requirement_count
      || 0,
    )

  const roadmapSummary =
    roadmap
      ?.progress_summary

  const roadmapCompleted =
    Number(
      roadmapSummary
        ?.completed
      || 0,
    )

  const roadmapTotal =
    Number(
      roadmapSummary
        ?.total
      || 0,
    )

  const unresolvedRequirements =
    useMemo(
      () =>
        getUnresolvedRequirements(
          readiness,
        ),
      [
        readiness,
      ],
    )

  const fixFirst =
    Array.isArray(
      skillGapSummary
        ?.fix_first,
    )
      ? skillGapSummary.fix_first
      : []

  const recommendedNextSteps =
    Array.isArray(
      skillGapSummary
        ?.recommended_next_steps,
    )
      ? skillGapSummary
        .recommended_next_steps
      : []

  const currentGaps =
    (
      fixFirst.length > 0
        ? fixFirst
        : unresolvedRequirements
    ).slice(
      0,
      MAX_VISIBLE_GAPS,
    )

  const nextGap =
    currentGaps[0]
    || null

  const nextActionDescription =
    String(
      recommendedNextSteps[0]
      || '',
    ).trim()
    || (
      nextGap
        ? (
          `Focus on ${nextGap.skill_name} `
          + 'using your current evidence, target, '
          + 'and linked learning resources.'
        )
        : (
          'Your current profile does not show an '
          + 'unresolved gap for this career.'
        )
    )

  const nextActionTitle =
    nextGap
      ? `Start with ${nextGap.skill_name}`
      : (
        unresolvedGapCount > 0
          ? 'Review your unresolved gaps'
          : 'Continue your career plan'
      )

  const profileEvidenceLabel =
    profileLoading
      ? 'Loading'
      : (
        `${profileEvidence.itemCount} evidence items · `
        + `${profileEvidence.areaCount} profile areas`
      )

  const roadmapProgressLabel =
    roadmapTotal > 0
      ? (
        `${roadmapCompleted} of `
        + `${roadmapTotal} steps complete`
      )
      : 'No roadmap steps yet'

  const latestHistory =
    interviewHistory.slice(
      0,
      MAX_VISIBLE_HISTORY,
    )

  const isCareerDataLoading =
    isCareerContextLoading
    || currentCareerState
      .isLoading

  const careerUnavailable =
    !dashboardCareerId

  const dashboardError =
    profileError
    || careerContextError
    || currentCareerState.error

  const nextGapSkillId =
    Number(
      nextGap
        ?.skill_id,
    )

  const learningResourcesPath =
    dashboardCareerId
    && Number.isInteger(
      nextGapSkillId,
    )
    && nextGapSkillId > 0
      ? (
        '/learning-resources'
        + `?career_id=${dashboardCareerId}`
        + `&skill_id=${nextGapSkillId}`
      )
      : '/learning-resources'


  return (
    <main className="student-dashboard-v2">
      <div className="student-dashboard-v2__content">
        <header className="student-dashboard-v2__header">
          <div>
            <h1>
              Dashboard
            </h1>

            <p>
              Your primary career, current progress,
              and the next action worth taking.
            </p>
          </div>

          <div
            className="student-dashboard-v2__account"
            aria-label={
              `Signed in as ${accountName}`
            }
          >
            <span aria-hidden="true">
              {accountInitial}
            </span>

            <strong>
              {accountName}
            </strong>
          </div>
        </header>


        {dashboardError && (
          <section
            className="student-dashboard-v2__notice"
            role="status"
          >
            <strong>
              Some dashboard information is unavailable.
            </strong>

            <p>
              {dashboardError}
            </p>
          </section>
        )}


        <section className="student-dashboard-v2__hero">
          <div className="student-dashboard-v2__hero-main">
            <span className="student-dashboard-v2__eyebrow">
              PRIMARY CAREER
            </span>

            <h2>
              {
                isCareerContextLoading
                  ? 'Loading career'
                  : (
                    primaryCareerName
                    || 'Primary career not set'
                  )
              }
            </h2>

            <p>
              Your default career focus comes from the
              Primary Career Goal in Student Profile.
            </p>

            {topCareerName && (
              <div className="student-dashboard-v2__top-match">
                <span>
                  Top recommendation
                </span>

                <strong>
                  {topCareerName}
                </strong>

                {
                  topCareerScore !== 'Not scored'
                  && (
                    <span>
                      {topCareerScore} match
                    </span>
                  )
                }
              </div>
            )}

            <div className="student-dashboard-v2__hero-actions">
              <button
                className="student-dashboard-v2__button student-dashboard-v2__button--primary"
                type="button"
                disabled={careerUnavailable}
                onClick={() =>
                  navigate(
                    '/career-roadmap',
                  )
                }
              >
                View Career Plan
              </button>

              <button
                className="student-dashboard-v2__button"
                type="button"
                onClick={() =>
                  navigate(
                    '/profile',
                  )
                }
              >
                Edit Primary Career
              </button>
            </div>
          </div>

          <aside className="student-dashboard-v2__readiness">
            <span>
              CAREER READINESS
            </span>

            <strong>
              {
                isCareerDataLoading
                  ? 'Loading'
                  : readinessScore
              }
            </strong>

            <p>
              Based on your current profile evidence
            </p>

            <div
              className="student-dashboard-v2__progress-track"
              aria-hidden="true"
            >
              <span
                style={{
                  width:
                    `${readinessProgress}%`,
                }}
              />
            </div>

            <small>
              {
                isCareerDataLoading
                  ? 'Loading unresolved gaps'
                  : (
                    `${unresolvedGapCount} unresolved `
                    + (
                      unresolvedGapCount === 1
                        ? 'gap'
                        : 'gaps'
                    )
                    + ' need attention'
                  )
              }
            </small>

            <small>
              {
                isCareerDataLoading
                  ? 'Loading roadmap progress'
                  : roadmapProgressLabel
              }
            </small>
          </aside>
        </section>


        <section className="student-dashboard-v2__summary">
          <div className="student-dashboard-v2__section-heading">
            <h2>
              Progress at a glance
            </h2>

            <p>
              One view of your evidence, development gaps,
              and roadmap progress.
            </p>
          </div>

          <div className="student-dashboard-v2__summary-grid">
            <div>
              <span>
                PROFILE EVIDENCE
              </span>

              <strong>
                {profileEvidenceLabel}
              </strong>
            </div>

            <div>
              <span>
                UNRESOLVED GAPS
              </span>

              <strong>
                {
                  isCareerDataLoading
                    ? 'Loading'
                    : (
                      `${unresolvedGapCount} `
                      + (
                        unresolvedGapCount === 1
                          ? 'needs'
                          : 'need'
                      )
                      + ' attention'
                    )
                }
              </strong>
            </div>

            <div>
              <span>
                ROADMAP
              </span>

              <strong>
                {
                  isCareerDataLoading
                    ? 'Loading'
                    : roadmapProgressLabel
                }
              </strong>
            </div>
          </div>
        </section>


        <section className="student-dashboard-v2__focus-grid">
          <article className="student-dashboard-v2__next-action">
            <span className="student-dashboard-v2__eyebrow">
              NEXT BEST ACTION
            </span>

            <h2>
              {
                isCareerDataLoading
                  ? 'Loading your next action'
                  : nextActionTitle
              }
            </h2>

            <p>
              {
                careerUnavailable
                  ? (
                    'Set a Primary Career Goal in '
                    + 'Student Profile to start your plan.'
                  )
                  : nextActionDescription
              }
            </p>

            <div className="student-dashboard-v2__hero-actions">
              <button
                className="student-dashboard-v2__button student-dashboard-v2__button--primary"
                type="button"
                onClick={() =>
                  navigate(
                    careerUnavailable
                      ? '/profile'
                      : '/skill-gap-analysis',
                  )
                }
              >
                {
                  careerUnavailable
                    ? 'Set Primary Career'
                    : 'View Skill Gap'
                }
              </button>

              <button
                className="student-dashboard-v2__button"
                type="button"
                disabled={careerUnavailable}
                onClick={() =>
                  navigate(
                    learningResourcesPath,
                  )
                }
              >
                Learning Resources
              </button>
            </div>
          </article>


          <article className="student-dashboard-v2__gaps">
            <div className="student-dashboard-v2__section-heading">
              <h2>
                Current skill gaps
              </h2>

              <p>
                Highest-priority development needs
              </p>
            </div>

            {
              isCareerDataLoading
                ? (
                  <div className="student-dashboard-v2__gaps-empty">
                    Loading skill gaps...
                  </div>
                )
                : currentGaps.length > 0
                  ? (
                    <div className="student-dashboard-v2__gap-list">
                      {
                        currentGaps.map(
                          (
                            gap,
                            index,
                          ) => (
                            <div
                              className="student-dashboard-v2__gap-row"
                              key={
                                gap.skill_id
                                || gap.skill_name
                                || index
                              }
                            >
                              <strong>
                                {gap.skill_name}
                              </strong>

                              <span>
                                {
                                  formatGapStatus(
                                    gap.status,
                                  )
                                }
                              </span>
                            </div>
                          ),
                        )
                      }
                    </div>
                  )
                  : (
                    <div className="student-dashboard-v2__gaps-empty">
                      No unresolved gaps found.
                    </div>
                  )
            }

            <button
              className="student-dashboard-v2__text-link"
              type="button"
              disabled={careerUnavailable}
              onClick={() =>
                navigate(
                  '/skill-gap-analysis',
                )
              }
            >
              View all skill gaps
              <ArrowRight
                size={15}
                strokeWidth={1.8}
                aria-hidden="true"
              />
            </button>
          </article>
        </section>


        <section className="student-dashboard-v2__tools">
          <div className="student-dashboard-v2__section-heading">
            <h2>
              Preparation tools
            </h2>

            <p>
              Continue where you left off.
            </p>
          </div>

          <div className="student-dashboard-v2__tool-grid">
            <PreparationTool
              icon={FileText}
              title="Resume Builder"
              status="Ready"
              onClick={() =>
                navigate(
                  '/resume-builder',
                )
              }
            />

            <PreparationTool
              icon={BriefcaseBusiness}
              title="Cover Letter"
              status="Ready"
              onClick={() =>
                navigate(
                  '/cover-letter-builder',
                )
              }
            />

            <PreparationTool
              icon={MessageSquare}
              title="Interview Prep"
              status="Pending integration"
              disabled
            />

            <PreparationTool
              icon={GraduationCap}
              title="Learning Resources"
              status="Personalised"
              onClick={() =>
                navigate(
                  learningResourcesPath,
                )
              }
            />
          </div>
        </section>


        <section className="student-dashboard-v2__history">
          <div className="student-dashboard-v2__history-heading">
            <div className="student-dashboard-v2__section-heading">
              <h2>
                Recent interview activity
              </h2>

              <p>
                Completed Interview Preparation sessions.
                Typed answers and AI feedback text are not stored.
              </p>
            </div>

            <span>
              {interviewHistory.length} completed
            </span>
          </div>

          {historyLoading && (
            <div className="student-dashboard-v2__history-state">
              Loading Interview History...
            </div>
          )}

          {
            !historyLoading
            && historyError
            && (
              <div
                className="student-dashboard-v2__history-state"
                role="status"
              >
                {historyError}
              </div>
            )
          }

          {
            !historyLoading
            && !historyError
            && latestHistory.length === 0
            && (
              <div className="student-dashboard-v2__history-state">
                <MessageSquare
                  size={22}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />

                <strong>
                  No completed interview sessions yet
                </strong>

                <p>
                  Completed Interview Preparation sessions
                  will appear here.
                </p>
              </div>
            )
          }

          {
            !historyLoading
            && !historyError
            && latestHistory.length > 0
            && (
              <div className="student-dashboard-v2__history-table-wrap">
                <table className="student-dashboard-v2__history-table">
                  <thead>
                    <tr>
                      <th scope="col">
                        Role
                      </th>

                      <th scope="col">
                        Date
                      </th>

                      <th scope="col">
                        Questions
                      </th>

                      <th scope="col">
                        With feedback
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {
                      latestHistory.map(
                        (session) => (
                          <tr key={session.id}>
                            <td>
                              {session.target_role}
                            </td>

                            <td>
                              {
                                formatInterviewDate(
                                  session.completed_at,
                                )
                              }
                            </td>

                            <td>
                              {session.total_questions}
                            </td>

                            <td>
                              {
                                session
                                  .questions_with_feedback
                              }
                            </td>
                          </tr>
                        ),
                      )
                    }
                  </tbody>
                </table>
              </div>
            )
          }

          <p className="student-dashboard-v2__history-privacy">
            Interview history stores metadata only.
          </p>
        </section>
      </div>
    </main>
  )
}


export default StudentDashboardPage
