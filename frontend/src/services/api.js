import axios from 'axios';
import { supabaseAuth } from './supabaseAuth.js';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 60000,
});

api.interceptors.request.use(async (config) => {
  if (!supabaseAuth) return config;
  const { data } = await supabaseAuth.auth.getSession();
  const token = data.session?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function postJson(path, payload, config = {}) {
  const { data } = await api.post(path, payload, config);
  return data;
}

export async function getJson(path, config = {}) {
  const { data } = await api.get(path, config);
  return data;
}

export async function deleteJson(path, config = {}) {
  const { data } = await api.delete(path, config);
  return data;
}

export async function uploadFile(path, file, extra = {}, onUploadProgress) {
  const formData = new FormData();
  formData.append('file', file);
  Object.entries(extra).forEach(([key, value]) => formData.append(key, value));
  const { data } = await api.post(path, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  });
  return data;
}

export default api;
