import { Link } from 'react-router'

import gradNaviLogoReversed from '../../assets/brand/gradnavi-logo-reversed-no-background.svg'
import authVisual from '../../assets/landing/gradnavi-homepage-hero-graduate-career-path.webp'

import './AuthLayout.css'


function AuthLayout({
  children,
  variant = '',
}) {
  const shellClassName =
    variant
      ? `auth-shell auth-shell--${variant}`
      : 'auth-shell'

  return (
    <main className={shellClassName}>
      <aside className="auth-shell__visual">
        <img
          className="auth-shell__visual-image"
          src={authVisual}
          alt=""
        />

        <div className="auth-shell__visual-overlay" />

        <div className="auth-shell__visual-content">
          <Link
            className="auth-shell__desktop-brand"
            to="/"
            aria-label="GradNavi home"
          >
            <img
              src={gradNaviLogoReversed}
              alt="GradNavi"
            />
          </Link>

          <div className="auth-shell__brand-message">
            <h1>
              Find Your Path.
              <br />
              Build Your Skills.
              <br />
              Get Career Ready.
            </h1>

            <p>
              Career guidance built around your skills,
              goals, and progress.
            </p>

            <div
              className="auth-shell__feature-row"
              aria-label="GradNavi features"
            >
              <span>
                Career Recommendations
              </span>

              <span>
                Skill Gap Analysis
              </span>

              <span>
                Career Roadmap
              </span>
            </div>
          </div>
        </div>
      </aside>


      <section className="auth-shell__form-panel">
        <header className="auth-shell__mobile-header">
          <Link
            to="/"
            aria-label="GradNavi home"
          >
            <img
              src={gradNaviLogoReversed}
              alt="GradNavi"
            />
          </Link>
        </header>

        <div className="auth-shell__form-panel-inner">
          <Link
            className="auth-shell__back-link"
            to="/"
          >
            ← Back to GradNavi
          </Link>

          {children}
        </div>
      </section>
    </main>
  )
}


export default AuthLayout
