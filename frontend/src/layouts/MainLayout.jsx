import { Link, Outlet } from 'react-router'

function MainLayout() {
  return (
    <>
      <header>
        <nav>
          <Link to="/">GradNavi</Link>
          <Link to="/">Home</Link>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
          <Link to="/profile">Student Profile</Link>
        </nav>
      </header>

      <Outlet />
    </>
  )
}

export default MainLayout