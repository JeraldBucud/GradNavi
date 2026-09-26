import { useState } from 'react'

import { generateInterviewFeedback } from '../../services/interviewService'

import './InterviewPractice.css'


function InterviewPractice({
  targetRole,
  questions,
  onEndPractice,
}) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [feedbackByQuestion, setFeedbackByQuestion] = useState({})
  const [isFeedbackLoading, setIsFeedbackLoading] = useState(false)
  const [feedbackError, setFeedbackError] = useState('')

  const currentQuestion = questions[currentIndex]
  const currentAnswer = answers[currentIndex] || ''
  const currentFeedback = feedbackByQuestion[currentIndex]
  const completedCount = Object.keys(feedbackByQuestion).length
  const isLastQuestion = currentIndex === questions.length - 1


  function getQuestionStatus(index) {
    if (index === currentIndex) {
      return 'Current'
    }

    if (feedbackByQuestion[index]) {
      return 'Completed'
    }

    return 'Not started'
  }


  function selectQuestion(index) {
    setCurrentIndex(index)
    setFeedbackError('')
  }


  function handleAnswerChange(event) {
    setAnswers({
      ...answers,
      [currentIndex]: event.target.value,
    })
  }


  async function handleGetFeedback() {
    if (!currentAnswer.trim()) {
      setFeedbackError('Write an answer before requesting feedback.')

      return
    }

    setIsFeedbackLoading(true)
    setFeedbackError('')

    try {
      const result = await generateInterviewFeedback({
        targetRole,
        question: currentQuestion.question,
        studentAnswer: currentAnswer.trim(),
      })

      setFeedbackByQuestion({
        ...feedbackByQuestion,
        [currentIndex]: result,
      })
    }
    catch (error) {
      setFeedbackError(
        error.message
        || 'Could not get feedback. Please try again.',
      )
    }
    finally {
      setIsFeedbackLoading(false)
    }
  }


  return (
    <div className="interview-practice">
      <section className="interview-practice__summary">
        <div className="interview-practice__summary-item">
          <span>Target role</span>
          <strong>{targetRole}</strong>
        </div>

        <div className="interview-practice__summary-item">
          <span>Progress</span>
          <strong>
            Question {currentIndex + 1} of {questions.length}
          </strong>
        </div>

        <div className="interview-practice__summary-item">
          <span>Current focus</span>
          <strong>{currentQuestion.focus_area}</strong>
        </div>

        <div className="interview-practice__progress">
          <span>Session progress</span>
          <div className="interview-practice__progress-track">
            <div
              className="interview-practice__progress-fill"
              style={{
                width: `${(completedCount / questions.length) * 100}%`,
              }}
            />
          </div>
          <small>
            {completedCount} of {questions.length} questions
            with feedback.
          </small>
        </div>
      </section>

      <h2 className="interview-prep__section-heading">
        Current Question
      </h2>
      <p className="interview-prep__muted">
        Use a real example where possible. Explain the situation,
        what you did, and what happened.
      </p>

      <div className="interview-practice__layout">
        <nav
          className="interview-practice__list"
          aria-label="Practice questions"
        >
          {questions.map((item, index) => (
            <button
              key={item.question}
              type="button"
              className={[
                'interview-practice__list-item',
                index === currentIndex
                  ? 'interview-practice__list-item--current'
                  : '',
              ]
                .filter(Boolean)
                .join(' ')}
              onClick={() => selectQuestion(index)}
            >
              <span className="interview-practice__number">
                #{index + 1}
              </span>
              <span>{getQuestionStatus(index)}</span>
            </button>
          ))}
        </nav>

        <section className="interview-practice__question-card">
          <span className="interview-practice__badge">
            AI-generated question
          </span>

          <h3>{currentQuestion.question}</h3>

          <label className="interview-prep__field interview-prep__field--wide">
            <span>
              {currentFeedback ? 'Revised answer' : 'Your answer'}
            </span>
            <textarea
              rows={6}
              value={currentAnswer}
              onChange={handleAnswerChange}
              placeholder="Write your response as if you were answering the interviewer. Include the situation, your action, and the result where possible."
            />
          </label>

          {feedbackError && (
            <p className="interview-prep__error" role="alert">
              {feedbackError}
            </p>
          )}

          <div className="interview-prep__button-row">
            <button
              type="button"
              className="interview-prep__button interview-prep__button--primary"
              onClick={handleGetFeedback}
              disabled={isFeedbackLoading}
            >
              {isFeedbackLoading && 'Getting feedback…'}
              {!isFeedbackLoading && feedbackError && 'Try Again'}
              {!isFeedbackLoading && !feedbackError && (
                currentFeedback
                  ? 'Get Updated Feedback'
                  : 'Get Feedback'
              )}
            </button>

            {!isLastQuestion && (
              <button
                type="button"
                className="interview-prep__button"
                onClick={() => selectQuestion(currentIndex + 1)}
                disabled={isFeedbackLoading}
              >
                Next Question
              </button>
            )}

            <button
              type="button"
              className="interview-prep__button"
              onClick={onEndPractice}
              disabled={isFeedbackLoading}
            >
              End Practice
            </button>
          </div>
        </section>
      </div>

      {currentFeedback && (
        <section
          className="interview-practice__feedback"
          aria-live="polite"
        >
          <div className="interview-practice__feedback-summary">
            <span className="interview-practice__badge">
              AI feedback
            </span>
            <h3>{currentFeedback.feedback_summary}</h3>
            <p className="interview-prep__muted">
              Use this feedback to improve your next response.
              GradNavi does not make hiring decisions or assign
              pass/fail outcomes.
            </p>
          </div>

          <div className="interview-practice__feedback-grid">
            <div className="interview-practice__feedback-card interview-practice__feedback-card--good">
              <h4>What you did well</h4>
              <ul>
                {currentFeedback.strengths.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="interview-practice__feedback-card interview-practice__feedback-card--improve">
              <h4>What to improve</h4>
              <ul>
                {currentFeedback.improvements.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="interview-practice__feedback-card interview-practice__feedback-card--grounded">
              <h4>Keep grounded</h4>
              <ul>
                <li>Use only real experience</li>
                <li>Do not invent achievements</li>
                <li>Review AI wording before using</li>
              </ul>
            </div>
          </div>

          <div className="interview-practice__example">
            <h4>Example approach</h4>
            <p>{currentFeedback.suggested_response}</p>
          </div>

          {currentFeedback.limitations?.length > 0 && (
            <p className="interview-prep__muted">
              {currentFeedback.limitations.join(' ')}
            </p>
          )}
        </section>
      )}
    </div>
  )
}


export default InterviewPractice