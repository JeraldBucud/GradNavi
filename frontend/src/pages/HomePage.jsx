import { Link } from 'react-router'

import './HomePage.css'


/*
 * Landing Page content follows the approved Sprint 1-3
 * high-fidelity Figma screen.
 *
 * Future features such as Job Description Matcher and
 * Admin are intentionally excluded from the current
 * feature cards.
 */

const features = [
  {
    title: 'Career Recommendations',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
  {
    title: 'Skill Gap Analysis',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
  {
    title: 'Career Roadmap',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
  {
    title: 'Learning Resources',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
  {
    title: 'Resume Draft Generation',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
  {
    title: 'Cover Letter Draft Generation',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
  {
    title: 'Interview Practice',
    description:
      'Repository-aligned student capability using implemented Sprint 1-3 contracts.',
  },
]


const workflowSteps = [
  {
    number: '1',
    title: 'Build Your Profile',
  },
  {
    number: '2',
    title: 'Explore Career Matches',
  },
  {
    number: '3',
    title: 'Close Skill Gaps',
  },
  {
    number: '4',
    title: 'Prepare Applications',
  },
]


function HomePage() {
  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="landing-header__inner">
          <Link
            className="landing-brand"
            to="/"
            aria-label="GradNavi home"
          >
            GradNavi
          </Link>

          <nav
            className="landing-nav"
            aria-label="Landing page navigation"
          >
            <a href="#how-it-works">
              How It Works
            </a>

            <a href="#features">
              Features
            </a>

            <Link to="/login">
              Log In
            </Link>

            <Link
              className="gn-button gn-button--primary landing-header__cta"
              to="/register"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>


      <main>
        <section className="landing-hero">
          <div className="landing-container landing-hero__grid">
            <div className="landing-hero__content">
              <h1 className="landing-hero__title">
                Plan your career with clearer evidence and next steps.
              </h1>

              <div className="landing-hero__actions">
                <Link
                  className="gn-button gn-button--primary landing-button landing-button--primary"
                  to="/register"
                >
                  Get Started
                </Link>

                <Link
                  className="gn-button gn-button--secondary landing-button landing-button--login"
                  to="/login"
                >
                  Log In
                </Link>
              </div>

              <p className="landing-hero__description">
                Build your Student Profile, review deterministic GradNavi
                career matches, understand readiness and skill gaps, follow
                learning suggestions, and prepare AI-assisted drafts and
                interview practice content.
              </p>
            </div>


            <aside
              className="landing-preview"
              aria-label="Illustrative Student Dashboard preview"
            >
              <div className="landing-preview__header">
                <h2>
                  Student Dashboard Preview
                </h2>

                <span className="landing-preview__badge">
                  Illustrative sample
                </span>
              </div>

              <div className="landing-preview__metrics">
                <div className="landing-preview__metric">
                  <span className="landing-preview__metric-label">
                    Recommendation Score
                  </span>

                  <strong>
                    86%
                  </strong>

                  <span>
                    GradNavi Analysis
                  </span>
                </div>

                <div className="landing-preview__metric">
                  <span className="landing-preview__metric-label">
                    Readiness Score
                  </span>

                  <strong>
                    72%
                  </strong>

                  <span>
                    Separate career analysis
                  </span>
                </div>

                <div className="landing-preview__metric">
                  <span className="landing-preview__metric-label">
                    Skill Gaps
                  </span>

                  <strong>
                    3
                  </strong>

                  <span>
                    Missing / below
                  </span>
                </div>
              </div>

              <h3 className="landing-preview__actions-title">
                Recommended next actions
              </h3>

              <div className="landing-preview__actions">
                <div>
                  Review Career Recommendations
                </div>

                <div>
                  Open Skill Gap Analysis
                </div>

                <div>
                  Generate AI Resume Draft
                </div>
              </div>
            </aside>
          </div>
        </section>


        <section
          className="landing-section"
          id="features"
        >
          <div className="landing-container">
            <div className="landing-section__heading">
              <h2>
                What GradNavi Helps You Do
              </h2>

              <p>
                Current Sprint 1-3 capabilities only. Job Description Matcher
                and Admin are future work.
              </p>
            </div>

            <div className="landing-features-grid">
              {features.map((feature) => (
                <article
                  className="landing-feature-card"
                  key={feature.title}
                >
                  <span
                    className="landing-feature-card__marker"
                    aria-hidden="true"
                  >
                    ◦
                  </span>

                  <div>
                    <h3>
                      {feature.title}
                    </h3>

                    <p>
                      {feature.description}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>


        <section
          className="landing-section landing-section--workflow"
          id="how-it-works"
        >
          <div className="landing-container">
            <div className="landing-section__heading">
              <h2>
                How GradNavi Works
              </h2>

              <p>
                GradNavi separates deterministic analysis from AI-generated
                draft and practice content.
              </p>
            </div>

            <div className="landing-workflow-grid">
              {workflowSteps.map((step) => (
                <article
                  className="landing-workflow-card"
                  key={step.number}
                >
                  <div className="landing-workflow-card__metric">
                    <span>
                      Step {step.number}
                    </span>

                    <strong>
                      {step.number}
                    </strong>

                    <small>
                      {step.title}
                    </small>
                  </div>

                  <h3>
                    {step.title}
                  </h3>
                </article>
              ))}
            </div>
          </div>
        </section>


        <section className="landing-section landing-section--responsibilities">
          <div className="landing-container">
            <div className="landing-responsibilities">
              <h2>
                AI and GradNavi Analysis Responsibilities
              </h2>

              <div className="landing-responsibilities__grid">
                <article className="landing-responsibility-card landing-responsibility-card--analysis">
                  <h3>
                    GradNavi Analysis
                  </h3>

                  <p>
                    Scores, ranks, readiness, skill gaps, priority ordering.
                  </p>
                </article>

                <article className="landing-responsibility-card landing-responsibility-card--ai">
                  <h3>
                    AI-generated content
                  </h3>

                  <p>
                    Resume drafts, cover-letter drafts, interview questions,
                    feedback.
                  </p>
                </article>

                <article className="landing-responsibility-card landing-responsibility-card--student">
                  <h3>
                    Student responsibility
                  </h3>

                  <p>
                    Review generated content and maintain profile evidence.
                  </p>
                </article>
              </div>
            </div>
          </div>
        </section>


        <section className="landing-cta-section">
          <div className="landing-container">
            <div className="landing-cta">
              <div>
                <h2>
                  Ready to build your career plan?
                </h2>

                <p>
                  Start with your profile, then review matches and next steps.
                </p>
              </div>

              <div className="landing-cta__actions">
                <Link
                  className="gn-button gn-button--primary landing-button landing-button--create"
                  to="/register"
                >
                  Create Account
                </Link>

                <Link
                  className="gn-button gn-button--secondary landing-button landing-button--cta-login"
                  to="/login"
                >
                  Log In
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}


export default HomePage