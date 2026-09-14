import { Routes, Route } from 'react-router'

import ProtectedRoute from './components/auth/ProtectedRoute'
import MainLayout from './layouts/MainLayout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import StudentProfilePage from './pages/StudentProfilePage'
import NotFoundPage from './pages/NotFoundPage'


function App() {
  return (
    <Routes>
      {/*
       * Public screens with their own approved shells.
       */}
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


      {/*
       * Existing authenticated routes continue using MainLayout
       * until each approved high-fidelity screen is implemented.
       */}
      <Route element={<MainLayout />}>
        <Route element={<ProtectedRoute />}>
          <Route
            path="/profile"
            element={<StudentProfilePage />}
          />
        </Route>

        <Route
          path="*"
          element={<NotFoundPage />}
        />
      </Route>
    </Routes>
  )
}


export default App