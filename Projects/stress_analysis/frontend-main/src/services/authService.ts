import axios from 'axios';

const API_URL = 'http://localhost:8080/api/auth';

interface AuthRequest {
  email: string;
  password: string;
}

export const authService = {
  async signup(data: AuthRequest) {
    try {
      const response = await axios.post(`${API_URL}/signup`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async login(data: AuthRequest) {
    try {
      const response = await axios.post(`${API_URL}/login`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}; 