import { useEffect, useState } from 'react'
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

function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const [currentUser, setCurrentUser] = useState(getStoredUser())

  useEffect(() => {
    setCurrentUser(getStoredUser())
  }, [location.pathname])

  async function handleLogout() {
    await logoutAccount()

    setCurrentUser(null)
    navigate('/login', { replace: true })
  }

  return (
    <>
      <header>
        <nav>
          <Link to="/">GradNavi</Link>
          <Link to="/">Home</Link>

          {currentUser ? (
            <>
              <Link to="/profile">Student Profile</Link>

              <button
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

      <Outlet />
    </>
  )
}

export default MainLayout