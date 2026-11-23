import axios from "axios";
import { LANGGRAPH_SERVER_URL, requireEnv } from "@/constants";

const langgraphClient = axios.create({
  baseURL: requireEnv(LANGGRAPH_SERVER_URL, "VITE_LANGGRAPH_SERVER_URL"),
});

export { langgraphClient };
