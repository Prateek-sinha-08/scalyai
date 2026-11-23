import * as React from "react"
import { useAuth } from "@clerk/react"

import type { BusinessDetails } from "@/schemas/business"
import {
  bootstrapWorkspace,
  switchActiveBusiness,
} from "@/features/workspace/logic/use-workspace-bootstrap"
import { writeStoredActiveBusinessId } from "@/features/workspace/logic/workspace-storage"
import type { WorkspaceContextValue } from "@/features/workspace/logic/workspace-types"

const WorkspaceContext = React.createContext<WorkspaceContextValue | null>(null)

function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn } = useAuth()
  const [state, setState] = React.useState<
    Omit<
      WorkspaceContextValue,
      | "setActiveBusinessId"
      | "registerCreatedBusiness"
      | "applyBusinessDetails"
      | "refresh"
    >
  >({
    status: "idle",
    error: null,
    user: null,
    memberships: [],
    activeBusinessId: null,
    activeBusiness: null,
  })

  const refresh = React.useCallback(async () => {
    setState((prev) => ({ ...prev, status: "loading", error: null }))
    const result = await bootstrapWorkspace()
    setState((prev) => {
      const next = { ...prev, ...result }
      if (
        result.status === "ready" &&
        result.activeBusinessId == null &&
        prev.activeBusinessId != null
      ) {
        next.activeBusinessId = prev.activeBusinessId
        if (result.activeBusiness == null) {
          next.activeBusiness = prev.activeBusiness
        }
      }
      if (
        result.status === "ready" &&
        result.memberships.length === 0 &&
        prev.memberships.length > 0
      ) {
        next.memberships = prev.memberships
      }
      return next
    })
  }, [])

  const applyBusinessDetails = React.useCallback((business: BusinessDetails) => {
    setState((prev) => ({
      ...prev,
      activeBusiness:
        prev.activeBusinessId === business.id ? business : prev.activeBusiness,
      memberships: prev.memberships.map((m) =>
        m.id === business.id
          ? {
              ...m,
              name: business.name,
              description: business.description,
              industry: business.industry,
            }
          : m
      ),
    }))
  }, [])

  const registerCreatedBusiness = React.useCallback((business: BusinessDetails) => {
    writeStoredActiveBusinessId(business.id)
    setState((prev) => {
      const hasMember = prev.memberships.some((m) => m.id === business.id)
      const memberships = hasMember
        ? prev.memberships.map((m) =>
            m.id === business.id
              ? {
                  ...m,
                  name: business.name,
                  description: business.description,
                  industry: business.industry,
                }
              : m
          )
        : [
            ...prev.memberships,
            {
              id: business.id,
              name: business.name,
              description: business.description,
              industry: business.industry,
              permissions: {},
              role: "owner" as const,
            },
          ]
      return {
        ...prev,
        status: "ready",
        error: null,
        memberships,
        activeBusinessId: business.id,
        activeBusiness: business,
      }
    })
  }, [])

  const setActiveBusinessId = React.useCallback(async (businessId: number) => {
    setState((prev) => ({ ...prev, status: "loading", error: null }))
    try {
      const next = await switchActiveBusiness(businessId)
      setState((prev) => ({
        ...prev,
        status: "ready",
        error: null,
        ...next,
      }))
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to switch business"
      setState((prev) => ({
        ...prev,
        status: "error",
        error: message,
      }))
    }
  }, [])

  React.useEffect(() => {
    if (!isLoaded || !isSignedIn) {
      setState({
        status: "idle",
        error: null,
        user: null,
        memberships: [],
        activeBusinessId: null,
        activeBusiness: null,
      })
      return
    }
    void refresh()
  }, [isLoaded, isSignedIn, refresh])

  const value = React.useMemo<WorkspaceContextValue>(
    () => ({
      ...state,
      setActiveBusinessId,
      registerCreatedBusiness,
      applyBusinessDetails,
      refresh,
    }),
    [state, setActiveBusinessId, registerCreatedBusiness, applyBusinessDetails, refresh]
  )

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  )
}

function useWorkspace() {
  const ctx = React.useContext(WorkspaceContext)
  if (!ctx) {
    throw new Error("useWorkspace must be used within WorkspaceProvider")
  }
  return ctx
}

export { WorkspaceProvider, useWorkspace }
