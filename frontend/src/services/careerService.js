import apiRequest from './apiClient'


async function getCareerRecommendations() {
  return apiRequest('/recommendations/', {
    requiresAuth: true,
  })
}


async function getLearningSuggestions(careerId) {
  return apiRequest(
    `/learning-resources/?career_id=${encodeURIComponent(careerId)}`,
    {
      requiresAuth: true,
    },
  )
}



async function getTopMatchExplanation() {
  return apiRequest(
    '/recommendations/top-explanation/',
    {
      requiresAuth: true,
    },
  )
}


async function getCareerReadiness(
  careerId,
) {
  const encodedCareerId =
    encodeURIComponent(careerId)

  return apiRequest(
    `/readiness/?career_id=${encodedCareerId}`,
    {
      requiresAuth: true,
    },
  )
}


async function getSkillGapSummary(
  careerId,
) {
  const encodedCareerId =
    encodeURIComponent(careerId)

  return apiRequest(
    `/skill-gap-summary/?career_id=${encodedCareerId}`,
    {
      requiresAuth: true,
    },
  )
}


export {
  getCareerReadiness,
  getSkillGapSummary,
  getCareerRecommendations,
  getLearningSuggestions,
  getTopMatchExplanation,
}
