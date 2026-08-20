import EducationSection from '../components/profile/EducationSection'
import ExperienceSection from '../components/profile/ExperienceSection'
import ProjectSection from '../components/profile/ProjectSection'
import CareerGoalsSection from '../components/profile/CareerGoalsSection'

function StudentProfilePage() {
  return (
    <main>
      <h1>Student Profile</h1>

      <p>
        Manage the information GradNavi uses for career recommendations,
        readiness analysis, and future application support.
      </p>

      <section>
        <h2>Skills</h2>
        <p>Add and manage your skills and proficiency levels.</p>
      </section>

      <section>
        <h2>Interests</h2>
        <p>Add and manage your career and technology interests.</p>
      </section>


      <EducationSection />

      <ExperienceSection />

      <ProjectSection />

      <CareerGoalsSection />

      <section>
        <h2>Personality Responses</h2>
        <p>Manage responses used to support career matching.</p>
      </section>
    </main>
  )
}

export default StudentProfilePage