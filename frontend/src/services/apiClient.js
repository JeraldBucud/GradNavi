import {
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  storeAccessToken,
  storeRefreshToken,
} from './authStorage'


const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'
const TOKEN_REFRESH_ENDPOINT = '/auth/token/refresh/'

let refreshPromise = null


function createApiError(
  response,
  responseData,
) {
  const error = new Error(
    responseData?.error?.message
    || 'API request failed.',
  )

  error.status = response.status
  error.data = responseData

  return error
}


function createSessionExpiredError(
  responseData = null,
) {
  const error = new Error(
    'Your session has expired. Please sign in again.',
  )

  error.status = 401
  error.data = responseData

  return error
}


async function readResponseData(response) {
  if (response.status === 204) {
    return null
  }

  const contentType =
    response.headers.get('content-type')
    || ''

  if (
    contentType
      .toLowerCase()
      .includes('application/json')
  ) {
    return response.json()
  }

  const error = new Error(
    'The server returned an unexpected response. '
    + 'Please try again.',
  )

  error.status = response.status
  error.data = null

  throw error
}


async function sendRequest(
  endpoint,
  {
    method,
    body,
    requiresAuth,
  },
  accessToken = null,
) {
  const headers = {}

  if (
    requiresAuth
    && accessToken
  ) {
    headers.Authorization =
      `Bearer ${accessToken}`
  }

  const requestOptions = {
    method,
    headers,
  }

  if (body !== null) {
    const requestBody =
      typeof body === 'function'
        ? body()
        : body

    const isFormData =
      typeof FormData !== 'undefined'
      && requestBody instanceof FormData

    if (isFormData) {
      requestOptions.body =
        requestBody
    } else {
      headers['Content-Type'] =
        'application/json'

      requestOptions.body =
        JSON.stringify(requestBody)
    }
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    requestOptions,
  )

  const responseData =
    await readResponseData(response)

  return {
    response,
    responseData,
  }
}


async function performTokenRefresh() {
  const refreshToken =
    getRefreshToken()

  if (!refreshToken) {
    clearAuthSession()

    throw createSessionExpiredError()
  }

  let response
  let responseData

  try {
    const result = await sendRequest(
      TOKEN_REFRESH_ENDPOINT,
      {
        method: 'POST',
        body: {
          refresh: refreshToken,
        },
        requiresAuth: false,
      },
    )

    response = result.response
    responseData = result.responseData
  }
  catch {
    clearAuthSession()

    throw createSessionExpiredError()
  }

  if (!response.ok) {
    clearAuthSession()

    throw createSessionExpiredError(
      responseData,
    )
  }

  const newAccessToken =
    responseData?.access

  if (
    typeof newAccessToken !== 'string'
    || !newAccessToken
  ) {
    clearAuthSession()

    throw createSessionExpiredError()
  }

  storeAccessToken(
    newAccessToken,
  )

  if (
    typeof responseData?.refresh === 'string'
    && responseData.refresh
  ) {
    storeRefreshToken(
      responseData.refresh,
    )
  }

  return newAccessToken
}


function refreshAuthSession() {
  if (!refreshPromise) {
    refreshPromise =
      performTokenRefresh()
        .finally(() => {
          refreshPromise = null
        })
  }

  return refreshPromise
}


async function retryAuthenticatedRequest(
  endpoint,
  requestConfig,
  accessToken,
) {
  const {
    response,
    responseData,
  } = await sendRequest(
    endpoint,
    requestConfig,
    accessToken,
  )

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthSession()

      throw createSessionExpiredError(
        responseData,
      )
    }

    throw createApiError(
      response,
      responseData,
    )
  }

  return responseData
}


async function apiRequest(
  endpoint,
  options = {},
) {
  const {
    method = 'GET',
    body = null,
    requiresAuth = false,
  } = options

  const requestConfig = {
    method,
    body,
    requiresAuth,
  }

  const accessToken =
    requiresAuth
      ? getAccessToken()
      : null

  const {
    response,
    responseData,
  } = await sendRequest(
    endpoint,
    requestConfig,
    accessToken,
  )

  const shouldAttemptRefresh =
    requiresAuth
    && response.status === 401
    && endpoint !== TOKEN_REFRESH_ENDPOINT

  if (!shouldAttemptRefresh) {
    if (!response.ok) {
      throw createApiError(
        response,
        responseData,
      )
    }

    return responseData
  }

  const currentAccessToken =
    getAccessToken()

  let retryAccessToken =
    currentAccessToken

  /*
   * Another request may already have refreshed the
   * session while this request was in flight.
   *
   * When the stored token differs from the token used
   * for the failed request, reuse the newer token
   * instead of rotating the refresh token again.
   */
  if (
    !retryAccessToken
    || retryAccessToken === accessToken
  ) {
    retryAccessToken =
      await refreshAuthSession()
  }

  return retryAuthenticatedRequest(
    endpoint,
    requestConfig,
    retryAccessToken,
  )
}


export default apiRequest
