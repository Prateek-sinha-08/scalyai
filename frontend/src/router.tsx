import { createBrowserRouter } from "react-router-dom"
import App from "@/App"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import {
  DashboardLayout,
  OnboardingLayout,
} from "@/features/layout/components"
import { APP_ROUTES, AUTH_ROUTES } from "@/features/layout/logic"
import { RequireActiveBusiness } from "@/features/workspace/components/require-active-business"
import Dashboard from "@/pages/Dashboard"
import Leads from "@/pages/Leads"
import Conversations from "@/pages/Conversations"
import Activity from "@/pages/Activity"
import Settings from "@/pages/Settings"
import Login from "@/pages/Login"
import Signup from "@/pages/Signup"
import SSOCallback from "@/pages/SSOCallback"
import GetStarted from "@/pages/GetStarted"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { path: AUTH_ROUTES.login.slice(1), element: <Login /> },
      { path: AUTH_ROUTES.signup.slice(1), element: <Signup /> },
      { path: AUTH_ROUTES.ssoCallback.slice(1), element: <SSOCallback /> },
      {
        element: <ProtectedRoute />,
        children: [
          /* Onboarding: no dashboard sidebar (Option B) */
          {
            path: APP_ROUTES.getStarted.slice(1),
            element: <OnboardingLayout />,
            children: [
              {
                index: true,
                element: (
                  <RequireActiveBusiness>
                    <GetStarted />
                  </RequireActiveBusiness>
                ),
              },
            ],
          },
          /* Main app shell */
          {
            element: <DashboardLayout />,
            children: [
              { index: true, element: <Dashboard /> },
              { path: APP_ROUTES.leads.slice(1), element: <Leads /> },
              {
                path: APP_ROUTES.conversations.slice(1),
                element: <Conversations />,
              },
              { path: APP_ROUTES.activity.slice(1), element: <Activity /> },
              { path: APP_ROUTES.settings.slice(1), element: <Settings /> },
            ],
          },
        ],
      },
    ],
  },
])