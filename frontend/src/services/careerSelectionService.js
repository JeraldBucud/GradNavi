const CAREER_SELECTION_STORAGE_KEY =
  'gradnavi.selectedCareer.v1'


function normalizeCareerSelection(
  value,
) {
  const careerId =
    Number(
      value?.career_id
      ?? value?.careerId,
    )

  const careerName =
    String(
      value?.career_name
      ?? value?.careerName
      ?? '',
    ).trim()

  if (
    !Number.isInteger(
      careerId,
    )
    || careerId <= 0
  ) {
    return null
  }

  return {
    career_id: careerId,
    career_name: careerName,
  }
}


function getStoredCareerSelection() {
  if (
    typeof window
    === 'undefined'
  ) {
    return null
  }

  try {
    const rawValue =
      window.localStorage.getItem(
        CAREER_SELECTION_STORAGE_KEY,
      )

    if (!rawValue) {
      return null
    }

    const parsedValue =
      JSON.parse(
        rawValue,
      )

    const normalizedValue =
      normalizeCareerSelection(
        parsedValue,
      )

    if (!normalizedValue) {
      window.localStorage.removeItem(
        CAREER_SELECTION_STORAGE_KEY,
      )

      return null
    }

    return normalizedValue
  } catch {
    window.localStorage.removeItem(
      CAREER_SELECTION_STORAGE_KEY,
    )

    return null
  }
}


function saveCareerSelection(
  value,
) {
  if (
    typeof window
    === 'undefined'
  ) {
    return null
  }

  const normalizedValue =
    normalizeCareerSelection(
      value,
    )

  if (!normalizedValue) {
    return null
  }

  window.localStorage.setItem(
    CAREER_SELECTION_STORAGE_KEY,
    JSON.stringify(
      normalizedValue,
    ),
  )

  return normalizedValue
}


function clearCareerSelection() {
  if (
    typeof window
    === 'undefined'
  ) {
    return
  }

  window.localStorage.removeItem(
    CAREER_SELECTION_STORAGE_KEY,
  )
}


export {
  CAREER_SELECTION_STORAGE_KEY,
  clearCareerSelection,
  getStoredCareerSelection,
  normalizeCareerSelection,
  saveCareerSelection,
}
