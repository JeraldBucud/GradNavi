import { Routes, Route } from 'react-router'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import StudentProfilePage from './pages/StudentProfilePage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={<StudentProfilePage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App