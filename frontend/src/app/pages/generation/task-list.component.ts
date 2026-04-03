import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { GenerationTaskService, GenerationTask } from '../../../application/services/generation-task.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
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
      padding: 2rem;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }

    .page-title {
      font-size: 2rem;
      font-weight: 700;
      color: #1f2937;
      margin: 0;
    }

    .page-actions {
      display: flex;
      gap: 1rem;
    }

    .filters {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding: 1rem;
      background: #f9fafb;
      border-radius: 8px;
    }

    .filter-group {
      display: flex;
      gap: 0.5rem;
    }

    .filter-btn {
      padding: 0.5rem 1rem;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      background: white;
      color: #4b5563;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.2s;
    }

    .filter-btn:hover {
      border-color: #667eea;
      color: #667eea;
    }

    .filter-btn.active {
      background: #667eea;
      border-color: #667eea;
      color: white;
    }

    .search-box {
      flex: 0 0 300px;
    }

    .search-input {
      width: 100%;
      padding: 0.5rem 1rem;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 0.875rem;
    }

    .search-input:focus {
      outline: none;
      border-color: #667eea;
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

    .empty-state {
      text-align: center;
      padding: 4rem;
      background: #f9fafb;
      border-radius: 12px;
    }

    .empty-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    .empty-state h3 {
      font-size: 1.5rem;
      color: #1f2937;
      margin-bottom: 0.5rem;
    }

    .empty-state p {
      color: #6b7280;
      margin-bottom: 1.5rem;
    }

    .tasks-table {
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      margin-bottom: 2rem;
    }

    .table-header {
      display: grid;
      grid-template-columns: 1fr 2fr 1fr 1fr 1fr 1fr;
      padding: 1rem;
      background: #f3f4f6;
      font-weight: 600;
      color: #374151;
      border-bottom: 1px solid #e5e7eb;
    }

    .table-row {
      display: grid;
      grid-template-columns: 1fr 2fr 1fr 1fr 1fr 1fr;
      padding: 1rem;
      border-bottom: 1px solid #f3f4f6;
      transition: background-color 0.2s;
    }

    .table-row:hover {
      background: #f9fafb;
    }

    .table-cell {
      display: flex;
      align-items: center;
      padding: 0.5rem;
    }

    .avatar-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .avatar-icon {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 1rem;
    }

    .avatar-name {
      font-weight: 500;
      color: #1f2937;
    }

    .text-cell {
      flex-direction: column;
      align-items: flex-start;
    }

    .task-text {
      color: #4b5563;
      line-height: 1.4;
    }

    .status-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }

    .progress-container {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      width: 100%;
    }

    .progress-bar {
      flex: 1;
      height: 6px;
      background: #e5e7eb;
      border-radius: 3px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      transition: width 0.3s;
    }

    .progress-text {
      font-size: 0.75rem;
      color: #6b7280;
      min-width: 40px;
      text-align: right;
    }

    .date-info {
      display: flex;
      flex-direction: column;
    }

    .date {
      font-weight: 500;
      color: #1f2937;
    }

    .time {
      font-size: 0.75rem;
      color: #6b7280;
    }

    .action-buttons {
      display: flex;
      gap: 0.25rem;
    }

    .pagination {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .pagination-info {
      color: #6b7280;
      font-size: 0.875rem;
    }

    .pagination-controls {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .pagination-btn {
      padding: 0.5rem 1rem;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      background: white;
      color: #4b5563;
      cursor: pointer;
      transition: all 0.2s;
    }

    .pagination-btn:hover:not(:disabled) {
      border-color: #667eea;
      color: #667eea;
    }

    .pagination-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .pagination-page {
      font-weight: 500;
      color: #1f2937;
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-weight: 500;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      font-size: 0.875rem;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }

    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    .btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }

    .btn-outline {
      background: transparent;
      color: #667eea;
      border: 1px solid #667eea;
    }

    .btn-outline:hover {
      background: #667eea;
      color: white;
    }

    .btn-sm {
      padding: 0.25rem 0.5rem;
      font-size: 0.75rem;
    }

    .btn-icon {
      font-size: 1rem;
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
        padding: 1rem;
      }
      
      .page-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }
      
      .filters {
        flex-direction: column;
        gap: 1rem;
      }
      
      .search-box {
        flex: 1;
        width: 100%;
      }
      
      .table-header,
      .table-row {
        grid-template-columns: 1fr;
        gap: 0.5rem;
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
