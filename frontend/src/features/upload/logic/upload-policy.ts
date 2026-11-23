export const UPLOAD_MAX_SIZE_BYTES = 25 * 1024 * 1024 // 25MB
export const UPLOAD_MAX_SIZE_MB = 25
export const UPLOAD_ACCEPT = ".pdf,application/pdf"
export const UPLOAD_DEFAULT_CONTENT_TYPE = "application/pdf"
export const UPLOAD_MAX_FILES_PER_SESSION = 10 /** Keep in sync with server MAX_FILES_PER_UPLOAD_SESSION (default 10). */


export type UploadValidationResult =
  | { ok: true }
  | { ok: false; message: string }

export function validatePdfFile(file: File): UploadValidationResult {
  const name = file.name.trim()
  if (!name) {
    return { ok: false, message: "Filename is required" }
  }

  const isPdfByExt = name.toLowerCase().endsWith(".pdf")
  const isPdfByType =
    file.type === "" || file.type === UPLOAD_DEFAULT_CONTENT_TYPE

  if (!isPdfByExt && !isPdfByType) {
    return { ok: false, message: "Only PDF documents are allowed" }
  }

  if (file.size < 1) {
    return { ok: false, message: "File is empty" }
  }

  if (file.size > UPLOAD_MAX_SIZE_BYTES) {
    return {
      ok: false,
      message: `File is too large. Max ${UPLOAD_MAX_SIZE_MB} MB.`,
    }
  }

  return { ok: true }
}


export function validatePdfFiles(files: File[]): UploadValidationResult {
  if (files.length === 0) {
    return { ok: false, message: "Select at least one PDF" }
  }
  if (files.length > UPLOAD_MAX_FILES_PER_SESSION) {
    return {
      ok: false,
      message: `At most ${UPLOAD_MAX_FILES_PER_SESSION} files per upload`,
    }
  }
  for (const file of files) {
    const check = validatePdfFile(file)
    if (!check.ok) return check
  }
  return { ok: true }
}