import {
  useEffect,
  useState,
} from 'react'
import { Link } from 'react-router'

import {
  getAdminAnalytics,
  getAdminDashboardSummary,
  listAdminAuditRecords,
  listAdminUsers,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'


const ANALYTICS_LIMIT = 5
const RECENT_ACTIVITY_LIMIT = 5
const RECENT_DAYS = 7
const DAY_IN_MS = 24 * 60 * 60 * 1000


function formatStudentCount(count) {
  return count === 1 ? '1 student' : `${count} students`
}


function formatAuditAction(action) {
  if (!action) {
    return '—'
  }

  const text = action
    .replace(/^admin\./, '')
    .replace(/[._]/g, ' ')
    .trim()

  return text.charAt(0).toUpperCase() + text.slice(1)
}


function formatDateTime(value) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString('en-AU', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}


function getAuditLink(record) {
  const params = new URLSearchParams()

  if (record.action) {
    params.set('action', record.action)
  }

  if (record.target_id) {
    params.set('target_id', String(record.target_id))
  }

  return `/admin/audit-records?${params.toString()}`
}


function AdminDashboardPage() {
  const [summary, setSummary] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [auditRecords, setAuditRecords] = useState([])
  const [recentChangeCount, setRecentChangeCount] = useState(0)
  const [usersById, setUsersById] = useState({})
  const [isAuditUnavailable, setIsAuditUnavailable] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [isPermissionDenied, setIsPermissionDenied] = useState(false)


  useEffect(() => {
    let isCancelled = false

    async function loadAuditActivity() {
      try {
        const [recordResult, userResult] = await Promise.all([
          listAdminAuditRecords(),
          listAdminUsers(),
        ])

        if (isCancelled) {
          return
        }

        const lookup = {}

        userResult.forEach((user) => {
          lookup[user.id] = user
        })

        const sorted = [...recordResult].sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at),
        )

        const recentCutoff = Date.now() - RECENT_DAYS * DAY_IN_MS

        setAuditRecords(sorted)
        setRecentChangeCount(
          sorted.filter(
            (record) => new Date(record.created_at).getTime() >= recentCutoff,
          ).length,
        )
        setUsersById(lookup)
      }
      catch {
        if (!isCancelled) {
          setIsAuditUnavailable(true)
        }
      }
    }

    async function loadDashboard() {
      try {
        const [summaryResult, analyticsResult] = await Promise.all([
          getAdminDashboardSummary(),
          getAdminAnalytics(),
          loadAuditActivity(),
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


  function getActorLabel(actorId) {
    if (!actorId) {
      return 'System'
    }

    const actor = usersById[actorId]

    return actor ? actor.email : `User #${actorId}`
  }


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


  /* Pending reports card */

  const pendingReportCount = summary?.pendingReportCount ?? 0

  let pendingReportText = 'No open resource reports.'
  let pendingBadge = pendingReportCount > 0 ? 'Review' : 'Clear'
  let pendingTone = pendingReportCount > 0 ? 'warning' : 'success'

  if (isLoading) {
    pendingReportText = 'Checking for open reports…'
    pendingBadge = 'Checking'
    pendingTone = 'neutral'
  }
  else if (pendingReportCount === 1) {
    pendingReportText = '1 open report is waiting for review.'
  }
  else if (pendingReportCount > 1) {
    pendingReportText = `${pendingReportCount} open reports are waiting for review.`
  }


  /* Recent admin changes card */

  let recentChangesText = `No admin changes in the last ${RECENT_DAYS} days.`

  if (isLoading) {
    recentChangesText = 'Checking recent changes…'
  }
  else if (isAuditUnavailable) {
    recentChangesText = 'Audit records could not be loaded.'
  }
  else if (recentChangeCount === 1) {
    recentChangesText = `1 admin change in the last ${RECENT_DAYS} days.`
  }
  else if (recentChangeCount > 1) {
    recentChangesText = `${recentChangeCount} admin changes in the last ${RECENT_DAYS} days.`
  }


  const attentionCards = [
    {
      badge: pendingBadge,
      tone: pendingTone,
      title: 'Pending resource reports',
      text: pendingReportText,
      link: { to: '/admin/reports', label: 'Review reports' },
    },
    {
      badge: 'Info',
      tone: 'info',
      title: 'Recent admin changes',
      text: recentChangesText,
      link: isAuditUnavailable
        ? null
        : { to: '/admin/audit-records', label: 'View audit records' },
    },
    {
      badge: 'Unavailable',
      tone: 'neutral',
      title: 'Data health',
      text: 'Data health checks are not available yet.',
    },
  ]


  const recentActivity = auditRecords.slice(0, RECENT_ACTIVITY_LIMIT)


  /* Analytics */

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


  function renderRecentActivity() {
    if (isLoading) {
      return <p className="admin-dashboard__empty">Loading activity…</p>
    }

    if (isAuditUnavailable) {
      return (
        <p className="admin-dashboard__empty">
          Recent activity could not be loaded.
        </p>
      )
    }

    if (recentActivity.length === 0) {
      return (
        <p className="admin-dashboard__empty">
          No admin activity recorded yet.
        </p>
      )
    }

    return (
      <>
        <ol className="admin-dashboard__list">
          {recentActivity.map((record) => (
            <li key={record.id}>
              <span>
                <Link to={getAuditLink(record)}>
                  {formatAuditAction(record.action)}
                </Link>
                {' '}
                {record.target_type}
                {record.target_id ? ` #${record.target_id}` : ''}
                {' · '}
                {getActorLabel(record.actor)}
              </span>
              <span className="admin-dashboard__list-value">
                {formatDateTime(record.created_at)}
              </span>
            </li>
          ))}
        </ol>

        <p className="admin-users__count">
          <Link to="/admin/audit-records">View all audit records</Link>
        </p>
      </>
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
                  {item.link && !isLoading && (
                    <p>
                      <Link to={item.link.to}>{item.link.label}</Link>
                    </p>
                  )}
                </article>
              ))}
            </div>
          </section>

          <section className="career-guidance-section">
            <div className="career-guidance-section__heading">
              <h2>Recent activity</h2>
              <p>Latest administrative changes recorded by the system.</p>
            </div>

            {renderRecentActivity()}
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