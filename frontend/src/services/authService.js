import apiRequest from './apiClient'

import {
  clearAuthSession,
  getRefreshToken,
  getStoredUser,
  hasStoredAccessToken,
  storeAccessToken,
  storeAuthSession,
  storeRefreshToken,
} from './authStorage'


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


async function requestPasswordReset(email) {
  return apiRequest('/auth/password/reset/', {
    method: 'POST',
    body: {
      email,
    },
  })
}


async function confirmPasswordReset(resetData) {
  return apiRequest('/auth/password/reset/confirm/', {
    method: 'POST',
    body: resetData,
  })
}


async function getCurrentUser() {
  return apiRequest('/auth/me/', {
    requiresAuth: true,
  })
}


async function refreshAccessToken() {
  const refreshToken = getRefreshToken()

  if (!refreshToken) {
    throw new Error(
      'No refresh token is available.',
    )
  }

  const tokenData = await apiRequest(
    '/auth/token/refresh/',
    {
      method: 'POST',
      body: {
        refresh: refreshToken,
      },
    },
  )

  storeAccessToken(tokenData.access)

  if (tokenData.refresh) {
    storeRefreshToken(tokenData.refresh)
  }

  return tokenData
}


async function logoutAccount() {
  const refreshToken = getRefreshToken()

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
    /*
     * Local logout must always finish.
     *
     * A failed server request must not leave access,
     * refresh, or user information in browser storage.
     */
    clearAuthSession()
  }
}


export {
  registerAccount,
  loginAccount,
  requestPasswordReset,
  confirmPasswordReset,
  logoutAccount,
  getCurrentUser,
  refreshAccessToken,
  getStoredUser,
  hasStoredAccessToken,
  clearAuthSession,
}