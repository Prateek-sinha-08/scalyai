import { apiClient } from "@/api/client"
import { apiRequest } from "@/api/request"
import type {
  BusinessDetails,
  BusinessMember,
  BusinessMemberPatchPayload,
  BusinessPatchPayload,
  CreateBusinessPayload,
} from "@/schemas/business"

const BUSINESS_BASE = "/api/v1/business"

export async function createBusiness(
  payload: CreateBusinessPayload
): Promise<BusinessDetails> {
  return apiRequest(
    () => apiClient.post<BusinessDetails>(`${BUSINESS_BASE}/`, payload),
    "Failed to create business"
  )
}

export async function getBusinessById(businessId: number): Promise<BusinessDetails> {
  return apiRequest(
    () => apiClient.get<BusinessDetails>(`${BUSINESS_BASE}/${businessId}`),
    "Failed to load business"
  )
}

export async function patchBusiness(
  businessId: number,
  payload: BusinessPatchPayload
): Promise<BusinessDetails> {
  return apiRequest(
    () =>
      apiClient.patch<BusinessDetails>(`${BUSINESS_BASE}/${businessId}`, payload),
    "Failed to update business"
  )
}

export async function deleteBusiness(businessId: number): Promise<BusinessDetails> {
  return apiRequest(
    () => apiClient.delete<BusinessDetails>(`${BUSINESS_BASE}/${businessId}`),
    "Failed to delete business"
  )
}

export async function getBusinessMembers(
  businessId: number
): Promise<BusinessMember[]> {
  return apiRequest(
    () =>
      apiClient.get<BusinessMember[]>(`${BUSINESS_BASE}/${businessId}/members`),
    "Failed to load team members"
  )
}

export async function patchBusinessMember(
  businessId: number,
  memberId: number,
  payload: BusinessMemberPatchPayload
): Promise<BusinessMember> {
  return apiRequest(
    () =>
      apiClient.patch<BusinessMember>(
        `${BUSINESS_BASE}/${businessId}/members/${memberId}`,
        payload
      ),
    "Failed to update team member"
  )
}

export async function deleteBusinessMember(
  businessId: number,
  memberId: number
): Promise<BusinessMember> {
  return apiRequest(
    () =>
      apiClient.delete<BusinessMember>(
        `${BUSINESS_BASE}/${businessId}/members/${memberId}`
      ),
    "Failed to remove team member"
  )
}
