import { useState } from 'react'
import {
  Link,
  useLocation,
  useNavigate,
} from 'react-router'

import AuthLayout from '../components/auth/AuthLayout'
import { loginAccount } from '../services/authService'


function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const requestedDestination =
    location.state?.from
    || null

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
      const authData =
        await loginAccount(
          email,
          password,
        )

      const defaultDestination =
        authData
          ?.user
          ?.role
        === 'admin'
          ? '/admin'
          : '/dashboard'

      navigate(
        requestedDestination
        || defaultDestination,
        {
          replace: true,
        },
      )
    } catch (requestError) {
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


  return (
    <AuthLayout>
      <div className="auth-page-heading">
        <h1>
          Welcome back
        </h1>

        <p>
          Log in to continue your career journey.
        </p>
      </div>

      <div className="auth-form-divider" />

      <form
        className="auth-form"
        onSubmit={handleSubmit}
      >
        <div className="auth-field">
          <label htmlFor="login-email">
            Email
          </label>

          <input
            id="login-email"
            className="auth-input"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            aria-invalid={Boolean(error)}
            aria-describedby={
              error
                ? 'login-error'
                : undefined
            }
            onChange={(event) => {
              setEmail(event.target.value)

              if (error) {
                setError('')
              }
            }}
          />
        </div>

        <div className="auth-field">
          <label htmlFor="login-password">
            Password
          </label>

          <div className="auth-password-control">
            <input
              id="login-password"
              className="auth-input"
              type={
                showPassword
                  ? 'text'
                  : 'password'
              }
              autoComplete="current-password"
              placeholder="Enter your password"
              value={password}
              aria-invalid={Boolean(error)}
              aria-describedby={
                error
                  ? 'login-error'
                  : undefined
              }
              onChange={(event) => {
                setPassword(event.target.value)

                if (error) {
                  setError('')
                }
              }}
            />

            <button
              className="auth-password-toggle"
              type="button"
              aria-label={
                showPassword
                  ? 'Hide password'
                  : 'Show password'
              }
              aria-pressed={showPassword}
              onClick={() => {
                setShowPassword(
                  (currentValue) => !currentValue,
                )
              }}
            >
              {
                showPassword
                  ? 'Hide'
                  : 'Show'
              }
            </button>
          </div>
        </div>

        <div className="auth-form-utility">
          <Link
            className="auth-text-link"
            to="/forgot-password"
          >
            Forgot password?
          </Link>
        </div>

        {error && (
          <p
            className="auth-form-error"
            id="login-error"
            role="alert"
          >
            {error}
          </p>
        )}

        <button
          className="auth-primary-button"
          type="submit"
          disabled={isLoading}
          aria-busy={isLoading}
        >
          {
            isLoading
              ? 'Logging In...'
              : 'Log In'
          }
        </button>
      </form>

      <p className="auth-form-footer">
        New to GradNavi?

        <Link to="/register">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  )
}


export default LoginPage
