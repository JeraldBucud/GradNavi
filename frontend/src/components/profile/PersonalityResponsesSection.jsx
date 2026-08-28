import {
  PROFILE_QUESTIONNAIRE,
  QUESTIONNAIRE_OPTIONS,
} from '../../data/profileQuestionnaire'

function PersonalityResponsesSection({
  items,
  onChange,
}) {
  function getResponse(questionKey) {
    return (
      items.find(
        (item) =>
          item.question_key === questionKey,
      )?.response_value || ''
    )
  }

  function handleResponseChange(
    questionKey,
    responseValue,
  ) {
    const existingResponseIndex =
      items.findIndex(
        (item) =>
          item.question_key === questionKey,
      )

    if (existingResponseIndex === -1) {
      onChange([
        ...items,
        {
          question_key: questionKey,
          response_value: responseValue,
        },
      ])

      return
    }

    const updatedItems = items.map(
      (item, index) => {
        if (index !== existingResponseIndex) {
          return item
        }

        return {
          ...item,
          response_value: responseValue,
        }
      },
    )

    onChange(updatedItems)
  }

  function handleClearResponse(questionKey) {
    onChange(
      items.filter(
        (item) =>
          item.question_key !== questionKey,
      ),
    )
  }

  const answeredCount =
    PROFILE_QUESTIONNAIRE.filter(
      (question) =>
        Boolean(getResponse(question.key)),
    ).length

  return (
    <section className="profile-section">
      <h2>Career Work Style Questionnaire</h2>

      <p>
        Rate how strongly you agree or disagree
        with each statement.
      </p>

      <p>
        These responses help GradNavi understand
        your preferred work style for future
        career recommendations.
      </p>

      <p>
        Answered: {answeredCount} of{' '}
        {PROFILE_QUESTIONNAIRE.length}
      </p>

      <div className="questionnaire-list">
        {PROFILE_QUESTIONNAIRE.map(
          (question, questionIndex) => {
            const currentResponse =
              getResponse(question.key)

            return (
              <fieldset
                className="questionnaire-item"
                key={question.key}
              >
                <legend>
                  {questionIndex + 1}.{' '}
                  {question.label}
                </legend>

                <p>{question.question}</p>

                <div className="questionnaire-options">
                  {QUESTIONNAIRE_OPTIONS.map(
                    (option) => {
                      const inputId =
                        `${question.key}-${option.value}`

                      return (
                        <label
                          key={option.value}
                          htmlFor={inputId}
                        >
                          <input
                            id={inputId}
                            type="radio"
                            name={question.key}
                            value={option.value}
                            checked={
                              currentResponse ===
                              option.value
                            }
                            onChange={(event) =>
                              handleResponseChange(
                                question.key,
                                event.target.value,
                              )
                            }
                          />

                          {option.value}.{' '}
                          {option.label}
                        </label>
                      )
                    },
                  )}
                </div>

                {currentResponse && (
                  <button
                    type="button"
                    onClick={() =>
                      handleClearResponse(
                        question.key,
                      )
                    }
                  >
                    Clear Response
                  </button>
                )}
              </fieldset>
            )
          },
        )}
      </div>
    </section>
  )
}

export default PersonalityResponsesSection