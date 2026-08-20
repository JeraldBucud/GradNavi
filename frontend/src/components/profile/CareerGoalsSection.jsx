import { useState } from 'react'

function CareerGoalsSection() {
  const [careerGoalItems, setCareerGoalItems] = useState([])
  const [careerGoalForm, setCareerGoalForm] = useState({
    target_role: '',
    description: '',
  })

  function handleChange(event) {
    const { name, value } = event.target

    setCareerGoalForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    setCareerGoalItems((currentItems) => [
      ...currentItems,
      careerGoalForm,
    ])

    setCareerGoalForm({
      target_role: '',
      description: '',
    })
  }

  function handleRemove(indexToRemove) {
    setCareerGoalItems((currentItems) =>
      currentItems.filter((_, index) => index !== indexToRemove),
    )
  }

  return (
    <section>
      <h2>Career Goals</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="target_role">Target Role</label>
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
          <label htmlFor="career_goal_description">Description</label>
          <textarea
            id="career_goal_description"
            name="description"
            value={careerGoalForm.description}
            onChange={handleChange}
          />
        </div>

        <button type="submit">Add Career Goal</button>
      </form>

      {careerGoalItems.length > 0 && (
        <div>
          <h3>Career Goals</h3>

          {careerGoalItems.map((careerGoal, index) => (
            <article key={`${careerGoal.target_role}-${index}`}>
              <h4>{careerGoal.target_role}</h4>

              {careerGoal.description && (
                <p>{careerGoal.description}</p>
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

export default CareerGoalsSection