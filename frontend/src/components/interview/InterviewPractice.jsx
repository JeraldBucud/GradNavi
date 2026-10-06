import {
  useEffect,
  useState,
} from 'react'

import {
  getActiveInterviewSession,
  patchActiveInterviewSession,
} from '../../services/interviewSessionStorage'

import { generateInterviewFeedback } from '../../services/interviewService'

import './InterviewPractice.css'


const SUMMARY_ITEM_LIMIT = 5


function collectUniqueItems(feedbackList, key) {
  const items = new Set()

  feedbackList.forEach((feedback) => {
    (feedback[key] || []).forEach((item) => items.add(item))
  })

  return Array.from(items).slice(0, SUMMARY_ITEM_LIMIT)
}


const FEEDBACK_VALIDATION_ERROR_CODE =
  'ai_response_invalid'


function getFeedbackErrorMessage(error) {
  const errorCode =
    error?.data?.error?.code

  if (
    errorCode ===
    FEEDBACK_VALIDATION_ERROR_CODE
  ) {
    return (
      "GradNavi couldn't validate the generated feedback. "
      + "Your answer is still here. "
      + "Try generating the feedback again."
    )
  }

  return (
    error?.message
    || 'Could not get feedback. Please try again.'
  )
}


function InterviewPractice({
  targetRole,
  questions,
  isFinishingSession = false,
  finishSessionError = '',
  onEndPractice,
}) {
  const [
    restoredPractice,
  ] = useState(
    () =>
      getActiveInterviewSession()
        ?.practice
      || {},
  )

  const [
    currentIndex,
    setCurrentIndex,
  ] = useState(
    () => {
      const restoredIndex =
        Number(
          restoredPractice
            ?.currentIndex,
        )

      if (
        Number.isInteger(
          restoredIndex,
        )
        && restoredIndex >= 0
        && restoredIndex
          < questions.length
      ) {
        return restoredIndex
      }

      return 0
    },
  )

  const [
    answers,
    setAnswers,
  ] = useState(
    () =>
      (
        restoredPractice
          ?.answers
        && typeof (
          restoredPractice.answers
        ) === 'object'
      )
        ? restoredPractice.answers
        : {},
  )

  const [
    feedbackByQuestion,
    setFeedbackByQuestion,
  ] = useState(
    () =>
      (
        restoredPractice
          ?.feedbackByQuestion
        && typeof (
          restoredPractice
            .feedbackByQuestion
        ) === 'object'
      )
        ? restoredPractice
            .feedbackByQuestion
        : {},
  )

  const [
    isFeedbackLoading,
    setIsFeedbackLoading,
  ] = useState(false)

  const [
    feedbackError,
    setFeedbackError,
  ] = useState('')

  const [
    isSummaryVisible,
    setIsSummaryVisible,
  ] = useState(
    () =>
      Boolean(
        restoredPractice
          ?.isSummaryVisible,
      ),
  )

  const [
    activeFeedbackTab,
    setActiveFeedbackTab,
  ] = useState('strengths')

  const [
    isExampleExpanded,
    setIsExampleExpanded,
  ] = useState(false)

  const currentQuestion = questions[currentIndex]
  const currentAnswer = answers[currentIndex] || ''
  const currentFeedback = feedbackByQuestion[currentIndex]
  const completedCount = Object.keys(feedbackByQuestion).length
  const isLastQuestion = currentIndex === questions.length - 1


  useEffect(
    () => {
      patchActiveInterviewSession({
        practice: {
          currentIndex,
          answers,
          feedbackByQuestion,
          isSummaryVisible,
        },
      })
    },
    [
      answers,
      currentIndex,
      feedbackByQuestion,
      isSummaryVisible,
    ],
  )


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
    setActiveFeedbackTab('strengths')
    setIsExampleExpanded(false)
  }


  function handleAnswerChange(event) {
    setAnswers({
      ...answers,
      [currentIndex]: event.target.value,
    })
  }


  function showSummary() {
    setFeedbackError('')
    setActiveFeedbackTab('strengths')
    setIsExampleExpanded(false)
    setIsSummaryVisible(true)
  }


  function returnToPractice() {
    setIsSummaryVisible(false)
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

      setIsExampleExpanded(false)
    }
    catch (error) {
      setFeedbackError(
        getFeedbackErrorMessage(
          error,
        ),
      )
    }
    finally {
      setIsFeedbackLoading(false)
    }
  }


  if (isSummaryVisible) {
    const reviewedQuestions = questions
      .map((item, index) => ({
        index,
        question: item.question,
        feedback: feedbackByQuestion[index],
      }))
      .filter((item) => item.feedback)

    const feedbackList = reviewedQuestions.map((item) => item.feedback)
    const strengths = collectUniqueItems(feedbackList, 'strengths')
    const improvements = collectUniqueItems(feedbackList, 'improvements')

    return (
      <div className="interview-practice">
        <section className="interview-practice__feedback">
          <div className="interview-practice__feedback-summary interview-practice__feedback-summary--compact interview-practice__feedback-summary--session">
            <span className="interview-practice__badge">
              Session summary
            </span>
            <h3>
              {completedCount === 0
                ? 'Practice ended without feedback.'
                : `You received feedback on ${completedCount} of ${questions.length} questions.`}
            </h3>
            <p className="interview-prep__muted">
              Target career: {targetRole}. Use this summary to plan
              your next practice session. GradNavi does not make
              hiring decisions or assign pass/fail outcomes.
            </p>
          </div>

          {completedCount > 0 && (
            <>
              <h2 className="interview-prep__section-heading">
                Session feedback
              </h2>
              <p className="interview-prep__muted">
                Review the main strengths, improvements, and
                reminders from this practice session.
              </p>

              <div className="interview-practice__feedback-tabs interview-practice__summary-feedback-tabs">
                <nav
                  className="interview-practice__feedback-nav"
                  aria-label="Session feedback sections"
                  role="tablist"
                >
                  <button
                    type="button"
                    id="summary-feedback-tab-strengths"
                    role="tab"
                    aria-selected={
                      activeFeedbackTab === 'strengths'
                    }
                    aria-controls="summary-feedback-panel"
                    className={[
                      'interview-practice__feedback-tab',
                      activeFeedbackTab === 'strengths'
                        ? 'interview-practice__feedback-tab--active'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    onClick={() => {
                      setActiveFeedbackTab('strengths')
                    }}
                  >
                    What you did well
                  </button>

                  <button
                    type="button"
                    id="summary-feedback-tab-improvements"
                    role="tab"
                    aria-selected={
                      activeFeedbackTab === 'improvements'
                    }
                    aria-controls="summary-feedback-panel"
                    className={[
                      'interview-practice__feedback-tab',
                      activeFeedbackTab === 'improvements'
                        ? 'interview-practice__feedback-tab--active'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    onClick={() => {
                      setActiveFeedbackTab('improvements')
                    }}
                  >
                    What to improve
                  </button>

                  <button
                    type="button"
                    id="summary-feedback-tab-grounded"
                    role="tab"
                    aria-selected={
                      activeFeedbackTab === 'grounded'
                    }
                    aria-controls="summary-feedback-panel"
                    className={[
                      'interview-practice__feedback-tab',
                      activeFeedbackTab === 'grounded'
                        ? 'interview-practice__feedback-tab--active'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    onClick={() => {
                      setActiveFeedbackTab('grounded')
                    }}
                  >
                    Keep grounded
                  </button>
                </nav>

                <div
                  id="summary-feedback-panel"
                  className="interview-practice__feedback-detail"
                  role="tabpanel"
                >
                  {activeFeedbackTab === 'strengths' && (
                    <div>
                      <h4>What you did well</h4>

                      <ul>
                        {strengths.map((item) => (
                          <li key={item}>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {activeFeedbackTab === 'improvements' && (
                    <div>
                      <h4>What to improve</h4>

                      <ul>
                        {improvements.map((item) => (
                          <li key={item}>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {activeFeedbackTab === 'grounded' && (
                    <div>
                      <h4>Keep grounded</h4>

                      <ul>
                        <li>
                          Use only real experience
                        </li>
                        <li>
                          Do not invent achievements
                        </li>
                        <li>
                          Review AI wording before using
                        </li>
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              <div className="interview-practice__reviewed">
                <div className="interview-practice__reviewed-heading">
                  <h2 className="interview-prep__section-heading">
                    Reviewed questions
                  </h2>

                  <p className="interview-prep__muted">
                    Feedback summaries from the questions you
                    completed during this session.
                  </p>
                </div>

                <div className="interview-practice__review-list">
                  {reviewedQuestions.map((item) => (
                    <div
                      key={item.index}
                      className="interview-practice__review-item"
                    >
                      <div className="interview-practice__review-question">
                        <span>
                          Question {item.index + 1}
                        </span>

                        <strong>
                          {item.question}
                        </strong>
                      </div>

                      <p>
                        {item.feedback.feedback_summary}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {finishSessionError && (
            <p
              className="interview-prep__error"
              role="alert"
            >
              {finishSessionError}
            </p>
          )}

          <div className="interview-prep__button-row">
            <button
              type="button"
              className="interview-prep__button"
              disabled={isFinishingSession}
              onClick={returnToPractice}
            >
              Back to Questions
            </button>

            <button
              type="button"
              className="interview-prep__button interview-prep__button--primary"
              disabled={isFinishingSession}
              onClick={() =>
                onEndPractice({
                  totalQuestions:
                    questions.length,
                  questionsWithFeedback:
                    completedCount,
                })
              }
            >
              {
                isFinishingSession
                  ? 'Saving Session...'
                  : 'Finish Session'
              }
            </button>
          </div>
        </section>
      </div>
    )
  }


  return (
    <div className="interview-practice">
      <section className="interview-practice__summary">
        <div className="interview-practice__summary-item">
          <span>Target career</span>
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
          <div className="interview-practice__question-meta">
            <span className="interview-practice__badge">
              AI-generated question
            </span>

            <span className="interview-practice__question-count">
              Question {currentIndex + 1} of {questions.length}
            </span>
          </div>

          <h3 className="interview-practice__question-title">
            {currentQuestion.question}
          </h3>

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
              onClick={showSummary}
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
          <div className="interview-practice__feedback-summary interview-practice__feedback-summary--compact">
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

          <div className="interview-practice__feedback-tabs">
            <nav
              className="interview-practice__feedback-nav"
              aria-label="AI feedback sections"
              role="tablist"
            >
              <button
                type="button"
                id="feedback-tab-strengths"
                role="tab"
                aria-selected={
                  activeFeedbackTab === 'strengths'
                }
                aria-controls="interview-feedback-panel"
                className={[
                  'interview-practice__feedback-tab',
                  activeFeedbackTab === 'strengths'
                    ? 'interview-practice__feedback-tab--active'
                    : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => {
                  setActiveFeedbackTab('strengths')
                }}
              >
                What you did well
              </button>

              <button
                type="button"
                id="feedback-tab-improvements"
                role="tab"
                aria-selected={
                  activeFeedbackTab === 'improvements'
                }
                aria-controls="interview-feedback-panel"
                className={[
                  'interview-practice__feedback-tab',
                  activeFeedbackTab === 'improvements'
                    ? 'interview-practice__feedback-tab--active'
                    : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => {
                  setActiveFeedbackTab('improvements')
                }}
              >
                What to improve
              </button>

              <button
                type="button"
                id="feedback-tab-grounded"
                role="tab"
                aria-selected={
                  activeFeedbackTab === 'grounded'
                }
                aria-controls="interview-feedback-panel"
                className={[
                  'interview-practice__feedback-tab',
                  activeFeedbackTab === 'grounded'
                    ? 'interview-practice__feedback-tab--active'
                    : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => {
                  setActiveFeedbackTab('grounded')
                }}
              >
                Keep grounded
              </button>
            </nav>

            <div
              id="interview-feedback-panel"
              className="interview-practice__feedback-detail"
              role="tabpanel"
              aria-live="polite"
            >
              {activeFeedbackTab === 'strengths' && (
                <div>
                  <h4>What you did well</h4>

                  <ul>
                    {currentFeedback.strengths.map(
                      (item) => (
                        <li key={item}>
                          {item}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}

              {activeFeedbackTab === 'improvements' && (
                <div>
                  <h4>What to improve</h4>

                  <ul>
                    {currentFeedback.improvements.map(
                      (item) => (
                        <li key={item}>
                          {item}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}

              {activeFeedbackTab === 'grounded' && (
                <div>
                  <h4>Keep grounded</h4>

                  <ul>
                    <li>
                      Use only real experience
                    </li>
                    <li>
                      Do not invent achievements
                    </li>
                    <li>
                      Review AI wording before using
                    </li>
                  </ul>
                </div>
              )}
            </div>
          </div>

          <div className="interview-practice__example interview-practice__example--collapsible">
            <button
              type="button"
              className="interview-practice__example-toggle"
              aria-expanded={isExampleExpanded}
              aria-controls="interview-example-answer"
              onClick={() => {
                setIsExampleExpanded(
                  (currentValue) => !currentValue,
                )
              }}
            >
              <span>
                Suggested stronger answer
              </span>

              <span className="interview-practice__example-toggle-action">
                {isExampleExpanded
                  ? 'Hide example answer'
                  : 'View example answer'}
              </span>
            </button>

            {isExampleExpanded && (
              <div
                id="interview-example-answer"
                className="interview-practice__example-content"
              >
                <p>
                  {currentFeedback.suggested_response}
                </p>

                {currentFeedback.limitations?.length > 0 && (
                  <div className="interview-practice__limitations">
                    <h5>
                      Areas not covered
                    </h5>

                    <p>
                      {currentFeedback.limitations.join(' ')}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}


export default InterviewPractice