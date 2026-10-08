import {
  useEffect,
  useState,
} from 'react'
import { Link, useNavigate } from 'react-router'

import {
  listAdminUsers,
  updateAdminUserRole,
  updateAdminUserStatus,
} from '../services/adminService'
import { getStoredUser } from '../services/authService'
import { clearAuthSession } from '../services/authStorage'
import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'
import './AdminCareersPage.css'


const ROLE_FILTERS = [
  { value: 'all', label: 'All roles' },
  { value: 'student', label: 'Students' },
  { value: 'admin', label: 'Admins' },
]

const STATUS_FILTERS = [
  { value: 'all', label: 'All statuses' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
]


function formatDate(value) {
  if (!value) {
    return 'Never'
  }

  return new Date(value).toLocaleDateString('en-AU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}


function getFullName(user) {
  const name = `${user.first_name || ''} ${user.last_name || ''}`.trim()

  return name || 'No name'
}


function getRoleLabel(role) {
  return role === 'admin' ? 'Admin' : 'Student'
}


function getAuditLink(action, userId) {
  return `/admin/audit-records?action=${action}&target_id=${userId}`
}


function AdminUsersPage() {
  const navigate = useNavigate()
  const currentUser = getStoredUser()

  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  const [pendingChange, setPendingChange] = useState(null)
  const [isSaving, setIsSaving] = useState(false)
  const [dialogError, setDialogError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [auditLink, setAuditLink] = useState('')


  useEffect(() => {
    let isCancelled = false

    async function loadUsers() {
      try {
        const result = await listAdminUsers()

        if (!isCancelled) {
          setUsers(result)
        }
      }
      catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message
            || 'Could not load users. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadUsers()

    return () => {
      isCancelled = true
    }
  }, [])


  useEffect(() => {
    if (!pendingChange) {
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !isSaving) {
        setPendingChange(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [pendingChange, isSaving])


  function isOwnAccount(user) {
    return Boolean(
      currentUser
      && String(currentUser.id) === String(user.id),
    )
  }


  function clearMessages() {
    setSuccessMessage('')
    setAuditLink('')
    setDialogError('')
  }


  function openRoleDialog(user) {
    clearMessages()
    setPendingChange({
      type: 'role',
      user,
      newRole: user.role === 'admin' ? 'student' : 'admin',
    })
  }


  function openStatusDialog(user) {
    clearMessages()
    setPendingChange({
      type: 'status',
      user,
      newIsActive: !user.is_active,
    })
  }


  function closeDialog() {
    if (isSaving) {
      return
    }

    setPendingChange(null)
    setDialogError('')
  }


  function replaceUser(userId, changes) {
    setUsers((previous) => previous.map((item) => (
      item.id === userId ? { ...item, ...changes } : item
    )))
  }


  async function handleConfirmRoleChange() {
    const { user, newRole } = pendingChange
    const updated = await updateAdminUserRole(user.id, newRole)

    if (isOwnAccount(user)) {
      clearAuthSession()
      navigate('/login', {
        replace: true,
        state: {
          message: 'Your role was changed. Please sign in again.',
        },
      })
      return
    }

    replaceUser(updated.id, { role: updated.role })
    setSuccessMessage(
      `${getFullName(user)} is now ${getRoleLabel(updated.role)}. `
      + 'This change was recorded in the audit log.',
    )
    setAuditLink(getAuditLink('admin.user.role_changed', updated.id))
  }


  async function handleConfirmStatusChange() {
    const { user, newIsActive } = pendingChange
    const updated = await updateAdminUserStatus(user.id, newIsActive)

    replaceUser(updated.id, { is_active: updated.is_active })
    setSuccessMessage(
      `${getFullName(user)} is now ${updated.is_active ? 'active' : 'inactive'}. `
      + 'This change was recorded in the audit log.',
    )
    setAuditLink(getAuditLink('admin.user.status_changed', updated.id))
  }


  async function handleConfirm() {
    setIsSaving(true)
    setDialogError('')

    try {
      if (pendingChange.type === 'role') {
        await handleConfirmRoleChange()
      }
      else {
        await handleConfirmStatusChange()
      }

      setPendingChange(null)
    }
    catch (error) {
      setDialogError(
        error.message
        || 'Could not save the change. Please try again.',
      )
    }
    finally {
      setIsSaving(false)
    }
  }


  const normalisedSearch = searchText.trim().toLowerCase()

  const visibleUsers = users.filter((user) => {
    const matchesRole =
      roleFilter === 'all' || user.role === roleFilter

    const matchesStatus =
      statusFilter === 'all'
      || (statusFilter === 'active' && user.is_active)
      || (statusFilter === 'inactive' && !user.is_active)

    const matchesSearch =
      !normalisedSearch
      || getFullName(user).toLowerCase().includes(normalisedSearch)
      || user.email.toLowerCase().includes(normalisedSearch)

    return matchesRole && matchesStatus && matchesSearch
  })


  function renderDialogBody() {
    const { type, user } = pendingChange

    if (type === 'role') {
      return (
        <>
          <p>
            Change <strong>{getFullName(user)}</strong>
            {' '}({user.email}) from
            {' '}<strong>{getRoleLabel(user.role)}</strong> to
            {' '}<strong>{getRoleLabel(pendingChange.newRole)}</strong>?
          </p>

          {pendingChange.newRole === 'admin' && (
            <p className="admin-users__warning">
              Admins can manage users, careers, skills and learning
              resources. Only give this role to trusted staff.
            </p>
          )}

          {isOwnAccount(user) && (
            <p className="admin-users__warning">
              This is your own account. You will be signed out and
              may lose access to the admin area.
            </p>
          )}
        </>
      )
    }

    return (
      <>
        <p>
          {pendingChange.newIsActive ? 'Activate' : 'Deactivate'}
          {' '}<strong>{getFullName(user)}</strong> ({user.email})?
        </p>

        {!pendingChange.newIsActive && (
          <p className="admin-users__warning">
            This user will not be able to log in until the account is
            activated again. Their data is kept.
          </p>
        )}
      </>
    )
  }


  function getDialogTitle() {
    if (pendingChange.type === 'role') {
      return 'Change user role?'
    }

    return pendingChange.newIsActive ? 'Activate user?' : 'Deactivate user?'
  }


  function getConfirmLabel() {
    if (isSaving) {
      return 'Saving…'
    }

    if (pendingChange.type === 'role') {
      return 'Confirm change'
    }

    return pendingChange.newIsActive ? 'Activate' : 'Deactivate'
  }


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>User Management</h1>
          <p>
            View GradNavi accounts, roles and account status.
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
            {successMessage}
            {auditLink && (
              <>
                {' '}
                <Link to={auditLink}>View audit record</Link>
              </>
            )}
          </span>
          <button
            type="button"
            className="admin-users__link-button"
            onClick={() => {
              setSuccessMessage('')
              setAuditLink('')
            }}
          >
            Dismiss
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
                onChange={(event) => setSearchText(event.target.value)}
                placeholder="Search by name or email"
              />
            </label>

            <label className="admin-users__field">
              <span>Role</span>
              <select
                value={roleFilter}
                onChange={(event) => setRoleFilter(event.target.value)}
              >
                {ROLE_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

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
            <p className="admin-dashboard__empty">Loading users…</p>
          )}

          {!isLoading && visibleUsers.length === 0 && (
            <p className="admin-dashboard__empty">
              No users match your search.
            </p>
          )}

          {!isLoading && visibleUsers.length > 0 && (
            <div className="admin-users__table-wrap">
              <table className="admin-users__table">
                <thead>
                  <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Email</th>
                    <th scope="col">Role</th>
                    <th scope="col">Status</th>
                    <th scope="col">Joined</th>
                    <th scope="col">Last login</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleUsers.map((user) => {
                    const ownAccount = isOwnAccount(user)

                    return (
                      <tr key={user.id}>
                        <td>
                          {getFullName(user)}
                          {ownAccount && (
                            <span className="admin-users__you"> (you)</span>
                          )}
                        </td>
                        <td>{user.email}</td>
                        <td>
                          <span
                            className={`admin-users__pill admin-users__pill--${user.role}`}
                          >
                            {getRoleLabel(user.role)}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`admin-users__pill ${user.is_active ? 'admin-users__pill--active' : 'admin-users__pill--inactive'}`}
                          >
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>{formatDate(user.date_joined)}</td>
                        <td>{formatDate(user.last_login)}</td>
                        <td>
                          <div className="admin-careers__row-actions">
                            <button
                              type="button"
                              className="admin-users__action-button"
                              onClick={() => openRoleDialog(user)}
                            >
                              {user.role === 'admin' ? 'Make student' : 'Make admin'}
                            </button>
                            <button
                              type="button"
                              className="admin-users__action-button"
                              onClick={() => openStatusDialog(user)}
                              disabled={ownAccount}
                              title={
                                ownAccount
                                  ? 'You cannot deactivate your own account.'
                                  : undefined
                              }
                            >
                              {user.is_active ? 'Deactivate' : 'Activate'}
                            </button>
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
              Showing {visibleUsers.length} of {users.length} users
            </p>
          )}
        </section>
      )}

      {pendingChange && (
        <div
          className="admin-users__backdrop"
          onClick={closeDialog}
        >
          <div
            className="admin-users__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="user-dialog-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="user-dialog-title">{getDialogTitle()}</h2>

            {renderDialogBody()}

            <p className="admin-users__dialog-note">
              This change will be recorded in the audit log.
            </p>

            {dialogError && (
              <p className="admin-users__dialog-error" role="alert">
                {dialogError}
              </p>
            )}

            <div className="admin-users__dialog-actions">
              <button
                type="button"
                className="admin-users__secondary-button"
                onClick={closeDialog}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                type="button"
                className="admin-users__primary-button"
                onClick={handleConfirm}
                disabled={isSaving}
              >
                {getConfirmLabel()}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


export default AdminUsersPage