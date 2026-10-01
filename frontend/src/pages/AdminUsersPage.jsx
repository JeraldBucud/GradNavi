import {
  useEffect,
  useState,
} from 'react'

import { listAdminUsers } from '../services/adminService'

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


function AdminUsersPage() {
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')


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
                  </tr>
                </thead>

                <tbody>
                  {visibleUsers.map((user) => (
                    <tr key={user.id}>
                      <td>{getFullName(user)}</td>
                      <td>{user.email}</td>
                      <td>
                        <span
                          className={`admin-users__pill admin-users__pill--${user.role}`}
                        >
                          {user.role === 'admin' ? 'Admin' : 'Student'}
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
    </div>
  )
}


export default AdminUsersPage