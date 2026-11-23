export type BusinessUserRole = "owner" | "admin" | "member"

export type BusinessMembership = {
  id: number
  name: string
  description: string
  industry: string
  permissions: Record<string, unknown>
  role: BusinessUserRole
}

export type BusinessDetails = {
  id: number
  name: string
  description: string
  industry: string
  created_at: string
  updated_at: string
}

export type CreateBusinessPayload = {
  name: string
  description: string
  industry: string
}

export type BusinessPatchPayload = {
  name?: string
  description?: string
  industry?: string
}

export type BusinessMember = {
  id: number
  name: string
  email: string
  role: BusinessUserRole
  permissions: Record<string, unknown>
}

export type BusinessMemberPatchPayload = {
  role?: BusinessUserRole
  permissions?: Record<string, unknown>
}
