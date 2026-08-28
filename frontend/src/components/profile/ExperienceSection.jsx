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
  const [experienceForm, setExperienceForm] = useState(
    createEmptyExperienceForm,
  )
  const [editingIndex, setEditingIndex] = useState(null)
  const [error, setError] = useState('')

  function handleChange(event) {
    const {
      name,
      value,
      type,
      checked,
    } = event.target

    setExperienceForm((currentForm) => ({
      ...currentForm,
      [name]:
        type === 'checkbox'
          ? checked
          : value,
    }))

    setError('')
  }

  function handleCurrentRoleChange(event) {
    const isCurrent = event.target.checked

    setExperienceForm((currentForm) => ({
      ...currentForm,
      is_current: isCurrent,
      end_date:
        isCurrent
          ? ''
          : currentForm.end_date,
    }))

    setError('')
  }

  function validateForm() {
    if (
      !experienceForm.job_title.trim() ||
      !experienceForm.company.trim() ||
      !experienceForm.start_date
    ) {
      return 'Job title, company, and start date are required.'
    }

    if (
      !experienceForm.is_current &&
      experienceForm.end_date &&
      experienceForm.end_date <
        experienceForm.start_date
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
        items.map((experience, index) => {
          if (index !== editingIndex) {
            return experience
          }

          return {
            ...experience,
            ...nextExperience,
          }
        }),
      )
    }

    setExperienceForm(
      createEmptyExperienceForm(),
    )
    setEditingIndex(null)
    setError('')
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
        Boolean(experience.is_current),
      description:
        experience.description || '',
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
    setExperienceForm(
      createEmptyExperienceForm(),
    )
    setEditingIndex(null)
    setError('')
  }

  return (
    <section className="profile-section">
      <h2>Experience</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="job_title">
            Job Title
          </label>

          <input
            id="job_title"
            name="job_title"
            type="text"
            value={experienceForm.job_title}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="company">
            Company
          </label>

          <input
            id="company"
            name="company"
            type="text"
            value={experienceForm.company}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="experience_start_date">
            Start Date
          </label>

          <input
            id="experience_start_date"
            name="start_date"
            type="date"
            value={experienceForm.start_date}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>
            <input
              name="is_current"
              type="checkbox"
              checked={experienceForm.is_current}
              onChange={handleCurrentRoleChange}
            />
            I currently work here
          </label>
        </div>

        <div>
          <label htmlFor="experience_end_date">
            End Date
          </label>

          <input
            id="experience_end_date"
            name="end_date"
            type="date"
            value={experienceForm.end_date}
            onChange={handleChange}
            disabled={experienceForm.is_current}
          />
        </div>

        <div>
          <label htmlFor="experience_description">
            Description
          </label>

          <textarea
            id="experience_description"
            name="description"
            value={experienceForm.description}
            onChange={handleChange}
          />
        </div>

        {error && (
          <p role="alert">{error}</p>
        )}

        <button type="submit">
          {editingIndex === null
            ? 'Add Experience'
            : 'Update Experience'}
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
          <h3>Experience History</h3>

          {items.map((experience, index) => (
            <article
              className="profile-item"
              key={
                experience.id ||
                `${experience.company}-${experience.job_title}-${index}`
              }
            >
              <h4>{experience.job_title}</h4>

              <p>{experience.company}</p>

              <p>
                {experience.start_date} to{' '}
                {experience.is_current
                  ? 'Present'
                  : experience.end_date ||
                    'Not specified'}
              </p>

              {experience.description && (
                <p>{experience.description}</p>
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

export default ExperienceSection