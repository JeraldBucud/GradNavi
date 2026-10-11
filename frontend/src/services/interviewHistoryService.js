import apiRequest from './apiClient'


async function getInterviewHistory() {
  return apiRequest(
    '/interviews/history/',
    {
      requiresAuth: true,
    },
  )
}


async function createInterviewHistorySession({
  targetRole,
  totalQuestions,
  questionsWithFeedback,
}) {
  return apiRequest(
    '/interviews/history/',
    {
      method: 'POST',
      requiresAuth: true,
      body: {
        target_role: targetRole,
        total_questions: totalQuestions,
        questions_with_feedback:
          questionsWithFeedback,
      },
    },
  )
}


export {
  createInterviewHistorySession,
  getInterviewHistory,
}
