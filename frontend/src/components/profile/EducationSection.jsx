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
  const [educationForm, setEducationForm] = useState(
    createEmptyEducationForm,
  )
  const [editingIndex, setEditingIndex] = useState(null)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setEducationForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))

    setError('')
  }

  function validateForm() {
    if (
      !educationForm.institution_name.trim() ||
      !educationForm.qualification.trim() ||
      !educationForm.field_of_study.trim() ||
      !educationForm.start_date
    ) {
      return 'Institution, qualification, field of study, and start date are required.'
    }

    if (
      educationForm.end_date &&
      educationForm.end_date < educationForm.start_date
    ) {
      return 'End date must not be earlier than start date.'
    }

    return ''
  }

  function handleSubmit(event) {
    event.preventDefault()

    const validationError = validateForm()

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
      start_date: educationForm.start_date,
      end_date: educationForm.end_date,
      description:
        educationForm.description.trim(),
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        nextEducation,
      ])
    } else {
      const updatedItems = items.map(
        (education, index) => {
          if (index !== editingIndex) {
            return education
          }

          return {
            ...education,
            ...nextEducation,
          }
        },
      )

      onChange(updatedItems)
    }

    setEducationForm(createEmptyEducationForm())
    setEditingIndex(null)
    setError('')
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
    setEducationForm(createEmptyEducationForm())
    setEditingIndex(null)
    setError('')
  }

  return (
    <section className="profile-section">
      <h2>Education</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="institution_name">
            Institution
          </label>

          <input
            id="institution_name"
            name="institution_name"
            type="text"
            value={educationForm.institution_name}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="qualification">
            Qualification
          </label>

          <input
            id="qualification"
            name="qualification"
            type="text"
            value={educationForm.qualification}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="field_of_study">
            Field of Study
          </label>

          <input
            id="field_of_study"
            name="field_of_study"
            type="text"
            value={educationForm.field_of_study}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="start_date">
            Start Date
          </label>

          <input
            id="start_date"
            name="start_date"
            type="date"
            value={educationForm.start_date}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="end_date">
            End Date
          </label>

          <input
            id="end_date"
            name="end_date"
            type="date"
            value={educationForm.end_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="education_description">
            Description
          </label>

          <textarea
            id="education_description"
            name="description"
            value={educationForm.description}
            onChange={handleChange}
          />
        </div>

        {error && (
          <p role="alert">{error}</p>
        )}

        <button type="submit">
          {editingIndex === null
            ? 'Add Education'
            : 'Update Education'}
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
          <h3>Education History</h3>

          {items.map((education, index) => (
            <article
              className="profile-item"
              key={
                education.id ||
                `${education.institution_name}-${index}`
              }
            >
              <h4>{education.qualification}</h4>

              <p>{education.institution_name}</p>
              <p>{education.field_of_study}</p>

              <p>
                {education.start_date} to{' '}
                {education.end_date || 'Present'}
              </p>

              {education.description && (
                <p>{education.description}</p>
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

export default EducationSection