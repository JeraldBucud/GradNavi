import { useState } from 'react'

function SkillsSection() {
  const [skillItems, setSkillItems] = useState([])
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
  }

  function handleSubmit(event) {
    event.preventDefault()

    const trimmedSkillName = skillForm.name.trim()

    if (!trimmedSkillName || !skillForm.proficiency_level) {
      setError('Skill name and proficiency level are required.')
      return
    }

    const duplicateSkill = skillItems.some(
      (skill) =>
        skill.name.toLowerCase() === trimmedSkillName.toLowerCase(),
    )

    if (duplicateSkill) {
      setError('This skill has already been added.')
      return
    }

    setSkillItems((currentItems) => [
      ...currentItems,
      {
        name: trimmedSkillName,
        proficiency_level: skillForm.proficiency_level,
      },
    ])

    setSkillForm({
      name: '',
      proficiency_level: '',
    })

    setError('')
  }

  function handleRemove(indexToRemove) {
    setSkillItems((currentItems) =>
      currentItems.filter((_, index) => index !== indexToRemove),
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
          <label htmlFor="skill-name">Skill</label>
          <input
            id="skill-name"
            name="name"
            type="text"
            value={skillForm.name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="proficiency-level">Proficiency Level</label>
          <select
            id="proficiency-level"
            name="proficiency_level"
            value={skillForm.proficiency_level}
            onChange={handleChange}
          >
            <option value="">Select proficiency</option>
            <option value="foundational">Foundational</option>
            <option value="developing">Developing</option>
            <option value="proficient">Proficient</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        {error && <p>{error}</p>}

        <button type="submit">Add Skill</button>
      </form>

      {skillItems.length > 0 && (
        <div>
          <h3>My Skills</h3>

          {skillItems.map((skill, index) => (
            <article
            className="profile-item"
            key={`${skill.name}-${index}`}>
              <h4>{skill.name}</h4>

              <p>
                Proficiency: {getProficiencyLabel(skill.proficiency_level)}
              </p>

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

export default SkillsSection