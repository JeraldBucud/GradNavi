const ACCESS_TOKEN_KEY = 'gradnavi_access_token'
const REFRESH_TOKEN_KEY = 'gradnavi_refresh_token'
const USER_KEY = 'gradnavi_user'


function storeAuthSession(authData) {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    authData.access,
  )

  localStorage.setItem(
    REFRESH_TOKEN_KEY,
    authData.refresh,
  )

  localStorage.setItem(
    USER_KEY,
    JSON.stringify(authData.user),
  )
}


function clearAuthSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
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
  storeAuthSession,
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  getStoredUser,
  storeAccessToken,
  storeRefreshToken,
  hasStoredAccessToken,
}