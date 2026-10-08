import {
  useEffect,
  useState,
} from 'react'

import {
  listAdminLearningResources,
  listAdminResourceReports,
  updateAdminResourceReportStatus,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'
import './AdminCareersPage.css'


const STATUS_FILTERS = [
  { value: 'open', label: 'Open' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'dismissed', label: 'Dismissed' },
  { value: 'all', label: 'All statuses' },
]

const REASON_LABELS = {
  broken_link: 'Broken link',
  outdated: 'Outdated',
  not_relevant: 'Not relevant',
  too_difficult: 'Too difficult',
  requires_payment: 'Requires payment',
  duplicate: 'Duplicate',
  other: 'Other',
}

const STATUS_PILLS = {
  open: 'admin-users__pill--inactive',
  resolved: 'admin-users__pill--active',
  dismissed: 'admin-users__pill--student',
}


function formatDate(value) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleDateString('en-AU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}


function capitalise(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : ''
}


function AdminReportsPage() {
  const [reports, setReports] = useState([])
  const [resourcesById, setResourcesById] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [statusFilter, setStatusFilter] = useState('open')
  const [successMessage, setSuccessMessage] = useState('')
  const [actionError, setActionError] = useState('')
  const [savingId, setSavingId] = useState(null)


  useEffect(() => {
    let isCancelled = false

    async function loadReports() {
      try {
        const [reportResult, resourceResult] = await Promise.all([
          listAdminResourceReports(),
          listAdminLearningResources(),
        ])

        if (!isCancelled) {
          const lookup = {}

          resourceResult.forEach((resource) => {
            lookup[resource.id] = resource
          })

          setReports(reportResult)
          setResourcesById(lookup)
        }
      }
      catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message
            || 'Could not load reports. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadReports()

    return () => {
      isCancelled = true
    }
  }, [])


  async function handleStatusChange(report, nextStatus) {
    setSavingId(report.id)
    setSuccessMessage('')
    setActionError('')

    try {
      const updated = await updateAdminResourceReportStatus(
        report.id,
        nextStatus,
      )

      setReports((previous) => previous.map((item) => (
        item.id === updated.id ? updated : item
      )))

      const resource = resourcesById[report.learning_resource]
      const title = resource ? resource.title : `Resource #${report.learning_resource}`

      setSuccessMessage(
        `Report on "${title}" marked as ${updated.status}.`,
      )
    }
    catch (error) {
      setActionError(
        error.message
        || 'Could not update the report. Please try again.',
      )
    }
    finally {
      setSavingId(null)
    }
  }


  const visibleReports = reports.filter((report) => (
    statusFilter === 'all' || report.status === statusFilter
  ))

  const openCount = reports.filter((report) => report.status === 'open').length


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>Resource Reports</h1>
          <p>
            Review learning resource issues reported by students.
            {' '}{openCount} open.
          </p>
        </div>
      </header>

      {errorMessage && (
        <section className="career-guidance-state-card" role="alert">
          <h2>Something went wrong</h2>
          <p>{errorMessage}</p>
        </section>
      )}

      {successMessage && (
        <div className="admin-users__success" role="status">
          <span>
            {successMessage} This change was recorded in the audit log.
          </span>
          <button
            type="button"
            className="admin-users__link-button"
            onClick={() => setSuccessMessage('')}
          >
            Dismiss
          </button>
        </div>
      )}

      {actionError && (
        <p className="admin-users__dialog-error" role="alert">
          {actionError}
        </p>
      )}

      {!errorMessage && (
        <section className="career-guidance-section">
          <div className="admin-users__filters">
            <label className="admin-users__field">
              <span>Status</span>
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
              >
                {STATUS_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {isLoading && (
            <p className="admin-dashboard__empty">Loading reports…</p>
          )}

          {!isLoading && visibleReports.length === 0 && (
            <p className="admin-dashboard__empty">
              {statusFilter === 'open'
                ? 'No open reports. Nice work.'
                : 'No reports match this filter.'}
            </p>
          )}

          {!isLoading && visibleReports.length > 0 && (
            <div className="admin-users__table-wrap">
              <table className="admin-users__table">
                <thead>
                  <tr>
                    <th scope="col">Resource</th>
                    <th scope="col">Reason</th>
                    <th scope="col">Comment</th>
                    <th scope="col">Status</th>
                    <th scope="col">Reported</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleReports.map((report) => {
                    const resource = resourcesById[report.learning_resource]
                    const isSaving = savingId === report.id

                    return (
                      <tr key={report.id}>
                        <td>
                          {resource ? (
                            <a
                              href={resource.url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {resource.title}
                            </a>
                          ) : (
                            `Resource #${report.learning_resource}`
                          )}
                        </td>
                        <td>{REASON_LABELS[report.reason] || report.reason}</td>
                        <td className="admin-reports__comment">
                          {report.comment || '—'}
                        </td>
                        <td>
                          <span
                            className={`admin-users__pill ${STATUS_PILLS[report.status] || ''}`}
                          >
                            {capitalise(report.status)}
                          </span>
                        </td>
                        <td>{formatDate(report.created_at)}</td>
                        <td>
                          <div className="admin-careers__row-actions">
                            {report.status === 'open' ? (
                              <>
                                <button
                                  type="button"
                                  className="admin-users__action-button"
                                  onClick={() => handleStatusChange(report, 'resolved')}
                                  disabled={isSaving}
                                >
                                  Resolve
                                </button>
                                <button
                                  type="button"
                                  className="admin-users__action-button"
                                  onClick={() => handleStatusChange(report, 'dismissed')}
                                  disabled={isSaving}
                                >
                                  Dismiss
                                </button>
                              </>
                            ) : (
                              <button
                                type="button"
                                className="admin-users__action-button"
                                onClick={() => handleStatusChange(report, 'open')}
                                disabled={isSaving}
                              >
                                Reopen
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading && (
            <p className="admin-users__count">
              Showing {visibleReports.length} of {reports.length} reports
            </p>
          )}
        </section>
      )}
    </div>
  )
}


export default AdminReportsPage