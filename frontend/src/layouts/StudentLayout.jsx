import {
  useEffect,
  useState,
} from 'react'

import {
  BarChart3,
  BookOpen,
  Briefcase,
  Compass,
  FileText,
  LayoutDashboard,
  LogOut,
  Mail,
  Menu,
  MessageSquare,
  Route,
  User,
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


const studentNavigation = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    implemented: false,
  },
  {
    label: 'Student Profile',
    icon: User,
    path: '/profile',
    implemented: true,
  },
  {
    label: 'Career Recommendations',
    icon: Briefcase,
    path: '/career-recommendations',
    implemented: true,
  },
  {
    label: 'Explore Careers',
    icon: Compass,
    path: '/explore-careers',
    implemented: true,
  },
  {
    label: 'Skill Gap Analysis',
    icon: BarChart3,
    path: '/skill-gap-analysis',
    implemented: true,
  },
  {
    label: 'Career Roadmap',
    icon: Route,
    path: '/career-roadmap',
    implemented: true,
  },
  {
    label: 'Learning Resources',
    icon: BookOpen,
    path: '/learning-resources',
    implemented: true,
  },
  {
    label: 'Resume Builder',
    icon: FileText,
    path: '/resume-builder',
    implemented: true,
  },
  {
    label: 'Cover Letter Builder',
    icon: Mail,
    path: '/cover-letter-builder',
    implemented: true,
  },
  {
    label: 'Interview Preparation',
    icon: MessageSquare,
    implemented: false,
  },
]


function StudentLayout() {
  const navigate = useNavigate()
  const currentUser = getStoredUser()

  const [
    isMobileNavigationOpen,
    setIsMobileNavigationOpen,
  ] = useState(false)

  const studentName =
    currentUser?.first_name?.trim() || 'Student'

  const studentInitial =
    studentName.charAt(0).toUpperCase()


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
          to="/"
          onClick={closeMobileNavigation}
        >
          GradNavi
        </Link>

        <div className="student-mobile-header__actions">
          <div
            className="student-mobile-header__account"
            aria-label={`Signed in as ${studentName}`}
          >
            <span
              className="student-account-avatar"
              aria-hidden="true"
            >
              {studentInitial}
            </span>

            <span className="student-mobile-header__name">
              {studentName}
            </span>
          </div>

          <button
            className="student-mobile-header__menu"
            type="button"
            aria-label="Open navigation menu"
            aria-controls="student-navigation-drawer"
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
        id="student-navigation-drawer"
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
            to="/"
            onClick={closeMobileNavigation}
          >
            GradNavi
          </Link>

          <nav
            className="student-sidebar__navigation"
            aria-label="Student navigation"
          >
            {studentNavigation.map((item) => {
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
              {studentInitial}
            </div>

            <div className="student-account-copy">
              <strong>
                {studentName}
              </strong>

              <span>
                Account
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


export default StudentLayout