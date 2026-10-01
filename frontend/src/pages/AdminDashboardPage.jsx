import {
  useEffect,
  useState,
} from 'react'

import {
  getAdminAnalytics,
  getAdminDashboardSummary,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'


const ANALYTICS_LIMIT = 5


const attentionItems = [
  {
    badge: 'Info',
    tone: 'info',
    title: 'Recent admin changes',
    text: 'Available once audit records (WBS 7.8) are connected.',
  },
  {
    badge: 'Unavailable',
    tone: 'neutral',
    title: 'Data health',
    text: 'Data health checks are not available yet.',
  },
]


function formatStudentCount(count) {
  return count === 1 ? '1 student' : `${count} students`
}


function AdminDashboardPage() {
  const [summary, setSummary] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [isPermissionDenied, setIsPermissionDenied] = useState(false)


  useEffect(() => {
    let isCancelled = false

    async function loadDashboard() {
      try {
        const [summaryResult, analyticsResult] = await Promise.all([
          getAdminDashboardSummary(),
          getAdminAnalytics(),
        ])

        if (!isCancelled) {
          setSummary(summaryResult)
          setAnalytics(analyticsResult)
        }
      }
      catch (error) {
        if (isCancelled) {
          return
        }

        if (error.status === 401 || error.status === 403) {
          setIsPermissionDenied(true)
        }
        else {
          setErrorMessage(
            error.message
            || 'Could not load the admin dashboard. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      isCancelled = true
    }
  }, [])


  const metrics = [
    {
      label: 'Students',
      value: summary?.studentCount,
      note: 'registered student accounts',
    },
    {
      label: 'Careers',
      value: summary?.activeCareerCount,
      note: 'active career records',
    },
    {
      label: 'Skills',
      value: summary?.skillCount,
      note: 'canonical skills available',
    },
    {
      label: 'Resources',
      value: summary?.activeResourceCount,
      note: 'learning resources',
    },
  ]


  const pendingReportCount = summary?.pendingReportCount ?? 0

  let pendingReportText = 'No open resource reports.'

  if (isLoading) {
    pendingReportText = 'Checking for open reports…'
  }
  else if (pendingReportCount === 1) {
    pendingReportText = '1 open report is waiting for review.'
  }
  else if (pendingReportCount > 1) {
    pendingReportText = `${pendingReportCount} open reports are waiting for review.`
  }

  const attentionCards = [
    {
      badge: pendingReportCount > 0 ? 'Review' : 'Clear',
      tone: pendingReportCount > 0 ? 'warning' : 'success',
      title: 'Pending resource reports',
      text: pendingReportText,
    },
    ...attentionItems,
  ]


  const popularCareers = (analytics?.popular_careers ?? [])
    .slice(0, ANALYTICS_LIMIT)

  const commonSkillGaps = (analytics?.common_skill_gaps ?? [])
    .slice(0, ANALYTICS_LIMIT)

  const analyticsCards = [
    {
      badge: 'Trend',
      tone: 'warning',
      title: 'Popular careers',
      emptyText: 'No career selections yet.',
      rows: popularCareers.map((career) => ({
        key: career.career_id,
        label: career.career_name,
        value: formatStudentCount(career.selection_count),
      })),
    },
    {
      badge: 'Gap',
      tone: 'info',
      title: 'Common skill gaps',
      emptyText: 'No skill gaps recorded yet.',
      rows: commonSkillGaps.map((skill) => ({
        key: skill.skill_id,
        label: skill.skill_name,
        value: formatStudentCount(skill.affected_student_count),
      })),
    },
    {
      badge: 'Info',
      tone: 'success',
      title: 'Analytics scope',
      text: 'Aggregated data only. No individual student details.',
    },
  ]


  function renderAnalyticsBody(item) {
    if (!item.rows) {
      return <p>{item.text}</p>
    }

    if (isLoading) {
      return <p>Loading…</p>
    }

    if (item.rows.length === 0) {
      return <p>{item.emptyText}</p>
    }

    return (
      <ol className="admin-dashboard__list">
        {item.rows.map((row) => (
          <li key={row.key}>
            <span>{row.label}</span>
            <span className="admin-dashboard__list-value">
              {row.value}
            </span>
          </li>
        ))}
      </ol>
    )
  }


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>Admin Dashboard</h1>
          <p>
            Monitor GradNavi content, users, analytics
            and operational activity.
          </p>
        </div>
      </header>

      {isPermissionDenied && (
        <section className="career-guidance-state-card" role="alert">
          <h2>Administrator access required</h2>
          <p>
            You need an administrator account to view this page.
          </p>
        </section>
      )}

      {errorMessage && (
        <section className="career-guidance-state-card" role="alert">
          <h2>Something went wrong</h2>
          <p>{errorMessage}</p>
        </section>
      )}

      {!isPermissionDenied && !errorMessage && (
        <>
          <section className="admin-dashboard__metrics">
            {metrics.map((metric) => (
              <div
                key={metric.label}
                className="career-guidance-metric-card"
              >
                <span>{metric.label}</span>
                <strong>
                  {isLoading ? '…' : metric.value}
                </strong>
                <small>{metric.note}</small>
              </div>
            ))}
          </section>

          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <h2>Needs attention</h2>
              <p>Review items that need an administrator action.</p>
            </div>

            <div className="admin-dashboard__card-grid">
              {attentionCards.map((item) => (
                <article
                  key={item.title}
                  className={`admin-dashboard__card admin-dashboard__card--${item.tone}`}
                >
                  <span className="admin-dashboard__badge">
                    {item.badge}
                  </span>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <h2>Recent activity</h2>
              <p>Latest administrative changes recorded by the system.</p>
            </div>

            <p className="admin-dashboard__empty">
              No activity to show yet. Recent activity will appear
              here once audit records (WBS 7.8) are available.
            </p>
          </section>

          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <h2>Admin analytics</h2>
              <p>
                Aggregated product signals required by FR-15.
                Top {ANALYTICS_LIMIT} shown.
              </p>
            </div>

            <div className="admin-dashboard__card-grid">
              {analyticsCards.map((item) => (
                <article
                  key={item.title}
                  className={`admin-dashboard__card admin-dashboard__card--${item.tone}`}
                >
                  <span className="admin-dashboard__badge">
                    {item.badge}
                  </span>
                  <h3>{item.title}</h3>
                  {renderAnalyticsBody(item)}
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}


export default AdminDashboardPage