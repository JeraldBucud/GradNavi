import {
  useEffect,
  useState,
} from 'react'

import {
  useLocation,
} from 'react-router'


import {
  COVER_LETTER_FOCUS_OPTIONS,
  COVER_LETTER_TONE_OPTIONS,
  generateCoverLetterDraft,
} from '../services/documentService'

import {
  loadDocumentCareerOptions,
} from '../services/documentCareerService'

import {
  buildCoverLetterVersionLabel,
  clearLegacyCoverLetterDraft,
  createCoverLetterVersionId,
  getActiveCoverLetterVersion,
  listCoverLetterDraftVersions,
  loadLegacyCoverLetterDraft,
  setActiveCoverLetterVersion,
  upsertCoverLetterDraftVersion,
} from '../services/coverLetterDraftLibraryService'

import {
  downloadCoverLetterDocx,
  downloadCoverLetterPdf,
} from '../services/documentExportService'

import {
  getCurrentUser,
  getStoredUser,
} from '../services/authService'

import {
  getStudentProfile,
} from '../services/profileService'

import HelpTip from '../components/HelpTip'

import './CoverLetterBuilderPage.css'


const COVER_LETTER_STORAGE_BASE_KEY =
  'gradnavi_cover_letter_builder_draft_v1'

const LEGACY_COVER_LETTER_STORAGE_KEY =
  'gradnavi_cover_letter_builder_draft_v1'


const EMPTY_JOB_CONTEXT = {
  jobTitle: '',
  company: '',
  jobDescription: '',
}


const RESUME_STORAGE_BASE_KEY =
  'gradnavi_resume_builder_draft_v1'


function getDraftStorageIdentity(user) {
  const identity =
    user?.id
    ?? user?.email

  if (
    identity === undefined
    || identity === null
    || String(identity).trim() === ''
  ) {
    return null
  }

  return encodeURIComponent(
    String(identity)
      .trim()
      .toLowerCase(),
  )
}


function getCoverLetterStorageKey(
  user,
) {
  const identity =
    getDraftStorageIdentity(
      user,
    )

  if (!identity) {
    return null
  }

  return (
    `${COVER_LETTER_STORAGE_BASE_KEY}:`
    + identity
  )
}


function getResumeStorageKey(user) {
  const identity =
    getDraftStorageIdentity(
      user,
    )

  if (!identity) {
    return null
  }

  return (
    `${RESUME_STORAGE_BASE_KEY}:`
    + identity
  )
}


const EMPTY_EXPORT_CONTACT = {
  fullName: '',
  email: '',
  phone: '',
  location: '',
  linkedin: '',
  portfolio: '',
}


function buildUserFullName(user) {
  return [
    user?.first_name,
    user?.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()
}


function getCoverLetterExportContact(
  user,
) {
  const fallback = {
    ...EMPTY_EXPORT_CONTACT,

    fullName:
      buildUserFullName(
        user,
      ),

    email:
      user?.email
      || '',
  }

  try {
    const storageKey =
      getResumeStorageKey(
        user,
      )

    if (!storageKey) {
      return fallback
    }

    const stored =
      localStorage.getItem(
        storageKey,
      )

    if (!stored) {
      return fallback
    }

    const parsed =
      JSON.parse(stored)

    const storedContact =
      parsed?.contact

    if (
      !storedContact
      || typeof storedContact
      !== 'object'
    ) {
      return fallback
    }

    const currentEmail =
      String(
        user?.email
        || '',
      )
        .trim()
        .toLowerCase()

    const storedEmail =
      String(
        storedContact.email
        || '',
      )
        .trim()
        .toLowerCase()

    if (
      currentEmail
      && storedEmail
      && currentEmail
      !== storedEmail
    ) {
      return fallback
    }

    return {
      ...fallback,
      ...storedContact,

      fullName:
        storedContact.fullName
        || fallback.fullName,

      email:
        storedContact.email
        || fallback.email,
    }
  }
  catch {
    return fallback
  }
}


function normaliseList(value) {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map((item) =>
      String(item).trim()
    )
    .filter(Boolean)
}


function normaliseDraft(value) {
  if (
    !value
    || typeof value !== 'object'
  ) {
    return null
  }

  return {
    opening:
      String(
        value.opening
        || '',
      ).trim(),

    body_paragraphs:
      normaliseList(
        value.body_paragraphs,
      ),

    closing:
      String(
        value.closing
        || '',
      ).trim(),

    matched_profile_facts:
      normaliseList(
        value.matched_profile_facts,
      ),

    missing_information:
      normaliseList(
        value.missing_information,
      ),

    limitations:
      normaliseList(
        value.limitations,
      ),

    is_draft: true,

    requires_user_review: true,
  }
}


function loadSavedDraft(user) {
  try {
    localStorage.removeItem(
      LEGACY_COVER_LETTER_STORAGE_KEY,
    )

    const storageKey =
      getCoverLetterStorageKey(
        user,
      )

    if (!storageKey) {
      return null
    }

    const stored =
      localStorage.getItem(
        storageKey,
      )

    if (!stored) {
      return null
    }

    const parsed =
      JSON.parse(stored)

    return {
      jobContext: {
        ...EMPTY_JOB_CONTEXT,
        ...(
          parsed.jobContext
          || {}
        ),
      },

      draft:
        normaliseDraft(
          parsed.draft,
        ),

      savedAt:
        parsed.savedAt
        || null,
    }
  }
  catch {
    return null
  }
}


function buildPlainText(draft) {
  if (!draft) {
    return ''
  }

  return [
    draft.opening,
    '',
    ...draft.body_paragraphs.flatMap(
      (paragraph) => [
        paragraph,
        '',
      ],
    ),
    draft.closing,
  ]
    .join('\n')
    .trim()
}


function getDocumentCareerOptionLabel(
  option,
) {
  const sources = []

  if (option?.from_career_goal) {
    sources.push(
      'Career Goal',
    )
  }

  if (option?.from_recommendation) {
    if (
      option.recommendation_rank
      !== null
      && option.recommendation_rank
      !== undefined
    ) {
      sources.push(
        `Recommendation #${option.recommendation_rank}`,
      )
    }
    else {
      sources.push(
        'Recommendation',
      )
    }
  }

  const sourceText =
    sources.join(
      ' + ',
    )

  if (!sourceText) {
    return (
      option?.career_name
      || 'Career'
    )
  }

  return (
    `${option.career_name} (${sourceText})`
  )
}


function CoverLetterBuilderPage() {
  const location = useLocation()

  const incomingJobDescription =
    typeof location.state?.jobDescription
    === 'string'
      ? location.state.jobDescription
        .trim()
        .slice(0, 20_000)
      : ''

  const [
    storedUser,
  ] = useState(
    () => getStoredUser(),
  )
  const [
    storedDraft,
  ] = useState(
    () => loadSavedDraft(
      storedUser,
    ),
  )

  const [
    currentUser,
    setCurrentUser,
  ] = useState(
    storedUser,
  )

  const [
    profile,
    setProfile,
  ] = useState(null)

  const [
    profileLoading,
    setProfileLoading,
  ] = useState(true)

  const [
    profileError,
    setProfileError,
  ] = useState('')

  const [
    jobContext,
    setJobContext,
  ] = useState(
    () => ({
      ...EMPTY_JOB_CONTEXT,
      ...(
        storedDraft?.jobContext
        || {}
      ),
      ...(
        incomingJobDescription
          ? {
            jobDescription:
              incomingJobDescription,
          }
          : {}
      ),
    }),
  )

  const [
    draft,
    setDraft,
  ] = useState(
    storedDraft?.draft
    || null,
  )

  const [
    generationState,
    setGenerationState,
  ] = useState(
    storedDraft?.draft
      ? 'success'
      : 'empty',
  )

  const [
    generationError,
    setGenerationError,
  ] = useState('')

  const [
    editingSection,
    setEditingSection,
  ] = useState(null)

  const [
    actionMessage,
    setActionMessage,
  ] = useState(
    incomingJobDescription
      ? (
        'Job description carried over '
        + 'from Job Matching. Add the '
        + 'job title and company to continue.'
      )
      : storedDraft?.draft
        ? (
          'Saved draft restored '
          + 'from this browser.'
        )
        : '',
  )

  const [
    savedAt,
    setSavedAt,
  ] = useState(
    storedDraft?.savedAt
    || null,
  )


  const [
    careerOptions,
    setCareerOptions,
  ] = useState([])

  const [
    careerOptionsLoading,
    setCareerOptionsLoading,
  ] = useState(true)

  const [
    careerOptionsError,
    setCareerOptionsError,
  ] = useState('')

  const [
    targetCareerId,
    setTargetCareerId,
  ] = useState('')

  const [
    tone,
    setTone,
  ] = useState('professional')

  const [
    coverLetterFocus,
    setCoverLetterFocus,
  ] = useState('balanced')

  const [
    versionName,
    setVersionName,
  ] = useState('')

  const [
    versionNameEdited,
    setVersionNameEdited,
  ] = useState(false)

  const [
    activeVersionId,
    setActiveVersionId,
  ] = useState(null)

  const [
    coverLetterVersions,
    setCoverLetterVersions,
  ] = useState([])

  const storageUser =
    currentUser
    || storedUser

  const selectedTargetCareer =
    careerOptions.find(
      (career) =>
        String(
          career.career_id,
        )
        === String(
          targetCareerId,
        ),
    )
    || null

  const selectedCareerVersions =
    coverLetterVersions.filter(
      (version) =>
        String(
          version.target_career_id,
        )
        === String(
          targetCareerId,
        ),
    )

  const automaticVersionName =
    buildCoverLetterVersionLabel({
      jobTitle:
        jobContext.jobTitle,
      company:
        jobContext.company,
    })

  const displayedVersionName =
    versionNameEdited
      ? versionName
      : automaticVersionName

  const isGenerationReady =
    Boolean(
      selectedTargetCareer
      && jobContext.jobTitle.trim()
      && jobContext.company.trim()
      && jobContext.jobDescription.trim()
    )


  useEffect(() => {
    let active = true

    async function loadCoverLetterTargets() {
      setCareerOptionsLoading(
        true,
      )

      setCareerOptionsError('')

      try {
        const result =
          await loadDocumentCareerOptions()

        if (!active) {
          return
        }

        const options =
          Array.isArray(
            result?.career_options,
          )
            ? result.career_options
            : []

        setCareerOptions(
          options,
        )

        const user =
          currentUser
          || storedUser

        let activeVersion =
          user
            ? getActiveCoverLetterVersion(
                user,
              )
            : null

        const activeCareerExists =
          activeVersion
          && options.some(
            (career) =>
              String(
                career.career_id,
              )
              === String(
                activeVersion
                  .target_career_id,
              ),
          )

        if (!activeCareerExists) {
          activeVersion = null
        }

        const primaryCareerOption =
          options.find(
            (career) =>
              career.is_primary,
          )
          || null

        const topRecommendationOption =
          options.find(
            (career) =>
              career.recommendation_rank
              === 1,
          )
          || null

        let defaultCareerId =
          activeVersion
            ?.target_career_id
          ?? primaryCareerOption
            ?.career_id
          ?? topRecommendationOption
            ?.career_id
          ?? options[0]
            ?.career_id
          ?? ''

        if (
          user
          && !activeVersion
          && defaultCareerId
        ) {
          const legacyDraft =
            loadLegacyCoverLetterDraft(
              user,
            )

          if (legacyDraft?.draft) {
            const targetCareer =
              options.find(
                (career) =>
                  String(
                    career.career_id,
                  )
                  === String(
                    defaultCareerId,
                  ),
              )

            const legacyContext =
              legacyDraft.jobContext
              || {}

            if (targetCareer) {
              activeVersion =
                upsertCoverLetterDraftVersion(
                  user,
                  {
                    targetCareerId:
                      targetCareer
                        .career_id,
                    targetCareerName:
                      targetCareer
                        .career_name,
                    versionName:
                      '',
                    tone:
                      'professional',
                    coverLetterFocus:
                      'balanced',
                    jobTitle:
                      legacyContext
                        .jobTitle
                      || '',
                    company:
                      legacyContext
                        .company
                      || '',
                    jobDescription:
                      legacyContext
                        .jobDescription
                      || '',
                    draft:
                      legacyDraft.draft,
                    savedAt:
                      legacyDraft
                        .savedAt
                      || null,
                  },
                )

              if (activeVersion) {
                clearLegacyCoverLetterDraft(
                  user,
                )

                defaultCareerId =
                  activeVersion
                    .target_career_id
              }
            }
          }
        }

        setTargetCareerId(
          defaultCareerId
            ? String(
                defaultCareerId,
              )
            : '',
        )

        if (user) {
          setCoverLetterVersions(
            listCoverLetterDraftVersions(
              user,
            ),
          )
        }
        else {
          setCoverLetterVersions([])
        }

        if (activeVersion) {
          if (incomingJobDescription) {
            setActiveVersionId(null)

            setTone('professional')

            setCoverLetterFocus(
              'balanced',
            )

            setVersionName('')
            setVersionNameEdited(false)

            setJobContext({
              jobTitle: '',
              company: '',
              jobDescription:
                incomingJobDescription,
            })

            setDraft(null)
            setSavedAt(null)

            setGenerationState(
              'empty',
            )

            setActionMessage(
              'Job description carried over '
              + 'from Job Matching. Add the '
              + 'job title and company to continue.',
            )
          }
          else {
            setActiveVersionId(
              activeVersion.id,
            )

            setTone(
              activeVersion.tone
              || 'professional',
            )

            setCoverLetterFocus(
              activeVersion
                .cover_letter_focus
              || 'balanced',
            )

            setVersionName(
              activeVersion
                .version_name
              || '',
            )

            setVersionNameEdited(
              true,
            )

            setJobContext({
              jobTitle:
                activeVersion
                  .job_title
                || '',
              company:
                activeVersion
                  .company
                || '',
              jobDescription:
                activeVersion
                  .job_description
                || '',
            })

            setDraft(
              activeVersion.draft
              || null,
            )

            setSavedAt(
              activeVersion.saved_at
              || null,
            )

            setGenerationState(
              activeVersion.draft
                ? 'success'
                : 'empty',
            )

            if (activeVersion.draft) {
              setActionMessage(
                'Saved cover letter version '
                + 'restored from this browser.',
              )
            }
          }
        }
      }
      catch (error) {
        if (!active) {
          return
        }

        setCareerOptionsError(
          error?.message
          || (
            'Cover letter career options '
            + 'failed to load.'
          ),
        )
      }
      finally {
        if (active) {
          setCareerOptionsLoading(
            false,
          )
        }
      }
    }

    loadCoverLetterTargets()

    return () => {
      active = false
    }
  }, [
    currentUser,
    incomingJobDescription,
    storedUser,
  ])


  useEffect(() => {
    let active = true

    async function loadContext() {
      setProfileLoading(true)
      setProfileError('')

      const [
        userResult,
        profileResult,
      ] = await Promise.allSettled([
        getCurrentUser(),
        getStudentProfile(),
      ])

      if (!active) {
        return
      }

      if (
        userResult.status
        === 'fulfilled'
      ) {
        setCurrentUser(
          userResult.value,
        )
      }

      if (
        profileResult.status
        === 'fulfilled'
      ) {
        setProfile(
          profileResult
            .value
            ?.data
            ?.profile
          || null,
        )
      }
      else {
        setProfileError(
          profileResult
            .reason
            ?.message
          || (
            'Student Profile '
            + 'could not be loaded.'
          ),
        )
      }

      setProfileLoading(false)
    }

    loadContext()

    return () => {
      active = false
    }
  }, [])


  const studentName =
    currentUser
      ?.first_name
      ?.trim()
    || 'Student'

  const studentInitial =
    studentName
      .charAt(0)
      .toUpperCase()


  const skills =
    profile?.skills
    || []

  const projects =
    profile?.projects
    || []

  const experience =
    profile?.experience
    || []

  const careerGoals =
    profile?.career_goals
    || []

  const primaryCareer =
    careerGoals.find(
      (goal) =>
        goal.is_primary,
    )
    || careerGoals[0]
    || null


  const matchedEvidence = [
    skills.length
      ? (
        'Skills: '
        + skills
          .slice(0, 4)
          .map(
            (skill) =>
              skill.name,
          )
          .join(', ')
      )
      : null,

    projects.length
      ? (
        'Projects: '
        + projects
          .slice(0, 2)
          .map(
            (project) =>
              project.name,
          )
          .join(', ')
      )
      : null,

    primaryCareer
      ? (
        'Career goal: '
        + primaryCareer.target_role
      )
      : null,
  ].filter(Boolean)


  const evidenceToImprove = [
    experience.length
      ? (
        'Review experience '
        + 'against the role'
      )
      : (
        'Add relevant work '
        + 'experience if available'
      ),

    projects.length
      ? (
        'Add measurable project '
        + 'outcomes where verified'
      )
      : (
        'Add relevant project '
        + 'evidence'
      ),

    'Confirm role-specific '
      + 'examples before use',
  ]


  function updateJobContext(
    field,
    value,
  ) {
    setJobContext(
      (current) => ({
        ...current,
        [field]: value,
      }),
    )

    setActionMessage('')

    if (
      generationState
      === 'validation'
    ) {
      setGenerationState(
        draft
          ? 'success'
          : 'empty',
      )
    }
  }


  function applyCoverLetterVersion(
    version,
  ) {
    if (!version) {
      return
    }

    setActiveVersionId(
      version.id,
    )

    setTargetCareerId(
      String(
        version.target_career_id,
      ),
    )

    setTone(
      version.tone
      || 'professional',
    )

    setCoverLetterFocus(
      version.cover_letter_focus
      || 'balanced',
    )

    setVersionName(
      version.version_name
      || '',
    )

    setVersionNameEdited(
      true,
    )

    setJobContext({
      jobTitle:
        version.job_title
        || '',
      company:
        version.company
        || '',
      jobDescription:
        version.job_description
        || '',
    })

    setDraft(
      version.draft
      || null,
    )

    setSavedAt(
      version.saved_at
      || null,
    )

    setGenerationState(
      version.draft
        ? 'success'
        : 'empty',
    )

    setGenerationError('')
    setEditingSection(null)

    setActionMessage(
      version.draft
        ? 'Saved cover letter version loaded.'
        : '',
    )
  }


  function resetCoverLetterVersionEditor() {
    setActiveVersionId(
      createCoverLetterVersionId(),
    )

    setTone(
      'professional',
    )

    setCoverLetterFocus(
      'balanced',
    )

    setVersionName('')
    setVersionNameEdited(false)

    setJobContext({
      ...EMPTY_JOB_CONTEXT,
    })

    setDraft(null)
    setSavedAt(null)
    setGenerationState('empty')
    setGenerationError('')
    setEditingSection(null)

    setActionMessage(
      'New cover letter version started.',
    )
  }


  function handleTargetCareerChange(
    event,
  ) {
    const nextCareerId =
      event.target.value

    setTargetCareerId(
      nextCareerId,
    )

    setGenerationError('')
    setEditingSection(null)

    if (!nextCareerId) {
      setActiveVersionId(null)
      setDraft(null)
      setSavedAt(null)
      setGenerationState('empty')
      setActionMessage('')
      return
    }

    const latestVersion =
      coverLetterVersions
        .filter(
          (version) =>
            String(
              version.target_career_id,
            )
            === String(
              nextCareerId,
            ),
        )
        .sort(
          (
            first,
            second,
          ) => (
            (
              Date.parse(
                second.saved_at,
              )
              || 0
            )
            - (
              Date.parse(
                first.saved_at,
              )
              || 0
            )
          ),
        )[0]

    if (latestVersion) {
      if (storageUser) {
        setActiveCoverLetterVersion(
          storageUser,
          latestVersion.id,
        )
      }

      applyCoverLetterVersion(
        latestVersion,
      )

      return
    }

    resetCoverLetterVersionEditor()

    setTargetCareerId(
      nextCareerId,
    )

    setActionMessage(
      'No saved cover letter exists '
      + 'for this career yet.',
    )
  }


  function handleSavedVersionChange(
    event,
  ) {
    const versionId =
      event.target.value

    if (!versionId) {
      return
    }

    const version =
      coverLetterVersions.find(
        (candidate) =>
          candidate.id
          === versionId,
      )

    if (!version) {
      return
    }

    if (storageUser) {
      setActiveCoverLetterVersion(
        storageUser,
        version.id,
      )
    }

    applyCoverLetterVersion(
      version,
    )
  }


  function handleNewCoverLetterVersion() {
    if (!selectedTargetCareer) {
      setActionMessage(
        'Select a target career '
        + 'before starting a new '
        + 'cover letter version.',
      )

      return
    }

    resetCoverLetterVersionEditor()
  }


  async function handleGenerate() {
    const jobTitle =
      jobContext.jobTitle.trim()

    const company =
      jobContext.company.trim()

    const jobDescription =
      jobContext.jobDescription.trim()

    if (
      !selectedTargetCareer
      || !jobTitle
      || !company
      || !jobDescription
    ) {
      setGenerationState(
        'validation',
      )

      setGenerationError(
        'Select a target career and '
        + 'add the job title, company, '
        + 'and job description before '
        + 'generating.',
      )

      return
    }

    setGenerationState(
      'generating',
    )

    setGenerationError('')
    setActionMessage('')
    setEditingSection(null)

    try {
      const response =
        await generateCoverLetterDraft({
          targetCareerId:
            selectedTargetCareer
              .career_id,
          tone,
          coverLetterFocus,
          jobTitle,
          company,
          jobDescription,
        })

      const generatedDraft =
        normaliseDraft(
          response
            ?.data
            ?.cover_letter_draft,
        )

      if (!generatedDraft) {
        throw new Error(
          'The generated cover letter '
          + 'response was invalid.',
        )
      }

      setDraft(
        generatedDraft,
      )

      if (!activeVersionId) {
        setActiveVersionId(
          createCoverLetterVersionId(),
        )
      }

      setGenerationState(
        'success',
      )

      setActionMessage(
        'Cover letter draft generated for '
        + jobTitle
        + ' at '
        + company
        + '. Review every claim before use.',
      )
    }
    catch (error) {
      setGenerationState(
        'error',
      )

      setGenerationError(
        error?.message
        || (
          'Cover letter draft '
          + 'was not created.'
        ),
      )
    }
  }

  function handleClearJobDescription() {
    setJobContext(
      (current) => ({
        ...current,
        jobDescription: '',
      }),
    )

    setGenerationState(
      draft
        ? 'success'
        : 'empty',
    )

    setGenerationError('')
    setActionMessage('')
  }


  function handleSaveDraft() {
    if (!draft) {
      return
    }

    if (!selectedTargetCareer) {
      setActionMessage(
        'Select a target career '
        + 'before saving this '
        + 'cover letter.',
      )

      return
    }

    const user =
      currentUser
      || storedUser

    if (!user) {
      setActionMessage(
        'Sign in before saving '
        + 'this draft.',
      )

      return
    }

    const timestamp =
      new Date()
        .toISOString()

    const versionId =
      activeVersionId
      || createCoverLetterVersionId()

    const savedVersion =
      upsertCoverLetterDraftVersion(
        user,
        {
          id:
            versionId,
          targetCareerId:
            selectedTargetCareer
              .career_id,
          targetCareerName:
            selectedTargetCareer
              .career_name,
          versionName:
            displayedVersionName,
          tone,
          coverLetterFocus,
          jobTitle:
            jobContext.jobTitle,
          company:
            jobContext.company,
          jobDescription:
            jobContext
              .jobDescription,
          draft,
          savedAt:
            timestamp,
        },
      )

    if (!savedVersion) {
      setActionMessage(
        'Cover letter version '
        + 'was not saved.',
      )

      return
    }

    setActiveVersionId(
      savedVersion.id,
    )

    setVersionName(
      savedVersion.version_name,
    )

    setVersionNameEdited(
      true,
    )

    setSavedAt(
      savedVersion.saved_at,
    )

    setCoverLetterVersions(
      listCoverLetterDraftVersions(
        user,
      ),
    )

    setActionMessage(
      'Cover letter version saved '
      + 'to this browser.',
    )
  }

  async function handleCopyContent() {
    if (!draft) {
      return
    }

    try {
      await navigator
        .clipboard
        .writeText(
          buildPlainText(
            draft,
          ),
        )

      setActionMessage(
        'Cover letter content copied.',
      )
    }
    catch {
      setActionMessage(
        'Copy failed. Select and '
        + 'copy the draft manually.',
      )
    }
  }


  async function handleDownloadWord() {
    if (!draft) {
      return
    }

    const exportContact =
      getCoverLetterExportContact(
        currentUser,
      )

    try {
      await downloadCoverLetterDocx(
        exportContact,
        jobContext,
        draft,
      )

      setActionMessage(
        'Word cover letter downloaded.',
      )
    }
    catch {
      setActionMessage(
        'Word download failed. '
        + 'Please try again.',
      )
    }
  }


  async function handleDownloadPdf() {
    if (!draft) {
      return
    }

    const exportContact =
      getCoverLetterExportContact(
        currentUser,
      )

    try {
      await downloadCoverLetterPdf(
        exportContact,
        jobContext,
        draft,
      )

      setActionMessage(
        'PDF cover letter downloaded.',
      )
    }
    catch {
      setActionMessage(
        'PDF download failed. '
        + 'Please try again.',
      )
    }
  }


  function handleReturnToContext() {
    document
      .getElementById(
        'cover-letter-job-context',
      )
      ?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
  }


  function isEditing(section) {
    return (
      editingSection === 'all'
      || editingSection === section
    )
  }


  function toggleEditing(section) {
    setEditingSection(
      (current) =>
        current === section
          ? null
          : section,
    )
  }


  function updateText(
    field,
    value,
  ) {
    setDraft(
      (current) => ({
        ...current,
        [field]: value,
      }),
    )

    setActionMessage('')
  }


  function updateParagraph(
    index,
    value,
  ) {
    setDraft(
      (current) => ({
        ...current,

        body_paragraphs:
          current
            .body_paragraphs
            .map(
              (
                paragraph,
                paragraphIndex,
              ) =>
                paragraphIndex
                === index
                  ? value
                  : paragraph,
            ),
      }),
    )

    setActionMessage('')
  }


  function renderTextSection(
    field,
    title,
  ) {
    const editing =
      isEditing(
        field,
      )

    return (
      <article
        className="cover-letter-builder__draft-section"
      >
        <div
          className="cover-letter-builder__draft-section-heading"
        >
          <h3>
            {title}
          </h3>

          <button
            className="cover-letter-builder__text-button"
            type="button"
            onClick={() =>
              toggleEditing(
                field,
              )
            }
          >
            {
              editing
                ? 'Done editing'
                : 'Edit section'
            }
          </button>
        </div>

        {
          editing
            ? (
              <textarea
                className="cover-letter-builder__draft-textarea"
                rows={6}
                value={
                  draft[field]
                }
                onChange={
                  (event) =>
                    updateText(
                      field,
                      event.target.value,
                    )
                }
              />
            )
            : (
              <p
                className="cover-letter-builder__draft-copy"
              >
                {
                  draft[field]
                  || 'No content yet.'
                }
              </p>
            )
        }
      </article>
    )
  }


  return (
    <main
      className="cover-letter-builder"
    >
      <div
        className="cover-letter-builder__content"
      >
        <header
          className="cover-letter-builder__header"
        >
          <div>
            <h1>
              Cover Letter Builder
            </h1>

            <p>
              Create a cover letter
              tailored to a specific role
              using your profile evidence
              and the job description.
            </p>
          </div>

          <div
            className="cover-letter-builder__account"
          >
            <span
              className="cover-letter-builder__avatar"
              aria-hidden="true"
            >
              {studentInitial}
            </span>

            <span>
              {studentName}
            </span>
          </div>
        </header>


        <details
          className="cover-letter-builder__guide"
        >
          <summary>
            How Cover Letter Builder works
          </summary>

          <div
            className="cover-letter-builder__intro-grid"
          >
            <article>
              <h2>
                Start with the role
              </h2>

              <ul>
                <li>
                  Add the job title
                  for your review
                </li>

                <li>
                  Add the company
                  for your review
                </li>

                <li>
                  Paste the job description
                  to tailor your letter
                </li>
              </ul>
            </article>

            <article>
              <h2>
                GradNavi matches evidence
              </h2>

              <ul>
                <li>
                  Skills and projects
                  from your profile
                </li>

                <li>
                  Career goal context
                </li>

                <li>
                  Missing facts stay visible
                </li>
              </ul>
            </article>

            <article>
              <h2>
                Review before use
              </h2>

              <ul>
                <li>
                  Check company names
                </li>

                <li>
                  Edit tone and details
                </li>

                <li>
                  Confirm every claim is true
                </li>
              </ul>
            </article>
          </div>
        </details>


        <section
          id="cover-letter-job-context"
          className="cover-letter-builder__section"
        >
          <div
            className="cover-letter-builder__section-heading"
          >
            <div>
              <h2>
                Cover Letter Target
              </h2>

              <p>
                Choose the career and job you are applying for. Add the job title, company, and job description to create a tailored cover letter.
              </p>
            </div>

            <span
              className="document-help-heading"
            >
              <span
                className="cover-letter-builder__ai-badge"
              >
                ATS-friendly
              </span>

              <HelpTip
                  label="What does ATS-friendly mean?"
                  title="ATS-friendly"
                  text="Many employers use applicant tracking systems to scan applications. GradNavi keeps your document clear, structured, and focused on relevant job terms so these systems read the document more easily. Review the final document before applying."
                />
            </span>
          </div>

          <div
            className="cover-letter-builder__application-grid"
          >
            <label>
              <span
                className="document-help-heading"
              >
                Target Career

                <HelpTip
                  label="Help with Target Career"
                  title="Target Career"
                  text="Choose the career you want this document to focus on. Career Goal means a role you selected in your Student Profile. Recommendation means a career GradNavi matched to your profile."
                />
              </span>

              <select
                value={
                  targetCareerId
                }
                disabled={
                  careerOptionsLoading
                }
                onChange={
                  handleTargetCareerChange
                }
              >
                <option value="">
                  {
                    careerOptionsLoading
                      ? 'Loading careers...'
                      : 'Select a career'
                  }
                </option>

                {
                  careerOptions.map(
                    (career) => (
                      <option
                        key={
                          career.career_id
                        }
                        value={
                          career.career_id
                        }
                      >
                        {
                          getDocumentCareerOptionLabel(
                            career,
                          )
                        }
                      </option>
                    ),
                  )
                }
              </select>

              <small>
                Includes your Career Goals
                and current GradNavi
                recommendations.
              </small>
            </label>

            <label>
              <span>
                Tone
              </span>

              <select
                value={tone}
                onChange={
                  (event) => {
                    setTone(
                      event.target.value,
                    )

                    setActionMessage('')
                  }
                }
              >
                {
                  COVER_LETTER_TONE_OPTIONS
                    .map(
                      (option) => (
                        <option
                          key={
                            option.value
                          }
                          value={
                            option.value
                          }
                        >
                          {option.label}
                        </option>
                      ),
                    )
                }
              </select>

              <small>
                Controls the writing style
                of the generated letter.
              </small>
            </label>

            <label>
              <span
                className="document-help-heading"
              >
                Cover Letter Focus

                <HelpTip
                  label="Help with Cover Letter Focus"
                  title="Cover Letter Focus"
                  text="Choose what your cover letter should emphasise, such as matching skills, experience, projects, or a career transition."
                />
              </span>

              <select
                value={
                  coverLetterFocus
                }
                onChange={
                  (event) => {
                    setCoverLetterFocus(
                      event.target.value,
                    )

                    setActionMessage('')
                  }
                }
              >
                {
                  COVER_LETTER_FOCUS_OPTIONS
                    .map(
                      (option) => (
                        <option
                          key={
                            option.value
                          }
                          value={
                            option.value
                          }
                        >
                          {option.label}
                        </option>
                      ),
                    )
                }
              </select>

              <small>
                Choose which evidence the
                letter should emphasise.
              </small>
            </label>

            <label>
              <span>
                Version Name
              </span>

              <input
                type="text"
                value={
                  displayedVersionName
                }
                placeholder={
                  'Cover Letter - Role at Company'
                }
                onChange={
                  (event) => {
                    const nextValue =
                      event.target.value

                    setVersionName(
                      nextValue,
                    )

                    setVersionNameEdited(
                      Boolean(
                        nextValue.trim(),
                      ),
                    )

                    setActionMessage('')
                  }
                }
              />

              <small>
                The name updates automatically from the job title and company. You may rename it anytime.
              </small>
            </label>

            <label>
              <span>
                Job Title
                {' '}
                <em>
                  Required
                </em>
              </span>

              <input
                type="text"
                value={
                  jobContext.jobTitle
                }
                placeholder={
                  'Software Engineer'
                }
                onChange={
                  (event) =>
                    updateJobContext(
                      'jobTitle',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                Company
                {' '}
                <em>
                  Required
                </em>
              </span>

              <input
                type="text"
                value={
                  jobContext.company
                }
                placeholder={
                  'Atlassian'
                }
                onChange={
                  (event) =>
                    updateJobContext(
                      'company',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                Saved Version
              </span>

              <select
                value={
                  activeVersionId
                  || ''
                }
                disabled={
                  !selectedCareerVersions
                    .length
                }
                onChange={
                  handleSavedVersionChange
                }
              >
                <option value="">
                  {
                    selectedCareerVersions
                      .length
                      ? 'Select a saved version'
                      : 'No saved versions'
                  }
                </option>

                {
                  selectedCareerVersions.map(
                    (version) => (
                      <option
                        key={
                          version.id
                        }
                        value={
                          version.id
                        }
                      >
                        {
                          version.version_name
                        }
                      </option>
                    ),
                  )
                }
              </select>

              <small>
                Saved applications stay
                separate for each career.
              </small>
            </label>

            <label
              className="cover-letter-builder__application-full"
            >
              <span>
                Job Description
                {' '}
                <em>
                  Required
                </em>
              </span>

              <textarea
                rows={10}
                value={
                  jobContext.jobDescription
                }
                placeholder={
                  'Paste the full job '
                  + 'description here.'
                }
                onChange={
                  (event) =>
                    updateJobContext(
                      'jobDescription',
                      event.target.value,
                    )
                }
              />

              <small>
                GradNavi uses the job description and information from your profile to tailor your cover letter.
              </small>
            </label>
          </div>

          {
            careerOptionsError
              ? (
                <div
                  className="cover-letter-builder__state-inline cover-letter-builder__state-inline--error"
                  role="alert"
                >
                  {careerOptionsError}
                </div>
              )
              : null
          }

          <p
            className="cover-letter-builder__field-note"
          >
            GradNavi uses these details to tailor your cover letter. Your version name helps you organise saved drafts.

            <HelpTip
                  label="How GradNavi uses your information"
                  title="Privacy"
                  text="GradNavi uses the information needed to prepare your document. Personal contact details are kept out of the writing request and are added only to the final document."
                />
          </p>

          <div
            className="cover-letter-builder__button-row"
          >
            <button
              className="cover-letter-builder__primary-button"
              type="button"
              disabled={
                generationState
                === 'generating'
                || !isGenerationReady
              }
              onClick={
                handleGenerate
              }
            >
              {
                generationState
                === 'generating'
                  ? 'Generating Cover Letter...'
                  : 'Generate Cover Letter'
              }
            </button>

            <button
              className="cover-letter-builder__secondary-button"
              type="button"
              disabled={
                !selectedTargetCareer
              }
              onClick={
                handleNewCoverLetterVersion
              }
            >
              New Cover Letter Version
            </button>

            <button
              className="cover-letter-builder__secondary-button"
              type="button"
              onClick={
                handleClearJobDescription
              }
            >
              Clear Job Description
            </button>
          </div>
        </section>


        <section
          className="cover-letter-builder__section"
        >
          <div
            className="cover-letter-builder__section-heading"
          >
            <div>
              <h2
                className="document-help-heading"
              >
                Profile Evidence

                <HelpTip
                  label="Help with Profile Evidence"
                  title="Profile Evidence"
                  text="These details come from your Student Profile, including skills, projects, experience, education, and career goals. Review them before generating your document."
                />
              </h2>

              <p>
                GradNavi uses approved
                Student Profile evidence
                to support the letter.
              </p>
            </div>
          </div>

          {
            profileLoading
              ? (
                <div
                  className="cover-letter-builder__inline-state"
                >
                  Loading profile evidence...
                </div>
              )
              : null
          }

          {
            profileError
              ? (
                <div
                  className="cover-letter-builder__notice cover-letter-builder__notice--error"
                >
                  {profileError}
                </div>
              )
              : null
          }

          {
            !profileLoading
              ? (
                <div
                  className="cover-letter-builder__evidence-grid"
                >
                  <article>
                    <h3>
                      Matched evidence
                    </h3>

                    {
                      matchedEvidence.length
                        ? (
                          <ul>
                            {
                              matchedEvidence.map(
                                (item) => (
                                  <li
                                    key={item}
                                  >
                                    {item}
                                  </li>
                                ),
                              )
                            }
                          </ul>
                        )
                        : (
                          <p>
                            Add more profile
                            evidence before
                            relying on the draft.
                          </p>
                        )
                    }
                  </article>

                  <article>
                    <h3>
                      May need more evidence
                    </h3>

                    <ul>
                      {
                        evidenceToImprove.map(
                          (item) => (
                            <li
                              key={item}
                            >
                              {item}
                            </li>
                          ),
                        )
                      }
                    </ul>
                  </article>

                  <article>
                    <h3>
                      Not included
                    </h3>

                    <ul>
                      <li>
                        Email, account role,
                        and internal IDs
                      </li>

                      <li>
                        Personality responses
                      </li>

                      <li>
                        Private project links
                      </li>
                    </ul>
                  </article>
                </div>
              )
              : null
          }
        </section>


        {
          generationState
          === 'empty'
            ? (
              <section
                className="cover-letter-builder__state-card"
              >
                <h2>
                  No cover letter draft yet
                </h2>

                <p>
                  Complete the application
                  target details, then
                  generate when the vacancy
                  context is ready.
                </p>
              </section>
            )
            : null
        }


        {
          generationState
          === 'validation'
            ? (
              <section
                className="cover-letter-builder__state-card cover-letter-builder__state-card--warning"
                role="alert"
              >
                <h2>
                  Complete application details
                  before generating
                </h2>

                <p>
                  {generationError}
                </p>
              </section>
            )
            : null
        }


        {
          generationState
          === 'generating'
            ? (
              <section
                className="cover-letter-builder__state-card"
                aria-live="polite"
              >
                <div
                  className="cover-letter-builder__spinner"
                  aria-hidden="true"
                />

                <h2>
                  Preparing your cover letter
                </h2>

                <p>
                  GradNavi is matching
                  verified profile evidence
                  against the supplied
                  job description.
                </p>
              </section>
            )
            : null
        }


        {
          generationState
          === 'error'
            ? (
              <section
                className="cover-letter-builder__state-card cover-letter-builder__state-card--error"
                role="alert"
              >
                <h2>
                  Cover letter could
                  not be created
                </h2>

                <p>
                  {generationError}
                </p>

                <div
                  className="cover-letter-builder__button-row"
                >
                  <button
                    className="cover-letter-builder__primary-button"
                    type="button"
                    onClick={
                      handleGenerate
                    }
                  >
                    Try Again
                  </button>

                  <button
                    className="cover-letter-builder__secondary-button"
                    type="button"
                    onClick={
                      handleReturnToContext
                    }
                  >
                    Review Job Context
                  </button>
                </div>
              </section>
            )
            : null
        }


        {
          draft
          && generationState
          === 'success'
            ? (
              <section
                className="cover-letter-builder__section cover-letter-builder__draft"
              >
                <div
                  className="cover-letter-builder__draft-heading"
                >
                  <div>
                    <h2>
                      Your Cover Letter Draft
                    </h2>

                    <p>
                      Review the letter
                      section by section,
                      edit the wording,
                      and confirm the details
                      before using it.
                    </p>
                  </div>
                </div>

                <div
                  className="cover-letter-builder__draft-toolbar"
                >
                  <div>
                    <span
                      className="cover-letter-builder__ai-badge"
                    >
                      AI-generated draft
                    </span>

                    <p>
                      Review names, facts,
                      experience details,
                      and tone before use.
                    </p>
                  </div>

                  <div
                    className="cover-letter-builder__draft-actions"
                  >
                    <button
                      className="cover-letter-builder__primary-button"
                      type="button"
                      onClick={() =>
                        setEditingSection(
                          editingSection
                          === 'all'
                            ? null
                            : 'all',
                        )
                      }
                    >
                      {
                        editingSection
                        === 'all'
                          ? 'Done Editing'
                          : 'Edit Draft'
                      }
                    </button>

                    <button
                      className="cover-letter-builder__secondary-button"
                      type="button"
                      onClick={
                        handleGenerate
                      }
                    >
                      Regenerate
                    </button>
                  </div>
                </div>


                <div
                  className="cover-letter-builder__draft-layout"
                >
                  <div
                    className="cover-letter-builder__draft-main"
                  >
                    {
                      renderTextSection(
                        'opening',
                        'Opening',
                      )
                    }

                    {
                      draft
                        .body_paragraphs
                        .map(
                          (
                            paragraph,
                            index,
                          ) => {
                            const section =
                              `body-${index}`

                            const editing =
                              isEditing(
                                section,
                              )

                            return (
                              <article
                                className="cover-letter-builder__draft-section"
                                key={section}
                              >
                                <div
                                  className="cover-letter-builder__draft-section-heading"
                                >
                                  <h3>
                                    Body paragraph
                                    {' '}
                                    {index + 1}
                                  </h3>

                                  <button
                                    className="cover-letter-builder__text-button"
                                    type="button"
                                    onClick={() =>
                                      toggleEditing(
                                        section,
                                      )
                                    }
                                  >
                                    {
                                      editing
                                        ? 'Done editing'
                                        : 'Edit section'
                                    }
                                  </button>
                                </div>

                                {
                                  editing
                                    ? (
                                      <textarea
                                        className="cover-letter-builder__draft-textarea"
                                        rows={7}
                                        value={
                                          paragraph
                                        }
                                        onChange={
                                          (event) =>
                                            updateParagraph(
                                              index,
                                              event.target.value,
                                            )
                                        }
                                      />
                                    )
                                    : (
                                      <p
                                        className="cover-letter-builder__draft-copy"
                                      >
                                        {paragraph}
                                      </p>
                                    )
                                }
                              </article>
                            )
                          },
                        )
                    }

                    {
                      renderTextSection(
                        'closing',
                        'Closing',
                      )
                    }
                  </div>


                  <aside
                    className="cover-letter-builder__draft-sidebar"
                  >
                    <article
                      className="cover-letter-builder__review-panel"
                    >
                      <h3>
                        Matched profile facts
                      </h3>

                      {
                        draft
                          .matched_profile_facts
                          .length
                          ? (
                            <ul>
                              {
                                draft
                                  .matched_profile_facts
                                  .map(
                                    (
                                      item,
                                      index,
                                    ) => (
                                      <li
                                        key={
                                          `fact-${index}`
                                        }
                                      >
                                        <span
                                          className="cover-letter-builder__dot cover-letter-builder__dot--safe"
                                          aria-hidden="true"
                                        />

                                        <span>
                                          {item}
                                        </span>
                                      </li>
                                    ),
                                  )
                              }
                            </ul>
                          )
                          : (
                            <p>
                              No matched
                              profile facts
                              were returned.
                            </p>
                          )
                      }
                    </article>


                    <article
                      className="cover-letter-builder__review-panel"
                    >
                      <h3>
                        Review carefully
                      </h3>

                      <ul>
                        <li>
                          <span
                            className="cover-letter-builder__dot cover-letter-builder__dot--warning"
                            aria-hidden="true"
                          />

                          <span>
                            Company name
                          </span>
                        </li>

                        <li>
                          <span
                            className="cover-letter-builder__dot cover-letter-builder__dot--warning"
                            aria-hidden="true"
                          />

                          <span>
                            Role requirements
                          </span>
                        </li>

                        <li>
                          <span
                            className="cover-letter-builder__dot cover-letter-builder__dot--warning"
                            aria-hidden="true"
                          />

                          <span>
                            Unsupported claims
                          </span>
                        </li>
                      </ul>
                    </article>


                    <article
                      className="cover-letter-builder__review-panel"
                    >
                      <h3>
                        Missing information
                      </h3>

                      {
                        draft
                          .missing_information
                          .length
                          ? (
                            <ul>
                              {
                                draft
                                  .missing_information
                                  .map(
                                    (
                                      item,
                                      index,
                                    ) => (
                                      <li
                                        key={
                                          `missing-${index}`
                                        }
                                      >
                                        <span
                                          className="cover-letter-builder__dot cover-letter-builder__dot--warning"
                                          aria-hidden="true"
                                        />

                                        <span>
                                          {item}
                                        </span>
                                      </li>
                                    ),
                                  )
                              }
                            </ul>
                          )
                          : (
                            <p>
                              No missing
                              information
                              was reported.
                            </p>
                          )
                      }
                    </article>
                  </aside>
                </div>


                <div
                  className="cover-letter-builder__final-actions"
                >
                  <button
                    className="cover-letter-builder__primary-button"
                    type="button"
                    onClick={
                      handleSaveDraft
                    }
                  >
                    Save Draft
                  </button>

                  <button
                    className="cover-letter-builder__secondary-button"
                    type="button"
                    onClick={
                      handleDownloadWord
                    }
                  >
                    Download Word
                  </button>

                  <button
                    className="cover-letter-builder__secondary-button"
                    type="button"
                    onClick={
                      handleDownloadPdf
                    }
                  >
                    Download PDF
                  </button>

                  <button
                    className="cover-letter-builder__secondary-button"
                    type="button"
                    onClick={
                      handleCopyContent
                    }
                  >
                    Copy Content
                  </button>

                  <button
                    className="cover-letter-builder__secondary-button"
                    type="button"
                    onClick={
                      handleReturnToContext
                    }
                  >
                    Return to Job Context
                  </button>
                </div>

                {
                  actionMessage
                    ? (
                      <p
                        className="cover-letter-builder__action-message"
                        aria-live="polite"
                      >
                        {actionMessage}

                        {
                          savedAt
                            ? (
                              <>
                                {' '}
                                Last saved:
                                {' '}
                                {
                                  new Date(
                                    savedAt,
                                  )
                                    .toLocaleString()
                                }
                              </>
                            )
                            : null
                        }
                      </p>
                    )
                    : null
                }
              </section>
            )
            : null
        }
      </div>
    </main>
  )
}


export default CoverLetterBuilderPage
