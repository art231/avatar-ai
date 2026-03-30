import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-training',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="training-container">
      <h1 class="page-title">Train Your Avatar</h1>
      <p class="page-subtitle">Upload photos and voice samples to train your AI avatar</p>
      
      <div class="training-steps">
        <div class="step active">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3 class="step-title">Upload Photos</h3>
            <p class="step-description">Upload 10-20 clear photos of your face from different angles</p>
            <div class="upload-area">
              <div class="upload-placeholder">
                <span class="upload-icon">📷</span>
                <p class="upload-text">Drag & drop photos here or click to browse</p>
                <p class="upload-hint">JPG, PNG up to 5MB each</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3 class="step-title">Upload Voice Sample</h3>
            <p class="step-description">Record or upload 30-60 seconds of clear speech</p>
            <div class="voice-upload">
              <button class="btn btn-outline">
                <span class="btn-icon">🎤</span>
                Record Voice
              </button>
              <button class="btn btn-outline">
                <span class="btn-icon">📁</span>
                Upload Audio File
              </button>
            </div>
          </div>
        </div>
        
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3 class="step-title">Start Training</h3>
            <p class="step-description">Begin AI model training process</p>
            <div class="training-options">
              <div class="option-card">
                <h4 class="option-title">Fast Training</h4>
                <p class="option-time">~30 minutes</p>
                <p class="option-description">Basic quality for quick results</p>
              </div>
              <div class="option-card recommended">
                <h4 class="option-title">Standard Training</h4>
                <p class="option-time">~2 hours</p>
                <p class="option-description">Recommended for most use cases</p>
              </div>
              <div class="option-card">
                <h4 class="option-title">Premium Training</h4>
                <p class="option-time">~6 hours</p>
                <p class="option-description">Highest quality for professional use</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="training-actions">
        <button class="btn btn-primary btn-lg">
          Start Training Process
        </button>
        <button class="btn btn-outline">
          Save as Draft
        </button>
      </div>
      
      <div class="training-tips">
        <h3 class="tips-title">Tips for Best Results</h3>
        <ul class="tips-list">
          <li class="tip">Use clear, well-lit photos with neutral expression</li>
          <li class="tip">Include photos from different angles (front, side, 45°)</li>
          <li class="tip">Avoid photos with glasses, hats, or heavy makeup</li>
          <li class="tip">Record voice in a quiet environment without background noise</li>
          <li class="tip">Speak naturally and clearly in your normal voice</li>
        </ul>
      </div>
    </div>
  `,
  styles: [`
    .training-container {
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
      margin-bottom: 3rem;
    }
    
    .training-steps {
      display: flex;
      flex-direction: column;
      gap: 3rem;
      margin-bottom: 3rem;
    }
    
    .step {
      display: flex;
      gap: 2rem;
      opacity: 0.6;
      transition: opacity 0.3s;
    }
    
    .step.active {
      opacity: 1;
    }
    
    .step-number {
      width: 50px;
      height: 50px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 700;
      flex-shrink: 0;
    }
    
    .step-content {
      flex: 1;
    }
    
    .step-title {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .step-description {
      color: #6b7280;
      margin-bottom: 1.5rem;
    }
    
    .upload-area {
      border: 2px dashed #d1d5db;
      border-radius: 12px;
      padding: 3rem;
      text-align: center;
      background: #f9fafb;
      cursor: pointer;
      transition: all 0.3s;
    }
    
    .upload-area:hover {
      border-color: #667eea;
      background: #f0f4ff;
    }
    
    .upload-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }
    
    .upload-icon {
      font-size: 3rem;
    }
    
    .upload-text {
      font-size: 1.125rem;
      font-weight: 500;
      color: #1f2937;
      margin: 0;
    }
    
    .upload-hint {
      font-size: 0.875rem;
      color: #6b7280;
      margin: 0;
    }
    
    .voice-upload {
      display: flex;
      gap: 1rem;
    }
    
    .training-options {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
    }
    
    .option-card {
      background: white;
      border: 2px solid #e5e7eb;
      border-radius: 12px;
      padding: 1.5rem;
      text-align: center;
      transition: all 0.3s;
      cursor: pointer;
    }
    
    .option-card:hover {
      border-color: #667eea;
      transform: translateY(-2px);
    }
    
    .option-card.recommended {
      border-color: #667eea;
      background: #f0f4ff;
    }
    
    .option-title {
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .option-time {
      font-size: 1.5rem;
      font-weight: 700;
      color: #667eea;
      margin-bottom: 0.5rem;
    }
    
    .option-description {
      font-size: 0.875rem;
      color: #6b7280;
      margin: 0;
    }
    
    .training-actions {
      display: flex;
      gap: 1rem;
      margin-bottom: 3rem;
    }
    
    .training-tips {
      background: #f9fafb;
      border-radius: 12px;
      padding: 2rem;
    }
    
    .tips-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: #1f2937;
    }
    
    .tips-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .tip {
      padding: 0.5rem 0;
      color: #6b7280;
      position: relative;
      padding-left: 1.5rem;
    }
    
    .tip:before {
      content: "✓";
      position: absolute;
      left: 0;
      color: #10b981;
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
    
    .btn-outline {
      background: transparent;
      color: #667eea;
      border: 2px solid #667eea;
    }
    
    .btn-outline:hover {
      background: #667eea;
      color: white;
    }
    
    .btn-lg {
      padding: 1rem 2rem;
      font-size: 1.125rem;
    }
    
    .btn-icon {
      font-size: 1.25rem;
    }
    
    @media (max-width: 768px) {
      .step {
        flex-direction: column;
        gap: 1rem;
      }
      
      .voice-upload {
        flex-direction: column;
      }
      
      .training-options {
        grid-template-columns: 1fr;
      }
      
      .training-actions {
        flex-direction: column;
      }
      
      .page-title {
        font-size: 2rem;
      }
    }
  `]
})
export class TrainingComponent {}