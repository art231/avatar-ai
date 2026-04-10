import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AvatarService, Avatar } from '../../../application/services/avatar.service';
import { GenerationTaskService, GenerationTask, CreateGenerationTaskRequest } from '../../../application/services/generation-task.service';
import { Subscription, Observable, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';

interface GenerationSettings {
  voiceStyle: string;
  videoLength: string;
  resolution: string;
  background: string;
}

interface WizardStep {
  title: string;
  active: boolean;
  completed: boolean;
}

interface TextStats {
  characters: number;
  words: number;
  duration: number;
}

@Component({
  selector: 'app-generation',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="generation-container">
      <h1 class="page-title">Generate Content</h1>
      <p class="page-subtitle">Create videos with your AI avatar</p>
      
      <!-- Wizard Navigation -->
      <div class="wizard-navigation">
        <div *ngFor="let step of wizardSteps; let i = index" 
             class="wizard-step-indicator"
             [class.active]="step.active"
             [class.completed]="step.completed"
             (click)="goToStep(i)">
          <div class="step-number">{{ i + 1 }}</div>
          <div class="step-title">{{ step.title }}</div>
        </div>
      </div>
      
      <!-- Step 1: Select Avatar -->
      <div class="wizard-step" *ngIf="currentStep === 0">
        <div class="step-header">
          <div class="step-number">1</div>
          <h3 class="step-title">Select Avatar</h3>
        </div>
        <div class="step-content">
          <div *ngIf="loadingAvatars" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading avatars...</p>
          </div>
          
          <div *ngIf="!loadingAvatars && avatars.length === 0" class="empty-state">
            <div class="empty-icon">👤</div>
            <h4>No avatars available</h4>
            <p>Create an avatar first to start generating content</p>
            <a routerLink="/avatars/create" class="btn btn-primary">
              Create Avatar
            </a>
          </div>
          
          <div *ngIf="!loadingAvatars && avatars.length > 0" class="avatar-selection">
            <div *ngFor="let avatar of avatars" 
                 class="avatar-option"
                 [class.selected]="selectedAvatar?.id === avatar.id"
                 (click)="selectAvatar(avatar)">
              <div class="avatar-preview">
                <span *ngIf="avatar.status === 'active'">👤</span>
                <span *ngIf="avatar.status === 'training'">⏳</span>
                <span *ngIf="avatar.status === 'failed'">❌</span>
              </div>
              <h4 class="avatar-name">{{ avatar.name }}</h4>
              <div class="avatar-status" [class]="avatar.status">
                {{ avatar.status === 'active' ? 'Ready' : 
                   avatar.status === 'training' ? 'Training' : 'Failed' }}
              </div>
            </div>
          </div>
          
          <div class="step-actions">
            <button class="btn btn-outline" (click)="goToStep(1)" [disabled]="!selectedAvatar">
              Next: Enter Text
            </button>
          </div>
        </div>
      </div>
      
      <!-- Step 2: Enter Text -->
      <div class="wizard-step" *ngIf="currentStep === 1">
        <div class="step-header">
          <div class="step-number">2</div>
          <h3 class="step-title">Enter Text</h3>
        </div>
        <div class="step-content">
          <div class="text-input">
            <textarea 
              class="text-area" 
              placeholder="Enter the text you want your avatar to speak..."
              rows="6"
              [(ngModel)]="generationText"
              (input)="updateTextStats()"
            ></textarea>
            <div class="text-stats">
              <span class="stat">Characters: {{ textStats.characters }}</span>
              <span class="stat">Words: {{ textStats.words }}</span>
              <span class="stat">Estimated duration: {{ textStats.duration }} seconds</span>
            </div>
          </div>
          
          <div class="step-actions">
            <button class="btn btn-outline" (click)="goToStep(0)">
              Back: Select Avatar
            </button>
            <button class="btn btn-primary" (click)="goToStep(2)" [disabled]="!generationText.trim()">
              Next: Configure Settings
            </button>
          </div>
        </div>
      </div>
      
      <!-- Step 3: Configure Settings -->
      <div class="wizard-step" *ngIf="currentStep === 2">
        <div class="step-header">
          <div class="step-number">3</div>
          <h3 class="step-title">Configure Settings</h3>
        </div>
        <div class="step-content">
          <div class="settings-grid">
            <div class="setting">
              <label class="setting-label">Voice Style</label>
              <select class="setting-select" [(ngModel)]="settings.voiceStyle">
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="enthusiastic">Enthusiastic</option>
                <option value="calm">Calm</option>
              </select>
            </div>
            <div class="setting">
              <label class="setting-label">Video Length</label>
              <select class="setting-select" [(ngModel)]="settings.videoLength">
                <option value="short">Short (10-30 seconds)</option>
                <option value="medium">Medium (30-60 seconds)</option>
                <option value="long">Long (1-2 minutes)</option>
              </select>
            </div>
            <div class="setting">
              <label class="setting-label">Resolution</label>
              <select class="setting-select" [(ngModel)]="settings.resolution">
                <option value="720p">720p HD</option>
                <option value="1080p">1080p Full HD</option>
                <option value="4k">4K Ultra HD</option>
              </select>
            </div>
            <div class="setting">
              <label class="setting-label">Background</label>
              <select class="setting-select" [(ngModel)]="settings.background">
                <option value="studio">Studio Background</option>
                <option value="office">Office Environment</option>
                <option value="outdoor">Outdoor Scene</option>
                <option value="custom">Custom Background</option>
              </select>
            </div>
          </div>
          
          <div class="step-actions">
            <button class="btn btn-outline" (click)="goToStep(1)">
              Back: Enter Text
            </button>
            <button class="btn btn-primary" (click)="goToStep(3)">
              Next: Preview & Generate
            </button>
          </div>
        </div>
      </div>
      
      <!-- Step 4: Preview & Generate -->
      <div class="wizard-step" *ngIf="currentStep === 3">
        <div class="step-header">
          <div class="step-number">4</div>
          <h3 class="step-title">Preview & Generate</h3>
        </div>
        <div class="step-content">
          <div class="preview-section">
            <div class="preview-summary">
              <h4>Generation Summary</h4>
              <div class="summary-details">
                <div class="summary-item">
                  <span class="summary-label">Avatar:</span>
                  <span class="summary-value">{{ selectedAvatar?.name }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">Text Length:</span>
                  <span class="summary-value">{{ textStats.words }} words ({{ textStats.duration }}s)</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">Voice Style:</span>
                  <span class="summary-value">{{ settings.voiceStyle }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">Resolution:</span>
                  <span class="summary-value">{{ settings.resolution }}</span>
                </div>
              </div>
            </div>
            
            <div class="generation-actions">
              <button class="btn btn-outline" (click)="goToStep(2)">
                Back: Configure Settings
              </button>
              <button class="btn btn-primary btn-lg" (click)="generateVideo()" [disabled]="isGenerating">
                <span class="btn-icon">⚡</span>
                {{ isGenerating ? 'Generating...' : 'Generate Video' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Generations -->
      <div class="recent-generations" *ngIf="recentTasks.length > 0">
        <h3 class="section-title">Recent Generations</h3>
        <div class="generations-list">
          <div *ngFor="let task of recentTasks" class="generation-item">
            <div class="generation-info">
              <h4 class="generation-title">{{ task.speechText.substring(0, 50) }}{{ task.speechText.length > 50 ? '...' : '' }}</h4>
              <p class="generation-details">
                {{ task.avatarName }} • 
                {{ task.videoLength || 'Medium' }} • 
                {{ task.resolution || '1080p' }}
              </p>
              <p class="generation-time">
                <span [class]="generationTaskService.getStatusColor(task)">
                  {{ generationTaskService.getStatusIcon(task) }} {{ task.status }}
                </span>
                • {{ task.createdAt | date:'short' }}
              </p>
            </div>
            <div class="generation-actions">
              <button *ngIf="task.videoUrl" class="btn btn-sm btn-outline" (click)="downloadVideo(task)">
                Download
              </button>
              <button *ngIf="generationTaskService.isTaskCompleted(task)" 
                      class="btn btn-sm btn-primary"
                      (click)="regenerateTask(task)">
                Regenerate
              </button>
              <button *ngIf="generationTaskService.isTaskFailed(task)" 
                      class="btn btn-sm btn-outline"
                      (click)="retryTask(task)">
                Retry
              </button>
              <button class="btn btn-sm btn-outline" [routerLink]="['/generation/tasks', task.id]">
                Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .generation-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: var(--spacing-xl);
    }
    
    .btn-icon {
      font-size: 1.25rem;
      margin-right: var(--spacing-sm);
    }
    
    @media (max-width: 768px) {
      .generation-container {
        padding: var(--spacing-md);
      }
      
      .wizard-navigation {
        flex-direction: column;
        gap: var(--spacing-lg);
      }
      
      .wizard-navigation::before {
        display: none;
      }
      
      .generation-item {
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: flex-start;
      }
      
      .generation-actions {
        width: 100%;
        justify-content: flex-start;
      }
    }
  `]
})
export class GenerationComponent implements OnInit, OnDestroy {
  avatars: Avatar[] = [];
  selectedAvatar: Avatar | null = null;
  loadingAvatars = true;
  generationText = '';
  textStats: TextStats = { characters: 0, words: 0, duration: 0 };
  settings: GenerationSettings = {
    voiceStyle: 'professional',
    videoLength: 'medium',
    resolution: '1080p',
    background: 'studio'
  };
  recentTasks: GenerationTask[] = [];
  isGenerating = false;
  
  wizardSteps: WizardStep[] = [
    { title: 'Select Avatar', active: true, completed: false },
    { title: 'Enter Text', active: false, completed: false },
    { title: 'Configure Settings', active: false, completed: false },
    { title: 'Preview & Generate', active: false, completed: false }
  ];
  currentStep = 0;
  
  private subscriptions: Subscription[] = [];

  constructor(
    private avatarService: AvatarService,
    public generationTaskService: GenerationTaskService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadAvatars();
    this.loadRecentTasks();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  private loadAvatars(): void {
    this.loadingAvatars = true;
    const sub = this.avatarService.getAvatars().subscribe({
      next: (response: any) => {
        this.avatars = response.data;
        this.loadingAvatars = false;
      },
      error: (error: any) => {
        console.error('Failed to load avatars:', error);
        this.loadingAvatars = false;
      }
    });
    this.subscriptions.push(sub);
  }

  private loadRecentTasks(): void {
    const sub = this.generationTaskService.getTasks().subscribe({
      next: (response: any) => {
        this.recentTasks = response.data.slice(0, 5); // Берем первые 5 задач
      },
      error: (error: any) => {
        console.error('Failed to load recent tasks:', error);
      }
    });
    this.subscriptions.push(sub);
  }

  selectAvatar(avatar: Avatar): void {
    this.selectedAvatar = avatar;
  }

  goToStep(stepIndex: number): void {
    if (stepIndex < 0 || stepIndex >= this.wizardSteps.length) return;
    
    // Update wizard steps
    this.wizardSteps.forEach((step, index) => {
      step.active = index === stepIndex;
      step.completed = index < stepIndex;
    });
    
    this.currentStep = stepIndex;
  }

  updateTextStats(): void {
    const text = this.generationText.trim();
    this.textStats.characters = text.length;
    this.textStats.words = text ? text.split(/\s+/).length : 0;
    // Estimate duration: ~150 words per minute = 2.5 words per second
    this.textStats.duration = Math.ceil(this.textStats.words / 2.5);
  }

  generateVideo(): void {
    if (!this.selectedAvatar || !this.generationText.trim() || this.isGenerating) {
      return;
    }

    this.isGenerating = true;

    const request: CreateGenerationTaskRequest = {
      avatarId: this.selectedAvatar.id,
      speechText: this.generationText,
      voiceStyle: this.settings.voiceStyle,
      videoLength: this.settings.videoLength,
      resolution: this.settings.resolution,
      background: this.settings.background
    };

    const sub = this.generationTaskService.createTask(request).subscribe({
      next: (response: any) => {
        this.isGenerating = false;
        alert('Generation task created successfully! You can track its progress in the tasks list.');
        this.router.navigate(['/generation/tasks', response.data.id]);
      },
      error: (error: any) => {
        this.isGenerating = false;
        alert('Failed to create generation task: ' + (error.message || 'Unknown error'));
      }
    });
    this.subscriptions.push(sub);
  }

  downloadVideo(task: GenerationTask): void {
    if (!task.videoUrl) return;
    
    const link = document.createElement('a');
    link.href = task.videoUrl;
    link.download = `avatar-video-${task.id}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  regenerateTask(task: GenerationTask): void {
    if (!task.avatarId) return;
    
    this.selectedAvatar = this.avatars.find(a => a.id === task.avatarId) || null;
    this.generationText = task.speechText;
    
    // Обновляем настройки из задачи
    this.settings = {
      voiceStyle: task.voiceStyle || this.settings.voiceStyle,
      videoLength: task.videoLength || this.settings.videoLength,
      resolution: task.resolution || this.settings.resolution,
      background: task.background || this.settings.background
    };
    
    this.updateTextStats();
    this.goToStep(3);
  }

  retryTask(task: GenerationTask): void {
    if (confirm('Are you sure you want to retry this task?')) {
      const sub = this.generationTaskService.retryTask(task.id).subscribe({
        next: () => {
          alert('Task retry initiated. You can track its progress in the tasks list.');
          this.loadRecentTasks();
        },
        error: (error: any) => {
          alert('Failed to retry task: ' + (error.message || 'Unknown error'));
        }
      });
      this.subscriptions.push(sub);
    }
  }
}
