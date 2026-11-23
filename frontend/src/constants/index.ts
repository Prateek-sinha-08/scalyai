/**
 * FastAPI (users, businesses, file upload) — separate from LangGraph Server.
 */
const FASTAPI_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/**
 * LangGraph Server (extractor agent /runs/wait).
 */
const LANGGRAPH_SERVER_URL = import.meta.env.VITE_LANGGRAPH_SERVER_URL;

function requireEnv(value: string | undefined, name: string): string {
  if (!value?.trim()) {
    throw new Error(`Missing ${name}. Add it to frontend/.env (see .env.example).`);
  }
  return value;
}

export {
  FASTAPI_URL,
  LANGGRAPH_SERVER_URL,
  requireEnv,
};
