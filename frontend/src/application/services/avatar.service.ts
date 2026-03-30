import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService, ApiResponse } from '../../infrastructure/api/api-client.service';

export interface Avatar {
  id: string;
  name: string;
  description?: string;
  status: 'training' | 'active' | 'failed';
  trainedImages: number;
  trainedVoice: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateAvatarRequest {
  name: string;
  description?: string;
  images: File[];
  voiceSample?: File;
}

export interface UpdateAvatarRequest {
  name?: string;
  description?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AvatarService {
  constructor(private apiClient: ApiClientService) {}

  getAvatars(): Observable<ApiResponse<Avatar[]>> {
    return this.apiClient.get<Avatar[]>('/avatars');
  }

  getAvatar(id: string): Observable<ApiResponse<Avatar>> {
    return this.apiClient.get<Avatar>(`/avatars/${id}`);
  }

  createAvatar(request: CreateAvatarRequest): Observable<ApiResponse<Avatar>> {
    const formData = new FormData();
    formData.append('name', request.name);
    
    if (request.description) {
      formData.append('description', request.description);
    }

    request.images.forEach((image, index) => {
      formData.append(`images[${index}]`, image);
    });

    if (request.voiceSample) {
      formData.append('voiceSample', request.voiceSample);
    }

    return this.apiClient.post<Avatar>('/avatars', formData);
  }

  updateAvatar(id: string, request: UpdateAvatarRequest): Observable<ApiResponse<Avatar>> {
    return this.apiClient.put<Avatar>(`/avatars/${id}`, request);
  }

  deleteAvatar(id: string): Observable<ApiResponse<void>> {
    return this.apiClient.delete<void>(`/avatars/${id}`);
  }

  startTraining(id: string): Observable<ApiResponse<void>> {
    return this.apiClient.post<void>(`/avatars/${id}/train`, {});
  }

  getTrainingProgress(id: string): Observable<ApiResponse<{ progress: number; status: string }>> {
    return this.apiClient.get<{ progress: number; status: string }>(`/avatars/${id}/training-progress`);
  }

  generateVideo(avatarId: string, text: string, options?: any): Observable<ApiResponse<{ taskId: string }>> {
    const request = {
      text,
      ...options
    };
    return this.apiClient.post<{ taskId: string }>(`/avatars/${avatarId}/generate`, request);
  }
}