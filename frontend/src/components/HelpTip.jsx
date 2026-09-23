import {
  useEffect,
  useId,
  useRef,
  useState,
} from 'react'

import './HelpTip.css'


function HelpTip({
  label,
  title,
  text,
}) {
  const [
    open,
    setOpen,
  ] = useState(false)

  const wrapperRef =
    useRef(null)

  const rawId =
    useId()

  const popoverId =
    (
      'document-help-'
      + rawId.replace(
        /:/g,
        '',
      )
    )


  useEffect(
    () => {
      if (!open) {
        return undefined
      }

      function handlePointerDown(
        event,
      ) {
        if (
          wrapperRef.current
          && !wrapperRef.current.contains(
            event.target,
          )
        ) {
          setOpen(false)
        }
      }


      function handleKeyDown(
        event,
      ) {
        if (
          event.key
          === 'Escape'
        ) {
          setOpen(false)
        }
      }


      document.addEventListener(
        'pointerdown',
        handlePointerDown,
      )

      document.addEventListener(
        'keydown',
        handleKeyDown,
      )


      return () => {
        document.removeEventListener(
          'pointerdown',
          handlePointerDown,
        )

        document.removeEventListener(
          'keydown',
          handleKeyDown,
        )
      }
    },
    [
      open,
    ],
  )


  return (
    <span
      ref={wrapperRef}
      className="document-help"
    >
      <button
        className="document-help__button"
        type="button"
        aria-label={label}
        aria-expanded={open}
        aria-controls={popoverId}
        onClick={
          (event) => {
            event.preventDefault()
            event.stopPropagation()

            setOpen(
              (current) =>
                !current,
            )
          }
        }
      >
        ?
      </button>

      {
        open
          ? (
            <span
              id={popoverId}
              className="document-help__popover"
              role="tooltip"
            >
              <strong
                className="document-help__title"
              >
                {title}
              </strong>

              <span
                className="document-help__text"
              >
                {text}
              </span>
            </span>
          )
          : null
      }
    </span>
  )
}


export default HelpTip
