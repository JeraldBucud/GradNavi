import EducationSection from '../components/profile/EducationSection'
import ExperienceSection from '../components/profile/ExperienceSection'
import ProjectSection from '../components/profile/ProjectSection'
import CareerGoalsSection from '../components/profile/CareerGoalsSection'
import SkillsSection from '../components/profile/SkillsSection'
import InterestsSection from '../components/profile/InterestsSection'
import PersonalityResponsesSection from '../components/profile/PersonalityResponsesSection'
import './StudentProfilePage.css'

function StudentProfilePage() {
  return (
    <main className="profile-page">
        <div className="profile-header">
            <h1>Student Profile</h1>

            <p>
                Manage the information GradNavi uses for career recommendations,
                readiness analysis, and future application support.
            </p>
        </div>

      <SkillsSection />
      <InterestsSection />
      <EducationSection />
      <ExperienceSection />
      <ProjectSection />
      <CareerGoalsSection />
      <PersonalityResponsesSection />
       
    </main>
    
  )
}

export default StudentProfilePage