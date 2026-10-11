const ACTIVE_INTERVIEW_SESSION_KEY =
  'gradnavi_active_interview_session_v1'

const ACTIVE_INTERVIEW_SESSION_VERSION = 1


function clearActiveInterviewSession() {
  if (
    typeof window === 'undefined'
  ) {
    return
  }

  window.sessionStorage.removeItem(
    ACTIVE_INTERVIEW_SESSION_KEY,
  )
}


function getActiveInterviewSession() {
  if (
    typeof window === 'undefined'
  ) {
    return null
  }

  const storedSession =
    window.sessionStorage.getItem(
      ACTIVE_INTERVIEW_SESSION_KEY,
    )

  if (!storedSession) {
    return null
  }

  try {
    const parsedSession =
      JSON.parse(storedSession)

    if (
      !parsedSession
      || typeof parsedSession !== 'object'
      || parsedSession.schemaVersion
        !== ACTIVE_INTERVIEW_SESSION_VERSION
    ) {
      clearActiveInterviewSession()

      return null
    }

    return parsedSession
  }
  catch {
    clearActiveInterviewSession()

    return null
  }
}


function storeActiveInterviewSession(
  sessionData,
) {
  if (
    typeof window === 'undefined'
  ) {
    return
  }

  window.sessionStorage.setItem(
    ACTIVE_INTERVIEW_SESSION_KEY,
    JSON.stringify({
      schemaVersion:
        ACTIVE_INTERVIEW_SESSION_VERSION,
      ...sessionData,
      updatedAt:
        new Date().toISOString(),
    }),
  )
}


function patchActiveInterviewSession(
  sessionData,
) {
  const currentSession =
    getActiveInterviewSession()
    || {}

  storeActiveInterviewSession({
    ...currentSession,
    ...sessionData,
  })
}


export {
  ACTIVE_INTERVIEW_SESSION_KEY,
  clearActiveInterviewSession,
  getActiveInterviewSession,
  patchActiveInterviewSession,
  storeActiveInterviewSession,
}
