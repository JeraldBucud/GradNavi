import {
  useEffect,
  useState,
} from 'react'

import {
  BookOpen,
  Briefcase,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  Menu,
  Sparkles,
  Users,
  X,
} from 'lucide-react'

import {
  Link,
  NavLink,
  Outlet,
  useNavigate,
} from 'react-router'

import {
  getStoredUser,
  logoutAccount,
} from '../services/authService'

import './StudentLayout.css'


const adminNavigation = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/admin',
    implemented: true,
  },
  {
    label: 'Users',
    icon: Users,
    implemented: false,
  },
  {
    label: 'Careers',
    icon: Briefcase,
    implemented: false,
  },
  {
    label: 'Skills',
    icon: Sparkles,
    implemented: false,
  },
  {
    label: 'Learning Resources',
    icon: BookOpen,
    implemented: false,
  },
  {
    label: 'Audit Records',
    icon: ClipboardList,
    implemented: false,
  },
]


function AdminLayout() {
  const navigate = useNavigate()
  const currentUser = getStoredUser()

  const [
    isMobileNavigationOpen,
    setIsMobileNavigationOpen,
  ] = useState(false)

  const adminName =
    currentUser?.first_name?.trim() || 'Admin'

  const adminInitial =
    adminName.charAt(0).toUpperCase()


  useEffect(
    () => {
      if (!isMobileNavigationOpen) {
        return undefined
      }

      const previousOverflow =
        document.body.style.overflow

      document.body.style.overflow =
        'hidden'

      function handleKeyDown(event) {
        if (event.key === 'Escape') {
          setIsMobileNavigationOpen(false)
        }
      }

      document.addEventListener(
        'keydown',
        handleKeyDown,
      )

      return () => {
        document.body.style.overflow =
          previousOverflow

        document.removeEventListener(
          'keydown',
          handleKeyDown,
        )
      }
    },
    [isMobileNavigationOpen],
  )


  function closeMobileNavigation() {
    setIsMobileNavigationOpen(false)
  }


  async function handleLogout() {
    closeMobileNavigation()

    try {
      await logoutAccount()
    } finally {
      navigate('/login', {
        replace: true,
      })
    }
  }


  return (
    <div className="student-shell">
      <header className="student-mobile-header">
        <Link
          className="student-mobile-header__brand"
          to="/admin"
          onClick={closeMobileNavigation}
        >
          GradNavi
        </Link>

        <div className="student-mobile-header__actions">
          <div
            className="student-mobile-header__account"
            aria-label={`Signed in as ${adminName}`}
          >
            <span
              className="student-account-avatar"
              aria-hidden="true"
            >
              {adminInitial}
            </span>

            <span className="student-mobile-header__name">
              {adminName}
            </span>
          </div>

          <button
            className="student-mobile-header__menu"
            type="button"
            aria-label="Open navigation menu"
            aria-controls="admin-navigation-drawer"
            aria-expanded={isMobileNavigationOpen}
            onClick={() =>
              setIsMobileNavigationOpen(true)
            }
          >
            <Menu
              size={24}
              strokeWidth={1.8}
              aria-hidden="true"
            />
          </button>
        </div>
      </header>

      <button
        className={[
          'student-mobile-overlay',
          isMobileNavigationOpen
            ? 'student-mobile-overlay--visible'
            : '',
        ]
          .filter(Boolean)
          .join(' ')}
        type="button"
        aria-label="Close navigation menu"
        tabIndex={
          isMobileNavigationOpen
            ? 0
            : -1
        }
        onClick={closeMobileNavigation}
      />

      <aside
        id="admin-navigation-drawer"
        className={[
          'student-sidebar',
          isMobileNavigationOpen
            ? 'student-sidebar--mobile-open'
            : '',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <button
          className="student-sidebar__mobile-close"
          type="button"
          aria-label="Close navigation menu"
          onClick={closeMobileNavigation}
        >
          <X
            size={24}
            strokeWidth={1.8}
            aria-hidden="true"
          />
        </button>

        <div className="student-sidebar__top">
          <Link
            className="student-sidebar__brand"
            to="/admin"
            onClick={closeMobileNavigation}
          >
            GradNavi
          </Link>

          <nav
            className="student-sidebar__navigation"
            aria-label="Admin navigation"
          >
            {adminNavigation.map((item) => {
              const Icon = item.icon

              if (item.implemented) {
                return (
                  <NavLink
                    key={item.label}
                    to={item.path}
                    end
                    onClick={
                      closeMobileNavigation
                    }
                    className={({ isActive }) =>
                      [
                        'student-nav-item',
                        isActive
                          ? 'student-nav-item--active'
                          : '',
                      ]
                        .filter(Boolean)
                        .join(' ')
                    }
                  >
                    <Icon
                      size={20}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <span>
                      {item.label}
                    </span>
                  </NavLink>
                )
              }

              return (
                <div
                  key={item.label}
                  className="student-nav-item student-nav-item--disabled"
                  aria-disabled="true"
                  title="This screen is not implemented yet."
                >
                  <Icon
                    size={20}
                    strokeWidth={1.8}
                    aria-hidden="true"
                  />

                  <span>
                    {item.label}
                  </span>
                </div>
              )
            })}
          </nav>
        </div>

        <div className="student-sidebar__account">
          <div className="student-account-summary">
            <div
              className="student-account-avatar"
              aria-hidden="true"
            >
              {adminInitial}
            </div>

            <div className="student-account-copy">
              <strong>
                {adminName}
              </strong>

              <span>
                Administrator account
              </span>
            </div>
          </div>

          <button
            className="student-account-logout"
            type="button"
            onClick={handleLogout}
          >
            <LogOut
              size={16}
              strokeWidth={1.8}
              aria-hidden="true"
            />

            <span>
              Log Out
            </span>
          </button>
        </div>
      </aside>

      <div className="student-shell__content">
        <Outlet />
      </div>
    </div>
  )
}


export default AdminLayout