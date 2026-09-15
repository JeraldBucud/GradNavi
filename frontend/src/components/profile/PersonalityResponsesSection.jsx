import {
  PROFILE_QUESTIONNAIRE,
  QUESTIONNAIRE_OPTIONS,
} from '../../data/profileQuestionnaire'


function PersonalityResponsesSection({
  items,
  onChange,
  onClose,
}) {
  function getResponse(
    questionKey,
  ) {
    return (
      items.find(
        (item) =>
          item.question_key ===
          questionKey,
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
          item.question_key ===
          questionKey,
      )

    if (
      existingResponseIndex === -1
    ) {
      onChange([
        ...items,

        {
          question_key:
            questionKey,

          response_value:
            responseValue,
        },
      ])

      return
    }

    onChange(
      items.map(
        (item, index) => {
          if (
            index !==
            existingResponseIndex
          ) {
            return item
          }

          /*
           * Spread the persisted response
           * first so its backend ID remains
           * attached after a value change.
           */
          return {
            ...item,

            response_value:
              responseValue,
          }
        },
      ),
    )
  }


  function handleClearResponse(
    questionKey,
  ) {
    onChange(
      items.filter(
        (item) =>
          item.question_key !==
          questionKey,
      ),
    )
  }


  const answeredCount =
    PROFILE_QUESTIONNAIRE.filter(
      (question) =>
        Boolean(
          getResponse(
            question.key,
          ),
        ),
    ).length


  return (
    <section className="profile-manager-section profile-manager-section--questionnaire">
      <div className="profile-manager-heading">
        <div>
          <h3>
            Personality Responses
          </h3>

          <p>
            Rate how strongly you agree
            or disagree with each
            statement.
          </p>
        </div>

        <button
          className="profile-manager-close"
          type="button"
          onClick={onClose}
        >
          Close
        </button>
      </div>


      <div className="profile-questionnaire-progress">
        <div>
          <strong>
            {answeredCount}
          </strong>

          <span>
            {' of '}
            {
              PROFILE_QUESTIONNAIRE.length
            }
            {' answered'}
          </span>
        </div>

        <p>
          These responses support
          GradNavi work-style and
          career-analysis features.
        </p>
      </div>


      <div className="profile-questionnaire-list">
        {
          PROFILE_QUESTIONNAIRE.map(
            (
              question,
              questionIndex,
            ) => {
              const currentResponse =
                getResponse(
                  question.key,
                )

              return (
                <fieldset
                  className="profile-questionnaire-item"
                  key={
                    question.key
                  }
                >
                  <legend>
                    {
                      questionIndex +
                      1
                    }
                    {'. '}
                    {question.label}
                  </legend>

                  <p>
                    {
                      question.question
                    }
                  </p>

                  <div className="profile-questionnaire-options">
                    {
                      QUESTIONNAIRE_OPTIONS.map(
                        (option) => {
                          const inputId =
                            `${question.key}-${option.value}`

                          return (
                            <label
                              key={
                                option.value
                              }
                              htmlFor={
                                inputId
                              }
                            >
                              <input
                                id={
                                  inputId
                                }
                                type="radio"
                                name={
                                  question.key
                                }
                                value={
                                  option.value
                                }
                                checked={
                                  currentResponse ===
                                  option.value
                                }
                                onChange={(
                                  event,
                                ) =>
                                  handleResponseChange(
                                    question.key,
                                    event
                                      .target
                                      .value,
                                  )
                                }
                              />

                              <span>
                                {
                                  option.value
                                }
                                {'. '}
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
                    currentResponse && (
                      <button
                        className="profile-clear-response"
                        type="button"
                        onClick={() =>
                          handleClearResponse(
                            question.key,
                          )
                        }
                      >
                        Clear Response
                      </button>
                    )
                  }
                </fieldset>
              )
            },
          )
        }
      </div>
    </section>
  )
}


export default PersonalityResponsesSection