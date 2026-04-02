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
              <h4 class="generation-title">{{ task.text.substring(0, 50) }}{{ task.text.length > 50 ? '...' : '' }}</h4>
              <p class="generation-details">
                {{ task.avatarName }} • 
                {{ task.settings?.videoLength || 'Medium' }} • 
                {{ task.settings?.resolution || '1080p' }}
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
      padding: 2rem;
    }
    
    .page-title {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .page-subtitle {
      font-size: 1.125rem;
      color: #6b7280;
      margin-bottom: 3rem;
    }
    
    .wizard-navigation {
      display: flex;
      justify-content: space-between;
      margin-bottom: 3rem;
      position: relative;
    }
    
    .wizard-navigation::before {
      content: '';
      position: absolute;
      top: 20px;
      left: 0;
      right: 0;
      height: 2px;
      background: #e5e7eb;
      z-index: 1;
    }
    
    .wizard-step-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      position: relative;
      z-index: 2;
      cursor: pointer;
    }
    
    .wizard-step-indicator .step-number {
      width: 40px;
      height: 40px;
      background: #e5e7eb;
      color: #6b7280;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      transition: all 0.3s;
    }
    
    .wizard-step-indicator.active .step-number {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    .wizard-step-indicator.completed .step-number {
      background: #10b981;
      color: white;
    }
    
    .wizard-step-indicator .step-title {
      font-size: 0.875rem;
      color: #6b7280;
      font-weight: 500;
    }
    
    .wizard-step-indicator.active .step-title {
      color: #1f2937;
      font-weight: 600;
    }
    
    .wizard-step {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      margin-bottom: 2rem;
    }
    
    .step-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    
    .step-header .step-number {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      font-weight: 700;
    }
    
    .step-header .step-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
      margin: 0;
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
    
    .empty-state h4 {
      font-size: 1.5rem;
      color: #1f2937;
      margin-bottom: 0.5rem;
    }
    
    .empty-state p {
      color: #6b7280;
      margin-bottom: 1.5rem;
    }
    
    .avatar-selection {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    
    .avatar-option {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      padding: 1.5rem;
      border: 2px solid #e5e7eb;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
    }
    
    .avatar-option:hover {
      border-color: #667eea;
      transform: translateY(-2px);
    }
    
    .avatar-option.selected {
      border-color: #667eea;
      background: #f0f4ff;
    }
    
    .avatar-preview {
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
    
    .avatar-name {
      font-size: 1rem;
      font-weight: 600;
      color: #1f2937;
      margin: 0;
    }
    
    .avatar-status {
      font-size: 0.75rem;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-weight: 500;
    }
    
    .avatar-status.active {
      background: #d1fae5;
      color: #065f46;
    }
    
    .avatar-status.training {
      background: #fef3c7;
      color: #92400e;
    }
    
    .avatar-status.failed {
      background: #fee2e2;
      color: #991b1b;
    }
    
    .step-content {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }
    
    .step-actions {
      display: flex;
      gap: 1rem;
      justify-content: flex-end;
      margin-top: 2rem;
    }
    
    .text-input {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .text-area {
      width: 100%;
      padding: 1rem;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      font-size: 1rem;
      font-family: inherit;
      resize: vertical;
      transition: border-color 0.3s;
    }
    
    .text-area:focus {
      outline: none;
      border-color: #667eea;
    }
    
    .text-stats {
      display: flex;
      gap: 1.5rem;
      font-size: 0.875rem;
      color: #6b7280;
    }
    
    .stat {
      font-weight: 500;
    }
    
    .settings-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
    }
    
    .setting {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .setting-label {
      font-size: 0.875rem;
      font-weight: 600;
      color: #1f2937;
    }
    
    .setting-select {
      padding: 0.75rem;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      font-size: 1rem;
      background: white;
      cursor: pointer;
      transition: border-color 0.3s;
    }
    
    .setting-select:focus {
      outline: none;
      border-color: #667eea;
    }
    
    .preview-section {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2rem;
    }
    
    .preview-summary {
      width: 100%;
      background: #f9fafb;
      border-radius: 12px;
      padding: 2rem;
    }
    
    .preview-summary h4 {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 1.5rem;
    }
    
    .summary-details {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }
    
    .summary-item {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }
    
    .summary-label {
      font-size: 0.875rem;
      color: #6b7280;
    }
    
    .summary-value {
      font-weight: 600;
      color: #1f2937;
    }
    
    .generation-actions {
      display: flex;
      gap: 1rem;
    }
    
    .recent-generations {
      background: #f9fafb;
      border-radius: 12px;
      padding: 2rem;
      margin-top: 3rem;
    }
    
    .section-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: #1f2937;
    }
    
    .generations-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .generation-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .generation-info {
      flex: 1;
    }
    
    .generation-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
      color: #1f2937;
    }
    
    .generation-details {
      font-size: 0.875rem;
      color: #6b7280;
      margin-bottom: 0.25rem;
    }
    
    .generation-time {
      font-size: 0.75rem;
      color: #9ca3af;
      margin: 0;
    }
    
    .generation-actions {
      display: flex;
      gap: 0.5rem;
    }
    
    .btn {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.3s;
      font-size: 1rem;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
    
    .btn-outline {
      background: transparent;
      color: #667eea;
      border: 2px solid #667eea;
    }
    
    .btn-outline:hover {
      background: #667eea;
      color: white;
    }
    
    .btn-outline:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      background: transparent;
      color: #667eea;
    }
    
    .btn-lg {
      padding: 1rem 2rem;
      font-size: 1.125rem;
    }
    
    .btn-sm {
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
    }
    
    .btn-icon {
      font-size: 1.25rem;
    }
    
    @media (max-width: 768px) {
      .wizard-navigation {
        flex-direction: column;
        gap: 1rem;
      }
      
      .wizard-navigation::before {
        display: none;
      }
      
      .avatar-selection {
        grid-template-columns: 1fr;
      }
      
      .settings-grid {
        grid-template-columns: 1fr;
      }
      
      .generation-item {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }
      
      .generation-actions {
        width: 100%;
        justify-content: center;
      }
      
      .page-title {
        font-size: 2rem;
      }
      
      .step-actions {
        flex-direction: column;
      }
      
      .step-actions .btn {
        width: 100%;
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
      text: this.generationText,
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
    this.generationText = task.text;
    
    // Обновляем настройки из задачи, если они есть
    if (task.settings) {
      this.settings = {
        voiceStyle: task.settings.voiceStyle || this.settings.voiceStyle,
        videoLength: task.settings.videoLength || this.settings.videoLength,
        resolution: task.settings.resolution || this.settings.resolution,
        background: task.settings.background || this.settings.background
      };
    }
    
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
