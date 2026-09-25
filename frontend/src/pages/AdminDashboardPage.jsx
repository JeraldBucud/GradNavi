import {
  useEffect,
  useState,
} from 'react'

import { getAdminDashboardSummary } from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'


const attentionItems = [
  {
    badge: 'Review',
    tone: 'warning',
    title: 'Pending resource reports',
    text: 'Available once audit records (WBS 7.8) are connected.',
  },
  {
    badge: 'Info',
    tone: 'info',
    title: 'Recent admin changes',
    text: 'Available once audit records (WBS 7.8) are connected.',
  },
  {
    badge: 'Healthy',
    tone: 'success',
    title: 'Data health',
    text: 'No blocking data issues detected.',
  },
]


const analyticsItems = [
  {
    badge: 'Trend',
    tone: 'warning',
    title: 'Popular careers',
    text: 'Top selected and recommended careers.',
  },
  {
    badge: 'Gap',
    tone: 'info',
    title: 'Common skill gaps',
    text: 'Most frequent missing skills across student profiles.',
  },
  {
    badge: 'Info',
    tone: 'success',
    title: 'Analytics scope',
    text: 'Aggregated data only. No individual student details.',
  },
]


function AdminDashboardPage() {
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [isPermissionDenied, setIsPermissionDenied] = useState(false)


  useEffect(() => {
    let isCancelled = false

    async function loadSummary() {
      try {
        const result = await getAdminDashboardSummary()

        if (!isCancelled) {
          setSummary(result)
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

    loadSummary()

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
              {attentionItems.map((item) => (
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
                Values remain placeholders until the admin API
                supplies them.
              </p>
            </div>

            <div className="admin-dashboard__card-grid">
              {analyticsItems.map((item) => (
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
        </>
      )}
    </div>
  )
}


export default AdminDashboardPage