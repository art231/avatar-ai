import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AvatarService, Avatar } from '../../../application/services/avatar.service';
import { catchError, finalize } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-avatars',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="avatars-container">
      <div class="page-header">
        <div>
          <h1 class="page-title">Мои аватары</h1>
          <p class="page-subtitle">Управляйте и просматривайте ваши AI аватары</p>
        </div>
        <button class="btn btn-primary" routerLink="/avatars/create">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Создать аватар
        </button>
      </div>

      <div class="loading-container" *ngIf="isLoading">
        <div class="loading-spinner"></div>
        <p>Загрузка аватаров...</p>
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
          <button class="btn btn-secondary btn-sm" (click)="loadAvatars()">Повторить</button>
        </div>
      </div>

      <div class="empty-state" *ngIf="!isLoading && !error && avatars.length === 0">
        <div class="empty-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <h3>У вас еще нет аватаров</h3>
        <p>Создайте свой первый AI аватар для генерации видео</p>
        <button class="btn btn-primary" routerLink="/avatars/create">
          Создать первый аватар
        </button>
      </div>

      <div class="avatars-grid" *ngIf="!isLoading && !error && avatars.length > 0">
        <div class="avatar-card" *ngFor="let avatar of avatars" [routerLink]="['/avatars', avatar.id]">
          <div class="avatar-image" [class.status-training]="avatar.status === 'training'" [class.status-active]="avatar.status === 'active'" [class.status-failed]="avatar.status === 'failed'">
            <div class="avatar-placeholder">{{getAvatarEmoji(avatar)}}</div>
            <div class="avatar-status-badge" [class]="'status-' + avatar.status">
              {{getStatusText(avatar.status)}}
            </div>
          </div>
          <div class="avatar-info">
            <h3 class="avatar-name">{{avatar.name}}</h3>
            <p class="avatar-description">{{avatar.description || 'Без описания'}}</p>
            <div class="avatar-stats">
              <span class="stat">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
                  <line x1="7" y1="2" x2="7" y2="22"></line>
                  <line x1="17" y1="2" x2="17" y2="22"></line>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <line x1="2" y1="7" x2="7" y2="7"></line>
                  <line x1="2" y1="17" x2="7" y2="17"></line>
                  <line x1="17" y1="17" x2="22" y2="17"></line>
                  <line x1="17" y1="7" x2="22" y2="7"></line>
                </svg>
                {{avatar.trainedImages}} изображений
              </span>
              <span class="stat">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                {{avatar.trainedVoice ? 'Голос обучен' : 'Без голоса'}}
              </span>
            </div>
            <div class="avatar-actions">
              <button class="btn btn-secondary btn-sm" (click)="onEditAvatar($event, avatar)">
                Редактировать
              </button>
              <button class="btn btn-danger btn-sm" (click)="onDeleteAvatar($event, avatar)">
                Удалить
              </button>
            </div>
          </div>
        </div>
        
        <div class="avatar-card add-new" routerLink="/avatars/create">
          <div class="add-new-content">
            <div class="add-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </div>
            <h3 class="add-title">Создать новый аватар</h3>
            <p class="add-description">Начать обучение нового AI аватара</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .avatars-container {
      max-width: 1200px;
      margin: 0 auto;
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
      margin-bottom: 2rem;
    }
    
    .avatars-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 2rem;
    }
    
    .avatar-card {
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .avatar-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    
    .avatar-image {
      height: 200px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .avatar-placeholder {
      font-size: 5rem;
      background: white;
      width: 120px;
      height: 120px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .avatar-info {
      padding: 1.5rem;
    }
    
    .avatar-name {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .avatar-status {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
    }
    
    .status-active {
      background: #d1fae5;
      color: #065f46;
    }
    
    .status-training {
      background: #fef3c7;
      color: #92400e;
    }
    
    .avatar-description {
      color: #6b7280;
      font-size: 0.875rem;
      margin-bottom: 1rem;
      line-height: 1.5;
    }
    
    .avatar-stats {
      display: flex;
      gap: 1rem;
      font-size: 0.75rem;
      color: #6b7280;
    }
    
    .stat {
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }
    
    .add-new {
      border: 2px dashed #d1d5db;
      background: #f9fafb;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s;
    }
    
    .add-new:hover {
      border-color: #667eea;
      background: #f0f4ff;
    }
    
    .add-new-content {
      text-align: center;
      padding: 2rem;
    }
    
    .add-icon {
      font-size: 3rem;
      color: #667eea;
      margin-bottom: 1rem;
    }
    
    .add-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .add-description {
      color: #6b7280;
      font-size: 0.875rem;
    }
    
    @media (max-width: 768px) {
      .avatars-grid {
        grid-template-columns: 1fr;
      }
      
      .page-title {
        font-size: 2rem;
      }
    }
  `]
})
export class AvatarsComponent implements OnInit {
  avatars: Avatar[] = [];
  isLoading = false;
  error: string | null = null;

  constructor(private avatarService: AvatarService) {}

  ngOnInit() {
    this.loadAvatars();
  }

  loadAvatars() {
    this.isLoading = true;
    this.error = null;

    this.avatarService.getAvatars()
      .pipe(
        catchError(error => {
          this.error = error.message || 'Не удалось загрузить аватары';
          return of({ data: [] });
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe(response => {
        this.avatars = response.data || [];
      });
  }

  getAvatarEmoji(avatar: Avatar): string {
    // Простая логика для выбора эмодзи на основе имени или статуса
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

  onEditAvatar(event: Event, avatar: Avatar) {
    event.stopPropagation();
    // TODO: Реализовать редактирование аватара
    console.log('Edit avatar:', avatar);
  }

  onDeleteAvatar(event: Event, avatar: Avatar) {
    event.stopPropagation();
    if (confirm(`Вы уверены, что хотите удалить аватар "${avatar.name}"?`)) {
      this.avatarService.deleteAvatar(avatar.id)
        .pipe(
          catchError(error => {
            alert(`Ошибка при удалении: ${error.message}`);
            return of(null);
          })
        )
        .subscribe(() => {
          this.loadAvatars(); // Перезагружаем список
        });
    }
  }
}
