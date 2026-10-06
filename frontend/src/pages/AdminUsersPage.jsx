import {
  useEffect,
  useState,
} from 'react'
import { Link, useNavigate } from 'react-router'

import {
  listAdminUsers,
  updateAdminUserRole,
} from '../services/adminService'
import { getStoredUser } from '../services/authService'
import { clearAuthSession } from '../services/authStorage'
import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'


const ROLE_FILTERS = [
  { value: 'all', label: 'All roles' },
  { value: 'student', label: 'Students' },
  { value: 'admin', label: 'Admins' },
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


function AdminUsersPage() {
  const navigate = useNavigate()
  const currentUser = getStoredUser()

  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')

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
    return (
      currentUser
      && String(currentUser.id) === String(user.id)
    )
  }


  function openRoleDialog(user) {
    setSuccessMessage('')
    setAuditLink('')
    setDialogError('')
    setPendingChange({
      user,
      newRole: user.role === 'admin' ? 'student' : 'admin',
    })
  }


  function closeRoleDialog() {
    if (isSaving) {
      return
    }

    setPendingChange(null)
    setDialogError('')
  }


  async function handleConfirmRoleChange() {
    const { user, newRole } = pendingChange

    setIsSaving(true)
    setDialogError('')

    try {
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

      setUsers((previous) => previous.map((item) => (
        item.id === updated.id
          ? { ...item, role: updated.role }
          : item
      )))

      setSuccessMessage(
        `${getFullName(user)} is now ${getRoleLabel(updated.role)}. `
        + 'This change was recorded in the audit log.',
      )
      setAuditLink(
        `/admin/audit-records?action=admin.user.role_changed&target_id=${updated.id}`,
      )
      setPendingChange(null)
    }
    catch (error) {
      setDialogError(
        error.message
        || 'Could not change the role. Please try again.',
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

    const matchesSearch =
      !normalisedSearch
      || getFullName(user).toLowerCase().includes(normalisedSearch)
      || user.email.toLowerCase().includes(normalisedSearch)

    return matchesRole && matchesSearch
  })


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
                  {visibleUsers.map((user) => (
                    <tr key={user.id}>
                      <td>
                        {getFullName(user)}
                        {isOwnAccount(user) && (
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
                        <button
                          type="button"
                          className="admin-users__action-button"
                          onClick={() => openRoleDialog(user)}
                        >
                          {user.role === 'admin' ? 'Make student' : 'Make admin'}
                        </button>
                      </td>
                    </tr>
                  ))}
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
          onClick={closeRoleDialog}
        >
          <div
            className="admin-users__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="role-dialog-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="role-dialog-title">Change user role?</h2>

            <p>
              Change <strong>{getFullName(pendingChange.user)}</strong>
              {' '}({pendingChange.user.email}) from
              {' '}<strong>{getRoleLabel(pendingChange.user.role)}</strong> to
              {' '}<strong>{getRoleLabel(pendingChange.newRole)}</strong>?
            </p>

            {pendingChange.newRole === 'admin' && (
              <p className="admin-users__warning">
                Admins can manage users, careers, skills and learning
                resources. Only give this role to trusted staff.
              </p>
            )}

            {isOwnAccount(pendingChange.user) && (
              <p className="admin-users__warning">
                This is your own account. You will be signed out and
                may lose access to the admin area.
              </p>
            )}

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
                onClick={closeRoleDialog}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                type="button"
                className="admin-users__primary-button"
                onClick={handleConfirmRoleChange}
                disabled={isSaving}
              >
                {isSaving ? 'Saving…' : 'Confirm change'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


export default AdminUsersPage