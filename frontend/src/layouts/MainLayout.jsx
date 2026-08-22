import {
  Link,
  Outlet,
  useLocation,
  useNavigate,
} from 'react-router'

import {
  getStoredUser,
  logoutAccount,
} from '../services/authService'
import './MainLayout.css'

function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const currentUser = getStoredUser()

  async function handleLogout() {
    await logoutAccount()

    navigate('/login', { replace: true })
  }

  return (
    <>
      <header className="main-header">
        <nav className="main-nav">
          <Link
            className="main-brand"
            to="/"
          >
            GradNavi
          </Link>

          <Link to="/">Home</Link>

          {currentUser ? (
            <>
              <Link to="/profile">Student Profile</Link>

              <button
                className="main-logout"
                type="button"
                onClick={handleLogout}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </nav>
      </header>

      <Outlet key={location.pathname} />
    </>
  )
}

export default MainLayout