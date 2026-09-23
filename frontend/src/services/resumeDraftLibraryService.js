const RESUME_LIBRARY_STORAGE_BASE_KEY =
  'gradnavi_resume_builder_library_v2'

const LEGACY_RESUME_STORAGE_BASE_KEY =
  'gradnavi_resume_builder_draft_v1'

const RESUME_LIBRARY_SCHEMA_VERSION = 2


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


function getResumeLibraryStorageKey(
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
    `${RESUME_LIBRARY_STORAGE_BASE_KEY}:`
    + identity
  )
}


function getLegacyResumeStorageKey(
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
    `${LEGACY_RESUME_STORAGE_BASE_KEY}:`
    + identity
  )
}


function emptyLibrary() {
  return {
    schema_version:
      RESUME_LIBRARY_SCHEMA_VERSION,
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
      ? value.versions
          .filter(
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
      RESUME_LIBRARY_SCHEMA_VERSION,
    active_version_id:
      activeVersionId,
    versions,
  }
}


function loadResumeDraftLibrary(
  user,
) {
  const storageKey =
    getResumeLibraryStorageKey(
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


function saveResumeDraftLibrary(
  user,
  library,
) {
  const storageKey =
    getResumeLibraryStorageKey(
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


function createResumeVersionId() {
  if (
    typeof crypto !== 'undefined'
    && typeof crypto.randomUUID
      === 'function'
  ) {
    return crypto.randomUUID()
  }

  return (
    'resume-'
    + Date.now()
    + '-'
    + Math.random()
        .toString(36)
        .slice(2, 10)
  )
}


function buildResumeVersionLabel({
  versionName = '',
  jobDescription = '',
} = {}) {
  const normalizedName =
    normalizeText(
      versionName,
    )

  if (normalizedName) {
    return normalizedName
  }

  if (
    normalizeText(
      jobDescription,
    )
  ) {
    return 'Tailored Resume'
  }

  return 'General Resume'
}


function normalizeVersion({
  id,
  targetCareerId,
  targetCareerName,
  versionName,
  resumeFocus = 'balanced',
  jobDescription = '',
  contact = {},
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

  const normalizedJobDescription =
    normalizeText(
      jobDescription,
    )

  const normalizedVersionName =
    buildResumeVersionLabel({
      versionName,
      jobDescription:
        normalizedJobDescription,
    })

  return {
    id:
      normalizeText(
        id,
      )
      || createResumeVersionId(),
    target_career_id:
      careerId,
    target_career_name:
      careerName,
    version_name:
      normalizedVersionName,
    resume_focus:
      normalizeText(
        resumeFocus,
      )
      || 'balanced',
    job_description:
      normalizedJobDescription,
    contact:
      contact
      && typeof contact === 'object'
        ? contact
        : {},
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


function upsertResumeDraftVersion(
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
    loadResumeDraftLibrary(
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
    saveResumeDraftLibrary(
      user,
      library,
    )

  if (!saved) {
    return null
  }

  return version
}


function getResumeDraftVersion(
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
    loadResumeDraftLibrary(
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


function listResumeDraftVersions(
  user,
  targetCareerId = null,
) {
  const library =
    loadResumeDraftLibrary(
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


function setActiveResumeVersion(
  user,
  versionId,
) {
  const version =
    getResumeDraftVersion(
      user,
      versionId,
    )

  if (!version) {
    return false
  }

  const library =
    loadResumeDraftLibrary(
      user,
    )

  library.active_version_id =
    version.id

  return saveResumeDraftLibrary(
    user,
    library,
  )
}


function getActiveResumeVersion(
  user,
) {
  const library =
    loadResumeDraftLibrary(
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


function removeResumeDraftVersion(
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
    loadResumeDraftLibrary(
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

  return saveResumeDraftLibrary(
    user,
    library,
  )
}


function loadLegacyResumeDraft(
  user,
) {
  const storageKey =
    getLegacyResumeStorageKey(
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
      || typeof parsed
        !== 'object'
    ) {
      return null
    }

    return parsed
  }
  catch {
    return null
  }
}


function clearLegacyResumeDraft(
  user,
) {
  const storageKey =
    getLegacyResumeStorageKey(
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
  buildResumeVersionLabel,
  clearLegacyResumeDraft,
  createResumeVersionId,
  getActiveResumeVersion,
  getResumeDraftVersion,
  listResumeDraftVersions,
  loadLegacyResumeDraft,
  loadResumeDraftLibrary,
  removeResumeDraftVersion,
  setActiveResumeVersion,
  upsertResumeDraftVersion,
}
