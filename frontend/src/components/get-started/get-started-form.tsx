import * as React from "react"
import { ArrowRight, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { uploadBusinessDocuments } from "@/api/upload"
import { extract } from "@/api/extract"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { requireActiveBusinessId } from "@/features/upload/logic"
import { useWorkspace } from "@/features/workspace/logic/workspace-context"
import { createEmptyBusinessContext } from "@/types/business-context"

import { useGetStarted } from "./get-started-context"
import { mergeBusinessContext } from "./merge-business-context"
import { StepUpload } from "./step-upload"

function GetStartedForm() {
  const { setPhase, setData, setUploadedDocuments } = useGetStarted()
  const { activeBusinessId, status } = useWorkspace()
  const [files, setFiles] = React.useState<File[]>([])
  const [uploading, setUploading] = React.useState(false)

  const workspaceLoading = status === "idle" || status === "loading"

  async function handleContinue() {
    if (files.length === 0) {
      toast.warning("Please add at least one PDF")
      return
    }

    setUploading(true)

    try {
      const businessId = requireActiveBusinessId(activeBusinessId)

      const uploadResult = await uploadBusinessDocuments(businessId, files)
      setUploadedDocuments(uploadResult.documents)

      toast.success(
        uploadResult.documents.length === 1
          ? "File uploaded successfully"
          : `${uploadResult.documents.length} files uploaded successfully`
      )
      setPhase("extracting")

      let mergedContext = createEmptyBusinessContext()
      for (const doc of uploadResult.documents) {
        if (!doc.file_url) continue
        const extractRes = await extract(doc.file_url)
        if (extractRes?.business_context) {
          mergedContext = mergeBusinessContext(
            mergedContext,
            extractRes.business_context
          )
        }
      }

      setData(mergedContext)
      toast.success("Information extracted successfully")
      setPhase("form")
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to process file. Please try again."
      toast.error(message)
      setPhase("upload")
    } finally {
      setUploading(false)
    }
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Upload your files</CardTitle>
        <CardDescription>
          Add one or more business PDFs and we&apos;ll extract the details for
          you.
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-1 pb-2">
        <StepUpload files={files} onFilesChange={setFiles} />
      </CardContent>

      <div className="flex items-center justify-end border-t px-4 py-3">
        <Button
          onClick={() => void handleContinue()}
          disabled={
            files.length === 0 ||
            uploading ||
            workspaceLoading ||
            activeBusinessId == null
          }
        >
          {uploading ? (
            <>
              <Loader2 data-icon="inline-start" className="animate-spin" />
              Uploading
            </>
          ) : (
            <>
              Continue
              <ArrowRight data-icon="inline-end" />
            </>
          )}
        </Button>
      </div>
    </Card>
  )
}

export { GetStartedForm }