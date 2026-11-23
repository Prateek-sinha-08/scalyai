import { apiClient } from "@/api/client"
import { apiRequest } from "@/api/request"
import {
  matchSlotsToFiles,
  toUploadFileDescriptors,
  validatePdfFile,
} from "@/features/upload/logic"
import type {
  BusinessDocument,
  CompleteUploadSessionResponse,
  CreateUploadSessionResponse,
  TransferUploadSlotResponse,
} from "@/schemas/fileUpload"

const UPLOAD_BASE = "/api/v1/business/documents/upload"

export type UploadBusinessDocumentsResult = CompleteUploadSessionResponse

export async function createUploadSession(
  businessId: number,
  files: File[]
): Promise<CreateUploadSessionResponse> {
  if (files.length === 0) {
    throw new Error("At least one file is required")
  }

  for (const file of files) {
    const check = validatePdfFile(file)
    if (!check.ok) throw new Error(check.message)
  }

  return apiRequest(
    () =>
      apiClient.post<CreateUploadSessionResponse>(
        `${UPLOAD_BASE}/sessions`,
        {
          business_id: businessId,
          files: toUploadFileDescriptors(files),
        }
      ),
    "Failed to start upload session"
  )
}

export async function transferUploadSlot(
  slotId: string,
  file: File
): Promise<TransferUploadSlotResponse> {
  const check = validatePdfFile(file)
  if (!check.ok) throw new Error(check.message)

  const formData = new FormData()
  formData.append("file", file)

  return apiRequest(
    () =>
      apiClient.post<TransferUploadSlotResponse>(
        `${UPLOAD_BASE}/slots/${slotId}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      ),
    "Failed to upload file"
  )
}

export async function completeUploadSession(
  uploadId: string
): Promise<CompleteUploadSessionResponse> {
  return apiRequest(
    () =>
      apiClient.post<CompleteUploadSessionResponse>(
        `${UPLOAD_BASE}/sessions/${uploadId}/complete`
      ),
    "Failed to finalize upload"
  )
}

/**
 * Full client-side upload protocol: init → transfer each slot → complete.
 */
export async function uploadBusinessDocuments(
  businessId: number,
  files: File[]
): Promise<UploadBusinessDocumentsResult> {
  const session = await createUploadSession(businessId, files)
  const pairs = matchSlotsToFiles(session.slots, files)

  for (const { slot, file } of pairs) {
    await transferUploadSlot(slot.slot_id, file)
  }

  return completeUploadSession(session.upload_id)
}

/** Convenience for single-file flows (get-started). */
export async function uploadBusinessDocument(
  businessId: number,
  file: File
): Promise<BusinessDocument> {
  const result = await uploadBusinessDocuments(businessId, [file])
  const doc = result.documents[0]
  if (!doc?.file_url) {
    throw new Error("Upload completed but no document was returned")
  }
  return doc
}