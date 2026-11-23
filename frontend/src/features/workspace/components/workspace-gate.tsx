import type { ReactNode } from "react"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useWorkspace } from "@/features/workspace/logic/workspace-context"

type WorkspaceGateProps = {
  children: ReactNode
}

/**
 * Dashboard-only guard: requires at least one business before main content.
 * Users without a business stay on the dashboard shell and use My business → Create.
 */
export function WorkspaceGate({ children }: WorkspaceGateProps) {
  const { status, error, memberships, refresh } = useWorkspace()

  if (status === "idle" || status === "loading") {
    return (
      <div className="flex flex-1 flex-col gap-4 p-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" />
          Loading workspace…
        </div>
      </div>
    )
  }

  if (status === "error") {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-4">
        <p className="text-sm text-destructive">{error ?? "Something went wrong."}</p>
        <Button type="button" variant="outline" size="sm" onClick={() => void refresh()}>
          Retry
        </Button>
      </div>
    )
  }

  if (memberships.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 p-8 text-center">
        <p className="text-sm font-medium">Create your first business</p>
        <p className="max-w-sm text-sm text-muted-foreground">
          Use <strong>My business</strong> in the top bar, then <strong>Create business</strong>.
          Get Started unlocks after you have an active business.
        </p>
      </div>
    )
  }

  return <>{children}</>
}