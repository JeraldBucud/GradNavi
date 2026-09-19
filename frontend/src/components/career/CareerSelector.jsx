function CareerSelector({
  careers,
  helperText,
  label = 'Career Focus',
  onChange,
  selectedCareerId,
  selectedCareerName = '',
}) {
  const hasSelectedCareer =
    Array.isArray(
      careers,
    )
    && careers.some(
      (career) =>
        Number(
          career.career_id,
        )
        === Number(
          selectedCareerId,
        ),
    )

  const displayedCareers =
    (
      selectedCareerId
      && !hasSelectedCareer
    )
      ? [
        {
          career_id:
            selectedCareerId,
          career_name:
            selectedCareerName
            || 'Selected career',
        },
        ...(
          Array.isArray(
            careers,
          )
            ? careers
            : []
        ),
      ]
      : (
        Array.isArray(
          careers,
        )
          ? careers
          : []
      )


  return (
    <div className="career-context-selector">
      <label className="career-context-selector__label">
        <span>
          {label}
        </span>

        <select
          className="career-context-selector__control"
          value={
            selectedCareerId
            || ''
          }
          disabled={
            displayedCareers.length
            === 0
          }
          onChange={
            (event) =>
              onChange(
                Number(
                  event.target.value,
                ),
              )
          }
        >
          {displayedCareers.length === 0 ? (
            <option value="">
              No career matches available
            </option>
          ) : (
            displayedCareers.map(
              (career) => (
                <option
                  key={
                    career.career_id
                  }
                  value={
                    career.career_id
                  }
                >
                  {
                    career.career_name
                    || 'Selected career'
                  }
                </option>
              ),
            )
          )}
        </select>
      </label>

      {helperText && (
        <p className="career-context-selector__helper">
          {helperText}
        </p>
      )}
    </div>
  )
}


export default CareerSelector
