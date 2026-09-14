import { useState } from 'react'
import {
  ArrowLeft,
  CircleCheck,
} from 'lucide-react'
import { Link } from 'react-router'

import { requestPasswordReset } from '../services/authService'
import './ForgotPasswordPage.css'


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

      /*
       * Do not reveal whether the email belongs to an account.
       *
       * The Django endpoint intentionally returns the same
       * response for registered and unregistered addresses.
       */
      setIsSubmitted(true)
    } catch (requestError) {
      const errorDetails = requestError.data?.error?.details

      if (errorDetails?.email?.length) {
        setError(errorDetails.email.join(' '))
      } else {
        setError(requestError.message)
      }
    } finally {
      setIsLoading(false)
    }
  }


  if (isSubmitted) {
    return (
      <main className="forgot-page">
        <header className="forgot-page__header">
          <Link
            className="forgot-page__brand"
            to="/"
            aria-label="GradNavi home"
          >
            GradNavi
          </Link>

          <div className="forgot-page__divider" />
        </header>


        <section className="forgot-layout">
          <div className="forgot-success-card">
            <div className="forgot-success-card__status">
              <span>
                Forgot Password - Success State
              </span>

              <CircleCheck
                aria-hidden="true"
                size={20}
                strokeWidth={2}
              />
            </div>

            <h1>
              Check Your Email
            </h1>

            <p>
              If an account exists for this email address,
              password reset instructions have been sent.
            </p>

            <Link
              className="forgot-secondary-button"
              to="/login"
            >
              <ArrowLeft
                aria-hidden="true"
                size={18}
                strokeWidth={2}
              />

              <span>
                Back to Log In
              </span>
            </Link>
          </div>
        </section>
      </main>
    )
  }


  return (
    <main className="forgot-page">
      <header className="forgot-page__header">
        <Link
          className="forgot-page__brand"
          to="/"
          aria-label="GradNavi home"
        >
          GradNavi
        </Link>

        <div className="forgot-page__divider" />
      </header>


      <section className="forgot-layout">
        <div className="forgot-card">
          <h1>
            Forgot Your Password?
          </h1>

          <p className="forgot-card__description">
            Enter your account email address to request password
            reset instructions.
          </p>


          <form
            className="forgot-form"
            onSubmit={handleSubmit}
          >
            <div className="forgot-field">
              <label htmlFor="forgot-email">
                Email Address
              </label>

              <input
                id="forgot-email"
                className="forgot-input"
                type="email"
                autoComplete="email"
                placeholder="student@example.com"
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
                  className="forgot-field-error"
                  id="forgot-email-error"
                  role="alert"
                >
                  {error}
                </p>
              )}
            </div>


            <button
              className="gn-button gn-button--primary forgot-submit"
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


          <Link
            className="forgot-secondary-button"
            to="/login"
          >
            <ArrowLeft
              aria-hidden="true"
              size={18}
              strokeWidth={2}
            />

            <span>
              Back to Log In
            </span>
          </Link>
        </div>
      </section>
    </main>
  )
}


export default ForgotPasswordPage