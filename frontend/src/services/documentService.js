import apiRequest from './apiClient'


const RESUME_FOCUS_OPTIONS = [
  {
    value: 'balanced',
    label: 'Balanced',
  },
  {
    value: 'technical_skills',
    label: 'Technical Skills',
  },
  {
    value: 'professional_experience',
    label: 'Professional Experience',
  },
  {
    value: 'projects',
    label: 'Projects',
  },
  {
    value: 'transferable_skills',
    label: 'Transferable Skills',
  },
]


const COVER_LETTER_TONE_OPTIONS = [
  {
    value: 'professional',
    label: 'Professional',
  },
  {
    value: 'warm',
    label: 'Warm',
  },
  {
    value: 'technical',
    label: 'Technical',
  },
  {
    value: 'concise',
    label: 'Concise',
  },
]


const COVER_LETTER_FOCUS_OPTIONS = [
  {
    value: 'balanced',
    label: 'Balanced',
  },
  {
    value: 'skills_match',
    label: 'Skills Match',
  },
  {
    value: 'experience',
    label: 'Experience',
  },
  {
    value: 'projects',
    label: 'Projects',
  },
  {
    value: 'career_transition',
    label: 'Career Transition',
  },
]


function normalizeRequiredCareerId(
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


async function generateResumeDraft({
  targetCareerId,
  resumeFocus = 'balanced',
  jobDescription = '',
} = {}) {
  const body = {
    target_career_id:
      normalizeRequiredCareerId(
        targetCareerId,
      ),
    resume_focus:
      normalizeText(
        resumeFocus,
      )
      || 'balanced',
  }

  const normalizedJobDescription =
    normalizeText(
      jobDescription,
    )

  if (normalizedJobDescription) {
    body.job_description =
      normalizedJobDescription
  }

  return apiRequest(
    '/documents/resume/generate/',
    {
      method: 'POST',
      requiresAuth: true,
      body,
    },
  )
}


async function generateCoverLetterDraft({
  targetCareerId,
  tone = 'professional',
  coverLetterFocus = 'balanced',
  jobTitle,
  company,
  jobDescription,
} = {}) {
  return apiRequest(
    '/documents/cover-letter/generate/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        target_career_id:
          normalizeRequiredCareerId(
            targetCareerId,
          ),
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
          normalizeText(
            jobTitle,
          ),
        company:
          normalizeText(
            company,
          ),
        job_description:
          normalizeText(
            jobDescription,
          ),
      },
    },
  )
}


export {
  COVER_LETTER_FOCUS_OPTIONS,
  COVER_LETTER_TONE_OPTIONS,
  RESUME_FOCUS_OPTIONS,
  generateCoverLetterDraft,
  generateResumeDraft,
}
