import { Routes, Route } from 'react-router'

import ProtectedRoute from './components/auth/ProtectedRoute'
import MainLayout from './layouts/MainLayout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import StudentProfilePage from './pages/StudentProfilePage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <Routes>
      {/*
       * The public Landing Page owns its approved Figma header.
       * Keeping it outside MainLayout prevents the temporary
       * development navigation from appearing above it.
       */}
      <Route path="/" element={<HomePage />} />

      {/*
       * Existing Sprint 1 application routes keep using MainLayout
       * until their approved high-fidelity screens are implemented.
       */}
      <Route element={<MainLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/profile" element={<StudentProfilePage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App