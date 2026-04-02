import { Injectable } from '@angular/core';
import { Observable, Subject, interval, merge, of } from 'rxjs';
import { map, switchMap, takeUntil, catchError, startWith, distinctUntilChanged, shareReplay } from 'rxjs/operators';
import { ApiClientService, ApiResponse } from '../../infrastructure/api/api-client.service';

export interface GenerationTask {
  id: string;
  avatarId: string;
  avatarName: string;
  text: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  stage?: string;
  videoUrl?: string;
  audioUrl?: string;
  errorMessage?: string;
  createdAt: string;
  completedAt?: string;
  settings?: {
    voiceStyle?: string;
    videoLength?: string;
    resolution?: string;
    background?: string;
  };
}

export interface CreateGenerationTaskRequest {
  avatarId: string;
  text: string;
  voiceStyle?: string;
  videoLength?: string;
  resolution?: string;
  background?: string;
}

export interface TaskProgress {
  progress: number;
  status: string;
  stage?: string;
  estimatedTimeRemaining?: number;
}

@Injectable({
  providedIn: 'root'
})
export class GenerationTaskService {
  private taskUpdates = new Subject<GenerationTask>();
  private activeTasks = new Map<string, Observable<GenerationTask>>();

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

  getTaskProgress(id: string): Observable<ApiResponse<TaskProgress>> {
    return this.apiClient.get<TaskProgress>(`/generation-tasks/${id}/progress`);
  }

  // Получение обновлений задачи в реальном времени
  subscribeToTaskUpdates(id: string): Observable<GenerationTask> {
    if (!this.activeTasks.has(id)) {
      const taskObservable = interval(2000).pipe(
        startWith(0),
        switchMap(() => this.getTask(id).pipe(
          map(response => response.data),
          catchError(() => of(null))
        )),
        distinctUntilChanged((prev, curr) => 
          prev?.status === curr?.status && prev?.progress === curr?.progress
        ),
        takeUntil(this.taskUpdates.pipe(
          map(task => task.id === id && (task.status === 'completed' || task.status === 'failed'))
        )),
        shareReplay(1)
      );
      
      this.activeTasks.set(id, taskObservable);
    }
    
    return this.activeTasks.get(id)!;
  }

  // Получение списка задач с автоматическим обновлением
  getTasksWithAutoRefresh(refreshInterval = 10000): Observable<GenerationTask[]> {
    return merge(
      this.getTasks().pipe(map(response => response.data)),
      interval(refreshInterval).pipe(
        switchMap(() => this.getTasks().pipe(
          map(response => response.data),
          catchError(() => of([]))
        ))
      )
    ).pipe(
      distinctUntilChanged((prev, curr) => 
        JSON.stringify(prev) === JSON.stringify(curr)
      )
    );
  }

  // Получение активных задач (в процессе выполнения)
  getActiveTasks(): Observable<GenerationTask[]> {
    return this.getTasks().pipe(
      map(response => response.data.filter(task => 
        task.status === 'pending' || task.status === 'processing'
      ))
    );
  }

  // Получение завершенных задач
  getCompletedTasks(): Observable<GenerationTask[]> {
    return this.getTasks().pipe(
      map(response => response.data.filter(task => 
        task.status === 'completed'
      ))
    );
  }

  // Получение задач по аватару
  getTasksByAvatar(avatarId: string): Observable<GenerationTask[]> {
    return this.getTasks().pipe(
      map(response => response.data.filter(task => 
        task.avatarId === avatarId
      ))
    );
  }

  // Очистка подписок
  cleanupTaskSubscription(id: string): void {
    this.activeTasks.delete(id);
  }

  // Уведомление об обновлении задачи
  notifyTaskUpdate(task: GenerationTask): void {
    this.taskUpdates.next(task);
  }

  // Вспомогательные методы для статусов
  isTaskActive(task: GenerationTask): boolean {
    return task.status === 'pending' || task.status === 'processing';
  }

  isTaskCompleted(task: GenerationTask): boolean {
    return task.status === 'completed';
  }

  isTaskFailed(task: GenerationTask): boolean {
    return task.status === 'failed';
  }

  getStatusColor(task: GenerationTask): string {
    switch (task.status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  getStatusIcon(task: GenerationTask): string {
    switch (task.status) {
      case 'pending': return '⏳';
      case 'processing': return '⚡';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '❓';
    }
  }
}
