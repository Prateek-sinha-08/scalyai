import * as React from "react"
import { Building2, ChevronsUpDown, Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Skeleton } from "@/components/ui/skeleton"
import { CreateBusinessSheet } from "@/features/workspace/components/create-business-sheet"
import { useWorkspace } from "@/features/workspace/logic/workspace-context"

export function BusinessSwitcher() {
  const {
    status,
    memberships,
    activeBusinessId,
    activeBusiness,
    setActiveBusinessId,
  } = useWorkspace()
  const [createOpen, setCreateOpen] = React.useState(false)

  if (status === "idle" || status === "loading") {
    return <Skeleton className="hidden h-8 w-36 md:block" />
  }

  const label =
    activeBusiness?.name ??
    (memberships.length === 0 ? "No business" : (memberships[0]?.name ?? "Business"))

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="hidden h-8 max-w-[14rem] gap-2 md:flex"
          >
            <Building2 className="size-3.5 shrink-0 text-muted-foreground" />
            <span className="truncate">{label}</span>
            <ChevronsUpDown className="size-3.5 shrink-0 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56">
          <DropdownMenuLabel>My business</DropdownMenuLabel>
          {memberships.map((m) => (
            <DropdownMenuItem
              key={m.id}
              className="cursor-pointer"
              onSelect={() => {
                if (m.id !== activeBusinessId) {
                  void setActiveBusinessId(m.id)
                }
              }}
            >
              <span className="truncate font-medium">{m.name}</span>
              {m.id === activeBusinessId ? (
                <span className="ml-auto text-xs text-muted-foreground">Active</span>
              ) : null}
            </DropdownMenuItem>
          ))}
          {memberships.length === 0 ? (
            <p className="px-2 py-1.5 text-xs text-muted-foreground">
              Create a business to upload documents and use the app.
            </p>
          ) : null}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="cursor-pointer"
            onSelect={() => setCreateOpen(true)}
          >
            <Plus className="size-4" />
            Create business
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <CreateBusinessSheet open={createOpen} onOpenChange={setCreateOpen} />
    </>
  )
}