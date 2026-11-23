import { NavLink, useLocation } from "react-router-dom"

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { getNavIcon, isNavLinkActive } from "@/features/layout/logic"
import type { NavItem } from "@/features/layout/logic"

type SidebarNavMenuProps = {
  items: readonly NavItem[]
  label?: string
}

/** Presentational nav list — pass `items` from nav-config; safe to reuse or copy. */
export function SidebarNavMenu({ items, label }: SidebarNavMenuProps) {
  const { pathname } = useLocation()

  return (
    <SidebarGroup>
      {label ? <SidebarGroupLabel>{label}</SidebarGroupLabel> : null}
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            const Icon = getNavIcon(item.icon)
            const active = isNavLinkActive(pathname, item.href)

            return (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  asChild
                  isActive={active}
                  tooltip={item.title}
                >
                  <NavLink to={item.href}>
                    <Icon />
                    <span>{item.title}</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            )
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
