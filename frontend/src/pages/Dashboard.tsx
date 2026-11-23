
import { useUser, useAuth } from "@clerk/react";
import { useEffect } from "react";

export default function Dashboard() {
  const { user, isLoaded } = useUser();
  const { getToken, isLoaded: authLoaded, isSignedIn } = useAuth();

  useEffect(() => {
    if (!authLoaded || !isSignedIn) return;

    let cancelled = false;

    const fetchData = async () => {
      try {
        const token = await getToken();

        if (!cancelled) {
          console.log("Token available:", Boolean(token));
        }
      } catch (error) {
        if (!cancelled) {
          console.error("Failed to retrieve Clerk token:", error);
        }
      }
    };

    void fetchData();

    return () => {
      cancelled = true;
    };
  }, [getToken, authLoaded, isSignedIn]);

  if (!isLoaded || !authLoaded) {
    return <p>Loading dashboard...</p>;
  }

  if (!isSignedIn || !user) {
    return <p>Please sign in to continue.</p>;
  }

  const email = user.primaryEmailAddress?.emailAddress
    ?? user.emailAddresses?.[0]?.emailAddress
    ?? "No email available";

  return (
    <div>
      <h1 className="text-xl font-semibold">Dashboard</h1>

      <p className="text-sm text-muted-foreground mt-1">
        Overview of your sales pipeline
      </p>

      <p className="text-sm text-muted-foreground mt-1">
        Welcome, {" "}{email} {" . "} {user.username ?? "Username not added"}
      </p>
    </div>
  );
}
