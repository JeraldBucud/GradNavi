import { useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { registerAccount } from '../services/authService'

function RegisterPage() {
  const navigate = useNavigate()

  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    if (!firstName || !lastName || !email || !password || !passwordConfirm) {
      setError('All fields are required.')
      return
    }

    if (password !== passwordConfirm) {
      setError('Passwords do not match.')
      return
    }

    setError('')
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
  const errorDetails = requestError.data?.error?.details

  if (errorDetails?.password?.length) {
    setError(errorDetails.password.join(' '))
    return
  }

  if (errorDetails?.email?.length) {
    setError(errorDetails.email.join(' '))
    return
  }

  if (errorDetails?.first_name?.length) {
    setError(errorDetails.first_name.join(' '))
    return
  }

  if (errorDetails?.last_name?.length) {
    setError(errorDetails.last_name.join(' '))
    return
  }

  if (errorDetails?.password_confirm?.length) {
    setError(errorDetails.password_confirm.join(' '))
    return
  }

  setError(requestError.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main>
      <h1>Register</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="first-name">First Name</label>
          <input
            id="first-name"
            type="text"
            value={firstName}
            onChange={(event) => setFirstName(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="last-name">Last Name</label>
          <input
            id="last-name"
            type="text"
            value={lastName}
            onChange={(event) => setLastName(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="password-confirm">Confirm Password</label>
          <input
            id="password-confirm"
            type="password"
            value={passwordConfirm}
            onChange={(event) => setPasswordConfirm(event.target.value)}
          />
        </div>

        {error && <p>{error}</p>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating account...' : 'Register'}
        </button>
      </form>

      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </main>
  )
}

export default RegisterPage