import type { BusinessDetails, BusinessMembership } from "@/schemas/business"
import type { UserProfile } from "@/schemas/user"

export type WorkspaceStatus = "idle" | "loading" | "ready" | "error"

export type WorkspaceState = {
  status: WorkspaceStatus
  error: string | null
  user: UserProfile | null
  memberships: BusinessMembership[]
  activeBusinessId: number | null
  activeBusiness: BusinessDetails | null
}

export type WorkspaceActions = {
  setActiveBusinessId: (businessId: number) => Promise<void>
  /** After POST /business: optimistic workspace + active tenant (avoids refresh race). */
  registerCreatedBusiness: (business: BusinessDetails) => void
  /** After PATCH /business: sync top bar + membership list labels. */
  applyBusinessDetails: (business: BusinessDetails) => void
  refresh: () => Promise<void>
}

export type WorkspaceContextValue = WorkspaceState & WorkspaceActions
