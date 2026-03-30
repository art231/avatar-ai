import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-generation',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="generation-container">
      <h1 class="page-title">Generate Content</h1>
      <p class="page-subtitle">Create videos with your AI avatar</p>
      
      <div class="generation-wizard">
        <div class="wizard-step active">
          <div class="step-header">
            <div class="step-number">1</div>
            <h3 class="step-title">Select Avatar</h3>
          </div>
          <div class="step-content">
            <div class="avatar-selection">
              <div class="avatar-option selected">
                <div class="avatar-preview">👨‍💼</div>
                <h4 class="avatar-name">Business You</h4>
              </div>
              <div class="avatar-option">
                <div class="avatar-preview">😎</div>
                <h4 class="avatar-name">Casual Me</h4>
              </div>
              <div class="avatar-option">
                <div class="avatar-preview">🎭</div>
                <h4 class="avatar-name">Creative Self</h4>
              </div>
            </div>
          </div>
        </div>
        
        <div class="wizard-step">
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
              >Hello! Welcome to AvatarAI. I'm your AI avatar, ready to help you create amazing content.</textarea>
              <div class="text-stats">
                <span class="stat">Characters: 85</span>
                <span class="stat">Words: 15</span>
                <span class="stat">Estimated duration: 12 seconds</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="wizard-step">
          <div class="step-header">
            <div class="step-number">3</div>
            <h3 class="step-title">Configure Settings</h3>
          </div>
          <div class="step-content">
            <div class="settings-grid">
              <div class="setting">
                <label class="setting-label">Voice Style</label>
                <select class="setting-select">
                  <option>Professional</option>
                  <option>Casual</option>
                  <option>Enthusiastic</option>
                  <option>Calm</option>
                </select>
              </div>
              <div class="setting">
                <label class="setting-label">Video Length</label>
                <select class="setting-select">
                  <option>Short (10-30 seconds)</option>
                  <option>Medium (30-60 seconds)</option>
                  <option>Long (1-2 minutes)</option>
                </select>
              </div>
              <div class="setting">
                <label class="setting-label">Resolution</label>
                <select class="setting-select">
                  <option>720p HD</option>
                  <option>1080p Full HD</option>
                  <option>4K Ultra HD</option>
                </select>
              </div>
              <div class="setting">
                <label class="setting-label">Background</label>
                <select class="setting-select">
                  <option>Studio Background</option>
                  <option>Office Environment</option>
                  <option>Outdoor Scene</option>
                  <option>Custom Background</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        
        <div class="wizard-step">
          <div class="step-header">
            <div class="step-number">4</div>
            <h3 class="step-title">Preview & Generate</h3>
          </div>
          <div class="step-content">
            <div class="preview-section">
              <div class="preview-placeholder">
                <div class="preview-icon">🎬</div>
                <p class="preview-text">Video preview will appear here</p>
              </div>
              <div class="generation-actions">
                <button class="btn btn-outline">
                  <span class="btn-icon">▶️</span>
                  Preview Audio
                </button>
                <button class="btn btn-primary btn-lg">
                  <span class="btn-icon">⚡</span>
                  Generate Video
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="recent-generations">
        <h3 class="section-title">Recent Generations</h3>
        <div class="generations-list">
          <div class="generation-item">
            <div class="generation-info">
              <h4 class="generation-title">Welcome Video</h4>
              <p class="generation-details">Business You • 15 seconds • 1080p</p>
              <p class="generation-time">Generated 2 hours ago</p>
            </div>
            <div class="generation-actions">
              <button class="btn btn-sm btn-outline">Download</button>
              <button class="btn btn-sm btn-primary">Regenerate</button>
            </div>
          </div>
          <div class="generation-item">
            <div class="generation-info">
              <h4 class="generation-title">Product Introduction</h4>
              <p class="generation-details">Casual Me • 45 seconds • 720p</p>
              <p class="generation-time">Generated yesterday</p>
            </div>
            <div class="generation-actions">
              <button class="btn btn-sm btn-outline">Download</button>
              <button class="btn btn-sm btn-primary">Regenerate</button>
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
    
    .generation-wizard {
      display: flex;
      flex-direction: column;
      gap: 2rem;
      margin-bottom: 3rem;
    }
    
    .wizard-step {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      opacity: 0.6;
      transition: opacity 0.3s;
    }
    
    .wizard-step.active {
      opacity: 1;
    }
    
    .step-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    
    .step-number {
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
    
    .step-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
      margin: 0;
    }
    
    .avatar-selection {
      display: flex;
      gap: 1.5rem;
    }
    
    .avatar-option {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      padding: 1rem;
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
    
    .preview-placeholder {
      width: 100%;
      height: 300px;
      background: #f9fafb;
      border: 2px dashed #d1d5db;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1rem;
    }
    
    .preview-icon {
      font-size: 4rem;
    }
    
    .preview-text {
      font-size: 1.125rem;
      color: #6b7280;
      margin: 0;
    }
    
    .generation-actions {
      display: flex;
      gap: 1rem;
    }
    
    .recent-generations {
      background: #f9fafb;
      border-radius: 12px;
      padding: 2rem;
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
    
    .btn-sm {
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
    }
    
    .btn-icon {
      font-size: 1.25rem;
    }
    
    @media (max-width: 768px) {
      .avatar-selection {
        flex-direction: column;
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
    }
  `]
})
export class GenerationComponent {}