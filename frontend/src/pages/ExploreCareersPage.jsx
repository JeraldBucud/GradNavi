import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router'

import {
  getStoredUser,
} from '../services/authService'

import {
  evaluateExploreCareer,
  getExploreCareerDetail,
  getExploreCareers,
} from '../services/careerService'

import {
  saveCareerSelection,
} from '../services/careerSelectionService'

import './CareerGuidancePage.css'


const PAGE_SIZE = 12


function formatScore(value) {
  if (
    value === null
    || value === undefined
    || value === ''
  ) {
    return 'Not evaluated'
  }

  const numericValue =
    Number(
      value,
    )

  if (!Number.isFinite(numericValue)) {
    return 'Not evaluated'
  }

  return `${Math.round(numericValue)}%`
}


function formatStatus(value) {
  if (value === 'recommended') {
    return 'Recommended'
  }

  if (value === 'evaluated') {
    return 'Evaluated'
  }

  return 'Not evaluated'
}


function getStatusClass(value) {
  if (value === 'recommended') {
    return (
      'explore-careers-figma__status '
      + 'explore-careers-figma__status--recommended'
    )
  }

  if (value === 'evaluated') {
    return (
      'explore-careers-figma__status '
      + 'explore-careers-figma__status--evaluated'
    )
  }

  return (
    'explore-careers-figma__status '
    + 'explore-careers-figma__status--neutral'
  )
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  return (
    requestError?.data?.error?.message
    || requestError?.message
    || fallbackMessage
  )
}


function ExploreCareersPage() {
  const navigate =
    useNavigate()

  const currentUser =
    getStoredUser()

  const studentName =
    currentUser?.first_name?.trim()
    || 'Student'

  const studentInitial =
    studentName
      .charAt(0)
      .toUpperCase()


  const [
    searchInput,
    setSearchInput,
  ] = useState('')

  const [
    appliedSearch,
    setAppliedSearch,
  ] = useState('')

  const [
    category,
    setCategory,
  ] = useState('')

  const [
    status,
    setStatus,
  ] = useState('all')

  const [
    page,
    setPage,
  ] = useState(1)

  const [
    careers,
    setCareers,
  ] = useState([])

  const [
    categories,
    setCategories,
  ] = useState([])

  const [
    pagination,
    setPagination,
  ] = useState({
    page: 1,
    page_size: PAGE_SIZE,
    total_count: 0,
    total_pages: 0,
    has_previous: false,
    has_next: false,
  })

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    loadError,
    setLoadError,
  ] = useState('')

  const [
    selectedCareer,
    setSelectedCareer,
  ] = useState(null)

  const [
    detailLoading,
    setDetailLoading,
  ] = useState(false)

  const [
    detailError,
    setDetailError,
  ] = useState('')

  const [
    evaluatingCareerId,
    setEvaluatingCareerId,
  ] = useState(null)

  const [
    evaluationError,
    setEvaluationError,
  ] = useState('')

  const [
    evaluationMessage,
    setEvaluationMessage,
  ] = useState('')

  const [
    catalogueRefreshKey,
    setCatalogueRefreshKey,
  ] = useState(0)


  useEffect(
    () => {
      let cancelled = false

      async function loadCareers() {
        setLoading(true)
        setLoadError('')

        try {
          const response =
            await getExploreCareers({
              search: appliedSearch,
              category,
              status,
              page,
              pageSize: PAGE_SIZE,
            })

          if (cancelled) {
            return
          }

          const data =
            response?.data || {}

          setCareers(
            Array.isArray(
              data.results,
            )
              ? data.results
              : [],
          )

          setCategories(
            Array.isArray(
              data
                ?.filters
                ?.categories,
            )
              ? data
                  .filters
                  .categories
              : [],
          )

          setPagination(
            data.pagination
            || {
              page,
              page_size: PAGE_SIZE,
              total_count: 0,
              total_pages: 0,
              has_previous: false,
              has_next: false,
            },
          )
        } catch (requestError) {
          if (cancelled) {
            return
          }

          setCareers([])

          setLoadError(
            getRequestErrorMessage(
              requestError,
              'Career catalogue is unavailable.',
            ),
          )
        } finally {
          if (!cancelled) {
            setLoading(false)
          }
        }
      }

      loadCareers()

      return () => {
        cancelled = true
      }
    },
    [
      appliedSearch,
      category,
      status,
      page,
      catalogueRefreshKey,
    ],
  )


  function clearSelectedCareer() {
    setSelectedCareer(null)
    setDetailError('')
    setDetailLoading(false)
    setEvaluatingCareerId(null)
    setEvaluationError('')
    setEvaluationMessage('')
  }


  useEffect(
    () => {
      const timeoutId =
        window.setTimeout(
          () => {
            clearSelectedCareer()

            setPage(1)

            setAppliedSearch(
              searchInput.trim(),
            )
          },
          300,
        )

      return () => {
        window.clearTimeout(
          timeoutId,
        )
      }
    },
    [
      searchInput,
    ],
  )


  function submitSearch(event) {
    event.preventDefault()

    clearSelectedCareer()

    setPage(1)

    setAppliedSearch(
      searchInput.trim(),
    )
  }


  function changeCategory(event) {
    clearSelectedCareer()

    setPage(1)

    setCategory(
      event.target.value,
    )
  }


  function changeStatus(event) {
    clearSelectedCareer()

    setPage(1)

    setStatus(
      event.target.value,
    )
  }


  function clearFilters() {
    clearSelectedCareer()

    setSearchInput('')
    setAppliedSearch('')
    setCategory('')
    setStatus('all')
    setPage(1)
  }


  async function openCareer(
    careerId,
  ) {
    setDetailLoading(true)
    setDetailError('')
    setEvaluationError('')
    setEvaluationMessage('')

    try {
      const response =
        await getExploreCareerDetail(
          careerId,
        )

      setSelectedCareer(
        response?.data || null,
      )
    } catch (requestError) {
      setSelectedCareer(null)

      setDetailError(
        getRequestErrorMessage(
          requestError,
          'Career details are unavailable.',
        ),
      )
    } finally {
      setDetailLoading(false)
    }
  }


  function rememberSelectedCareer() {
    const careerId =
      selectedCareer
        ?.career_id

    const careerName =
      selectedCareer
        ?.career_name

    if (
      !careerId
      || !careerName
    ) {
      return false
    }

    saveCareerSelection(
      {
        career_id:
          careerId,
        career_name:
          careerName,
      },
    )

    return true
  }


  function openSelectedSkillGaps() {
    const careerId =
      selectedCareer
        ?.career_id

    if (
      !careerId
      || !rememberSelectedCareer()
    ) {
      return
    }

    navigate(
      `/skill-gap-analysis?career_id=${careerId}`,
    )
  }


  function openSelectedLearningResources() {
    const careerId =
      selectedCareer
        ?.career_id

    if (
      !careerId
      || !rememberSelectedCareer()
    ) {
      return
    }

    navigate(
      `/learning-resources?career_id=${careerId}`,
    )
  }


  async function evaluateSelectedCareer() {
    const careerId =
      selectedCareer
        ?.career_id

    if (!careerId) {
      return
    }

    setEvaluatingCareerId(
      careerId,
    )

    setEvaluationError('')
    setEvaluationMessage('')

    try {
      const response =
        await evaluateExploreCareer(
          careerId,
        )

      const updatedCareer =
        response
          ?.data
          ?.career

      if (updatedCareer) {
        setSelectedCareer(
          updatedCareer,
        )
      }

      setEvaluationMessage(
        (
          'Career evaluation complete. '
          + 'Your current profile match '
          + 'is now available.'
        ),
      )

      setCatalogueRefreshKey(
        (current) =>
          current + 1,
      )
    } catch (requestError) {
      setEvaluationError(
        getRequestErrorMessage(
          requestError,
          'Career evaluation is unavailable.',
        ),
      )
    } finally {
      setEvaluatingCareerId(null)
    }
  }


  const hasActiveFilters =
    Boolean(
      appliedSearch
      || category
      || status !== 'all',
    )


  return (
    <main className="career-guidance-page explore-careers-figma">
      <div className="explore-careers-figma__content">
        <header className="explore-careers-figma__header">
          <div>
            <h1>
              Explore Careers
            </h1>

            <p>
              Browse available career paths,
              search the catalogue, and review
              how each career relates to your
              current GradNavi profile.
            </p>
          </div>

          <div className="explore-careers-figma__account">
            <span
              className="explore-careers-figma__avatar"
              aria-hidden="true"
            >
              {studentInitial}
            </span>

            <span>
              {studentName}
            </span>
          </div>
        </header>


        <section className="explore-careers-figma__filters">
          <div className="explore-careers-figma__section-heading">
            <h2>
              Career catalogue
            </h2>

            <p>
              Search by career name,
              description, or category.
            </p>
          </div>

          <form
            className="explore-careers-figma__search"
            onSubmit={
              submitSearch
            }
          >
            <label>
              <span>
                Search careers
              </span>

              <input
                type="search"
                value={
                  searchInput
                }
                placeholder="Search careers"
                autoComplete="off"
                onChange={
                  (event) =>
                    setSearchInput(
                      event.target.value,
                    )
                }
              />

              <small>
                Results update as you type.
              </small>
            </label>
          </form>


          <div className="explore-careers-figma__filter-grid">
            <label>
              <span>
                Category
              </span>

              <select
                value={
                  category
                }
                onChange={
                  changeCategory
                }
              >
                <option value="">
                  All categories
                </option>

                {
                  categories.map(
                    (item) => (
                      <option
                        key={
                          item
                        }
                        value={
                          item
                        }
                      >
                        {
                          item
                        }
                      </option>
                    ),
                  )
                }
              </select>
            </label>

            <label>
              <span>
                Status
              </span>

              <select
                value={
                  status
                }
                onChange={
                  changeStatus
                }
              >
                <option value="all">
                  All careers
                </option>

                <option value="recommended">
                  Recommended
                </option>

                <option value="evaluated">
                  Evaluated
                </option>

                <option value="not_evaluated">
                  Not evaluated
                </option>
              </select>
            </label>

            <div className="explore-careers-figma__filter-summary">
              <span>
                Results
              </span>

              <strong>
                {
                  pagination
                    .total_count
                }
              </strong>

              <small>
                careers found
              </small>
            </div>
          </div>


          {
            hasActiveFilters
            && (
              <button
                className="explore-careers-figma__clear"
                type="button"
                onClick={
                  clearFilters
                }
              >
                Clear search and filters
              </button>
            )
          }
        </section>


        {
          detailLoading
          && (
            <section className="career-guidance-loading-card">
              <h2>
                Loading career
              </h2>

              <p>
                Opening the selected career.
              </p>
            </section>
          )
        }


        {
          detailError
          && (
            <section className="career-guidance-inline-state">
              <h3>
                Career details unavailable
              </h3>

              <p role="alert">
                {
                  detailError
                }
              </p>
            </section>
          )
        }


        {
          selectedCareer
          && !detailLoading
          && (
            <section className="explore-careers-figma__detail">
              <div className="explore-careers-figma__detail-heading">
                <div>
                  <span
                    className={
                      getStatusClass(
                        selectedCareer
                          .status,
                      )
                    }
                  >
                    {
                      formatStatus(
                        selectedCareer
                          .status,
                      )
                    }
                  </span>

                  <h2>
                    {
                      selectedCareer
                        .career_name
                    }
                  </h2>

                  <p>
                    {
                      selectedCareer
                        .category
                      || 'Career category'
                    }
                  </p>
                </div>

                <button
                  className="explore-careers-figma__close"
                  type="button"
                  onClick={
                    clearSelectedCareer
                  }
                >
                  Close
                </button>
              </div>


              <div className="explore-careers-figma__detail-grid">
                <article>
                  <span>
                    Match score
                  </span>

                  <strong>
                    {
                      formatScore(
                        selectedCareer
                          .match_score,
                      )
                    }
                  </strong>
                </article>

                <article>
                  <span>
                    Recommendation rank
                  </span>

                  <strong>
                    {
                      selectedCareer
                        .recommendation_rank
                      ? (
                          '#'
                          + selectedCareer
                            .recommendation_rank
                        )
                      : 'Not ranked'
                    }
                  </strong>
                </article>

                <article>
                  <span>
                    Profile status
                  </span>

                  <strong>
                    {
                      formatStatus(
                        selectedCareer
                          .status,
                      )
                    }
                  </strong>
                </article>
              </div>


              <div className="explore-careers-figma__detail-description">
                <h3>
                  About this career
                </h3>

                <p>
                  {
                    selectedCareer
                      .description
                    || (
                      'No career description '
                      + 'is available yet.'
                    )
                  }
                </p>
              </div>


              <div className="explore-careers-figma__evaluation">
                <div className="explore-careers-figma__evaluation-copy">
                  <h3>
                    Profile evaluation
                  </h3>

                  {
                    selectedCareer
                      .recommended
                    ? (
                        <p>
                          This career is already
                          part of your current
                          recommendations and has
                          a profile match score.
                        </p>
                      )
                    : selectedCareer
                        .evaluated
                      ? (
                          <p>
                            This career has been
                            evaluated against your
                            current profile.
                          </p>
                        )
                      : (
                          <p>
                            Evaluate this career
                            against your current
                            GradNavi profile to
                            see your match score.
                          </p>
                        )
                  }
                </div>


                {
                  !selectedCareer
                    .recommended
                  && !selectedCareer
                    .evaluated
                  ? (
                      <button
                        className="gn-button gn-button--primary"
                        type="button"
                        disabled={
                          evaluatingCareerId
                          === selectedCareer
                            .career_id
                        }
                        onClick={
                          evaluateSelectedCareer
                        }
                      >
                        {
                          evaluatingCareerId
                          === selectedCareer
                            .career_id
                            ? 'Evaluating...'
                            : 'Evaluate Career'
                        }
                      </button>
                    )
                  : (
                      <span className="explore-careers-figma__evaluation-state">
                        {
                          selectedCareer
                            .recommended
                            ? 'Current recommendation'
                            : 'Evaluation complete'
                        }
                      </span>
                    )
                }
              </div>


              {
                evaluationError
                && (
                  <p
                    className="explore-careers-figma__evaluation-message explore-careers-figma__evaluation-message--error"
                    role="alert"
                  >
                    {
                      evaluationError
                    }
                  </p>
                )
              }


              {
                evaluationMessage
                && (
                  <p
                    className="explore-careers-figma__evaluation-message explore-careers-figma__evaluation-message--success"
                    role="status"
                  >
                    {
                      evaluationMessage
                    }
                  </p>
                )
              }


              {
                (
                  selectedCareer
                    .evaluated
                  || selectedCareer
                    .recommended
                )
                && (
                  <div className="explore-careers-figma__next-actions">
                    <div className="explore-careers-figma__next-actions-copy">
                      <h3>
                        Continue with this career
                      </h3>

                      <p>
                        Review your skill gaps or
                        find learning resources
                        for this career path.
                      </p>
                    </div>

                    <div className="explore-careers-figma__next-action-buttons">
                      <button
                        className="gn-button gn-button--primary"
                        type="button"
                        onClick={
                          openSelectedSkillGaps
                        }
                      >
                        View Skill Gaps
                      </button>

                      <button
                        className="career-recommendations-figma__secondary-button"
                        type="button"
                        onClick={
                          openSelectedLearningResources
                        }
                      >
                        Learning Resources
                      </button>
                    </div>
                  </div>
                )
              }
            </section>
          )
        }


        <section className="explore-careers-figma__catalogue">
          <div className="explore-careers-figma__catalogue-heading">
            <div>
              <h2>
                Careers
              </h2>

              <p>
                Twelve careers are shown
                per page.
              </p>
            </div>

            {
              pagination.total_pages
              > 0
              && (
                <span>
                  Page {
                    pagination.page
                  } of {
                    pagination.total_pages
                  }
                </span>
              )
            }
          </div>


          {
            loading
            && (
              <div className="career-guidance-loading-card">
                <h2>
                  Loading careers
                </h2>

                <p>
                  GradNavi is loading the
                  career catalogue.
                </p>
              </div>
            )
          }


          {
            loadError
            && !loading
            && (
              <div className="career-guidance-inline-state">
                <h3>
                  Career catalogue unavailable
                </h3>

                <p role="alert">
                  {
                    loadError
                  }
                </p>
              </div>
            )
          }


          {
            !loading
            && !loadError
            && careers.length === 0
            && (
              <div className="career-guidance-inline-state">
                <h3>
                  No careers found
                </h3>

                <p>
                  Try another search,
                  category, or status.
                </p>
              </div>
            )
          }


          {
            !loading
            && !loadError
            && careers.length > 0
            && (
              <div className="explore-careers-figma__grid">
                {
                  careers.map(
                    (career) => (
                      <article
                        key={
                          career
                            .career_id
                        }
                        className="explore-careers-figma__card"
                      >
                        <div className="explore-careers-figma__card-heading">
                          <span
                            className={
                              getStatusClass(
                                career
                                  .status,
                              )
                            }
                          >
                            {
                              formatStatus(
                                career
                                  .status,
                              )
                            }
                          </span>

                          {
                            career
                              .recommendation_rank
                            && (
                              <span className="explore-careers-figma__rank">
                                #{
                                  career
                                    .recommendation_rank
                                }
                              </span>
                            )
                          }
                        </div>

                        <h3>
                          {
                            career
                              .career_name
                          }
                        </h3>

                        <p className="explore-careers-figma__category">
                          {
                            career
                              .category
                            || 'Career category'
                          }
                        </p>

                        <p className="explore-careers-figma__description">
                          {
                            career
                              .description
                            || (
                              'No career description '
                              + 'is available yet.'
                            )
                          }
                        </p>

                        <div className="explore-careers-figma__card-footer">
                          <div>
                            <span>
                              Match
                            </span>

                            <strong>
                              {
                                formatScore(
                                  career
                                    .match_score,
                                )
                              }
                            </strong>
                          </div>

                          <button
                            className="career-recommendations-figma__secondary-button"
                            type="button"
                            onClick={
                              () =>
                                openCareer(
                                  career
                                    .career_id,
                                )
                            }
                          >
                            View Career
                          </button>
                        </div>
                      </article>
                    ),
                  )
                }
              </div>
            )
          }


          {
            !loading
            && !loadError
            && pagination.total_pages
            > 1
            && (
              <div className="explore-careers-figma__pagination">
                <button
                  className="career-recommendations-figma__secondary-button"
                  type="button"
                  disabled={
                    !pagination
                      .has_previous
                  }
                  onClick={
                    () => {
                      clearSelectedCareer()

                      setPage(
                        (current) =>
                          Math.max(
                            1,
                            current - 1,
                          ),
                      )
                    }
                  }
                >
                  Previous
                </button>

                <span>
                  Page {
                    pagination.page
                  } of {
                    pagination.total_pages
                  }
                </span>

                <button
                  className="career-recommendations-figma__secondary-button"
                  type="button"
                  disabled={
                    !pagination
                      .has_next
                  }
                  onClick={
                    () => {
                      clearSelectedCareer()

                      setPage(
                        (current) =>
                          current + 1,
                      )
                    }
                  }
                >
                  Next
                </button>
              </div>
            )
          }
        </section>
      </div>
    </main>
  )
}


export default ExploreCareersPage
