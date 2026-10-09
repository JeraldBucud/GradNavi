let Document
let Packer
let Paragraph
let TextRun
let AlignmentType
let BorderStyle
let jsPDF

let docxModulePromise
let jsPdfModulePromise


async function ensureDocxLibrary() {
  if (
    Document
    && Packer
    && Paragraph
    && TextRun
    && AlignmentType
    && BorderStyle
  ) {
    return
  }

  if (!docxModulePromise) {
    docxModulePromise =
      import('docx')
  }

  const module =
    await docxModulePromise

  Document =
    module.Document

  Packer =
    module.Packer

  Paragraph =
    module.Paragraph

  TextRun =
    module.TextRun

  AlignmentType =
    module.AlignmentType

  BorderStyle =
    module.BorderStyle
}


async function ensurePdfLibrary() {
  if (jsPDF) {
    return
  }

  if (!jsPdfModulePromise) {
    jsPdfModulePromise =
      import('jspdf')
  }

  const module =
    await jsPdfModulePromise

  jsPDF =
    module.jsPDF
}


const WORD_FONT = 'Arial'
const WORD_BODY_SIZE = 21
const WORD_HEADING_SIZE = 23

const PDF_FONT = 'helvetica'
const PDF_BODY_SIZE = 9.7
const PDF_HEADING_SIZE = 11


function normaliseExportText(
  value,
) {
  return String(
    value || '',
  )
    .replace(
      /[\u2010\u2011\u2012\u2013\u2014\u2212]/g,
      '-',
    )
    .replace(
      /\u00a0/g,
      ' ',
    )
    .replace(
      /[\u2018\u2019]/g,
      "'",
    )
    .replace(
      /[\u201c\u201d]/g,
      '"',
    )
    .replace(
      /\u2026/g,
      '...',
    )
}


function safeText(value) {
  return normaliseExportText(
    value,
  ).trim()
}


function safeList(value) {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map(
      (item) =>
        safeText(
          item,
        ),
    )
    .filter(Boolean)
}


function safeProfileList(
  profile,
  key,
) {
  const value =
    profile?.[key]

  return Array.isArray(value)
    ? value
    : []
}


function sanitiseFileName(
  value,
) {
  return (
    safeText(value)
      .replace(
        /[<>:"/\\|?*]+/g,
        '',
      )
      .replace(
        /\s+/g,
        '_',
      )
      .replace(
        /_+/g,
        '_',
      )
      .replace(
        /^_+|_+$/g,
        '',
      )
    || 'GradNavi'
  )
}


function todayStamp() {
  return new Date()
    .toISOString()
    .slice(
      0,
      10,
    )
}


function triggerDownload(
  blob,
  fileName,
) {
  const url =
    URL.createObjectURL(
      blob,
    )

  const anchor =
    document.createElement(
      'a',
    )

  anchor.href =
    url

  anchor.download =
    fileName

  document.body
    .appendChild(
      anchor,
    )

  anchor.click()
  anchor.remove()

  window.setTimeout(
    () => {
      URL.revokeObjectURL(
        url,
      )
    },
    1000,
  )
}


function buildContactLine(
  contact,
) {
  return [
    contact?.email,
    contact?.phone,
    contact?.location,
    contact?.linkedin,
    contact?.portfolio,
  ]
    .map(
      (item) =>
        safeText(
          item,
        ),
    )
    .filter(Boolean)
    .join(' | ')
}


function formatMonthYear(
  value,
) {
  const clean =
    safeText(value)

  if (!clean) {
    return ''
  }

  const match =
    clean.match(
      /^(\d{4})-(\d{2})(?:-\d{2})?$/,
    )

  if (!match) {
    return clean
  }

  const year =
    Number(
      match[1],
    )

  const month =
    Number(
      match[2],
    )

  if (
    !Number.isInteger(
      year,
    )
    || month < 1
    || month > 12
  ) {
    return clean
  }

  const date =
    new Date(
      Date.UTC(
        year,
        month - 1,
        1,
      ),
    )

  const monthLabel =
    date.toLocaleDateString(
      'en-AU',
      {
        month: 'short',
        timeZone: 'UTC',
      },
    )

  return (
    `${monthLabel} ${year}`
  )
}


function formatDateRange(
  startDate,
  endDate,
  isCurrent = false,
) {
  const start =
    formatMonthYear(
      startDate,
    )

  const end =
    isCurrent
      ? 'Present'
      : formatMonthYear(
          endDate,
        )
        || 'Present'

  if (!start) {
    return end
  }

  return (
    `${start} - ${end}`
  )
}


function resolveResumeTitle(
  profile,
  targetCareerName,
) {
  const explicit =
    safeText(
      targetCareerName,
    )

  if (explicit) {
    return explicit
  }

  const goals =
    safeProfileList(
      profile,
      'career_goals',
    )

  const primary =
    goals.find(
      (goal) =>
        goal?.is_primary,
    )
    || goals[0]

  return safeText(
    primary?.target_role,
  )
}


function parseSkillRow(
  value,
) {
  let clean =
    safeText(
      value,
    )

  if (!clean) {
    return null
  }

  clean =
    clean.replace(
      /^CATEGORY\s*:\s*/i,
      '',
    )

  clean =
    clean.replace(
      /\s*\|\s*/g,
      ' | ',
    )

  const colonIndex =
    clean.indexOf(':')

  if (colonIndex > 0) {
    const label =
      safeText(
        clean.slice(
          0,
          colonIndex,
        ),
      )

    const skills =
      safeText(
        clean.slice(
          colonIndex + 1,
        ),
      )

    if (
      label
      && skills
    ) {
      return {
        label,
        skills,
      }
    }
  }

  const pipeParts =
    clean
      .split('|')
      .map(
        (item) =>
          safeText(
            item,
          ),
      )
      .filter(Boolean)

  if (
    pipeParts.length
    > 1
  ) {
    return {
      label:
        pipeParts[0],
      skills:
        pipeParts
          .slice(1)
          .join(' | '),
    }
  }

  return {
    label:
      'Core Skills',
    skills:
      clean,
  }
}


function buildSkillRows(
  draft,
) {
  return safeList(
    draft?.skills,
  )
    .map(
      parseSkillRow,
    )
    .filter(Boolean)
    .slice(
      0,
      7,
    )
}


const INTERNAL_COVER_LETTER_PATTERN =
  /^(?:opening|body_paragraphs|closing|matched_profile_facts|missing_information|limitations|is_draft|requires_user_review)\s*(?::|=|\[|\{|$)/i


function isInternalCoverLetterArtifact(
  value,
) {
  const clean =
    safeText(
      value,
    )

  if (!clean) {
    return false
  }

  return (
    INTERNAL_COVER_LETTER_PATTERN
      .test(
        clean,
      )
  )
}


function cleanCoverLetterText(
  value,
) {
  const clean =
    safeText(
      value,
    )

  if (
    isInternalCoverLetterArtifact(
      clean,
    )
  ) {
    return ''
  }

  return clean
}


function cleanCoverLetterParagraphs(
  draft,
) {
  return [
    cleanCoverLetterText(
      draft?.opening,
    ),

    ...safeList(
      draft?.body_paragraphs,
    )
      .filter(
        (item) =>
          !isInternalCoverLetterArtifact(
            item,
          ),
      ),

    cleanCoverLetterText(
      draft?.closing,
    ),
  ].filter(Boolean)
}


function splitEvidenceBullets(
  value,
) {
  const clean =
    safeText(
      value,
    )

  if (!clean) {
    return []
  }

  const sentences =
    clean
      .split(
        /(?<=[.!?])\s+/,
      )
      .map(
        (item) =>
          safeText(
            item,
          ),
      )
      .filter(Boolean)

  if (
    sentences.length
    <= 1
  ) {
    return [
      clean,
    ]
  }

  return sentences.slice(
    0,
    3,
  )
}


function stripLeadingMetadata(
  value,
  metadata,
) {
  const clean =
    safeText(
      value,
    )

  const prefix =
    safeText(
      metadata,
    )

  if (
    !clean
    || !prefix
  ) {
    return clean
  }

  if (
    clean
      .toLowerCase()
      .startsWith(
        prefix.toLowerCase(),
      )
  ) {
    return safeText(
      clean.slice(
        prefix.length,
      ),
    )
  }

  return clean
}


function cleanResumeEvidence(
  value,
  record,
  type,
) {
  let clean =
    safeText(
      value,
    )

  if (!clean) {
    return ''
  }

  if (
    type === 'experience'
  ) {
    /*
     * Generated experience text sometimes repeats:
     *
     * Job Title at Company - DATE to DATE: evidence
     *
     * The resume already renders the title, company,
     * and formatted date range separately.
     */

    clean =
      stripLeadingMetadata(
        clean,
        record?.job_title,
      )

    clean =
      clean.replace(
        /^\s*[-|,:]\s*/,
        '',
      )

    clean =
      clean.replace(
        /^\s*at\s+/i,
        '',
      )

    clean =
      stripLeadingMetadata(
        clean,
        record?.company,
      )
  }

  if (
    type === 'project'
  ) {
    /*
     * Project name and dates are already rendered
     * in the structured project heading.
     */

    clean =
      stripLeadingMetadata(
        clean,
        record?.name,
      )
  }

  /*
   * Remove separators left after known metadata.
   */
  clean =
    clean.replace(
      /^\s*[-|,:]\s*/,
      '',
    )

  /*
   * Remove ISO-style leading date metadata:
   *
   * 2025-07-01 to present:
   * 2024-02-01 to 2024-11-30:
   * 2025-07-01-Present
   * start 2026-07-01:
   */
  clean =
    clean.replace(
      /^\s*(?:\(\s*)?(?:start\s*:?\s*)?\d{4}-\d{2}(?:-\d{2})?(?:\s*(?:to|-)\s*(?:present|\d{4}-\d{2}(?:-\d{2})?))?(?:\s*\))?\s*(?::|-|\||,)?\s*/i,
      '',
    )

  /*
   * Retain compatibility with older generated
   * parenthesised metadata forms.
   */
  clean =
    clean.replace(
      /^\s*\((?=[^)]*(?:\d{4}|start|end|present))[^)]*\)\s*/i,
      '',
    )

  clean =
    clean.replace(
      /^\s*[-|,:]\s*/,
      '',
    )

  /*
   * A generated item containing only date metadata
   * does not provide useful resume evidence.
   */
  if (
    /^(?:start|end|from|to|present|\d{4}(?:-\d{2}(?:-\d{2})?)?|[-\s,;:|()])+$/i
      .test(
        clean,
      )
  ) {
    return ''
  }

  return safeText(
    clean,
  )
}


function selectResumeEvidence(
  generated,
  fallback,
  record,
  type,
) {
  const cleanedGenerated =
    cleanResumeEvidence(
      generated,
      record,
      type,
    )

  if (cleanedGenerated) {
    return cleanedGenerated
  }

  return safeText(
    fallback,
  )
}


function resumeFileBase(
  contact,
) {
  return (
    `${sanitiseFileName(
      contact?.fullName,
    )}_Resume_${todayStamp()}`
  )
}


function coverLetterFileBase(
  contact,
  jobContext,
) {
  return (
    `${sanitiseFileName(
      contact?.fullName,
    )}_Cover_Letter_${sanitiseFileName(
      jobContext?.company
      || 'Application',
    )}_${todayStamp()}`
  )
}


function wordParagraph(
  text,
  options = {},
) {
  const {
    bold = false,
    italic = false,
    size = WORD_BODY_SIZE,
    spacingBefore = 0,
    spacingAfter = 100,
    alignment =
      AlignmentType.LEFT,
    keepNext = false,
  } = options

  return new Paragraph({
    alignment,
    keepNext,

    spacing: {
      before:
        spacingBefore,
      after:
        spacingAfter,
    },

    children: [
      new TextRun({
        text:
          safeText(
            text,
          ),
        bold,
        italic,
        font:
          WORD_FONT,
        size,
      }),
    ],
  })
}


function wordRichParagraph(
  runs,
  options = {},
) {
  const {
    spacingBefore = 0,
    spacingAfter = 100,
    alignment =
      AlignmentType.LEFT,
    keepNext = false,
  } = options

  return new Paragraph({
    alignment,
    keepNext,

    spacing: {
      before:
        spacingBefore,
      after:
        spacingAfter,
    },

    children:
      runs
        .filter(
          (run) =>
            safeText(
              run?.text,
            ),
        )
        .map(
          (run) =>
            new TextRun({
              text:
                normaliseExportText(
                  run.text,
                ),
              bold:
                Boolean(
                  run.bold,
                ),
              italic:
                Boolean(
                  run.italic,
                ),
              font:
                WORD_FONT,
              size:
                run.size
                || WORD_BODY_SIZE,
            }),
        ),
  })
}


function wordSectionHeading(
  title,
) {
  return new Paragraph({
    keepNext: true,

    spacing: {
      before: 260,
      after: 130,
    },

    border: {
      bottom: {
        style:
          BorderStyle.SINGLE,
        color:
          'B8C1CB',
        size: 5,
        space: 5,
      },
    },

    children: [
      new TextRun({
        text:
          safeText(
            title,
          ).toUpperCase(),
        bold: true,
        font:
          WORD_FONT,
        size:
          WORD_HEADING_SIZE,
      }),
    ],
  })
}


function wordBullet(
  text,
) {
  return new Paragraph({
    bullet: {
      level: 0,
    },

    spacing: {
      after: 70,
    },

    children: [
      new TextRun({
        text:
          safeText(
            text,
          ),
        font:
          WORD_FONT,
        size:
          WORD_BODY_SIZE,
      }),
    ],
  })
}


function addWordEvidenceBullets(
  children,
  value,
) {
  const bullets =
    splitEvidenceBullets(
      value,
    )

  for (
    const bullet
    of bullets
  ) {
    children.push(
      wordBullet(
        bullet,
      ),
    )
  }
}


function buildResumeWordDocument(
  contact,
  draft,
  profile,
  targetCareerName,
) {
  const children = []

  const fullName =
    safeText(
      contact?.fullName,
    )

  const resumeTitle =
    resolveResumeTitle(
      profile,
      targetCareerName,
    )

  const contactLine =
    buildContactLine(
      contact,
    )

  if (fullName) {
    children.push(
      wordParagraph(
        fullName,
        {
          bold: true,
          size: 36,
          spacingAfter: 45,
          alignment:
            AlignmentType.CENTER,
        },
      ),
    )
  }

  if (resumeTitle) {
    children.push(
      wordParagraph(
        resumeTitle,
        {
          bold: true,
          size: 22,
          spacingAfter: 60,
          alignment:
            AlignmentType.CENTER,
        },
      ),
    )
  }

  if (contactLine) {
    children.push(
      wordParagraph(
        contactLine,
        {
          size: 18,
          spacingAfter: 150,
          alignment:
            AlignmentType.CENTER,
        },
      ),
    )
  }

  const summary =
    safeText(
      draft?.professional_summary,
    )

  if (summary) {
    children.push(
      wordSectionHeading(
        'Professional Summary',
      ),

      wordParagraph(
        summary,
        {
          spacingAfter: 90,
        },
      ),
    )
  }

  const skillRows =
    buildSkillRows(
      draft,
    )

  if (
    skillRows.length
  ) {
    children.push(
      wordSectionHeading(
        'Skills',
      ),
    )

    for (
      const row
      of skillRows
    ) {
      children.push(
        wordRichParagraph(
          [
            {
              text:
                `${row.label}: `,
              bold: true,
            },
            {
              text:
                row.skills,
            },
          ],
          {
            spacingAfter: 65,
          },
        ),
      )
    }
  }

  const experience =
    safeProfileList(
      profile,
      'experience',
    )

  if (
    experience.length
  ) {
    children.push(
      wordSectionHeading(
        'Professional Experience',
      ),
    )

    experience.forEach(
      (
        record,
        index,
      ) => {
        children.push(
          wordParagraph(
            record.job_title,
            {
              bold: true,
              size: 22,
              spacingAfter: 20,
              keepNext: true,
            },
          ),
        )

        children.push(
          wordRichParagraph(
            [
              {
                text:
                  record.company,
                bold: true,
              },
              {
                text:
                  record.company
                    ? ' | '
                    : '',
              },
              {
                text:
                  formatDateRange(
                    record.start_date,
                    record.end_date,
                    record.is_current,
                  ),
                italic: true,
              },
            ],
            {
              spacingAfter: 65,
              keepNext: true,
            },
          ),
        )

        const generated =
          safeList(
            draft?.experience,
          )[index]

        const evidence =
          selectResumeEvidence(
            generated,
            record.description,
            record,
            'experience',
          )

        addWordEvidenceBullets(
          children,
          evidence,
        )
      },
    )
  }

  const education =
    safeProfileList(
      profile,
      'education',
    )

  if (
    education.length
  ) {
    children.push(
      wordSectionHeading(
        'Education',
      ),
    )

    education.forEach(
      (
        record,
      ) => {
        children.push(
          wordParagraph(
            record.qualification,
            {
              bold: true,
              size: 22,
              spacingAfter: 20,
              keepNext: true,
            },
          ),
        )

        children.push(
          wordRichParagraph(
            [
              {
                text:
                  record.institution_name,
                bold: true,
              },
              {
                text:
                  record.institution_name
                    ? ' | '
                    : '',
              },
              {
                text:
                  formatDateRange(
                    record.start_date,
                    record.end_date,
                    false,
                  ),
                italic: true,
              },
            ],
            {
              spacingAfter: 35,
            },
          ),
        )

        if (
          safeText(
            record.field_of_study,
          )
        ) {
          children.push(
            wordParagraph(
              record.field_of_study,
              {
                spacingAfter: 45,
              },
            ),
          )
        }

      },
    )
  }

  const projects =
    safeProfileList(
      profile,
      'projects',
    )

  if (
    projects.length
  ) {
    children.push(
      wordSectionHeading(
        'Projects',
      ),
    )

    projects.forEach(
      (
        record,
        index,
      ) => {
        children.push(
          wordRichParagraph(
            [
              {
                text:
                  record.name,
                bold: true,
                size: 22,
              },
              {
                text:
                  record.name
                    ? ' | '
                    : '',
              },
              {
                text:
                  formatDateRange(
                    record.start_date,
                    record.end_date,
                    false,
                  ),
                italic: true,
              },
            ],
            {
              spacingAfter: 55,
              keepNext: true,
            },
          ),
        )

        const generated =
          safeList(
            draft?.projects,
          )[index]

        const evidence =
          selectResumeEvidence(
            generated,
            record.description,
            record,
            'project',
          )

        addWordEvidenceBullets(
          children,
          evidence,
        )
      },
    )
  }

  return new Document({
    creator: 'GradNavi',

    title:
      `${fullName || 'Student'} Resume`,

    description:
      'ATS-friendly resume created in GradNavi.',

    styles: {
      default: {
        document: {
          run: {
            font:
              WORD_FONT,
            size:
              WORD_BODY_SIZE,
          },
        },
      },
    },

    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 720,
              right: 820,
              bottom: 720,
              left: 820,
            },
          },
        },

        children,
      },
    ],
  })
}


function buildCoverLetterWordDocument(
  contact,
  jobContext,
  draft,
) {
  const children = []

  const fullName =
    safeText(
      contact?.fullName,
    )

  const contactLine =
    buildContactLine(
      contact,
    )

  if (fullName) {
    children.push(
      wordParagraph(
        fullName,
        {
          bold: true,
          size: 32,
          spacingAfter: 40,
        },
      ),
    )
  }

  if (contactLine) {
    children.push(
      wordParagraph(
        contactLine,
        {
          size: 18,
          spacingAfter: 130,
        },
      ),
    )
  }

  children.push(
    wordParagraph(
      new Date()
        .toLocaleDateString(
          'en-AU',
          {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          },
        ),
      {
        spacingAfter: 125,
      },
    ),
  )

  const jobTitle =
    safeText(
      jobContext?.jobTitle,
    )

  const company =
    safeText(
      jobContext?.company,
    )

  const subject =
    [
      jobTitle,
      company
        ? `at ${company}`
        : '',
    ]
      .filter(Boolean)
      .join(' ')

  if (subject) {
    children.push(
      wordParagraph(
        subject,
        {
          bold: true,
          size: 22,
          spacingAfter: 120,
        },
      ),
    )
  }

  children.push(
    wordParagraph(
      'Dear Hiring Team,',
      {
        spacingAfter: 120,
      },
    ),
  )

  const paragraphs =
    cleanCoverLetterParagraphs(
      draft,
    )

  for (
    const paragraph
    of paragraphs
  ) {
    children.push(
      wordParagraph(
        paragraph,
        {
          spacingAfter: 125,
        },
      ),
    )
  }

  children.push(
    wordParagraph(
      'Kind regards,',
      {
        spacingBefore: 60,
        spacingAfter: 45,
      },
    ),
  )

  if (fullName) {
    children.push(
      wordParagraph(
        fullName,
        {
          bold: true,
        },
      ),
    )
  }

  return new Document({
    creator: 'GradNavi',

    title:
      `${fullName || 'Student'} Cover Letter`,

    description:
      'Professional cover letter created in GradNavi.',

    styles: {
      default: {
        document: {
          run: {
            font:
              WORD_FONT,
            size:
              WORD_BODY_SIZE,
          },
        },
      },
    },

    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 800,
              right: 900,
              bottom: 800,
              left: 900,
            },
          },
        },

        children,
      },
    ],
  })
}


function createPdfWriter(
  pdf,
  options = {},
) {
  const pageWidth =
    pdf.internal
      .pageSize
      .getWidth()

  const pageHeight =
    pdf.internal
      .pageSize
      .getHeight()

  const marginTop =
    options.marginTop
    ?? 17

  const marginBottom =
    options.marginBottom
    ?? 17

  const marginLeft =
    options.marginLeft
    ?? 17

  const marginRight =
    options.marginRight
    ?? 17

  const usableWidth =
    pageWidth
    - marginLeft
    - marginRight

  const pageCapacity =
    pageHeight
    - marginTop
    - marginBottom

  let y =
    marginTop


  function lineHeight(
    size,
  ) {
    return (
      size
      * 0.352778
      * 1.18
    )
  }


  function bottomBoundary() {
    return (
      pageHeight
      - marginBottom
    )
  }


  function addPage() {
    pdf.addPage()

    y =
      marginTop
  }


  function ensureSpace(
    height,
  ) {
    if (
      y + height
      <= bottomBoundary()
    ) {
      return
    }

    addPage()
  }


  function text(
    value,
    options = {},
  ) {
    const clean =
      safeText(
        value,
      )

    if (!clean) {
      return
    }

    const {
      bold = false,
      size = PDF_BODY_SIZE,
      gapAfter = 3,
      align = 'left',
      indent = 0,
      width =
        usableWidth
        - indent,
    } = options

    pdf.setFont(
      PDF_FONT,
      bold
        ? 'bold'
        : 'normal',
    )

    pdf.setFontSize(
      size,
    )

    const lines =
      pdf.splitTextToSize(
        clean,
        width,
      )

    const step =
      lineHeight(
        size,
      )

    const blockHeight =
      lines.length
      * step
      + gapAfter

    if (
      blockHeight
      <= pageCapacity
      && y + blockHeight
      > bottomBoundary()
    ) {
      addPage()
    }

    for (
      const line
      of lines
    ) {
      if (
        y + step
        > bottomBoundary()
      ) {
        addPage()
      }

      if (
        align === 'center'
      ) {
        pdf.text(
          line,
          pageWidth / 2,
          y,
          {
            align: 'center',
          },
        )
      }
      else {
        pdf.text(
          line,
          marginLeft
            + indent,
          y,
        )
      }

      y +=
        step
    }

    y +=
      gapAfter
  }


  function rule(
    gapAfter = 5,
  ) {
    ensureSpace(
      gapAfter + 1,
    )

    pdf.setDrawColor(
      182,
      193,
      204,
    )

    pdf.setLineWidth(
      0.25,
    )

    pdf.line(
      marginLeft,
      y,
      pageWidth
        - marginRight,
      y,
    )

    y +=
      gapAfter
  }


  function heading(
    value,
  ) {
    const required =
      lineHeight(
        PDF_HEADING_SIZE,
      )
      + 8

    ensureSpace(
      required,
    )

    y += 3

    text(
      safeText(
        value,
      ).toUpperCase(),
      {
        bold: true,
        size:
          PDF_HEADING_SIZE,
        gapAfter: 1.5,
      },
    )

    pdf.setDrawColor(
      188,
      198,
      208,
    )

    pdf.setLineWidth(
      0.22,
    )

    pdf.line(
      marginLeft,
      y,
      pageWidth
        - marginRight,
      y,
    )

    /*
     * Keep visible breathing room between the
     * divider and the following section content.
     */
    y += 5
  }


  function labelValue(
    label,
    value,
  ) {
    const cleanLabel =
      safeText(
        label,
      )

    const cleanValue =
      safeText(
        value,
      ).replace(
        /\s*\|\s*/g,
        ' | ',
      )

    if (
      !cleanLabel
      || !cleanValue
    ) {
      return
    }

    const size = 9.3
    const step =
      lineHeight(
        size,
      )

    const atsLine =
      `${cleanLabel}: ${cleanValue}`

    pdf.setFont(
      PDF_FONT,
      'normal',
    )

    pdf.setFontSize(
      size,
    )

    const lines =
      pdf.splitTextToSize(
        atsLine,
        usableWidth,
      )

    const blockHeight =
      lines.length
      * step
      + 2

    ensureSpace(
      blockHeight,
    )

    for (
      let index = 0;
      index < lines.length;
      index += 1
    ) {
      pdf.text(
        lines[index],
        marginLeft,
        y
          + (
            index
            * step
          ),
      )
    }

    y +=
      lines.length
      * step
      + 2
  }


  function bullet(
    value,
  ) {
    const clean =
      safeText(
        value,
      )

    if (!clean) {
      return
    }

    const size =
      PDF_BODY_SIZE

    const step =
      lineHeight(
        size,
      )

    const indent = 5

    pdf.setFont(
      PDF_FONT,
      'normal',
    )

    pdf.setFontSize(
      size,
    )

    const lines =
      pdf.splitTextToSize(
        clean,
        usableWidth
        - indent,
      )

    const blockHeight =
      lines.length
      * step
      + 2

    ensureSpace(
      blockHeight,
    )

    for (
      let index = 0;
      index < lines.length;
      index += 1
    ) {
      if (
        y + step
        > bottomBoundary()
      ) {
        addPage()
      }

      if (
        index === 0
      ) {
        pdf.text(
          '\u2022',
          marginLeft,
          y,
        )
      }

      pdf.text(
        lines[index],
        marginLeft
          + indent,
        y,
      )

      y +=
        step
    }

    y += 2
  }


  return {
    text,
    rule,
    heading,
    labelValue,
    bullet,
  }
}


function addPdfEvidenceBullets(
  writer,
  value,
) {
  const bullets =
    splitEvidenceBullets(
      value,
    )

  for (
    const bullet
    of bullets
  ) {
    writer.bullet(
      bullet,
    )
  }
}


function buildResumePdf(
  contact,
  draft,
  profile,
  targetCareerName,
) {
  const pdf =
    new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

  const fullName =
    safeText(
      contact?.fullName,
    )

  const resumeTitle =
    resolveResumeTitle(
      profile,
      targetCareerName,
    )

  pdf.setProperties({
    title:
      `${fullName || 'Student'} Resume`,
    subject:
      'ATS-friendly resume created in GradNavi',
    creator:
      'GradNavi',
  })

  const writer =
    createPdfWriter(
      pdf,
      {
        marginTop: 15,
        marginBottom: 16,
        marginLeft: 17,
        marginRight: 17,
      },
    )

  if (fullName) {
    writer.text(
      fullName,
      {
        bold: true,
        size: 18,
        align: 'center',
        gapAfter: 1.8,
      },
    )
  }

  if (resumeTitle) {
    writer.text(
      resumeTitle,
      {
        bold: true,
        size: 10.8,
        align: 'center',
        gapAfter: 2,
      },
    )
  }

  const contactLine =
    buildContactLine(
      contact,
    )

  if (contactLine) {
    writer.text(
      contactLine,
      {
        size: 8.7,
        align: 'center',
        gapAfter: 3,
      },
    )
  }

  writer.rule(5)

  const summary =
    safeText(
      draft?.professional_summary,
    )

  if (summary) {
    writer.heading(
      'Professional Summary',
    )

    writer.text(
      summary,
      {
        size: 9.7,
        gapAfter: 2,
      },
    )
  }

  const skillRows =
    buildSkillRows(
      draft,
    )

  if (
    skillRows.length
  ) {
    writer.heading(
      'Skills',
    )

    for (
      const row
      of skillRows
    ) {
      writer.labelValue(
        row.label,
        row.skills,
      )
    }
  }

  const experience =
    safeProfileList(
      profile,
      'experience',
    )

  if (
    experience.length
  ) {
    writer.heading(
      'Professional Experience',
    )

    experience.forEach(
      (
        record,
        index,
      ) => {
        writer.text(
          record.job_title,
          {
            bold: true,
            size: 10.2,
            gapAfter: 0.8,
          },
        )

        writer.text(
          [
            safeText(
              record.company,
            ),
            formatDateRange(
              record.start_date,
              record.end_date,
              record.is_current,
            ),
          ]
            .filter(Boolean)
            .join(' | '),
          {
            size: 9.2,
            gapAfter: 2,
          },
        )

        const generated =
          safeList(
            draft?.experience,
          )[index]

        addPdfEvidenceBullets(
          writer,
          selectResumeEvidence(
            generated,
            record.description,
            record,
            'experience',
          ),
        )
      },
    )
  }

  const education =
    safeProfileList(
      profile,
      'education',
    )

  if (
    education.length
  ) {
    writer.heading(
      'Education',
    )

    education.forEach(
      (
        record,
      ) => {
        writer.text(
          record.qualification,
          {
            bold: true,
            size: 10.2,
            gapAfter: 0.8,
          },
        )

        writer.text(
          [
            safeText(
              record.institution_name,
            ),
            formatDateRange(
              record.start_date,
              record.end_date,
              false,
            ),
          ]
            .filter(Boolean)
            .join(' | '),
          {
            size: 9.2,
            gapAfter: 1,
          },
        )

        if (
          safeText(
            record.field_of_study,
          )
        ) {
          writer.text(
            record.field_of_study,
            {
              size: 9.2,
              gapAfter: 1.5,
            },
          )
        }

      },
    )
  }

  const projects =
    safeProfileList(
      profile,
      'projects',
    )

  if (
    projects.length
  ) {
    writer.heading(
      'Projects',
    )

    projects.forEach(
      (
        record,
        index,
      ) => {
        writer.text(
          record.name,
          {
            bold: true,
            size: 10.2,
            gapAfter: 0.8,
          },
        )

        writer.text(
          formatDateRange(
            record.start_date,
            record.end_date,
            false,
          ),
          {
            size: 9.2,
            gapAfter: 1.5,
          },
        )

        const generated =
          safeList(
            draft?.projects,
          )[index]

        addPdfEvidenceBullets(
          writer,
          selectResumeEvidence(
            generated,
            record.description,
            record,
            'project',
          ),
        )
      },
    )
  }

  return pdf
}


function buildCoverLetterPdf(
  contact,
  jobContext,
  draft,
) {
  const pdf =
    new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

  const fullName =
    safeText(
      contact?.fullName,
    )

  pdf.setProperties({
    title:
      `${fullName || 'Student'} Cover Letter`,
    subject:
      'Professional cover letter created in GradNavi',
    creator:
      'GradNavi',
  })

  const writer =
    createPdfWriter(
      pdf,
      {
        marginTop: 17,
        marginBottom: 17,
        marginLeft: 18,
        marginRight: 18,
      },
    )

  if (fullName) {
    writer.text(
      fullName,
      {
        bold: true,
        size: 16,
        gapAfter: 1.5,
      },
    )
  }

  const contactLine =
    buildContactLine(
      contact,
    )

  if (contactLine) {
    writer.text(
      contactLine,
      {
        size: 8.8,
        gapAfter: 3,
      },
    )
  }

  writer.rule(5)

  writer.text(
    new Date()
      .toLocaleDateString(
        'en-AU',
        {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        },
      ),
    {
      size: 9.7,
      gapAfter: 5,
    },
  )

  const jobTitle =
    safeText(
      jobContext?.jobTitle,
    )

  const company =
    safeText(
      jobContext?.company,
    )

  const subject =
    [
      jobTitle,
      company
        ? `at ${company}`
        : '',
    ]
      .filter(Boolean)
      .join(' ')

  if (subject) {
    writer.text(
      subject,
      {
        bold: true,
        size: 10.2,
        gapAfter: 5,
      },
    )
  }

  writer.text(
    'Dear Hiring Team,',
    {
      size: 9.8,
      gapAfter: 5,
    },
  )

  const paragraphs =
    cleanCoverLetterParagraphs(
      draft,
    )

  for (
    const paragraph
    of paragraphs
  ) {
    writer.text(
      paragraph,
      {
        size: 9.8,
        gapAfter: 5,
      },
    )
  }

  writer.text(
    'Kind regards,',
    {
      size: 9.8,
      gapAfter: 1.8,
    },
  )

  if (fullName) {
    writer.text(
      fullName,
      {
        bold: true,
        size: 9.8,
        gapAfter: 0,
      },
    )
  }

  return pdf
}


async function downloadResumeDocx(
  contact,
  draft,
  profile = null,
  targetCareerName = '',
) {
  await ensureDocxLibrary()

  const wordDocument =
    buildResumeWordDocument(
      contact,
      draft,
      profile,
      targetCareerName,
    )

  const blob =
    await Packer.toBlob(
      wordDocument,
    )

  triggerDownload(
    blob,
    `${resumeFileBase(
      contact,
    )}.docx`,
  )
}


async function downloadResumePdf(
  contact,
  draft,
  profile = null,
  targetCareerName = '',
) {
  await ensurePdfLibrary()

  const pdf =
    buildResumePdf(
      contact,
      draft,
      profile,
      targetCareerName,
    )

  pdf.save(
    `${resumeFileBase(
      contact,
    )}.pdf`,
  )
}


async function downloadCoverLetterDocx(
  contact,
  jobContext,
  draft,
) {
  await ensureDocxLibrary()

  const wordDocument =
    buildCoverLetterWordDocument(
      contact,
      jobContext,
      draft,
    )

  const blob =
    await Packer.toBlob(
      wordDocument,
    )

  triggerDownload(
    blob,
    `${
      coverLetterFileBase(
        contact,
        jobContext,
      )
    }.docx`,
  )
}


async function downloadCoverLetterPdf(
  contact,
  jobContext,
  draft,
) {
  await ensurePdfLibrary()

  const pdf =
    buildCoverLetterPdf(
      contact,
      jobContext,
      draft,
    )

  pdf.save(
    `${
      coverLetterFileBase(
        contact,
        jobContext,
      )
    }.pdf`,
  )
}


export {
  downloadResumeDocx,
  downloadResumePdf,
  downloadCoverLetterDocx,
  downloadCoverLetterPdf,
}
