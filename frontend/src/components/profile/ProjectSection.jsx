import { useState } from 'react'

function ProjectSection() {
  const [projectItems, setProjectItems] = useState([])
  const [projectForm, setProjectForm] = useState({
    name: '',
    description: '',
    project_url: '',
    start_date: '',
    end_date: '',
  })

  function handleChange(event) {
    const { name, value } = event.target

    setProjectForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    setProjectItems((currentItems) => [
      ...currentItems,
      projectForm,
    ])

    setProjectForm({
      name: '',
      description: '',
      project_url: '',
      start_date: '',
      end_date: '',
    })
  }

  function handleRemove(indexToRemove) {
    setProjectItems((currentItems) =>
      currentItems.filter((_, index) => index !== indexToRemove),
    )
  }

  return (
    <section className="profile-section">
      <h2>Projects</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="project_name">Project Name</label>
          <input
            id="project_name"
            name="name"
            type="text"
            value={projectForm.name}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="project_url">Project URL</label>
          <input
            id="project_url"
            name="project_url"
            type="url"
            value={projectForm.project_url}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="project_start_date">Start Date</label>
          <input
            id="project_start_date"
            name="start_date"
            type="date"
            value={projectForm.start_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="project_end_date">End Date</label>
          <input
            id="project_end_date"
            name="end_date"
            type="date"
            value={projectForm.end_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="project_description">Description</label>
          <textarea
            id="project_description"
            name="description"
            value={projectForm.description}
            onChange={handleChange}
          />
        </div>

        <button type="submit">Add Project</button>
      </form>

      {projectItems.length > 0 && (
        <div>
          <h3>Project History</h3>

          {projectItems.map((project, index) => (
            <article
            className="profile-item"
            key={`${project.name}-${index}`}>
              <h4>{project.name}</h4>

              {project.project_url && (
                <p>
                  <a
                    href={project.project_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View Project
                  </a>
                </p>
              )}

              <p>
                {project.start_date || 'Start date not specified'} to{' '}
                {project.end_date || 'Present'}
              </p>

              <p>{project.description}</p>

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

export default ProjectSection