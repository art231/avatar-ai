import { Component, EventEmitter, Output, Input, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-image-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="image-upload-container" [class.drag-over]="isDragOver" (dragover)="onDragOver($event)" (dragleave)="onDragLeave($event)" (drop)="onDrop($event)">
      <div class="upload-area" *ngIf="!previewUrls.length">
        <div class="upload-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <h3 class="upload-title">Загрузите изображения для аватара</h3>
        <p class="upload-description">
          Перетащите файлы сюда или нажмите для выбора
        </p>
        <p class="upload-requirements">
          Поддерживаемые форматы: JPG, PNG, WebP<br>
          Минимум: {{minImages}} изображений<br>
          Максимум: {{maxImages}} изображений
        </p>
        <input 
          type="file" 
          #fileInput 
          (change)="onFileSelected($event)" 
          [multiple]="true" 
          accept="image/jpeg,image/png,image/webp" 
          hidden
        />
        <button type="button" class="btn btn-primary" (click)="triggerFileInput()">
          Выбрать файлы
        </button>
      </div>

      <div class="preview-container" *ngIf="previewUrls.length">
        <div class="preview-header">
          <h3>Выбранные изображения ({{previewUrls.length}}/{{maxImages}})</h3>
          <button type="button" class="btn btn-secondary btn-sm" (click)="clearAll()" *ngIf="previewUrls.length > 0">
            Очистить все
          </button>
        </div>
        
        <div class="preview-grid">
          <div class="preview-item" *ngFor="let preview of previewUrls; let i = index">
            <div class="preview-image-container">
              <img [src]="preview" alt="Preview" class="preview-image" />
              <div class="preview-overlay">
                <button type="button" class="btn btn-danger btn-sm" (click)="removeImage(i)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
            <div class="preview-info">
              <span class="file-name">{{files[i].name || 'Изображение ' + (i + 1)}}</span>
              <span class="file-size">{{formatFileSize(files[i].size)}}</span>
            </div>
          </div>
          
          <div class="preview-item add-more" *ngIf="previewUrls.length < maxImages" (click)="triggerFileInput()">
            <div class="add-more-content">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              <span>Добавить еще</span>
            </div>
          </div>
        </div>

        <div class="validation-message" *ngIf="showValidation && previewUrls.length < minImages">
          <div class="alert alert-warning">
            Необходимо загрузить минимум {{minImages}} изображений для качественного обучения модели.
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .image-upload-container {
      border: 2px dashed #dee2e6;
      border-radius: 8px;
      padding: 2rem;
      transition: all 0.3s ease;
      background-color: #f8f9fa;
    }

    .image-upload-container.drag-over {
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
      margin-bottom: 1rem;
    }

    .preview-header h3 {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 600;
      color: #212529;
    }

    .preview-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .preview-item {
      border: 1px solid #dee2e6;
      border-radius: 6px;
      overflow: hidden;
      background-color: white;
      transition: transform 0.2s ease;
    }

    .preview-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .preview-image-container {
      position: relative;
      aspect-ratio: 1;
      overflow: hidden;
    }

    .preview-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .preview-overlay {
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    .preview-image-container:hover .preview-overlay {
      opacity: 1;
    }

    .preview-info {
      padding: 0.75rem;
      border-top: 1px solid #dee2e6;
    }

    .file-name {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
      color: #212529;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .file-size {
      display: block;
      font-size: 0.75rem;
      color: #6c757d;
      margin-top: 0.25rem;
    }

    .add-more {
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      border-style: dashed;
      background-color: #f8f9fa;
    }

    .add-more-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      color: #6c757d;
      padding: 2rem;
    }

    .add-more:hover {
      border-color: #0d6efd;
      color: #0d6efd;
    }

    .validation-message {
      margin-top: 1rem;
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

    .btn-danger {
      background-color: #dc3545;
      color: white;
      padding: 0.25rem 0.5rem;
    }

    .btn-danger:hover {
      background-color: #bb2d3b;
    }

    .btn-sm {
      padding: 0.25rem 0.5rem;
      font-size: 0.875rem;
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
  `]
})
export class ImageUploadComponent implements OnInit {
  @Input() minImages: number = 5;
  @Input() maxImages: number = 20;
  @Input() showValidation: boolean = false;
  @Output() imagesChange = new EventEmitter<File[]>();

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  files: File[] = [];
  previewUrls: string[] = [];
  isDragOver = false;

  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
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
    if (files) {
      this.processFiles(Array.from(files));
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.processFiles(Array.from(input.files));
    }
  }

  private processFiles(fileList: File[]) {
    const imageFiles = fileList.filter(file => 
      file.type.startsWith('image/') && 
      ['image/jpeg', 'image/png', 'image/webp'].includes(file.type)
    );

    if (imageFiles.length === 0) {
      // TODO: Показать ошибку о неподдерживаемых форматах
      return;
    }

    // Проверяем, не превысим ли мы максимальное количество
    const availableSlots = this.maxImages - this.files.length;
    const filesToAdd = imageFiles.slice(0, availableSlots);

    if (filesToAdd.length < imageFiles.length) {
      // TODO: Показать предупреждение о превышении лимита
    }

    // Добавляем файлы
    this.files.push(...filesToAdd);
    this.updatePreviews();
    this.emitChanges();
  }

  removeImage(index: number) {
    this.files.splice(index, 1);
    this.updatePreviews();
    this.emitChanges();
  }

  clearAll() {
    this.files = [];
    this.previewUrls = [];
    this.emitChanges();
  }

  private updatePreviews() {
    // Очищаем старые URL для предотвращения утечек памяти
    this.previewUrls.forEach(url => URL.revokeObjectURL(url));
    
    this.previewUrls = this.files.map(file => URL.createObjectURL(file));
  }

  private emitChanges() {
    this.imagesChange.emit([...this.files]);
  }

  formatFileSize(bytes?: number): string {
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

  ngOnDestroy() {
    // Очищаем все URL при уничтожении компонента
    this.previewUrls.forEach(url => URL.revokeObjectURL(url));
  }
}