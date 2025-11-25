import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export interface MessageIn {
  id: number;
  chat_id_id: number;
  text: string;
  timestamp: string;
  ticket_id_id: number;
}

export interface MessageOut {
  id: number;
  user_id: number;
  text: string;
  timestamp: string;
  ticket_id_id: number;
}

export interface TicketMessagesResponse {
  ticket_id: number;
  messages_in: MessageIn[];
  messages_out: MessageOut[];
}
export default api;
