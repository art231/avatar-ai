import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AvatarService, CreateAvatarRequest } from '../../../application/services/avatar.service';
import { AuthService } from '../../../application/services/auth.service';
import { ImageUploadComponent } from '../../../ui/components/image-upload.component';
import { AudioUploadComponent } from '../../../ui/components/audio-upload.component';
import { catchError, finalize } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-avatar-create',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, ImageUploadComponent, AudioUploadComponent],
  template: `
    <div class="avatar-create-container">
      <div class="back-button">
        <button class="btn btn-secondary" routerLink="/avatars">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Назад к аватарам
        </button>
      </div>

      <div class="create-header">
        <h1 class="page-title">Создание нового аватара</h1>
        <p class="page-subtitle">Загрузите изображения и аудио для обучения AI модели</p>
      </div>

      <form (ngSubmit)="onSubmit()" #avatarForm="ngForm" class="create-form">
        <div class="form-section">
          <h2 class="section-title">Основная информация</h2>
          
          <div class="form-group">
            <label for="avatarName" class="form-label">Название аватара *</label>
            <input 
              type="text" 
              id="avatarName" 
              name="avatarName" 
              [(ngModel)]="avatarData.name" 
              required 
              minlength="3" 
              maxlength="50"
              class="form-control"
              placeholder="Например: Деловой образ"
              #nameInput="ngModel"
            />
            <div class="validation-error" *ngIf="nameInput.invalid && (nameInput.dirty || nameInput.touched)">
              <span *ngIf="nameInput.errors?.['required']">Название обязательно</span>
              <span *ngIf="nameInput.errors?.['minlength']">Минимум 3 символа</span>
              <span *ngIf="nameInput.errors?.['maxlength']">Максимум 50 символов</span>
            </div>
          </div>

          <div class="form-group">
            <label for="avatarDescription" class="form-label">Описание</label>
            <textarea 
              id="avatarDescription" 
              name="avatarDescription" 
              [(ngModel)]="avatarData.description" 
              rows="3"
              class="form-control"
              placeholder="Опишите назначение аватара (например: для бизнес-презентаций)"
              maxlength="500"
            ></textarea>
            <div class="form-hint">
              {{avatarData.description?.length || 0}}/500 символов
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2 class="section-title">Изображения для обучения</h2>
          <p class="section-description">
            Загрузите 5-20 изображений лица в хорошем качестве. Изображения должны быть четкими, с хорошим освещением и показывать лицо с разных ракурсов.
          </p>
          
          <app-image-upload 
            [minImages]="5"
            [maxImages]="20"
            [showValidation]="showValidation"
            (imagesChange)="onImagesChange($event)"
          ></app-image-upload>
          
          <div class="validation-error" *ngIf="showValidation && (!selectedImages || selectedImages.length < 5)">
            Необходимо загрузить минимум 5 изображений
          </div>
        </div>

        <div class="form-section">
          <h2 class="section-title">Голосовой профиль (опционально)</h2>
          <p class="section-description">
            Загрузите аудио для клонирования голоса. Аудио должно быть чистым, без фонового шума, длительностью 10-60 секунд.
          </p>
          
          <app-audio-upload 
            [minDuration]="10"
            [maxDuration]="60"
            [showValidation]="showValidation"
            (audioChange)="onAudioChange($event)"
          ></app-audio-upload>
          
          <div class="form-hint">
            Голосовой профиль можно добавить позже. Без него аватар будет использовать стандартный синтез речи.
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" routerLink="/avatars">
            Отмена
          </button>
          <button 
            type="submit" 
            class="btn btn-primary" 
            [disabled]="isSubmitting || !avatarForm.form.valid || !selectedImages || selectedImages.length < 5"
          >
            <span *ngIf="!isSubmitting">Создать аватар</span>
            <span *ngIf="isSubmitting">
              <span class="spinner"></span>
              Создание...
            </span>
          </button>
        </div>

        <div class="error-container" *ngIf="error">
          <div class="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <div>
              <h4>Ошибка создания</h4>
              <p>{{error}}</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .avatar-create-container {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .back-button {
      margin-bottom: 2rem;
    }

    .create-header {
      margin-bottom: 3rem;
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
    }

    .create-form {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .form-section {
      margin-bottom: 3rem;
    }

    .section-title {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }

    .section-description {
      color: #6b7280;
      margin-bottom: 1.5rem;
      line-height: 1.6;
    }

    .form-group {
      margin-bottom: 1.5rem;
    }

    .form-label {
      display: block;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #374151;
    }

    .form-control {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color 0.2s;
    }

    .form-control:focus {
      outline: none;
      border-color: #0d6efd;
      box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }

    .form-control::placeholder {
      color: #9ca3af;
    }

    textarea.form-control {
      resize: vertical;
      min-height: 100px;
    }

    .form-hint {
      font-size: 0.875rem;
      color: #6b7280;
      margin-top: 0.5rem;
    }

    .validation-error {
      font-size: 0.875rem;
      color: #dc3545;
      margin-top: 0.5rem;
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 1rem;
      margin-top: 3rem;
      padding-top: 2rem;
      border-top: 1px solid #e5e7eb;
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

    .btn-primary:hover:not(:disabled) {
      background: #0b5ed7;
    }

    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: #6c757d;
      color: white;
    }

    .btn-secondary:hover {
      background: #5c636a;
    }

    .spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 1s linear infinite;
      margin-right: 0.5rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .error-container {
      margin-top: 2rem;
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

    @media (max-width: 768px) {
      .avatar-create-container {
        padding: 1rem;
      }
      
      .create-form {
        padding: 1.5rem;
      }
      
      .page-title {
        font-size: 2rem;
      }
      
      .form-actions {
        flex-direction: column;
      }
      
      .btn {
        width: 100%;
        justify-content: center;
      }
    }
  `]
})
export class AvatarCreateComponent implements OnInit {
  avatarData: CreateAvatarRequest = {
    userId: '',
    name: '',
    description: '',
    images: [],
    voiceSample: undefined
  };

  selectedImages: File[] = [];
  selectedAudio: File | null = null;
  isSubmitting = false;
  error: string | null = null;
  showValidation = false;

  constructor(
    private avatarService: AvatarService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Устанавливаем userId из текущего пользователя
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.avatarData.userId = currentUser.id;
    }
  }

  onImagesChange(images: File[]) {
    this.selectedImages = images;
    this.avatarData.images = images;
  }

  onAudioChange(audio: File | null) {
    this.selectedAudio = audio;
    this.avatarData.voiceSample = audio || undefined;
  }

  onSubmit() {
    this.showValidation = true;
    
    // Проверка авторизации пользователя
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) {
      this.error = 'Для создания аватара необходимо авторизоваться';
      return;
    }
    
    // Устанавливаем userId из текущего пользователя
    this.avatarData.userId = currentUser.id;
    
    // Проверка валидности формы
    if (!this.avatarData.name || this.selectedImages.length < 5) {
      return;
    }

    this.isSubmitting = true;
    this.error = null;

    this.avatarService.createAvatar(this.avatarData)
      .pipe(
        catchError((error: any) => {
          this.error = error.message || 'Не удалось создать аватар';
          return of({ data: null });
        }),
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe(response => {
        if (response.data) {
          this.router.navigate(['/avatars', response.data.id]);
        }
      });
  }
}