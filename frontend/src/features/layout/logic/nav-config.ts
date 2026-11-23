import { APP_ROUTES } from "@/features/layout/logic/app-routes"
import type { NavItem } from "@/features/layout/logic/nav-types"

/**
 * Primary app navigation — hrefs from `app-routes.ts` (synced with `router.tsx`).
 */
export const MAIN_NAV: readonly NavItem[] = [
  {
    title: "Dashboard",
    href: APP_ROUTES.dashboard,
    icon: "LayoutDashboard",
    description: "Overview of your sales pipeline",
  },
  {
    title: "Leads",
    href: APP_ROUTES.leads,
    icon: "Users",
    description: "Manage and track your leads",
  },
  {
    title: "Conversations",
    href: APP_ROUTES.conversations,
    icon: "MessageSquare",
    description: "Lead conversations and replies",
  },
  {
    title: "Activity",
    href: APP_ROUTES.activity,
    icon: "Activity",
    description: "Recent workspace activity",
  },
  {
    title: "Settings",
    href: APP_ROUTES.settings,
    icon: "Settings",
    description: "Workspace and account settings",
  },
] as const

/**
 * Onboarding / setup — shown separately from core workflow nav (Step 5 sidebar).
 */
export const SECONDARY_NAV: readonly NavItem[] = [
  {
    title: "Get started",
    href: APP_ROUTES.getStarted,
    icon: "Rocket",
    description: "Upload documents and configure your business context",
  },
] as const

/** All routable nav entries (main + secondary). */
export const ALL_NAV: readonly NavItem[] = [...MAIN_NAV, ...SECONDARY_NAV]
