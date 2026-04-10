import { Injectable } from '@angular/core';
import { Observable, Subject, interval, merge, of } from 'rxjs';
import { map, switchMap, takeUntil, catchError, startWith, distinctUntilChanged, shareReplay } from 'rxjs/operators';
import { ApiClientService, ApiResponse } from '../../infrastructure/api/api-client.service';

export interface TaskLog {
  id: string;
  taskId: string;
  stage: TaskStage;
  message: string;
  createdAt: string;
}

export enum TaskStage {
  AudioPreprocessing = 'AudioPreprocessing',
  VoiceCloning = 'VoiceCloning',
  MediaAnalysis = 'MediaAnalysis',
  Lipsync = 'Lipsync',
  VideoRendering = 'VideoRendering',
  PostProcessing = 'PostProcessing',
  Completed = 'Completed',
  Failed = 'Failed',
  DataPreparation = 'DataPreparation',
  FaceAnalysis = 'FaceAnalysis',
  VoiceAnalysis = 'VoiceAnalysis',
  ModelTraining = 'ModelTraining',
  ModelValidation = 'ModelValidation'
}

export enum TaskStatus {
  Pending = 'Pending',
  Processing = 'Processing',
  Completed = 'Completed',
  Failed = 'Failed'
}

export interface GenerationTask {
  id: string;
  avatarId: string;
  userId: string;
  speechText: string;
  actionPrompt?: string;
  status: TaskStatus;
  stage: TaskStage;
  progress: number; // 0-1 decimal
  outputPath?: string;
  errorMessage?: string;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  taskLogs: TaskLog[];
  
  // Настройки
  voiceStyle?: string;
  videoLength?: string;
  resolution?: string;
  background?: string;
  
  // Дополнительные поля для фронтенда
  avatarName?: string;
  videoUrl?: string;
  audioUrl?: string;
}

export interface CreateGenerationTaskRequest {
  avatarId: string;
  speechText?: string;
  actionPrompt?: string;
  voiceStyle?: string;
  videoLength?: string;
  resolution?: string;
  background?: string;
}

export interface TaskProgress {
  taskId: string;
  status: string;
  progress: number; // 0-100 percentage
  currentStage: string;
  estimatedTimeRemaining?: string;
  logs?: Array<{
    timestamp: string;
    stage: string;
    message: string;
  }>;
}

@Injectable({
  providedIn: 'root'
})
export class GenerationTaskService {
  private taskUpdates = new Subject<GenerationTask>();
  private activeTasks = new Map<string, Observable<GenerationTask | null>>();

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
  subscribeToTaskUpdates(id: string): Observable<GenerationTask | null> {
    if (!this.activeTasks.has(id)) {
      const taskObservable = interval(2000).pipe(
        startWith(0),
        switchMap(() => this.getTask(id).pipe(
          map(response => response.data),
          catchError(() => of({} as GenerationTask))
        )),
        distinctUntilChanged((prev, curr) => 
          prev?.status === curr?.status && prev?.progress === curr?.progress
        ),
        takeUntil(this.taskUpdates.pipe(
          map(task => task.id === id && (task.status === TaskStatus.Completed || task.status === TaskStatus.Failed))
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
        task.status === TaskStatus.Pending || task.status === TaskStatus.Processing
      ))
    );
  }

  // Получение завершенных задач
  getCompletedTasks(): Observable<GenerationTask[]> {
    return this.getTasks().pipe(
      map(response => response.data.filter(task => 
        task.status === TaskStatus.Completed
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
    return task.status === TaskStatus.Pending || task.status === TaskStatus.Processing;
  }

  isTaskCompleted(task: GenerationTask): boolean {
    return task.status === TaskStatus.Completed;
  }

  isTaskFailed(task: GenerationTask): boolean {
    return task.status === TaskStatus.Failed;
  }

  getStatusColor(task: GenerationTask): string {
    switch (task.status) {
      case TaskStatus.Pending: return 'bg-yellow-100 text-yellow-800';
      case TaskStatus.Processing: return 'bg-blue-100 text-blue-800';
      case TaskStatus.Completed: return 'bg-green-100 text-green-800';
      case TaskStatus.Failed: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  getStatusIcon(task: GenerationTask): string {
    switch (task.status) {
      case TaskStatus.Pending: return '⏳';
      case TaskStatus.Processing: return '⚡';
      case TaskStatus.Completed: return '✅';
      case TaskStatus.Failed: return '❌';
      default: return '❓';
    }
  }
}
