import axios from 'axios';
import { Question } from '../types';

// 错题相关API
export const questionsAPI = {
  // 获取错题列表
  getQuestions: (skip = 0, limit = 10) => 
    axios.get<{ data: Question[], total: number }>(`/api/v1/questions/?skip=${skip}&limit=${limit}`),
  
  // 获取单个错题详情
  getQuestion: (id: number) => 
    axios.get<{ data: Question }>(`/api/v1/questions/${id}`),
  
  // 创建错题
  createQuestion: (data: Partial<Question>) => 
    axios.post<{ data: Question }>('/api/v1/questions/', data),
  
  // 更新错题
  updateQuestion: (id: number, data: Partial<Question>) => 
    axios.put<{ data: Question }>(`/api/v1/questions/${id}`, data),
  
  // 删除错题
  deleteQuestion: (id: number) => 
    axios.delete(`/api/v1/questions/${id}`),
  
  // 从图片创建错题
  createFromImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post<{ data: Question }>('/api/v1/questions/from-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};
