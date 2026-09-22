import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router'

import {
  generateResumeDraft,
} from '../services/documentService'

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


function ResumeBuilderPage() {
  const navigate = useNavigate()

  const storedUser =
    getStoredUser()

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
    storedDraft?.draft
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


  async function handleGenerate() {
    setGenerationState(
      'generating',
    )

    setGenerationError('')
    setActionMessage('')
    setEditingSection(null)

    try {
      const response =
        await generateResumeDraft()

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

      setGenerationState(
        'success',
      )

      setActionMessage(
        'Resume draft generated. '
        + 'Review every section '
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

    const timestamp =
      new Date()
        .toISOString()

    const storageKey =
      getResumeStorageKey(
        currentUser
        || storedUser,
      )

    if (!storageKey) {
      setActionMessage(
        'Sign in before saving '
        + 'this draft.',
      )

      return
    }

    localStorage.setItem(
      storageKey,
      JSON.stringify({
        contact,
        draft,
        savedAt: timestamp,
      }),
    )

    setSavedAt(
      timestamp,
    )

    setActionMessage(
      'Draft saved in this browser.',
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


        <section
          className="resume-builder__intro-grid"
          aria-label="Resume Builder overview"
        >
          <article>
            <h2>
              Start with your target
            </h2>

            <ul>
              <li>
                Selected career:
                {' '}
                {targetCareer}
              </li>

              <li>
                Resume focus:
                {' '}
                graduate roles
              </li>

              <li>
                Profile evidence
                supplies the facts
              </li>
            </ul>
          </article>

          <article>
            <h2>
              AI creates the first draft
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
        </section>


        <section
          className="resume-builder__section"
        >
          <div
            className="resume-builder__section-heading"
          >
            <div>
              <h2>
                Target Context
              </h2>

              <p>
                Review the career context
                used by the Resume Builder.
                These display fields do not
                add unsupported facts to
                your profile.
              </p>
            </div>
          </div>

          <div
            className="resume-builder__field-grid"
          >
            <div>
              <span>
                Target career
              </span>

              <strong>
                {targetCareer}
              </strong>
            </div>

            <div>
              <span>
                Resume focus
              </span>

              <strong>
                Graduate / entry-level role
              </strong>
            </div>

            <div>
              <span>
                Tone
              </span>

              <strong>
                Professional and concise
              </strong>
            </div>
          </div>

          <div
            className="resume-builder__button-row"
          >
            <button
              className="resume-builder__primary-button"
              type="button"
              disabled={
                generationState
                === 'generating'
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
              className="resume-builder__privacy-badge"
            >
              Not sent to AI
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
            Contact details stay outside
            the AI generation prompt.
            They are added only to the
            student-controlled final
            document.
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
                Profile Evidence
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


        <section
          className="resume-builder__section"
        >
          <div
            className="resume-builder__section-heading"
          >
            <div>
              <h2>
                Review Inputs
              </h2>

              <p>
                A quick check before
                generation keeps the
                draft grounded and
                easier to review.
              </p>
            </div>
          </div>

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
                AI will not add
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
        </section>


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
                  Review your profile
                  evidence and contact
                  details, then generate
                  a draft when ready.
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
