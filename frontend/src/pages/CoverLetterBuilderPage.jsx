import {
  useEffect,
  useState,
} from 'react'


import {
  generateCoverLetterDraft,
} from '../services/documentService'

import {
  getCurrentUser,
  getStoredUser,
} from '../services/authService'

import {
  getStudentProfile,
} from '../services/profileService'

import './CoverLetterBuilderPage.css'


const STORAGE_KEY =
  'gradnavi_cover_letter_builder_draft_v1'


const EMPTY_JOB_CONTEXT = {
  jobTitle: '',
  company: '',
  applicationFocus: '',
  jobDescription: '',
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


function loadSavedDraft() {
  try {
    const stored =
      localStorage.getItem(
        STORAGE_KEY,
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


function CoverLetterBuilderPage() {

  const storedUser =
    getStoredUser()

  const [
    storedDraft,
  ] = useState(
    () => loadSavedDraft(),
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
    storedDraft?.jobContext
    || EMPTY_JOB_CONTEXT,
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


  async function handleGenerate() {
    const jobDescription =
      jobContext
        .jobDescription
        .trim()

    if (!jobDescription) {
      setGenerationState(
        'validation',
      )

      setGenerationError(
        'Add a job description '
        + 'before generating.',
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
        await generateCoverLetterDraft(
          jobDescription,
        )

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

      setGenerationState(
        'success',
      )

      setActionMessage(
        'Cover letter draft generated. '
        + 'Review every claim before use.',
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
          + 'could not be created.'
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

    const timestamp =
      new Date()
        .toISOString()

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        jobContext,
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


        <section
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
                for AI tailoring
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
        </section>


        <section
          id="cover-letter-job-context"
          className="cover-letter-builder__section"
        >
          <div
            className="cover-letter-builder__section-heading"
          >
            <div>
              <h2>
                Job Context
              </h2>

              <p>
                A cover letter needs a
                specific role. The job
                description is the only
                role information sent to
                the generation endpoint.
              </p>
            </div>

            <span
              className="cover-letter-builder__privacy-badge"
            >
              Job description only to AI
            </span>
          </div>

          <div
            className="cover-letter-builder__context-grid"
          >
            <label>
              <span>
                Job title
              </span>

              <input
                type="text"
                value={
                  jobContext.jobTitle
                }
                placeholder="Junior Software Developer"
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
              </span>

              <input
                type="text"
                value={
                  jobContext.company
                }
                placeholder="Sample Company"
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
                Application focus
              </span>

              <input
                type="text"
                value={
                  jobContext.applicationFocus
                }
                placeholder="Software development role"
                onChange={
                  (event) =>
                    updateJobContext(
                      'applicationFocus',
                      event.target.value,
                    )
                }
              />
            </label>
          </div>

          <label
            className="cover-letter-builder__job-description"
          >
            <span>
              Job Description
            </span>

            <textarea
              rows={10}
              value={
                jobContext.jobDescription
              }
              placeholder={
                'Paste the job description here. '
                + 'Include responsibilities, '
                + 'required skills, and role context.'
              }
              onChange={
                (event) =>
                  updateJobContext(
                    'jobDescription',
                    event.target.value,
                  )
              }
            />
          </label>

          <p
            className="cover-letter-builder__field-note"
          >
            Job title, company, and
            application focus stay in
            your browser for review.
            The API receives only the
            job description.
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
              <h2>
                Profile Evidence
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
                  Add a job description
                  first, then generate
                  when the role context
                  is ready.
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
                  Add a job description
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
