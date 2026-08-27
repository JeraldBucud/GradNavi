import { useState } from 'react'

function createEmptyCareerGoalForm() {
  return {
    target_role: '',
    description: '',
  }
}

function CareerGoalsSection({
  items,
  onChange,
}) {
  const [careerGoalForm, setCareerGoalForm] = useState(
    createEmptyCareerGoalForm,
  )
  const [editingIndex, setEditingIndex] = useState(null)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setCareerGoalForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))

    setError('')
  }

  function handleSubmit(event) {
    event.preventDefault()

    if (!careerGoalForm.target_role.trim()) {
      setError('Target role is required.')
      return
    }

    const nextCareerGoal = {
      target_role:
        careerGoalForm.target_role.trim(),
      description:
        careerGoalForm.description.trim(),
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        nextCareerGoal,
      ])
    } else {
      onChange(
        items.map((careerGoal, index) => {
          if (index !== editingIndex) {
            return careerGoal
          }

          return {
            ...careerGoal,
            ...nextCareerGoal,
          }
        }),
      )
    }

    setCareerGoalForm(
      createEmptyCareerGoalForm(),
    )
    setEditingIndex(null)
    setError('')
  }

  function handleEdit(index) {
    const careerGoal = items[index]

    setCareerGoalForm({
      target_role:
        careerGoal.target_role || '',
      description:
        careerGoal.description || '',
    })

    setEditingIndex(index)
    setError('')
  }

  function handleRemove(indexToRemove) {
    onChange(
      items.filter(
        (_, index) => index !== indexToRemove,
      ),
    )

    if (editingIndex === indexToRemove) {
      handleCancelEdit()
    } else if (
      editingIndex !== null &&
      editingIndex > indexToRemove
    ) {
      setEditingIndex(
        (currentIndex) => currentIndex - 1,
      )
    }
  }

  function handleCancelEdit() {
    setCareerGoalForm(
      createEmptyCareerGoalForm(),
    )
    setEditingIndex(null)
    setError('')
  }

  return (
    <section className="profile-section">
      <h2>Career Goals</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="target_role">
            Target Role
          </label>

          <input
            id="target_role"
            name="target_role"
            type="text"
            value={careerGoalForm.target_role}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="career_goal_description">
            Description
          </label>

          <textarea
            id="career_goal_description"
            name="description"
            value={careerGoalForm.description}
            onChange={handleChange}
          />
        </div>

        {error && (
          <p role="alert">{error}</p>
        )}

        <button type="submit">
          {editingIndex === null
            ? 'Add Career Goal'
            : 'Update Career Goal'}
        </button>

        {editingIndex !== null && (
          <button
            type="button"
            onClick={handleCancelEdit}
          >
            Cancel Edit
          </button>
        )}
      </form>

      {items.length > 0 && (
        <div>
          <h3>Career Goals</h3>

          {items.map((careerGoal, index) => (
            <article
              className="profile-item"
              key={
                careerGoal.id ||
                `${careerGoal.target_role}-${index}`
              }
            >
              <h4>{careerGoal.target_role}</h4>

              {careerGoal.description && (
                <p>{careerGoal.description}</p>
              )}

              <button
                type="button"
                onClick={() => handleEdit(index)}
              >
                Edit
              </button>

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

export default CareerGoalsSection