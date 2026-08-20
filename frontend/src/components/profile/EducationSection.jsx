import { useState } from 'react'

function EducationSection() {
  const [educationItems, setEducationItems] = useState([])
  const [educationForm, setEducationForm] = useState({
    institution_name: '',
    qualification: '',
    field_of_study: '',
    start_date: '',
    end_date: '',
    description: '',
  })

  function handleChange(event) {
    const { name, value } = event.target

    setEducationForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    setEducationItems((currentItems) => [
      ...currentItems,
      educationForm,
    ])

    setEducationForm({
      institution_name: '',
      qualification: '',
      field_of_study: '',
      start_date: '',
      end_date: '',
      description: '',
    })
  }

  function handleRemove(indexToRemove) {
    setEducationItems((currentItems) =>
      currentItems.filter((_, index) => index !== indexToRemove),
    )
  }

  return (
    <section>
      <h2>Education</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="institution_name">Institution</label>
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
          <label htmlFor="qualification">Qualification</label>
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
          <label htmlFor="field_of_study">Field of Study</label>
          <input
            id="field_of_study"
            name="field_of_study"
            type="text"
            value={educationForm.field_of_study}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="start_date">Start Date</label>
          <input
            id="start_date"
            name="start_date"
            type="date"
            value={educationForm.start_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="end_date">End Date</label>
          <input
            id="end_date"
            name="end_date"
            type="date"
            value={educationForm.end_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={educationForm.description}
            onChange={handleChange}
          />
        </div>

        <button type="submit">Add Education</button>
      </form>

      {educationItems.length > 0 && (
        <div>
          <h3>Education History</h3>

          {educationItems.map((education, index) => (
            <article key={`${education.institution_name}-${index}`}>
              <h4>{education.qualification}</h4>
              <p>{education.institution_name}</p>
              <p>{education.field_of_study}</p>
              <p>
                {education.start_date} to {education.end_date || 'Present'}
              </p>
              <p>{education.description}</p>

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