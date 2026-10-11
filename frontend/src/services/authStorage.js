import {
  clearActiveInterviewSession,
} from './interviewSessionStorage'


const ACCESS_TOKEN_KEY = 'gradnavi_access_token'
const REFRESH_TOKEN_KEY = 'gradnavi_refresh_token'
const USER_KEY = 'gradnavi_user'

const USER_UPDATED_EVENT =
  'gradnavi:user-updated'


function storeStoredUser(userData) {
  localStorage.setItem(
    USER_KEY,
    JSON.stringify(userData),
  )

  if (
    typeof window !== 'undefined'
  ) {
    window.dispatchEvent(
      new CustomEvent(
        USER_UPDATED_EVENT,
        {
          detail: userData,
        },
      ),
    )
  }
}


function storeAuthSession(authData) {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    authData.access,
  )

  localStorage.setItem(
    REFRESH_TOKEN_KEY,
    authData.refresh,
  )

  storeStoredUser(
    authData.user,
  )
}


function clearAuthSession() {
  clearActiveInterviewSession()

  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)

  if (
    typeof window !== 'undefined'
  ) {
    window.dispatchEvent(
      new CustomEvent(
        USER_UPDATED_EVENT,
        {
          detail: null,
        },
      ),
    )
  }
}


function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}


function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}


function getStoredUser() {
  const storedUser = localStorage.getItem(USER_KEY)

  if (!storedUser) {
    return null
  }

  try {
    return JSON.parse(storedUser)
  } catch {
    /*
     * Corrupted authentication storage represents an
     * inconsistent session.
     *
     * Clear the full session instead of allowing the
     * application to continue with mismatched tokens
     * and user information.
     */
    clearAuthSession()

    return null
  }
}


function storeAccessToken(accessToken) {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    accessToken,
  )
}


function storeRefreshToken(refreshToken) {
  localStorage.setItem(
    REFRESH_TOKEN_KEY,
    refreshToken,
  )
}


function hasStoredAccessToken() {
  return Boolean(getAccessToken())
}


export {
  USER_UPDATED_EVENT,
  storeAuthSession,
  storeStoredUser,
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  getStoredUser,
  storeAccessToken,
  storeRefreshToken,
  hasStoredAccessToken,
}
