let Document
let Packer
let Paragraph
let TextRun
let jsPDF

let docxModulePromise
let jsPdfModulePromise


async function ensureDocxLibrary() {
  if (
    Document
    && Packer
    && Paragraph
    && TextRun
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
const WORD_BODY_SIZE = 22
const WORD_HEADING_SIZE = 23

const PDF_FONT = 'helvetica'
const PDF_BODY_SIZE = 10.5
const PDF_HEADING_SIZE = 11


function safeText(value) {
  return String(value || '').trim()
}


function safeList(value) {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map((item) => safeText(item))
    .filter(Boolean)
}


function sanitiseFileName(value) {
  return (
    safeText(value)
      .replace(/[<>:"/\\|?*]+/g, '')
      .replace(/\s+/g, '_')
      .replace(/_+/g, '_')
      .replace(/^_+|_+$/g, '')
    || 'GradNavi'
  )
}


function todayStamp() {
  return new Date()
    .toISOString()
    .slice(0, 10)
}


function triggerDownload(
  blob,
  fileName,
) {
  const url =
    URL.createObjectURL(blob)

  const anchor =
    document.createElement('a')

  anchor.href = url
  anchor.download = fileName

  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()

  window.setTimeout(
    () => {
      URL.revokeObjectURL(url)
    },
    1000,
  )
}


function buildContactLine(contact) {
  return [
    contact?.email,
    contact?.phone,
    contact?.location,
    contact?.linkedin,
    contact?.portfolio,
  ]
    .map((item) => safeText(item))
    .filter(Boolean)
    .join(' | ')
}


function wordParagraph(
  text,
  options = {},
) {
  const {
    bold = false,
    size = WORD_BODY_SIZE,
    spacingAfter = 100,
  } = options

  return new Paragraph({
    spacing: {
      after: spacingAfter,
    },

    children: [
      new TextRun({
        text: safeText(text),
        bold,
        font: WORD_FONT,
        size,
      }),
    ],
  })
}


function wordHeading(title) {
  return new Paragraph({
    spacing: {
      before: 180,
      after: 90,
    },

    children: [
      new TextRun({
        text: title.toUpperCase(),
        bold: true,
        font: WORD_FONT,
        size: WORD_HEADING_SIZE,
      }),
    ],
  })
}


function wordBullet(text) {
  return new Paragraph({
    bullet: {
      level: 0,
    },

    spacing: {
      after: 70,
    },

    children: [
      new TextRun({
        text: safeText(text),
        font: WORD_FONT,
        size: WORD_BODY_SIZE,
      }),
    ],
  })
}


function appendListSection(
  children,
  title,
  values,
  useBullets = true,
) {
  const items = safeList(values)

  if (!items.length) {
    return
  }

  children.push(
    wordHeading(title),
  )

  for (const item of items) {
    children.push(
      useBullets
        ? wordBullet(item)
        : wordParagraph(item),
    )
  }
}


function resumeFileBase(contact) {
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


function buildResumeWordDocument(
  contact,
  draft,
) {
  const children = []

  const fullName =
    safeText(contact?.fullName)

  const contactLine =
    buildContactLine(contact)

  if (fullName) {
    children.push(
      wordParagraph(
        fullName,
        {
          bold: true,
          size: 30,
          spacingAfter: 60,
        },
      ),
    )
  }

  if (contactLine) {
    children.push(
      wordParagraph(
        contactLine,
        {
          size: 19,
          spacingAfter: 150,
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
      wordHeading(
        'Professional Summary',
      ),

      wordParagraph(summary),
    )
  }

  const skills =
    safeList(draft?.skills)

  if (skills.length) {
    children.push(
      wordHeading('Skills'),

      wordParagraph(
        skills.join(', '),
      ),
    )
  }

  appendListSection(
    children,
    'Experience',
    draft?.experience,
    true,
  )

  appendListSection(
    children,
    'Education',
    draft?.education,
    false,
  )

  appendListSection(
    children,
    'Projects',
    draft?.projects,
    true,
  )

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
            font: WORD_FONT,
            size: WORD_BODY_SIZE,
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
              right: 720,
              bottom: 720,
              left: 720,
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
    safeText(contact?.fullName)

  const contactLine =
    buildContactLine(contact)

  if (fullName) {
    children.push(
      wordParagraph(
        fullName,
        {
          bold: true,
          size: 28,
          spacingAfter: 50,
        },
      ),
    )
  }

  if (contactLine) {
    children.push(
      wordParagraph(
        contactLine,
        {
          size: 19,
          spacingAfter: 130,
        },
      ),
    )
  }

  children.push(
    wordParagraph(
      new Date()
        .toLocaleDateString(
          undefined,
          {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          },
        ),
      {
        spacingAfter: 160,
      },
    ),
  )

  const company =
    safeText(jobContext?.company)

  const jobTitle =
    safeText(jobContext?.jobTitle)

  if (jobTitle || company) {
    children.push(
      wordParagraph(
        `Re: ${
          [
            jobTitle,
            company
              ? `at ${company}`
              : '',
          ]
            .filter(Boolean)
            .join(' ')
        }`,
        {
          bold: true,
          spacingAfter: 160,
        },
      ),
    )
  }

  if (safeText(draft?.opening)) {
    children.push(
      wordParagraph(
        draft.opening,
        {
          spacingAfter: 150,
        },
      ),
    )
  }

  for (
    const paragraph
    of safeList(
      draft?.body_paragraphs,
    )
  ) {
    children.push(
      wordParagraph(
        paragraph,
        {
          spacingAfter: 150,
        },
      ),
    )
  }

  if (safeText(draft?.closing)) {
    children.push(
      wordParagraph(
        draft.closing,
        {
          spacingAfter: 180,
        },
      ),
    )
  }

  if (fullName) {
    children.push(
      wordParagraph(fullName),
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
            font: WORD_FONT,
            size: WORD_BODY_SIZE,
          },
        },
      },
    },

    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 900,
              right: 900,
              bottom: 900,
              left: 900,
            },
          },
        },

        children,
      },
    ],
  })
}


function createPdfWriter(pdf) {
  const pageWidth =
    pdf.internal
      .pageSize
      .getWidth()

  const pageHeight =
    pdf.internal
      .pageSize
      .getHeight()

  const margin = 18

  const usableWidth =
    pageWidth - (margin * 2)

  let y = margin


  function ensureSpace(height) {
    if (
      y + height
      <= pageHeight - margin
    ) {
      return
    }

    pdf.addPage()
    y = margin
  }


  function text(
    value,
    options = {},
  ) {
    const clean =
      safeText(value)

    if (!clean) {
      return
    }

    const {
      bold = false,
      size = PDF_BODY_SIZE,
      gapAfter = 4,
    } = options

    pdf.setFont(
      PDF_FONT,
      bold
        ? 'bold'
        : 'normal',
    )

    pdf.setFontSize(size)

    const lines =
      pdf.splitTextToSize(
        clean,
        usableWidth,
      )

    const lineHeight =
      size * 0.42

    const height =
      Math.max(
        lineHeight,
        lines.length * lineHeight,
      )

    ensureSpace(
      height + gapAfter,
    )

    pdf.text(
      lines,
      margin,
      y,
    )

    y +=
      height + gapAfter
  }


  function heading(value) {
    y += 2

    text(
      safeText(value)
        .toUpperCase(),
      {
        bold: true,
        size: PDF_HEADING_SIZE,
        gapAfter: 3,
      },
    )
  }


  function bullet(value) {
    const clean =
      safeText(value)

    if (!clean) {
      return
    }

    pdf.setFont(
      PDF_FONT,
      'normal',
    )

    pdf.setFontSize(
      PDF_BODY_SIZE,
    )

    const indent = 5

    const lines =
      pdf.splitTextToSize(
        clean,
        usableWidth - indent,
      )

    const lineHeight =
      PDF_BODY_SIZE * 0.42

    const height =
      lines.length * lineHeight

    ensureSpace(
      height + 3,
    )

    pdf.text(
      '\u2022',
      margin,
      y,
    )

    pdf.text(
      lines,
      margin + indent,
      y,
    )

    y +=
      height + 3
  }


  return {
    text,
    heading,
    bullet,
  }
}


function buildResumePdf(
  contact,
  draft,
) {
  const pdf =
    new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

  pdf.setProperties({
    title:
      `${
        safeText(
          contact?.fullName,
        )
        || 'Student'
      } Resume`,

    subject:
      'ATS-friendly resume created in GradNavi',

    creator:
      'GradNavi',
  })

  const writer =
    createPdfWriter(pdf)

  const fullName =
    safeText(contact?.fullName)

  if (fullName) {
    writer.text(
      fullName,
      {
        bold: true,
        size: 16,
        gapAfter: 3,
      },
    )
  }

  const contactLine =
    buildContactLine(contact)

  if (contactLine) {
    writer.text(
      contactLine,
      {
        size: 9,
        gapAfter: 6,
      },
    )
  }

  const summary =
    safeText(
      draft?.professional_summary,
    )

  if (summary) {
    writer.heading(
      'Professional Summary',
    )

    writer.text(summary)
  }

  const skills =
    safeList(draft?.skills)

  if (skills.length) {
    writer.heading('Skills')

    writer.text(
      skills.join(', '),
    )
  }

  const experience =
    safeList(draft?.experience)

  if (experience.length) {
    writer.heading('Experience')

    experience.forEach(
      (item) =>
        writer.bullet(item),
    )
  }

  const education =
    safeList(draft?.education)

  if (education.length) {
    writer.heading('Education')

    education.forEach(
      (item) =>
        writer.text(item),
    )
  }

  const projects =
    safeList(draft?.projects)

  if (projects.length) {
    writer.heading('Projects')

    projects.forEach(
      (item) =>
        writer.bullet(item),
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

  pdf.setProperties({
    title:
      `${
        safeText(
          contact?.fullName,
        )
        || 'Student'
      } Cover Letter`,

    subject:
      'Professional cover letter created in GradNavi',

    creator:
      'GradNavi',
  })

  const writer =
    createPdfWriter(pdf)

  const fullName =
    safeText(contact?.fullName)

  if (fullName) {
    writer.text(
      fullName,
      {
        bold: true,
        size: 15,
        gapAfter: 2,
      },
    )
  }

  const contactLine =
    buildContactLine(contact)

  if (contactLine) {
    writer.text(
      contactLine,
      {
        size: 9,
        gapAfter: 6,
      },
    )
  }

  writer.text(
    new Date()
      .toLocaleDateString(
        undefined,
        {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        },
      ),
    {
      gapAfter: 6,
    },
  )

  const company =
    safeText(jobContext?.company)

  const jobTitle =
    safeText(jobContext?.jobTitle)

  if (jobTitle || company) {
    writer.text(
      `Re: ${
        [
          jobTitle,
          company
            ? `at ${company}`
            : '',
        ]
          .filter(Boolean)
          .join(' ')
      }`,
      {
        bold: true,
        gapAfter: 6,
      },
    )
  }

  writer.text(
    draft?.opening,
    {
      gapAfter: 6,
    },
  )

  for (
    const paragraph
    of safeList(
      draft?.body_paragraphs,
    )
  ) {
    writer.text(
      paragraph,
      {
        gapAfter: 6,
      },
    )
  }

  writer.text(
    draft?.closing,
    {
      gapAfter: 8,
    },
  )

  if (fullName) {
    writer.text(fullName)
  }

  return pdf
}


async function downloadResumeDocx(
  contact,
  draft,
) {
  await ensureDocxLibrary()

  const wordDocument =
    buildResumeWordDocument(
      contact,
      draft,
    )

  const blob =
    await Packer.toBlob(
      wordDocument,
    )

  triggerDownload(
    blob,
    `${resumeFileBase(contact)}.docx`,
  )
}


async function downloadResumePdf(
  contact,
  draft,
) {
  await ensurePdfLibrary()

  const pdf =
    buildResumePdf(
      contact,
      draft,
    )

  pdf.save(
    `${resumeFileBase(contact)}.pdf`,
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
