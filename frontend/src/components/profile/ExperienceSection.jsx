import { useState } from 'react'

function ExperienceSection() {
  const [experienceItems, setExperienceItems] = useState([])
  const [experienceForm, setExperienceForm] = useState({
    job_title: '',
    company: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
  })

  function handleChange(event) {
    const { name, value, type, checked } = event.target

    setExperienceForm((currentForm) => ({
      ...currentForm,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  function handleCurrentRoleChange(event) {
    const isCurrent = event.target.checked

    setExperienceForm((currentForm) => ({
      ...currentForm,
      is_current: isCurrent,
      end_date: isCurrent ? '' : currentForm.end_date,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    setExperienceItems((currentItems) => [
      ...currentItems,
      experienceForm,
    ])

    setExperienceForm({
      job_title: '',
      company: '',
      start_date: '',
      end_date: '',
      is_current: false,
      description: '',
    })
  }

  function handleRemove(indexToRemove) {
    setExperienceItems((currentItems) =>
      currentItems.filter((_, index) => index !== indexToRemove),
    )
  }

  return (
    <section>
      <h2>Experience</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="job_title">Job Title</label>
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
          <label htmlFor="company">Company</label>
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
          <label htmlFor="experience_start_date">Start Date</label>
          <input
            id="experience_start_date"
            name="start_date"
            type="date"
            value={experienceForm.start_date}
            onChange={handleChange}
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
          <label htmlFor="experience_end_date">End Date</label>
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
          <label htmlFor="experience_description">Description</label>
          <textarea
            id="experience_description"
            name="description"
            value={experienceForm.description}
            onChange={handleChange}
          />
        </div>

        <button type="submit">Add Experience</button>
      </form>

      {experienceItems.length > 0 && (
        <div>
          <h3>Experience History</h3>

          {experienceItems.map((experience, index) => (
            <article key={`${experience.company}-${experience.job_title}-${index}`}>
              <h4>{experience.job_title}</h4>

              <p>{experience.company}</p>

              <p>
                {experience.start_date} to{' '}
                {experience.is_current
                  ? 'Present'
                  : experience.end_date || 'Not specified'}
              </p>

              <p>{experience.description}</p>

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