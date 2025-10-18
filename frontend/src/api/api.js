import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Clients API
export const clientsApi = {
  getAll: () => axios.get(`${API}/clients`),
  getOne: (id) => axios.get(`${API}/clients/${id}`),
  create: (data) => axios.post(`${API}/clients`, data),
  update: (id, data) => axios.put(`${API}/clients/${id}`, data),
  delete: (id) => axios.delete(`${API}/clients/${id}`),
};

// Projects API
export const projectsApi = {
  getAll: (params) => axios.get(`${API}/projects`, { params }),
  getOne: (id) => axios.get(`${API}/projects/${id}`),
  create: (data) => axios.post(`${API}/projects`, data),
  update: (id, data) => axios.put(`${API}/projects/${id}`, data),
  delete: (id) => axios.delete(`${API}/projects/${id}`),
  getStats: () => axios.get(`${API}/projects/stats/dashboard`),
};

// Work Hours API
export const workHoursApi = {
  getAll: (params) => axios.get(`${API}/workhours`, { params }),
  getOne: (id) => axios.get(`${API}/workhours/${id}`),
  create: (data) => axios.post(`${API}/workhours`, data),
  update: (id, data) => axios.put(`${API}/workhours/${id}`, data),
  delete: (id) => axios.delete(`${API}/workhours/${id}`),
  getSummary: (params) => axios.get(`${API}/workhours/summary/stats`, { params }),
};

// Photos API
export const photosApi = {
  getAll: (params) => axios.get(`${API}/photos`, { params }),
  getOne: (id) => axios.get(`${API}/photos/${id}`),
  create: (data) => axios.post(`${API}/photos`, data),
  update: (id, data) => axios.put(`${API}/photos/${id}`, data),
  delete: (id) => axios.delete(`${API}/photos/${id}`),
};

// Employee Work Entries API
export const employeeWorkApi = {
  getSummary: (params) => axios.get(`${API}/employee-work-entries/summary`, { params }),
};
