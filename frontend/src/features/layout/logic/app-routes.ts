/**
 * Single source of truth for app paths — keep in sync with `src/router.tsx`.
 */
export const AUTH_ROUTES = {
  login: "/login",
  signup: "/signup",
  ssoCallback: "/sso-callback",
} as const

export const APP_ROUTES = {
  dashboard: "/",
  leads: "/leads",
  conversations: "/conversations",
  activity: "/activity",
  settings: "/settings",
  getStarted: "/get-started",
} as const

/** Paths rendered inside `DashboardLayout` (excludes onboarding). */
export const DASHBOARD_APP_PATHS = [
  APP_ROUTES.dashboard,
  APP_ROUTES.leads,
  APP_ROUTES.conversations,
  APP_ROUTES.activity,
  APP_ROUTES.settings,
] as const
