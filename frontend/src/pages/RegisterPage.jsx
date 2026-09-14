import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import {
  Link,
  useNavigate,
} from 'react-router'

import { registerAccount } from '../services/authService'
import './AuthPage.css'


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
      nextErrors.passwordConfirm = 'Confirm password is required.'
    }

    if (
      password
      && passwordConfirm
      && password !== passwordConfirm
    ) {
      nextErrors.passwordConfirm = 'Passwords do not match.'
    }

    const hasErrors = Object.values(nextErrors).some(Boolean)

    if (hasErrors) {
      setErrors(nextErrors)
      return false
    }

    return true
  }


  function applyApiErrors(requestError) {
    const errorDetails = requestError.data?.error?.details

    if (!errorDetails) {
      setErrors({
        ...EMPTY_ERRORS,
        form: requestError.message,
      })
      return
    }

    setErrors({
      firstName: errorDetails.first_name?.join(' ') || '',
      lastName: errorDetails.last_name?.join(' ') || '',
      email: errorDetails.email?.join(' ') || '',
      password: errorDetails.password?.join(' ') || '',
      passwordConfirm:
        errorDetails.password_confirm?.join(' ') || '',
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
    <main className="register-page">
      <header className="register-page__header">
        <Link
          className="register-page__brand"
          to="/"
          aria-label="GradNavi home"
        >
          GradNavi
        </Link>

        <div className="register-page__divider" />
      </header>


      <section className="register-layout">
        <div className="register-heading">
          <h1>
            Create Your GradNavi Account
          </h1>

          <p>
            Create your student account to build your profile and begin
            career analysis.
          </p>
        </div>


        <div className="register-card">
          <form
            className="register-form"
            onSubmit={handleSubmit}
          >
            <div className="register-name-grid">
              <div className="register-field">
                <label htmlFor="register-first-name">
                  First Name
                </label>

                <input
                  id="register-first-name"
                  className="register-input"
                  type="text"
                  autoComplete="given-name"
                  placeholder="First name placeholder"
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
                    className="register-field-error"
                    id="register-first-name-error"
                    role="alert"
                  >
                    {errors.firstName}
                  </p>
                )}
              </div>


              <div className="register-field">
                <label htmlFor="register-last-name">
                  Last Name
                </label>

                <input
                  id="register-last-name"
                  className="register-input"
                  type="text"
                  autoComplete="family-name"
                  placeholder="Last name placeholder"
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
                    className="register-field-error"
                    id="register-last-name-error"
                    role="alert"
                  >
                    {errors.lastName}
                  </p>
                )}
              </div>
            </div>


            <div className="register-field">
              <label htmlFor="register-email">
                Email Address
              </label>

              <input
                id="register-email"
                className="register-input"
                type="email"
                autoComplete="email"
                placeholder="student@example.com"
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
                  className="register-field-error"
                  id="register-email-error"
                  role="alert"
                >
                  {errors.email}
                </p>
              )}
            </div>


            <div className="register-field">
              <label htmlFor="register-password">
                Password
              </label>

              <div className="register-password-control">
                <input
                  id="register-password"
                  className="register-input"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="Password"
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
                  className="register-password-toggle"
                  type="button"
                  aria-label={
                    showPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                  aria-pressed={showPassword}
                  onClick={() => {
                    setShowPassword((currentValue) => !currentValue)
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
                  className="register-field-error"
                  id="register-password-error"
                  role="alert"
                >
                  {errors.password}
                </p>
              )}
            </div>


            <div className="register-field">
              <label htmlFor="register-password-confirm">
                Confirm Password
              </label>

              <div className="register-password-control">
                <input
                  id="register-password-confirm"
                  className="register-input"
                  type={showPasswordConfirm ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="Confirm password"
                  value={passwordConfirm}
                  aria-invalid={Boolean(errors.passwordConfirm)}
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
                  className="register-password-toggle"
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
                  className="register-field-error"
                  id="register-password-confirm-error"
                  role="alert"
                >
                  {errors.passwordConfirm}
                </p>
              )}
            </div>


            <div
              className="register-password-requirements"
              id="register-password-help"
            >
              <h2>
                Password requirements based on system validation
              </h2>

              <p>
                At least 8 characters; not too common; not entirely
                numeric; not too similar to personal details.
              </p>
            </div>


            <div className="register-terms-placeholder">
              Terms / Privacy acknowledgement placeholder, if required.
            </div>


            {errors.form && (
              <p
                className="register-form-error"
                role="alert"
              >
                {errors.form}
              </p>
            )}


            <button
              className="gn-button gn-button--primary register-submit"
              type="submit"
              disabled={isLoading}
              aria-busy={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>


          <p className="register-login">
            <span>
              Already have an account?
            </span>

            <Link to="/login">
              Log In
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}


export default RegisterPage