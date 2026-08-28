import { useState } from 'react'

function createEmptyProjectForm() {
  return {
    name: '',
    description: '',
    project_url: '',
    start_date: '',
    end_date: '',
  }
}

function ProjectSection({
  items,
  onChange,
}) {
  const [projectForm, setProjectForm] = useState(
    createEmptyProjectForm,
  )
  const [editingIndex, setEditingIndex] = useState(null)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setProjectForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))

    setError('')
  }

  function validateForm() {
    if (
      !projectForm.name.trim() ||
      !projectForm.start_date
    ) {
      return 'Project name and start date are required.'
    }

    if (
      projectForm.end_date &&
      projectForm.end_date < projectForm.start_date
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

    const nextProject = {
      name: projectForm.name.trim(),
      description:
        projectForm.description.trim(),
      project_url:
        projectForm.project_url.trim(),
      start_date:
        projectForm.start_date,
      end_date:
        projectForm.end_date,
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        nextProject,
      ])
    } else {
      onChange(
        items.map((project, index) => {
          if (index !== editingIndex) {
            return project
          }

          return {
            ...project,
            ...nextProject,
          }
        }),
      )
    }

    setProjectForm(createEmptyProjectForm())
    setEditingIndex(null)
    setError('')
  }

  function handleEdit(index) {
    const project = items[index]

    setProjectForm({
      name:
        project.name || '',
      description:
        project.description || '',
      project_url:
        project.project_url || '',
      start_date:
        project.start_date || '',
      end_date:
        project.end_date || '',
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
    setProjectForm(createEmptyProjectForm())
    setEditingIndex(null)
    setError('')
  }

  return (
    <section className="profile-section">
      <h2>Projects</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="project_name">
            Project Name
          </label>

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
          <label htmlFor="project_url">
            Project URL
          </label>

          <input
            id="project_url"
            name="project_url"
            type="url"
            value={projectForm.project_url}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="project_start_date">
            Start Date
          </label>

          <input
            id="project_start_date"
            name="start_date"
            type="date"
            value={projectForm.start_date}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="project_end_date">
            End Date
          </label>

          <input
            id="project_end_date"
            name="end_date"
            type="date"
            value={projectForm.end_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="project_description">
            Description
          </label>

          <textarea
            id="project_description"
            name="description"
            value={projectForm.description}
            onChange={handleChange}
          />
        </div>

        {error && (
          <p role="alert">{error}</p>
        )}

        <button type="submit">
          {editingIndex === null
            ? 'Add Project'
            : 'Update Project'}
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
          <h3>Project History</h3>

          {items.map((project, index) => (
            <article
              className="profile-item"
              key={
                project.id ||
                `${project.name}-${index}`
              }
            >
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
                {project.start_date} to{' '}
                {project.end_date || 'Present'}
              </p>

              {project.description && (
                <p>{project.description}</p>
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

export default ProjectSection