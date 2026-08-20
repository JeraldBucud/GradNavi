import { useState } from 'react'

function InterestsSection() {
  const [interestItems, setInterestItems] = useState([])
  const [interestForm, setInterestForm] = useState({
    name: '',
    category: '',
  })
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setInterestForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    const trimmedInterestName = interestForm.name.trim()
    const trimmedCategory = interestForm.category.trim()

    if (!trimmedInterestName) {
      setError('Interest name is required.')
      return
    }

    const duplicateInterest = interestItems.some(
      (interest) =>
        interest.name.toLowerCase() === trimmedInterestName.toLowerCase(),
    )

    if (duplicateInterest) {
      setError('This interest has already been added.')
      return
    }

    setInterestItems((currentItems) => [
      ...currentItems,
      {
        name: trimmedInterestName,
        category: trimmedCategory,
      },
    ])

    setInterestForm({
      name: '',
      category: '',
    })

    setError('')
  }

  function handleRemove(indexToRemove) {
    setInterestItems((currentItems) =>
      currentItems.filter((_, index) => index !== indexToRemove),
    )
  }

  return (
    <section className="profile-section">
      <h2>Interests</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="interest-name">Interest</label>
          <input
            id="interest-name"
            name="name"
            type="text"
            value={interestForm.name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="interest-category">Category</label>
          <input
            id="interest-category"
            name="category"
            type="text"
            value={interestForm.category}
            onChange={handleChange}
          />
        </div>

        {error && <p>{error}</p>}

        <button type="submit">Add Interest</button>
      </form>

      {interestItems.length > 0 && (
        <div>
          <h3>My Interests</h3>

          {interestItems.map((interest, index) => (
            <article
            className="profile-item" 
            key={`${interest.name}-${index}`}>
              <h4>{interest.name}</h4>

              {interest.category && (
                <p>Category: {interest.category}</p>
              )}

              <button
                type="button"
                onClick={() => handleRemove(index)}
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