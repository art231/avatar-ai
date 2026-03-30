import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="dashboard-container">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Overview of your AI avatars and activities</p>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👤</div>
          <div class="stat-content">
            <h3 class="stat-title">Active Avatars</h3>
            <p class="stat-value">3</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎬</div>
          <div class="stat-content">
            <h3 class="stat-title">Videos Generated</h3>
            <p class="stat-value">24</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <h3 class="stat-title">Training Time</h3>
            <p class="stat-value">2h 30m</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💾</div>
          <div class="stat-content">
            <h3 class="stat-title">Storage Used</h3>
            <p class="stat-value">1.2 GB</p>
          </div>
        </div>
      </div>
      
      <div class="recent-activity">
        <h2 class="section-title">Recent Activity</h2>
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-icon">✅</div>
            <div class="activity-content">
              <h4 class="activity-title">Avatar "Business You" trained successfully</h4>
              <p class="activity-time">2 hours ago</p>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon">🎥</div>
            <div class="activity-content">
              <h4 class="activity-title">Video generation completed</h4>
              <p class="activity-time">Yesterday, 3:45 PM</p>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon">📤</div>
            <div class="activity-content">
              <h4 class="activity-title">Uploaded 15 training images</h4>
              <p class="activity-time">2 days ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
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
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }
    
    .stat-card {
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s;
    }
    
    .stat-card:hover {
      transform: translateY(-2px);
    }
    
    .stat-icon {
      font-size: 2.5rem;
    }
    
    .stat-content {
      flex: 1;
    }
    
    .stat-title {
      font-size: 0.875rem;
      color: #6b7280;
      margin-bottom: 0.25rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .stat-value {
      font-size: 1.875rem;
      font-weight: 700;
      color: #1f2937;
      margin: 0;
    }
    
    .recent-activity {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: #1f2937;
    }
    
    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .activity-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1rem;
      border-radius: 8px;
      background: #f9fafb;
      transition: background-color 0.3s;
    }
    
    .activity-item:hover {
      background: #f3f4f6;
    }
    
    .activity-icon {
      font-size: 1.5rem;
    }
    
    .activity-content {
      flex: 1;
    }
    
    .activity-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
      color: #1f2937;
    }
    
    .activity-time {
      font-size: 0.875rem;
      color: #6b7280;
      margin: 0;
    }
    
    @media (max-width: 768px) {
      .stats-grid {
        grid-template-columns: 1fr;
      }
      
      .page-title {
        font-size: 2rem;
      }
    }
  `]
})
export class DashboardComponent {}