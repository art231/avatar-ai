import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService, ApiResponse } from '../../infrastructure/api/api-client.service';

export interface GenerationTask {
  id: string;
  avatarId: string;
  avatarName: string;
  text: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  videoUrl?: string;
  audioUrl?: string;
  errorMessage?: string;
  createdAt: string;
  completedAt?: string;
}

export interface CreateGenerationTaskRequest {
  avatarId: string;
  text: string;
  voiceStyle?: string;
  videoLength?: string;
  resolution?: string;
  background?: string;
}

@Injectable({
  providedIn: 'root'
})
export class GenerationTaskService {
  constructor(private apiClient: ApiClientService) {}

  getTasks(): Observable<ApiResponse<GenerationTask[]>> {
    return this.apiClient.get<GenerationTask[]>('/generation-tasks');
  }

  getTask(id: string): Observable<ApiResponse<GenerationTask>> {
    return this.apiClient.get<GenerationTask>(`/generation-tasks/${id}`);
  }

  createTask(request: CreateGenerationTaskRequest): Observable<ApiResponse<GenerationTask>> {
    return this.apiClient.post<GenerationTask>('/generation-tasks', request);
  }

  cancelTask(id: string): Observable<ApiResponse<void>> {
    return this.apiClient.post<void>(`/generation-tasks/${id}/cancel`, {});
  }

  retryTask(id: string): Observable<ApiResponse<void>> {
    return this.apiClient.post<void>(`/generation-tasks/${id}/retry`, {});
  }

  deleteTask(id: string): Observable<ApiResponse<void>> {
    return this.apiClient.delete<void>(`/generation-tasks/${id}`);
  }

  getTaskProgress(id: string): Observable<ApiResponse<{ progress: number; status: string; stage?: string }>> {
    return this.apiClient.get<{ progress: number; status: string; stage?: string }>(`/generation-tasks/${id}/progress`);
  }

  subscribeToTaskUpdates(id: string): Observable<GenerationTask> {
    // Здесь будет реализация WebSocket или Server-Sent Events
    // Пока возвращаем заглушку
    return new Observable<GenerationTask>(observer => {
      // Реальная реализация будет использовать WebSocket
      observer.complete();
    });
  }
}