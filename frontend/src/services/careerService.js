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


export {
  getCareerRecommendations,
  getLearningSuggestions,
}
