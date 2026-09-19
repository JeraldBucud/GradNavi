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
  getStoredCareerSelection,
  saveCareerSelection,
} from '../services/careerSelectionService'


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
    isLoadingRecommendations,
    setIsLoadingRecommendations,
  ] = useState(true)

  const [
    recommendationError,
    setRecommendationError,
  ] = useState('')

  const [
    storedSelection,
    setStoredSelection,
  ] = useState(
    () =>
      getStoredCareerSelection(),
  )


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


  const selectedCareer =
    useMemo(
      () => {
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
            storedSelection
              ?.career_id
            === urlCareerId
          ) {
            return storedSelection
          }

          return {
            career_id:
              urlCareerId,
            career_name: '',
          }
        }

        if (storedSelection) {
          const storedCareer =
            careerOptions.find(
              (career) =>
                Number(
                  career.career_id,
                )
                === Number(
                  storedSelection
                    .career_id,
                ),
            )

          if (storedCareer) {
            return storedCareer
          }
        }

        return (
          careerOptions[0]
          || null
        )
      },
      [
        careerOptions,
        storedSelection,
        urlCareerId,
      ],
    )


  const selectedCareerId =
    getPositiveCareerId(
      selectedCareer
        ?.career_id,
    )


  const isResolvingCareer =
    Boolean(
      isLoadingRecommendations
      && !selectedCareerId,
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
      if (!selectedCareerId) {
        return
      }

      const selectedCareerName =
        String(
          selectedCareer
            ?.career_name
          || '',
        ).trim()

      if (selectedCareerName) {
        const currentStoredId =
          Number(
            storedSelection
              ?.career_id,
          )

        const currentStoredName =
          String(
            storedSelection
              ?.career_name
            || '',
          ).trim()

        if (
          currentStoredId
            !== selectedCareerId
          || currentStoredName
            !== selectedCareerName
        ) {
          saveCareerSelection(
            {
              career_id:
                selectedCareerId,
              career_name:
                selectedCareerName,
            },
          )
        }
      }

      const currentUrlCareerId =
        getPositiveCareerId(
          searchParams.get(
            'career_id',
          ),
        )

      if (
        currentUrlCareerId
        === selectedCareerId
      ) {
        return
      }

      const nextParams =
        new URLSearchParams(
          searchParams,
        )

      nextParams.set(
        'career_id',
        String(
          selectedCareerId,
        ),
      )

      setSearchParams(
        nextParams,
        {
          replace: true,
        },
      )
    },
    [
      searchParams,
      selectedCareer,
      selectedCareerId,
      setSearchParams,
      storedSelection,
    ],
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

    const career =
      careerOptions.find(
        (option) =>
          Number(
            option.career_id,
          )
          === normalizedCareerId,
      )

    if (!career) {
      return false
    }

    const savedSelection =
      saveCareerSelection(
        {
          career_id:
            normalizedCareerId,
          career_name:
            career.career_name,
        },
      )

    setStoredSelection(
      savedSelection,
    )

    const nextParams =
      new URLSearchParams(
        searchParams,
      )

    nextParams.set(
      'career_id',
      String(
        normalizedCareerId,
      ),
    )

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
      recommendationError,
    isLoading:
      isResolvingCareer,
    selectedCareer,
    selectedCareerId,
    selectCareer,
    topCareer:
      careerOptions[0]
      || null,
  }
}


export default useCareerContext
