import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { ApiClientService, ApiResponse } from '../../infrastructure/api/api-client.service';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
  };
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'user';
  
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private apiClient: ApiClientService) {
    this.loadStoredAuth();
  }

  private loadStoredAuth(): void {
    const accessToken = this.getAccessToken();
    const user = this.getStoredUser();
    
    if (accessToken && user) {
      this.currentUserSubject.next(user);
      this.isAuthenticatedSubject.next(true);
    }
  }

  login(credentials: LoginRequest): Observable<ApiResponse<AuthResponse>> {
    return this.apiClient.post<AuthResponse>('/auth/login', credentials).pipe(
      map(response => response.data),
      tap(response => {
        this.handleAuthResponse(response.data);
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => error);
      })
    );
  }

  register(userData: RegisterRequest): Observable<ApiResponse<AuthResponse>> {
    return this.apiClient.post<AuthResponse>('/auth/register', userData).pipe(
      map(response => response.data),
      tap(response => {
        this.handleAuthResponse(response.data);
      }),
      catchError(error => {
        console.error('Registration error:', error);
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    this.clearAuth();
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }

  refreshToken(): Observable<ApiResponse<AuthResponse>> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      this.clearAuth();
      return throwError(() => new Error('No refresh token available'));
    }

    return this.apiClient.post<AuthResponse>('/auth/refresh', { refreshToken }).pipe(
      map(response => response.data),
      tap(response => {
        this.handleAuthResponse(response.data);
      }),
      catchError(error => {
        console.error('Token refresh error:', error);
        this.clearAuth();
        return throwError(() => error);
      })
    );
  }

  forgotPassword(email: string): Observable<ApiResponse<{ success: boolean; message: string }>> {
    return this.apiClient.post<{ success: boolean; message: string }>('/auth/forgot-password', { email }).pipe(
      map(response => response.data)
    );
  }

  resetPassword(token: string, newPassword: string): Observable<ApiResponse<{ success: boolean; message: string }>> {
    return this.apiClient.post<{ success: boolean; message: string }>('/auth/reset-password', {
      token,
      newPassword
    }).pipe(
      map(response => response.data)
    );
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isLoggedIn(): boolean {
    return this.isAuthenticatedSubject.value;
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  private handleAuthResponse(response: AuthResponse): void {
    this.setTokens(response.accessToken, response.refreshToken);
    this.setUser(response.user);
    this.currentUserSubject.next(response.user);
    this.isAuthenticatedSubject.next(true);
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  private setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  private getStoredUser(): User | null {
    const userJson = localStorage.getItem(this.USER_KEY);
    if (!userJson) return null;
    
    try {
      return JSON.parse(userJson);
    } catch {
      return null;
    }
  }

  private clearAuth(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  updateUserProfile(userData: Partial<User>): Observable<ApiResponse<User>> {
    return this.apiClient.put<User>('/auth/profile', userData).pipe(
      map(response => response.data),
        this.setUser(response.data);
        this.currentUserSubject.next(response.data);
      })
    );
  }

  changePassword(currentPassword: string, newPassword: string): Observable<ApiResponse<{ success: boolean; message: string }>> {
    return this.apiClient.post<{ success: boolean; message: string }>('/auth/change-password', {
      currentPassword,
      newPassword
    }).pipe(
      map(response => response.data)
    );
  }
}