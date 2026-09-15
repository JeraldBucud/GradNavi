import { useState } from 'react'

import {
  SPRINT_1_INTERESTS,
} from '../../data/profileReferenceData'


function InterestsSection({
  items,
  onChange,
  onClose,
}) {
  const [
    selectedInterest,
    setSelectedInterest,
  ] = useState('')

  const [
    isFormOpen,
    setIsFormOpen,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState('')


  function resetForm() {
    setSelectedInterest('')
    setError('')
    setIsFormOpen(false)
  }


  function handleInterestChange(
    event,
  ) {
    setSelectedInterest(
      event.target.value,
    )

    setError('')
  }


  function handleAdd() {
    setSelectedInterest('')
    setError('')
    setIsFormOpen(true)
  }


  function handleSubmit(event) {
    event.preventDefault()

    if (!selectedInterest) {
      setError(
        'Select an interest.',
      )

      return
    }

    const interestReference =
      SPRINT_1_INTERESTS.find(
        (interest) =>
          interest.name ===
          selectedInterest,
      )

    if (!interestReference) {
      setError(
        'Select a valid interest.',
      )

      return
    }

    const duplicateInterest =
      items.some(
        (interest) =>
          interest.name
            .toLowerCase() ===
          interestReference.name
            .toLowerCase(),
      )

    if (duplicateInterest) {
      setError(
        'This interest has already been added.',
      )

      return
    }

    onChange([
      ...items,

      {
        name:
          interestReference.name,

        category:
          interestReference.category,
      },
    ])

    resetForm()
  }


  function handleRemove(
    indexToRemove,
  ) {
    onChange(
      items.filter(
        (_, index) =>
          index !==
          indexToRemove,
      ),
    )
  }


  return (
    <section className="profile-manager-section">
      <div className="profile-manager-heading">
        <div>
          <h3>
            Interests
          </h3>

          <p>
            Interests use the approved
            Sprint 1 reference data
            linked to your profile.
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


      <div className="profile-manager-records">
        {items.length === 0 ? (
          <div className="profile-manager-empty">
            No interests added yet.
          </div>
        ) : (
          items.map(
            (
              interest,
              index,
            ) => (
              <article
                className="profile-manager-record"
                key={
                  interest.id ||
                  `${interest.name}-${index}`
                }
              >
                <div className="profile-manager-record__content">
                  <strong>
                    {interest.name}
                  </strong>

                  {
                    interest
                      .category && (
                      <p>
                        {
                          interest
                            .category
                        }
                      </p>
                    )
                  }
                </div>

                <div className="profile-manager-record__actions">
                  <button
                    className="profile-text-action profile-text-action--danger"
                    type="button"
                    onClick={() =>
                      handleRemove(
                        index,
                      )
                    }
                  >
                    Remove
                  </button>
                </div>
              </article>
            ),
          )
        )}
      </div>


      {!isFormOpen && (
        <div className="profile-manager-actions">
          <button
            className="profile-secondary-action"
            type="button"
            onClick={handleAdd}
          >
            Add Interest
          </button>
        </div>
      )}


      {isFormOpen && (
        <form
          className="profile-manager-form"
          onSubmit={handleSubmit}
        >
          <div className="profile-field">
            <label htmlFor="interest-name">
              Interest
            </label>

            <select
              id="interest-name"
              value={
                selectedInterest
              }
              onChange={
                handleInterestChange
              }
            >
              <option value="">
                Select an interest
              </option>

              {
                SPRINT_1_INTERESTS.map(
                  (interest) => (
                    <option
                      key={
                        interest.name
                      }
                      value={
                        interest.name
                      }
                    >
                      {
                        interest.name
                      }
                    </option>
                  ),
                )
              }
            </select>
          </div>


          {selectedInterest && (
            <p className="profile-reference-detail">
              Category:{' '}
              {
                SPRINT_1_INTERESTS.find(
                  (interest) =>
                    interest.name ===
                    selectedInterest,
                )?.category
              }
            </p>
          )}


          {error && (
            <p
              className="profile-error-message"
              role="alert"
            >
              {error}
            </p>
          )}


          <div className="profile-inline-form__actions">
            <button
              className="profile-primary-action"
              type="submit"
            >
              Add Interest
            </button>

            <button
              className="profile-secondary-action"
              type="button"
              onClick={resetForm}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </section>
  )
}


export default InterestsSection