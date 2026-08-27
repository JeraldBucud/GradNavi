import apiRequest from './apiClient'

async function getStudentProfile() {
  return apiRequest('/profile/', {
    requiresAuth: true,
  })
}

async function updateStudentProfile(profileData) {
  return apiRequest('/profile/', {
    method: 'PATCH',
    requiresAuth: true,
    body: profileData,
  })
}

export {
  getStudentProfile,
  updateStudentProfile,
}