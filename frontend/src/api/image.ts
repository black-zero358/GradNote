import axios from 'axios';

// 图像处理相关API
export const imageAPI = {
  // 处理图片（上传并OCR识别）
  processImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post<{ image_url: string; text: string }>('/api/v1/image/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};
