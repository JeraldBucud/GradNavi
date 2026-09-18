import {
  useState,
} from 'react'

import {
  PROFILE_QUESTIONNAIRE,
  QUESTIONNAIRE_OPTIONS,
} from '../../data/profileQuestionnaire'


function PersonalityResponsesSection({
  items,
  onChange,
  onClose,
  onSave,
  isSaving = false,
}) {
  function getResponse(
    questionKey,
  ) {
    return (
      items.find(
        (item) =>
          item.question_key
          === questionKey,
      )?.response_value
      || ''
    )
  }


  const firstUnansweredIndex =
    PROFILE_QUESTIONNAIRE.findIndex(
      (question) =>
        !getResponse(
          question.key,
        ),
    )


  const [
    currentQuestionIndex,
    setCurrentQuestionIndex,
  ] = useState(
    firstUnansweredIndex >= 0
      ? firstUnansweredIndex
      : 0,
  )


  const [
    error,
    setError,
  ] = useState('')


  const currentQuestion =
    PROFILE_QUESTIONNAIRE[
      currentQuestionIndex
    ]


  const currentResponse =
    getResponse(
      currentQuestion.key,
    )


  const answeredCount =
    PROFILE_QUESTIONNAIRE.filter(
      (question) =>
        Boolean(
          getResponse(
            question.key,
          ),
        ),
    ).length


  function handleResponseChange(
    responseValue,
  ) {
    const existingResponseIndex =
      items.findIndex(
        (item) =>
          item.question_key
          === currentQuestion.key,
      )

    if (
      existingResponseIndex
      === -1
    ) {
      onChange([
        ...items,

        {
          question_key:
            currentQuestion.key,

          response_value:
            responseValue,
        },
      ])
    } else {
      onChange(
        items.map(
          (
            item,
            index,
          ) => {
            if (
              index
              !== existingResponseIndex
            ) {
              return item
            }

            return {
              ...item,

              response_value:
                responseValue,
            }
          },
        ),
      )
    }

    setError('')
  }


  function handleClearResponse() {
    onChange(
      items.filter(
        (item) =>
          item.question_key
          !== currentQuestion.key,
      ),
    )

    setError('')
  }


  function handlePrevious() {
    setError('')

    setCurrentQuestionIndex(
      (
        currentIndex,
      ) =>
        Math.max(
          0,
          currentIndex - 1,
        ),
    )
  }


  async function handleSaveAndContinue() {
    if (!currentResponse) {
      setError(
        'Choose a response before continuing.',
      )

      return
    }

    let didSave = true

    if (onSave) {
      didSave =
        await onSave()
    }

    if (!didSave) {
      return
    }

    setError('')

    if (
      currentQuestionIndex
      < PROFILE_QUESTIONNAIRE
        .length - 1
    ) {
      setCurrentQuestionIndex(
        (
          currentIndex,
        ) =>
          currentIndex + 1,
      )
    }
  }


  return (
    <div className="student-profile-personality">
      <div className="student-profile-personality__progress">
        <div>
          <strong>
            Question {
              currentQuestionIndex
              + 1
            } of {
              PROFILE_QUESTIONNAIRE
                .length
            }
          </strong>

          <span>
            {
              answeredCount
            } of {
              PROFILE_QUESTIONNAIRE
                .length
            } answered
          </span>
        </div>

        <div
          className="student-profile-personality__progress-track"
          aria-hidden="true"
        >
          <span
            style={{
              width:
                `${
                  (
                    answeredCount
                    / PROFILE_QUESTIONNAIRE
                      .length
                  ) * 100
                }%`,
            }}
          />
        </div>
      </div>


      <div className="student-profile-personality__question-card">
        <span className="student-profile-personality__trait">
          {
            currentQuestion.label
          }
        </span>

        <h3>
          {
            currentQuestion.question
          }
        </h3>

        <div className="student-profile-personality__options">
          {
            QUESTIONNAIRE_OPTIONS.map(
              (option) => {
                const optionId =
                  `${
                    currentQuestion.key
                  }-${
                    option.value
                  }`

                const isSelected =
                  currentResponse
                  === option.value

                return (
                  <label
                    key={
                      option.value
                    }
                    className={[
                      'student-profile-personality__option',
                      isSelected
                        ? 'student-profile-personality__option--selected'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    htmlFor={
                      optionId
                    }
                  >
                    <input
                      id={
                        optionId
                      }
                      type="radio"
                      name={
                        currentQuestion
                          .key
                      }
                      value={
                        option.value
                      }
                      checked={
                        isSelected
                      }
                      onChange={(
                        event,
                      ) =>
                        handleResponseChange(
                          event
                            .target
                            .value,
                        )
                      }
                    />

                    <span className="student-profile-personality__option-value">
                      {
                        option.value
                      }
                    </span>

                    <span>
                      {
                        option.label
                      }
                    </span>
                  </label>
                )
              },
            )
          }
        </div>


        {
          currentResponse
          && (
            <button
              className="student-profile-personality__clear"
              type="button"
              onClick={
                handleClearResponse
              }
            >
              Clear response
            </button>
          )
        }


        {
          error
          && (
            <p
              className="student-profile-redesign__error"
              role="alert"
            >
              {error}
            </p>
          )
        }
      </div>


      <div className="student-profile-personality__actions">
        <div>
          <button
            className="student-profile-redesign__secondary-button"
            type="button"
            onClick={
              handlePrevious
            }
            disabled={
              currentQuestionIndex
              === 0
            }
          >
            Previous
          </button>

          <button
            className="student-profile-redesign__secondary-button"
            type="button"
            onClick={
              onClose
            }
          >
            Back to Profile Summary
          </button>
        </div>

        <button
          className="student-profile-redesign__primary-button"
          type="button"
          onClick={
            handleSaveAndContinue
          }
          disabled={
            isSaving
          }
        >
          {
            isSaving
              ? 'Saving...'
              : (
                currentQuestionIndex
                === PROFILE_QUESTIONNAIRE
                  .length - 1
                  ? 'Save Assessment'
                  : 'Save & Continue'
              )
          }
        </button>
      </div>
    </div>
  )
}


export default PersonalityResponsesSection
