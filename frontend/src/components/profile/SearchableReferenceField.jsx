import {
  useEffect,
  useState,
} from 'react'


function SearchableReferenceField({
  id,
  label,
  placeholder,
  searchReference,
  selectedItem,
  onSelect,
  excludedIds = [],
  disabled = false,
  helperText = '',
}) {
  const [
    query,
    setQuery,
  ] = useState(
    selectedItem?.name || '',
  )

  const [
    results,
    setResults,
  ] = useState([])

  const [
    total,
    setTotal,
  ] = useState(0)

  const [
    isLoading,
    setIsLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState('')

  const [
    isOpen,
    setIsOpen,
  ] = useState(false)

  const [
    activeIndex,
    setActiveIndex,
  ] = useState(-1)


  useEffect(() => {
    const trimmedQuery =
      query.trim()

    if (
      disabled ||
      selectedItem ||
      trimmedQuery.length === 0
    ) {
      return undefined
    }


    let cancelled = false

    const timer =
      window.setTimeout(
        async () => {
          try {
            setIsLoading(true)
            setError('')

            const response =
              await searchReference(
                trimmedQuery,
              )

            if (cancelled) {
              return
            }

            const data =
              response?.data

            const nextResults =
              Array.isArray(
                data?.results,
              )
                ? data.results
                : []

            setResults(
              nextResults,
            )

            setTotal(
              typeof data?.total ===
                'number'
                ? data.total
                : nextResults.length,
            )

            setActiveIndex(-1)
            setIsOpen(true)
          } catch {
            if (cancelled) {
              return
            }

            setResults([])
            setTotal(0)

            setError(
              'Unable to search reference data.',
            )

            setIsOpen(true)
          } finally {
            if (!cancelled) {
              setIsLoading(false)
            }
          }
        },
        250,
      )


    return () => {
      cancelled = true

      window.clearTimeout(
        timer,
      )
    }
  }, [
    disabled,
    query,
    searchReference,
    selectedItem,
  ])


  const excludedIdSet =
    new Set(excludedIds)

  const visibleResults =
    results.filter(
      (item) =>
        !excludedIdSet.has(
          item.id,
        ),
    )

  const displayQuery =
    selectedItem?.name ||
    query

  const showResults =
    isOpen &&
    !disabled &&
    !selectedItem &&
    query.trim().length > 0


  function handleInputChange(
    event,
  ) {
    const nextQuery =
      event.target.value

    if (selectedItem) {
      onSelect(null)
    }

    setQuery(
      nextQuery,
    )

    setResults([])
    setTotal(0)
    setError('')

    setIsOpen(
      nextQuery
        .trim()
        .length > 0,
    )

    setActiveIndex(-1)
  }


  function handleSelect(
    item,
  ) {
    setQuery(
      item.name || '',
    )

    setResults([])
    setTotal(0)
    setError('')
    setIsOpen(false)
    setActiveIndex(-1)

    onSelect(item)
  }


  function handleKeyDown(
    event,
  ) {
    if (
      !showResults ||
      visibleResults.length === 0
    ) {
      if (
        event.key ===
        'Escape'
      ) {
        setIsOpen(false)
        setActiveIndex(-1)
      }

      return
    }


    if (
      event.key ===
      'ArrowDown'
    ) {
      event.preventDefault()

      setActiveIndex(
        (currentIndex) =>
          currentIndex >=
            visibleResults.length - 1
            ? 0
            : currentIndex + 1,
      )

      return
    }


    if (
      event.key ===
      'ArrowUp'
    ) {
      event.preventDefault()

      setActiveIndex(
        (currentIndex) =>
          currentIndex <= 0
            ? visibleResults.length - 1
            : currentIndex - 1,
      )

      return
    }


    if (
      event.key ===
        'Enter' &&
      activeIndex >= 0
    ) {
      event.preventDefault()

      handleSelect(
        visibleResults[
          activeIndex
        ],
      )

      return
    }


    if (
      event.key ===
      'Escape'
    ) {
      setIsOpen(false)
      setActiveIndex(-1)
    }
  }


  function handleBlur() {
    window.setTimeout(
      () => {
        setIsOpen(false)
        setActiveIndex(-1)
      },
      120,
    )
  }


  return (
    <div className="profile-field profile-reference-search">
      <label htmlFor={id}>
        {label}
      </label>

      <div className="profile-reference-search__control">
        <input
          id={id}
          type="text"
          role="combobox"
          autoComplete="off"
          value={displayQuery}
          placeholder={
            placeholder
          }
          disabled={
            disabled
          }
          aria-expanded={
            showResults
          }
          aria-controls={
            `${id}-results`
          }
          aria-autocomplete="list"
          onChange={
            handleInputChange
          }
          onKeyDown={
            handleKeyDown
          }
          onFocus={() => {
            if (
              query.trim() &&
              !selectedItem &&
              !disabled
            ) {
              setIsOpen(true)
            }
          }}
          onBlur={
            handleBlur
          }
        />

        {isLoading && (
          <span className="profile-reference-search__status">
            Searching...
          </span>
        )}
      </div>


      {helperText && (
        <p className="profile-reference-search__helper">
          {helperText}
        </p>
      )}


      {showResults && (
        <div
          id={`${id}-results`}
          className="profile-reference-search__results"
          role="listbox"
        >
          {error ? (
            <div className="profile-reference-search__message profile-reference-search__message--error">
              {error}
            </div>
          ) : (
            <>
              {!isLoading &&
                visibleResults.length ===
                  0 && (
                  <div className="profile-reference-search__message">
                    No matching records.
                  </div>
                )}

              {visibleResults.map(
                (
                  item,
                  index,
                ) => (
                  <button
                    key={item.id}
                    className={[
                      'profile-reference-search__result',
                      activeIndex ===
                        index
                        ? 'profile-reference-search__result--active'
                        : '',
                    ]
                      .filter(
                        Boolean,
                      )
                      .join(' ')}
                    type="button"
                    role="option"
                    aria-selected={
                      activeIndex ===
                      index
                    }
                    onMouseDown={(
                      event,
                    ) => {
                      event.preventDefault()
                    }}
                    onClick={() =>
                      handleSelect(
                        item,
                      )
                    }
                  >
                    <strong>
                      {item.name}
                    </strong>

                    {item.category && (
                      <span>
                        {
                          item.category
                        }
                      </span>
                    )}
                  </button>
                ),
              )}

              {!isLoading &&
                visibleResults.length >
                  0 && (
                  <div className="profile-reference-search__summary">
                    Showing{' '}
                    {
                      visibleResults.length
                    }{' '}
                    of {total}{' '}
                    matching records
                  </div>
                )}
            </>
          )}
        </div>
      )}
    </div>
  )
}


export default SearchableReferenceField
