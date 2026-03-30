import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="home-container">
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">Create Your AI Avatar</h1>
          <p class="hero-subtitle">
            Transform your photos and voice into a personalized AI avatar that can speak, move, and express emotions.
          </p>
          <div class="hero-actions">
            <button routerLink="/training" class="btn btn-primary btn-lg">
              Start Training
            </button>
            <button routerLink="/generation" class="btn btn-outline btn-lg">
              Try Demo
            </button>
          </div>
        </div>
        <div class="hero-image">
          <div class="avatar-preview">
            <div class="avatar-placeholder">
              <span class="avatar-icon">🤖</span>
            </div>
          </div>
        </div>
      </section>

      <section class="features-section">
        <h2 class="section-title">Powerful Features</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🎭</div>
            <h3 class="feature-title">Face Analysis</h3>
            <p class="feature-description">
              Advanced AI analyzes facial features and expressions from your photos.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎤</div>
            <h3 class="feature-title">Voice Cloning</h3>
            <p class="feature-description">
              Create a perfect voice clone from just a few seconds of audio.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">👄</div>
            <h3 class="feature-title">Lip Sync</h3>
            <p class="feature-description">
              Realistic lip synchronization with advanced MuseTalk technology.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎬</div>
            <h3 class="feature-title">Video Generation</h3>
            <p class="feature-description">
              Generate high-quality videos with natural movements and expressions.
            </p>
          </div>
        </div>
      </section>

      <section class="how-it-works">
        <h2 class="section-title">How It Works</h2>
        <div class="steps-container">
          <div class="step">
            <div class="step-number">1</div>
            <h3 class="step-title">Upload Photos & Voice</h3>
            <p class="step-description">
              Upload 10-20 photos and a short voice sample for training.
            </p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h3 class="step-title">AI Training</h3>
            <p class="step-description">
              Our AI models analyze and learn your unique features.
            </p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h3 class="step-title">Generate Content</h3>
            <p class="step-description">
              Create videos with your avatar speaking any text you provide.
            </p>
          </div>
        </div>
      </section>

      <section class="cta-section">
        <h2 class="cta-title">Ready to Create Your Avatar?</h2>
        <p class="cta-description">
          Join thousands of users who have already created their AI avatars.
        </p>
        <button routerLink="/training" class="btn btn-primary btn-xl">
          Get Started Free
        </button>
      </section>
    </div>
  `,
  styles: [`
    .home-container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .hero-section {
      display: flex;
      align-items: center;
      gap: 4rem;
      margin-bottom: 4rem;
      padding: 2rem 0;
    }
    
    .hero-content {
      flex: 1;
    }
    
    .hero-title {
      font-size: 3rem;
      font-weight: 800;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .hero-subtitle {
      font-size: 1.25rem;
      color: #6b7280;
      margin-bottom: 2rem;
      line-height: 1.6;
    }
    
    .hero-actions {
      display: flex;
      gap: 1rem;
    }
    
    .hero-image {
      flex: 1;
      display: flex;
      justify-content: center;
    }
    
    .avatar-preview {
      width: 300px;
      height: 300px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .avatar-placeholder {
      width: 250px;
      height: 250px;
      background: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .avatar-icon {
      font-size: 8rem;
    }
    
    .features-section {
      margin-bottom: 4rem;
    }
    
    .section-title {
      font-size: 2.5rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 3rem;
      color: #1f2937;
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;
    }
    
    .feature-card {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      text-align: center;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .feature-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    
    .feature-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
    
    .feature-title {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .feature-description {
      color: #6b7280;
      line-height: 1.5;
    }
    
    .how-it-works {
      margin-bottom: 4rem;
    }
    
    .steps-container {
      display: flex;
      justify-content: space-between;
      gap: 2rem;
    }
    
    .step {
      flex: 1;
      text-align: center;
      padding: 2rem;
    }
    
    .step-number {
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      font-weight: 700;
      margin: 0 auto 1.5rem;
    }
    
    .step-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }
    
    .step-description {
      color: #6b7280;
      line-height: 1.5;
    }
    
    .cta-section {
      text-align: center;
      padding: 4rem 2rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 20px;
      color: white;
      margin-bottom: 2rem;
    }
    
    .cta-title {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 1rem;
    }
    
    .cta-description {
      font-size: 1.25rem;
      margin-bottom: 2rem;
      opacity: 0.9;
    }
    
    .btn {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.3s;
      font-size: 1rem;
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
    
    .btn-xl {
      padding: 1.25rem 2.5rem;
      font-size: 1.25rem;
    }
    
    @media (max-width: 768px) {
      .hero-section {
        flex-direction: column;
        text-align: center;
      }
      
      .hero-actions {
        justify-content: center;
      }
      
      .steps-container {
        flex-direction: column;
      }
      
      .hero-title {
        font-size: 2.5rem;
      }
      
      .section-title {
        font-size: 2rem;
      }
    }
  `]
})
export class HomeComponent {}