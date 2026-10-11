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


async function getRoadmapOverview(
  careerId,
) {
  const encodedCareerId =
    encodeURIComponent(
      careerId,
    )

  return apiRequest(
    `/roadmap-overview/?career_id=${encodedCareerId}`,
    {
      requiresAuth: true,
    },
  )
}


async function startRoadmapStep(
  careerId,
  skillId,
) {
  return apiRequest(
    '/roadmap-progress/start/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        career_id: careerId,
        skill_id: skillId,
      },
    },
  )
}


async function completeRoadmapStep(
  careerId,
  skillId,
) {
  return apiRequest(
    '/roadmap-progress/complete/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        career_id: careerId,
        skill_id: skillId,
      },
    },
  )
}


async function getLearningResourceRecommendations(
  careerId,
  skillId,
  accessType = '',
) {
  const params =
    new URLSearchParams()

  params.set(
    'career_id',
    String(
      careerId,
    ),
  )

  params.set(
    'skill_id',
    String(
      skillId,
    ),
  )

  if (accessType) {
    params.set(
      'access_type',
      accessType,
    )
  }

  return apiRequest(
    (
      '/learning-resource-recommendations/'
      + `?${params.toString()}`
    ),
    {
      requiresAuth: true,
    },
  )
}


async function setLearningResourceFeedback(
  resourceId,
  feedbackType,
) {
  const encodedResourceId =
    encodeURIComponent(
      resourceId,
    )

  return apiRequest(
    (
      '/learning-resource-feedback/'
      + `${encodedResourceId}/`
    ),
    {
      method: 'PUT',
      requiresAuth: true,
      body: {
        feedback_type: feedbackType,
      },
    },
  )
}


async function reportLearningResource({
  resourceId,
  reason,
  comment = '',
}) {
  return apiRequest(
    '/learning-resource-reports/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        resource_id: resourceId,
        reason,
        comment,
      },
    },
  )
}


async function getExploreCareers({
  search = '',
  category = '',
  status = 'all',
  page = 1,
  pageSize = 12,
} = {}) {
  const params =
    new URLSearchParams()

  const normalizedSearch =
    String(
      search || '',
    ).trim()

  const normalizedCategory =
    String(
      category || '',
    ).trim()

  const normalizedStatus =
    String(
      status || 'all',
    ).trim()

  if (normalizedSearch) {
    params.set(
      'search',
      normalizedSearch,
    )
  }

  if (normalizedCategory) {
    params.set(
      'category',
      normalizedCategory,
    )
  }

  params.set(
    'status',
    normalizedStatus || 'all',
  )

  params.set(
    'page',
    String(
      page,
    ),
  )

  params.set(
    'page_size',
    String(
      pageSize,
    ),
  )

  return apiRequest(
    (
      '/explore-careers/'
      + `?${params.toString()}`
    ),
    {
      requiresAuth: true,
    },
  )
}


async function getExploreCareerDetail(
  careerId,
) {
  const encodedCareerId =
    encodeURIComponent(
      careerId,
    )

  return apiRequest(
    (
      '/explore-careers/'
      + `${encodedCareerId}/`
    ),
    {
      requiresAuth: true,
    },
  )
}


async function evaluateExploreCareer(
  careerId,
) {
  const encodedCareerId =
    encodeURIComponent(
      careerId,
    )

  return apiRequest(
    (
      '/explore-careers/'
      + `${encodedCareerId}/evaluate/`
    ),
    {
      method: 'POST',
      requiresAuth: true,
    },
  )
}


async function getGuidanceCareers() {
  return apiRequest(
    '/guidance-careers/',
    {
      requiresAuth: true,
    },
  )
}


export {
  completeRoadmapStep,
  evaluateExploreCareer,
  getExploreCareerDetail,
  getExploreCareers,
  getGuidanceCareers,
  getLearningResourceRecommendations,
  getRoadmapOverview,
  reportLearningResource,
  setLearningResourceFeedback,
  startRoadmapStep,
  getCareerReadiness,
  getSkillGapSummary,
  getCareerRecommendations,
  getLearningSuggestions,
  getTopMatchExplanation,
}
