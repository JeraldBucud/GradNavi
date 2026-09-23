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
  refreshAccessToken,
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
        await getCurrentUser()

        if (isMounted) {
          setIsAuthenticated(true)
        }
      } catch (requestError) {
        if (requestError.status === 401) {
          try {
            /*
             * Access tokens are short-lived.
             *
             * A 401 from /auth/me/ first attempts the
             * approved refresh-token flow before the
             * session is considered invalid.
             */
            await refreshAccessToken()
            await getCurrentUser()

            if (isMounted) {
              setIsAuthenticated(true)
            }

            return
          } catch {
            clearAuthSession()

            if (isMounted) {
              setIsAuthenticated(false)
            }
          }
        } else {
          /*
           * Preserve the existing Sprint 1 behaviour.
           *
           * Authentication verification failures outside
           * the refresh flow do not grant protected access.
           */
          clearAuthSession()

          if (isMounted) {
            setIsAuthenticated(false)
          }
        }
      } finally {
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