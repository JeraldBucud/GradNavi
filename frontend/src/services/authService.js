import apiRequest from './apiClient'

const ACCESS_TOKEN_KEY = 'gradnavi_access_token'
const REFRESH_TOKEN_KEY = 'gradnavi_refresh_token'
const USER_KEY = 'gradnavi_user'

function storeAuthSession(authData) {
  localStorage.setItem(ACCESS_TOKEN_KEY, authData.access)
  localStorage.setItem(REFRESH_TOKEN_KEY, authData.refresh)
  localStorage.setItem(USER_KEY, JSON.stringify(authData.user))
}

function clearAuthSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

function getStoredUser() {
  const storedUser = localStorage.getItem(USER_KEY)

  if (!storedUser) {
    return null
  }

  return JSON.parse(storedUser)
}

async function registerAccount(registrationData) {
  return apiRequest('/auth/register/', {
    method: 'POST',
    body: registrationData,
  })
}

async function loginAccount(email, password) {
  const authData = await apiRequest('/auth/login/', {
    method: 'POST',
    body: {
      email,
      password,
    },
  })

  storeAuthSession(authData)

  return authData
}

async function getCurrentUser() {
  return apiRequest('/auth/me/', {
    requiresAuth: true,
  })
}

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

  if (!refreshToken) {
    throw new Error('No refresh token is available.')
  }

  const tokenData = await apiRequest('/auth/token/refresh/', {
    method: 'POST',
    body: {
      refresh: refreshToken,
    },
  })

  localStorage.setItem(ACCESS_TOKEN_KEY, tokenData.access)

  if (tokenData.refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, tokenData.refresh)
  }

  return tokenData
}

async function logoutAccount() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

  try {
    if (refreshToken) {
      await apiRequest('/auth/logout/', {
        method: 'POST',
        requiresAuth: true,
        body: {
          refresh: refreshToken,
        },
      })
    }
  } finally {
    clearAuthSession()
  }
}

export {
  registerAccount,
  loginAccount,
  logoutAccount,
  getCurrentUser,
  refreshAccessToken,
  getStoredUser,
  clearAuthSession,
}