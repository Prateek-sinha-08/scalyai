import { apiClient } from "@/api/client"
import { apiRequest } from "@/api/request"
import type { BusinessMembership } from "@/schemas/business"
import type {
  UserPatchPayload,
  UserPatchResponse,
  UserProfile,
} from "@/schemas/user"

const ME_BASE = "/api/v1/me"

export async function getMe(): Promise<UserProfile> {
  return apiRequest(
    () => apiClient.get<UserProfile>(`${ME_BASE}/`),
    "Failed to load profile"
  )
}

export async function patchMe(payload: UserPatchPayload): Promise<UserPatchResponse> {
  return apiRequest(
    () => apiClient.patch<UserPatchResponse>(`${ME_BASE}/`, payload),
    "Failed to update profile"
  )
}

export async function getMyBusinesses(): Promise<BusinessMembership[]> {
  return apiRequest(
    () => apiClient.get<BusinessMembership[]>(`${ME_BASE}/businesses`),
    "Failed to load businesses"
  )
}
