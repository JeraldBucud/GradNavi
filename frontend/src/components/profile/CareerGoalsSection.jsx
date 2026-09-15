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
  onClose,
}) {
  const [
    careerGoalForm,
    setCareerGoalForm,
  ] = useState(
    createEmptyCareerGoalForm,
  )

  const [
    editingIndex,
    setEditingIndex,
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
    setCareerGoalForm(
      createEmptyCareerGoalForm(),
    )

    setEditingIndex(null)
    setIsFormOpen(false)
    setError('')
  }


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setCareerGoalForm(
      (currentForm) => ({
        ...currentForm,

        [name]:
          value,
      }),
    )

    setError('')
  }


  function handleAdd() {
    setCareerGoalForm(
      createEmptyCareerGoalForm(),
    )

    setEditingIndex(null)
    setError('')
    setIsFormOpen(true)
  }


  function handleEdit(index) {
    const careerGoal =
      items[index]

    setCareerGoalForm({
      target_role:
        careerGoal.target_role || '',

      description:
        careerGoal.description || '',
    })

    setEditingIndex(index)
    setError('')
    setIsFormOpen(true)
  }


  function handleSubmit(event) {
    event.preventDefault()

    if (
      !careerGoalForm
        .target_role
        .trim()
    ) {
      setError(
        'Target role is required.',
      )

      return
    }

    const nextCareerGoal = {
      target_role:
        careerGoalForm
          .target_role
          .trim(),

      description:
        careerGoalForm
          .description
          .trim(),
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        nextCareerGoal,
      ])
    } else {
      onChange(
        items.map(
          (
            careerGoal,
            index,
          ) => {
            if (
              index !==
              editingIndex
            ) {
              return careerGoal
            }

            /*
             * Keep the existing object first
             * so persisted IDs survive edits.
             */
            return {
              ...careerGoal,
              ...nextCareerGoal,
            }
          },
        ),
      )
    }

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

    if (
      editingIndex ===
      indexToRemove
    ) {
      resetForm()

      return
    }

    if (
      editingIndex !== null &&
      editingIndex >
        indexToRemove
    ) {
      setEditingIndex(
        (currentIndex) =>
          currentIndex - 1,
      )
    }
  }


  return (
    <section className="profile-manager-section">
      <div className="profile-manager-heading">
        <div>
          <h3>
            Career Goals
          </h3>

          <p>
            Manage target roles stored
            as Student Profile text.
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
            No career goals added yet.
          </div>
        ) : (
          items.map(
            (
              careerGoal,
              index,
            ) => (
              <article
                className="profile-manager-record"
                key={
                  careerGoal.id ||
                  `${careerGoal.target_role}-${index}`
                }
              >
                <div className="profile-manager-record__content">
                  <strong>
                    {
                      careerGoal
                        .target_role
                    }
                  </strong>

                  {
                    careerGoal
                      .description && (
                      <p>
                        {
                          careerGoal
                            .description
                        }
                      </p>
                    )
                  }
                </div>

                <div className="profile-manager-record__actions">
                  <button
                    className="profile-text-action"
                    type="button"
                    onClick={() =>
                      handleEdit(
                        index,
                      )
                    }
                  >
                    Edit
                  </button>

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
            Add Career Goal
          </button>
        </div>
      )}


      {isFormOpen && (
        <form
          className="profile-manager-form"
          onSubmit={handleSubmit}
        >
          <div className="profile-field">
            <label htmlFor="target_role">
              Target Role
            </label>

            <input
              id="target_role"
              name="target_role"
              type="text"
              value={
                careerGoalForm
                  .target_role
              }
              onChange={handleChange}
            />
          </div>


          <div className="profile-field profile-field--full">
            <label htmlFor="career_goal_description">
              Description
            </label>

            <textarea
              id="career_goal_description"
              name="description"
              value={
                careerGoalForm
                  .description
              }
              onChange={handleChange}
            />
          </div>


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
              {
                editingIndex ===
                null
                  ? 'Add Career Goal'
                  : 'Update Career Goal'
              }
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


export default CareerGoalsSection