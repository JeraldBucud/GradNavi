import { useState } from 'react'

import { SPRINT_1_SKILLS } from '../../data/profileReferenceData'

function SkillsSection({
  items,
  onChange,
}) {
  const [skillForm, setSkillForm] = useState({
    name: '',
    proficiency_level: '',
  })
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setSkillForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))

    setError('')
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

    const selectedSkill = SPRINT_1_SKILLS.find(
      (skill) => skill.name === skillForm.name,
    )

    if (!selectedSkill) {
      setError('Select a valid skill.')
      return
    }

    const duplicateSkill = items.some(
      (skill) =>
        skill.name.toLowerCase() ===
        selectedSkill.name.toLowerCase(),
    )

    if (duplicateSkill) {
      setError('This skill has already been added.')
      return
    }

    onChange([
      ...items,
      {
        name: selectedSkill.name,
        category: selectedSkill.category,
        proficiency_level:
          skillForm.proficiency_level,
      },
    ])

    setSkillForm({
      name: '',
      proficiency_level: '',
    })

    setError('')
  }

  function handleRemove(indexToRemove) {
    onChange(
      items.filter(
        (_, index) => index !== indexToRemove,
      ),
    )
  }

  function getProficiencyLabel(value) {
    const proficiencyLabels = {
      foundational: 'Foundational',
      developing: 'Developing',
      proficient: 'Proficient',
      advanced: 'Advanced',
    }

    return proficiencyLabels[value] || value
  }

  return (
    <section className="profile-section">
      <h2>Skills</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="skill-name">
            Skill
          </label>

          <select
            id="skill-name"
            name="name"
            value={skillForm.name}
            onChange={handleChange}
          >
            <option value="">
              Select a skill
            </option>

            {SPRINT_1_SKILLS.map((skill) => (
              <option
                key={skill.name}
                value={skill.name}
              >
                {skill.name} ({skill.category})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="proficiency-level">
            Proficiency Level
          </label>

          <select
            id="proficiency-level"
            name="proficiency_level"
            value={skillForm.proficiency_level}
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

        {error && (
          <p role="alert">{error}</p>
        )}

        <button type="submit">
          Add Skill
        </button>
      </form>

      {items.length > 0 && (
        <div>
          <h3>My Skills</h3>

          {items.map((skill, index) => (
            <article
              className="profile-item"
              key={
                skill.id ||
                `${skill.name}-${index}`
              }
            >
              <h4>{skill.name}</h4>

              {skill.category && (
                <p>
                  Category: {skill.category}
                </p>
              )}

              <p>
                Proficiency:{' '}
                {getProficiencyLabel(
                  skill.proficiency_level,
                )}
              </p>

              <button
                type="button"
                onClick={() =>
                  handleRemove(index)
                }
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

export default SkillsSection