import apiRequest from './apiClient'


const JOB_DESCRIPTION_MAX_LENGTH = 20_000


function normalizeJobDescription(
  value,
) {
  return String(
    value ?? '',
  ).trim()
}


async function matchJobDescription({
  jobDescription,
} = {}) {
  return apiRequest(
    '/careers/job-match/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        job_description:
          normalizeJobDescription(
            jobDescription,
          ),
      },
    },
  )
}


export {
  JOB_DESCRIPTION_MAX_LENGTH,
  matchJobDescription,
}
