import { useState } from 'react'

import {
  ExternalLink,
} from 'lucide-react'


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
  const [
    projectForm,
    setProjectForm,
  ] = useState(
    createEmptyProjectForm,
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
    setProjectForm(
      createEmptyProjectForm(),
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

    setProjectForm(
      (currentForm) => ({
        ...currentForm,
        [name]: value,
      }),
    )

    setError('')
  }


  function handleAdd() {
    setProjectForm(
      createEmptyProjectForm(),
    )

    setEditingIndex(null)
    setError('')
    setIsFormOpen(true)
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
    setIsFormOpen(true)
  }


  function validateForm() {
    if (
      !projectForm.name.trim() ||
      !projectForm.start_date
    ) {
      return (
        'Project name and start date are required.'
      )
    }

    if (
      projectForm.end_date &&
      projectForm.end_date <
        projectForm.start_date
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

    const nextProject = {
      name:
        projectForm.name.trim(),

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
        items.map(
          (project, index) => {
            if (index !== editingIndex) {
              return project
            }

            return {
              ...project,
              ...nextProject,
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
      id="projects"
      className="profile-evidence-group"
    >
      <div className="profile-evidence-group__heading">
        <div>
          <h3>
            Projects
          </h3>

          <p>
            Portfolio and project evidence.
          </p>
        </div>

        {!isFormOpen && (
          <button
            className="profile-evidence-add"
            type="button"
            onClick={handleAdd}
          >
            Add Project
          </button>
        )}
      </div>


      <div className="profile-evidence-records">
        {items.length === 0 ? (
          <div className="profile-evidence-empty">
            No project records added.
          </div>
        ) : (
          items.map(
            (project, index) => (
              <article
                className="profile-evidence-record"
                key={
                  project.id ||
                  `${project.name}-${index}`
                }
              >
                <div className="profile-evidence-record__content">
                  <strong>
                    {project.name}
                  </strong>

                  <span>
                    {project.start_date}
                    {' to '}
                    {
                      project.end_date ||
                      'Present'
                    }
                  </span>

                  {project.description && (
                    <p>
                      {project.description}
                    </p>
                  )}

                  {project.project_url && (
                    <a
                      className="profile-project-link"
                      href={
                        project.project_url
                      }
                      target="_blank"
                      rel="noreferrer"
                    >
                      <ExternalLink
                        size={14}
                        strokeWidth={1.8}
                        aria-hidden="true"
                      />

                      <span>
                        View Project
                      </span>
                    </a>
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
              <label htmlFor="project_name">
                Project Name
              </label>

              <input
                id="project_name"
                name="name"
                type="text"
                value={
                  projectForm.name
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="project_url">
                Project URL
              </label>

              <input
                id="project_url"
                name="project_url"
                type="url"
                placeholder="https://example.com"
                value={
                  projectForm.project_url
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="project_start_date">
                Start Date
              </label>

              <input
                id="project_start_date"
                name="start_date"
                type="date"
                value={
                  projectForm.start_date
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field">
              <label htmlFor="project_end_date">
                End Date
              </label>

              <input
                id="project_end_date"
                name="end_date"
                type="date"
                value={
                  projectForm.end_date
                }
                onChange={handleChange}
              />
            </div>


            <div className="profile-field profile-field--full">
              <label htmlFor="project_description">
                Description
              </label>

              <textarea
                id="project_description"
                name="description"
                value={
                  projectForm.description
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
                ? 'Add Project'
                : 'Update Project'}
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


export default ProjectSection