import { useState } from 'react'

import {
  searchProfileCareers,
} from '../../services/profileService'

import SearchableReferenceField from './SearchableReferenceField'


function createEmptyCareerGoalForm(
  isFirstGoal = false,
) {
  return {
    selectedCareer: null,
    description: '',
    is_primary: isFirstGoal,
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
    createEmptyCareerGoalForm(
      items.length === 0,
    ),
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
      createEmptyCareerGoalForm(
        items.length === 0,
      ),
    )

    setEditingIndex(null)
    setIsFormOpen(false)
    setError('')
  }


  function handleCareerSelect(
    career,
  ) {
    setCareerGoalForm(
      (currentForm) => ({
        ...currentForm,

        selectedCareer:
          career,
      }),
    )

    setError('')
  }


  function handleDescriptionChange(
    event,
  ) {
    setCareerGoalForm(
      (currentForm) => ({
        ...currentForm,

        description:
          event.target.value,
      }),
    )

    setError('')
  }


  function handlePrimaryChange(
    event,
  ) {
    setCareerGoalForm(
      (currentForm) => ({
        ...currentForm,

        is_primary:
          event.target.checked,
      }),
    )

    setError('')
  }


  function handleAdd() {
    setCareerGoalForm(
      createEmptyCareerGoalForm(
        items.length === 0,
      ),
    )

    setEditingIndex(null)
    setError('')
    setIsFormOpen(true)
  }


  function handleEdit(
    index,
  ) {
    const careerGoal =
      items[index]

    setCareerGoalForm({
      selectedCareer:
        careerGoal.career_id
          ? {
              id:
                careerGoal
                  .career_id,

              name:
                careerGoal
                  .target_role,

              category: '',
            }
          : null,

      description:
        careerGoal.description || '',

      is_primary:
        Boolean(
          careerGoal.is_primary,
        ),
    })

    setEditingIndex(index)
    setError('')
    setIsFormOpen(true)
  }


  function handleSubmit(
    event,
  ) {
    event.preventDefault()

    if (
      !careerGoalForm
        .selectedCareer
    ) {
      setError(
        'Select a Career from the GradNavi catalogue.',
      )

      return
    }


    const selectedCareerId =
      careerGoalForm
        .selectedCareer
        .id


    const duplicateCareer =
      items.some(
        (
          careerGoal,
          index,
        ) =>
          index !==
            editingIndex &&
          careerGoal
            .career_id ===
            selectedCareerId,
      )


    if (duplicateCareer) {
      setError(
        'This Career Goal has already been added.',
      )

      return
    }


    const nextCareerGoal = {
      career_id:
        selectedCareerId,

      target_role:
        careerGoalForm
          .selectedCareer
          .name,

      description:
        careerGoalForm
          .description
          .trim(),

      is_primary:
        Boolean(
          careerGoalForm
            .is_primary,
        ),
    }


    let nextItems


    if (
      editingIndex ===
      null
    ) {
      nextItems = [
        ...items,
        nextCareerGoal,
      ]

      if (
        nextCareerGoal
          .is_primary
      ) {
        nextItems =
          nextItems.map(
            (
              careerGoal,
              index,
            ) => ({
              ...careerGoal,

              is_primary:
                index ===
                nextItems.length - 1,
            }),
          )
      }
    } else {
      nextItems =
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

            return {
              ...careerGoal,
              ...nextCareerGoal,
            }
          },
        )


      if (
        nextCareerGoal
          .is_primary
      ) {
        nextItems =
          nextItems.map(
            (
              careerGoal,
              index,
            ) => ({
              ...careerGoal,

              is_primary:
                index ===
                editingIndex,
            }),
          )
      }
    }


    onChange(
      nextItems,
    )

    resetForm()
  }


  function handleRemove(
    indexToRemove,
  ) {
    const removedGoal =
      items[
        indexToRemove
      ]

    let nextItems =
      items.filter(
        (
          _,
          index,
        ) =>
          index !==
          indexToRemove,
      )


    if (
      removedGoal
        ?.is_primary &&
      nextItems.length > 0 &&
      !nextItems.some(
        (careerGoal) =>
          careerGoal
            .is_primary,
      )
    ) {
      nextItems =
        nextItems.map(
          (
            careerGoal,
            index,
          ) => ({
            ...careerGoal,

            is_primary:
              index === 0,
          }),
        )
    }


    onChange(
      nextItems,
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


  const excludedCareerIds =
    items
      .filter(
        (
          _,
          index,
        ) =>
          index !==
          editingIndex,
      )
      .map(
        (careerGoal) =>
          careerGoal
            .career_id,
      )
      .filter(
        Boolean,
      )


  const primaryLocked =
    (
      editingIndex ===
        null &&
      items.length === 0
    ) ||
    (
      editingIndex !==
        null &&
      Boolean(
        items[
          editingIndex
        ]?.is_primary,
      )
    )


  return (
    <section className="profile-manager-section">
      <div className="profile-manager-heading">
        <div>
          <h3>
            Career Goals
          </h3>

          <p>
            Search active GradNavi Careers,
            add your goals, and choose one
            primary Career Goal.
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
            No Career Goals added yet.
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
                  careerGoal
                    .career_id ||
                  `${careerGoal.target_role}-${index}`
                }
              >
                <div className="profile-manager-record__content">
                  <div className="profile-career-goal-title">
                    <strong>
                      {
                        careerGoal
                          .target_role
                      }
                    </strong>

                    {
                      careerGoal
                        .is_primary && (
                        <span className="profile-primary-badge">
                          Primary
                        </span>
                      )
                    }
                  </div>

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
            onClick={
              handleAdd
            }
          >
            Add Career Goal
          </button>
        </div>
      )}


      {isFormOpen && (
        <form
          className="profile-manager-form"
          onSubmit={
            handleSubmit
          }
        >
          <SearchableReferenceField
            id="career-reference-search"
            label="Career"
            placeholder="Search Careers, for example software"
            searchReference={
              searchProfileCareers
            }
            selectedItem={
              careerGoalForm
                .selectedCareer
            }
            onSelect={
              handleCareerSelect
            }
            excludedIds={
              excludedCareerIds
            }
            helperText="Search the 36 active Careers and select one approved Career record."
          />


          <div className="profile-field">
            <label className="profile-checkbox-field">
              <input
                type="checkbox"
                checked={
                  careerGoalForm
                    .is_primary
                }
                disabled={
                  primaryLocked
                }
                onChange={
                  handlePrimaryChange
                }
              />

              Primary Career Goal
            </label>

            <p className="profile-reference-search__helper">
              {
                primaryLocked
                  ? 'A profile must keep one primary Career Goal. To change the primary goal, edit another goal and mark it primary.'
                  : 'Mark this goal as the main Career used for your profile.'
              }
            </p>
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
              placeholder="Optional details about this Career Goal"
              onChange={
                handleDescriptionChange
              }
            />
          </div>


          {
            careerGoalForm
              .selectedCareer && (
              <p className="profile-reference-detail">
                Selected:{' '}
                {
                  careerGoalForm
                    .selectedCareer
                    .name
                }
              </p>
            )
          }


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


export default CareerGoalsSection
