import apiRequest from './apiClient'


async function generateResumeDraft() {
  return apiRequest(
    '/documents/resume/generate/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {},
    },
  )
}


async function generateCoverLetterDraft(
  jobDescription,
) {
  return apiRequest(
    '/documents/cover-letter/generate/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        job_description:
          jobDescription,
      },
    },
  )
}


export {
  generateCoverLetterDraft,
  generateResumeDraft,
}