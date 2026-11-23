/*
Server returns slots in init order; matching by 
original_filename (with index fallback) scales to 
batch uploads without assuming a single file.
*/
import type { UploadSlotCredentials } from "@/schemas/fileUpload"

export type SlotFilePair = {
  slot: UploadSlotCredentials
  file: File
}

/**
 * Pairs each server slot with the client File that declared the same metadata.
 * Falls back to index order when names collide (same name twice is unlikely in v1).
 */
export function matchSlotsToFiles(
  slots: UploadSlotCredentials[],
  files: File[]
): SlotFilePair[] {
  const byName = new Map<string, File[]>()
  for (const file of files) {
    const list = byName.get(file.name) ?? []
    list.push(file)
    byName.set(file.name, list)
  }

  const pairs: SlotFilePair[] = []

  slots.forEach((slot, index) => {
    const queue = byName.get(slot.original_filename)
    const file =
      queue && queue.length > 0
        ? queue.shift()!
        : files[index]

    if (!file) {
      throw new Error(
        `No local file for upload slot "${slot.original_filename}"`
      )
    }

    pairs.push({ slot, file })
  })

  return pairs
}