import { getBusinessById } from "@/api/business"
import { getMe, getMyBusinesses } from "@/api/me"
import {
  readStoredActiveBusinessId,
  resolveActiveBusinessId,
  writeStoredActiveBusinessId,
} from "@/features/workspace/logic/workspace-storage"
import type { WorkspaceState } from "@/features/workspace/logic/workspace-types"

export async function loadActiveBusinessDetails(businessId: number) {
  return getBusinessById(businessId)
}

/** Fetches profile, memberships, and active business details. */
export async function bootstrapWorkspace(): Promise<
  Pick<
    WorkspaceState,
    "user" | "memberships" | "activeBusinessId" | "activeBusiness" | "error"
  > & { status: "ready" | "error" }
> {
  try {
    const [user, memberships] = await Promise.all([getMe(), getMyBusinesses()])
    const storedId = readStoredActiveBusinessId()
    const activeBusinessId = resolveActiveBusinessId(memberships, storedId)

    if (activeBusinessId != null) {
      writeStoredActiveBusinessId(activeBusinessId)
    }

    let activeBusiness =
      activeBusinessId != null
        ? await loadActiveBusinessDetails(activeBusinessId)
        : null

    // Membership list can lag right after create; trust stored id if fetch succeeds.
    if (activeBusinessId == null && storedId != null) {
      try {
        activeBusiness = await loadActiveBusinessDetails(storedId)
        return {
          status: "ready",
          error: null,
          user,
          memberships,
          activeBusinessId: storedId,
          activeBusiness,
        }
      } catch {
        // fall through with null active business
      }
    }

    return {
      status: "ready",
      error: null,
      user,
      memberships,
      activeBusinessId,
      activeBusiness,
    }
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to load workspace"
    return {
      status: "error",
      error: message,
      user: null,
      memberships: [],
      activeBusinessId: null,
      activeBusiness: null,
    }
  }
}

export async function switchActiveBusiness(businessId: number) {
  writeStoredActiveBusinessId(businessId)
  const activeBusiness = await loadActiveBusinessDetails(businessId)
  return { activeBusinessId: businessId, activeBusiness }
}
