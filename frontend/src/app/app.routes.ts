import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AvatarsComponent } from './pages/avatars/avatars.component';
import { TrainingComponent } from './pages/training/training.component';
import { GenerationComponent } from './pages/generation/generation.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'avatars', component: AvatarsComponent },
  { path: 'training', component: TrainingComponent },
  { path: 'generation', component: GenerationComponent },
  { path: '**', redirectTo: '' }
];