import axios from 'axios';
import { BASE_URL } from './config.mjs';

// Create an axios instance
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Login API - MOCKED (Backend not available)
export const loginUser = async ({ email, password }) => {
  try {
    // Mock successful login response
    return {
      data: {
        username: 'Admin User',
        email: email,
        user_id: 'admin123',
        token: 'mock-token-12345'
      }
    };
    
    // Uncomment below for actual backend call
    // const response = await axiosInstance.post('/api/login', {
    //   email,
    //   password
    // });
    // return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error.response?.data || { message: 'Login error' };
  }
};

// Signup API - MOCKED (Backend not available)
export const signupUser = async ({ username, email, password }) => {
  try {
    // Mock successful signup response
    return {
      data: {
        username: username,
        email: email,
        user_id: 'user' + Date.now(),
        token: 'mock-token-' + Date.now()
      }
    };
    
    // Uncomment below for actual backend call
    // const response = await axiosInstance.post('/api/signup', {
    //   username,
    //   email,
    //   password
    // });
    // return response.data;
  } catch (error) {
    console.error('Signup failed:', error);
    throw error.response?.data || { message: 'Signup error' };
  }
};

const AUTH_APIS = {
    loginUser,
    signupUser
};

export default AUTH_APIS;
