export type UserProfile = {
  id: number
  clerk_id: string
  name: string | null
  email: string | null
  created_at: string
  updated_at: string
}

export type UserPatchPayload = {
  name?: string
  email?: string
}

/** Response from PATCH /api/v1/me/ (same shape as profile). */
export type UserPatchResponse = UserProfile
