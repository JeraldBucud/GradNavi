import {
  useEffect,
  useState,
} from 'react'

import {
  createAdminLearningResource,
  listAdminLearningResources,
  listAdminSkills,
  updateAdminLearningResource,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'
import './AdminCareersPage.css'


const PAGE_SIZE = 50

const RESOURCE_TYPES = [
  { value: 'course', label: 'Course' },
  { value: 'documentation', label: 'Documentation' },
  { value: 'article', label: 'Article' },
  { value: 'video', label: 'Video' },
  { value: 'tutorial', label: 'Tutorial' },
  { value: 'book', label: 'Book' },
  { value: 'other', label: 'Other' },
]

const ACCESS_TYPES = [
  { value: 'free', label: 'Free' },
  { value: 'freemium', label: 'Freemium' },
  { value: 'paid', label: 'Paid' },
  { value: 'unknown', label: 'Unknown' },
]

const SOURCE_TYPES = [
  { value: 'curated', label: 'Curated' },
  { value: 'discovered', label: 'Discovered' },
]

const HEALTH_STATUSES = [
  { value: 'active', label: 'Active' },
  { value: 'needs_review', label: 'Needs review' },
  { value: 'broken', label: 'Broken' },
  { value: 'archived', label: 'Archived' },
]

const HEALTH_PILLS = {
  active: 'admin-users__pill--active',
  needs_review: 'admin-users__pill--inactive',
  broken: 'admin-users__pill--danger',
  archived: 'admin-users__pill--student',
}

const EMPTY_FORM = {
  title: '',
  resource_key: '',
  provider: '',
  url: '',
  resource_type: 'other',
  description: '',
  is_active: true,
  access_type: 'unknown',
  source_type: 'curated',
  health_status: 'active',
  skill_ids: [],
}

const ERROR_FIELDS = [
  ['title', 'Title'],
  ['resource_key', 'Resource key'],
  ['url', 'URL'],
  ['skill_ids', 'Skills'],
]


function getLabel(options, value) {
  const match = options.find((option) => option.value === value)

  return match ? match.label : value
}


function slugify(value) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 120)
}


function findFieldError(data, field) {
  if (!data || typeof data !== 'object') {
    return null
  }

  if (field in data) {
    const value = data[field]

    if (Array.isArray(value) && value.length > 0) {
      return String(value[0])
    }

    if (typeof value === 'string') {
      return value
    }
  }

  for (const value of Object.values(data)) {
    const found = findFieldError(value, field)

    if (found) {
      return found
    }
  }

  return null
}


function getErrorMessage(error, fallback) {
  for (const [field, label] of ERROR_FIELDS) {
    const fieldError = findFieldError(error?.data, field)

    if (fieldError) {
      return `${label}: ${fieldError}`
    }
  }

  return error?.message || fallback
}


function AdminLearningResourcesPage() {
  const [resources, setResources] = useState([])
  const [skills, setSkills] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [healthFilter, setHealthFilter] = useState('all')
  const [activeFilter, setActiveFilter] = useState('all')
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)
  const [successMessage, setSuccessMessage] = useState('')

  const [formMode, setFormMode] = useState(null)
  const [editingResource, setEditingResource] = useState(null)
  const [formValues, setFormValues] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')
  const [isKeyEdited, setIsKeyEdited] = useState(false)
  const [skillSearch, setSkillSearch] = useState('')

  const [pendingToggle, setPendingToggle] = useState(null)
  const [toggleError, setToggleError] = useState('')

  const [isSaving, setIsSaving] = useState(false)


  useEffect(() => {
    let isCancelled = false

    async function loadData() {
      try {
        const [resourceResult, skillResult] = await Promise.all([
          listAdminLearningResources(),
          listAdminSkills(),
        ])

        if (!isCancelled) {
          setResources(resourceResult)
          setSkills(skillResult)
        }
      }
      catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message
            || 'Could not load learning resources. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadData()

    return () => {
      isCancelled = true
    }
  }, [])


  const isDialogOpen = Boolean(formMode || pendingToggle)

  useEffect(() => {
    if (!isDialogOpen) {
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !isSaving) {
        setFormMode(null)
        setPendingToggle(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [isDialogOpen, isSaving])


  function handleSearchChange(event) {
    setSearchText(event.target.value)
    setVisibleCount(PAGE_SIZE)
  }


  function handleHealthFilterChange(event) {
    setHealthFilter(event.target.value)
    setVisibleCount(PAGE_SIZE)
  }


  function handleActiveFilterChange(event) {
    setActiveFilter(event.target.value)
    setVisibleCount(PAGE_SIZE)
  }


  const skillsById = {}

  skills.forEach((skill) => {
    skillsById[skill.id] = skill
  })


  function replaceResource(updated) {
    setResources((previous) => previous.map((item) => (
      item.id === updated.id ? updated : item
    )))
  }


  /* Add / edit form */

  function openCreateForm() {
    setSuccessMessage('')
    setFormError('')
    setEditingResource(null)
    setFormValues(EMPTY_FORM)
    setIsKeyEdited(false)
    setSkillSearch('')
    setFormMode('create')
  }


  function openEditForm(resource) {
    setSuccessMessage('')
    setFormError('')
    setEditingResource(resource)
    setFormValues({
      title: resource.title || '',
      resource_key: resource.resource_key || '',
      provider: resource.provider || '',
      url: resource.url || '',
      resource_type: resource.resource_type || 'other',
      description: resource.description || '',
      is_active: resource.is_active,
      access_type: resource.access_type || 'unknown',
      source_type: resource.source_type || 'curated',
      health_status: resource.health_status || 'active',
      skill_ids: resource.skill_ids || [],
    })
    setIsKeyEdited(true)
    setSkillSearch('')
    setFormMode('edit')
  }


  function closeForm() {
    if (isSaving) {
      return
    }

    setFormMode(null)
    setFormError('')
  }


  function handleFieldChange(event) {
    const { name, value, type, checked } = event.target

    setFormValues((previous) => {
      const next = {
        ...previous,
        [name]: type === 'checkbox' ? checked : value,
      }

      if (
        name === 'title'
        && formMode === 'create'
        && !isKeyEdited
      ) {
        next.resource_key = slugify(value)
      }

      return next
    })

    if (name === 'resource_key') {
      setIsKeyEdited(true)
    }
  }


  function addSkill(skillId) {
    setFormValues((previous) => (
      previous.skill_ids.includes(skillId)
        ? previous
        : { ...previous, skill_ids: [...previous.skill_ids, skillId] }
    ))
    setSkillSearch('')
  }


  function removeSkill(skillId) {
    setFormValues((previous) => ({
      ...previous,
      skill_ids: previous.skill_ids.filter((id) => id !== skillId),
    }))
  }


  async function handleFormSubmit(event) {
    event.preventDefault()

    const payload = {
      title: formValues.title.trim(),
      resource_key: formValues.resource_key.trim(),
      provider: formValues.provider.trim(),
      url: formValues.url.trim(),
      resource_type: formValues.resource_type,
      description: formValues.description.trim(),
      is_active: formValues.is_active,
      access_type: formValues.access_type,
      source_type: formValues.source_type,
      health_status: formValues.health_status,
      skill_ids: formValues.skill_ids,
    }

    if (!payload.title || !payload.resource_key || !payload.url) {
      setFormError('Title, resource key and URL are required.')
      return
    }

    setIsSaving(true)
    setFormError('')

    try {
      if (formMode === 'create') {
        const created = await createAdminLearningResource(payload)

        setResources((previous) => [...previous, created])
        setSuccessMessage(`${created.title} was added.`)
      }
      else {
        const updated = await updateAdminLearningResource(
          editingResource.id,
          payload,
        )

        replaceResource(updated)
        setSuccessMessage(`${updated.title} was updated.`)
      }

      setFormMode(null)
    }
    catch (error) {
      setFormError(
        getErrorMessage(error, 'Could not save the resource. Please try again.'),
      )
    }
    finally {
      setIsSaving(false)
    }
  }


  /* Activate / deactivate */

  function openToggleDialog(resource) {
    setSuccessMessage('')
    setToggleError('')
    setPendingToggle(resource)
  }


  function closeToggleDialog() {
    if (isSaving) {
      return
    }

    setPendingToggle(null)
    setToggleError('')
  }


  async function handleConfirmToggle() {
    setIsSaving(true)
    setToggleError('')

    try {
      const updated = await updateAdminLearningResource(
        pendingToggle.id,
        { is_active: !pendingToggle.is_active },
      )

      replaceResource(updated)
      setSuccessMessage(
        `${updated.title} is now ${updated.is_active ? 'active' : 'inactive'}.`,
      )
      setPendingToggle(null)
    }
    catch (error) {
      setToggleError(
        getErrorMessage(error, 'Could not update the resource. Please try again.'),
      )
    }
    finally {
      setIsSaving(false)
    }
  }


  /* Filtering */

  const normalisedSearch = searchText.trim().toLowerCase()

  const filteredResources = resources.filter((resource) => {
    const matchesHealth =
      healthFilter === 'all' || resource.health_status === healthFilter

    const matchesActive =
      activeFilter === 'all'
      || (activeFilter === 'active' && resource.is_active)
      || (activeFilter === 'inactive' && !resource.is_active)

    const matchesSearch =
      !normalisedSearch
      || resource.title.toLowerCase().includes(normalisedSearch)
      || (resource.provider || '').toLowerCase().includes(normalisedSearch)

    return matchesHealth && matchesActive && matchesSearch
  })

  const visibleResources = filteredResources.slice(0, visibleCount)

  const normalisedSkillSearch = skillSearch.trim().toLowerCase()

  const skillMatches = normalisedSkillSearch
    ? skills
      .filter((skill) => (
        !formValues.skill_ids.includes(skill.id)
        && skill.name.toLowerCase().includes(normalisedSkillSearch)
      ))
      .slice(0, 8)
    : []


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading admin-careers__heading">
        <div className="career-guidance-heading__copy">
          <h1>Learning Resource Management</h1>
          <p>
            Add, edit and review the learning resources students see.
          </p>
        </div>

        <button
          type="button"
          className="admin-users__primary-button"
          onClick={openCreateForm}
        >
          Add resource
        </button>
      </header>

      {errorMessage && (
        <section className="career-guidance-state-card" role="alert">
          <h2>Something went wrong</h2>
          <p>{errorMessage}</p>
        </section>
      )}

      {successMessage && (
        <div className="admin-users__success" role="status">
          <span>
            {successMessage} This change was recorded in the audit log.
          </span>
          <button
            type="button"
            className="admin-users__link-button"
            onClick={() => setSuccessMessage('')}
          >
            Dismiss
          </button>
        </div>
      )}

      {!errorMessage && (
        <section className="career-guidance-section">
          <div className="admin-users__filters">
            <label className="admin-users__field">
              <span>Search</span>
              <input
                type="search"
                value={searchText}
                onChange={handleSearchChange}
                placeholder="Search by title or provider"
              />
            </label>

            <label className="admin-users__field">
              <span>Health</span>
              <select
                value={healthFilter}
                onChange={handleHealthFilterChange}
              >
                <option value="all">All health statuses</option>
                {HEALTH_STATUSES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="admin-users__field">
              <span>Visibility</span>
              <select
                value={activeFilter}
                onChange={handleActiveFilterChange}
              >
                <option value="all">All</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
          </div>

          {isLoading && (
            <p className="admin-dashboard__empty">Loading resources…</p>
          )}

          {!isLoading && filteredResources.length === 0 && (
            <p className="admin-dashboard__empty">
              No resources match your search.
            </p>
          )}

          {!isLoading && filteredResources.length > 0 && (
            <div className="admin-users__table-wrap">
              <table className="admin-users__table">
                <thead>
                  <tr>
                    <th scope="col">Title</th>
                    <th scope="col">Provider</th>
                    <th scope="col">Type</th>
                    <th scope="col">Access</th>
                    <th scope="col">Health</th>
                    <th scope="col">Visibility</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleResources.map((resource) => (
                    <tr key={resource.id}>
                      <td className="admin-reports__comment">
                        <a
                          href={resource.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {resource.title}
                        </a>
                      </td>
                      <td>{resource.provider || '—'}</td>
                      <td>{getLabel(RESOURCE_TYPES, resource.resource_type)}</td>
                      <td>{getLabel(ACCESS_TYPES, resource.access_type)}</td>
                      <td>
                        <span
                          className={`admin-users__pill ${HEALTH_PILLS[resource.health_status] || ''}`}
                        >
                          {getLabel(HEALTH_STATUSES, resource.health_status)}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`admin-users__pill ${resource.is_active ? 'admin-users__pill--active' : 'admin-users__pill--inactive'}`}
                        >
                          {resource.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <div className="admin-careers__row-actions">
                          <button
                            type="button"
                            className="admin-users__action-button"
                            onClick={() => openEditForm(resource)}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="admin-users__action-button"
                            onClick={() => openToggleDialog(resource)}
                          >
                            {resource.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading && filteredResources.length > visibleCount && (
            <div className="admin-skills__more">
              <button
                type="button"
                className="admin-users__secondary-button"
                onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}
              >
                Show more
              </button>
            </div>
          )}

          {!isLoading && (
            <p className="admin-users__count">
              Showing {visibleResources.length} of {filteredResources.length} matching
              {' '}({resources.length} total)
            </p>
          )}
        </section>
      )}

      {formMode && (
        <div
          className="admin-users__backdrop"
          onClick={closeForm}
        >
          <form
            className="admin-users__dialog admin-careers__form admin-resources__form"
            role="dialog"
            aria-modal="true"
            aria-labelledby="resource-form-title"
            onClick={(event) => event.stopPropagation()}
            onSubmit={handleFormSubmit}
            noValidate
          >
            <h2 id="resource-form-title">
              {formMode === 'create' ? 'Add learning resource' : 'Edit learning resource'}
            </h2>

            <label className="admin-careers__form-field">
              <span>Title *</span>
              <input
                name="title"
                type="text"
                value={formValues.title}
                onChange={handleFieldChange}
                maxLength={255}
                autoFocus
              />
            </label>

            <label className="admin-careers__form-field">
              <span>URL *</span>
              <input
                name="url"
                type="url"
                value={formValues.url}
                onChange={handleFieldChange}
                placeholder="https://"
              />
            </label>

            <div className="admin-resources__grid">
              <label className="admin-careers__form-field">
                <span>Resource key *</span>
                <input
                  name="resource_key"
                  type="text"
                  value={formValues.resource_key}
                  onChange={handleFieldChange}
                  maxLength={120}
                />
              </label>

              <label className="admin-careers__form-field">
                <span>Provider</span>
                <input
                  name="provider"
                  type="text"
                  value={formValues.provider}
                  onChange={handleFieldChange}
                  maxLength={255}
                  placeholder="e.g. Coursera"
                />
              </label>

              <label className="admin-careers__form-field">
                <span>Type</span>
                <select
                  name="resource_type"
                  value={formValues.resource_type}
                  onChange={handleFieldChange}
                >
                  {RESOURCE_TYPES.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="admin-careers__form-field">
                <span>Access</span>
                <select
                  name="access_type"
                  value={formValues.access_type}
                  onChange={handleFieldChange}
                >
                  {ACCESS_TYPES.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="admin-careers__form-field">
                <span>Source</span>
                <select
                  name="source_type"
                  value={formValues.source_type}
                  onChange={handleFieldChange}
                >
                  {SOURCE_TYPES.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="admin-careers__form-field">
                <span>Health</span>
                <select
                  name="health_status"
                  value={formValues.health_status}
                  onChange={handleFieldChange}
                >
                  {HEALTH_STATUSES.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="admin-careers__form-field">
              <span>Description</span>
              <textarea
                name="description"
                rows={3}
                value={formValues.description}
                onChange={handleFieldChange}
              />
            </label>

            <div className="admin-careers__form-field">
              <span>Linked skills</span>

              {formValues.skill_ids.length > 0 && (
                <div className="admin-resources__chips">
                  {formValues.skill_ids.map((skillId) => (
                    <span key={skillId} className="admin-resources__chip">
                      {skillsById[skillId]?.name || `Skill #${skillId}`}
                      <button
                        type="button"
                        aria-label={`Remove ${skillsById[skillId]?.name || 'skill'}`}
                        onClick={() => removeSkill(skillId)}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}

              <input
                type="search"
                value={skillSearch}
                onChange={(event) => setSkillSearch(event.target.value)}
                placeholder="Search skills to link"
                aria-label="Search skills to link"
              />

              {skillMatches.length > 0 && (
                <ul className="admin-resources__skill-results">
                  {skillMatches.map((skill) => (
                    <li key={skill.id}>
                      <button
                        type="button"
                        onClick={() => addSkill(skill.id)}
                      >
                        {skill.name}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <label className="admin-careers__checkbox">
              <input
                name="is_active"
                type="checkbox"
                checked={formValues.is_active}
                onChange={handleFieldChange}
              />
              <span>Active (visible to students)</span>
            </label>

            <p className="admin-users__dialog-note">
              This change will be recorded in the audit log.
            </p>

            {formError && (
              <p className="admin-users__dialog-error" role="alert">
                {formError}
              </p>
            )}

            <div className="admin-users__dialog-actions">
              <button
                type="button"
                className="admin-users__secondary-button"
                onClick={closeForm}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="admin-users__primary-button"
                disabled={isSaving}
              >
                {isSaving ? 'Saving…' : 'Save resource'}
              </button>
            </div>
          </form>
        </div>
      )}

      {pendingToggle && (
        <div
          className="admin-users__backdrop"
          onClick={closeToggleDialog}
        >
          <div
            className="admin-users__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="resource-toggle-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="resource-toggle-title">
              {pendingToggle.is_active ? 'Deactivate resource?' : 'Activate resource?'}
            </h2>

            <p>
              {pendingToggle.is_active ? 'Deactivate' : 'Activate'}
              {' '}<strong>{pendingToggle.title}</strong>?
            </p>

            {pendingToggle.is_active && (
              <p className="admin-users__warning">
                Students will no longer see this resource in their
                learning suggestions. Feedback and reports are kept.
              </p>
            )}

            <p className="admin-users__dialog-note">
              This change will be recorded in the audit log.
            </p>

            {toggleError && (
              <p className="admin-users__dialog-error" role="alert">
                {toggleError}
              </p>
            )}

            <div className="admin-users__dialog-actions">
              <button
                type="button"
                className="admin-users__secondary-button"
                onClick={closeToggleDialog}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                type="button"
                className="admin-users__primary-button"
                onClick={handleConfirmToggle}
                disabled={isSaving}
              >
                {isSaving
                  ? 'Saving…'
                  : pendingToggle.is_active ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


export default AdminLearningResourcesPage