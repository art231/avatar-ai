import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AvatarsComponent } from './pages/avatars/avatars.component';
import { AvatarDetailComponent } from './pages/avatars/avatar-detail.component';
import { TrainingComponent } from './pages/training/training.component';
import { GenerationComponent } from './pages/generation/generation.component';
import { LoginComponent } from './pages/auth/login.component';
import { RegisterComponent } from './pages/auth/register.component';
import { ForgotPasswordComponent } from './pages/auth/forgot-password.component';
import { AuthGuard, NoAuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Публичные роуты (только для неавторизованных)
  { 
    path: '', 
    component: HomeComponent,
    canActivate: [NoAuthGuard]
  },
  { 
    path: 'login', 
    component: LoginComponent,
    canActivate: [NoAuthGuard]
  },
  { 
    path: 'register', 
    component: RegisterComponent,
    canActivate: [NoAuthGuard]
  },
  { 
    path: 'forgot-password', 
    component: ForgotPasswordComponent,
    canActivate: [NoAuthGuard]
  },

  // Защищенные роуты (только для авторизованных)
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'avatars', 
    component: AvatarsComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'avatars/create', 
    loadComponent: () => import('./pages/avatars/avatar-create.component').then(m => m.AvatarCreateComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'avatars/:id', 
    component: AvatarDetailComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'training', 
    component: TrainingComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'generation', 
    component: GenerationComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'generation/tasks', 
    loadComponent: () => import('./pages/generation/task-list.component').then(m => m.TaskListComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'generation/tasks/:id', 
    loadComponent: () => import('./pages/generation/task-detail.component').then(m => m.TaskDetailComponent),
    canActivate: [AuthGuard]
  },

  // Роут для сброса пароля (будет добавлен позже)
  // { path: 'reset-password/:token', component: ResetPasswordComponent },

  // Редирект для несуществующих роутов
  { path: '**', redirectTo: '' }
];
