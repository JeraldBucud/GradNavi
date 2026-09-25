import { useState } from 'react'

import { generateInterviewQuestions } from '../services/interviewService'

import './CareerGuidancePage.css'
import './InterviewPreparationPage.css'


const DEFAULT_QUESTION_COUNT = 5


function InterviewPreparationPage() {
  const [targetRole, setTargetRole] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [questionCount, setQuestionCount] = useState(
    DEFAULT_QUESTION_COUNT,
  )

  const [questionSet, setQuestionSet] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')


  async function handleGenerateQuestions() {
    if (!targetRole.trim()) {
      setErrorMessage('Enter a target role first.')

      return
    }

    setIsLoading(true)
    setErrorMessage('')

    try {
      const result = await generateInterviewQuestions({
        targetRole: targetRole.trim(),
        jobDescription: jobDescription.trim(),
        questionCount,
      })

      setQuestionSet(result)
    }
    catch (error) {
      setErrorMessage(
        error.message
        || 'Could not generate questions. Please try again.',
      )
    }
    finally {
      setIsLoading(false)
    }
  }


  function handleClearContext() {
    setTargetRole('')
    setJobDescription('')
    setQuestionCount(DEFAULT_QUESTION_COUNT)
    setQuestionSet(null)
    setErrorMessage('')
  }


  return (
    <div className="career-guidance-page interview-prep">
      <div className="career-guidance-heading">
        <div className="career-guidance-heading__copy">
          <h1>Interview Preparation</h1>
          <p>
            Practise interview questions for your target role
            and get feedback on your answers.
          </p>
        </div>
      </div>

      <section className="interview-prep__section">
        <h2 className="interview-prep__section-heading">
          Interview Setup
        </h2>
        <p className="interview-prep__muted">
          Choose a target role and optional job description.
          GradNavi will generate a focused set of practice
          questions.
        </p>

        <div className="interview-prep__setup-grid">
          <label className="interview-prep__field">
            <span>Target role</span>
            <input
              type="text"
              value={targetRole}
              placeholder="e.g. Software Developer"
              onChange={(event) => {
                setTargetRole(event.target.value)
              }}
            />
          </label>

          <label className="interview-prep__field">
            <span>Question count</span>
            <select
              value={questionCount}
              onChange={(event) => {
                setQuestionCount(
                  Number(event.target.value),
                )
              }}
            >
              {[3, 5, 8, 10].map((count) => (
                <option key={count} value={count}>
                  {count} questions
                </option>
              ))}
            </select>
          </label>

          <label className="interview-prep__field interview-prep__field--wide">
            <span>Job description (optional)</span>
            <textarea
              rows={5}
              value={jobDescription}
              placeholder="Paste a job description if you want questions tailored to a specific role."
              onChange={(event) => {
                setJobDescription(event.target.value)
              }}
            />
          </label>
        </div>

        <div className="interview-prep__button-row">
          <button
            type="button"
            className="interview-prep__button interview-prep__button--primary"
            disabled={isLoading}
            onClick={handleGenerateQuestions}
          >
            {isLoading
              ? 'Generating…'
              : 'Generate Practice Questions'}
          </button>

          <button
            type="button"
            className="interview-prep__button"
            onClick={handleClearContext}
          >
            Clear Context
          </button>
        </div>

        {errorMessage && (
          <p className="interview-prep__error">
            {errorMessage}
          </p>
        )}
      </section>

      {questionSet && (
        <section className="interview-prep__section">
          <h2 className="interview-prep__section-heading">
            Generated Questions
          </h2>
          <p className="interview-prep__muted">
            These are AI-generated practice questions, not
            questions from a real employer.
          </p>

          <table className="interview-prep__table">
            <thead>
              <tr>
                <th>#</th>
                <th>Question</th>
                <th>Focus area</th>
              </tr>
            </thead>
            <tbody>
              {questionSet.questions.map((item, index) => (
                <tr key={item.question}>
                  <td>{index + 1}</td>
                  <td>{item.question}</td>
                  <td>{item.focus_area}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}


export default InterviewPreparationPage