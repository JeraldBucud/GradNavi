import {
  useEffect,
  useState,
} from 'react'

import {
  useLocation,
  useNavigate,
} from 'react-router'

import {
  RESUME_FOCUS_OPTIONS,
  generateResumeDraft,
} from '../services/documentService'

import {
  loadDocumentCareerOptions,
} from '../services/documentCareerService'

import {
  clearLegacyResumeDraft,
  createResumeVersionId,
  getActiveResumeVersion,
  listResumeDraftVersions,
  loadLegacyResumeDraft,
  setActiveResumeVersion,
  upsertResumeDraftVersion,
} from '../services/resumeDraftLibraryService'

import {
  downloadResumeDocx,
  downloadResumePdf,
} from '../services/documentExportService'

import {
  getCurrentUser,
  getStoredUser,
} from '../services/authService'

import {
  getStudentProfile,
} from '../services/profileService'

import HelpTip from '../components/HelpTip'

import './ResumeBuilderPage.css'


const RESUME_STORAGE_BASE_KEY =
  'gradnavi_resume_builder_draft_v1'

const LEGACY_RESUME_STORAGE_KEY =
  'gradnavi_resume_builder_draft_v1'


function getResumeStorageKey(user) {
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

  const scopedIdentity =
    encodeURIComponent(
      String(identity)
        .trim()
        .toLowerCase(),
    )

  return (
    `${RESUME_STORAGE_BASE_KEY}:`
    + scopedIdentity
  )
}


const EMPTY_CONTACT_DETAILS = {
  fullName: '',
  email: '',
  phone: '',
  location: '',
  linkedin: '',
  portfolio: '',
}


function buildFullName(user) {
  return [
    user?.first_name,
    user?.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()
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


function normaliseResumeDraft(value) {
  if (
    !value
    || typeof value !== 'object'
  ) {
    return null
  }

  return {
    professional_summary:
      String(
        value.professional_summary
        || '',
      ).trim(),

    skills:
      normaliseList(
        value.skills,
      ),

    education:
      normaliseList(
        value.education,
      ),

    experience:
      normaliseList(
        value.experience,
      ),

    projects:
      normaliseList(
        value.projects,
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


function listFromTextarea(value) {
  return value
    .split('\n')
    .map((item) =>
      item.trim()
    )
    .filter(Boolean)
}


function loadLocalDraft(user) {
  try {
    localStorage.removeItem(
      LEGACY_RESUME_STORAGE_KEY,
    )

    const storageKey =
      getResumeStorageKey(
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
      contact: {
        ...EMPTY_CONTACT_DETAILS,
        ...(
          parsed.contact
          || {}
        ),
      },

      draft:
        normaliseResumeDraft(
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


function buildResumePlainText(
  contact,
  draft,
) {
  if (!draft) {
    return ''
  }

  const lines = []

  if (contact.fullName.trim()) {
    lines.push(
      contact.fullName.trim(),
    )
  }

  const contactLine = [
    contact.email,
    contact.phone,
    contact.location,
    contact.linkedin,
    contact.portfolio,
  ]
    .map((item) =>
      item.trim()
    )
    .filter(Boolean)
    .join(' | ')

  if (contactLine) {
    lines.push(
      contactLine,
    )
  }

  if (lines.length) {
    lines.push('')
  }

  lines.push(
    'PROFESSIONAL SUMMARY',
    draft.professional_summary,
    '',
    'SKILLS',
    draft.skills.join(', '),
    '',
    'EXPERIENCE',
    ...draft.experience,
    '',
    'EDUCATION',
    ...draft.education,
    '',
    'PROJECTS',
    ...draft.projects,
  )

  return lines
    .join('\n')
    .trim()
}


function getCareerOptionLabel(
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


function ResumeBuilderPage() {
  const navigate = useNavigate()
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
    () => loadLocalDraft(
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
    contact,
    setContact,
  ] = useState(() => ({
    ...EMPTY_CONTACT_DETAILS,

    fullName:
      buildFullName(
        storedUser,
      ),

    email:
      storedUser?.email
      || '',

    ...(
      storedDraft?.contact
      || {}
    ),
  }))

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
        + 'from Job Matching.'
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
    resumeFocus,
    setResumeFocus,
  ] = useState('balanced')

  const [
    jobDescription,
    setJobDescription,
  ] = useState(
    incomingJobDescription,
  )

  const [
    versionName,
    setVersionName,
  ] = useState('General Resume')

  const [
    activeVersionId,
    setActiveVersionId,
  ] = useState(null)

  const [
    resumeVersions,
    setResumeVersions,
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
    resumeVersions.filter(
      (version) =>
        String(
          version.target_career_id,
        )
        === String(
          targetCareerId,
        ),
    )

  const selectedResumeFocusLabel =
    RESUME_FOCUS_OPTIONS.find(
      (option) =>
        option.value
        === resumeFocus,
    )?.label
    || 'Balanced'


  useEffect(() => {
    let active = true

    async function loadPageContext() {
      setProfileLoading(true)
      setProfileError('')

      try {
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
          const user =
            userResult.value

          setCurrentUser(
            user,
          )

          setContact(
            (current) => ({
              ...current,

              fullName:
                current.fullName
                || buildFullName(
                  user,
                ),

              email:
                current.email
                || user?.email
                || '',
            }),
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
      }
      finally {
        if (active) {
          setProfileLoading(false)
        }
      }
    }

    loadPageContext()

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true

    async function loadResumeTargets() {
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
            ? getActiveResumeVersion(
                user,
              )
            : null

        const activeVersionCareerExists =
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

        if (!activeVersionCareerExists) {
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
            loadLegacyResumeDraft(
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

            if (targetCareer) {
              activeVersion =
                upsertResumeDraftVersion(
                  user,
                  {
                    targetCareerId:
                      targetCareer
                        .career_id,
                    targetCareerName:
                      targetCareer
                        .career_name,
                    versionName:
                      'General Resume',
                    resumeFocus:
                      'balanced',
                    jobDescription:
                      '',
                    contact:
                      legacyDraft
                        .contact
                      || {},
                    draft:
                      legacyDraft
                        .draft,
                    savedAt:
                      legacyDraft
                        .savedAt
                      || null,
                  },
                )

              if (activeVersion) {
                clearLegacyResumeDraft(
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
          setResumeVersions(
            listResumeDraftVersions(
              user,
            ),
          )
        }
        else {
          setResumeVersions([])
        }

        if (activeVersion) {
          if (incomingJobDescription) {
            setActiveVersionId(null)

            setVersionName(
              'Job-tailored Resume',
            )

            setResumeFocus('balanced')

            setJobDescription(
              incomingJobDescription,
            )

            setContact(
              (current) => ({
                ...current,
                ...(
                  activeVersion
                    .contact
                  || {}
                ),
              }),
            )

            setDraft(null)
            setSavedAt(null)

            setGenerationState(
              'empty',
            )

            setActionMessage(
              'Job description carried over '
              + 'from Job Matching. Generate '
              + 'a new draft before saving.',
            )
          }
          else {
            setActiveVersionId(
              activeVersion.id,
            )

            setVersionName(
              activeVersion
                .version_name
              || 'General Resume',
            )

            setResumeFocus(
              activeVersion
                .resume_focus
              || 'balanced',
            )

            setJobDescription(
              activeVersion
                .job_description
              || '',
            )

            setContact(
              (current) => ({
                ...current,
                ...(
                  activeVersion
                    .contact
                  || {}
                ),
              }),
            )

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
                'Saved resume version '
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
            'Resume career options '
            + 'could not be loaded.'
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

    loadResumeTargets()

    return () => {
      active = false
    }
  }, [
    currentUser,
    incomingJobDescription,
    storedUser,
  ])



  const studentName =
    currentUser
      ?.first_name
      ?.trim()
    || 'Student'

  const studentInitial =
    studentName
      .charAt(0)
      .toUpperCase()


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

  const targetCareer =
    primaryCareer
      ?.target_role
    || 'No target career selected'


  const skills =
    profile?.skills
    || []

  const education =
    profile?.education
    || []

  const experience =
    profile?.experience
    || []

  const projects =
    profile?.projects
    || []


  const includedEvidence = [
    skills.length
      ? (
        'Skills: '
        + skills
          .slice(0, 5)
          .map(
            (skill) =>
              skill.name,
          )
          .join(', ')
      )
      : null,

    education.length
      ? (
        'Education: '
        + education[0]
          .qualification
      )
      : null,

    projects.length
      ? (
        'Projects: '
        + projects
          .slice(0, 3)
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
        + targetCareer
      )
      : null,
  ].filter(Boolean)


  const improvementItems = [
    projects.length
      ? (
        'Add measurable project '
        + 'outcomes where available'
      )
      : (
        'Add project evidence '
        + 'where available'
      ),

    experience.length
      ? (
        'Review experience '
        + 'descriptions for evidence'
      )
      : (
        'Add work experience '
        + 'if available'
      ),

    education.length
      ? (
        'Check dates and '
        + 'qualification names'
      )
      : (
        'Add education details'
      ),

    'Remove unsupported claims',
  ]


  const readyItems = [
    skills.length
      ? 'Skills are available'
      : null,

    education.length
      ? 'Education is available'
      : null,

    projects.length
      ? (
        'Project evidence '
        + 'supports examples'
      )
      : null,

    primaryCareer
      ? (
        'Career goal gives '
        + 'the resume direction'
      )
      : null,
  ].filter(Boolean)


  function updateContact(
    field,
    value,
  ) {
    setContact(
      (current) => ({
        ...current,
        [field]: value,
      }),
    )

    setActionMessage('')
  }


  function updateDraftText(
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


  function updateDraftList(
    field,
    value,
  ) {
    setDraft(
      (current) => ({
        ...current,

        [field]:
          listFromTextarea(
            value,
          ),
      }),
    )

    setActionMessage('')
  }


  function applyResumeVersion(
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

    setVersionName(
      version.version_name
      || 'General Resume',
    )

    setResumeFocus(
      version.resume_focus
      || 'balanced',
    )

    setJobDescription(
      version.job_description
      || '',
    )

    setContact(
      (current) => ({
        ...current,
        ...(
          version.contact
          || {}
        ),
      }),
    )

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
        ? (
            'Saved resume version '
            + 'loaded.'
          )
        : '',
    )
  }


  function resetResumeVersionEditor() {
    setActiveVersionId(
      createResumeVersionId(),
    )

    setVersionName(
      'General Resume',
    )

    setResumeFocus(
      'balanced',
    )

    setJobDescription('')
    setDraft(null)
    setSavedAt(null)
    setGenerationState('empty')
    setGenerationError('')
    setEditingSection(null)

    setActionMessage(
      'New resume version started.',
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
      resumeVersions
        .filter(
          (version) =>
            String(
              version
                .target_career_id,
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
        setActiveResumeVersion(
          storageUser,
          latestVersion.id,
        )
      }

      applyResumeVersion(
        latestVersion,
      )

      return
    }

    setActiveVersionId(
      createResumeVersionId(),
    )

    setVersionName(
      'General Resume',
    )

    setResumeFocus(
      'balanced',
    )

    setJobDescription('')
    setDraft(null)
    setSavedAt(null)
    setGenerationState('empty')

    setActionMessage(
      'No saved resume exists '
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
      resumeVersions.find(
        (candidate) =>
          candidate.id
          === versionId,
      )

    if (!version) {
      return
    }

    if (storageUser) {
      setActiveResumeVersion(
        storageUser,
        version.id,
      )
    }

    applyResumeVersion(
      version,
    )
  }


  function handleNewResumeVersion() {
    if (!selectedTargetCareer) {
      setActionMessage(
        'Select a target career '
        + 'before starting a '
        + 'new resume version.',
      )

      return
    }

    resetResumeVersionEditor()
  }


  async function handleGenerate() {
    if (!selectedTargetCareer) {
      setGenerationState(
        'error',
      )

      setGenerationError(
        'Select a target career '
        + 'before generating '
        + 'a resume.',
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
        await generateResumeDraft({
          targetCareerId:
            selectedTargetCareer
              .career_id,
          resumeFocus,
          jobDescription,
        })

      const generatedDraft =
        normaliseResumeDraft(
          response
            ?.data
            ?.resume_draft,
        )

      if (!generatedDraft) {
        throw new Error(
          'The generated resume '
          + 'response was invalid.',
        )
      }

      setDraft(
        generatedDraft,
      )

      if (!activeVersionId) {
        setActiveVersionId(
          createResumeVersionId(),
        )
      }

      setGenerationState(
        'success',
      )

      setActionMessage(
        'Resume draft generated for '
        + selectedTargetCareer
            .career_name
        + '. Review every section '
        + 'before use.',
      )
    }
    catch (error) {
      setGenerationState(
        'error',
      )

      setGenerationError(
        error?.message
        || (
          'Resume draft could '
          + 'not be created.'
        ),
      )
    }
  }

  function handleSaveDraft() {
    if (!draft) {
      return
    }

    if (!selectedTargetCareer) {
      setActionMessage(
        'Select a target career '
        + 'before saving '
        + 'this resume.',
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
      || createResumeVersionId()

    const savedVersion =
      upsertResumeDraftVersion(
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
          versionName,
          resumeFocus,
          jobDescription,
          contact,
          draft,
          savedAt:
            timestamp,
        },
      )

    if (!savedVersion) {
      setActionMessage(
        'Resume version could '
        + 'not be saved.',
      )

      return
    }

    setActiveVersionId(
      savedVersion.id,
    )

    setVersionName(
      savedVersion
        .version_name,
    )

    setSavedAt(
      savedVersion
        .saved_at,
    )

    setResumeVersions(
      listResumeDraftVersions(
        user,
      ),
    )

    setActionMessage(
      'Resume version saved '
      + 'to this browser.',
    )
  }

  async function handleCopyContent() {
    if (!draft) {
      return
    }

    const content =
      buildResumePlainText(
        contact,
        draft,
      )

    try {
      await navigator
        .clipboard
        .writeText(
          content,
        )

      setActionMessage(
        'Resume content copied.',
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

    try {
      await downloadResumeDocx(
        contact,
        draft,
      )

      setActionMessage(
        'Word resume downloaded.',
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

    try {
      await downloadResumePdf(
        contact,
        draft,
      )

      setActionMessage(
        'PDF resume downloaded.',
      )
    }
    catch {
      setActionMessage(
        'PDF download failed. '
        + 'Please try again.',
      )
    }
  }


  function handleEditSection(
    section,
  ) {
    setEditingSection(
      (current) =>
        current === section
          ? null
          : section,
    )
  }


  function isEditing(
    section,
  ) {
    return (
      editingSection === 'all'
      || editingSection === section
    )
  }


  function renderDraftSection(
    field,
    title,
    isList = false,
  ) {
    if (!draft) {
      return null
    }

    const editing =
      isEditing(
        field,
      )

    const value =
      isList
        ? draft[field].join('\n')
        : draft[field]

    return (
      <article
        className="resume-builder__draft-section"
      >
        <div
          className="resume-builder__draft-section-heading"
        >
          <h3>
            {title}
          </h3>

          <button
            className="resume-builder__text-button"
            type="button"
            onClick={() =>
              handleEditSection(
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
                className="resume-builder__draft-textarea"
                value={value}
                rows={
                  field
                    === 'professional_summary'
                    ? 5
                    : 7
                }
                aria-label={
                  `Edit ${title}`
                }
                onChange={
                  (event) => {
                    if (isList) {
                      updateDraftList(
                        field,
                        event.target.value,
                      )
                    }
                    else {
                      updateDraftText(
                        field,
                        event.target.value,
                      )
                    }
                  }
                }
              />
            )
            : (
              isList
                ? (
                  draft[field].length
                    ? (
                      <ul
                        className="resume-builder__draft-list"
                      >
                        {
                          draft[field]
                            .map(
                              (
                                item,
                                index,
                              ) => (
                                <li
                                  key={
                                    `${field}-${index}`
                                  }
                                >
                                  {item}
                                </li>
                              ),
                            )
                        }
                      </ul>
                    )
                    : (
                      <p
                        className="resume-builder__empty-copy"
                      >
                        No content yet.
                      </p>
                    )
                )
                : (
                  <p
                    className="resume-builder__draft-copy"
                  >
                    {
                      draft[field]
                      || 'No content yet.'
                    }
                  </p>
                )
            )
        }
      </article>
    )
  }


  return (
    <main
      className="resume-builder"
    >
      <div
        className="resume-builder__content"
      >
        <header
          className="resume-builder__header"
        >
          <div>
            <h1>
              Resume Builder
            </h1>

            <p>
              Build a resume tailored
              to your target career
              using the evidence in
              your GradNavi profile.
            </p>
          </div>

          <div
            className="resume-builder__account"
          >
            <span
              className="resume-builder__avatar"
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
          className="resume-builder__guide"
        >
          <summary>
            How Resume Builder works
          </summary>

          <div
            className="resume-builder__intro-grid"
          >
            <article>
              <h2>
                Start with your target
              </h2>

              <ul>
                <li>
                  Selected career:
                  {' '}
                  {
                    selectedTargetCareer
                      ?.career_name
                    || targetCareer
                  }
                </li>

                <li>
                  Resume focus:
                  {' '}
                  {
                    selectedResumeFocusLabel
                  }
                </li>

                <li>
                  Profile evidence
                  supplies the facts
                </li>
              </ul>
            </article>

            <article>
              <h2>
                GradNavi creates the first draft
              </h2>

              <ul>
                <li>
                  Professional summary
                </li>

                <li>
                  Skills, education,
                  experience, projects
                </li>

                <li>
                  Missing information
                  and limitations
                </li>
              </ul>
            </article>

            <article>
              <h2>
                You stay in control
              </h2>

              <ul>
                <li>
                  Review every section
                </li>

                <li>
                  Edit wording before use
                </li>

                <li>
                  Save or continue to
                  a cover letter
                </li>
              </ul>
            </article>
          </div>
        </details>


        <section
          className="resume-builder__section"
        >
          <div
            className="resume-builder__section-heading"
          >
            <div>
              <h2>
                Resume Target
              </h2>

              <p>
                Choose one career for this
                resume. GradNavi keeps
                separate resume versions for
                different careers and
                vacancies.
              </p>
            </div>

            <span
              className="document-help-heading"
            >
              <span
                className="resume-builder__ai-badge"
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
            className="resume-builder__document-config-grid"
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
                          getCareerOptionLabel(
                            career,
                          )
                        }
                      </option>
                    ),
                  )
                }
              </select>

              <small>
                Career Goals and current
                GradNavi recommendations
                appear here.
              </small>
            </label>

            <label>
              <span
                className="document-help-heading"
              >
                Resume Focus

                <HelpTip
                  label="Help with Resume Focus"
                  title="Resume Focus"
                  text="Choose what your resume should emphasise. Select a balanced resume or focus on skills, projects, experience, or another available option."
                />
              </span>

              <select
                value={
                  resumeFocus
                }
                onChange={
                  (event) => {
                    setResumeFocus(
                      event.target.value,
                    )

                    setActionMessage('')
                  }
                }
              >
                {
                  RESUME_FOCUS_OPTIONS.map(
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
                Current focus:
                {' '}
                {
                  selectedResumeFocusLabel
                }.
              </small>
            </label>

            <label>
              <span>
                Version Name
              </span>

              <input
                type="text"
                value={
                  versionName
                }
                placeholder={
                  'General Resume or Company Name'
                }
                onChange={
                  (event) => {
                    setVersionName(
                      event.target.value,
                    )

                    setActionMessage('')
                  }
                }
              />

              <small>
                Use a name that helps you identify this resume. You may rename it anytime.
              </small>
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
                Saved versions are kept
                separately for the selected
                career.
              </small>
            </label>

            <label
              className="resume-builder__config-full"
            >
              <span>
                Job Description
                {' '}
                <em>
                  Optional
                </em>
              </span>

              <textarea
                value={
                  jobDescription
                }
                placeholder={
                  'Paste a job description '
                  + 'to tailor this resume '
                  + 'to a specific vacancy.'
                }
                onChange={
                  (event) => {
                    setJobDescription(
                      event.target.value,
                    )

                    setActionMessage('')
                  }
                }
              />

              <small>
                Leave this empty for a general ATS-friendly resume. Add a job description to tailor the resume to a specific role.
              </small>
            </label>
          </div>

          {
            careerOptionsError
              ? (
                <div
                  className="resume-builder__state-inline resume-builder__state-inline--error"
                  role="alert"
                >
                  {careerOptionsError}
                </div>
              )
              : null
          }

          <div
            className="resume-builder__button-row"
          >
            <button
              className="resume-builder__primary-button"
              type="button"
              disabled={
                generationState
                === 'generating'
                || !selectedTargetCareer
              }
              onClick={
                handleGenerate
              }
            >
              {
                generationState
                === 'generating'
                  ? 'Generating Resume...'
                  : 'Generate Resume Draft'
              }
            </button>

            <button
              className="resume-builder__secondary-button"
              type="button"
              disabled={
                !selectedTargetCareer
              }
              onClick={
                handleNewResumeVersion
              }
            >
              New Resume Version
            </button>

            <button
              className="resume-builder__secondary-button"
              type="button"
              onClick={() =>
                navigate('/profile')
              }
            >
              Edit Profile
            </button>
          </div>
        </section>


        <section
          className="resume-builder__section"
        >
          <div
            className="resume-builder__section-heading"
          >
            <div>
              <h2>
                Contact Details
              </h2>

              <p>
                Review the contact details
                used only in your saved
                and exported resume.
              </p>
            </div>

            <span
              className="document-help-heading"
            >
              <span
                className="resume-builder__privacy-badge"
              >
                Private contact details
              </span>

              <HelpTip
                  label="How GradNavi uses your information"
                  title="Privacy"
                  text="GradNavi uses the information needed to prepare your document. Personal contact details are kept out of the writing request and are added only to the final document."
                />
            </span>
          </div>

          <div
            className="resume-builder__contact-grid"
          >
            <label>
              <span>
                Full Name
              </span>

              <input
                type="text"
                value={
                  contact.fullName
                }
                onChange={
                  (event) =>
                    updateContact(
                      'fullName',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                Email
              </span>

              <input
                type="email"
                value={
                  contact.email
                }
                onChange={
                  (event) =>
                    updateContact(
                      'email',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                Phone
              </span>

              <input
                type="tel"
                value={
                  contact.phone
                }
                placeholder="+61 ..."
                onChange={
                  (event) =>
                    updateContact(
                      'phone',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                Location
              </span>

              <input
                type="text"
                value={
                  contact.location
                }
                placeholder="City, State"
                onChange={
                  (event) =>
                    updateContact(
                      'location',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                LinkedIn
              </span>

              <input
                type="url"
                value={
                  contact.linkedin
                }
                placeholder="https://linkedin.com/in/..."
                onChange={
                  (event) =>
                    updateContact(
                      'linkedin',
                      event.target.value,
                    )
                }
              />
            </label>

            <label>
              <span>
                Portfolio / Website
              </span>

              <input
                type="url"
                value={
                  contact.portfolio
                }
                placeholder="https://..."
                onChange={
                  (event) =>
                    updateContact(
                      'portfolio',
                      event.target.value,
                    )
                }
              />
            </label>
          </div>

          <div
            className="resume-builder__privacy-notice"
          >
            GradNavi does not use your contact details to write the draft. They are added only to your final resume.
          </div>
        </section>


        <section
          className="resume-builder__section"
        >
          <div
            className="resume-builder__section-heading"
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
                These profile details
                shape your resume.
                Review anything that
                needs updating before
                generation.
              </p>
            </div>
          </div>

          {
            profileLoading
              ? (
                <div
                  className="resume-builder__state-inline"
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
                  className="resume-builder__notice resume-builder__notice--error"
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
                  className="resume-builder__evidence-grid"
                >
                  <article>
                    <h3>
                      Included evidence
                    </h3>

                    {
                      includedEvidence.length
                        ? (
                          <ul>
                            {
                              includedEvidence
                                .map(
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
                            No profile evidence
                            is available yet.
                          </p>
                        )
                    }
                  </article>

                  <article>
                    <h3>
                      Worth improving
                      before generation
                    </h3>

                    <ul>
                      {
                        improvementItems
                          .map(
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
                </div>
              )
              : null
          }

          {
            !experience.length
            && !profileLoading
              ? (
                <div
                  className="resume-builder__notice resume-builder__notice--info"
                >
                  <strong>
                    Missing information notice
                  </strong>

                  <p>
                    Your profile does not
                    include detailed work
                    experience yet. You may
                    still generate a resume
                    using education, projects,
                    skills, and career goals,
                    then add more evidence
                    later.
                  </p>
                </div>
              )
              : null
          }
        </section>


        <details
          className="resume-builder__review-details"
        >
          <summary>
            <span>
              Review before generating
            </span>

            <small>
              Ready items, unsupported claims,
              and final checks
            </small>
          </summary>

          <div
            className="resume-builder__review-grid"
          >
            <article>
              <h3>
                Ready for draft
              </h3>

              {
                readyItems.length
                  ? (
                    <ul>
                      {
                        readyItems.map(
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
                      Add profile evidence
                      before relying on
                      the generated draft.
                    </p>
                  )
              }
            </article>

            <article>
              <h3>
                GradNavi will not add
              </h3>

              <ul>
                <li>
                  Employers you have
                  not listed
                </li>

                <li>
                  Unverified certifications
                </li>

                <li>
                  Achievements without
                  profile evidence
                </li>
              </ul>
            </article>

            <article>
              <h3>
                Before using the resume
              </h3>

              <ul>
                <li>
                  Edit wording
                </li>

                <li>
                  Confirm facts
                </li>

                <li>
                  Add missing details
                  where needed
                </li>
              </ul>
            </article>
          </div>
        </details>


        {
          generationState
          === 'empty'
            ? (
              <section
                className="resume-builder__state-card"
              >
                <h2>
                  No resume draft yet
                </h2>

                <p>
                  Select a target career,
                  choose your resume
                  focus, review your
                  profile evidence, then
                  generate a draft.
                </p>

                <button
                  className="resume-builder__primary-button"
                  type="button"
                  onClick={
                    handleGenerate
                  }
                >
                  Generate Resume Draft
                </button>
              </section>
            )
            : null
        }


        {
          generationState
          === 'generating'
            ? (
              <section
                className="resume-builder__state-card"
                aria-live="polite"
              >
                <div
                  className="resume-builder__loading-indicator"
                  aria-hidden="true"
                />

                <h2>
                  Preparing your draft
                </h2>

                <p>
                  GradNavi is using
                  approved Student Profile
                  evidence. Keep this page
                  open while the request
                  finishes.
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
                className="resume-builder__state-card resume-builder__state-card--error"
                role="alert"
              >
                <h2>
                  Resume draft could
                  not be created
                </h2>

                <p>
                  {generationError}
                </p>

                <div
                  className="resume-builder__button-row"
                >
                  <button
                    className="resume-builder__primary-button"
                    type="button"
                    onClick={
                      handleGenerate
                    }
                  >
                    Try Again
                  </button>

                  <button
                    className="resume-builder__secondary-button"
                    type="button"
                    onClick={() =>
                      navigate('/profile')
                    }
                  >
                    Review Profile
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
                className="resume-builder__section resume-builder__draft"
              >
                <div
                  className="resume-builder__draft-heading"
                >
                  <div>
                    <h2>
                      Your Resume Draft
                    </h2>

                    <p>
                      Review each section,
                      edit the wording,
                      and confirm every
                      detail before use.
                    </p>
                  </div>


                </div>

                <div
                  className="resume-builder__draft-toolbar"
                >
                  <div
                    className="resume-builder__draft-toolbar-copy"
                  >
                    <span
                      className="resume-builder__ai-badge"
                    >
                      AI-generated draft
                    </span>

                    <p>
                      Review and edit the
                      content before using
                      your resume.
                    </p>
                  </div>

                  <div
                    className="resume-builder__draft-toolbar-actions"
                  >
                    <button
                      className="resume-builder__primary-button"
                      type="button"
                      onClick={() =>
                        setEditingSection(
                          (
                            editingSection
                            === 'all'
                          )
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
                      className="resume-builder__secondary-button"
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
                  className="resume-builder__draft-layout"
                >
                  <div
                    className="resume-builder__draft-main"
                  >
                    {
                      renderDraftSection(
                        'professional_summary',
                        'Professional Summary',
                      )
                    }

                    {
                      renderDraftSection(
                        'skills',
                        'Skills',
                        true,
                      )
                    }

                    {
                      renderDraftSection(
                        'education',
                        'Education',
                        true,
                      )
                    }

                    {
                      renderDraftSection(
                        'projects',
                        'Projects',
                        true,
                      )
                    }

                    {
                      renderDraftSection(
                        'experience',
                        'Experience',
                        true,
                      )
                    }
                  </div>


                  <aside
                    className="resume-builder__draft-sidebar"
                  >
                    <article
                      className="resume-builder__review-panel"
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
                                          className="resume-builder__status-dot resume-builder__status-dot--warning"
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


                    <article
                      className="resume-builder__review-panel"
                    >
                      <h3>
                        Draft limitations
                      </h3>

                      {
                        draft
                          .limitations
                          .length
                          ? (
                            <ul>
                              {
                                draft
                                  .limitations
                                  .map(
                                    (
                                      item,
                                      index,
                                    ) => (
                                      <li
                                        key={
                                          `limitation-${index}`
                                        }
                                      >
                                        <span
                                          className="resume-builder__status-dot resume-builder__status-dot--safe"
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
                              Review all
                              generated content
                              before use.
                            </p>
                          )
                      }
                    </article>
                  </aside>
                </div>

                <div
                  className="resume-builder__final-actions"
                >
                  <button
                    className="resume-builder__primary-button"
                    type="button"
                    onClick={
                      handleSaveDraft
                    }
                  >
                    Save Draft
                  </button>

                  <button
                    className="resume-builder__secondary-button"
                    type="button"
                    onClick={
                      handleDownloadWord
                    }
                  >
                    Download Word
                  </button>

                  <button
                    className="resume-builder__secondary-button"
                    type="button"
                    onClick={
                      handleDownloadPdf
                    }
                  >
                    Download PDF
                  </button>

                  <button
                    className="resume-builder__secondary-button"
                    type="button"
                    onClick={
                      handleCopyContent
                    }
                  >
                    Copy Content
                  </button>

                  <button
                    className="resume-builder__secondary-button"
                    type="button"
                    onClick={() =>
                      navigate(
                        '/cover-letter-builder',
                      )
                    }
                  >
                    Start Cover Letter
                  </button>
                </div>

                {
                  actionMessage
                    ? (
                      <p
                        className="resume-builder__action-message"
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


export default ResumeBuilderPage
