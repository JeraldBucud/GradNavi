import { useState } from 'react'
import { Link } from 'react-router'

import gradNaviLogo from '../assets/brand/gradnavi-logo-primary.png'

import homepageHero from '../assets/landing/gradnavi-homepage-hero-graduate-career-path.png'
import careerExploration from '../assets/landing/gradnavi-career-exploration-students.png'
import aiGuidance from '../assets/landing/gradnavi-ai-guidance-students.png'
import skillDevelopment from '../assets/landing/gradnavi-skill-development-student.png'
import applicationPreparation from '../assets/landing/gradnavi-application-preparation.png'
import ctaBackground from '../assets/landing/gradnavi-cta-career-path-background.png'
import careerRecommendationsPreview from '../assets/landing/career-recommendations-preview.png'
import skillGapPreview from '../assets/landing/skill-gap-preview.png'

import './HomePage.css'


const trustItems = [
  {
    title: 'Your evidence first',
    description:
      'Recommendations start from the profile data you choose to provide.',
  },
  {
    title: 'AI explains the result',
    description:
      'AI adds clear explanations and guidance after structured scoring.',
  },
  {
    title: 'You stay in control',
    description:
      'Scores, drafts, and learning steps stay visible, editable, and reviewable.',
  },
]


function HomePage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] =
    useState(false)


  function closeMobileMenu() {
    setIsMobileMenuOpen(false)
  }


  function scrollToSection(event, sectionId) {
    event.preventDefault()

    const section =
      document.getElementById(sectionId)

    if (section) {
      section.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    }

    closeMobileMenu()
  }


  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="landing-header__inner">
          <Link
            className="landing-brand"
            to="/"
            aria-label="GradNavi home"
          >
            <img
              src={gradNaviLogo}
              alt="GradNavi"
            />
          </Link>

          <nav
            className="landing-nav landing-nav--desktop"
            aria-label="Public navigation"
          >
            <a
              href="#how-it-works"
              onClick={(event) => {
                scrollToSection(
                  event,
                  'how-it-works',
                )
              }}
            >
              How It Works
            </a>

            <a
              href="#ai-guidance"
              onClick={(event) => {
                scrollToSection(
                  event,
                  'ai-guidance',
                )
              }}
            >
              AI Guidance
            </a>

            <a
              href="#features"
              onClick={(event) => {
                scrollToSection(
                  event,
                  'features',
                )
              }}
            >
              Features
            </a>

            <Link to="/login">
              Log In
            </Link>

            <Link
              className="landing-button landing-button--primary landing-header__cta"
              to="/register"
            >
              Get Started
            </Link>
          </nav>

          <button
            className="landing-menu-button"
            type="button"
            aria-expanded={isMobileMenuOpen}
            aria-controls="landing-mobile-navigation"
            aria-label={
              isMobileMenuOpen
                ? 'Close navigation'
                : 'Open navigation'
            }
            onClick={() => {
              setIsMobileMenuOpen(
                (currentValue) => !currentValue,
              )
            }}
          >
            <span />
            <span />
            <span />
          </button>
        </div>

        {isMobileMenuOpen && (
          <nav
            className="landing-mobile-nav"
            id="landing-mobile-navigation"
            aria-label="Mobile public navigation"
          >
            <a
              href="#how-it-works"
              onClick={(event) => {
                scrollToSection(
                  event,
                  'how-it-works',
                )
              }}
            >
              How It Works
            </a>

            <a
              href="#ai-guidance"
              onClick={(event) => {
                scrollToSection(
                  event,
                  'ai-guidance',
                )
              }}
            >
              AI Guidance
            </a>

            <a
              href="#features"
              onClick={(event) => {
                scrollToSection(
                  event,
                  'features',
                )
              }}
            >
              Features
            </a>

            <Link
              to="/login"
              onClick={closeMobileMenu}
            >
              Log In
            </Link>

            <Link
              className="landing-button landing-button--primary"
              to="/register"
              onClick={closeMobileMenu}
            >
              Get Started
            </Link>
          </nav>
        )}
      </header>


      <main>
        <section className="landing-hero">
          <img
            className="landing-hero__image"
            src={homepageHero}
            alt=""
          />

          <div className="landing-hero__overlay" />

          <div className="landing-hero__inner">
            <div className="landing-hero__copy">
              <span className="landing-kicker landing-hero__badge">
                AI-POWERED CAREER GUIDANCE
              </span>

              <h1>
                Find Your Path.
                <br />
                Build Your Skills.
                <br />
                Get Career Ready.
              </h1>

              <p>
                GradNavi turns your profile evidence
                into career recommendations, skill-gap
                insights, personalised learning, and
                application guidance.
              </p>

              <div className="landing-actions">
                <Link
                  className="landing-button landing-button--primary"
                  to="/register"
                >
                  Get Started
                </Link>

                <a
                  className="landing-button landing-button--secondary"
                  href="#how-it-works"
                  onClick={(event) => {
                    scrollToSection(
                      event,
                      'how-it-works',
                    )
                  }}
                >
                  See How It Works
                </a>
              </div>
            </div>
          </div>
        </section>


        <section
          className="landing-trust"
          id="how-it-works"
        >
          <div className="landing-trust__inner">
            {trustItems.map((item) => (
              <article
                className="landing-trust__item"
                key={item.title}
              >
                <h2>
                  {item.title}
                </h2>

                <p>
                  {item.description}
                </p>
              </article>
            ))}
          </div>
        </section>


        <section className="landing-feature-section landing-feature-section--muted">
          <div className="landing-feature-section__inner">
            <div className="landing-feature-section__media">
              <img
                src={careerExploration}
                alt="Students exploring career directions"
              />
            </div>

            <div className="landing-feature-section__copy">
              <span className="landing-kicker">
                EXPLORE
              </span>

              <h2>
                See career directions that connect
                with your profile.
              </h2>

              <p>
                Browse career options, compare structured
                match evidence, and choose the path you
                want GradNavi to use across skill gaps,
                roadmap, and learning resources.
              </p>

              <ul>
                <li>
                  Career recommendations with clear
                  match evidence
                </li>

                <li>
                  Explore careers beyond your current
                  top recommendation
                </li>

                <li>
                  Keep one selected career consistent
                  across guidance pages
                </li>
              </ul>

              <a
                className="landing-button landing-button--secondary"
                href="#product-evidence"
                onClick={(event) => {
                  scrollToSection(
                    event,
                    'product-evidence',
                  )
                }}
              >
                Explore Career Guidance
              </a>
            </div>
          </div>
        </section>


        <section
          className="landing-feature-section"
          id="ai-guidance"
        >
          <div className="landing-feature-section__inner landing-feature-section__inner--reverse">
            <div className="landing-feature-section__copy">
              <span className="landing-kicker">
                AI GUIDANCE
              </span>

              <h2>
                Understand why a career fits,
                where the gaps are, and what to do next.
              </h2>

              <p>
                GradNavi keeps structured scores separate
                from AI explanations. The AI layer explains
                the evidence, summarises your gaps, and
                gives focused next steps without changing
                the underlying score.
              </p>

              <div className="landing-ai-points">
                <article>
                  <h3>
                    Why this career matches
                  </h3>

                  <p>
                    Explains the strongest evidence
                    behind each recommendation.
                  </p>
                </article>

                <article>
                  <h3>
                    AI Gap Summary
                  </h3>

                  <p>
                    Explains readiness and turns unresolved
                    gaps into clear next actions.
                  </p>
                </article>

                <article>
                  <h3>
                    Roadmap guidance
                  </h3>

                  <p>
                    Adds Why this matters and Your focus
                    to structured development steps.
                  </p>
                </article>
              </div>
            </div>

            <div className="landing-feature-section__media">
              <img
                src={aiGuidance}
                alt="Students using AI-supported career guidance"
              />
            </div>
          </div>
        </section>


        <section
          className="landing-growth"
          id="features"
        >
          <div className="landing-section-heading">
            <span className="landing-kicker">
              FROM LEARNING TO APPLICATIONS
            </span>

            <h2>
              Build evidence. Improve readiness.
              Prepare stronger applications.
            </h2>

            <p>
              GradNavi connects learning resources,
              roadmap progress, resume drafting,
              cover letters, job matching, and
              interview preparation around the same
              Student Profile.
            </p>
          </div>

          <div className="landing-growth__cards">
            <article className="landing-story-card">
              <img
                src={skillDevelopment}
                alt="Student developing career skills"
              />

              <div className="landing-story-card__copy">
                <h3>
                  Build your skills
                </h3>

                <p>
                  Follow an ordered roadmap and use
                  learning resources tied to unresolved
                  gaps.
                </p>
              </div>
            </article>

            <article className="landing-story-card">
              <img
                src={applicationPreparation}
                alt="Students preparing career applications"
              />

              <div className="landing-story-card__copy">
                <h3>
                  Prepare to apply
                </h3>

                <p>
                  Turn your profile and job context
                  into editable resume and
                  cover-letter drafts.
                </p>
              </div>
            </article>
          </div>
        </section>


        <section
          className="landing-product"
          id="product-evidence"
        >
          <div className="landing-section-heading">
            <span className="landing-kicker">
              INSIDE GRADNAVI
            </span>

            <h2>
              The guidance stays visible and inspectable.
            </h2>

            <p>
              See the real product experience, including
              recommendation evidence and the AI Gap
              Summary, with the reasoning kept visible
              and reviewable.
            </p>
          </div>

          <div className="landing-product__grid">
            <article className="landing-product-card">
              <div className="landing-product-card__image">
                <img
                  src={careerRecommendationsPreview}
                  alt="GradNavi Career Recommendations screen"
                />
              </div>

              <h3>
                Career Recommendations
              </h3>
            </article>

            <article className="landing-product-card">
              <div className="landing-product-card__image">
                <img
                  src={skillGapPreview}
                  alt="GradNavi Skill Gap Analysis screen"
                />
              </div>

              <h3>
                Skill Gap Analysis
              </h3>
            </article>
          </div>
        </section>


        <section className="landing-final-cta">
          <img
            className="landing-final-cta__background"
            src={ctaBackground}
            alt=""
          />

          <div className="landing-final-cta__overlay" />

          <div className="landing-final-cta__inner">
            <h2>
              Ready to move from career uncertainty
              to a clear next step?
            </h2>

            <p>
              Build your profile once, then use the same
              evidence across recommendations, skill gaps,
              roadmap, learning, and application preparation.
            </p>

            <div className="landing-actions">
              <Link
                className="landing-button landing-button--primary"
                to="/register"
              >
                Create Your Profile
              </Link>

              <Link
                className="landing-button landing-button--secondary"
                to="/login"
              >
                Log In
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}


export default HomePage
