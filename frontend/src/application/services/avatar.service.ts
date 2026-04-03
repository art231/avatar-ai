import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService, ApiResponse } from '../../infrastructure/api/api-client.service';

export interface Avatar {
  id: string;
  userId: string;
  name: string;
  description?: string;
  status: string; // 'Pending' | 'Training' | 'Active' | 'Failed' - соответствует AvatarStatus enum в бэкенде
  loraPath?: string;
  trainedImages: number;
  trainedVoice: boolean;
  createdAt: string;
  updatedAt: string;
  voiceProfile?: VoiceProfile;
  generationTasks?: GenerationTask[];
}

export interface VoiceProfile {
  id: string;
  avatarId: string;
  audioSamplePath: string;
  xttsModelPath?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GenerationTask {
  id: string;
  avatarId: string;
  userId: string;
  speechText: string;
  actionPrompt?: string;
  status: string;
  stage: string;
  progress: number;
  outputPath?: string;
  errorMessage?: string;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  taskLogs: TaskLog[];
  voiceStyle?: string;
  videoLength?: string;
  resolution?: string;
  background?: string;
  avatarName?: string;
  videoUrl?: string;
  audioUrl?: string;
}

export interface TaskLog {
  id: string;
  taskId: string;
  stage: string;
  message: string;
  createdAt: string;
}

export interface CreateAvatarRequest {
  userId: string;
  name: string;
  description?: string;
  images: File[];
  voiceSample?: File;
}

export interface UpdateAvatarRequest {
  name?: string;
  description?: string;
}

export interface TrainingProgress {
  avatarId: string;
  status: string;
  progress: number;
  totalSteps: number;
  currentStep: number;
  currentStepName: string;
  errorMessage?: string;
  startedAt: string;
  estimatedCompletion?: string;
}

export interface GenerateVideoRequest {
  text: string;
  voiceStyle?: string;
  videoLength?: string;
  resolution?: string;
  background?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AvatarService {
  constructor(private apiClient: ApiClientService) {}

  getAvatars(userId?: string): Observable<ApiResponse<Avatar[]>> {
    const params = userId ? { userId } : undefined;
    return this.apiClient.get<Avatar[]>('/avatars', params);
  }

  getAvatar(id: string): Observable<ApiResponse<Avatar>> {
    return this.apiClient.get<Avatar>(`/avatars/${id}`);
  }

  createAvatar(request: CreateAvatarRequest): Observable<ApiResponse<Avatar>> {
    const formData = new FormData();
    formData.append('userId', request.userId);
    formData.append('name', request.name);
    
    if (request.description) {
      formData.append('description', request.description);
    }

    request.images.forEach((image, index) => {
      formData.append(`images`, image); // Бэкенд ожидает массив файлов с именем 'images'
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

  getTrainingProgress(id: string): Observable<ApiResponse<TrainingProgress>> {
    return this.apiClient.get<TrainingProgress>(`/avatars/${id}/training-progress`);
  }

  generateVideo(avatarId: string, request: GenerateVideoRequest): Observable<ApiResponse<GenerationTask>> {
    return this.apiClient.post<GenerationTask>(`/avatars/${avatarId}/generate`, request);
  }
}
