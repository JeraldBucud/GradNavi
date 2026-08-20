import { useState } from 'react'
import {
  Link,
  useLocation,
  useNavigate,
} from 'react-router'

import { loginAccount } from '../services/authService'

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const destination = location.state?.from || '/profile'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
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
      setError(requestError.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main>
      <h1>Login</h1>

      <form onSubmit={handleSubmit}>
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

        {error && <p>{error}</p>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p>
        Don&apos;t have an account? <Link to="/register">Register</Link>
      </p>
    </main>
  )
}

export default LoginPage