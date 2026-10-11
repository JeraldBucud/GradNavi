import {
  useEffect,
  useState,
} from 'react'

import {
  Navigate,
  Outlet,
  useLocation,
} from 'react-router'

import {
  clearAuthSession,
  getCurrentUser,
  hasStoredAccessToken,
} from '../../services/authService'


function ProtectedRoute() {
  const location = useLocation()

  const [isCheckingAuth, setIsCheckingAuth] =
    useState(true)

  const [isAuthenticated, setIsAuthenticated] =
    useState(false)


  useEffect(() => {
    let isMounted = true


    async function checkAuthentication() {
      if (!hasStoredAccessToken()) {
        if (isMounted) {
          setIsAuthenticated(false)
          setIsCheckingAuth(false)
        }

        return
      }


      try {
        /*
         * getCurrentUser() now uses the shared apiClient
         * authentication flow.
         *
         * If the access token has expired, apiClient
         * refreshes the session and retries /auth/me/
         * once before this call fails.
         */
        await getCurrentUser()

        if (isMounted) {
          setIsAuthenticated(true)
        }
      }
      catch {
        /*
         * Preserve the existing protected-route behaviour.
         *
         * apiClient already handles expired access tokens.
         * Any authentication verification failure that
         * reaches this point denies protected access and
         * clears the local session.
         */
        clearAuthSession()

        if (isMounted) {
          setIsAuthenticated(false)
        }
      }
      finally {
        if (isMounted) {
          setIsCheckingAuth(false)
        }
      }
    }


    checkAuthentication()


    return () => {
      isMounted = false
    }
  }, [])


  if (isCheckingAuth) {
    return (
      <p>
        Checking authentication...
      </p>
    )
  }


  if (!isAuthenticated) {
    const requestedLocation = [
      location.pathname,
      location.search,
      location.hash,
    ].join('')

    return (
      <Navigate
        to="/login"
        state={{
          from: requestedLocation,
        }}
        replace
      />
    )
  }


  return <Outlet />
}


export default ProtectedRoute
