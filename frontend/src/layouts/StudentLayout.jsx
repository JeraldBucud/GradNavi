import {
  BarChart3,
  BookOpen,
  Briefcase,
  Compass,
  FileText,
  LayoutDashboard,
  LogOut,
  Mail,
  MessageSquare,
  Route,
  User,
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
    implemented: false,
  },
  {
    label: 'Cover Letter Builder',
    icon: Mail,
    implemented: false,
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

  const studentName =
    currentUser?.first_name?.trim() || 'Student'

  const studentInitial =
    studentName.charAt(0).toUpperCase()


  async function handleLogout() {
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
      <aside className="student-sidebar">
        <div className="student-sidebar__top">
          <Link
            className="student-sidebar__brand"
            to="/"
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
