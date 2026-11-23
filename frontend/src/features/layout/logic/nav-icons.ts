import {
  Activity,
  LayoutDashboard,
  MessageSquare,
  Rocket,
  Settings,
  Users,
  type LucideIcon,
} from "lucide-react"

import type { NavIconName } from "@/features/layout/logic/nav-types"

const NAV_ICONS: Record<NavIconName, LucideIcon> = {
  LayoutDashboard,
  Users,
  MessageSquare,
  Activity,
  Settings,
  Rocket,
}

export function getNavIcon(name: NavIconName): LucideIcon {
  return NAV_ICONS[name]
}
