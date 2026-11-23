import axios from "axios";
import { FASTAPI_URL } from "@/constants";

/** Axios client for the ScalyAI FastAPI backend (Clerk JWT attached when signed in). */
const apiClient = axios.create({
  baseURL: FASTAPI_URL,
});

let tokenGetter: (() => Promise<string | null>) | null = null;

export const setTokenGetter = (getter: () => Promise<string | null>) => {
    tokenGetter = getter;
};

apiClient.interceptors.request.use(async (config) => {
    if(tokenGetter) {
        const token = await tokenGetter();
        if(token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
})

export {
    apiClient,
}