const ACTIVE_BUSINESS_ID_KEY = "scalyai_active_business_id"

export function readStoredActiveBusinessId(): number | null {
  try {
    const raw = localStorage.getItem(ACTIVE_BUSINESS_ID_KEY)
    if (!raw) return null
    const id = Number.parseInt(raw, 10)
    return Number.isFinite(id) ? id : null
  } catch {
    return null
  }
}

export function writeStoredActiveBusinessId(businessId: number): void {
  localStorage.setItem(ACTIVE_BUSINESS_ID_KEY, String(businessId))
}

export function clearStoredActiveBusinessId(): void {
  localStorage.removeItem(ACTIVE_BUSINESS_ID_KEY)
}

/** Pick active business id from storage or default to first membership. */
export function resolveActiveBusinessId(
  memberships: { id: number }[],
  storedId: number | null
): number | null {
  if (memberships.length === 0) return null
  if (storedId != null && memberships.some((m) => m.id === storedId)) {
    return storedId
  }
  return memberships[0].id
}
