import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { GenerationTaskService, GenerationTask } from '../../../application/services/generation-task.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="task-list-container">
      <div class="page-header">
        <h1 class="page-title">Generation Tasks</h1>
        <div class="page-actions">
          <a routerLink="/generation" class="btn btn-primary">
            <span class="btn-icon">➕</span>
            New Generation
          </a>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters">
        <div class="filter-group">
          <button 
            *ngFor="let filter of statusFilters" 
            class="filter-btn"
            [class.active]="activeFilter === filter.value"
            (click)="setFilter(filter.value)">
            {{ filter.label }}
          </button>
        </div>
        <div class="search-box">
          <input 
            type="text" 
            placeholder="Search tasks..." 
            class="search-input"
            [(ngModel)]="searchQuery"
            (input)="onSearch()">
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading tasks...</p>
      </div>

      <!-- Empty State -->
      <div *ngIf="!loading && filteredTasks.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No tasks found</h3>
        <p *ngIf="activeFilter === 'all'">Start by creating your first generation task</p>
        <p *ngIf="activeFilter !== 'all'">No tasks match your current filter</p>
        <a routerLink="/generation" class="btn btn-primary">
          Create Generation
        </a>
      </div>

      <!-- Tasks Table -->
      <div *ngIf="!loading && filteredTasks.length > 0" class="tasks-table">
        <div class="table-header">
          <div class="table-cell">Avatar</div>
          <div class="table-cell">Text</div>
          <div class="table-cell">Status</div>
          <div class="table-cell">Progress</div>
          <div class="table-cell">Created</div>
          <div class="table-cell">Actions</div>
        </div>
        
        <div *ngFor="let task of filteredTasks" class="table-row">
          <div class="table-cell">
            <div class="avatar-info">
              <div class="avatar-icon">👤</div>
              <span class="avatar-name">{{ task.avatarName }}</span>
            </div>
          </div>
          
          <div class="table-cell text-cell">
            <div class="task-text">{{ task.speechText.substring(0, 100) }}{{ task.speechText.length > 100 ? '...' : '' }}</div>
          </div>
          
          <div class="table-cell">
            <span class="status-badge" [class]="generationTaskService.getStatusColor(task)">
              {{ generationTaskService.getStatusIcon(task) }} {{ task.status }}
            </span>
          </div>
          
          <div class="table-cell">
            <div *ngIf="generationTaskService.isTaskActive(task)" class="progress-container">
              <div class="progress-bar">
                <div class="progress-fill" [style.width.%]="task.progress * 100"></div>
              </div>
              <span class="progress-text">{{ (task.progress * 100).toFixed(0) }}%</span>
            </div>
            <div *ngIf="!generationTaskService.isTaskActive(task)" class="progress-text">
              {{ (task.progress * 100).toFixed(0) }}%
            </div>
          </div>
          
          <div class="table-cell">
            <div class="date-info">
              <div class="date">{{ task.createdAt | date:'shortDate' }}</div>
              <div class="time">{{ task.createdAt | date:'shortTime' }}</div>
            </div>
          </div>
          
          <div class="table-cell">
            <div class="action-buttons">
              <button 
                class="btn btn-sm btn-outline"
                [routerLink]="['/generation/tasks', task.id]">
                View
              </button>
              
              <button 
                *ngIf="generationTaskService.isTaskActive(task)"
                class="btn btn-sm btn-outline"
                (click)="cancelTask(task.id)">
                Cancel
              </button>
              
              <button 
                *ngIf="generationTaskService.isTaskCompleted(task) && task.videoUrl"
                class="btn btn-sm btn-primary"
                (click)="downloadVideo(task)">
                Download
              </button>
              
              <button 
                *ngIf="generationTaskService.isTaskFailed(task)"
                class="btn btn-sm btn-outline"
                (click)="retryTask(task.id)">
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div *ngIf="filteredTasks.length > 0" class="pagination">
        <div class="pagination-info">
          Showing {{ filteredTasks.length }} of {{ allTasks.length }} tasks
        </div>
        <div class="pagination-controls">
          <button 
            class="pagination-btn"
            [disabled]="currentPage === 1"
            (click)="previousPage()">
            Previous
          </button>
          <span class="pagination-page">Page {{ currentPage }}</span>
          <button 
            class="pagination-btn"
            [disabled]="currentPage * pageSize >= filteredTasks.length"
            (click)="nextPage()">
            Next
          </button>
        </div>
      </div>
    </div>
  `,
  styles: `
    .task-list-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: var(--spacing-2xl);
    }

    .filters {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-xl);
      padding: var(--spacing-md);
      background: var(--color-bg-secondary);
      border-radius: var(--radius-lg);
    }

    .filter-group {
      display: flex;
      gap: var(--spacing-sm);
    }

    .filter-btn {
      padding: var(--spacing-sm) var(--spacing-md);
      border: 1px solid var(--color-border-dark);
      border-radius: var(--radius-md);
      background: var(--color-bg-primary);
      color: var(--color-text-secondary);
      font-size: var(--font-size-sm);
      cursor: pointer;
      transition: all 0.2s;
    }

    .filter-btn:hover {
      border-color: var(--color-primary);
      color: var(--color-primary);
    }

    .filter-btn.active {
      background: var(--gradient-primary);
      border-color: var(--color-primary);
      color: var(--color-text-white);
    }

    .search-box {
      flex: 0 0 300px;
    }

    .search-input {
      width: 100%;
      padding: var(--spacing-sm) var(--spacing-md);
      border: 1px solid var(--color-border-dark);
      border-radius: var(--radius-md);
      font-size: var(--font-size-sm);
      background: var(--color-bg-primary);
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }

    .avatar-info {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
    }

    .avatar-icon {
      width: 32px;
      height: 32px;
      background: var(--gradient-primary);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-text-white);
      font-size: var(--font-size-base);
    }

    .avatar-name {
      font-weight: var(--font-weight-medium);
      color: var(--color-text-primary);
    }

    .text-cell {
      flex-direction: column;
      align-items: flex-start;
    }

    .task-text {
      color: var(--color-text-secondary);
      line-height: 1.4;
    }

    .date-info {
      display: flex;
      flex-direction: column;
    }

    .date {
      font-weight: var(--font-weight-medium);
      color: var(--color-text-primary);
    }

    .time {
      font-size: var(--font-size-xs);
      color: var(--color-text-secondary);
    }

    .action-buttons {
      display: flex;
      gap: var(--spacing-xs);
    }

    .pagination {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--spacing-md);
      background: var(--color-bg-primary);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
    }

    .pagination-info {
      color: var(--color-text-secondary);
      font-size: var(--font-size-sm);
    }

    .pagination-controls {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
    }

    .pagination-btn {
      padding: var(--spacing-sm) var(--spacing-md);
      border: 1px solid var(--color-border-dark);
      border-radius: var(--radius-md);
      background: var(--color-bg-primary);
      color: var(--color-text-secondary);
      cursor: pointer;
      transition: all 0.2s;
    }

    .pagination-btn:hover:not(:disabled) {
      border-color: var(--color-primary);
      color: var(--color-primary);
    }

    .pagination-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .pagination-page {
      font-weight: var(--font-weight-medium);
      color: var(--color-text-primary);
    }

    .btn-icon {
      font-size: var(--font-size-base);
    }

    @media (max-width: 1024px) {
      .table-header,
      .table-row {
        grid-template-columns: 1fr 1fr 1fr;
      }
      
      .table-cell:nth-child(4),
      .table-cell:nth-child(5),
      .table-cell:nth-child(6) {
        display: none;
      }
    }

    @media (max-width: 768px) {
      .task-list-container {
        padding: var(--spacing-md);
      }
      
      .page-header {
        flex-direction: column;
        gap: var(--spacing-md);
        text-align: center;
      }
      
      .filters {
        flex-direction: column;
        gap: var(--spacing-md);
      }
      
      .search-box {
        flex: 1;
        width: 100%;
      }
      
      .table-header,
      .table-row {
        grid-template-columns: 1fr;
        gap: var(--spacing-sm);
      }
      
      .table-cell {
        display: block;
      }
      
      .action-buttons {
        justify-content: center;
      }
    }
  `
})
export class TaskListComponent implements OnInit, OnDestroy {
  allTasks: GenerationTask[] = [];
  filteredTasks: GenerationTask[] = [];
  loading = true;
  searchQuery = '';
  activeFilter = 'all';
  currentPage = 1;
  pageSize = 10;
  
  statusFilters = [
    { value: 'all', label: 'All Tasks' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' }
  ];
  
  private subscription?: Subscription;

  constructor(public generationTaskService: GenerationTaskService) {}

  ngOnInit(): void {
    this.loadTasks();
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  loadTasks(): void {
    this.loading = true;
    this.subscription = this.generationTaskService.getTasksWithAutoRefresh().subscribe({
      next: (tasks) => {
        this.allTasks = tasks;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading tasks:', error);
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.allTasks];

    // Apply status filter
    if (this.activeFilter !== 'all') {
      filtered = filtered.filter(task => {
        if (this.activeFilter === 'active') {
          return this.generationTaskService.isTaskActive(task);
        } else if (this.activeFilter === 'completed') {
          return this.generationTaskService.isTaskCompleted(task);
        } else if (this.activeFilter === 'failed') {
          return this.generationTaskService.isTaskFailed(task);
        }
        return true;
      });
    }

    // Apply search filter
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(task =>
        (task.speechText?.toLowerCase() || '').includes(query) ||
        (task.avatarName?.toLowerCase() || '').includes(query) ||
        task.status.toLowerCase().includes(query)
      );
    }

    this.filteredTasks = filtered;
  }

  setFilter(filter: string): void {
    this.activeFilter = filter;
    this.applyFilters();
    this.currentPage = 1;
  }

  onSearch(): void {
    this.applyFilters();
    this.currentPage = 1;
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  nextPage(): void {
    if (this.currentPage * this.pageSize < this.filteredTasks.length) {
      this.currentPage++;
    }
  }

  cancelTask(taskId: string): void {
    if (confirm('Are you sure you want to cancel this task?')) {
      this.generationTaskService.cancelTask(taskId).subscribe({
        next: () => {
          console.log('Task cancelled successfully');
          this.loadTasks();
        },
        error: (error) => {
          console.error('Error cancelling task:', error);
          alert('Failed to cancel task');
        }
      });
    }
  }

  retryTask(taskId: string): void {
    this.generationTaskService.retryTask(taskId).subscribe({
      next: () => {
        console.log('Task retry initiated');
        this.loadTasks();
      },
      error: (error) => {
        console.error('Error retrying task:', error);
        alert('Failed to retry task');
      }
    });
  }

  downloadVideo(task: GenerationTask): void {
    if (task.videoUrl) {
      window.open(task.videoUrl, '_blank');
    }
  }
}
