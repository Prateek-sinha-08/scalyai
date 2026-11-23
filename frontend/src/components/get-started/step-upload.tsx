"use client"

import * as React from "react"
import { FileText, UploadCloud, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  UPLOAD_ACCEPT,
  UPLOAD_MAX_FILES_PER_SESSION,
  UPLOAD_MAX_SIZE_MB,
  validatePdfFile,
} from "@/features/upload/logic"
import { cn } from "@/lib/utils"

type StepUploadProps = {
  files: File[]
  onFilesChange: (files: File[]) => void
  /** Must match server `DocumentPolicy` (PDF). */
  accept?: string
  maxSizeMb?: number
  maxFiles?: number
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function fileKey(file: File) {
  return `${file.name}-${file.size}-${file.lastModified}`
}

function mergeIncomingFiles(
  existing: File[],
  incoming: File[],
  maxFiles: number
): { files: File[]; error: string | null } {
  const map = new Map<string, File>()
  for (const f of existing) map.set(fileKey(f), f)

  for (const f of incoming) {
    const check = validatePdfFile(f)
    if (!check.ok) return { files: existing, error: check.message }
    map.set(fileKey(f), f)
  }

  const merged = Array.from(map.values())
  if (merged.length > maxFiles) {
    return {
      files: existing,
      error: `At most ${maxFiles} PDFs per upload`,
    }
  }

  return { files: merged, error: null }
}

function StepUpload({
  files,
  onFilesChange,
  accept = UPLOAD_ACCEPT,
  maxSizeMb = UPLOAD_MAX_SIZE_MB,
  maxFiles = UPLOAD_MAX_FILES_PER_SESSION,
}: StepUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  function addFiles(incoming: File[]) {
    setError(null)
    if (incoming.length === 0) return
    const { files: next, error: mergeError } = mergeIncomingFiles(
      files,
      incoming,
      maxFiles
    )
    if (mergeError) {
      setError(mergeError)
      return
    }
    onFilesChange(next)
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragOver(false)
    addFiles(Array.from(e.dataTransfer.files ?? []))
  }

  function handleSelect(e: React.ChangeEvent<HTMLInputElement>) {
    addFiles(Array.from(e.target.files ?? []))
    e.target.value = ""
  }

  function removeFile(e: React.MouseEvent, key: string) {
    e.stopPropagation()
    setError(null)
    onFilesChange(files.filter((f) => fileKey(f) !== key))
  }

  const atMax = files.length >= maxFiles

  return (
    <div className="space-y-3">
      <div
        role="button"
        tabIndex={0}
        onClick={() => {
          if (!atMax) inputRef.current?.click()
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault()
            if (!atMax) inputRef.current?.click()
          }
        }}
        onDragOver={(e) => {
          e.preventDefault()
          if (!atMax) setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={cn(
          "group relative flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-input bg-muted/30 px-6 py-10 text-center transition-colors outline-none",
          "hover:border-ring/60 hover:bg-muted/50",
          "focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
          dragOver && "border-ring bg-muted/60",
          files.length > 0 && "border-solid border-input bg-background",
          atMax && "cursor-default opacity-90"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple
          onChange={handleSelect}
          className="sr-only"
          disabled={atMax}
        />

        {files.length > 0 ? (
          <ul className="flex w-full flex-col gap-2">
            {files.map((file) => {
              const key = fileKey(file)
              return (
                <li
                  key={key}
                  className="flex w-full items-center gap-3 text-left"
                >
                  <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <FileText className="size-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatBytes(file.size)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={(e) => removeFile(e, key)}
                    aria-label={`Remove ${file.name}`}
                  >
                    <X />
                  </Button>
                </li>
              )
            })}
            {!atMax ? (
              <p className="pt-1 text-center text-xs text-muted-foreground">
                Drop more PDFs or browse to add ({files.length}/{maxFiles})
              </p>
            ) : null}
          </ul>
        ) : (
          <>
            <div className="flex size-10 items-center justify-center rounded-full bg-background text-muted-foreground ring-1 ring-foreground/10 transition-colors group-hover:text-foreground">
              <UploadCloud className="size-5" />
            </div>
            <div className="space-y-0.5">
              <p className="text-sm font-medium">
                Drop files here, or{" "}
                <span className="text-primary underline-offset-4 group-hover:underline">
                  browse
                </span>
              </p>
              <p className="text-xs text-muted-foreground">
                PDF only · up to {maxSizeMb} MB each · max {maxFiles} files
              </p>
            </div>
          </>
        )}
      </div>

      {error && (
        <p className="text-xs text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

export { StepUpload }