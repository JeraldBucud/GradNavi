import apiRequest from './apiClient'


async function generateInterviewQuestions({
  targetRole,
  jobDescription,
  questionCount,
}) {
  const body = {
    target_role: targetRole,
    question_count: questionCount,
  }

  if (jobDescription) {
    body.job_description = jobDescription
  }

  const response = await apiRequest('/interviews/questions/', {
    method: 'POST',
    body,
    requiresAuth: true,
  })

  return response.data
}


async function generateInterviewFeedback({
  targetRole,
  question,
  studentAnswer,
}) {
  const response = await apiRequest('/interviews/feedback/', {
    method: 'POST',
    body: {
      target_role: targetRole,
      question,
      student_answer: studentAnswer,
    },
    requiresAuth: true,
  })

  return response.data
}


export {
  generateInterviewQuestions,
  generateInterviewFeedback,
}