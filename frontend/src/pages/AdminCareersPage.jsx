import {
  useEffect,
  useState,
} from 'react'

import {
  createAdminCareer,
  listAdminCareers,
  updateAdminCareer,
} from '../services/adminService'

import './CareerGuidancePage.css'
import './AdminDashboardPage.css'
import './AdminUsersPage.css'
import './AdminCareersPage.css'


const STATUS_FILTERS = [
  { value: 'all', label: 'All statuses' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
]

const EMPTY_FORM = {
  name: '',
  category: '',
  description: '',
  active: true,
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


function AdminCareersPage() {
  const [careers, setCareers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [searchText, setSearchText] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [successMessage, setSuccessMessage] = useState('')

  const [formMode, setFormMode] = useState(null)
  const [editingCareer, setEditingCareer] = useState(null)
  const [formValues, setFormValues] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')

  const [pendingToggle, setPendingToggle] = useState(null)
  const [toggleError, setToggleError] = useState('')

  const [isSaving, setIsSaving] = useState(false)


  useEffect(() => {
    let isCancelled = false

    async function loadCareers() {
      try {
        const result = await listAdminCareers()

        if (!isCancelled) {
          setCareers(result)
        }
      }
      catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message
            || 'Could not load careers. Please try again.',
          )
        }
      }
      finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadCareers()

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


  function replaceCareer(updated) {
    setCareers((previous) => previous.map((item) => (
      item.id === updated.id ? updated : item
    )))
  }


  /* Add / edit form */

  function openCreateForm() {
    setSuccessMessage('')
    setFormError('')
    setEditingCareer(null)
    setFormValues(EMPTY_FORM)
    setFormMode('create')
  }


  function openEditForm(career) {
    setSuccessMessage('')
    setFormError('')
    setEditingCareer(career)
    setFormValues({
      name: career.name || '',
      category: career.category || '',
      description: career.description || '',
      active: career.active,
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
    const { name, value, type, checked } = event.target

    setFormValues((previous) => ({
      ...previous,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }


  async function handleFormSubmit(event) {
    event.preventDefault()

    const payload = {
      name: formValues.name.trim(),
      category: formValues.category.trim(),
      description: formValues.description.trim(),
      active: formValues.active,
    }

    if (!payload.name) {
      setFormError('Career name is required.')
      return
    }

    setIsSaving(true)
    setFormError('')

    try {
      if (formMode === 'create') {
        const created = await createAdminCareer(payload)

        setCareers((previous) => [...previous, created])
        setSuccessMessage(`${created.name} was added.`)
      }
      else {
        const updated = await updateAdminCareer(
          editingCareer.id,
          payload,
        )

        replaceCareer(updated)
        setSuccessMessage(`${updated.name} was updated.`)
      }

      setFormMode(null)
    }
    catch (error) {
      setFormError(
        getErrorMessage(error, 'Could not save the career. Please try again.'),
      )
    }
    finally {
      setIsSaving(false)
    }
  }


  /* Activate / deactivate */

  function openToggleDialog(career) {
    setSuccessMessage('')
    setToggleError('')
    setPendingToggle(career)
  }


  function closeToggleDialog() {
    if (isSaving) {
      return
    }

    setPendingToggle(null)
    setToggleError('')
  }


  async function handleConfirmToggle() {
    const nextActive = !pendingToggle.active

    setIsSaving(true)
    setToggleError('')

    try {
      const updated = await updateAdminCareer(
        pendingToggle.id,
        { active: nextActive },
      )

      replaceCareer(updated)
      setSuccessMessage(
        `${updated.name} is now ${updated.active ? 'active' : 'inactive'}.`,
      )
      setPendingToggle(null)
    }
    catch (error) {
      setToggleError(
        getErrorMessage(error, 'Could not update the career. Please try again.'),
      )
    }
    finally {
      setIsSaving(false)
    }
  }


  /* Filtering */

  const normalisedSearch = searchText.trim().toLowerCase()

  const visibleCareers = careers.filter((career) => {
    const matchesStatus =
      statusFilter === 'all'
      || (statusFilter === 'active' && career.active)
      || (statusFilter === 'inactive' && !career.active)

    const matchesSearch =
      !normalisedSearch
      || career.name.toLowerCase().includes(normalisedSearch)
      || (career.category || '').toLowerCase().includes(normalisedSearch)

    return matchesStatus && matchesSearch
  })


  return (
    <div className="career-guidance-page">
      <header className="career-guidance-heading admin-careers__heading">
        <div className="career-guidance-heading__copy">
          <h1>Career Management</h1>
          <p>
            Add, edit and activate GradNavi careers.
          </p>
        </div>

        <button
          type="button"
          className="admin-users__primary-button"
          onClick={openCreateForm}
        >
          Add career
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
              <span>Status</span>
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
              >
                {STATUS_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {isLoading && (
            <p className="admin-dashboard__empty">Loading careers…</p>
          )}

          {!isLoading && visibleCareers.length === 0 && (
            <p className="admin-dashboard__empty">
              No careers match your search.
            </p>
          )}

          {!isLoading && visibleCareers.length > 0 && (
            <div className="admin-users__table-wrap">
              <table className="admin-users__table">
                <thead>
                  <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Category</th>
                    <th scope="col">Status</th>
                    <th scope="col">Last updated</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleCareers.map((career) => (
                    <tr key={career.id}>
                      <td>{career.name}</td>
                      <td>{career.category || '—'}</td>
                      <td>
                        <span
                          className={`admin-users__pill ${career.active ? 'admin-users__pill--active' : 'admin-users__pill--inactive'}`}
                        >
                          {career.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{formatDate(career.updated_at)}</td>
                      <td>
                        <div className="admin-careers__row-actions">
                          <button
                            type="button"
                            className="admin-users__action-button"
                            onClick={() => openEditForm(career)}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="admin-users__action-button"
                            onClick={() => openToggleDialog(career)}
                          >
                            {career.active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading && (
            <p className="admin-users__count">
              Showing {visibleCareers.length} of {careers.length} careers
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
            aria-labelledby="career-form-title"
            onClick={(event) => event.stopPropagation()}
            onSubmit={handleFormSubmit}
            noValidate
          >
            <h2 id="career-form-title">
              {formMode === 'create' ? 'Add career' : 'Edit career'}
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
              <span>Category</span>
              <input
                name="category"
                type="text"
                value={formValues.category}
                onChange={handleFieldChange}
                maxLength={100}
                placeholder="e.g. Software Development"
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

            <label className="admin-careers__checkbox">
              <input
                name="active"
                type="checkbox"
                checked={formValues.active}
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
                {isSaving ? 'Saving…' : 'Save career'}
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
            aria-labelledby="career-toggle-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="career-toggle-title">
              {pendingToggle.active ? 'Deactivate career?' : 'Activate career?'}
            </h2>

            <p>
              {pendingToggle.active ? 'Deactivate' : 'Activate'}
              {' '}<strong>{pendingToggle.name}</strong>?
            </p>

            {pendingToggle.active && (
              <p className="admin-users__warning">
                Students will no longer see this career in recommendations
                or Explore Careers. Existing student data is kept.
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
                  : pendingToggle.active ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


export default AdminCareersPage