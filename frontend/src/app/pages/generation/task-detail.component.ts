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
      <div class="back-navigation">
        <button class="btn btn-outline" routerLink="/generation/tasks">
          ← Back to Tasks
        </button>
      </div>

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
      </div>

      <div *ngIf="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading task details...</p>
      </div>

      <div *ngIf="error" class="error-state">
        <div class="error-icon">❌</div>
        <h3>Error Loading Task</h3>
        <p>{{ error }}</p>
        <button class="btn btn-outline" routerLink="/generation/tasks">
          Back to Tasks
        </button>
      </div>

      <div *ngIf="task && !loading" class="task-content">
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
        </div>
      </div>
    </div>
  `,
  styles: [`
    .task-detail-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }

    .back-navigation {
      margin-bottom: 1rem;
    }

    .task-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .task-title-section {
      flex: 1;
    }

    .task-title {
      font-size: 1.5rem;
      font-weight: bold;
      color: #111827;
      margin-bottom: 0.5rem;
    }

    .task-meta {
      display: flex;
      gap: 1rem;
      color: #6b7280;
      font-size: 0.875rem;
    }

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      color: #6b7280;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #e5e7eb;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-state {
      text-align: center;
      padding: 2rem;
      background: #fef2f2;
      border-radius: 0.75rem;
      border: 1px solid #fecaca;
    }

    .error-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    .error-state h3 {
      font-size: 1.25rem;
      color: #dc2626;
      margin-bottom: 0.5rem;
    }

    .error-state p {
      color: #6b7280;
      margin-bottom: 1rem;
    }

    .task-content {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .status-card {
      background: white;
      border-radius: 0.75rem;
      padding: 1rem;
      box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }

    .status-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .status-icon {
      font-size: 3rem;
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
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
      font-size: 1.125rem;
      font-weight: 600;
      color: #111827;
      margin-bottom: 0.5rem;
    }

    .status-badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.875rem;
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
  }

  getProgressPercentage(): number {
    if (!this.task) return 0;
    // Progress is stored as decimal (0-1) in backend, convert to percentage (0-100)
    return Math.round(this.task.progress * 100);
}