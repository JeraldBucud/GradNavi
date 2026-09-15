import { useState } from 'react'


function createEmptyEducationForm() {
  return {
    institution_name: '',
    qualification: '',
    field_of_study: '',
    start_date: '',
    end_date: '',
    description: '',
  }
}


function EducationSection({
  items,
  onChange,
}) {
  const [
    educationForm,
    setEducationForm,
  ] = useState(
    createEmptyEducationForm,
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
    setEducationForm(
      createEmptyEducationForm(),
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

    setEducationForm(
      (currentForm) => ({
        ...currentForm,
        [name]: value,
      }),
    )

    setError('')
  }


  function handleAdd() {
    setEducationForm(
      createEmptyEducationForm(),
    )

    setEditingIndex(null)
    setError('')
    setIsFormOpen(true)
  }


  function handleEdit(index) {
    const education = items[index]

    setEducationForm({
      institution_name:
        education.institution_name || '',
      qualification:
        education.qualification || '',
      field_of_study:
        education.field_of_study || '',
      start_date:
        education.start_date || '',
      end_date:
        education.end_date || '',
      description:
        education.description || '',
    })

    setEditingIndex(index)
    setError('')
    setIsFormOpen(true)
  }


  function validateForm() {
    if (
      !educationForm.institution_name.trim() ||
      !educationForm.qualification.trim() ||
      !educationForm.field_of_study.trim() ||
      !educationForm.start_date
    ) {
      return (
        'Institution, qualification, field of study, ' +
        'and start date are required.'
      )
    }

    if (
      educationForm.end_date &&
      educationForm.end_date <
        educationForm.start_date
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

    const nextEducation = {
      institution_name:
        educationForm.institution_name.trim(),

      qualification:
        educationForm.qualification.trim(),

      field_of_study:
        educationForm.field_of_study.trim(),

      start_date:
        educationForm.start_date,

      end_date:
        educationForm.end_date,

      description:
        educationForm.description.trim(),
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        nextEducation,
      ])
    } else {
      onChange(
        items.map(
          (education, index) => {
            if (index !== editingIndex) {
              return education
            }

            /*
             * Spread the existing record first.
             *
             * This preserves the backend-provided ID
             * while changing editable values.
             */
            return {
              ...education,
              ...nextEducation,
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
      id="education"
      className="profile-evidence-group"
    >
      <div className="profile-evidence-group__heading">
        <div>
          <h3>
            Education
          </h3>

          <p>
            Qualifications and study history.
          </p>
        </div>

        {!isFormOpen && (
          <button
            className="profile-evidence-add"
            type="button"
            onClick={handleAdd}
          >
            Add Education
          </button>
        )}
      </div>


      <div className="profile-evidence-records">
        {items.length === 0 ? (
          <div className="profile-evidence-empty">
            No education records added.
          </div>
        ) : (
          items.map(
            (education, index) => (
              <article
                className="profile-evidence-record"
                key={
                  education.id ||
                  `${education.institution_name}-${index}`
                }
              >
                <div className="profile-evidence-record__content">
                  <strong>
                    {education.qualification}
                  </strong>

                  <span>
                    {education.institution_name}
                  </span>

                  <span>
                    {education.field_of_study}
                  </span>

                  <span>
                    {education.start_date}
                    {' to '}
                    {
                      education.end_date ||
                      'Present'
                    }
                  </span>

                  {education.description && (
                    <p>
                      {education.description}
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
              <label htmlFor="institution_name">
                Institution
              </label>

              <input
                id="institution_name"
                name="institution_name"
                type="text"
                value={
                  educationForm.institution_name
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="qualification">
                Qualification
              </label>

              <input
                id="qualification"
                name="qualification"
                type="text"
                value={
                  educationForm.qualification
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="field_of_study">
                Field of Study
              </label>

              <input
                id="field_of_study"
                name="field_of_study"
                type="text"
                value={
                  educationForm.field_of_study
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="education_start_date">
                Start Date
              </label>

              <input
                id="education_start_date"
                name="start_date"
                type="date"
                value={
                  educationForm.start_date
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="education_end_date">
                End Date
              </label>

              <input
                id="education_end_date"
                name="end_date"
                type="date"
                value={
                  educationForm.end_date
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field profile-field--full">
              <label htmlFor="education_description">
                Description
              </label>

              <textarea
                id="education_description"
                name="description"
                value={
                  educationForm.description
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
                ? 'Add Education'
                : 'Update Education'}
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


export default EducationSection