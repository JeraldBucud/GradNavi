import {
  useEffect,
  useState,
} from 'react'

import {
  createAdminSkill,
  listAdminSkills,
  updateAdminSkill,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'
import './AdminCareersPage.css'


const PAGE_SIZE = 50

const CONCEPT_TYPES = [
  { value: 'skill', label: 'Skill' },
  { value: 'knowledge', label: 'Knowledge' },
  { value: 'technology', label: 'Technology' },
]

const TYPE_FILTERS = [
  { value: 'all', label: 'All types' },
  ...CONCEPT_TYPES,
]

const EMPTY_FORM = {
  name: '',
  concept_type: 'skill',
  category: '',
  description: '',
}


function formatDate(value) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleDateString('en-AU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}


function getTypeLabel(value) {
  const match = CONCEPT_TYPES.find((option) => option.value === value)

  return match ? match.label : value
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
  const nameError = findFieldError(error?.data, 'name')

  if (nameError) {
    return `Name: ${nameError}`
  }

  return error?.message || fallback
}


function AdminSkillsPage() {
  const [skills, setSkills] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)
  const [successMessage, setSuccessMessage] = useState('')

  const [formMode, setFormMode] = useState(null)
  const [editingSkill, setEditingSkill] = useState(null)
  const [formValues, setFormValues] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')
  const [isSaving, setIsSaving] = useState(false)


  useEffect(() => {
    let isCancelled = false

    async function loadSkills() {
      try {
        const result = await listAdminSkills()

        if (!isCancelled) {
          setSkills(result)
        }
      }
      catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message
            || 'Could not load skills. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadSkills()

    return () => {
      isCancelled = true
    }
  }, [])


  useEffect(() => {
    if (!formMode) {
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !isSaving) {
        setFormMode(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [formMode, isSaving])


  useEffect(() => {
    setVisibleCount(PAGE_SIZE)
  }, [searchText, typeFilter])


  function openCreateForm() {
    setSuccessMessage('')
    setFormError('')
    setEditingSkill(null)
    setFormValues(EMPTY_FORM)
    setFormMode('create')
  }


  function openEditForm(skill) {
    setSuccessMessage('')
    setFormError('')
    setEditingSkill(skill)
    setFormValues({
      name: skill.name || '',
      concept_type: skill.concept_type || 'skill',
      category: skill.category || '',
      description: skill.description || '',
    })
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
    const { name, value } = event.target

    setFormValues((previous) => ({
      ...previous,
      [name]: value,
    }))
  }


  async function handleFormSubmit(event) {
    event.preventDefault()

    const payload = {
      name: formValues.name.trim(),
      concept_type: formValues.concept_type,
      category: formValues.category.trim(),
      description: formValues.description.trim(),
    }

    if (!payload.name) {
      setFormError('Skill name is required.')
      return
    }

    setIsSaving(true)
    setFormError('')

    try {
      if (formMode === 'create') {
        const created = await createAdminSkill(payload)

        setSkills((previous) => [...previous, created])
        setSuccessMessage(`${created.name} was added.`)
      }
      else {
        const updated = await updateAdminSkill(editingSkill.id, payload)

        setSkills((previous) => previous.map((item) => (
          item.id === updated.id ? updated : item
        )))
        setSuccessMessage(`${updated.name} was updated.`)
      }

      setFormMode(null)
    }
    catch (error) {
      setFormError(
        getErrorMessage(error, 'Could not save the skill. Please try again.'),
      )
    }
    finally {
      setIsSaving(false)
    }
  }


  const normalisedSearch = searchText.trim().toLowerCase()

  const filteredSkills = skills.filter((skill) => {
    const matchesType =
      typeFilter === 'all' || skill.concept_type === typeFilter

    const matchesSearch =
      !normalisedSearch
      || skill.name.toLowerCase().includes(normalisedSearch)
      || (skill.category || '').toLowerCase().includes(normalisedSearch)

    return matchesType && matchesSearch
  })

  const visibleSkills = filteredSkills.slice(0, visibleCount)


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading admin-careers__heading">
        <div className="career-guidance-heading__copy">
          <h1>Skill Management</h1>
          <p>
            Add and edit the canonical skills used across GradNavi.
          </p>
        </div>

        <button
          type="button"
          className="admin-users__primary-button"
          onClick={openCreateForm}
        >
          Add skill
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
                onChange={(event) => setSearchText(event.target.value)}
                placeholder="Search by name or category"
              />
            </label>

            <label className="admin-users__field">
              <span>Type</span>
              <select
                value={typeFilter}
                onChange={(event) => setTypeFilter(event.target.value)}
              >
                {TYPE_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {isLoading && (
            <p className="admin-dashboard__empty">Loading skills…</p>
          )}

          {!isLoading && filteredSkills.length === 0 && (
            <p className="admin-dashboard__empty">
              No skills match your search.
            </p>
          )}

          {!isLoading && filteredSkills.length > 0 && (
            <div className="admin-users__table-wrap">
              <table className="admin-users__table">
                <thead>
                  <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Type</th>
                    <th scope="col">Category</th>
                    <th scope="col">Last updated</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleSkills.map((skill) => (
                    <tr key={skill.id}>
                      <td>{skill.name}</td>
                      <td>
                        <span className="admin-users__pill admin-users__pill--student">
                          {getTypeLabel(skill.concept_type)}
                        </span>
                      </td>
                      <td>{skill.category || '—'}</td>
                      <td>{formatDate(skill.updated_at)}</td>
                      <td>
                        <button
                          type="button"
                          className="admin-users__action-button"
                          onClick={() => openEditForm(skill)}
                        >
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading && filteredSkills.length > visibleCount && (
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
              Showing {visibleSkills.length} of {filteredSkills.length} matching
              {' '}({skills.length} total)
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
            className="admin-users__dialog admin-careers__form"
            role="dialog"
            aria-modal="true"
            aria-labelledby="skill-form-title"
            onClick={(event) => event.stopPropagation()}
            onSubmit={handleFormSubmit}
            noValidate
          >
            <h2 id="skill-form-title">
              {formMode === 'create' ? 'Add skill' : 'Edit skill'}
            </h2>

            <label className="admin-careers__form-field">
              <span>Name *</span>
              <input
                name="name"
                type="text"
                value={formValues.name}
                onChange={handleFieldChange}
                maxLength={255}
                autoFocus
              />
            </label>

            <label className="admin-careers__form-field">
              <span>Type</span>
              <select
                name="concept_type"
                value={formValues.concept_type}
                onChange={handleFieldChange}
              >
                {CONCEPT_TYPES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="admin-careers__form-field">
              <span>Category</span>
              <input
                name="category"
                type="text"
                value={formValues.category}
                onChange={handleFieldChange}
                maxLength={100}
                placeholder="e.g. Programming"
              />
            </label>

            <label className="admin-careers__form-field">
              <span>Description</span>
              <textarea
                name="description"
                rows={4}
                value={formValues.description}
                onChange={handleFieldChange}
              />
            </label>

            {formMode === 'edit' && (
              <p className="admin-users__warning">
                This skill may be used by careers, students and learning
                resources. Renaming it changes it everywhere.
              </p>
            )}

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
                {isSaving ? 'Saving…' : 'Save skill'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}


export default AdminSkillsPage