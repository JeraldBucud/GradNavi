import { useState } from 'react'

import {
  SPRINT_1_INTERESTS,
} from '../../data/profileReferenceData'

function InterestsSection({
  items,
  onChange,
}) {
  const [selectedInterest, setSelectedInterest] =
    useState('')
  const [error, setError] = useState('')

  function handleInterestChange(event) {
    setSelectedInterest(event.target.value)
    setError('')
  }

  function handleSubmit(event) {
    event.preventDefault()

    if (!selectedInterest) {
      setError('Select an interest.')
      return
    }

    const interestReference =
      SPRINT_1_INTERESTS.find(
        (interest) =>
          interest.name === selectedInterest,
      )

    if (!interestReference) {
      setError('Select a valid interest.')
      return
    }

    const duplicateInterest = items.some(
      (interest) =>
        interest.name.toLowerCase() ===
        interestReference.name.toLowerCase(),
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
        name: interestReference.name,
        category: interestReference.category,
      },
    ])

    setSelectedInterest('')
    setError('')
  }

  function handleRemove(indexToRemove) {
    onChange(
      items.filter(
        (_, index) => index !== indexToRemove,
      ),
    )
  }

  return (
    <section className="profile-section">
      <h2>Interests</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="interest-name">
            Interest
          </label>

          <select
            id="interest-name"
            value={selectedInterest}
            onChange={handleInterestChange}
          >
            <option value="">
              Select an interest
            </option>

            {SPRINT_1_INTERESTS.map(
              (interest) => (
                <option
                  key={interest.name}
                  value={interest.name}
                >
                  {interest.name}
                </option>
              ),
            )}
          </select>
        </div>

        {selectedInterest && (
          <p>
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
          <p role="alert">{error}</p>
        )}

        <button type="submit">
          Add Interest
        </button>
      </form>

      {items.length > 0 && (
        <div>
          <h3>My Interests</h3>

          {items.map((interest, index) => (
            <article
              className="profile-item"
              key={
                interest.id ||
                `${interest.name}-${index}`
              }
            >
              <h4>{interest.name}</h4>

              {interest.category && (
                <p>
                  Category: {interest.category}
                </p>
              )}

              <button
                type="button"
                onClick={() =>
                  handleRemove(index)
                }
              >
                Remove
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default InterestsSection