import {
  getCareerRecommendations,
} from './careerService'

import {
  getStoredCareerSelection,
} from './careerSelectionService'

import {
  getStudentProfile,
} from './profileService'


function normalizePositiveId(
  value,
) {
  const id =
    Number(
      value,
    )

  if (!Number.isInteger(id)) {
    return null
  }

  if (id <= 0) {
    return null
  }

  return id
}


function normalizeCareerName(
  value,
) {
  return String(
    value ?? '',
  ).trim()
}


function extractProfileData(
  response,
) {
  return (
    response?.data
    ?? response
    ?? {}
  )
}


function extractRecommendationData(
  response,
) {
  return (
    response?.data
    ?? response
    ?? {}
  )
}


function createCareerOption({
  careerId,
  careerName,
  isPrimary = false,
  recommendationRank = null,
  fromCareerGoal = false,
  fromRecommendation = false,
}) {
  const normalizedId =
    normalizePositiveId(
      careerId,
    )

  const normalizedName =
    normalizeCareerName(
      careerName,
    )

  if (!normalizedId) {
    return null
  }

  if (!normalizedName) {
    return null
  }

  const numericRank =
    Number(
      recommendationRank,
    )

  const normalizedRank =
    Number.isInteger(
      numericRank,
    )
      ? numericRank
      : null

  return {
    career_id:
      normalizedId,
    career_name:
      normalizedName,
    is_primary:
      Boolean(
        isPrimary,
      ),
    recommendation_rank:
      normalizedRank,
    from_career_goal:
      Boolean(
        fromCareerGoal,
      ),
    from_recommendation:
      Boolean(
        fromRecommendation,
      ),
  }
}


function mergeCareerOption(
  optionsById,
  incoming,
) {
  if (!incoming) {
    return
  }

  const current =
    optionsById.get(
      incoming.career_id,
    )

  if (!current) {
    optionsById.set(
      incoming.career_id,
      incoming,
    )

    return
  }

  optionsById.set(
    incoming.career_id,
    {
      ...current,
      career_name:
        current.career_name
        || incoming.career_name,
      is_primary:
        current.is_primary
        || incoming.is_primary,
      recommendation_rank:
        current.recommendation_rank
        ?? incoming.recommendation_rank,
      from_career_goal:
        current.from_career_goal
        || incoming.from_career_goal,
      from_recommendation:
        current.from_recommendation
        || incoming.from_recommendation,
    },
  )
}


function compareCareerOptions(
  first,
  second,
) {
  if (
    first.is_primary
    !== second.is_primary
  ) {
    return first.is_primary
      ? -1
      : 1
  }

  const firstRank =
    first.recommendation_rank

  const secondRank =
    second.recommendation_rank

  if (firstRank !== null) {
    if (secondRank === null) {
      return -1
    }

    if (firstRank !== secondRank) {
      return (
        firstRank
        - secondRank
      )
    }
  }

  if (secondRank !== null) {
    return 1
  }

  return (
    first.career_name
      .localeCompare(
        second.career_name,
      )
  )
}


function resolveDefaultCareerId(
  options,
) {
  if (!options.length) {
    return null
  }

  const storedSelection =
    getStoredCareerSelection()

  const storedCareerId =
    normalizePositiveId(
      storedSelection
        ?.career_id,
    )

  if (storedCareerId) {
    const storedExists =
      options.some(
        (option) =>
          option.career_id
          === storedCareerId,
      )

    if (storedExists) {
      return storedCareerId
    }
  }

  const primaryGoal =
    options.find(
      (option) =>
        option.is_primary,
    )

  if (primaryGoal) {
    return primaryGoal.career_id
  }

  const topRecommendation =
    options.find(
      (option) =>
        option.recommendation_rank
        === 1,
    )

  if (topRecommendation) {
    return (
      topRecommendation
        .career_id
    )
  }

  return options[0].career_id
}


async function loadDocumentCareerOptions() {
  const [
    profileResult,
    recommendationResult,
  ] =
    await Promise.allSettled([
      getStudentProfile(),
      getCareerRecommendations(),
    ])

  if (
    profileResult.status
    !== 'fulfilled'
  ) {
    throw profileResult.reason
  }

  const profile =
    extractProfileData(
      profileResult.value,
    )

  let recommendationPayload = {}

  if (
    recommendationResult.status
    === 'fulfilled'
  ) {
    recommendationPayload =
      extractRecommendationData(
        recommendationResult.value,
      )
  }

  const careerGoals =
    Array.isArray(
      profile?.career_goals,
    )
      ? profile.career_goals
      : []

  const recommendations =
    Array.isArray(
      recommendationPayload
        ?.recommendations,
    )
      ? recommendationPayload
          .recommendations
      : []

  const optionsById =
    new Map()

  careerGoals.forEach(
    (goal) => {
      mergeCareerOption(
        optionsById,
        createCareerOption({
          careerId:
            goal?.career_id,
          careerName:
            goal?.target_role,
          isPrimary:
            goal?.is_primary,
          fromCareerGoal:
            true,
        }),
      )
    },
  )

  recommendations.forEach(
    (recommendation) => {
      mergeCareerOption(
        optionsById,
        createCareerOption({
          careerId:
            recommendation
              ?.career_id,
          careerName:
            recommendation
              ?.career_name,
          recommendationRank:
            recommendation
              ?.rank,
          fromRecommendation:
            true,
        }),
      )
    },
  )

  const options =
    Array.from(
      optionsById.values(),
    )

  options.sort(
    compareCareerOptions,
  )

  return {
    career_options:
      options,
    default_career_id:
      resolveDefaultCareerId(
        options,
      ),
    recommendation_status:
      recommendationResult.status
      === 'fulfilled'
        ? 'available'
        : 'unavailable',
  }
}


export {
  loadDocumentCareerOptions,
}
