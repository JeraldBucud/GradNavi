import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  useSearchParams,
} from 'react-router'

import {
  getCareerRecommendations,
} from '../services/careerService'

import {
  getStudentProfile,
} from '../services/profileService'


function getRequestErrorMessage(
  requestError,
) {
  return (
    requestError
      ?.data
      ?.error
      ?.message
    || requestError?.message
    || 'Unable to load career choices.'
  )
}


function normalizeRecommendations(
  recommendations,
) {
  if (
    !Array.isArray(
      recommendations,
    )
  ) {
    return []
  }

  return [
    ...recommendations,
  ]
    .filter(
      (recommendation) => {
        const careerId =
          Number(
            recommendation
              ?.career_id,
          )

        return (
          Number.isInteger(
            careerId,
          )
          && careerId > 0
        )
      },
    )
    .sort(
      (first, second) =>
        Number(
          first.rank
          || 9999,
        )
        - Number(
          second.rank
          || 9999,
        ),
    )
}


function getPositiveCareerId(
  value,
) {
  const careerId =
    Number(
      value,
    )

  if (
    !Number.isInteger(
      careerId,
    )
    || careerId <= 0
  ) {
    return null
  }

  return careerId
}


function getPrimaryCareer(
  profile,
) {
  const careerGoals =
    Array.isArray(
      profile?.career_goals,
    )
      ? profile.career_goals
      : []

  const primaryGoal =
    careerGoals.find(
      (goal) =>
        Boolean(
          goal?.is_primary,
        )
        && Boolean(
          getPositiveCareerId(
            goal?.career_id,
          ),
        ),
    )

  if (!primaryGoal) {
    return null
  }

  return {
    career_id:
      getPositiveCareerId(
        primaryGoal.career_id,
      ),
    career_name:
      String(
        primaryGoal.target_role
        || '',
      ).trim(),
  }
}


function useCareerContext() {
  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams()

  const [
    recommendations,
    setRecommendations,
  ] = useState([])

  const [
    profile,
    setProfile,
  ] = useState(null)

  const [
    isLoadingRecommendations,
    setIsLoadingRecommendations,
  ] = useState(true)

  const [
    isLoadingProfile,
    setIsLoadingProfile,
  ] = useState(true)

  const [
    recommendationError,
    setRecommendationError,
  ] = useState('')

  const [
    profileError,
    setProfileError,
  ] = useState('')


  const urlCareerId =
    getPositiveCareerId(
      searchParams.get(
        'career_id',
      ),
    )


  const careerOptions =
    useMemo(
      () =>
        normalizeRecommendations(
          recommendations,
        ),
      [
        recommendations,
      ],
    )


  const primaryCareer =
    useMemo(
      () =>
        getPrimaryCareer(
          profile,
        ),
      [
        profile,
      ],
    )


  const primaryCareerId =
    getPositiveCareerId(
      primaryCareer
        ?.career_id,
    )


  const selectedCareer =
    useMemo(
      () => {
        /*
         * Explicit career_id is temporary page-level
         * exploration.
         *
         * Without an explicit career_id, the Student
         * Profile primary career is authoritative.
         *
         * Top recommendation is only the final fallback.
         */

        if (urlCareerId) {
          const urlCareer =
            careerOptions.find(
              (career) =>
                Number(
                  career.career_id,
                )
                === urlCareerId,
            )

          if (urlCareer) {
            return urlCareer
          }

          if (
            primaryCareerId
            === urlCareerId
          ) {
            return primaryCareer
          }

          return {
            career_id:
              urlCareerId,
            career_name: '',
          }
        }

        if (primaryCareer) {
          const recommendationCareer =
            careerOptions.find(
              (career) =>
                Number(
                  career.career_id,
                )
                === primaryCareerId,
            )

          if (recommendationCareer) {
            return {
              ...recommendationCareer,
              career_name:
                recommendationCareer
                  .career_name
                || primaryCareer
                  .career_name,
            }
          }

          return primaryCareer
        }

        return (
          careerOptions[0]
          || null
        )
      },
      [
        careerOptions,
        primaryCareer,
        primaryCareerId,
        urlCareerId,
      ],
    )


  const selectedCareerId =
    getPositiveCareerId(
      selectedCareer
        ?.career_id,
    )


  const isTemporarySelection =
    Boolean(
      urlCareerId
      && (
        !primaryCareerId
        || urlCareerId
          !== primaryCareerId
      )
    )


  const isResolvingCareer =
    Boolean(
      (
        isLoadingRecommendations
        || isLoadingProfile
      )
      && !selectedCareerId
    )


  useEffect(
    () => {
      let isActive = true

      async function loadRecommendations() {
        try {
          setRecommendationError('')

          const response =
            await getCareerRecommendations()

          if (!isActive) {
            return
          }

          const responseRecommendations =
            response
              ?.data
              ?.recommendations

          setRecommendations(
            Array.isArray(
              responseRecommendations,
            )
              ? responseRecommendations
              : [],
          )
        } catch (
          requestError
        ) {
          if (!isActive) {
            return
          }

          setRecommendationError(
            getRequestErrorMessage(
              requestError,
            ),
          )
        } finally {
          if (isActive) {
            setIsLoadingRecommendations(
              false,
            )
          }
        }
      }

      void loadRecommendations()

      return () => {
        isActive = false
      }
    },
    [],
  )


  useEffect(
    () => {
      let isActive = true

      async function loadProfile() {
        try {
          setProfileError('')

          const response =
            await getStudentProfile()

          if (!isActive) {
            return
          }

          setProfile(
            response
              ?.data
              ?.profile
            || null,
          )
        } catch (
          requestError
        ) {
          if (!isActive) {
            return
          }

          setProfileError(
            getRequestErrorMessage(
              requestError,
            ),
          )
        } finally {
          if (isActive) {
            setIsLoadingProfile(
              false,
            )
          }
        }
      }

      void loadProfile()

      return () => {
        isActive = false
      }
    },
    [],
  )


  function selectCareer(
    careerId,
    {
      clearSkillId = false,
    } = {},
  ) {
    const normalizedCareerId =
      getPositiveCareerId(
        careerId,
      )

    if (!normalizedCareerId) {
      return false
    }

    const recommendationCareer =
      careerOptions.find(
        (option) =>
          Number(
            option.career_id,
          )
          === normalizedCareerId,
      )

    const isPrimaryCareer =
      normalizedCareerId
      === primaryCareerId

    if (
      !recommendationCareer
      && !isPrimaryCareer
    ) {
      return false
    }

    const nextParams =
      new URLSearchParams(
        searchParams,
      )

    /*
     * Choosing the primary career restores the
     * default state and removes the temporary
     * career override from the URL.
     */
    if (isPrimaryCareer) {
      nextParams.delete(
        'career_id',
      )
    } else {
      nextParams.set(
        'career_id',
        String(
          normalizedCareerId,
        ),
      )
    }

    if (clearSkillId) {
      nextParams.delete(
        'skill_id',
      )
    }

    setSearchParams(
      nextParams,
    )

    return true
  }


  return {
    careerOptions,
    error:
      recommendationError
      || profileError,
    isLoading:
      isResolvingCareer,
    isTemporarySelection,
    primaryCareer,
    selectedCareer,
    selectedCareerId,
    selectCareer,
    topCareer:
      careerOptions[0]
      || null,
  }
}


export {
  getPrimaryCareer,
}

export default useCareerContext
