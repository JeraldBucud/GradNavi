import { Route, Routes } from 'react-router'

import ProtectedRoute from './components/auth/ProtectedRoute'
import StudentLayout from './layouts/StudentLayout'
import CareerRecommendationsPage from './pages/CareerRecommendationsPage'
import CareerRoadmapPage from './pages/CareerRoadmapPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import LearningResourcesPage from './pages/LearningResourcesPage'
import NotFoundPage from './pages/NotFoundPage'
import RegisterPage from './pages/RegisterPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import SkillGapAnalysisPage from './pages/SkillGapAnalysisPage'
import StudentProfilePage from './pages/StudentProfilePage'


function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={<HomePage />}
      />

      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        path="/register"
        element={<RegisterPage />}
      />

      <Route
        path="/forgot-password"
        element={<ForgotPasswordPage />}
      />

      <Route
        path="/password/reset/confirm/"
        element={<ResetPasswordPage />}
      />

      <Route element={<ProtectedRoute />}>
        <Route element={<StudentLayout />}>
          <Route
            path="/profile"
            element={<StudentProfilePage />}
          />

          <Route
            path="/career-recommendations"
            element={<CareerRecommendationsPage />}
          />

          <Route
            path="/skill-gap-analysis"
            element={<SkillGapAnalysisPage />}
          />

          <Route
            path="/career-roadmap"
            element={<CareerRoadmapPage />}
          />

          <Route
            path="/learning-resources"
            element={<LearningResourcesPage />}
          />
        </Route>
      </Route>

      <Route
        path="*"
        element={<NotFoundPage />}
      />
    </Routes>
  )
}


export default App
