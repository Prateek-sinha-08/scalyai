"use client"
import * as React from "react"
import { flushSync } from "react-dom"
import { useNavigate } from "react-router-dom"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"

import { createBusiness } from "@/api/business"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { APP_ROUTES } from "@/features/layout/logic"
import { useWorkspace } from "@/features/workspace/logic/workspace-context"
import type { CreateBusinessPayload } from "@/schemas/business"

type CreateBusinessSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  /**
   * When true (default), after create: activate new tenant + go to Get Started.
   * When false, only refresh workspace (e.g. create from dashboard without onboarding).
   */
  navigateToGetStarted?: boolean
}

const EMPTY_FORM: CreateBusinessPayload = {
  name: "",
  description: "",
  industry: "",
}

export function CreateBusinessSheet({
  open,
  onOpenChange,
  navigateToGetStarted = true,
}: CreateBusinessSheetProps) {
  const navigate = useNavigate()
  const { registerCreatedBusiness, refresh } = useWorkspace()
  const [form, setForm] = React.useState<CreateBusinessPayload>(EMPTY_FORM)
  const [submitting, setSubmitting] = React.useState(false)

  React.useEffect(() => {
    if (!open) setForm(EMPTY_FORM)
  }, [open])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name.trim()) {
      toast.warning("Business name is required")
      return
    }

    setSubmitting(true)
    try {
      const created = await createBusiness({
        name: form.name.trim(),
        description: form.description.trim(),
        industry: form.industry.trim() || "General",
      })

      // Commit workspace before navigate so RequireActiveBusiness sees the new tenant
      flushSync(() => {
        registerCreatedBusiness(created)
      })
      onOpenChange(false)

      if (navigateToGetStarted) {
        navigate(APP_ROUTES.getStarted, { replace: true })
      } else {
        toast.success("Business created")
      }

      // Sync server state without blocking navigation
      window.setTimeout(() => void refresh(), 0)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to create business"
      toast.error(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right">
        <SheetHeader>
          <SheetTitle>Create business</SheetTitle>
          <SheetDescription>
            Add a workspace for another company. It becomes active immediately.
          </SheetDescription>
        </SheetHeader>

        <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-1 flex-col gap-4 px-4">
          <div className="space-y-2">
            <Label htmlFor="biz-name">Name</Label>
            <Input
              id="biz-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="biz-industry">Industry</Label>
            <Input
              id="biz-industry"
              value={form.industry}
              onChange={(e) => setForm((p) => ({ ...p, industry: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="biz-desc">Description</Label>
            <Textarea
              id="biz-desc"
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              rows={3}
            />
          </div>

          <SheetFooter className="px-0">
            <Button type="submit" disabled={submitting}>
              {submitting ? (
                <>
                  <Loader2 className="animate-spin" data-icon="inline-start" />
                  Creating…
                </>
              ) : (
                "Create business"
              )}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  )
}