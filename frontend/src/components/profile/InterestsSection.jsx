import { useState } from 'react'

import {
  searchProfileInterests,
} from '../../services/profileService'

import SearchableReferenceField from './SearchableReferenceField'


function InterestsSection({
  items,
  onChange,
  onClose,
}) {
  const [
    selectedInterest,
    setSelectedInterest,
  ] = useState(null)

  const [
    isFormOpen,
    setIsFormOpen,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState('')


  function resetForm() {
    setSelectedInterest(null)
    setError('')
    setIsFormOpen(false)
  }


  function handleInterestSelect(
    interest,
  ) {
    setSelectedInterest(
      interest,
    )

    setError('')
  }


  function handleAdd() {
    setSelectedInterest(null)
    setError('')
    setIsFormOpen(true)
  }


  function handleSubmit(
    event,
  ) {
    event.preventDefault()

    if (!selectedInterest) {
      setError(
        'Select an interest.',
      )

      return
    }


    const duplicateInterest =
      items.some(
        (interest) =>
          interest.id ===
            selectedInterest.id,
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
        id:
          selectedInterest.id,

        name:
          selectedInterest.name,

        category:
          selectedInterest.category || '',
      },
    ])

    resetForm()
  }


  function handleRemove(
    indexToRemove,
  ) {
    onChange(
      items.filter(
        (
          _,
          index,
        ) =>
          index !==
          indexToRemove,
      ),
    )
  }


  const excludedInterestIds =
    items
      .map(
        (interest) =>
          interest.id,
      )
      .filter(
        Boolean,
      )


  return (
    <section className="profile-manager-section">
      <div className="profile-manager-heading">
        <div>
          <h3>
            Interests
          </h3>

          <p>
            Search the GradNavi Interest catalogue
            and select interests linked to your
            career preferences.
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

                  {interest.category && (
                    <p>
                      {
                        interest.category
                      }
                    </p>
                  )}
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
          <SearchableReferenceField
            id="interest-reference-search"
            label="Interest"
            placeholder="Search interests, for example data"
            searchReference={
              searchProfileInterests
            }
            selectedItem={
              selectedInterest
            }
            onSelect={
              handleInterestSelect
            }
            excludedIds={
              excludedInterestIds
            }
            helperText="Type an interest name or category, then select an approved result."
          />


          {selectedInterest && (
            <p className="profile-reference-detail">
              Selected:{' '}
              {
                selectedInterest.name
              }

              {
                selectedInterest.category
                  ? ` · ${selectedInterest.category}`
                  : ''
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
              onClick={
                resetForm
              }
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
