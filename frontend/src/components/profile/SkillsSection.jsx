import { useState } from 'react'

import {
  SPRINT_1_SKILLS,
} from '../../data/profileReferenceData'


function createEmptySkillForm() {
  return {
    name: '',
    proficiency_level: '',
  }
}


function SkillsSection({
  items,
  onChange,
}) {
  const [skillForm, setSkillForm] =
    useState(createEmptySkillForm)

  const [editingIndex, setEditingIndex] =
    useState(null)

  const [isFormOpen, setIsFormOpen] =
    useState(false)

  const [error, setError] =
    useState('')


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setSkillForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))

    setError('')
  }


  function handleAddSkill() {
    setSkillForm(createEmptySkillForm())
    setEditingIndex(null)
    setError('')
    setIsFormOpen(true)
  }


  function handleEdit(index) {
    const skill = items[index]

    setSkillForm({
      name: skill.name || '',
      proficiency_level:
        skill.proficiency_level || '',
    })

    setEditingIndex(index)
    setError('')
    setIsFormOpen(true)
  }


  function handleCancel() {
    setSkillForm(createEmptySkillForm())
    setEditingIndex(null)
    setError('')
    setIsFormOpen(false)
  }


  function handleSubmit(event) {
    event.preventDefault()

    if (
      !skillForm.name ||
      !skillForm.proficiency_level
    ) {
      setError(
        'Skill and proficiency level are required.',
      )

      return
    }

    const selectedSkill =
      SPRINT_1_SKILLS.find(
        (skill) =>
          skill.name === skillForm.name,
      )

    if (!selectedSkill) {
      setError(
        'Select a valid skill.',
      )

      return
    }

    const duplicateSkill =
      items.some(
        (skill, index) =>
          index !== editingIndex &&
          skill.name.toLowerCase() ===
            selectedSkill.name.toLowerCase(),
      )

    if (duplicateSkill) {
      setError(
        'This skill has already been added.',
      )

      return
    }

    if (editingIndex === null) {
      onChange([
        ...items,
        {
          name: selectedSkill.name,
          category:
            selectedSkill.category,
          proficiency_level:
            skillForm.proficiency_level,
        },
      ])
    } else {
      onChange(
        items.map((skill, index) => {
          if (index !== editingIndex) {
            return skill
          }

          return {
            ...skill,
            proficiency_level:
              skillForm.proficiency_level,
          }
        }),
      )
    }

    handleCancel()
  }


  function handleRemove(indexToRemove) {
    onChange(
      items.filter(
        (_, index) =>
          index !== indexToRemove,
      ),
    )

    if (editingIndex === indexToRemove) {
      handleCancel()
    } else if (
      editingIndex !== null &&
      editingIndex > indexToRemove
    ) {
      setEditingIndex(
        (currentIndex) =>
          currentIndex - 1,
      )
    }
  }


  function getProficiencyLabel(value) {
    const proficiencyLabels = {
      foundational: 'Foundational',
      developing: 'Developing',
      proficient: 'Proficient',
      advanced: 'Advanced',
    }

    return (
      proficiencyLabels[value] || value
    )
  }


  return (
    <section
      id="skills"
      className="profile-section profile-section--skills"
    >
      <div className="profile-card-heading">
        <h2>
          Skills
        </h2>

        <p>
          Skill proficiency values are Foundational,
          Developing, Proficient, Advanced.
        </p>
      </div>


      <div className="profile-table">
        <div
          className="profile-table__header profile-table__header--skills"
          aria-hidden="true"
        >
          <span>
            Skill
          </span>

          <span>
            Proficiency
          </span>

          <span>
            Action
          </span>
        </div>

        {items.length === 0 ? (
          <div className="profile-empty-state">
            No skills added yet.
          </div>
        ) : (
          <div className="profile-table__body">
            {items.map(
              (skill, index) => (
                <div
                  className="profile-table__row profile-table__row--skills"
                  key={
                    skill.id ||
                    `${skill.name}-${index}`
                  }
                >
                  <div>
                    <strong>
                      {skill.name}
                    </strong>

                    {skill.category && (
                      <span className="profile-row-secondary">
                        {skill.category}
                      </span>
                    )}
                  </div>

                  <span>
                    {getProficiencyLabel(
                      skill.proficiency_level,
                    )}
                  </span>

                  <div className="profile-row-actions">
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
                </div>
              ),
            )}
          </div>
        )}
      </div>


      {isFormOpen && (
        <form
          className="profile-inline-form"
          onSubmit={handleSubmit}
        >
          <div className="profile-inline-form__grid">
            <div className="profile-field">
              <label htmlFor="skill-name">
                Skill
              </label>

              <select
                id="skill-name"
                name="name"
                value={skillForm.name}
                onChange={handleChange}
                disabled={
                  editingIndex !== null
                }
              >
                <option value="">
                  Select a skill
                </option>

                {SPRINT_1_SKILLS.map(
                  (skill) => (
                    <option
                      key={skill.name}
                      value={skill.name}
                    >
                      {skill.name}
                    </option>
                  ),
                )}
              </select>
            </div>

            <div className="profile-field">
              <label htmlFor="proficiency-level">
                Proficiency Level
              </label>

              <select
                id="proficiency-level"
                name="proficiency_level"
                value={
                  skillForm.proficiency_level
                }
                onChange={handleChange}
              >
                <option value="">
                  Select proficiency
                </option>

                <option value="foundational">
                  Foundational
                </option>

                <option value="developing">
                  Developing
                </option>

                <option value="proficient">
                  Proficient
                </option>

                <option value="advanced">
                  Advanced
                </option>
              </select>
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
                ? 'Add Skill'
                : 'Update Skill'}
            </button>

            <button
              className="profile-secondary-action"
              type="button"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </form>
      )}


      {!isFormOpen && (
        <div className="profile-card-actions">
          <button
            className="profile-secondary-action"
            type="button"
            onClick={handleAddSkill}
          >
            Add Skill
          </button>
        </div>
      )}
    </section>
  )
}


export default SkillsSection