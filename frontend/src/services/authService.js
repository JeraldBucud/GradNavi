import apiRequest from './apiClient'

import {
  USER_UPDATED_EVENT,
  clearAuthSession,
  getRefreshToken,
  getStoredUser,
  hasStoredAccessToken,
  storeAuthSession,
  storeStoredUser,
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




async function getAccountSettings() {
  const accountData = await apiRequest(
    '/auth/settings/',
    {
      requiresAuth: true,
    },
  )

  storeStoredUser(
    accountData,
  )

  return accountData
}


async function updateAccountSettings(
  accountData,
) {
  const updatedAccount =
    await apiRequest(
      '/auth/settings/',
      {
        method: 'PATCH',
        requiresAuth: true,
        body: accountData,
      },
    )

  storeStoredUser(
    updatedAccount,
  )

  return updatedAccount
}


async function uploadProfilePhoto(
  profilePhoto,
) {
  const formData =
    new FormData()

  formData.append(
    'profile_photo',
    profilePhoto,
  )

  const updatedAccount =
    await apiRequest(
      '/auth/settings/',
      {
        method: 'PATCH',
        requiresAuth: true,
        body: formData,
      },
    )

  storeStoredUser(
    updatedAccount,
  )

  return updatedAccount
}


async function removeProfilePhoto() {
  const updatedAccount =
    await apiRequest(
      '/auth/settings/profile-photo/',
      {
        method: 'DELETE',
        requiresAuth: true,
      },
    )

  storeStoredUser(
    updatedAccount,
  )

  return updatedAccount
}


async function changePassword(
  passwordData,
) {
  return apiRequest(
    '/auth/password/change/',
    {
      method: 'POST',
      requiresAuth: true,
      body: passwordData,
    },
  )
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
  USER_UPDATED_EVENT,
  registerAccount,
  loginAccount,
  requestPasswordReset,
  confirmPasswordReset,
  getAccountSettings,
  updateAccountSettings,
  uploadProfilePhoto,
  removeProfilePhoto,
  changePassword,
  logoutAccount,
  getCurrentUser,
  getStoredUser,
  hasStoredAccessToken,
  clearAuthSession,
}
