import { UPLOAD_DEFAULT_CONTENT_TYPE } from "./upload-policy"
import type { UploadFileDescriptor } from "@/schemas/fileUpload"


/*
Init session needs metadata only; one function keeps 
descriptor shape consistent for multi-file uploads.
*/
export function toUploadFileDescriptor(file: File): UploadFileDescriptor {
  return {
    original_filename: file.name,
    content_type: file.type || UPLOAD_DEFAULT_CONTENT_TYPE,
    size_bytes: file.size,
  }
}

export function toUploadFileDescriptors(files: File[]): UploadFileDescriptor[] {
  return files.map(toUploadFileDescriptor)
}