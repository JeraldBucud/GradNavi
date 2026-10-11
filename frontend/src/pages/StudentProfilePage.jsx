import {
  useEffect,
  useState,
} from 'react'

import CareerGoalsSection from '../components/profile/CareerGoalsSection'
import EducationSection from '../components/profile/EducationSection'
import ExperienceSection from '../components/profile/ExperienceSection'
import InterestsSection from '../components/profile/InterestsSection'
import PersonalityResponsesSection from '../components/profile/PersonalityResponsesSection'
import ProjectSection from '../components/profile/ProjectSection'
import SkillsSection from '../components/profile/SkillsSection'

import {
  PROFILE_QUESTIONNAIRE,
} from '../data/profileQuestionnaire'

import {
  getStoredUser,
} from '../services/authService'

import {
  getStudentProfile,
  updateStudentProfile,
} from '../services/profileService'

import './StudentProfilePage.css'


function createEmptyProfile() {
  return {
    skills: [],
    interests: [],
    education: [],
    experience: [],
    projects: [],
    career_goals: [],
    personality_responses: [],
  }
}


function normalizeProfileResponse(
  responseData,
) {
  const profileData =
    responseData?.data?.profile

  if (!profileData) {
    return createEmptyProfile()
  }

  return {
    skills:
      Array.isArray(
        profileData.skills,
      )
        ? profileData.skills
        : [],

    interests:
      Array.isArray(
        profileData.interests,
      )
        ? profileData.interests
        : [],

    education:
      Array.isArray(
        profileData.education,
      )
        ? profileData.education
        : [],

    experience:
      Array.isArray(
        profileData.experience,
      )
        ? profileData.experience
        : [],

    projects:
      Array.isArray(
        profileData.projects,
      )
        ? profileData.projects
        : [],

    career_goals:
      Array.isArray(
        profileData.career_goals,
      )
        ? profileData.career_goals
        : [],

    personality_responses:
      Array.isArray(
        profileData
          .personality_responses,
      )
        ? profileData
          .personality_responses
        : [],
  }
}


function buildProfilePayload(
  profile,
) {
  return {
    skills:
      profile.skills.map(
        (skill) => ({
          ...(skill.id
            ? {
                id: skill.id,
              }
            : {
                name:
                  skill.name,
              }),

          proficiency_level:
            skill.proficiency_level,
        }),
      ),

    interests:
      profile.interests.map(
        (interest) => ({
          ...(interest.id
            ? {
                id:
                  interest.id,
              }
            : {
                name:
                  interest.name,
              }),
        }),
      ),

    education:
      profile.education.map(
        (education) => ({
          ...(education.id
            ? {
                id:
                  education.id,
              }
            : {}),

          institution_name:
            education
              .institution_name,

          qualification:
            education
              .qualification,

          field_of_study:
            education
              .field_of_study,

          start_date:
            education.start_date,

          end_date:
            education.end_date
            || null,

          description:
            education.description
            || '',
        }),
      ),

    experience:
      profile.experience.map(
        (experience) => ({
          ...(experience.id
            ? {
                id:
                  experience.id,
              }
            : {}),

          job_title:
            experience.job_title,

          company:
            experience.company,

          start_date:
            experience.start_date,

          end_date:
            experience.is_current
              ? null
              : experience.end_date
                || null,

          is_current:
            Boolean(
              experience.is_current,
            ),

          description:
            experience.description
            || '',
        }),
      ),

    projects:
      profile.projects.map(
        (project) => ({
          ...(project.id
            ? {
                id:
                  project.id,
              }
            : {}),

          name:
            project.name,

          description:
            project.description
            || '',

          project_url:
            project.project_url
            || '',

          start_date:
            project.start_date,

          end_date:
            project.end_date
            || null,
        }),
      ),

    career_goals:
      profile.career_goals.map(
        (careerGoal) => ({
          ...(careerGoal.id
            ? {
                id:
                  careerGoal.id,
              }
            : {}),

          ...(careerGoal.career_id
            ? {
                career_id:
                  careerGoal
                    .career_id,
              }
            : {
                target_role:
                  careerGoal
                    .target_role,
              }),

          description:
            careerGoal.description
            || '',

          is_primary:
            Boolean(
              careerGoal.is_primary,
            ),
        }),
      ),

    personality_responses:
      profile
        .personality_responses
        .map(
          (
            personalityResponse,
          ) => ({
            ...(personalityResponse.id
              ? {
                  id:
                    personalityResponse
                      .id,
                }
              : {}),

            question_key:
              personalityResponse
                .question_key,

            response_value:
              personalityResponse
                .response_value,
          }),
        ),
  }
}


function getFirstErrorMessage(
  value,
) {
  if (!value) {
    return ''
  }

  if (
    typeof value
    === 'string'
  ) {
    return value
  }

  if (
    Array.isArray(
      value,
    )
  ) {
    for (
      const item
      of value
    ) {
      const message =
        getFirstErrorMessage(
          item,
        )

      if (message) {
        return message
      }
    }

    return ''
  }

  if (
    typeof value
    === 'object'
  ) {
    for (
      const nestedValue
      of Object.values(
        value,
      )
    ) {
      const message =
        getFirstErrorMessage(
          nestedValue,
        )

      if (message) {
        return message
      }
    }
  }

  return ''
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  const details =
    requestError
      ?.data
      ?.error
      ?.details

  return (
    getFirstErrorMessage(
      details,
    )
    || requestError?.message
    || fallbackMessage
  )
}


function getStructuredSummary(
  items,
  type,
) {
  if (
    !Array.isArray(items)
    || items.length === 0
  ) {
    return 'No records added yet'
  }

  const first =
    items[0]

  let summary = ''

  if (
    type === 'education'
  ) {
    summary = [
      first.qualification,
      first.institution_name,
    ]
      .filter(Boolean)
      .join(' · ')
  }

  if (
    type === 'experience'
  ) {
    summary = [
      first.job_title,
      first.company,
    ]
      .filter(Boolean)
      .join(' · ')
  }

  if (
    type === 'projects'
  ) {
    summary =
      first.name
      || 'Project evidence'
  }

  if (
    items.length > 1
  ) {
    return (
      `${summary} +${
        items.length - 1
      } more`
    )
  }

  return summary
}


function StudentProfilePage() {
  const [
    profile,
    setProfile,
  ] = useState(
    createEmptyProfile,
  )

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    isSaving,
    setIsSaving,
  ] = useState(false)

  const [
    isDirty,
    setIsDirty,
  ] = useState(false)

  const [
    loadError,
    setLoadError,
  ] = useState('')

  const [
    saveError,
    setSaveError,
  ] = useState('')

  const [
    saveMessage,
    setSaveMessage,
  ] = useState('')

  const [
    activeEditor,
    setActiveEditor,
  ] = useState(null)


  const currentUser =
    getStoredUser()

  const accountName =
    currentUser
      ?.first_name
      ?.trim()
    || 'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()


  const primaryCareerGoalRecord =
    profile.career_goals.find(
      (careerGoal) =>
        careerGoal.is_primary,
    )
    || profile.career_goals[0]
    || null


  const primaryCareerGoal =
    primaryCareerGoalRecord
      ?.target_role
    || 'Not set'


  const answeredPersonalityCount =
    PROFILE_QUESTIONNAIRE.filter(
      (question) =>
        profile
          .personality_responses
          .some(
            (response) =>
              response
                .question_key
              === question.key
              && Boolean(
                response
                  .response_value,
              ),
          ),
    ).length


  const structuredEvidenceCount =
    profile.education.length
    + profile.experience.length
    + profile.projects.length


  useEffect(() => {
    let isActive = true

    async function loadProfile() {
      try {
        setIsLoading(true)
        setLoadError('')

        const responseData =
          await getStudentProfile()

        if (!isActive) {
          return
        }

        const loadedProfile =
          normalizeProfileResponse(
            responseData,
          )

        setProfile(
          loadedProfile,
        )

        setIsDirty(false)
      } catch (
        requestError
      ) {
        if (!isActive) {
          return
        }

        if (
          requestError.status
          === 404
        ) {
          setLoadError(
            'Student profile not found for this account.',
          )
        } else {
          setLoadError(
            getRequestErrorMessage(
              requestError,
              (
                'Unable to load '
                + 'the Student Profile.'
              ),
            ),
          )
        }
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    loadProfile()

    return () => {
      isActive = false
    }
  }, [])


  function handleSectionChange(
    sectionName,
    nextItems,
  ) {
    setProfile(
      (
        currentProfile,
      ) => ({
        ...currentProfile,

        [sectionName]:
          nextItems,
      }),
    )

    setIsDirty(true)
    setSaveMessage('')
    setSaveError('')
  }


  function scrollToSection(
    sectionId,
  ) {
    window
      .requestAnimationFrame(
        () => {
          document
            .getElementById(
              sectionId,
            )
            ?.scrollIntoView(
              {
                behavior:
                  'smooth',

                block:
                  'start',
              },
            )
        },
      )
  }


  function openEditor(
    editorName,
    targetId,
  ) {
    setActiveEditor(
      editorName,
    )

    if (targetId) {
      scrollToSection(
        targetId,
      )
    }
  }


  function closeEditor() {
    setActiveEditor(null)
  }


  async function handleSaveProfile() {
    try {
      setIsSaving(true)
      setSaveError('')
      setSaveMessage('')

      const profilePayload =
        buildProfilePayload(
          profile,
        )

      const responseData =
        await updateStudentProfile(
          profilePayload,
        )

      const savedProfile =
        normalizeProfileResponse(
          responseData,
        )

      setProfile(
        savedProfile,
      )

      setIsDirty(false)

      setSaveMessage(
        'Profile saved successfully.',
      )

      return true
    } catch (
      requestError
    ) {
      setSaveError(
        getRequestErrorMessage(
          requestError,
          (
            'Unable to save '
            + 'the Student Profile.'
          ),
        ),
      )

      return false
    } finally {
      setIsSaving(false)
    }
  }


  function renderProfileEvidenceEditor() {
    if (
      activeEditor === 'skills'
    ) {
      return (
        <div
          id="profile-evidence-editor"
          className="student-profile-redesign__editor"
        >
          <div className="student-profile-redesign__editor-heading">
            <div>
              <h3>
                Edit Skills
              </h3>

              <p>
                Search approved GradNavi
                Skills and record your
                proficiency.
              </p>
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={closeEditor}
            >
              Close
            </button>
          </div>

          <SkillsSection
            items={
              profile.skills
            }
            onChange={(
              nextItems,
            ) =>
              handleSectionChange(
                'skills',
                nextItems,
              )
            }
          />
        </div>
      )
    }


    if (
      activeEditor
      === 'career-goals'
    ) {
      return (
        <div
          id="profile-evidence-editor"
          className="student-profile-redesign__editor"
        >
          <CareerGoalsSection
            items={
              profile
                .career_goals
            }
            onChange={(
              nextItems,
            ) =>
              handleSectionChange(
                'career_goals',
                nextItems,
              )
            }
            onClose={
              closeEditor
            }
          />
        </div>
      )
    }


    if (
      activeEditor
      === 'interests'
    ) {
      return (
        <div
          id="profile-evidence-editor"
          className="student-profile-redesign__editor"
        >
          <InterestsSection
            items={
              profile.interests
            }
            onChange={(
              nextItems,
            ) =>
              handleSectionChange(
                'interests',
                nextItems,
              )
            }
            onClose={
              closeEditor
            }
          />
        </div>
      )
    }


    return null
  }


  function renderStructuredEditor() {
    if (
      activeEditor
      === 'education'
    ) {
      return (
        <div
          id="structured-evidence-editor"
          className="student-profile-redesign__editor"
        >
          <div className="student-profile-redesign__editor-heading">
            <div>
              <h3>
                Education Evidence
              </h3>

              <p>
                Add or edit your
                qualifications and
                study history.
              </p>
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={closeEditor}
            >
              Close
            </button>
          </div>

          <EducationSection
            items={
              profile.education
            }
            onChange={(
              nextItems,
            ) =>
              handleSectionChange(
                'education',
                nextItems,
              )
            }
          />
        </div>
      )
    }


    if (
      activeEditor
      === 'experience'
    ) {
      return (
        <div
          id="structured-evidence-editor"
          className="student-profile-redesign__editor"
        >
          <div className="student-profile-redesign__editor-heading">
            <div>
              <h3>
                Experience Evidence
              </h3>

              <p>
                Add or edit employment
                and professional
                experience.
              </p>
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={closeEditor}
            >
              Close
            </button>
          </div>

          <ExperienceSection
            items={
              profile.experience
            }
            onChange={(
              nextItems,
            ) =>
              handleSectionChange(
                'experience',
                nextItems,
              )
            }
          />
        </div>
      )
    }


    if (
      activeEditor
      === 'projects'
    ) {
      return (
        <div
          id="structured-evidence-editor"
          className="student-profile-redesign__editor"
        >
          <div className="student-profile-redesign__editor-heading">
            <div>
              <h3>
                Project Evidence
              </h3>

              <p>
                Add or edit portfolio
                and project evidence.
              </p>
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={closeEditor}
            >
              Close
            </button>
          </div>

          <ProjectSection
            items={
              profile.projects
            }
            onChange={(
              nextItems,
            ) =>
              handleSectionChange(
                'projects',
                nextItems,
              )
            }
          />
        </div>
      )
    }


    return null
  }


  if (isLoading) {
    return (
      <main className="student-profile-page student-profile-redesign">
        <section className="student-profile-redesign__state">
          <span>
            Loading Student Profile...
          </span>
        </section>
      </main>
    )
  }


  if (loadError) {
    return (
      <main className="student-profile-page student-profile-redesign">
        <header className="student-profile-redesign__heading">
          <div>
            <h1>
              Student Profile
            </h1>
          </div>
        </header>

        <section className="student-profile-redesign__state">
          <strong>
            Profile unavailable
          </strong>

          <p role="alert">
            {loadError}
          </p>
        </section>
      </main>
    )
  }


  return (
    <main className="student-profile-page student-profile-redesign">
      <header className="student-profile-redesign__heading">
        <div className="student-profile-redesign__heading-copy">
          <h1>
            Student Profile
          </h1>

          <p>
            Build the evidence GradNavi
            uses for recommendations,
            readiness, skill gaps, and
            AI-assisted application
            drafts.
          </p>
        </div>

        <div
          className="student-profile-account-pill"
          aria-label={
            `Signed in as ${
              accountName
            }`
          }
        >
          <span
            className="student-profile-account-pill__avatar"
            aria-hidden="true"
          >
            {accountInitial}
          </span>

          <span>
            {accountName}
          </span>
        </div>
      </header>


      <section
        id="profile-summary"
        className="student-profile-redesign__section"
      >
        <div className="student-profile-redesign__section-heading">
          <div>
            <h2>
              Profile Evidence Summary
            </h2>

            <p>
              A factual overview of
              the evidence currently
              stored in your profile.
            </p>
          </div>

          <button
            className="student-profile-redesign__primary-button"
            type="button"
            onClick={
              handleSaveProfile
            }
            disabled={
              !isDirty
              || isSaving
            }
          >
            {
              isSaving
                ? 'Saving Profile...'
                : 'Save Profile'
            }
          </button>
        </div>


        <div className="student-profile-redesign__summary-grid">
          <article className="student-profile-redesign__metric-card">
            <span>
              Structured evidence
            </span>

            <strong>
              {
                structuredEvidenceCount
              }
            </strong>

            <small>
              {
                structuredEvidenceCount
                === 1
                  ? 'saved entry'
                  : 'saved entries'
              }
            </small>
          </article>


          <article className="student-profile-redesign__metric-card">
            <span>
              Skills saved
            </span>

            <strong>
              {
                profile.skills.length
              }
            </strong>

            <small>
              approved GradNavi skills
            </small>
          </article>


          <article className="student-profile-redesign__metric-card">
            <span>
              Primary goal
            </span>

            <strong className="student-profile-redesign__metric-card-value--text">
              {
                primaryCareerGoal
              }
            </strong>

            <small>
              {
                profile
                  .career_goals
                  .length
              } career {
                profile
                  .career_goals
                  .length === 1
                  ? 'goal'
                  : 'goals'
              }
            </small>
          </article>


          <article className="student-profile-redesign__metric-card">
            <span>
              Personality
            </span>

            <strong>
              {
                answeredPersonalityCount
              }
              {' / '}
              {
                PROFILE_QUESTIONNAIRE
                  .length
              }
            </strong>

            <small>
              responses completed
            </small>
          </article>
        </div>


        <div
          className="student-profile-redesign__save-state"
          aria-live="polite"
        >
          {isDirty && (
            <p className="student-profile-redesign__unsaved">
              You have unsaved
              profile changes.
            </p>
          )}

          {saveError && (
            <p
              className="student-profile-redesign__error"
              role="alert"
            >
              {saveError}
            </p>
          )}

          {saveMessage && (
            <p className="student-profile-redesign__success">
              {saveMessage}
            </p>
          )}
        </div>
      </section>


      <section className="student-profile-redesign__section">
        <div className="student-profile-redesign__section-heading">
          <div>
            <h2>
              Profile Evidence
            </h2>

            <p>
              Add the skills, career
              direction, and interests
              that help GradNavi
              understand your profile.
            </p>
          </div>
        </div>


        <div className="student-profile-redesign__evidence-grid">
          <article className="student-profile-redesign__evidence-card">
            <div>
              <h3>
                Skills
              </h3>

              <p>
                Search approved skills
                and record proficiency.
              </p>
            </div>

            <div className="student-profile-redesign__chips">
              {
                profile.skills
                  .slice(
                    0,
                    6,
                  )
                  .map(
                    (skill) => (
                      <span
                        key={
                          skill.id
                          || skill.name
                        }
                        className="student-profile-redesign__chip"
                      >
                        {skill.name}
                      </span>
                    ),
                  )
              }

              {
                profile.skills
                  .length === 0
                && (
                  <span className="student-profile-redesign__empty">
                    No skills saved
                  </span>
                )
              }

              {
                profile.skills
                  .length > 6
                && (
                  <span className="student-profile-redesign__chip student-profile-redesign__chip--neutral">
                    +{
                      profile
                        .skills
                        .length - 6
                    } more
                  </span>
                )
              }
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={() =>
                openEditor(
                  'skills',
                  'profile-evidence-editor',
                )
              }
            >
              Edit Skills
            </button>
          </article>


          <article className="student-profile-redesign__evidence-card">
            <div>
              <h3>
                Career Goals
              </h3>

              <p>
                Keep multiple career
                goals and choose one
                Primary Goal.
              </p>
            </div>

            <div className="student-profile-redesign__chips">
              {
                profile
                  .career_goals
                  .slice(
                    0,
                    5,
                  )
                  .map(
                    (
                      careerGoal,
                    ) => (
                      <span
                        key={
                          careerGoal.id
                          || careerGoal
                            .career_id
                          || careerGoal
                            .target_role
                        }
                        className={[
                          'student-profile-redesign__chip',
                          careerGoal
                            .is_primary
                            ? 'student-profile-redesign__chip--primary'
                            : '',
                        ]
                          .filter(
                            Boolean,
                          )
                          .join(' ')}
                      >
                        {
                          careerGoal
                            .target_role
                        }

                        {
                          careerGoal
                            .is_primary
                          ? ' · Primary'
                          : ''
                        }
                      </span>
                    ),
                  )
              }

              {
                profile
                  .career_goals
                  .length === 0
                && (
                  <span className="student-profile-redesign__empty">
                    No Career Goals saved
                  </span>
                )
              }

              {
                profile
                  .career_goals
                  .length > 5
                && (
                  <span className="student-profile-redesign__chip student-profile-redesign__chip--neutral">
                    +{
                      profile
                        .career_goals
                        .length - 5
                    } more
                  </span>
                )
              }
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={() =>
                openEditor(
                  'career-goals',
                  'profile-evidence-editor',
                )
              }
            >
              Edit Career Goals
            </button>
          </article>


          <article className="student-profile-redesign__evidence-card">
            <div>
              <h3>
                Interests
              </h3>

              <p>
                Save interests linked
                to your career
                preferences.
              </p>
            </div>

            <div className="student-profile-redesign__chips">
              {
                profile
                  .interests
                  .slice(
                    0,
                    6,
                  )
                  .map(
                    (
                      interest,
                    ) => (
                      <span
                        key={
                          interest.id
                          || interest.name
                        }
                        className="student-profile-redesign__chip"
                      >
                        {
                          interest.name
                        }
                      </span>
                    ),
                  )
              }

              {
                profile
                  .interests
                  .length === 0
                && (
                  <span className="student-profile-redesign__empty">
                    No interests saved
                  </span>
                )
              }

              {
                profile
                  .interests
                  .length > 6
                && (
                  <span className="student-profile-redesign__chip student-profile-redesign__chip--neutral">
                    +{
                      profile
                        .interests
                        .length - 6
                    } more
                  </span>
                )
              }
            </div>

            <button
              className="student-profile-redesign__secondary-button"
              type="button"
              onClick={() =>
                openEditor(
                  'interests',
                  'profile-evidence-editor',
                )
              }
            >
              Edit Interests
            </button>
          </article>
        </div>


        {
          [
            'skills',
            'career-goals',
            'interests',
          ].includes(
            activeEditor,
          )
          && renderProfileEvidenceEditor()
        }
      </section>


      <section className="student-profile-redesign__section">
        <div className="student-profile-redesign__section-heading">
          <div>
            <h2>
              Structured Evidence
            </h2>

            <p>
              Education, professional
              experience, and projects
              provide stronger context
              for recommendations and
              readiness analysis.
            </p>
          </div>
        </div>


        <div className="student-profile-redesign__structured-list">
          <article className="student-profile-redesign__structured-row">
            <div className="student-profile-redesign__structured-main">
              <span className="student-profile-redesign__structured-icon">
                E
              </span>

              <div>
                <h3>
                  Education
                </h3>

                <p>
                  {
                    getStructuredSummary(
                      profile.education,
                      'education',
                    )
                  }
                </p>
              </div>
            </div>

            <div className="student-profile-redesign__structured-actions">
              <span>
                {
                  profile
                    .education
                    .length
                } {
                  profile
                    .education
                    .length === 1
                    ? 'entry'
                    : 'entries'
                }
              </span>

              <button
                className="student-profile-redesign__secondary-button"
                type="button"
                onClick={() =>
                  openEditor(
                    'education',
                    'structured-evidence-editor',
                  )
                }
              >
                {
                  profile
                    .education
                    .length > 0
                    ? 'Edit'
                    : 'Add'
                }
              </button>
            </div>
          </article>


          <article className="student-profile-redesign__structured-row">
            <div className="student-profile-redesign__structured-main">
              <span className="student-profile-redesign__structured-icon">
                X
              </span>

              <div>
                <h3>
                  Experience
                </h3>

                <p>
                  {
                    getStructuredSummary(
                      profile.experience,
                      'experience',
                    )
                  }
                </p>
              </div>
            </div>

            <div className="student-profile-redesign__structured-actions">
              <span>
                {
                  profile
                    .experience
                    .length
                } {
                  profile
                    .experience
                    .length === 1
                    ? 'entry'
                    : 'entries'
                }
              </span>

              <button
                className="student-profile-redesign__secondary-button"
                type="button"
                onClick={() =>
                  openEditor(
                    'experience',
                    'structured-evidence-editor',
                  )
                }
              >
                {
                  profile
                    .experience
                    .length > 0
                    ? 'Edit'
                    : 'Add'
                }
              </button>
            </div>
          </article>


          <article className="student-profile-redesign__structured-row">
            <div className="student-profile-redesign__structured-main">
              <span className="student-profile-redesign__structured-icon">
                P
              </span>

              <div>
                <h3>
                  Projects
                </h3>

                <p>
                  {
                    getStructuredSummary(
                      profile.projects,
                      'projects',
                    )
                  }
                </p>
              </div>
            </div>

            <div className="student-profile-redesign__structured-actions">
              <span>
                {
                  profile
                    .projects
                    .length
                } {
                  profile
                    .projects
                    .length === 1
                    ? 'entry'
                    : 'entries'
                }
              </span>

              <button
                className="student-profile-redesign__secondary-button"
                type="button"
                onClick={() =>
                  openEditor(
                    'projects',
                    'structured-evidence-editor',
                  )
                }
              >
                {
                  profile
                    .projects
                    .length > 0
                    ? 'Edit'
                    : 'Add'
                }
              </button>
            </div>
          </article>
        </div>


        {
          [
            'education',
            'experience',
            'projects',
          ].includes(
            activeEditor,
          )
          && renderStructuredEditor()
        }
      </section>


      <section
        id="personality-assessment"
        className="student-profile-redesign__section student-profile-redesign__personality-section"
      >
        <div className="student-profile-redesign__section-heading">
          <div>
            <h2>
              Personality Assessment
            </h2>

            <p>
              Answer 16 work-style
              statements one at a time.
              Your responses support
              career-analysis features.
            </p>
          </div>

          <span className="student-profile-redesign__personality-progress-pill">
            {
              answeredPersonalityCount
            }
            {' / '}
            {
              PROFILE_QUESTIONNAIRE
                .length
            }
            {' answered'}
          </span>
        </div>


        <PersonalityResponsesSection
          items={
            profile
              .personality_responses
          }
          onChange={(
            nextItems,
          ) =>
            handleSectionChange(
              'personality_responses',
              nextItems,
            )
          }
          onClose={() =>
            scrollToSection(
              'profile-summary',
            )
          }
          onSave={
            handleSaveProfile
          }
          isSaving={
            isSaving
          }
        />
      </section>
    </main>
  )
}


export default StudentProfilePage
