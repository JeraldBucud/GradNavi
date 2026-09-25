import apiRequest from './apiClient'


const ADMIN_BASE_PATH = '/administration'


function listAdminUsers() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/users/`,
    { requiresAuth: true },
  )
}


function listAdminCareers() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/careers/`,
    { requiresAuth: true },
  )
}


function listAdminSkills() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/skills/`,
    { requiresAuth: true },
  )
}


function listAdminLearningResources() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/learning-resources/`,
    { requiresAuth: true },
  )
}


async function getAdminDashboardSummary() {
  const [
    users,
    careers,
    skills,
    learningResources,
  ] = await Promise.all([
    listAdminUsers(),
    listAdminCareers(),
    listAdminSkills(),
    listAdminLearningResources(),
  ])

  return {
    studentCount: users.filter(
      (user) => user.role === 'student',
    ).length,
    activeCareerCount: careers.filter(
      (career) => career.active,
    ).length,
    skillCount: skills.length,
    activeResourceCount: learningResources.filter(
      (resource) => resource.is_active,
    ).length,
  }
}


export {
  getAdminDashboardSummary,
  listAdminCareers,
  listAdminLearningResources,
  listAdminSkills,
  listAdminUsers,
}