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
    try {
      await logoutAccount()
    } finally {
      /*
       * logoutAccount clears the local authentication
       * session even when the backend request fails.
       *
       * Navigation therefore also needs to finish
       * regardless of the server response.
       */
      navigate('/login', {
        replace: true,
      })
    }
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


          <Link to="/">
            Home
          </Link>


          {currentUser ? (
            <>
              <Link to="/profile">
                Student Profile
              </Link>

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
              <Link to="/login">
                Login
              </Link>

              <Link to="/register">
                Register
              </Link>
            </>
          )}
        </nav>
      </header>


      <Outlet key={location.pathname} />
    </>
  )
}


export default MainLayout