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


async function searchProfileSkills(search = '') {
  const query =
    encodeURIComponent(
      search.trim(),
    )

  return apiRequest(
    `/profile/reference/skills/?search=${query}`,
    {
      requiresAuth: true,
    },
  )
}


async function searchProfileInterests(
  search = '',
) {
  const query =
    encodeURIComponent(
      search.trim(),
    )

  return apiRequest(
    `/profile/reference/interests/?search=${query}`,
    {
      requiresAuth: true,
    },
  )
}


async function searchProfileCareers(
  search = '',
) {
  const query =
    encodeURIComponent(
      search.trim(),
    )

  return apiRequest(
    `/profile/reference/careers/?search=${query}`,
    {
      requiresAuth: true,
    },
  )
}


export {
  getStudentProfile,
  searchProfileCareers,
  searchProfileInterests,
  searchProfileSkills,
  updateStudentProfile,
}
