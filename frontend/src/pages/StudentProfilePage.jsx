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

import { getStoredUser } from '../services/authService'

import {
  getStudentProfile,
  updateStudentProfile,
} from '../services/profileService'

import './StudentProfilePage.css'


const profileSections = [
  {
    key: 'skills',
    label: 'Skills',
    target: 'skills',
    editor: null,
  },
  {
    key: 'interests',
    label: 'Interests',
    target: 'career-goals',
    editor: 'interests',
  },
  {
    key: 'education',
    label: 'Education',
    target: 'education',
    editor: null,
  },
  {
    key: 'experience',
    label: 'Experience',
    target: 'experience',
    editor: null,
  },
  {
    key: 'projects',
    label: 'Projects',
    target: 'projects',
    editor: null,
  },
  {
    key: 'career-goals',
    label: 'Career Goals',
    target: 'career-goals',
    editor: 'career-goals',
  },
  {
    key: 'personality',
    label: 'Personality',
    target: 'career-goals',
    editor: 'personality',
  },
]


const editorSectionMap = {
  'career-goals': 'career-goals',
  interests: 'interests',
  personality: 'personality',
}


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


function normalizeProfileResponse(responseData) {
  const profileData =
    responseData?.data?.profile

  if (!profileData) {
    return createEmptyProfile()
  }

  return {
    skills:
      Array.isArray(profileData.skills)
        ? profileData.skills
        : [],

    interests:
      Array.isArray(profileData.interests)
        ? profileData.interests
        : [],

    education:
      Array.isArray(profileData.education)
        ? profileData.education
        : [],

    experience:
      Array.isArray(profileData.experience)
        ? profileData.experience
        : [],

    projects:
      Array.isArray(profileData.projects)
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
        profileData.personality_responses,
      )
        ? profileData.personality_responses
        : [],
  }
}


function buildProfilePayload(profile) {
  return {
    skills:
      profile.skills.map((skill) => ({
        ...(skill.id
          ? {
              id: skill.id,
            }
          : {
              name: skill.name,
            }),

        proficiency_level:
          skill.proficiency_level,
      })),

    interests:
      profile.interests.map(
        (interest) => ({
          ...(interest.id
            ? {
                id: interest.id,
              }
            : {
                name: interest.name,
              }),
        }),
      ),

    education:
      profile.education.map(
        (education) => ({
          ...(education.id
            ? {
                id: education.id,
              }
            : {}),

          institution_name:
            education.institution_name,

          qualification:
            education.qualification,

          field_of_study:
            education.field_of_study,

          start_date:
            education.start_date,

          end_date:
            education.end_date || null,

          description:
            education.description || '',
        }),
      ),

    experience:
      profile.experience.map(
        (experience) => ({
          ...(experience.id
            ? {
                id: experience.id,
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
              : experience.end_date || null,

          is_current:
            Boolean(
              experience.is_current,
            ),

          description:
            experience.description || '',
        }),
      ),

    projects:
      profile.projects.map(
        (project) => ({
          ...(project.id
            ? {
                id: project.id,
              }
            : {}),

          name:
            project.name,

          description:
            project.description || '',

          project_url:
            project.project_url || '',

          start_date:
            project.start_date,

          end_date:
            project.end_date || null,
        }),
      ),

    career_goals:
      profile.career_goals.map(
        (careerGoal) => ({
          ...(careerGoal.id
            ? {
                id: careerGoal.id,
              }
            : {}),

          ...(careerGoal.career_id
            ? {
                career_id:
                  careerGoal.career_id,
              }
            : {
                target_role:
                  careerGoal.target_role,
              }),

          description:
            careerGoal.description || '',

          is_primary:
            Boolean(
              careerGoal.is_primary,
            ),
        }),
      ),

    personality_responses:
      profile.personality_responses.map(
        (personalityResponse) => ({
          ...(personalityResponse.id
            ? {
                id:
                  personalityResponse.id,
              }
            : {}),

          question_key:
            personalityResponse.question_key,

          response_value:
            personalityResponse.response_value,
        }),
      ),
  }
}


function getFirstErrorMessage(value) {
  if (!value) {
    return ''
  }

  if (typeof value === 'string') {
    return value
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const message =
        getFirstErrorMessage(item)

      if (message) {
        return message
      }
    }

    return ''
  }

  if (typeof value === 'object') {
    for (
      const nestedValue
      of Object.values(value)
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
    requestError?.data?.error?.details

  return (
    getFirstErrorMessage(details) ||
    requestError?.message ||
    fallbackMessage
  )
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
    activeProfileEditor,
    setActiveProfileEditor,
  ] = useState(null)

  const [
    activeProfileSection,
    setActiveProfileSection,
  ] = useState('skills')

  const currentUser =
    getStoredUser()

  const accountName =
    currentUser?.first_name?.trim() ||
    'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()

  const primaryCareerGoalRecord =
    profile.career_goals.find(
      (careerGoal) =>
        careerGoal.is_primary,
    ) ||
    profile.career_goals[0]


  const primaryCareerGoal =
    primaryCareerGoalRecord
      ?.target_role ||
    'No target role'

  const answeredPersonalityCount =
    PROFILE_QUESTIONNAIRE.filter(
      (question) =>
        profile.personality_responses.some(
          (response) =>
            response.question_key ===
              question.key &&
            Boolean(
              response.response_value,
            ),
        ),
    ).length


  useEffect(() => {
    async function loadProfile() {
      try {
        setIsLoading(true)
        setLoadError('')

        const responseData =
          await getStudentProfile()

        const loadedProfile =
          normalizeProfileResponse(
            responseData,
          )

        setProfile(loadedProfile)
        setIsDirty(false)
      } catch (requestError) {
        if (
          requestError.status === 404
        ) {
          setLoadError(
            'Student profile not found for this account.',
          )
        } else {
          setLoadError(
            getRequestErrorMessage(
              requestError,
              'Unable to load the Student Profile.',
            ),
          )
        }
      } finally {
        setIsLoading(false)
      }
    }


    loadProfile()
  }, [])


  useEffect(() => {
    const trackedSections = [
      'skills',
      'education',
      'experience',
      'projects',
      'career-goals',
    ]


    function updateActiveSection() {
      let nextSection = 'skills'

      for (
        const sectionId
        of trackedSections
      ) {
        const element =
          document.getElementById(
            sectionId,
          )

        if (!element) {
          continue
        }

        const sectionTop =
          element
            .getBoundingClientRect()
            .top

        if (sectionTop <= 180) {
          nextSection =
            sectionId
        }
      }


      if (
        nextSection ===
          'career-goals' &&
        activeProfileEditor
      ) {
        nextSection =
          editorSectionMap[
            activeProfileEditor
          ] || 'career-goals'
      }


      setActiveProfileSection(
        (currentSection) =>
          currentSection ===
          nextSection
            ? currentSection
            : nextSection,
      )
    }


    window.addEventListener(
      'scroll',
      updateActiveSection,
      {
        passive: true,
      },
    )

    updateActiveSection()


    return () => {
      window.removeEventListener(
        'scroll',
        updateActiveSection,
      )
    }
  }, [activeProfileEditor])


  function handleSectionChange(
    sectionName,
    nextItems,
  ) {
    setProfile(
      (currentProfile) => ({
        ...currentProfile,

        [sectionName]:
          nextItems,
      }),
    )

    setIsDirty(true)
    setSaveMessage('')
    setSaveError('')
  }


  function scrollToProfileSection(
    targetId,
  ) {
    const targetElement =
      document.getElementById(
        targetId,
      )

    if (!targetElement) {
      return
    }

    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }


  function handleProfileSectionNavigation(
    section,
  ) {
    setActiveProfileSection(
      section.key,
    )

    setActiveProfileEditor(
      section.editor,
    )

    window.requestAnimationFrame(
      () => {
        scrollToProfileSection(
          section.target,
        )
      },
    )
  }


  function toggleProfileEditor(
    editorName,
  ) {
    const nextEditor =
      activeProfileEditor ===
      editorName
        ? null
        : editorName

    setActiveProfileEditor(
      nextEditor,
    )

    setActiveProfileSection(
      nextEditor
        ? editorSectionMap[
            nextEditor
          ]
        : 'career-goals',
    )
  }


  function closeProfileEditor() {
    setActiveProfileEditor(null)

    setActiveProfileSection(
      'career-goals',
    )
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

      setProfile(savedProfile)
      setIsDirty(false)

      setSaveMessage(
        'Profile saved successfully.',
      )
    } catch (requestError) {
      setSaveError(
        getRequestErrorMessage(
          requestError,
          'Unable to save the Student Profile.',
        ),
      )
    } finally {
      setIsSaving(false)
    }
  }


  if (isLoading) {
    return (
      <main className="student-profile-page">
        <div className="profile-state-card">
          <p>
            Loading Student Profile...
          </p>
        </div>
      </main>
    )
  }


  if (loadError) {
    return (
      <main className="student-profile-page">
        <header className="student-profile-heading">
          <div>
            <h1>
              Student Profile
            </h1>
          </div>
        </header>

        <div className="profile-state-card">
          <p role="alert">
            {loadError}
          </p>
        </div>
      </main>
    )
  }


  return (
    <main className="student-profile-page">
      <header className="student-profile-heading">
        <div className="student-profile-heading__copy">
          <h1>
            Student Profile
          </h1>

          <p>
            Manage information GradNavi uses
            for recommendations, readiness
            analysis, and AI-assisted
            application drafts.
          </p>
        </div>

        <div
          className="student-profile-account-pill"
          aria-label={
            `Signed in as ${accountName}`
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


      <nav
        className="profile-section-navigation"
        aria-label="Student Profile sections"
      >
        <div className="profile-section-navigation__heading">
          <h2>
            Profile Sections
          </h2>
        </div>

        <div className="profile-section-navigation__scroller">
          <div className="profile-section-navigation__items">
            {profileSections.map(
              (section) => {
                const isActive =
                  activeProfileSection ===
                  section.key

                return (
                  <button
                    key={section.key}
                    className={[
                      'profile-section-navigation__item',
                      isActive
                        ? 'profile-section-navigation__item--active'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    type="button"
                    aria-current={
                      isActive
                        ? 'location'
                        : undefined
                    }
                    onClick={() =>
                      handleProfileSectionNavigation(
                        section,
                      )
                    }
                  >
                    {section.label}
                  </button>
                )
              },
            )}
          </div>
        </div>
      </nav>


      <div className="profile-content-stack">
        <SkillsSection
          items={profile.skills}
          onChange={(nextItems) =>
            handleSectionChange(
              'skills',
              nextItems,
            )
          }
        />


        <section
          className="profile-section profile-section--evidence profile-section--standalone-evidence"
        >
          <EducationSection
            items={profile.education}
            onChange={(nextItems) =>
              handleSectionChange(
                'education',
                nextItems,
              )
            }
          />
        </section>


        <section
          className="profile-section profile-section--evidence profile-section--standalone-evidence"
        >
          <ExperienceSection
            items={profile.experience}
            onChange={(nextItems) =>
              handleSectionChange(
                'experience',
                nextItems,
              )
            }
          />
        </section>


        <section
          className="profile-section profile-section--evidence profile-section--standalone-evidence"
        >
          <ProjectSection
            items={profile.projects}
            onChange={(nextItems) =>
              handleSectionChange(
                'projects',
                nextItems,
              )
            }
          />
        </section>
      </div>


      <section
        id="career-goals"
        className="profile-goals-card"
        aria-labelledby="profile-goals-heading"
      >
        <div className="profile-card-heading">
          <h2 id="profile-goals-heading">
            Career Goals and Interests
          </h2>

          <p>
            Career Goals use active GradNavi
            Career records. Choose one primary
            goal for your profile.
          </p>
        </div>


        <div className="profile-goals-summary-grid">
          <button
            className="profile-summary-card"
            type="button"
            aria-expanded={
              activeProfileEditor ===
              'career-goals'
            }
            onClick={() =>
              toggleProfileEditor(
                'career-goals',
              )
            }
          >
            <span className="profile-summary-card__label">
              Career Goals
            </span>

            <strong>
              {primaryCareerGoal}
            </strong>

            <span className="profile-summary-card__meta">
              {
                profile.career_goals
                  .length
              }{' '}
              {
                profile.career_goals
                  .length === 1
                  ? 'goal'
                  : 'goals'
              }{' '}
              saved
            </span>

            <span className="profile-summary-card__manage">
              Manage
            </span>
          </button>


          <button
            className="profile-summary-card"
            type="button"
            aria-expanded={
              activeProfileEditor ===
              'interests'
            }
            onClick={() =>
              toggleProfileEditor(
                'interests',
              )
            }
          >
            <span className="profile-summary-card__label">
              Interests
            </span>

            <strong>
              reference data
            </strong>

            <span className="profile-summary-card__meta">
              {
                profile.interests.length
              }{' '}
              linked to profile
            </span>

            <span className="profile-summary-card__manage">
              Manage
            </span>
          </button>


          <button
            className="profile-summary-card"
            type="button"
            aria-expanded={
              activeProfileEditor ===
              'personality'
            }
            onClick={() =>
              toggleProfileEditor(
                'personality',
              )
            }
          >
            <span className="profile-summary-card__label">
              Personality
            </span>

            <strong>
              responses
            </strong>

            <span className="profile-summary-card__meta">
              {
                answeredPersonalityCount
              }
              {' of '}
              {
                PROFILE_QUESTIONNAIRE.length
              }
              {' answered'}
            </span>

            <span className="profile-summary-card__manage">
              Manage
            </span>
          </button>


          <div className="profile-goals-save-column">
            <button
              className="profile-save-button"
              type="button"
              onClick={
                handleSaveProfile
              }
              disabled={
                !isDirty ||
                isSaving
              }
            >
              {
                isSaving
                  ? 'Saving Profile...'
                  : 'Save Profile'
              }
            </button>
          </div>
        </div>


        <div
          className="profile-save-status"
          aria-live="polite"
        >
          {isDirty && (
            <p className="profile-unsaved-message">
              You have unsaved profile
              changes.
            </p>
          )}

          {saveError && (
            <p
              className="profile-error-message"
              role="alert"
            >
              {saveError}
            </p>
          )}

          {saveMessage && (
            <p className="profile-success-message">
              {saveMessage}
            </p>
          )}
        </div>


        {activeProfileEditor && (
          <div className="profile-goals-editor">
            {
              activeProfileEditor ===
                'career-goals' && (
                <CareerGoalsSection
                  items={
                    profile.career_goals
                  }
                  onChange={(nextItems) =>
                    handleSectionChange(
                      'career_goals',
                      nextItems,
                    )
                  }
                  onClose={
                    closeProfileEditor
                  }
                />
              )
            }


            {
              activeProfileEditor ===
                'interests' && (
                <InterestsSection
                  items={
                    profile.interests
                  }
                  onChange={(nextItems) =>
                    handleSectionChange(
                      'interests',
                      nextItems,
                    )
                  }
                  onClose={
                    closeProfileEditor
                  }
                />
              )
            }


            {
              activeProfileEditor ===
                'personality' && (
                <PersonalityResponsesSection
                  items={
                    profile
                      .personality_responses
                  }
                  onChange={(nextItems) =>
                    handleSectionChange(
                      'personality_responses',
                      nextItems,
                    )
                  }
                  onClose={
                    closeProfileEditor
                  }
                />
              )
            }
          </div>
        )}
      </section>
    </main>
  )
}


export default StudentProfilePage