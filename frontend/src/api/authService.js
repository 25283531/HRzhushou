import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'; // 从环境变量或默认值获取后端API基础URL

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 可以添加请求拦截器来附加JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const login = async (credentials) => {
  try {
    const response = await apiClient.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Login failed');
  }
};

export const register = async (userData) => {
  try {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Registration failed');
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  // Optionally, notify the backend about logout
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

export default {
  login,
  register,
  logout,
  isAuthenticated,
  apiClient, // 导出 apiClient 以便在其他地方使用
};