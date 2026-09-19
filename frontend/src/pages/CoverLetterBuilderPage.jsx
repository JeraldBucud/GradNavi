import {
  useNavigate,
} from 'react-router'


function CoverLetterBuilderPage() {
  const navigate = useNavigate()


  return (
    <main>
      <header>
        <h1>
          Cover Letter Builder
        </h1>

        <p>
          Generate an editable AI cover letter
          from approved Student Profile data and
          one supplied job description.
        </p>
      </header>


      <section className="gn-card">
        <h2>
          Cover Letter Builder
        </h2>

        <p>
          Your Student Profile supplies approved
          student information. A job description
          provides the role context.
        </p>

        <button
          className="gn-button gn-button--secondary"
          type="button"
          onClick={() =>
            navigate('/profile')
          }
        >
          Review Student Profile
        </button>
      </section>


      <section className="gn-notice gn-notice--info">
        <h2 className="gn-notice__title">
          Interface foundation
        </h2>

        <p className="gn-notice__body">
          Job-description input, generation, and
          editable draft controls are scheduled
          for the next WBS 6.5 checkpoint.
        </p>
      </section>
    </main>
  )
}


export default CoverLetterBuilderPage