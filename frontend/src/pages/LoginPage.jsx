import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import {
  Link,
  useLocation,
  useNavigate,
} from 'react-router'

import { loginAccount } from '../services/authService'
import './AuthPage.css'


function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  /*
   * Preserve the existing protected-route redirect behaviour.
   *
   * When a user is redirected to Login from a protected page,
   * return them to the original destination after authentication.
   */
  const destination = location.state?.from || '/profile'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)


  async function handleSubmit(event) {
    event.preventDefault()

    if (!email || !password) {
      setError('Email and password are required.')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      await loginAccount(email, password)

      navigate(destination, { replace: true })
    } catch (requestError) {
      /*
       * Credential failures use the approved Figma wording.
       *
       * Other API or network errors preserve the message returned
       * by the application's API client.
       */
      if (
        requestError.status === 400
        || requestError.status === 401
      ) {
        setError('Email or password is incorrect.')
      } else {
        setError(requestError.message)
      }
    } finally {
      setIsLoading(false)
    }
  }


  function handleEmailChange(event) {
    setEmail(event.target.value)

    if (error) {
      setError('')
    }
  }


  function handlePasswordChange(event) {
    setPassword(event.target.value)

    if (error) {
      setError('')
    }
  }


  function togglePasswordVisibility() {
    setShowPassword((currentValue) => !currentValue)
  }


  return (
    <main className="login-page">
      <header className="login-page__header">
        <Link
          className="login-page__brand"
          to="/"
          aria-label="GradNavi home"
        >
          GradNavi
        </Link>

        <div className="login-page__divider" />
      </header>


      <section className="login-layout">
        <aside className="login-info-panel">
          <h2>
            GradNavi account access
          </h2>

          <p>
            Use one account to access profile, career analysis,
            document drafts, interview preparation, and learning
            resources.
          </p>
        </aside>


        <div className="login-content">
          <div className="login-heading">
            <h1>
              Welcome Back
            </h1>

            <p>
              Log in to continue to GradNavi.
            </p>
          </div>


          <div className="login-card">
            <form
              className="login-form"
              onSubmit={handleSubmit}
            >
              <div className="login-field">
                <label htmlFor="login-email">
                  Email Address
                </label>

                <input
                  id="login-email"
                  className="login-input"
                  type="email"
                  autoComplete="email"
                  placeholder="student@example.com"
                  value={email}
                  aria-invalid={Boolean(error)}
                  onChange={handleEmailChange}
                />
              </div>


              <div className="login-field">
                <label htmlFor="login-password">
                  Password
                </label>

                <div className="login-password-control">
                  <input
                    id="login-password"
                    className="login-input"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="Password"
                    value={password}
                    aria-invalid={Boolean(error)}
                    aria-describedby={
                      error
                        ? 'login-error'
                        : undefined
                    }
                    onChange={handlePasswordChange}
                  />

                  <button
                    className="login-password-toggle"
                    type="button"
                    aria-label={
                      showPassword
                        ? 'Hide password'
                        : 'Show password'
                    }
                    aria-pressed={showPassword}
                    onClick={togglePasswordVisibility}
                  >
                    {showPassword ? (
                      <EyeOff
                        aria-hidden="true"
                        size={20}
                        strokeWidth={1.8}
                      />
                    ) : (
                      <Eye
                        aria-hidden="true"
                        size={20}
                        strokeWidth={1.8}
                      />
                    )}
                  </button>
                </div>
              </div>


              <div className="login-forgot-row">
                <Link to="/forgot-password">
                  Forgot Password?
                </Link>
              </div>


              {error && (
                <p
                  className="login-error"
                  id="login-error"
                  role="alert"
                >
                  {error}
                </p>
              )}


              <button
                className="gn-button gn-button--primary login-submit"
                type="submit"
                disabled={isLoading}
                aria-busy={isLoading}
              >
                {isLoading ? 'Logging In...' : 'Log In'}
              </button>
            </form>


            <p className="login-register">
              <span>
                Don&apos;t have an account?
              </span>

              <Link to="/register">
                Create Account
              </Link>
            </p>
          </div>
        </div>
      </section>
    </main>
  )
}


export default LoginPage