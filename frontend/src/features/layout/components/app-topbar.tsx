import { useClerk, useUser } from "@clerk/react"
import { LogOut, Settings } from "lucide-react"
import { Link, useLocation } from "react-router-dom"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { APP_ROUTES, getNavItemForPath } from "@/features/layout/logic"
import { BusinessSwitcher } from "@/features/workspace/components"

function userInitials(name: string | null | undefined, email: string | undefined) {
  if (name?.trim()) {
    const parts = name.trim().split(/\s+/)
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    }
    return name.slice(0, 2).toUpperCase()
  }
  if (email) {
    return email.slice(0, 2).toUpperCase()
  }
  return "SA"
}

export function AppTopbar() {
  const { pathname } = useLocation()
  const { user } = useUser()
  const { signOut } = useClerk()

  const navItem = getNavItemForPath(pathname)
  const title = navItem?.title ?? "ScalyAI"
  const description = navItem?.description

  const email =
    user?.primaryEmailAddress?.emailAddress ??
    user?.emailAddresses[0]?.emailAddress ??
    ""

  const displayName = user?.fullName ?? user?.username ?? email

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border/60 bg-background/80 px-4 backdrop-blur-sm">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 hidden h-4 sm:block" />

      <div className="flex min-w-0 flex-1 flex-col">
        <h1 className="truncate text-sm font-semibold leading-tight">{title}</h1>
        {description ? (
          <p className="hidden truncate text-xs text-muted-foreground sm:block">
            {description}
          </p>
        ) : null}
      </div>

      <BusinessSwitcher />

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="relative size-9 rounded-full p-0"
            aria-label="Open account menu"
          >
            <Avatar className="size-8">
              {user?.imageUrl ? (
                <AvatarImage src={user.imageUrl} alt={displayName ?? "Account"} />
              ) : null}
              <AvatarFallback className="bg-primary/15 text-xs text-primary">
                {userInitials(displayName, email)}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col gap-0.5">
              <span className="truncate text-sm font-medium">{displayName}</span>
              {email ? (
                <span className="truncate text-xs text-muted-foreground">{email}</span>
              ) : null}
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link to={APP_ROUTES.settings} className="cursor-pointer">
              <Settings className="size-4" />
              Settings
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            variant="destructive"
            className="cursor-pointer"
            onSelect={() => {
              void signOut({ redirectUrl: "/login" })
            }}
          >
            <LogOut className="size-4" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
