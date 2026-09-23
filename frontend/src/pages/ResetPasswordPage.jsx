import { useState } from 'react'
import {
  ArrowLeft,
  CircleCheck,
  CircleX,
  Eye,
  EyeOff,
} from 'lucide-react'
import {
  Link,
  useSearchParams,
} from 'react-router'

import { confirmPasswordReset } from '../services/authService'
import './ResetPasswordPage.css'


const EMPTY_ERRORS = {
  password: '',
  passwordConfirm: '',
  form: '',
}


function ResetPasswordPage() {
  const [searchParams] = useSearchParams()

  const uid = searchParams.get('uid') || ''
  const token = searchParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')

  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)

  const [errors, setErrors] = useState(EMPTY_ERRORS)
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccessful, setIsSuccessful] = useState(false)
  const [isInvalidLink, setIsInvalidLink] = useState(
    !uid || !token,
  )


  function clearFieldError(fieldName) {
    setErrors((currentErrors) => ({
      ...currentErrors,
      [fieldName]: '',
      form: '',
    }))
  }


  function validateForm() {
    const nextErrors = {
      ...EMPTY_ERRORS,
    }

    if (!password) {
      nextErrors.password = 'New password is required.'
    }

    if (!passwordConfirm) {
      nextErrors.passwordConfirm =
        'Confirm new password is required.'
    }

    if (
      password
      && passwordConfirm
      && password !== passwordConfirm
    ) {
      nextErrors.passwordConfirm =
        'Passwords do not match.'
    }

    const hasErrors = Object.values(nextErrors).some(Boolean)

    if (hasErrors) {
      setErrors(nextErrors)
      return false
    }

    return true
  }


  async function handleSubmit(event) {
    event.preventDefault()

    if (!uid || !token) {
      setIsInvalidLink(true)
      return
    }

    if (!validateForm()) {
      return
    }

    setErrors(EMPTY_ERRORS)
    setIsLoading(true)

    try {
      await confirmPasswordReset({
        uid,
        token,
        password,
        password_confirm: passwordConfirm,
      })

      setIsSuccessful(true)
    } catch (requestError) {
      /*
       * Django AuthenticationFailed represents an invalid
       * or expired reset token. Do not expose token details.
       */
      if (requestError.status === 401) {
        setIsInvalidLink(true)
        return
      }

      const errorDetails = requestError.data?.error?.details

      if (errorDetails?.password?.length) {
        setErrors({
          ...EMPTY_ERRORS,
          password: errorDetails.password.join(' '),
        })
        return
      }

      if (errorDetails?.password_confirm?.length) {
        setErrors({
          ...EMPTY_ERRORS,
          passwordConfirm:
            errorDetails.password_confirm.join(' '),
        })
        return
      }

      setErrors({
        ...EMPTY_ERRORS,
        form: 'Password reset failed. Please try again.',
      })
    } finally {
      setIsLoading(false)
    }
  }


  if (isSuccessful) {
    return (
      <main className="reset-page">
        <header className="reset-page__header">
          <Link
            className="reset-page__brand"
            to="/"
            aria-label="GradNavi home"
          >
            GradNavi
          </Link>

          <div className="reset-page__divider" />
        </header>


        <section className="reset-layout">
          <div className="reset-state-card reset-state-card--success">
            <div className="reset-state-card__status reset-state-card__status--success">
              <span>
                Reset Password - Success State
              </span>

              <CircleCheck
                aria-hidden="true"
                size={20}
                strokeWidth={2}
              />
            </div>

            <h1>
              Password Updated
            </h1>

            <p>
              Your password has been reset successfully.
            </p>

            <Link
              className="reset-return-button"
              to="/login"
            >
              <ArrowLeft
                aria-hidden="true"
                size={18}
                strokeWidth={2}
              />

              <span>
                Return to Log In
              </span>
            </Link>
          </div>
        </section>
      </main>
    )
  }


  if (isInvalidLink) {
    return (
      <main className="reset-page">
        <header className="reset-page__header">
          <Link
            className="reset-page__brand"
            to="/"
            aria-label="GradNavi home"
          >
            GradNavi
          </Link>

          <div className="reset-page__divider" />
        </header>


        <section className="reset-layout">
          <div className="reset-state-card reset-state-card--invalid">
            <div className="reset-state-card__status reset-state-card__status--invalid">
              <span>
                Reset Password - Invalid Link State
              </span>

              <CircleX
                aria-hidden="true"
                size={20}
                strokeWidth={2}
              />
            </div>

            <h1>
              Reset Link Expired
            </h1>

            <p>
              This password reset link is invalid or has expired.
            </p>

            <div className="reset-invalid-actions">
              <Link
                className="gn-button gn-button--primary reset-request-button"
                to="/forgot-password"
              >
                Request New Reset Link
              </Link>

              <Link
                className="reset-back-button"
                to="/login"
              >
                Back to Log In
              </Link>
            </div>
          </div>
        </section>
      </main>
    )
  }


  return (
    <main className="reset-page">
      <header className="reset-page__header">
        <Link
          className="reset-page__brand"
          to="/"
          aria-label="GradNavi home"
        >
          GradNavi
        </Link>

        <div className="reset-page__divider" />
      </header>


      <section className="reset-layout">
        <div className="reset-card">
          <h1>
            Set a New Password
          </h1>

          <p className="reset-card__description">
            Enter and confirm your new password.
          </p>


          <form
            className="reset-form"
            onSubmit={handleSubmit}
          >
            <div className="reset-field">
              <label htmlFor="reset-password">
                New Password
              </label>

              <div className="reset-password-control">
                <input
                  id="reset-password"
                  className="reset-input"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="New password"
                  value={password}
                  aria-invalid={Boolean(errors.password)}
                  aria-describedby={
                    errors.password
                      ? 'reset-password-error'
                      : 'reset-password-help'
                  }
                  onChange={(event) => {
                    setPassword(event.target.value)
                    clearFieldError('password')
                  }}
                />

                <button
                  className="reset-password-toggle"
                  type="button"
                  aria-label={
                    showPassword
                      ? 'Hide new password'
                      : 'Show new password'
                  }
                  aria-pressed={showPassword}
                  onClick={() => {
                    setShowPassword(
                      (currentValue) => !currentValue,
                    )
                  }}
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

              {errors.password && (
                <p
                  className="reset-field-error"
                  id="reset-password-error"
                  role="alert"
                >
                  {errors.password}
                </p>
              )}
            </div>


            <div className="reset-field">
              <label htmlFor="reset-password-confirm">
                Confirm New Password
              </label>

              <div className="reset-password-control">
                <input
                  id="reset-password-confirm"
                  className="reset-input"
                  type={
                    showPasswordConfirm
                      ? 'text'
                      : 'password'
                  }
                  autoComplete="new-password"
                  placeholder="Confirm new password"
                  value={passwordConfirm}
                  aria-invalid={Boolean(errors.passwordConfirm)}
                  aria-describedby={
                    errors.passwordConfirm
                      ? 'reset-password-confirm-error'
                      : undefined
                  }
                  onChange={(event) => {
                    setPasswordConfirm(event.target.value)
                    clearFieldError('passwordConfirm')
                  }}
                />

                <button
                  className="reset-password-toggle"
                  type="button"
                  aria-label={
                    showPasswordConfirm
                      ? 'Hide confirm password'
                      : 'Show confirm password'
                  }
                  aria-pressed={showPasswordConfirm}
                  onClick={() => {
                    setShowPasswordConfirm(
                      (currentValue) => !currentValue,
                    )
                  }}
                >
                  {showPasswordConfirm ? (
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

              {errors.passwordConfirm && (
                <p
                  className="reset-field-error"
                  id="reset-password-confirm-error"
                  role="alert"
                >
                  {errors.passwordConfirm}
                </p>
              )}
            </div>


            <div
              className="reset-password-requirements"
              id="reset-password-help"
            >
              <h2>
                Password requirements based on system validation
              </h2>

              <p>
                Use the current Django password validation rules.
              </p>
            </div>


            {errors.form && (
              <p
                className="reset-form-error"
                role="alert"
              >
                {errors.form}
              </p>
            )}


            <button
              className="gn-button gn-button--primary reset-submit"
              type="submit"
              disabled={isLoading}
              aria-busy={isLoading}
            >
              {
                isLoading
                  ? 'Resetting Password...'
                  : 'Reset Password'
              }
            </button>
          </form>
        </div>
      </section>
    </main>
  )
}


export default ResetPasswordPage