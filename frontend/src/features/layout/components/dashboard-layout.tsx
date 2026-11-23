import { Outlet } from "react-router-dom"

import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/features/layout/components/app-sidebar"
import { AppTopbar } from "@/features/layout/components/app-topbar"
import { WorkspaceGate } from "@/features/workspace/components"

export function DashboardLayout() {
  return (
    <SidebarProvider defaultOpen>
      <AppSidebar />
      <SidebarInset>
        <AppTopbar />
        <WorkspaceGate>
          <main className="flex flex-1 flex-col overflow-auto p-4 md:p-6">
            <Outlet />
          </main>
        </WorkspaceGate>
      </SidebarInset>
    </SidebarProvider>
  )
}
