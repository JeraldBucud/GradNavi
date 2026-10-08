import { useState } from 'react'

import {
  useNavigate,
} from 'react-router'

import CareerSelector from '../components/career/CareerSelector'

import useCareerContext from '../hooks/useCareerContext'

import {
  getStoredUser,
} from '../services/authService'

import {
  clearActiveInterviewSession,
  getActiveInterviewSession,
  storeActiveInterviewSession,
} from '../services/interviewSessionStorage'

import { generateInterviewQuestions } from '../services/interviewService'
import { createInterviewHistorySession } from '../services/interviewHistoryService'
import InterviewPractice from '../components/interview/InterviewPractice'

import './CareerGuidancePage.css'
import './InterviewPreparationPage.css'


const DEFAULT_QUESTION_COUNT = 5


function InterviewPreparationPage() {
  const navigate =
    useNavigate()

  const currentUser =
    getStoredUser()

  const accountName =
    currentUser?.first_name?.trim()
    || 'Student'

  const accountInitial =
    accountName
      .charAt(0)
      .toUpperCase()

  const {
    careerOptions,
    error:
      careerContextError,
    isLoading:
      isCareerContextLoading,
    primaryCareer,
    profileSetupRequired,
    selectedCareer,
    selectedCareerId,
    selectCareer,
  } = useCareerContext()

  const [
    restoredInterviewSession,
  ] = useState(
    () =>
      getActiveInterviewSession(),
  )

  const [
    jobDescription,
    setJobDescription,
  ] = useState(
    () =>
      restoredInterviewSession
        ?.sessionContext
        ?.jobDescription
      || '',
  )
  const [
    questionCount,
    setQuestionCount,
  ] = useState(
    () =>
      restoredInterviewSession
        ?.sessionContext
        ?.questionCount
      || DEFAULT_QUESTION_COUNT,
  )

  const [
    questionSet,
    setQuestionSet,
  ] = useState(
    () =>
      restoredInterviewSession
        ?.questionSet
      || null,
  )

  const [
    sessionContext,
    setSessionContext,
  ] = useState(
    () =>
      restoredInterviewSession
        ?.sessionContext
      || null,
  )
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [
    isFinishingSession,
    setIsFinishingSession,
  ] = useState(false)
  const [
    finishSessionError,
    setFinishSessionError,
  ] = useState('')

  const isSessionActive =
    Boolean(questionSet && sessionContext)

  const selectedCareerName =
    String(
      selectedCareer
        ?.career_name
      || '',
    ).trim()


  const displayedCareerId =
    isSessionActive
      ? sessionContext?.careerId
      : selectedCareerId

  const displayedCareerName =
    isSessionActive
      ? sessionContext?.targetRole
      : selectedCareerName


  async function handleGenerateQuestions() {
    const normalizedTargetRole =
      selectedCareerName

    const normalizedJobDescription =
      jobDescription.trim()

    const requestedQuestionCount =
      questionCount

    if (
      !selectedCareerId
      || !normalizedTargetRole
    ) {
      setErrorMessage(
        profileSetupRequired
          ? (
            'Set up your Student Profile '
            + 'before starting interview practice.'
          )
          : 'Choose a target career first.',
      )

      return
    }

    setIsLoading(true)
    setErrorMessage('')
    setFinishSessionError('')

    try {
      const result = await generateInterviewQuestions({
        targetRole: normalizedTargetRole,
        jobDescription: normalizedJobDescription,
        questionCount: requestedQuestionCount,
      })

      const nextSessionContext = {
        careerId: selectedCareerId,
        targetRole: normalizedTargetRole,
        jobDescription: normalizedJobDescription,
        questionCount: requestedQuestionCount,
      }

      setSessionContext(
        nextSessionContext,
      )

      setQuestionSet(result)

      storeActiveInterviewSession({
        sessionContext:
          nextSessionContext,
        questionSet:
          result,
        practice: {
          currentIndex: 0,
          answers: {},
          feedbackByQuestion: {},
          isSummaryVisible: false,
        },
      })
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
    clearActiveInterviewSession()

    if (primaryCareer?.career_id) {
      selectCareer(
        primaryCareer.career_id,
      )
    }

    setJobDescription('')
    setQuestionCount(DEFAULT_QUESTION_COUNT)
    setQuestionSet(null)
    setSessionContext(null)
    setErrorMessage('')
    setFinishSessionError('')
  }


  async function handleFinishSession(
    sessionSummary,
  ) {
    if (
      !sessionContext
      || isFinishingSession
    ) {
      return
    }

    setIsFinishingSession(true)
    setFinishSessionError('')

    try {
      await createInterviewHistorySession({
        targetRole:
          sessionContext.targetRole,
        totalQuestions:
          sessionSummary.totalQuestions,
        questionsWithFeedback:
          sessionSummary.questionsWithFeedback,
      })

      clearActiveInterviewSession()

      setQuestionSet(null)
      setSessionContext(null)
      setErrorMessage('')
    }
    catch (error) {
      setFinishSessionError(
        error.message
        || (
          'Your session could not be saved. '
          + 'Please try again.'
        ),
      )
    }
    finally {
      setIsFinishingSession(false)
    }
  }


  return (
    <div className="career-guidance-page interview-prep">
      <div className="career-guidance-heading interview-prep__heading">
        <div className="career-guidance-heading__copy">
          <h1>
            Interview Preparation
          </h1>

          <p>
            Practise interview questions for your target
            career and get focused feedback on your answers.
          </p>
        </div>

        <div
          className="career-guidance-account-pill"
          aria-label={`Signed in as ${accountName}`}
        >
          <span
            className="career-guidance-account-pill__avatar"
            aria-hidden="true"
          >
            {accountInitial}
          </span>

          <strong>
            {accountName}
          </strong>
        </div>
      </div>

      {isSessionActive ? (
        <section className="career-guidance-section interview-prep__session-context">
          <div className="interview-prep__session-context-main">
            <div className="interview-prep__session-career">
              <span className="interview-prep__session-kicker">
                Active practice session
              </span>

              <strong>
                {sessionContext.targetRole}
              </strong>
            </div>

            <div className="interview-prep__session-facts">
              <span>
                {sessionContext.questionCount}{' '}
                {Number(sessionContext.questionCount) === 1
                  ? 'question'
                  : 'questions'}
              </span>

              <span>
                {sessionContext.jobDescription
                  ? 'Job description added'
                  : 'General interview practice'}
              </span>
            </div>
          </div>

          <p className="interview-prep__session-note">
            Finish this practice session before changing
            the interview setup.
          </p>
        </section>
      ) : (
<section className="career-guidance-section interview-prep__section">
        <h2 className="interview-prep__section-heading">
          Interview Setup
        </h2>
        <p className="interview-prep__muted">
          Your Primary Career is selected by default.
          Choose another GradNavi career if you want to
          practise for a different role, then optionally
          add a job description for more focused questions.
        </p>

        {profileSetupRequired && (
          <div className="interview-prep__profile-guidance">
            <div>
              <strong>
                Set up your Student Profile first
              </strong>

              <p>
                Add your skills and career direction so
                GradNavi has a mapped career to use for
                interview practice.
              </p>
            </div>

            <button
              type="button"
              className="interview-prep__button"
              onClick={() =>
                navigate('/profile')
              }
            >
              Set Up My Profile
            </button>
          </div>
        )}

        <div className="interview-prep__setup-grid">
          <div className="interview-prep__field">
            <CareerSelector
              careers={careerOptions}
              disabled={
                isLoading
                || isSessionActive
                || isCareerContextLoading
                || profileSetupRequired
              }
              label="Target career"
              onChange={(careerId) => {
                selectCareer(careerId)
                setErrorMessage('')
              }}
              selectedCareerId={displayedCareerId}
              selectedCareerName={displayedCareerName}
            />
          </div>

          <label className="interview-prep__field">
            <span>Question count</span>
            <select
              value={questionCount}
              disabled={isLoading || isSessionActive || profileSetupRequired}
              onChange={(event) => {
                setQuestionCount(
                  Number(event.target.value),
                )
              }}
            >
                            {Array.from(
                { length: 10 },
                (_, index) => index + 1,
              ).map((count) => (
                <option key={count} value={count}>
                  {count === 1
                    ? '1 question'
                    : `${count} questions`}
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
              disabled={isLoading || isSessionActive || profileSetupRequired}
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
            disabled={
              isLoading
              || isSessionActive
              || isCareerContextLoading
              || profileSetupRequired
              || !selectedCareerId
              || !selectedCareerName
            }
            onClick={handleGenerateQuestions}
          >
            {isLoading
              ? 'Generating questions...'
              : 'Generate Practice Questions'}
          </button>

          <button
            type="button"
            className="interview-prep__button"
            disabled={isLoading || isSessionActive || profileSetupRequired}
            onClick={handleClearContext}
          >
            Clear Context
          </button>
        </div>

        {isLoading && (
          <div
            className="interview-prep__generation-status"
            role="status"
            aria-live="polite"
          >
            <span
              className="interview-prep__spinner"
              aria-hidden="true"
            />

            <span>
              Creating {questionCount}{' '}
              {Number(questionCount) === 1
                ? 'interview question'
                : 'interview questions'}{' '}
              for {selectedCareerName}.
              {' '}This usually takes a few seconds.
            </span>
          </div>
        )}

        {careerContextError && (
          <p
            className="interview-prep__error"
            role="alert"
          >
            {careerContextError}
          </p>
        )}

        {isSessionActive && (
          <p className="interview-prep__muted">
            Finish the current practice session before changing
            the interview setup.
          </p>
        )}

        {errorMessage && (
          <p
            className="interview-prep__error"
            role="alert"
          >
            {errorMessage}
          </p>
        )}
      </section>
      )}
        {questionSet && sessionContext && (
          <section className="career-guidance-section interview-prep__section">
            <InterviewPractice
              key={questionSet.questions
                .map((item) => item.question)
                .join('|')}
              targetRole={sessionContext.targetRole}
              questions={questionSet.questions}
              isFinishingSession={isFinishingSession}
              finishSessionError={finishSessionError}
              onEndPractice={handleFinishSession}
            />
          </section>
        )}
    </div>
  )
}


export default InterviewPreparationPage