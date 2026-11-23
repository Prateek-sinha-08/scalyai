import { Link, Outlet } from "react-router-dom"

import { APP_ROUTES } from "@/features/layout/logic/app-routes"
import { BusinessSwitcher } from "@/features/workspace/components"

/**
 * Minimal shell for first-time setup — no sidebar (see Step 6 routing).
 */
export function OnboardingLayout() {
  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <header className="flex h-14 shrink-0 items-center border-b border-border/60 px-4 md:px-6">
        <Link
          to={APP_ROUTES.dashboard}
          className="flex items-center gap-2 rounded-md outline-none ring-ring focus-visible:ring-2"
        >
          <img
            src="/scaly-main.svg"
            alt=""
            className="size-8 rounded-md"
            width={32}
            height={32}
          />
          <span className="text-sm font-semibold tracking-tight">ScalyAI</span>
        </Link>
        <p className="ml-4 hidden text-xs text-muted-foreground sm:block">
          Set up your business context
        </p>
        <div className="ml-auto">
          <BusinessSwitcher />
        </div>
      </header>

      <div className="relative flex flex-1 flex-col">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,theme(colors.muted)_0%,transparent_55%)]"
        />
        <div className="relative flex flex-1 items-center justify-center px-4 py-8 sm:py-12">
          <Outlet />
        </div>
      </div>
    </div>
  )
}