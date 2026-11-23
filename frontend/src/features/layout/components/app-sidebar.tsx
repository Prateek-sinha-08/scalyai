import { Link } from "react-router-dom"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
  SidebarSeparator,
} from "@/components/ui/sidebar"
import { MAIN_NAV, SECONDARY_NAV } from "@/features/layout/logic"
import { SidebarNavMenu } from "@/features/layout/components/sidebar-nav-menu"
import { useWorkspace } from "@/features/workspace/logic/workspace-context"

export function AppSidebar() {
  const { memberships, activeBusinessId } = useWorkspace()
  const canUseGetStarted = memberships.length > 0 && activeBusinessId != null
  const setupNav = canUseGetStarted ? SECONDARY_NAV : []

  return (
    <Sidebar collapsible="icon" variant="inset">
      <SidebarHeader>
        <Link
          to="/"
          className="flex items-center gap-2 rounded-md px-2 py-1.5 outline-none ring-sidebar-ring hover:bg-sidebar-accent focus-visible:ring-2"
        >
          <img
            src="/scaly-sidebar.svg"
            alt="ScalyAI logo"
            className="h-12 w-10 shrink-0 rounded-md object-contain"
          />
          <span className="truncate text-sm font-semibold tracking-tight group-data-[collapsible=icon]:hidden">
            ScalyAI
          </span>
        </Link>
      </SidebarHeader>

      <SidebarContent>
        <SidebarNavMenu items={MAIN_NAV} label="Platform" />
        {setupNav.length > 0 ? (
          <>
            <SidebarSeparator className="mx-2" />
            <SidebarNavMenu items={setupNav} label="Setup" />
          </>
        ) : null}
      </SidebarContent>

      <SidebarFooter className="p-2 group-data-[collapsible=icon]:hidden">
        <p className="px-2 text-xs text-muted-foreground">
          One Stop Lead Funneling | ScalyAI
        </p>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}