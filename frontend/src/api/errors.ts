import { AxiosError } from "axios"

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === "string") return detail
    if (Array.isArray(detail)) {
      return detail.map((d) => d?.msg ?? String(d)).join(", ")
    }
    const message = error.response?.data?.message
    if (typeof message === "string") return message
  }
  if (error instanceof Error) return error.message
  return fallback
}
