import apiRequest from './apiClient'


const ADMIN_BASE_PATH = '/administration'


function listAdminUsers() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/users/`,
    { requiresAuth: true },
  )
}


function updateAdminUserRole(userId, role) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/users/${userId}/role/`,
    {
      method: 'PATCH',
      body: { role },
      requiresAuth: true,
    },
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


function listAdminResourceReports() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/learning-resource-reports/`,
    { requiresAuth: true },
  )
}


function getAdminAnalytics() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/analytics/`,
    { requiresAuth: true },
  )
}

async function getAdminDashboardSummary() {
  const [
    users,
    careers,
    skills,
    learningResources,
    resourceReports,
  ] = await Promise.all([
    listAdminUsers(),
    listAdminCareers(),
    listAdminSkills(),
    listAdminLearningResources(),
    listAdminResourceReports(),
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
    pendingReportCount: resourceReports.filter(
      (report) => report.status === 'open',
    ).length,
  }
}


export {
  getAdminAnalytics,
  getAdminDashboardSummary,
  listAdminCareers,
  listAdminLearningResources,
  listAdminResourceReports,
  listAdminSkills,
  listAdminUsers,
  updateAdminUserRole,
}