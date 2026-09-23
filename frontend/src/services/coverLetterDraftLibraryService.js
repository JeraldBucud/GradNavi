const COVER_LETTER_LIBRARY_STORAGE_BASE_KEY =
  'gradnavi_cover_letter_builder_library_v2'

const LEGACY_COVER_LETTER_STORAGE_BASE_KEY =
  'gradnavi_cover_letter_builder_draft_v1'

const COVER_LETTER_LIBRARY_SCHEMA_VERSION = 2


function getStorageIdentity(
  user,
) {
  const identity =
    user?.id
    ?? user?.email

  if (
    identity === undefined
    || identity === null
  ) {
    return null
  }

  const normalized =
    String(
      identity,
    ).trim()

  if (!normalized) {
    return null
  }

  return encodeURIComponent(
    normalized,
  )
}


function getCoverLetterLibraryStorageKey(
  user,
) {
  const identity =
    getStorageIdentity(
      user,
    )

  if (!identity) {
    return null
  }

  return (
    `${COVER_LETTER_LIBRARY_STORAGE_BASE_KEY}:`
    + identity
  )
}


function getLegacyCoverLetterStorageKey(
  user,
) {
  const identity =
    getStorageIdentity(
      user,
    )

  if (!identity) {
    return null
  }

  return (
    `${LEGACY_COVER_LETTER_STORAGE_BASE_KEY}:`
    + identity
  )
}


function emptyLibrary() {
  return {
    schema_version:
      COVER_LETTER_LIBRARY_SCHEMA_VERSION,
    active_version_id: null,
    versions: [],
  }
}


function normalizeCareerId(
  value,
) {
  const careerId =
    Number(
      value,
    )

  if (!Number.isInteger(careerId)) {
    return null
  }

  if (careerId <= 0) {
    return null
  }

  return careerId
}


function normalizeText(
  value,
) {
  return String(
    value ?? '',
  ).trim()
}


function normalizeLibrary(
  value,
) {
  if (
    !value
    || typeof value !== 'object'
  ) {
    return emptyLibrary()
  }

  const versions =
    Array.isArray(
      value.versions,
    )
      ? value.versions.filter(
          (version) =>
            version
            && typeof version
              === 'object',
        )
      : []

  const activeVersionId =
    normalizeText(
      value.active_version_id,
    )
    || null

  return {
    schema_version:
      COVER_LETTER_LIBRARY_SCHEMA_VERSION,
    active_version_id:
      activeVersionId,
    versions,
  }
}


function loadCoverLetterDraftLibrary(
  user,
) {
  const storageKey =
    getCoverLetterLibraryStorageKey(
      user,
    )

  if (!storageKey) {
    return emptyLibrary()
  }

  try {
    const stored =
      localStorage.getItem(
        storageKey,
      )

    if (!stored) {
      return emptyLibrary()
    }

    return normalizeLibrary(
      JSON.parse(
        stored,
      ),
    )
  }
  catch {
    return emptyLibrary()
  }
}


function saveCoverLetterDraftLibrary(
  user,
  library,
) {
  const storageKey =
    getCoverLetterLibraryStorageKey(
      user,
    )

  if (!storageKey) {
    return false
  }

  localStorage.setItem(
    storageKey,
    JSON.stringify(
      normalizeLibrary(
        library,
      ),
    ),
  )

  return true
}


function createCoverLetterVersionId() {
  if (
    typeof crypto !== 'undefined'
    && typeof crypto.randomUUID
      === 'function'
  ) {
    return crypto.randomUUID()
  }

  return (
    'cover-letter-'
    + Date.now()
    + '-'
    + Math.random()
        .toString(36)
        .slice(2, 10)
  )
}


function buildCoverLetterVersionLabel({
  versionName = '',
  jobTitle = '',
  company = '',
} = {}) {
  const normalizedVersionName =
    normalizeText(
      versionName,
    )

  if (normalizedVersionName) {
    return normalizedVersionName
  }

  const normalizedJobTitle =
    normalizeText(
      jobTitle,
    )

  const normalizedCompany =
    normalizeText(
      company,
    )

  if (
    normalizedJobTitle
    && normalizedCompany
  ) {
    return (
      `Cover Letter - ${normalizedJobTitle} at `
      + normalizedCompany
    )
  }

  if (normalizedCompany) {
    return (
      `Cover Letter - ${normalizedCompany}`
    )
  }

  if (normalizedJobTitle) {
    return (
      `Cover Letter - ${normalizedJobTitle}`
    )
  }

  return 'Cover Letter'
}


function normalizeVersion({
  id,
  targetCareerId,
  targetCareerName,
  versionName,
  tone = 'professional',
  coverLetterFocus = 'balanced',
  jobTitle = '',
  company = '',
  jobDescription = '',
  draft = null,
  savedAt = null,
} = {}) {
  const careerId =
    normalizeCareerId(
      targetCareerId,
    )

  const careerName =
    normalizeText(
      targetCareerName,
    )

  if (!careerId) {
    return null
  }

  if (!careerName) {
    return null
  }

  const normalizedJobTitle =
    normalizeText(
      jobTitle,
    )

  const normalizedCompany =
    normalizeText(
      company,
    )

  const normalizedJobDescription =
    normalizeText(
      jobDescription,
    )

  const normalizedVersionName =
    buildCoverLetterVersionLabel({
      versionName,
      jobTitle:
        normalizedJobTitle,
      company:
        normalizedCompany,
    })

  return {
    id:
      normalizeText(
        id,
      )
      || createCoverLetterVersionId(),

    target_career_id:
      careerId,

    target_career_name:
      careerName,

    version_name:
      normalizedVersionName,

    tone:
      normalizeText(
        tone,
      )
      || 'professional',

    cover_letter_focus:
      normalizeText(
        coverLetterFocus,
      )
      || 'balanced',

    job_title:
      normalizedJobTitle,

    company:
      normalizedCompany,

    job_description:
      normalizedJobDescription,

    draft:
      draft
      && typeof draft === 'object'
        ? draft
        : null,

    saved_at:
      normalizeText(
        savedAt,
      )
      || new Date()
          .toISOString(),
  }
}


function upsertCoverLetterDraftVersion(
  user,
  versionInput,
) {
  const version =
    normalizeVersion(
      versionInput,
    )

  if (!version) {
    return null
  }

  const library =
    loadCoverLetterDraftLibrary(
      user,
    )

  const existingIndex =
    library.versions.findIndex(
      (candidate) =>
        candidate.id
        === version.id,
    )

  if (existingIndex >= 0) {
    library.versions[
      existingIndex
    ] = version
  }
  else {
    library.versions.push(
      version,
    )
  }

  library.active_version_id =
    version.id

  const saved =
    saveCoverLetterDraftLibrary(
      user,
      library,
    )

  if (!saved) {
    return null
  }

  return version
}


function getCoverLetterDraftVersion(
  user,
  versionId,
) {
  const normalizedVersionId =
    normalizeText(
      versionId,
    )

  if (!normalizedVersionId) {
    return null
  }

  const library =
    loadCoverLetterDraftLibrary(
      user,
    )

  return (
    library.versions.find(
      (version) =>
        version.id
        === normalizedVersionId,
    )
    ?? null
  )
}


function listCoverLetterDraftVersions(
  user,
  targetCareerId = null,
) {
  const library =
    loadCoverLetterDraftLibrary(
      user,
    )

  const normalizedCareerId =
    normalizeCareerId(
      targetCareerId,
    )

  const versions =
    normalizedCareerId
      ? library.versions.filter(
          (version) =>
            Number(
              version.target_career_id,
            )
            === normalizedCareerId,
        )
      : library.versions

  return [...versions]
    .sort(
      (
        first,
        second,
      ) => {
        const firstTime =
          Date.parse(
            first.saved_at,
          )
          || 0

        const secondTime =
          Date.parse(
            second.saved_at,
          )
          || 0

        return (
          secondTime
          - firstTime
        )
      },
    )
}


function setActiveCoverLetterVersion(
  user,
  versionId,
) {
  const version =
    getCoverLetterDraftVersion(
      user,
      versionId,
    )

  if (!version) {
    return false
  }

  const library =
    loadCoverLetterDraftLibrary(
      user,
    )

  library.active_version_id =
    version.id

  return saveCoverLetterDraftLibrary(
    user,
    library,
  )
}


function getActiveCoverLetterVersion(
  user,
) {
  const library =
    loadCoverLetterDraftLibrary(
      user,
    )

  if (!library.active_version_id) {
    return null
  }

  return (
    library.versions.find(
      (version) =>
        version.id
        === library.active_version_id,
    )
    ?? null
  )
}


function removeCoverLetterDraftVersion(
  user,
  versionId,
) {
  const normalizedVersionId =
    normalizeText(
      versionId,
    )

  if (!normalizedVersionId) {
    return false
  }

  const library =
    loadCoverLetterDraftLibrary(
      user,
    )

  const originalCount =
    library.versions.length

  library.versions =
    library.versions.filter(
      (version) =>
        version.id
        !== normalizedVersionId,
    )

  if (
    library.versions.length
    === originalCount
  ) {
    return false
  }

  if (
    library.active_version_id
    === normalizedVersionId
  ) {
    library.active_version_id =
      library.versions[0]?.id
      ?? null
  }

  return saveCoverLetterDraftLibrary(
    user,
    library,
  )
}


function loadLegacyCoverLetterDraft(
  user,
) {
  const storageKey =
    getLegacyCoverLetterStorageKey(
      user,
    )

  if (!storageKey) {
    return null
  }

  try {
    const stored =
      localStorage.getItem(
        storageKey,
      )

    if (!stored) {
      return null
    }

    const parsed =
      JSON.parse(
        stored,
      )

    if (
      !parsed
      || typeof parsed !== 'object'
    ) {
      return null
    }

    return parsed
  }
  catch {
    return null
  }
}


function clearLegacyCoverLetterDraft(
  user,
) {
  const storageKey =
    getLegacyCoverLetterStorageKey(
      user,
    )

  if (!storageKey) {
    return
  }

  localStorage.removeItem(
    storageKey,
  )
}


export {
  buildCoverLetterVersionLabel,
  clearLegacyCoverLetterDraft,
  createCoverLetterVersionId,
  getActiveCoverLetterVersion,
  getCoverLetterDraftVersion,
  listCoverLetterDraftVersions,
  loadCoverLetterDraftLibrary,
  loadLegacyCoverLetterDraft,
  removeCoverLetterDraftVersion,
  setActiveCoverLetterVersion,
  upsertCoverLetterDraftVersion,
}
