import { useEffect, useState } from 'react'

import EducationSection from '../components/profile/EducationSection'
import ExperienceSection from '../components/profile/ExperienceSection'
import ProjectSection from '../components/profile/ProjectSection'
import CareerGoalsSection from '../components/profile/CareerGoalsSection'
import SkillsSection from '../components/profile/SkillsSection'
import InterestsSection from '../components/profile/InterestsSection'
import PersonalityResponsesSection from '../components/profile/PersonalityResponsesSection'
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

function normalizeProfileResponse(responseData) {
  const profileData = responseData?.data?.profile

  if (!profileData) {
    return createEmptyProfile()
  }

  return {
    skills: Array.isArray(profileData.skills)
      ? profileData.skills
      : [],
    interests: Array.isArray(profileData.interests)
      ? profileData.interests
      : [],
    education: Array.isArray(profileData.education)
      ? profileData.education
      : [],
    experience: Array.isArray(profileData.experience)
      ? profileData.experience
      : [],
    projects: Array.isArray(profileData.projects)
      ? profileData.projects
      : [],
    career_goals: Array.isArray(profileData.career_goals)
      ? profileData.career_goals
      : [],
    personality_responses: Array.isArray(
      profileData.personality_responses,
    )
      ? profileData.personality_responses
      : [],
  }
}

function buildProfilePayload(profile) {
  return {
    skills: profile.skills.map((skill) => ({
      ...(skill.id ? { id: skill.id } : { name: skill.name }),
      proficiency_level: skill.proficiency_level,
    })),

    interests: profile.interests.map((interest) => ({
      ...(interest.id
        ? { id: interest.id }
        : { name: interest.name }),
    })),

    education: profile.education.map((education) => ({
      ...(education.id ? { id: education.id } : {}),
      institution_name: education.institution_name,
      qualification: education.qualification,
      field_of_study: education.field_of_study,
      start_date: education.start_date,
      end_date: education.end_date || null,
      description: education.description || '',
    })),

    experience: profile.experience.map((experience) => ({
      ...(experience.id ? { id: experience.id } : {}),
      job_title: experience.job_title,
      company: experience.company,
      start_date: experience.start_date,
      end_date: experience.is_current
        ? null
        : experience.end_date || null,
      is_current: Boolean(experience.is_current),
      description: experience.description || '',
    })),

    projects: profile.projects.map((project) => ({
      ...(project.id ? { id: project.id } : {}),
      name: project.name,
      description: project.description || '',
      project_url: project.project_url || '',
      start_date: project.start_date,
      end_date: project.end_date || null,
    })),

    career_goals: profile.career_goals.map((careerGoal) => ({
      ...(careerGoal.id ? { id: careerGoal.id } : {}),
      target_role: careerGoal.target_role,
      description: careerGoal.description || '',
    })),

    personality_responses: profile.personality_responses.map(
      (personalityResponse) => ({
        ...(personalityResponse.id
          ? { id: personalityResponse.id }
          : {}),
        question_key: personalityResponse.question_key,
        response_value: personalityResponse.response_value,
      }),
    ),
  }
}

function StudentProfilePage() {
  const [profile, setProfile] = useState(createEmptyProfile)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isDirty, setIsDirty] = useState(false)
  const [loadError, setLoadError] = useState('')
  const [saveError, setSaveError] = useState('')
  const [saveMessage, setSaveMessage] = useState('')

  useEffect(() => {
    async function loadProfile() {
      try {
        setIsLoading(true)
        setLoadError('')

        const responseData = await getStudentProfile()
        const loadedProfile = normalizeProfileResponse(responseData)

        setProfile(loadedProfile)
        setIsDirty(false)
      } catch (requestError) {
        if (requestError.status === 404) {
          setLoadError(
            'Student profile not found for this account.',
          )
        } else {
          setLoadError(
            requestError.message ||
              'Unable to load the Student Profile.',
          )
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadProfile()
  }, [])

  function handleSectionChange(sectionName, nextItems) {
    setProfile((currentProfile) => ({
      ...currentProfile,
      [sectionName]: nextItems,
    }))

    setIsDirty(true)
    setSaveMessage('')
    setSaveError('')
  }

  async function handleSaveProfile() {
    try {
      setIsSaving(true)
      setSaveError('')
      setSaveMessage('')

      const profilePayload = buildProfilePayload(profile)
      const responseData =
        await updateStudentProfile(profilePayload)

      const savedProfile =
        normalizeProfileResponse(responseData)

      setProfile(savedProfile)
      setIsDirty(false)
      setSaveMessage('Profile saved successfully.')
    } catch (requestError) {
      setSaveError(
        requestError.message ||
          'Unable to save the Student Profile.',
      )
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <main className="profile-page">
        <p>Loading Student Profile...</p>
      </main>
    )
  }

  if (loadError) {
    return (
      <main className="profile-page">
        <div className="profile-header">
          <h1>Student Profile</h1>
        </div>

        <p role="alert">{loadError}</p>
      </main>
    )
  }

  return (
    <main className="profile-page">
      <div className="profile-header">
        <h1>Student Profile</h1>

        <p>
          Manage the information GradNavi uses for career
          recommendations, readiness analysis, and future
          application support.
        </p>
      </div>

      <SkillsSection
        items={profile.skills}
        onChange={(nextItems) =>
          handleSectionChange('skills', nextItems)
        }
      />

      <InterestsSection
        items={profile.interests}
        onChange={(nextItems) =>
          handleSectionChange('interests', nextItems)
        }
      />

      <EducationSection
        items={profile.education}
        onChange={(nextItems) =>
          handleSectionChange('education', nextItems)
        }
      />

      <ExperienceSection
        items={profile.experience}
        onChange={(nextItems) =>
          handleSectionChange('experience', nextItems)
        }
      />

      <ProjectSection
        items={profile.projects}
        onChange={(nextItems) =>
          handleSectionChange('projects', nextItems)
        }
      />

      <CareerGoalsSection
        items={profile.career_goals}
        onChange={(nextItems) =>
          handleSectionChange('career_goals', nextItems)
        }
      />

      <PersonalityResponsesSection
        items={profile.personality_responses}
        onChange={(nextItems) =>
          handleSectionChange(
            'personality_responses',
            nextItems,
          )
        }
      />

      <section className="profile-save-section">
        {isDirty && (
          <p>You have unsaved profile changes.</p>
        )}

        {saveError && (
          <p role="alert">{saveError}</p>
        )}

        {saveMessage && (
          <p role="status">{saveMessage}</p>
        )}

        <button
          type="button"
          onClick={handleSaveProfile}
          disabled={!isDirty || isSaving}
        >
          {isSaving ? 'Saving Profile...' : 'Save Profile'}
        </button>
      </section>
    </main>
  )
}

export default StudentProfilePage