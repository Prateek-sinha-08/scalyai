import type { AxiosResponse } from "axios"

import { getApiErrorMessage } from "@/api/errors"

/** Run an axios call and return `data`, mapping failures to `Error` with a readable message. */
export async function apiRequest<T>(
  request: () => Promise<AxiosResponse<T>>,
  fallbackMessage: string
): Promise<T> {
  try {
    const response = await request()
    return response.data
  } catch (error) {
    throw new Error(getApiErrorMessage(error, fallbackMessage))
  }
}
