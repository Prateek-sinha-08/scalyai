import type { BusinessContext } from "@/types/business-context"

/**
 * Merges extractor output from multiple documents (later files override section fields).
 */
export function mergeBusinessContext(
  base: BusinessContext,
  patch: Partial<BusinessContext>
): BusinessContext {
  const next: BusinessContext = { ...base }

  ;(Object.keys(patch) as (keyof BusinessContext)[]).forEach((key) => {
    const value = patch[key]
    if (value == null) return
    const prev = base[key]
    const merged =
      prev != null &&
      typeof prev === "object" &&
      typeof value === "object" &&
      !Array.isArray(value)
        ? { ...prev, ...value }
        : value
    Object.assign(next, { [key]: merged })
  })

  return next
}