/**
 * Upload APIs require a business the user is a member of.
 * Active business must come from workspace (create via My Business dropdown).
 */
export function requireActiveBusinessId(activeBusinessId: number | null): number {
  if (activeBusinessId == null) {
    throw new Error(
      "No active business. Create a business from My Business first."
    )
  }
  return activeBusinessId
}