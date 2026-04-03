import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink],
  template: `
    <div class="app-container">
      <header class="app-header">
        <div class="header-content">
          <h1 class="app-title">AvatarAI</h1>
          <nav class="app-nav">
            <a routerLink="/" class="nav-link">Home</a>
            <a routerLink="/dashboard" class="nav-link">Dashboard</a>
            <a routerLink="/avatars" class="nav-link">Avatars</a>
            <a routerLink="/training" class="nav-link">Training</a>
            <a routerLink="/generation" class="nav-link">Generation</a>
          </nav>
        </div>
      </header>
      
      <main class="app-main">
        <router-outlet></router-outlet>
      </main>
      
      <footer class="app-footer">
        <div class="footer-content">
          <p>AvatarAI &copy; 2024 - AI-powered avatar generation platform</p>
          <div class="footer-links">
            <a href="#" class="footer-link">Privacy Policy</a>
            <a href="#" class="footer-link">Terms of Service</a>
            <a href="#" class="footer-link">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    
    .app-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 1rem 2rem;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .app-title {
      font-size: 1.8rem;
      font-weight: bold;
      margin: 0;
    }
    
    .app-nav {
      display: flex;
      gap: 2rem;
    }
    
    .nav-link {
      color: white;
      text-decoration: none;
      font-weight: 500;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      transition: background-color 0.3s;
    }
    
    .nav-link:hover {
      background-color: rgba(255,255,255,0.1);
    }
    
    .app-main {
      flex: 1;
      padding: 2rem;
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }
    
    .app-footer {
      background-color: #f8f9fa;
      padding: 1.5rem 2rem;
      border-top: 1px solid #e9ecef;
    }
    
    .footer-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .footer-links {
      display: flex;
      gap: 1.5rem;
    }
    
    .footer-link {
      color: #6c757d;
      text-decoration: none;
      font-size: 0.9rem;
    }
    
    .footer-link:hover {
      color: #495057;
    }
    
    @media (max-width: 768px) {
      .header-content {
        flex-direction: column;
        gap: 1rem;
      }
      
      .app-nav {
        flex-wrap: wrap;
        justify-content: center;
      }
      
      .footer-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }
    }
  `]
})
export class AppComponent {
  title = 'AvatarAI';
}