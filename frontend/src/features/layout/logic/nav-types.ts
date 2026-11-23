/** Lucide icon keys used in navigation config (resolved in nav-icons.ts). */
export const NAV_ICON_NAMES = [
  "LayoutDashboard",
  "Users",
  "MessageSquare",
  "Activity",
  "Settings",
  "Rocket",
] as const

export type NavIconName = (typeof NAV_ICON_NAMES)[number]

export type NavItem = {
  title: string
  href: string
  icon: NavIconName
  /** Shown in page headers / tooltips when sidebar is collapsed */
  description?: string
}
