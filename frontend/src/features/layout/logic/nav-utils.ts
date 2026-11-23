import { ALL_NAV } from "@/features/layout/logic/nav-config"
import type { NavItem } from "@/features/layout/logic/nav-types"

/** Whether `href` is the active route for `pathname` (React Router). */
export function isNavLinkActive(pathname: string, href: string): boolean {
  const normalized = pathname.replace(/\/+$/, "") || "/"
  if (href === "/") {
    return normalized === "/"
  }
  return normalized === href || normalized.startsWith(`${href}/`)
}

/** Nav item for the current path, if any (for topbar title in Step 5). */
export function getNavItemForPath(pathname: string): NavItem | undefined {
  return ALL_NAV.find((item) => isNavLinkActive(pathname, item.href))
}
