/** Mirrors server `InitUploadFileDTO`. */
export type UploadFileDescriptor = {
  original_filename: string
  content_type: string
  size_bytes: number
}

export type CreateUploadSessionPayload = {
  business_id: number
  files: UploadFileDescriptor[]
}

export type UploadSlotCredentials = {
  slot_id: string
  upload_url: string
  original_filename: string
  content_type: string
  expected_size_bytes: number
}

export type CreateUploadSessionResponse = {
  upload_id: string
  expires_at: string
  slots: UploadSlotCredentials[]
}

export type TransferUploadSlotResponse = {
  slot_id: string
  status: string
  uploaded_at: string
}

export type BusinessDocument = {
  document_id: number
  storage_public_id: string
  file_url: string
  original_filename: string
}

export type CompleteUploadSessionResponse = {
  upload_id: string
  documents: BusinessDocument[]
}