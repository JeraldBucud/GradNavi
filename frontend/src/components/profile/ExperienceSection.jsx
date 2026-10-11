import { useState } from 'react'


function createEmptyExperienceForm() {
  return {
    job_title: '',
    company: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
  }
}


function ExperienceSection({
  items,
  onChange,
}) {
  const [
    experienceForm,
    setExperienceForm,
  ] = useState(
    createEmptyExperienceForm,
  )

  const [
    editingIndex,
    setEditingIndex,
  ] = useState(null)

  const [
    isFormOpen,
    setIsFormOpen,
  ] = useState(false)

  const [error, setError] =
    useState('')


  function resetForm() {
    setExperienceForm(
      createEmptyExperienceForm(),
    )

    setEditingIndex(null)
    setError('')
    setIsFormOpen(false)
  }


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setExperienceForm(
      (currentForm) => ({
        ...currentForm,
        [name]: value,
      }),
    )

    setError('')
  }


  function handleCurrentRoleChange(
    event,
  ) {
    const isCurrent =
      event.target.checked

    setExperienceForm(
      (currentForm) => ({
        ...currentForm,

        is_current:
          isCurrent,

        end_date:
          isCurrent
            ? ''
            : currentForm.end_date,
      }),
    )

    setError('')
  }


  function handleAdd() {
    setExperienceForm(
      createEmptyExperienceForm(),
    )

    setEditingIndex(null)
    setError('')
    setIsFormOpen(true)
  }


  function handleEdit(index) {
    const experience = items[index]

    setExperienceForm({
      job_title:
        experience.job_title || '',

      company:
        experience.company || '',

      start_date:
        experience.start_date || '',

      end_date:
        experience.end_date || '',

      is_current:
        Boolean(
          experience.is_current,
        ),

      description:
        experience.description || '',
    })

    setEditingIndex(index)
    setError('')
    setIsFormOpen(true)
  }


  function validateForm() {
    if (
      !experienceForm.job_title.trim() ||
      !experienceForm.company.trim() ||
      !experienceForm.start_date
    ) {
      return (
        'Job title, company, and start date ' +
        'are required.'
      )
    }

    if (
      !experienceForm.is_current &&
      experienceForm.end_date &&
      experienceForm.end_date <
        experienceForm.start_date
    ) {
      return (
        'End date must not be earlier than ' +
        'start date.'
      )
    }

    return ''
  }


  function handleSubmit(event) {
    event.preventDefault()

    const validationError =
      validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    const nextExperience = {
      job_title:
        experienceForm.job_title.trim(),

      company:
        experienceForm.company.trim(),

      start_date:
        experienceForm.start_date,

      end_date:
        experienceForm.is_current
          ? ''
          : experienceForm.end_date,

      is_current:
        experienceForm.is_current,

      description:
        experienceForm.description.trim(),
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        nextExperience,
      ])
    } else {
      onChange(
        items.map(
          (experience, index) => {
            if (index !== editingIndex) {
              return experience
            }

            return {
              ...experience,
              ...nextExperience,
            }
          },
        ),
      )
    }

    resetForm()
  }


  function handleRemove(indexToRemove) {
    onChange(
      items.filter(
        (_, index) =>
          index !== indexToRemove,
      ),
    )

    if (
      editingIndex === indexToRemove
    ) {
      resetForm()
      return
    }

    if (
      editingIndex !== null &&
      editingIndex > indexToRemove
    ) {
      setEditingIndex(
        (currentIndex) =>
          currentIndex - 1,
      )
    }
  }


  return (
    <section
      id="experience"
      className="profile-evidence-group"
    >
      <div className="profile-evidence-group__heading">
        <div>
          <h3>
            Experience
          </h3>

          <p>
            Employment and professional experience.
          </p>
        </div>

        {!isFormOpen && (
          <button
            className="profile-evidence-add"
            type="button"
            onClick={handleAdd}
          >
            Add Experience
          </button>
        )}
      </div>


      <div className="profile-evidence-records">
        {items.length === 0 ? (
          <div className="profile-evidence-empty">
            No experience records added.
          </div>
        ) : (
          items.map(
            (experience, index) => (
              <article
                className="profile-evidence-record"
                key={
                  experience.id ||
                  `${experience.company}-${experience.job_title}-${index}`
                }
              >
                <div className="profile-evidence-record__content">
                  <strong>
                    {experience.job_title}
                  </strong>

                  <span>
                    {experience.company}
                  </span>

                  <span>
                    {experience.start_date}
                    {' to '}
                    {
                      experience.is_current
                        ? 'Present'
                        : experience.end_date ||
                          'Not specified'
                    }
                  </span>

                  {experience.description && (
                    <p>
                      {experience.description}
                    </p>
                  )}
                </div>

                <div className="profile-evidence-record__actions">
                  <button
                    className="profile-text-action"
                    type="button"
                    onClick={() =>
                      handleEdit(index)
                    }
                  >
                    Edit
                  </button>

                  <button
                    className="profile-text-action profile-text-action--danger"
                    type="button"
                    onClick={() =>
                      handleRemove(index)
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


      {isFormOpen && (
        <form
          className="profile-evidence-form"
          onSubmit={handleSubmit}
        >
          <div className="profile-evidence-form__grid">
            <div className="profile-field">
              <label htmlFor="job_title">
                Job Title
              </label>

              <input
                id="job_title"
                name="job_title"
                type="text"
                value={
                  experienceForm.job_title
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="company">
                Company
              </label>

              <input
                id="company"
                name="company"
                type="text"
                value={
                  experienceForm.company
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="experience_start_date">
                Start Date
              </label>

              <input
                id="experience_start_date"
                name="start_date"
                type="date"
                value={
                  experienceForm.start_date
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="experience_end_date">
                End Date
              </label>

              <input
                id="experience_end_date"
                name="end_date"
                type="date"
                value={
                  experienceForm.end_date
                }
                onChange={handleChange}
                disabled={
                  experienceForm.is_current
                }
              />
            </div>


            <div className="profile-field profile-field--full">
              <label className="profile-checkbox-field">
                <input
                  name="is_current"
                  type="checkbox"
                  checked={
                    experienceForm.is_current
                  }
                  onChange={
                    handleCurrentRoleChange
                  }
                />

                <span>
                  I currently work here
                </span>
              </label>
            </div>


            <div className="profile-field profile-field--full">
              <label htmlFor="experience_description">
                Description
              </label>

              <textarea
                id="experience_description"
                name="description"
                value={
                  experienceForm.description
                }
                onChange={handleChange}
              />
            </div>
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
              {editingIndex === null
                ? 'Add Experience'
                : 'Update Experience'}
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


export default ExperienceSection