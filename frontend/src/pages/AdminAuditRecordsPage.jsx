import {
  useEffect,
  useState,
} from 'react'
import {
  Link,
  useSearchParams,
} from 'react-router'

import {
  listAdminAuditRecords,
  listAdminUsers,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'
import './AdminCareersPage.css'


const PAGE_SIZE = 50


function formatDateTime(value) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString('en-AU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
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


function formatMetadataValue(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}


function AdminAuditRecordsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const actionParam = searchParams.get('action') || ''
  const targetParam = searchParams.get('target_id') || ''
  const hasLinkFilter = Boolean(actionParam || targetParam)

  const [records, setRecords] = useState([])
  const [usersById, setUsersById] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [areaFilter, setAreaFilter] = useState('all')
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)
  const [selectedRecord, setSelectedRecord] = useState(null)


  useEffect(() => {
    let isCancelled = false

    async function loadRecords() {
      try {
        const [recordResult, userResult] = await Promise.all([
          listAdminAuditRecords(),
          listAdminUsers(),
        ])

        if (!isCancelled) {
          const lookup = {}

          userResult.forEach((user) => {
            lookup[user.id] = user
          })

          const sorted = [...recordResult].sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at),
          )

          setRecords(sorted)
          setUsersById(lookup)
        }
      }
      catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message
            || 'Could not load audit records. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadRecords()

    return () => {
      isCancelled = true
    }
  }, [])


  useEffect(() => {
    if (!selectedRecord) {
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setSelectedRecord(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [selectedRecord])


  function getActorLabel(actorId) {
    if (!actorId) {
      return 'System'
    }

    const actor = usersById[actorId]

    return actor ? actor.email : `User #${actorId}`
  }


  function handleSearchChange(event) {
    setSearchText(event.target.value)
    setVisibleCount(PAGE_SIZE)
  }


  function handleAreaChange(event) {
    setAreaFilter(event.target.value)
    setVisibleCount(PAGE_SIZE)
  }


  function clearLinkFilter() {
    setSearchParams({})
    setVisibleCount(PAGE_SIZE)
  }


  const areas = [...new Set(
    records.map((record) => record.area).filter(Boolean),
  )].sort()

  const normalisedSearch = searchText.trim().toLowerCase()

  const filteredRecords = records.filter((record) => {
    const matchesLink =
      (!actionParam || record.action === actionParam)
      && (!targetParam || String(record.target_id) === targetParam)

    const matchesArea =
      areaFilter === 'all' || record.area === areaFilter

    const matchesSearch =
      !normalisedSearch
      || (record.action || '').toLowerCase().includes(normalisedSearch)
      || (record.target_type || '').toLowerCase().includes(normalisedSearch)
      || String(record.target_id || '').includes(normalisedSearch)
      || getActorLabel(record.actor).toLowerCase().includes(normalisedSearch)

    return matchesLink && matchesArea && matchesSearch
  })

  const visibleRecords = filteredRecords.slice(0, visibleCount)


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>Audit Records</h1>
          <p>
            A read-only history of administrative changes in GradNavi.
          </p>
        </div>
      </header>

      {errorMessage && (
        <section className="career-guidance-state-card" role="alert">
          <h2>Something went wrong</h2>
          <p>{errorMessage}</p>
        </section>
      )}

      {hasLinkFilter && (
        <div className="admin-users__success" role="status">
          <span>
            Showing records for
            {' '}<strong>{formatAuditAction(actionParam) || 'all actions'}</strong>
            {targetParam && <> on target #{targetParam}</>}.
          </span>
          <button
            type="button"
            className="admin-users__link-button"
            onClick={clearLinkFilter}
          >
            Show all records
          </button>
        </div>
      )}

      {!errorMessage && (
        <section className="career-guidance-section">
          <div className="admin-users__filters">
            <label className="admin-users__field">
              <span>Search</span>
              <input
                type="search"
                value={searchText}
                onChange={handleSearchChange}
                placeholder="Search action, target or admin"
              />
            </label>

            <label className="admin-users__field">
              <span>Area</span>
              <select
                value={areaFilter}
                onChange={handleAreaChange}
              >
                <option value="all">All areas</option>
                {areas.map((area) => (
                  <option key={area} value={area}>
                    {area}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {isLoading && (
            <p className="admin-dashboard__empty">Loading audit records…</p>
          )}

          {!isLoading && filteredRecords.length === 0 && (
            <p className="admin-dashboard__empty">
              No audit records match your search.
            </p>
          )}

          {!isLoading && filteredRecords.length > 0 && (
            <div className="admin-users__table-wrap">
              <table className="admin-users__table">
                <thead>
                  <tr>
                    <th scope="col">When</th>
                    <th scope="col">Admin</th>
                    <th scope="col">Action</th>
                    <th scope="col">Target</th>
                    <th scope="col">Details</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleRecords.map((record) => (
                    <tr key={record.id}>
                      <td>{formatDateTime(record.created_at)}</td>
                      <td>{getActorLabel(record.actor)}</td>
                      <td>{formatAuditAction(record.action)}</td>
                      <td>
                        {record.target_type || '—'}
                        {record.target_id ? ` #${record.target_id}` : ''}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="admin-users__action-button"
                          onClick={() => setSelectedRecord(record)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading && filteredRecords.length > visibleCount && (
            <div className="admin-skills__more">
              <button
                type="button"
                className="admin-users__secondary-button"
                onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}
              >
                Show more
              </button>
            </div>
          )}

          {!isLoading && (
            <p className="admin-users__count">
              Showing {visibleRecords.length} of {filteredRecords.length} matching
              {' '}({records.length} total)
            </p>
          )}
        </section>
      )}

      {selectedRecord && (
        <div
          className="admin-users__backdrop"
          onClick={() => setSelectedRecord(null)}
        >
          <div
            className="admin-users__dialog admin-audit__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="audit-dialog-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="audit-dialog-title">
              Audit record #{selectedRecord.id}
            </h2>

            <dl className="admin-audit__details">
              <dt>When</dt>
              <dd>{formatDateTime(selectedRecord.created_at)}</dd>

              <dt>Admin</dt>
              <dd>{getActorLabel(selectedRecord.actor)}</dd>

              <dt>Action</dt>
              <dd>
                {formatAuditAction(selectedRecord.action)}
                <code>{selectedRecord.action}</code>
              </dd>

              <dt>Area</dt>
              <dd>{selectedRecord.area || '—'}</dd>

              <dt>Target</dt>
              <dd>
                {selectedRecord.target_type || '—'}
                {selectedRecord.target_id ? ` #${selectedRecord.target_id}` : ''}
              </dd>

              {Object.entries(selectedRecord.metadata || {}).map(([key, value]) => (
                <div key={key} className="admin-audit__meta-row">
                  <dt>{key.replace(/_/g, ' ')}</dt>
                  <dd>{formatMetadataValue(value)}</dd>
                </div>
              ))}
            </dl>

            <div className="admin-users__dialog-actions">
              <button
                type="button"
                className="admin-users__secondary-button"
                onClick={() => setSelectedRecord(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <p className="admin-users__count">
        <Link to="/admin">Back to dashboard</Link>
      </p>
    </div>
  )
}


export default AdminAuditRecordsPage