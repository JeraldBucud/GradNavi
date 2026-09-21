import { getAccessToken } from './authStorage'


const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'


async function apiRequest(endpoint, options = {}) {
  const {
    method = 'GET',
    body = null,
    requiresAuth = false,
  } = options

  const headers = {
    'Content-Type': 'application/json',
  }

  if (requiresAuth) {
    const accessToken = getAccessToken()

    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`
    }
  }

  const requestOptions = {
    method,
    headers,
  }

  if (body !== null) {
    requestOptions.body = JSON.stringify(body)
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    requestOptions,
  )

  let responseData = null

  if (response.status !== 204) {
    const contentType =
      response.headers.get('content-type')
      || ''

    if (
      contentType
        .toLowerCase()
        .includes('application/json')
    ) {
      responseData =
        await response.json()
    }
    else {
      const error = new Error(
        'The server returned an unexpected response. '
        + 'Please try again.',
      )

      error.status = response.status
      error.data = null

      throw error
    }
  }

  if (!response.ok) {
    const error = new Error(
      responseData?.error?.message
      || 'API request failed.',
    )

    error.status = response.status
    error.data = responseData

    throw error
  }

  return responseData
}


export default apiRequest