import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AvatarService, Avatar } from '../../../application/services/avatar.service';
import { catchError, finalize } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-avatar-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="avatar-detail-container">
      <div class="back-button">
        <button class="btn btn-secondary" routerLink="/avatars">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Назад к аватарам
        </button>
      </div>

      <div class="loading-container" *ngIf="isLoading">
        <div class="loading-spinner"></div>
        <p>Загрузка данных аватара...</p>
      </div>

      <div class="error-container" *ngIf="error">
        <div class="alert alert-error">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div>
            <h4>Ошибка загрузки</h4>
            <p>{{error}}</p>
          </div>
          <button class="btn btn-secondary" (click)="loadAvatar()">Повторить</button>
        </div>
      </div>

      <div class="not-found" *ngIf="!isLoading && !error && !avatar">
        <div class="not-found-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        </div>
        <h3>Аватар не найден</h3>
        <p>Запрошенный аватар не существует или был удален</p>
        <button class="btn btn-primary" routerLink="/avatars">Вернуться к аватарам</button>
      </div>

      <div class="avatar-detail" *ngIf="!isLoading && !error && avatar">
        <div class="avatar-header">
          <div class="avatar-preview">
            <div class="avatar-image-large">
              <div class="avatar-placeholder-large">{{getAvatarEmoji(avatar)}}</div>
            </div>
            <div class="avatar-status-large" [class]="'status-' + avatar.status">
              {{getStatusText(avatar.status)}}
            </div>
          </div>
          
          <div class="avatar-info-header">
            <div class="avatar-title-section">
              <h1 class="avatar-name">{{avatar.name}}</h1>
              <p class="avatar-description">{{avatar.description || 'Без описания'}}</p>
            </div>
            
            <div class="avatar-actions-header">
              <button class="btn btn-primary" (click)="startTraining()" *ngIf="avatar.status !== 'training'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                Начать обучение
              </button>
              
              <button class="btn btn-secondary" (click)="onEditAvatar()">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Редактировать
              </button>
              
              <button class="btn btn-danger" (click)="onDeleteAvatar()">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  <line x1="10" y1="11" x2="10" y2="17"></line>
                  <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
                Удалить
              </button>
            </div>
          </div>
        </div>

        <div class="avatar-stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
                <line x1="7" y1="2" x2="7" y2="22"></line>
                <line x1="17" y1="2" x2="17" y2="22"></line>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <line x1="2" y1="7" x2="7" y2="7"></line>
                <line x1="2" y1="17" x2="7" y2="17"></line>
                <line x1="17" y1="17" x2="22" y2="17"></line>
                <line x1="17" y1="7" x2="22" y2="7"></line>
              </svg>
            </div>
            <div class="stat-info">
              <h3 class="stat-title">Обученные изображения</h3>
              <p class="stat-value">{{avatar.trainedImages}}</p>
              <p class="stat-description">Изображений использовано для обучения</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <div class="stat-info">
              <h3 class="stat-title">Голосовой профиль</h3>
              <p class="stat-value">{{avatar.trainedVoice ? 'Обучен' : 'Не обучен'}}</p>
              <p class="stat-description">{{avatar.trainedVoice ? 'Голос клонирован' : 'Требуется загрузка аудио'}}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <polygon points="23 7 16 12 23 17 23 7"></polygon>
              </svg>
            </div>
            <div class="stat-info">
              <h3 class="stat-title">Созданные видео</h3>
              <p class="stat-value">0</p>
              <p class="stat-description">Видео сгенерировано этим аватаром</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <div class="stat-info">
              <h3 class="stat-title">Дата создания</h3>
              <p class="stat-value">{{formatDate(avatar.createdAt)}}</p>
              <p class="stat-description">Аватар создан</p>
            </div>
          </div>
        </div>

        <div class="training-progress" *ngIf="avatar.status === 'training'">
          <div class="progress-header">
            <h3>Прогресс обучения</h3>
            <span class="progress-percentage">{{trainingProgress}}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" [style.width.%]="trainingProgress"></div>
          </div>
          <p class="progress-description">Обучение модели может занять несколько часов</p>
        </div>

        <div class="action-section">
          <h2>Действия с аватаром</h2>
          <div class="action-buttons">
            <button class="btn btn-primary btn-large" routerLink="/generation" [queryParams]="{avatarId: avatar.id}">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <polygon points="23 7 16 12 23 17 23 7"></polygon>
              </svg>
              Создать видео
            </button>
            
            <button class="btn btn-secondary btn-large" (click)="addMoreImages()">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              Добавить изображения
            </button>
            
            <button class="btn btn-secondary btn-large" (click)="addVoiceSample()">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
              Добавить голос
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .avatar-detail-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .back-button {
      margin-bottom: 2rem;
    }

    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 4rem;
      text-align: center;
    }

    .loading-spinner {
      width: 48px;
      height: 48px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #0d6efd;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .error-container {
      margin: 2rem 0;
    }

    .alert {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1rem;
    }

    .alert-error {
      background-color: #fee;
      border: 1px solid #fcc;
      color: #c00;
    }

    .not-found {
      text-align: center;
      padding: 4rem 2rem;
    }

    .not-found-icon {
      color: #6c757d;
      margin-bottom: 1.5rem;
    }

    .avatar-header {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 3rem;
      margin-bottom: 3rem;
      align-items: start;
    }

    @media (max-width: 768px) {
      .avatar-header {
        grid-template-columns: 1fr;
        gap: 2rem;
      }
    }

    .avatar-preview {
      position: relative;
    }

    .avatar-image-large {
      width: 200px;
      height: 200px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .avatar-placeholder-large {
      font-size: 6rem;
      background: white;
      width: 140px;
      height: 140px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .avatar-status-large {
      position: absolute;
      top: 1rem;
      right: -0.5rem;
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-size: 0.875rem;
      font-weight: 600;
    }

    .status-training {
      background: #fef3c7;
      color: #92400e;
    }

    .status-active {
      background: #d1fae5;
      color: #065f46;
    }

    .status-failed {
      background: #fee2e2;
      color: #991b1b;
    }

    .avatar-info-header {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .avatar-title-section {
      margin-bottom: 2rem;
    }

    .avatar-name {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }

    .avatar-description {
      font-size: 1.125rem;
      color: #6b7280;
      line-height: 1.6;
    }

    .avatar-actions-header {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .avatar-stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }

    .stat-card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .stat-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .stat-icon {
      color: #0d6efd;
      flex-shrink: 0;
    }

    .stat-info {
      flex: 1;
    }

    .stat-title {
      font-size: 0.875rem;
      font-weight: 600;
      color: #6b7280;
      margin-bottom: 0.25rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 0.25rem;
    }

    .stat-description {
      font-size: 0.875rem;
      color: #6b7280;
    }

    .training-progress {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 3rem;
    }

    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .progress-header h3 {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 600;
      color: #1f2937;
    }

    .progress-percentage {
      font-size: 1.25rem;
      font-weight: 700;
      color: #0d6efd;
    }

    .progress-bar {
      height: 8px;
      background: #e5e7eb;
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 0.5rem;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #0d6efd, #0b5ed7);
      border-radius: 4px;
      transition: width 0.3s ease;
    }

    .progress-description {
      font-size: 0.875rem;
      color: #6b7280;
      margin: 0;
    }

    .action-section {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 2rem;
    }

    .action-section h2 {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: #1f2937;
    }

    .action-buttons {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .btn {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      border: none;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s;
    }

    .btn-primary {
      background: #0d6efd;
      color: white;
    }

    .btn-primary:hover {
      background: #0b5ed7;
    }

    .btn-secondary {
      background: #6c757d;
      color: white;
    }

    .btn-secondary:hover {
      background: #5c636a;
    }

    .btn-danger {
      background: #dc3545;
      color: white;
    }

    .btn-danger:hover {
      background: #bb2d3b;
    }

    .btn-large {
      padding: 1rem 2rem;
      font-size: 1.125rem;
    }

    .btn-sm {
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
    }

    @media (max-width: 768px) {
      .avatar-name {
        font-size: 2rem;
      }
      
      .avatar-stats-grid {
        grid-template-columns: 1fr;
      }
      
      .action-buttons {
        flex-direction: column;
      }
      
      .btn-large {
        width: 100%;
        justify-content: center;
      }
    }
  `]
})
export class AvatarDetailComponent implements OnInit {
  avatar: Avatar | null = null;
  isLoading = false;
  error: string | null = null;
  trainingProgress = 0;
  private progressInterval: any;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private avatarService: AvatarService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      const avatarId = params['id'];
      if (avatarId) {
        this.loadAvatar(avatarId);
      }
    });
  }

  loadAvatar(avatarId?: string) {
    const id = avatarId || this.route.snapshot.params['id'];
    if (!id) return;

    this.isLoading = true;
    this.error = null;

    this.avatarService.getAvatar(id)
      .pipe(
        catchError((error: any) => {
          this.error = error.message || 'Не удалось загрузить данные аватара';
          return of({ data: null });
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe(response => {
        this.avatar = response.data;
        if (this.avatar?.status === 'training') {
          this.startProgressTracking();
        }
      });
  }

  startProgressTracking() {
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
    }

    this.progressInterval = setInterval(() => {
      if (this.avatar) {
        this.avatarService.getTrainingProgress(this.avatar.id)
          .pipe(
            catchError(() => of({ data: { progress: this.trainingProgress, status: 'training' } }))
          )
          .subscribe(response => {
            this.trainingProgress = response.data?.progress || 0;
            
            if (this.trainingProgress >= 100 || response.data?.status !== 'training') {
              clearInterval(this.progressInterval);
              this.loadAvatar(); // Перезагружаем для обновления статуса
            }
          });
      }
    }, 5000); // Проверяем каждые 5 секунд
  }

  getAvatarEmoji(avatar: Avatar): string {
    if (avatar.name.toLowerCase().includes('business') || avatar.name.toLowerCase().includes('деловой')) {
      return '👨‍💼';
    } else if (avatar.name.toLowerCase().includes('casual') || avatar.name.toLowerCase().includes('повседневный')) {
      return '😎';
    } else if (avatar.name.toLowerCase().includes('creative') || avatar.name.toLowerCase().includes('креативный')) {
      return '🎭';
    } else if (avatar.status === 'training') {
      return '🔄';
    } else if (avatar.status === 'failed') {
      return '❌';
    }
    return '👤';
  }

  getStatusText(status: string): string {
    switch (status) {
      case 'training': return 'Обучение';
      case 'active': return 'Активен';
      case 'failed': return 'Ошибка';
      default: return status;
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  }

  startTraining() {
    if (!this.avatar) return;

    this.avatarService.startTraining(this.avatar.id)
      .pipe(
        catchError((error: any) => {
          alert(`Ошибка при запуске обучения: ${error.message}`);
          return of(null);
        })
      )
      .subscribe(() => {
        this.loadAvatar(); // Перезагружаем для обновления статуса
      });
  }

  onEditAvatar() {
    if (!this.avatar) return;
    // TODO: Реализовать редактирование аватара
    console.log('Edit avatar:', this.avatar);
  }

  onDeleteAvatar() {
    if (!this.avatar) return;

    if (confirm(`Вы уверены, что хотите удалить аватар "${this.avatar.name}"?`)) {
      this.avatarService.deleteAvatar(this.avatar.id)
        .pipe(
          catchError((error: any) => {
            alert(`Ошибка при удалении: ${error.message}`);
            return of(null);
          })
        )
        .subscribe(() => {
          this.router.navigate(['/avatars']);
        });
    }
  }

  addMoreImages() {
    if (!this.avatar) return;
    // TODO: Реализовать добавление изображений
    console.log('Add more images for avatar:', this.avatar);
  }

  addVoiceSample() {
    if (!this.avatar) return;
    // TODO: Реализовать добавление голоса
    console.log('Add voice sample for avatar:', this.avatar);
  }

  ngOnDestroy() {
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
    }
  }
}
