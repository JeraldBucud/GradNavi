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

  return apiRequest('/interviews/questions/', {
    method: 'POST',
    body,
    requiresAuth: true,
  })
}


async function generateInterviewFeedback({
  targetRole,
  question,
  studentAnswer,
}) {
  return apiRequest('/interviews/feedback/', {
    method: 'POST',
    body: {
      target_role: targetRole,
      question,
      student_answer: studentAnswer,
    },
    requiresAuth: true,
  })
}


export {
  generateInterviewQuestions,
  generateInterviewFeedback,
}