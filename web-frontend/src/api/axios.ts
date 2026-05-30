import axios from 'axios';

// Create a custom Axios instance with our backend's base URL
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export interface PredictionResponse {
  status: 'success' | 'error';
  filename: string;
  prediction: string;
  error_message: string | null;
}

export const uploadImage = async (file: File): Promise<PredictionResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post<PredictionResponse>('http://127.0.0.1:8000/predict', formData);
  return response.data;
};

export const uploadVideo = async (file: File): Promise<PredictionResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post<PredictionResponse>('http://127.0.0.1:8000/predict', formData);
  return response.data;
};
