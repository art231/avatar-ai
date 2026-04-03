import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { GenerationTaskService, GenerationTask } from '../../../application/services/generation-task.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-task-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="task-detail-container">
      <!-- Back Navigation -->
      <div class="back-navigation">
        <button class="btn btn-outline" routerLink="/generation/tasks">
          ← Back to Tasks
        </button>
      </div>

      <!-- Task Header -->
      <div class="task-header">
        <div class="task-title-section">
          <h1 class="task-title">Generation Task Details</h1>
          <div class="task-meta">
            <span class="task-id">ID: {{ task?.id }}</span>
            <span class="task-date" *ngIf="task">
              Created: {{ task.createdAt | date:'medium' }}
            </span>
          </div>
        </div>
        
        <div class="task-actions">
          <button 
            *ngIf="task && generationTaskService.isTaskActive(task)"
            class="btn btn-outline"
            (click)="cancelTask()">
            Cancel Task
          </button>
          
          <button 
            *ngIf="task && generationTaskService.isTaskCompleted(task) && task.videoUrl"
            class="btn btn-primary"
            (click)="downloadVideo()">
            Download Video
          </button>
          
          <button 
            *ngIf="task && generationTaskService.isTaskFailed(task)"
            class="btn btn-outline"
            (click)="retryTask()">
            Retry Task
          </button>
          
          <button 
            *ngIf="task"
            class="btn btn-outline"
            (click)="deleteTask()">
            Delete Task
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading task details...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="error" class="error-state">
        <div class="error-icon">❌</div>
        <h3>Error Loading Task</h3>
        <p>{{ error }}</p>
        <button class="btn btn-outline" routerLink="/generation/tasks">
          Back to Tasks
        </button>
      </div>

      <!-- Task Content -->
      <div *ngIf="task && !loading" class="task-content">
        <!-- Status Card -->
        <div class="status-card">
          <div class="status-header">
            <div class="status-icon">{{ generationTaskService.getStatusIcon(task) }}</div>
            <div class="status-info">
              <h3 class="status-title">Status</h3>
              <div class="status-badge" [class]="generationTaskService.getStatusColor(task)">
                {{ task.status | titlecase }}
              </div>
            </div>
          </div>
          
          <div class="progress-section" *ngIf="generationTaskService.isTaskActive(task)">
            <div class="progress-info">
              <span class="progress-label">Progress</span>
              <span class="progress-value">{{ getProgressPercentage() }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" [style.width.%]="getProgressPercentage()"></div>
            </div>
            <div class="stage-info" *ngIf="task.stage">
              <span class="stage-label">Current Stage:</span>
              <span class="stage-value">{{ task.stage }}</span>
            </div>
          </div>
          
          <div class="completion-info" *ngIf="task.completedAt">
            <span class="completion-label">Completed:</span>
            <span class="completion-value">{{ task.completedAt | date:'medium' }}</span>
          </div>
          
          <div class="error-info" *ngIf="task.errorMessage">
            <span class="error-label">Error:</span>
            <span class="error-value">{{ task.errorMessage }}</span>
          </div>
        </div>

        <!-- Task Details Grid -->
        <div class="details-grid">
          <!-- Avatar Info -->
          <div class="detail-card">
            <h3 class="detail-title">Avatar Information</h3>
            <div class="detail-content">
              <div class="detail-item">
                <span class="detail-label">Avatar Name:</span>
                <span class="detail-value">{{ task.avatarName }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Avatar ID:</span>
                <span class="detail-value">{{ task.avatarId }}</span>
              </div>
            </div>
          </div>

          <!-- Text Content -->
          <div class="detail-card">
            <h3 class="detail-title">Text Content</h3>
            <div class="detail-content">
              <div class="text-content">
                {{ task.speechText }}
              </div>
              <div class="text-stats">
                <div class="stat">
                  <span class="stat-label">Characters:</span>
                  <span class="stat-value">{{ task.speechText.length }}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">Words:</span>
                  <span class="stat-value">{{ countWords(task.speechText) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Generation Settings -->
          <div class="detail-card" *ngIf="task.voiceStyle || task.videoLength || task.resolution || task.background">
            <h3 class="detail-title">Generation Settings</h3>
            <div class="detail-content">
              <div class="settings-grid">
                <div class="setting-item" *ngIf="task.voiceStyle">
                  <span class="setting-label">Voice Style:</span>
                  <span class="setting-value">{{ task.voiceStyle }}</span>
                </div>
                <div class="setting-item" *ngIf="task.videoLength">
                  <span class="setting-label">Video Length:</span>
                  <span class="setting-value">{{ task.videoLength }}</span>
                </div>
                <div class="setting-item" *ngIf="task.resolution">
                  <span class="setting-label">Resolution:</span>
                  <span class="setting-value">{{ task.resolution }}</span>
                </div>
                <div class="setting-item" *ngIf="task.background">
                  <span class="setting-label">Background:</span>
                  <span class="setting-value">{{ task.background }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Media Preview -->
          <div class="detail-card media-card" *ngIf="task.videoUrl || task.audioUrl">
            <h3 class="detail-title">Generated Media</h3>
            <div class="detail-content">
              <div class="media-preview" *ngIf="task.videoUrl">
                <div class="video-preview">
                  <video 
                    *ngIf="task.videoUrl"
                    [src]="task.videoUrl"
                    controls
                    class="video-player">
                    Your browser does not support the video tag.
                  </video>
                  <div class="video-actions">
                    <button class="btn btn-sm btn-primary" (click)="downloadVideo()">
                      Download Video
                    </button>
                    <button class="btn btn-sm btn-outline" (click)="copyVideoUrl()">
                      Copy URL
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="audio-preview" *ngIf="task.audioUrl">
                <div class="audio-player">
                  <audio 
                    [src]="task.audioUrl"
                    controls
                    class="audio-element">
                    Your browser does not support the audio element.
                  </audio>
                  <div class="audio-actions">
                    <button class="btn btn-sm btn-outline" (click)="downloadAudio()">
                      Download Audio
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Real-time Updates -->
        <div class="updates-section" *ngIf="generationTaskService.isTaskActive(task)">
          <h3 class="updates-title">Real-time Updates</h3>
          <div class="updates-info">
            <p>This page will automatically update as the task progresses.</p>
            <p>Last updated: {{ lastUpdate | date:'mediumTime' }}</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .task-detail-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }

    .back-navigation {
      margin-bottom: 2rem;
    }

    .task-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .task-title-section {
      flex: 1;
    }

    .task-title {
      font-size: 2rem;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 0.5rem;
    }

    .task-meta {
      display: flex;
      gap: 1.5rem;
      color: #6b7280;
      font-size: 0.875rem;
    }

    .task-actions {
      display: flex;
      gap: 0.5rem;
    }

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 4rem;
      color: #6b7280;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #e5e7eb;
      border-top-color: #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-state {
      text-align: center;
      padding: 4rem;
      background: #fef2f2;
      border-radius: 12px;
      border: 1px solid #fecaca;
    }

    .error-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    .error-state h3 {
      font-size: 1.5rem;
      color: #dc2626;
      margin-bottom: 0.5rem;
    }

    .error-state p {
      color: #6b7280;
      margin-bottom: 1.5rem;
    }

    .task-content {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .status-card {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .status-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .status-icon {
      font-size: 3rem;
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .status-info {
      flex: 1;
    }

    .status-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 0.5rem;
    }

    .status-badge {
      display: inline-block;
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.875rem;
    }

    .progress-section {
      margin-top: 1.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid #e5e7eb;
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .progress-label {
      font-weight: 500;
      color: #4b5563;
    }

    .progress-value {
      font-weight: 600;
      color: #667eea;
    }

    .progress-bar {
      height: 8px;
      background: #e5e7eb;
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 1rem;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      transition: width 0.3s;
    }

    .stage-info {
      display: flex;
      gap: 0.5rem;
      font-size: 0.875rem;
      color: #6b7280;
    }

    .stage-label {
      font-weight: 500;
    }

    .completion-info,
    .error-info {
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid #e5e7eb;
      font-size: 0.875rem;
    }

    .completion-label,
    .error-label {
      font-weight: 500;
      color: #4b5563;
      margin-right: 0.5rem;
    }

    .completion-value {
      color: #059669;
    }

    .error-value {
      color: #dc2626;
    }

    .details-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 1.5rem;
    }

    .detail-card {
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .detail-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .detail-content {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .detail-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0;
    }

    .detail-label {
      font-weight: 500;
      color: #4b5563;
      font-size: 0.875rem;
    }

    .detail-value {
      color: #1f2937;
      font-weight: 500;
      font-size: 0.875rem;
    }

    .text-content {
      background: #f9fafb;
      padding: 1rem;
      border-radius: 8px;
      line-height: 1.6;
      color: #4b5563;
      max-height: 200px;
      overflow-y: auto;
    }

    .text-stats {
      display: flex;
      gap: 1.5rem;
      font-size: 0.875rem;
      color: #6b7280;
    }

    .stat {
      display: flex;
      gap: 0.25rem;
    }

    .stat-label {
      font-weight: 500;
    }

    .settings-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
    }

    .setting-item {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .setting-label {
      font-size: 0.75rem;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .setting-value {
      font-weight: 500;
      color: #1f2937;
    }

    .media-card {
      grid-column: 1 / -1;
    }

    .media-preview {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .video-preview,
    .audio-preview {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .video-player {
      width: 100%;
      max-height: 400px;
      border-radius: 8px;
      background: #000;
    }

    .audio-element {
      width: 100%;
    }

    .video-actions,
    .audio-actions {
      display: flex;
      gap: 0.5rem;
    }

    .updates-section {
      background: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 12px;
      padding: 1.5rem;
    }

    .updates-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #0369a1;
      margin-bottom: 0.5rem;
    }

    .updates-info {
      color: #0c4a6e;
      font-size: 0.875rem;
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      border: 1px solid transparent;
      font-weight: 500;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }

    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
    }

    .btn-primary:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }

    .btn-outline {
      background: transparent;
      color: #4b5563;
      border: 1px solid #d1d5db;
    }

    .btn-outline:hover {
      background: #f9fafb;
      border-color: #9ca3af;
    }

    .btn-sm {
      padding: 0.25rem 0.75rem;
      font-size: 0.75rem;
    }

    .status-badge.pending {
      background: #fef3c7;
      color: #92400e;
    }

    .status-badge.processing {
      background: #dbeafe;
      color: #1e40af;
    }

    .status-badge.completed {
      background: #d1fae5;
      color: #065f46;
    }

    .status-badge.failed {
      background: #fee2e2;
      color: #991b1b;
    }

    .status-badge.cancelled {
      background: #f3f4f6;
      color: #374151;
    }
  `]
})
export class TaskDetailComponent implements OnInit, OnDestroy {
  task: GenerationTask | null = null;
  loading = true;
  error: string | null = null;
  lastUpdate = new Date();
  private taskSubscription: Subscription | null = null;
  private routeSubscription: Subscription | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    public generationTaskService: GenerationTaskService
  ) {}

  ngOnInit(): void {
    this.routeSubscription = this.route.params.subscribe(params => {
      const taskId = params['id'];
      if (taskId) {
        this.loadTask(taskId);
        this.subscribeToTaskUpdates(taskId);
      }
    });
  }

  ngOnDestroy(): void {
    if (this.taskSubscription) {
      this.taskSubscription.unsubscribe();
    }
    if (this.routeSubscription) {
      this.routeSubscription.unsubscribe();
    }
  }

  private loadTask(taskId: string): void {
    this.loading = true;
    this.error = null;
    
    this.generationTaskService.getTask(taskId).subscribe({
      next: (response) => {
        this.task = response.data;
        this.loading = false;
        this.lastUpdate = new Date();
      },
      error: (err) => {
        this.error = err.message || 'Failed to load task details';
        this.loading = false;
      }
    });
  }

  private subscribeToTaskUpdates(taskId: string): void {
    this.taskSubscription = this.generationTaskService.subscribeToTaskUpdates(taskId).subscribe({
      next: (task) => {
        if (task) {
          this.task = task;
          this.lastUpdate = new Date();
        }
      },
      error: (err) => {
        console.error('Error in task updates subscription:', err);
      }
    });
  }

  countWords(text: string): number {
    if (!text) return 0;
    return text.trim().split(/\s+/).length;
  }

  cancelTask(): void {
    if (!this.task) return;
    
    if (confirm('Are you sure you want to cancel this task?')) {
      this.generationTaskService.cancelTask(this.task.id).subscribe({
        next: () => {
          // Task will be updated via subscription
        },
        error: (err) => {
          alert('Failed to cancel task: ' + (err.message || 'Unknown error'));
        }
      });
    }
  }

  retryTask(): void {
    if (!this.task) return;
    
    if (confirm('Are you sure you want to retry this task?')) {
      this.generationTaskService.retryTask(this.task.id).subscribe({
        next: () => {
          // Task will be updated via subscription
        },
        error: (err) => {
          alert('Failed to retry task: ' + (err.message || 'Unknown error'));
        }
      });
    }
  }

  deleteTask(): void {
    if (!this.task) return;
    
    if (confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      this.generationTaskService.deleteTask(this.task.id).subscribe({
        next: () => {
          this.router.navigate(['/generation/tasks']);
        },
        error: (err) => {
          alert('Failed to delete task: ' + (err.message || 'Unknown error'));
        }
      });
    }
  }

  downloadVideo(): void {
    if (!this.task?.videoUrl) return;
    
    const link = document.createElement('a');
    link.href = this.task.videoUrl;
    link.download = `avatar-video-${this.task.id}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  downloadAudio(): void {
    if (!this.task?.audioUrl) return;
    
    const link = document.createElement('a');
    link.href = this.task.audioUrl;
    link.download = `avatar-audio-${this.task.id}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  getProgressPercentage(): number {
    if (!this.task) return 0;
    // Progress is stored as decimal (0-1) in backend, convert to percentage (0-100)
    return Math.round(this.task.progress * 100);
  }

  copyVideoUrl(): void {
    if (!this.task?.videoUrl) return;
    
    navigator.clipboard.writeText(this.task.videoUrl)
      .then(() => {
        alert('Video URL copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy URL:', err);
        alert('Failed to copy URL to clipboard');
      });
  }
}
