import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-avatars',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="avatars-container">
      <h1 class="page-title">My Avatars</h1>
      <p class="page-subtitle">Manage and view your AI avatars</p>
      
      <div class="avatars-grid">
        <div class="avatar-card">
          <div class="avatar-image">
            <div class="avatar-placeholder">👨‍💼</div>
          </div>
          <div class="avatar-info">
            <h3 class="avatar-name">Business You</h3>
            <p class="avatar-status status-active">Active</p>
            <p class="avatar-description">Professional avatar for business presentations</p>
            <div class="avatar-stats">
              <span class="stat">🎬 12 videos</span>
              <span class="stat">⏱️ 45 min trained</span>
            </div>
          </div>
        </div>
        
        <div class="avatar-card">
          <div class="avatar-image">
            <div class="avatar-placeholder">😎</div>
          </div>
          <div class="avatar-info">
            <h3 class="avatar-name">Casual Me</h3>
            <p class="avatar-status status-active">Active</p>
            <p class="avatar-description">Relaxed avatar for social media content</p>
            <div class="avatar-stats">
              <span class="stat">🎬 8 videos</span>
              <span class="stat">⏱️ 30 min trained</span>
            </div>
          </div>
        </div>
        
        <div class="avatar-card">
          <div class="avatar-image">
            <div class="avatar-placeholder">🎭</div>
          </div>
          <div class="avatar-info">
            <h3 class="avatar-name">Creative Self</h3>
            <p class="avatar-status status-training">Training</p>
            <p class="avatar-description">Artistic avatar for creative projects</p>
            <div class="avatar-stats">
              <span class="stat">🎬 4 videos</span>
              <span class="stat">⏱️ 75 min trained</span>
            </div>
          </div>
        </div>
        
        <div class="avatar-card add-new">
          <div class="add-new-content">
            <div class="add-icon">+</div>
            <h3 class="add-title">Create New Avatar</h3>
            <p class="add-description">Start training a new AI avatar</p>
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
export class AvatarsComponent {}