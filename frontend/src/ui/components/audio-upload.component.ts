import { Component, EventEmitter, Output, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-audio-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="audio-upload-container" [class.drag-over]="isDragOver" (dragover)="onDragOver($event)" (dragleave)="onDragLeave($event)" (drop)="onDrop($event)">
      <div class="upload-area" *ngIf="!audioFile">
        <div class="upload-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 18V5l12-2v13"></path>
            <circle cx="6" cy="18" r="3"></circle>
            <circle cx="18" cy="16" r="3"></circle>
          </svg>
        </div>
        <h3 class="upload-title">Загрузите аудио для клонирования голоса</h3>
        <p class="upload-description">
          Перетащите файл сюда или нажмите для выбора
        </p>
        <p class="upload-requirements">
          Поддерживаемые форматы: WAV, MP3, FLAC<br>
          Длительность: 10-60 секунд<br>
          Качество: 16kHz, моно
        </p>
        <input 
          type="file" 
          #fileInput 
          (change)="onFileSelected($event)" 
          accept="audio/wav,audio/mpeg,audio/flac,audio/x-wav" 
          hidden
        />
        <button type="button" class="btn btn-primary" (click)="fileInput.click()">
          Выбрать файл
        </button>
      </div>

      <div class="preview-container" *ngIf="audioFile">
        <div class="preview-header">
          <h3>Выбранное аудио</h3>
          <button type="button" class="btn btn-secondary btn-sm" (click)="clearAudio()">
            Удалить
          </button>
        </div>
        
        <div class="audio-preview">
          <div class="audio-info">
            <div class="audio-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
            </div>
            <div class="audio-details">
              <h4 class="file-name">{{audioFile.name}}</h4>
              <div class="audio-metadata">
                <span class="file-size">{{formatFileSize(audioFile.size)}}</span>
                <span class="file-duration" *ngIf="audioDuration">{{formatDuration(audioDuration)}}</span>
                <span class="file-format">{{getFileFormat(audioFile.name)}}</span>
              </div>
            </div>
          </div>

          <div class="audio-player" *ngIf="audioUrl">
            <div class="player-controls">
              <button type="button" class="btn btn-icon" (click)="togglePlay()" [disabled]="!audioUrl">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon *ngIf="!isPlaying" points="5 3 19 12 5 21 5 3"></polygon>
                  <rect *ngIf="isPlaying" x="6" y="4" width="4" height="16"></rect>
                  <rect *ngIf="isPlaying" x="14" y="4" width="4" height="16"></rect>
                </svg>
              </button>
              
              <div class="progress-container">
                <div class="progress-bar" [style.width.%]="progressPercentage">
                  <div class="progress-handle"></div>
                </div>
                <input 
                  type="range" 
                  class="progress-slider" 
                  [value]="currentTime" 
                  [max]="audioDuration || 0" 
                  (input)="onSeek($event)"
                  (change)="onSeekEnd($event)"
                />
              </div>
              
              <div class="time-display">
                <span class="current-time">{{formatTime(currentTime)}}</span>
                <span class="duration">{{formatTime(audioDuration || 0)}}</span>
              </div>
            </div>

            <div class="volume-control">
              <button type="button" class="btn btn-icon" (click)="toggleMute()">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon *ngIf="!isMuted && volume > 0.5" points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                  <polygon *ngIf="!isMuted && volume <= 0.5 && volume > 0" points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                  <path *ngIf="!isMuted && volume <= 0.5 && volume > 0" d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                  <path *ngIf="isMuted || volume === 0" d="M11 5L19 19"></path>
                  <path *ngIf="isMuted || volume === 0" d="M19 5L11 19"></path>
                  <path *ngIf="!isMuted && volume > 0.5" d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                  <path *ngIf="!isMuted && volume > 0.5" d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                </svg>
              </button>
              <input 
                type="range" 
                class="volume-slider" 
                [value]="volume * 100" 
                min="0" 
                max="100" 
                (input)="onVolumeChange($event)"
              />
            </div>
          </div>

          <div class="validation-message" *ngIf="showValidation && !isAudioValid">
            <div class="alert alert-warning">
              Аудио должно быть длительностью 10-60 секунд для качественного клонирования голоса.
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .audio-upload-container {
      border: 2px dashed #dee2e6;
      border-radius: 8px;
      padding: 2rem;
      transition: all 0.3s ease;
      background-color: #f8f9fa;
    }

    .audio-upload-container.drag-over {
      border-color: #0d6efd;
      background-color: rgba(13, 110, 253, 0.05);
    }

    .upload-area {
      text-align: center;
      padding: 2rem 0;
    }

    .upload-icon {
      color: #6c757d;
      margin-bottom: 1rem;
    }

    .upload-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #212529;
    }

    .upload-description {
      color: #6c757d;
      margin-bottom: 1rem;
    }

    .upload-requirements {
      color: #6c757d;
      font-size: 0.875rem;
      margin-bottom: 1.5rem;
      line-height: 1.5;
    }

    .preview-container {
      margin-top: 1rem;
    }

    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .preview-header h3 {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 600;
      color: #212529;
    }

    .audio-preview {
      background-color: white;
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .audio-info {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .audio-icon {
      color: #0d6efd;
    }

    .audio-details {
      flex: 1;
    }

    .file-name {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      font-weight: 600;
      color: #212529;
    }

    .audio-metadata {
      display: flex;
      gap: 1rem;
      font-size: 0.875rem;
      color: #6c757d;
    }

    .audio-player {
      margin-top: 1.5rem;
    }

    .player-controls {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .btn-icon {
      background: none;
      border: none;
      padding: 0.5rem;
      color: #6c757d;
      cursor: pointer;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .btn-icon:hover {
      background-color: #f8f9fa;
      color: #212529;
    }

    .btn-icon:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .progress-container {
      flex: 1;
      position: relative;
      height: 24px;
    }

    .progress-bar {
      position: absolute;
      top: 11px;
      left: 0;
      height: 2px;
      background-color: #0d6efd;
      border-radius: 1px;
      transition: width 0.1s linear;
    }

    .progress-handle {
      position: absolute;
      right: -4px;
      top: -3px;
      width: 8px;
      height: 8px;
      background-color: #0d6efd;
      border-radius: 50%;
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    .progress-container:hover .progress-handle {
      opacity: 1;
    }

    .progress-slider {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 24px;
      opacity: 0;
      cursor: pointer;
    }

    .time-display {
      display: flex;
      justify-content: space-between;
      font-size: 0.75rem;
      color: #6c757d;
      min-width: 80px;
    }

    .volume-control {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .volume-slider {
      width: 80px;
      height: 4px;
      -webkit-appearance: none;
      background: #dee2e6;
      border-radius: 2px;
      outline: none;
    }

    .volume-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 12px;
      height: 12px;
      background: #0d6efd;
      border-radius: 50%;
      cursor: pointer;
    }

    .volume-slider::-moz-range-thumb {
      width: 12px;
      height: 12px;
      background: #0d6efd;
      border-radius: 50%;
      cursor: pointer;
      border: none;
    }

    .validation-message {
      margin-top: 1rem;
    }

    .alert {
      padding: 0.75rem 1rem;
      border-radius: 4px;
      border: 1px solid transparent;
    }

    .alert-warning {
      background-color: #fff3cd;
      border-color: #ffecb5;
      color: #664d03;
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 4px;
      border: none;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .btn-primary {
      background-color: #0d6efd;
      color: white;
    }

    .btn-primary:hover {
      background-color: #0b5ed7;
    }

    .btn-secondary {
      background-color: #6c757d;
      color: white;
    }

    .btn-secondary:hover {
      background-color: #5c636a;
    }

    .btn-sm {
      padding: 0.25rem 0.5rem;
      font-size: 0.875rem;
    }
  `]
})
export class AudioUploadComponent implements OnInit {
  @Input() minDuration: number = 10; // секунды
  @Input() maxDuration: number = 60; // секунды
  @Input() showValidation: boolean = false;
  @Output() audioChange = new EventEmitter<File | null>();

  audioFile: File | null = null;
  audioUrl: string | null = null;
  audioElement: HTMLAudioElement | null = null;
  audioDuration: number = 0;
  currentTime: number = 0;
  isPlaying: boolean = false;
  isMuted: boolean = false;
  volume: number = 1;
  isDragOver = false;

  get progressPercentage(): number {
    if (!this.audioDuration) return 0;
    return (this.currentTime / this.audioDuration) * 100;
  }

  get isAudioValid(): boolean {
    if (!this.audioDuration) return true;
    return this.audioDuration >= this.minDuration && this.audioDuration <= this.maxDuration;
  }

  ngOnInit() {
    // Инициализация компонента
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.processFile(files[0]);
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.processFile(input.files[0]);
    }
  }

  private processFile(file: File) {
    // Проверяем тип файла
    if (!file.type.startsWith('audio/')) {
      // TODO: Показать ошибку о неподдерживаемом формате
      return;
    }

    // Очищаем предыдущий аудио элемент
    this.cleanupAudio();

    // Устанавливаем новый файл
    this.audioFile = file;
    this.audioUrl = URL.createObjectURL(file);
    
    // Создаем аудио элемент для получения метаданных
    this.audioElement = new Audio(this.audioUrl);
    
    this.audioElement.addEventListener('loadedmetadata', () => {
      this.audioDuration = this.audioElement?.duration || 0;
    });

    this.audioElement.addEventListener('timeupdate', () => {
      this.currentTime = this.audioElement?.currentTime || 0;
    });

    this.audioElement.addEventListener('ended', () => {
      this.isPlaying = false;
      this.currentTime = 0;
    });

    this.emitChanges();
  }

  clearAudio() {
    this.cleanupAudio();
    this.audioFile = null;
    this.audioUrl = null;
    this.audioDuration = 0;
    this.currentTime = 0;
    this.isPlaying = false;
    this.emitChanges();
  }

  private cleanupAudio() {
    if (this.audioElement) {
      this.audioElement.pause();
      this.audioElement.src = '';
      this.audioElement = null;
    }
    
    if (this.audioUrl) {
      URL.revokeObjectURL(this.audioUrl);
    }
  }

  togglePlay() {
    if (!this.audioElement) return;

    if (this.isPlaying) {
      this.audioElement.pause();
    } else {
      this.audioElement.play();
    }
    this.isPlaying = !this.isPlaying;
  }

  toggleMute() {
    if (!this.audioElement) return;
    
    this.isMuted = !this.isMuted;
    this.audioElement.muted = this.isMuted;
    
    if (this.isMuted) {
      this.volume = 0;
    } else {
      this.volume = 0.7;
    }
  }

  onSeek(event: Event) {
    const input = event.target as HTMLInputElement;
    const time = parseFloat(input.value);
    
    if (this.audioElement) {
      this.audioElement.currentTime = time;
      this.currentTime = time;
    }
  }

  onSeekEnd(event: Event) {
    // Дополнительная логика при завершении перемотки
  }

  onVolumeChange(event: Event) {
    const input = event.target as HTMLInputElement;
    this.volume = parseFloat(input.value) / 100;
    
    if (this.audioElement) {
      this.audioElement.volume = this.volume;
      this.isMuted = this.volume === 0;
    }
  }

  private emitChanges() {
    this.audioChange.emit(this.audioFile);
  }

  formatFileSize(bytes: number): string {
    if (!bytes) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }

  formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  getFileFormat(filename: string): string {
    const parts = filename.split('.');
    return parts.length > 1 ? parts[parts.length - 1].toUpperCase() : 'UNKNOWN';
  }

  ngOnDestroy() {
    this.cleanupAudio();
  }
}
