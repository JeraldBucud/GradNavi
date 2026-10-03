import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  Camera,
  CheckCircle2,
  KeyRound,
  LockKeyhole,
  Mail,
  Save,
  ShieldCheck,
  Trash2,
  Upload,
  UserRound,
} from 'lucide-react'

import {
  changePassword,
  getAccountSettings,
  removeProfilePhoto,
  updateAccountSettings,
  uploadProfilePhoto,
} from '../services/authService'

import './SettingsPage.css'


const PROFILE_PHOTO_MAX_BYTES =
  5 * 1024 * 1024

const PROFILE_PHOTO_TYPES =
  new Set([
    'image/jpeg',
    'image/png',
    'image/webp',
  ])


function getFirstErrorMessage(
  value,
) {
  if (!value) {
    return ''
  }

  if (
    typeof value === 'string'
  ) {
    return value
  }

  if (
    Array.isArray(value)
  ) {
    for (const item of value) {
      const message =
        getFirstErrorMessage(
          item,
        )

      if (message) {
        return message
      }
    }

    return ''
  }

  if (
    typeof value === 'object'
  ) {
    for (
      const nestedValue
      of Object.values(value)
    ) {
      const message =
        getFirstErrorMessage(
          nestedValue,
        )

      if (message) {
        return message
      }
    }
  }

  return ''
}


function getRequestErrorMessage(
  requestError,
  fallbackMessage,
) {
  const details =
    requestError
      ?.data
      ?.error
      ?.details

  return (
    getFirstErrorMessage(details)
    || requestError?.message
    || fallbackMessage
  )
}


function SettingsPage() {
  const fileInputRef =
    useRef(null)

  const [
    account,
    setAccount,
  ] = useState(null)

  const [
    profileForm,
    setProfileForm,
  ] = useState({
    first_name: '',
    last_name: '',
  })

  const [
    passwordForm,
    setPasswordForm,
  ] = useState({
    current_password: '',
    new_password: '',
    new_password_confirm: '',
  })

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    isSavingProfile,
    setIsSavingProfile,
  ] = useState(false)

  const [
    isUploadingPhoto,
    setIsUploadingPhoto,
  ] = useState(false)

  const [
    isRemovingPhoto,
    setIsRemovingPhoto,
  ] = useState(false)

  const [
    isChangingPassword,
    setIsChangingPassword,
  ] = useState(false)

  const [
    loadError,
    setLoadError,
  ] = useState('')

  const [
    profileError,
    setProfileError,
  ] = useState('')

  const [
    profileMessage,
    setProfileMessage,
  ] = useState('')

  const [
    photoError,
    setPhotoError,
  ] = useState('')

  const [
    photoMessage,
    setPhotoMessage,
  ] = useState('')

  const [
    passwordError,
    setPasswordError,
  ] = useState('')

  const [
    passwordMessage,
    setPasswordMessage,
  ] = useState('')


  useEffect(() => {
    let isActive = true

    async function loadSettings() {
      try {
        setIsLoading(true)
        setLoadError('')

        const accountData =
          await getAccountSettings()

        if (!isActive) {
          return
        }

        setAccount(
          accountData,
        )

        setProfileForm({
          first_name:
            accountData
              ?.first_name
              || '',

          last_name:
            accountData
              ?.last_name
              || '',
        })
      } catch (
        requestError
      ) {
        if (!isActive) {
          return
        }

        setLoadError(
          getRequestErrorMessage(
            requestError,
            (
              'Unable to load '
              + 'your account settings.'
            ),
          ),
        )
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    loadSettings()

    return () => {
      isActive = false
    }
  }, [])


  function updateProfileField(
    event,
  ) {
    const {
      name,
      value,
    } = event.target

    setProfileForm(
      (currentForm) => ({
        ...currentForm,
        [name]: value,
      }),
    )

    setProfileError('')
    setProfileMessage('')
  }


  function updatePasswordField(
    event,
  ) {
    const {
      name,
      value,
    } = event.target

    setPasswordForm(
      (currentForm) => ({
        ...currentForm,
        [name]: value,
      }),
    )

    setPasswordError('')
    setPasswordMessage('')
  }


  async function handleProfileSubmit(
    event,
  ) {
    event.preventDefault()

    try {
      setIsSavingProfile(true)
      setProfileError('')
      setProfileMessage('')

      const updatedAccount =
        await updateAccountSettings(
          {
            first_name:
              profileForm
                .first_name,

            last_name:
              profileForm
                .last_name,
          },
        )

      setAccount(
        updatedAccount,
      )

      setProfileForm({
        first_name:
          updatedAccount
            .first_name,

        last_name:
          updatedAccount
            .last_name,
      })

      setProfileMessage(
        'Account details updated successfully.',
      )
    } catch (
      requestError
    ) {
      setProfileError(
        getRequestErrorMessage(
          requestError,
          (
            'Unable to update '
            + 'your account details.'
          ),
        ),
      )
    } finally {
      setIsSavingProfile(false)
    }
  }


  async function handlePhotoSelected(
    event,
  ) {
    const file =
      event.target.files?.[0]

    event.target.value = ''

    if (!file) {
      return
    }

    setPhotoError('')
    setPhotoMessage('')

    if (
      !PROFILE_PHOTO_TYPES.has(
        file.type,
      )
    ) {
      setPhotoError(
        'Choose a JPEG, PNG, or WebP image.',
      )

      return
    }

    if (
      file.size
      > PROFILE_PHOTO_MAX_BYTES
    ) {
      setPhotoError(
        'Profile photos must be 5 MB or smaller.',
      )

      return
    }

    try {
      setIsUploadingPhoto(true)

      const updatedAccount =
        await uploadProfilePhoto(
          file,
        )

      setAccount(
        updatedAccount,
      )

      setPhotoMessage(
        'Profile photo updated successfully.',
      )
    } catch (
      requestError
    ) {
      setPhotoError(
        getRequestErrorMessage(
          requestError,
          (
            'Unable to upload '
            + 'your profile photo.'
          ),
        ),
      )
    } finally {
      setIsUploadingPhoto(false)
    }
  }


  async function handleRemovePhoto() {
    try {
      setIsRemovingPhoto(true)
      setPhotoError('')
      setPhotoMessage('')

      const updatedAccount =
        await removeProfilePhoto()

      setAccount(
        updatedAccount,
      )

      setPhotoMessage(
        'Profile photo removed.',
      )
    } catch (
      requestError
    ) {
      setPhotoError(
        getRequestErrorMessage(
          requestError,
          (
            'Unable to remove '
            + 'your profile photo.'
          ),
        ),
      )
    } finally {
      setIsRemovingPhoto(false)
    }
  }


  async function handlePasswordSubmit(
    event,
  ) {
    event.preventDefault()

    setPasswordError('')
    setPasswordMessage('')

    if (
      passwordForm
        .new_password
      !== passwordForm
        .new_password_confirm
    ) {
      setPasswordError(
        'New password confirmation does not match.',
      )

      return
    }

    try {
      setIsChangingPassword(true)

      const responseData =
        await changePassword(
          passwordForm,
        )

      setPasswordForm({
        current_password: '',
        new_password: '',
        new_password_confirm: '',
      })

      setPasswordMessage(
        responseData?.message
        || 'Password changed successfully.',
      )
    } catch (
      requestError
    ) {
      setPasswordError(
        getRequestErrorMessage(
          requestError,
          (
            'Unable to change '
            + 'your password.'
          ),
        ),
      )
    } finally {
      setIsChangingPassword(false)
    }
  }


  if (isLoading) {
    return (
      <main className="settings-page">
        <div className="settings-page__state">
          <strong>
            Loading settings
          </strong>

          <p>
            Retrieving your account details.
          </p>
        </div>
      </main>
    )
  }


  if (
    loadError
    || !account
  ) {
    return (
      <main className="settings-page">
        <div className="settings-page__state settings-page__state--error">
          <strong>
            Unable to load settings
          </strong>

          <p>
            {loadError
            || 'Account settings are unavailable.'}
          </p>
        </div>
      </main>
    )
  }


  const displayName =
    [
      account.first_name,
      account.last_name,
    ]
      .filter(Boolean)
      .join(' ')
      || 'Student'

  const accountInitial =
    displayName
      .charAt(0)
      .toUpperCase()


  return (
    <main className="settings-page">
      <header className="settings-page__heading">
        <div>
          <span className="settings-page__eyebrow">
            Account preferences
          </span>

          <h1>
            Settings
          </h1>

          <p>
            Manage your account details,
            profile photo, and password.
          </p>
        </div>

        <div className="settings-page__security-status">
          <ShieldCheck
            size={18}
            strokeWidth={1.8}
            aria-hidden="true"
          />

          <span>
            Secure account
          </span>
        </div>
      </header>


      <section className="settings-card">
        <div className="settings-card__heading">
          <div className="settings-card__icon">
            <UserRound
              size={20}
              strokeWidth={1.8}
              aria-hidden="true"
            />
          </div>

          <div>
            <h2>
              Account
            </h2>

            <p>
              Update the name and photo
              shown across GradNavi.
            </p>
          </div>
        </div>


        <div className="settings-photo">
          <div className="settings-photo__preview">
            {account.profile_photo ? (
              <img
                src={account.profile_photo}
                alt={`${displayName} profile`}
              />
            ) : (
              <span
                aria-hidden="true"
              >
                {accountInitial}
              </span>
            )}
          </div>

          <div className="settings-photo__content">
            <div>
              <h3>
                Profile photo
              </h3>

              <p>
                JPEG, PNG, or WebP.
                Maximum file size 5 MB.
              </p>
            </div>

            <div className="settings-photo__actions">
              <input
                ref={fileInputRef}
                className="settings-photo__input"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handlePhotoSelected}
              />

              <button
                className="settings-button settings-button--secondary"
                type="button"
                disabled={
                  isUploadingPhoto
                  || isRemovingPhoto
                }
                onClick={() =>
                  fileInputRef
                    .current
                    ?.click()
                }
              >
                {isUploadingPhoto ? (
                  <>
                    <Camera
                      size={16}
                      aria-hidden="true"
                    />

                    Uploading
                  </>
                ) : (
                  <>
                    <Upload
                      size={16}
                      aria-hidden="true"
                    />

                    {account.profile_photo
                      ? 'Replace photo'
                      : 'Upload photo'}
                  </>
                )}
              </button>

              <button
                className="settings-button settings-button--danger"
                type="button"
                disabled={
                  !account.profile_photo
                  || isUploadingPhoto
                  || isRemovingPhoto
                }
                onClick={handleRemovePhoto}
              >
                <Trash2
                  size={16}
                  aria-hidden="true"
                />

                {isRemovingPhoto
                  ? 'Removing'
                  : 'Remove'}
              </button>
            </div>

            {photoMessage ? (
              <p className="settings-message settings-message--success">
                <CheckCircle2
                  size={15}
                  aria-hidden="true"
                />

                {photoMessage}
              </p>
            ) : null}

            {photoError ? (
              <p className="settings-message settings-message--error">
                {photoError}
              </p>
            ) : null}
          </div>
        </div>


        <form
          className="settings-form"
          onSubmit={handleProfileSubmit}
        >
          <div className="settings-form__grid">
            <label className="settings-field">
              <span>
                First name
              </span>

              <input
                name="first_name"
                type="text"
                autoComplete="given-name"
                value={
                  profileForm.first_name
                }
                onChange={updateProfileField}
              />
            </label>

            <label className="settings-field">
              <span>
                Last name
              </span>

              <input
                name="last_name"
                type="text"
                autoComplete="family-name"
                value={
                  profileForm.last_name
                }
                onChange={updateProfileField}
              />
            </label>

            <label className="settings-field settings-field--wide">
              <span>
                Email address
              </span>

              <div className="settings-field__readonly">
                <Mail
                  size={17}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />

                <input
                  type="email"
                  value={account.email}
                  readOnly
                  aria-readonly="true"
                />
              </div>

              <small>
                Email changes are not
                available in this version.
              </small>
            </label>
          </div>

          <div className="settings-form__footer">
            <div>
              {profileMessage ? (
                <p className="settings-message settings-message--success">
                  <CheckCircle2
                    size={15}
                    aria-hidden="true"
                  />

                  {profileMessage}
                </p>
              ) : null}

              {profileError ? (
                <p className="settings-message settings-message--error">
                  {profileError}
                </p>
              ) : null}
            </div>

            <button
              className="settings-button settings-button--primary"
              type="submit"
              disabled={isSavingProfile}
            >
              <Save
                size={16}
                strokeWidth={1.8}
                aria-hidden="true"
              />

              {isSavingProfile
                ? 'Saving'
                : 'Save changes'}
            </button>
          </div>
        </form>
      </section>


      <section className="settings-card">
        <div className="settings-card__heading">
          <div className="settings-card__icon">
            <KeyRound
              size={20}
              strokeWidth={1.8}
              aria-hidden="true"
            />
          </div>

          <div>
            <h2>
              Security
            </h2>

            <p>
              Change your password using
              your current password.
            </p>
          </div>
        </div>


        <form
          className="settings-form"
          onSubmit={handlePasswordSubmit}
        >
          <div className="settings-form__grid">
            <label className="settings-field settings-field--wide">
              <span>
                Current password
              </span>

              <div className="settings-field__password">
                <LockKeyhole
                  size={17}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />

                <input
                  name="current_password"
                  type="password"
                  autoComplete="current-password"
                  value={
                    passwordForm
                      .current_password
                  }
                  onChange={updatePasswordField}
                  required
                />
              </div>
            </label>

            <label className="settings-field">
              <span>
                New password
              </span>

              <input
                name="new_password"
                type="password"
                autoComplete="new-password"
                value={
                  passwordForm
                    .new_password
                }
                onChange={updatePasswordField}
                required
              />
            </label>

            <label className="settings-field">
              <span>
                Confirm new password
              </span>

              <input
                name="new_password_confirm"
                type="password"
                autoComplete="new-password"
                value={
                  passwordForm
                    .new_password_confirm
                }
                onChange={updatePasswordField}
                required
              />
            </label>
          </div>

          <div className="settings-password-note">
            <ShieldCheck
              size={17}
              strokeWidth={1.8}
              aria-hidden="true"
            />

            <p>
              Your new password must pass
              GradNavi's account security rules.
            </p>
          </div>

          <div className="settings-form__footer">
            <div>
              {passwordMessage ? (
                <p className="settings-message settings-message--success">
                  <CheckCircle2
                    size={15}
                    aria-hidden="true"
                  />

                  {passwordMessage}
                </p>
              ) : null}

              {passwordError ? (
                <p className="settings-message settings-message--error">
                  {passwordError}
                </p>
              ) : null}
            </div>

            <button
              className="settings-button settings-button--primary"
              type="submit"
              disabled={isChangingPassword}
            >
              <KeyRound
                size={16}
                strokeWidth={1.8}
                aria-hidden="true"
              />

              {isChangingPassword
                ? 'Changing password'
                : 'Change password'}
            </button>
          </div>
        </form>
      </section>
    </main>
  )
}


export default SettingsPage
