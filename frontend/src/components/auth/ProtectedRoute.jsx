import { useEffect, useState } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router'

import {
  clearAuthSession,
  getCurrentUser,
  refreshAccessToken,
} from '../../services/authService'

function ProtectedRoute() {
  const location = useLocation()

  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    async function checkAuthentication() {
      const accessToken = localStorage.getItem('gradnavi_access_token')

      if (!accessToken) {
        setIsAuthenticated(false)
        setIsCheckingAuth(false)
        return
      }

      try {
        await getCurrentUser()

        setIsAuthenticated(true)
      } catch (requestError) {
        if (requestError.status === 401) {
          try {
            await refreshAccessToken()
            await getCurrentUser()

            setIsAuthenticated(true)
            return
          } catch {
            clearAuthSession()
            setIsAuthenticated(false)
          }
        } else {
          clearAuthSession()
          setIsAuthenticated(false)
        }
      } finally {
        setIsCheckingAuth(false)
      }
    }

    checkAuthentication()
  }, [])

  if (isCheckingAuth) {
    return <p>Checking authentication...</p>
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        state={{ from: location.pathname }}
        replace
      />
    )
  }

  return <Outlet />
}

export default ProtectedRoute