import type { ReactNode } from "react"
import { Navigate, Outlet } from "react-router-dom"
import { Loader2 } from "lucide-react"

import { APP_ROUTES } from "@/features/layout/logic"
import { useWorkspace } from "@/features/workspace/logic/workspace-context"

type RequireActiveBusinessProps = {
  children?: ReactNode
}

/**
 * Blocks Get Started until the user has an active business (create via My business).
 */
export function RequireActiveBusiness({ children }: RequireActiveBusinessProps) {
  const { status, activeBusinessId, memberships } = useWorkspace()

  const hasTenant =
    activeBusinessId != null || memberships.length > 0

  if (hasTenant && status !== "error") {
    return children ? <>{children}</> : <Outlet />
  }

  if (status === "idle" || status === "loading") {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return <Navigate to={APP_ROUTES.dashboard} replace />
}