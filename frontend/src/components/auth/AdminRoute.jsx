import {
  useEffect,
  useState,
} from 'react'

import {
  Navigate,
  Outlet,
} from 'react-router'

import { getCurrentUser } from '../../services/authService'


function AdminRoute() {
  const [isCheckingRole, setIsCheckingRole] =
    useState(true)

  const [isAdmin, setIsAdmin] =
    useState(false)


  useEffect(() => {
    let isMounted = true


    async function checkRole() {
      try {
        const user = await getCurrentUser()

        if (isMounted) {
          setIsAdmin(user?.role === 'admin')
        }
      } catch {
        if (isMounted) {
          setIsAdmin(false)
        }
      } finally {
        if (isMounted) {
          setIsCheckingRole(false)
        }
      }
    }


    checkRole()


    return () => {
      isMounted = false
    }
  }, [])


  if (isCheckingRole) {
    return (
      <p>
        Checking access...
      </p>
    )
  }


  if (!isAdmin) {
    return (
      <Navigate
        to="/profile"
        replace
      />
    )
  }


  return <Outlet />
}


export default AdminRoute