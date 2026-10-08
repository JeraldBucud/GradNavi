import { useState } from 'react'
import { CircleCheck } from 'lucide-react'
import { Link } from 'react-router'

import AuthLayout from '../components/auth/AuthLayout'
import { requestPasswordReset } from '../services/authService'


function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)


  async function handleSubmit(event) {
    event.preventDefault()

    if (!email.trim()) {
      setError('Email address is required.')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      await requestPasswordReset(email.trim())

      setIsSubmitted(true)
    } catch (requestError) {
      const errorDetails =
        requestError.data?.error?.details

      if (errorDetails?.email?.length) {
        setError(
          errorDetails.email.join(' '),
        )
      } else {
        setError(requestError.message)
      }
    } finally {
      setIsLoading(false)
    }
  }


  if (isSubmitted) {
    return (
      <AuthLayout>
        <div className="auth-state-card auth-state-card--success">
          <div className="auth-state-card__status">
            <CircleCheck
              aria-hidden="true"
              size={20}
              strokeWidth={2}
            />

            <span>
              Reset instructions sent
            </span>
          </div>

          <h1>
            Check your email
          </h1>

          <p>
            If an account exists for this email address,
            password reset instructions have been sent.
          </p>

          <div className="auth-state-card__actions">
            <Link
              className="auth-secondary-button"
              to="/login"
            >
              Back to Log In
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }


  return (
    <AuthLayout>
      <div className="auth-page-heading">
        <h1>
          Reset your password
        </h1>

        <p>
          Enter your email and we&apos;ll send password
          reset instructions.
        </p>
      </div>

      <div className="auth-form-divider" />

      <form
        className="auth-form"
        onSubmit={handleSubmit}
      >
        <div className="auth-field">
          <label htmlFor="forgot-email">
            Email
          </label>

          <input
            id="forgot-email"
            className="auth-input"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            aria-invalid={Boolean(error)}
            aria-describedby={
              error
                ? 'forgot-email-error'
                : undefined
            }
            onChange={(event) => {
              setEmail(event.target.value)

              if (error) {
                setError('')
              }
            }}
          />

          {error && (
            <p
              className="auth-field-error"
              id="forgot-email-error"
              role="alert"
            >
              {error}
            </p>
          )}
        </div>

        <button
          className="auth-primary-button"
          type="submit"
          disabled={isLoading}
          aria-busy={isLoading}
        >
          {
            isLoading
              ? 'Sending...'
              : 'Send Reset Instructions'
          }
        </button>
      </form>

      <p className="auth-form-footer">
        <Link to="/login">
          ← Back to Log In
        </Link>
      </p>
    </AuthLayout>
  )
}


export default ForgotPasswordPage
