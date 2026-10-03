import { useState } from 'react'
import {
  CircleCheck,
  CircleX,
} from 'lucide-react'
import {
  Link,
  useSearchParams,
} from 'react-router'

import AuthLayout from '../components/auth/AuthLayout'
import { confirmPasswordReset } from '../services/authService'


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
      nextErrors.password =
        'New password is required.'
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

    const hasErrors =
      Object
        .values(nextErrors)
        .some(Boolean)

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
      if (requestError.status === 401) {
        setIsInvalidLink(true)
        return
      }

      const errorDetails =
        requestError.data?.error?.details

      if (errorDetails?.password?.length) {
        setErrors({
          ...EMPTY_ERRORS,
          password:
            errorDetails.password.join(' '),
        })

        return
      }

      if (
        errorDetails
          ?.password_confirm
          ?.length
      ) {
        setErrors({
          ...EMPTY_ERRORS,
          passwordConfirm:
            errorDetails
              .password_confirm
              .join(' '),
        })

        return
      }

      setErrors({
        ...EMPTY_ERRORS,
        form:
          'Password reset failed. Please try again.',
      })
    } finally {
      setIsLoading(false)
    }
  }


  if (isSuccessful) {
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
              Password updated
            </span>
          </div>

          <h1>
            Password updated
          </h1>

          <p>
            Your password has been reset successfully.
          </p>

          <div className="auth-state-card__actions">
            <Link
              className="auth-primary-button"
              to="/login"
            >
              Return to Log In
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }


  if (isInvalidLink) {
    return (
      <AuthLayout>
        <div className="auth-state-card auth-state-card--error">
          <div className="auth-state-card__status">
            <CircleX
              aria-hidden="true"
              size={20}
              strokeWidth={2}
            />

            <span>
              Invalid reset link
            </span>
          </div>

          <h1>
            Reset link expired
          </h1>

          <p>
            This password reset link is invalid or
            has expired.
          </p>

          <div className="auth-state-card__actions">
            <Link
              className="auth-primary-button"
              to="/forgot-password"
            >
              Request New Reset Link
            </Link>

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
          Choose a new password
        </h1>

        <p>
          Create a new password for your
          GradNavi account.
        </p>
      </div>

      <div className="auth-form-divider" />

      <form
        className="auth-form"
        onSubmit={handleSubmit}
      >
        <div className="auth-field">
          <label htmlFor="reset-password">
            New password
          </label>

          <div className="auth-password-control">
            <input
              id="reset-password"
              className="auth-input"
              type={
                showPassword
                  ? 'text'
                  : 'password'
              }
              autoComplete="new-password"
              placeholder="Create a new password"
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
              className="auth-password-toggle"
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
              {
                showPassword
                  ? 'Hide'
                  : 'Show'
              }
            </button>
          </div>

          {errors.password && (
            <p
              className="auth-field-error"
              id="reset-password-error"
              role="alert"
            >
              {errors.password}
            </p>
          )}
        </div>

        <div className="auth-field">
          <label htmlFor="reset-password-confirm">
            Confirm new password
          </label>

          <div className="auth-password-control">
            <input
              id="reset-password-confirm"
              className="auth-input"
              type={
                showPasswordConfirm
                  ? 'text'
                  : 'password'
              }
              autoComplete="new-password"
              placeholder="Re-enter your new password"
              value={passwordConfirm}
              aria-invalid={
                Boolean(errors.passwordConfirm)
              }
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
              className="auth-password-toggle"
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
              {
                showPasswordConfirm
                  ? 'Hide'
                  : 'Show'
              }
            </button>
          </div>

          {errors.passwordConfirm && (
            <p
              className="auth-field-error"
              id="reset-password-confirm-error"
              role="alert"
            >
              {errors.passwordConfirm}
            </p>
          )}
        </div>

        <div
          className="auth-password-requirements"
          id="reset-password-help"
        >
          <strong>
            Password requirements
          </strong>

          At least 8 characters. Django validation
          also rejects passwords that are too common,
          entirely numeric, or too similar to personal
          details.
        </div>

        {errors.form && (
          <p
            className="auth-form-error"
            role="alert"
          >
            {errors.form}
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
              ? 'Updating Password...'
              : 'Update Password'
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


export default ResetPasswordPage
