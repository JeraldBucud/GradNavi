import { useState } from 'react'
import {
  CheckCircle2,
} from 'lucide-react'
import {
  Link,
  useNavigate,
} from 'react-router'

import AuthLayout from '../components/auth/AuthLayout'
import { registerAccount } from '../services/authService'


const EMPTY_ERRORS = {
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  passwordConfirm: '',
  form: '',
}


function RegisterPage() {
  const navigate = useNavigate()

  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')

  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)

  const [errors, setErrors] = useState(EMPTY_ERRORS)
  const [isLoading, setIsLoading] = useState(false)


  function clearFieldError(fieldName) {
    setErrors((currentErrors) => ({
      ...currentErrors,
      [fieldName]: '',
      form: '',
    }))
  }


  function validateRequiredFields() {
    const nextErrors = {
      ...EMPTY_ERRORS,
    }

    if (!firstName.trim()) {
      nextErrors.firstName = 'First name is required.'
    }

    if (!lastName.trim()) {
      nextErrors.lastName = 'Last name is required.'
    }

    if (!email.trim()) {
      nextErrors.email = 'Email address is required.'
    }

    if (!password) {
      nextErrors.password = 'Password is required.'
    }

    if (!passwordConfirm) {
      nextErrors.passwordConfirm =
        'Confirm password is required.'
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


  function applyApiErrors(requestError) {
    const errorDetails =
      requestError.data?.error?.details

    if (!errorDetails) {
      setErrors({
        ...EMPTY_ERRORS,
        form: requestError.message,
      })

      return
    }

    setErrors({
      firstName:
        errorDetails.first_name?.join(' ')
        || '',
      lastName:
        errorDetails.last_name?.join(' ')
        || '',
      email:
        errorDetails.email?.join(' ')
        || '',
      password:
        errorDetails.password?.join(' ')
        || '',
      passwordConfirm:
        errorDetails.password_confirm?.join(' ')
        || '',
      form: '',
    })
  }


  async function handleSubmit(event) {
    event.preventDefault()

    if (!validateRequiredFields()) {
      return
    }

    setErrors(EMPTY_ERRORS)
    setIsLoading(true)

    try {
      await registerAccount({
        email,
        password,
        password_confirm: passwordConfirm,
        first_name: firstName,
        last_name: lastName,
      })

      navigate('/login')
    } catch (requestError) {
      applyApiErrors(requestError)
    } finally {
      setIsLoading(false)
    }
  }


  return (
    <AuthLayout variant="register">
      <div className="auth-page-heading">
        <span className="auth-page-eyebrow">
          GET STARTED WITH GRADNAVI
        </span>

        <h1>
          Create your account
        </h1>

        <p>
          Start building your GradNavi career profile.
        </p>
      </div>

      <div className="auth-form-divider" />

      <form
        className="auth-form"
        onSubmit={handleSubmit}
      >
        <div className="auth-name-grid">
          <div className="auth-field">
            <label htmlFor="register-first-name">
              First name
            </label>

            <input
              id="register-first-name"
              className="auth-input"
              type="text"
              autoComplete="given-name"
              placeholder="Alex"
              value={firstName}
              aria-invalid={Boolean(errors.firstName)}
              aria-describedby={
                errors.firstName
                  ? 'register-first-name-error'
                  : undefined
              }
              onChange={(event) => {
                setFirstName(event.target.value)
                clearFieldError('firstName')
              }}
            />

            {errors.firstName && (
              <p
                className="auth-field-error"
                id="register-first-name-error"
                role="alert"
              >
                {errors.firstName}
              </p>
            )}
          </div>

          <div className="auth-field">
            <label htmlFor="register-last-name">
              Last name
            </label>

            <input
              id="register-last-name"
              className="auth-input"
              type="text"
              autoComplete="family-name"
              placeholder="Morgan"
              value={lastName}
              aria-invalid={Boolean(errors.lastName)}
              aria-describedby={
                errors.lastName
                  ? 'register-last-name-error'
                  : undefined
              }
              onChange={(event) => {
                setLastName(event.target.value)
                clearFieldError('lastName')
              }}
            />

            {errors.lastName && (
              <p
                className="auth-field-error"
                id="register-last-name-error"
                role="alert"
              >
                {errors.lastName}
              </p>
            )}
          </div>
        </div>

        <div className="auth-field">
          <label htmlFor="register-email">
            Email
          </label>

          <input
            id="register-email"
            className="auth-input"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            aria-invalid={Boolean(errors.email)}
            aria-describedby={
              errors.email
                ? 'register-email-error'
                : undefined
            }
            onChange={(event) => {
              setEmail(event.target.value)
              clearFieldError('email')
            }}
          />

          {errors.email && (
            <p
              className="auth-field-error"
              id="register-email-error"
              role="alert"
            >
              {errors.email}
            </p>
          )}
        </div>

        <div className="auth-field">
          <label htmlFor="register-password">
            Password
          </label>

          <div className="auth-password-control">
            <input
              id="register-password"
              className="auth-input"
              type={
                showPassword
                  ? 'text'
                  : 'password'
              }
              autoComplete="new-password"
              placeholder="Create a password"
              value={password}
              aria-invalid={Boolean(errors.password)}
              aria-describedby={
                errors.password
                  ? 'register-password-error'
                  : 'register-password-help'
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

          {errors.password && (
            <p
              className="auth-field-error"
              id="register-password-error"
              role="alert"
            >
              {errors.password}
            </p>
          )}
        </div>

        <div className="auth-field">
          <label htmlFor="register-password-confirm">
            Confirm password
          </label>

          <div className="auth-password-control">
            <input
              id="register-password-confirm"
              className="auth-input"
              type={
                showPasswordConfirm
                  ? 'text'
                  : 'password'
              }
              autoComplete="new-password"
              placeholder="Re-enter your password"
              value={passwordConfirm}
              aria-invalid={
                Boolean(errors.passwordConfirm)
              }
              aria-describedby={
                errors.passwordConfirm
                  ? 'register-password-confirm-error'
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
              id="register-password-confirm-error"
              role="alert"
            >
              {errors.passwordConfirm}
            </p>
          )}
        </div>

        <div
          className="auth-password-requirements"
          id="register-password-help"
        >
          <strong>
            Password requirements
          </strong>

          <ul className="auth-password-requirements__list">
            <li>
              <CheckCircle2
                size={15}
                strokeWidth={2}
                aria-hidden="true"
              />

              <span>
                At least 8 characters
              </span>
            </li>

            <li>
              <CheckCircle2
                size={15}
                strokeWidth={2}
                aria-hidden="true"
              />

              <span>
                Avoid using your name or email
              </span>
            </li>

            <li>
              <CheckCircle2
                size={15}
                strokeWidth={2}
                aria-hidden="true"
              />

              <span>
                Avoid common passwords
              </span>
            </li>

            <li>
              <CheckCircle2
                size={15}
                strokeWidth={2}
                aria-hidden="true"
              />

              <span>
                Do not use numbers only
              </span>
            </li>
          </ul>
        </div>

        <p className="auth-legal-copy">
          Create your account to use GradNavi&apos;s
          student career guidance features.
        </p>

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
              ? 'Creating Account...'
              : 'Create Account'
          }
        </button>
      </form>

      <p className="auth-form-footer">
        Already have an account?

        <Link to="/login">
          Log in
        </Link>
      </p>
    </AuthLayout>
  )
}


export default RegisterPage
