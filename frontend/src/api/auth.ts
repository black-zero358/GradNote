import axios from 'axios';

interface LoginParams {
  email: string;
  password: string;
}

interface RegisterParams {
  username: string;
  email: string;
  password: string;
}

export const authAPI = {
  login: (data: LoginParams) => 
    axios.post('/api/v1/auth/login', data),
  
  register: (data: RegisterParams) => 
    axios.post('/api/v1/auth/register', data),
  
  logout: () => 
    axios.post('/api/v1/auth/logout'),
  
  getCurrentUser: () => 
    axios.get('/api/v1/auth/me')
};
