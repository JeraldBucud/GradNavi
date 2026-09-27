import apiRequest from './apiClient'

import {
  clearAuthSession,
  getRefreshToken,
  getStoredUser,
  hasStoredAccessToken,
  storeAuthSession,
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


async function logoutAccount() {
  const refreshToken = getRefreshToken()

  try {
    if (refreshToken) {
      await apiRequest('/auth/logout/', {
        method: 'POST',
        requiresAuth: true,
        body: () => ({
          refresh: getRefreshToken(),
        }),
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
  getStoredUser,
  hasStoredAccessToken,
  clearAuthSession,
}
