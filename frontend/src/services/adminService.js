import apiRequest from './apiClient'


const ADMIN_BASE_PATH = '/administration'


/* Users */

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


function updateAdminUserStatus(userId, isActive) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/users/${userId}/status/`,
    {
      method: 'PATCH',
      body: { is_active: isActive },
      requiresAuth: true,
    },
  )
}


/* Shared helpers for careers, skills, learning resources */

function createAdminRecord(resourcePath, data) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/${resourcePath}/`,
    {
      method: 'POST',
      body: data,
      requiresAuth: true,
    },
  )
}


function updateAdminRecord(resourcePath, id, data) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/${resourcePath}/${id}/`,
    {
      method: 'PATCH',
      body: data,
      requiresAuth: true,
    },
  )
}


function deleteAdminRecord(resourcePath, id) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/${resourcePath}/${id}/`,
    {
      method: 'DELETE',
      requiresAuth: true,
    },
  )
}


/* Careers */

function listAdminCareers() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/careers/`,
    { requiresAuth: true },
  )
}


function createAdminCareer(data) {
  return createAdminRecord('careers', data)
}


function updateAdminCareer(id, data) {
  return updateAdminRecord('careers', id, data)
}


function deleteAdminCareer(id) {
  return deleteAdminRecord('careers', id)
}


/* Skills */

function listAdminSkills() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/skills/`,
    { requiresAuth: true },
  )
}


function createAdminSkill(data) {
  return createAdminRecord('skills', data)
}


function updateAdminSkill(id, data) {
  return updateAdminRecord('skills', id, data)
}


function deleteAdminSkill(id) {
  return deleteAdminRecord('skills', id)
}


/* Learning resources */

function listAdminLearningResources() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/learning-resources/`,
    { requiresAuth: true },
  )
}


function createAdminLearningResource(data) {
  return createAdminRecord('learning-resources', data)
}


function updateAdminLearningResource(id, data) {
  return updateAdminRecord('learning-resources', id, data)
}


function deleteAdminLearningResource(id) {
  return deleteAdminRecord('learning-resources', id)
}


/* Resource reports */

function listAdminResourceReports() {
  return apiRequest(
    `${ADMIN_BASE_PATH}/learning-resource-reports/`,
    { requiresAuth: true },
  )
}


function updateAdminResourceReportStatus(id, status) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/learning-resource-reports/${id}/`,
    {
      method: 'PATCH',
      body: { status },
      requiresAuth: true,
    },
  )
}


/* Audit records */

function listAdminAuditRecords(searchText = '') {
  const query = searchText
    ? `?search=${encodeURIComponent(searchText)}`
    : ''

  return apiRequest(
    `${ADMIN_BASE_PATH}/audit-records/${query}`,
    { requiresAuth: true },
  )
}


function getAdminAuditRecord(id) {
  return apiRequest(
    `${ADMIN_BASE_PATH}/audit-records/${id}/`,
    { requiresAuth: true },
  )
}


/* Analytics + dashboard */

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
  createAdminCareer,
  createAdminLearningResource,
  createAdminSkill,
  deleteAdminCareer,
  deleteAdminLearningResource,
  deleteAdminSkill,
  getAdminAnalytics,
  getAdminAuditRecord,
  getAdminDashboardSummary,
  listAdminAuditRecords,
  listAdminCareers,
  listAdminLearningResources,
  listAdminResourceReports,
  listAdminSkills,
  listAdminUsers,
  updateAdminCareer,
  updateAdminLearningResource,
  updateAdminResourceReportStatus,
  updateAdminSkill,
  updateAdminUserRole,
  updateAdminUserStatus,
}