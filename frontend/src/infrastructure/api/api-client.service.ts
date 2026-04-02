import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiClientService {
  private baseUrl = '/api';
  private isBrowser: boolean;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });

    // Добавляем токен авторизации, если он есть
    if (this.isBrowser) {
      const token = this.getAuthToken();
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }
    }

    return headers;
  }

  private getAuthToken(): string | null {
    if (!this.isBrowser) return null;
    return localStorage.getItem('access_token');
  }

  get<T>(endpoint: string, params?: any): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders(),
      params: this.createParams(params)
    };
    return this.http.get<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, options)
      .pipe(catchError(this.handleError));
  }

  post<T>(endpoint: string, body: any): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders()
    };
    return this.http.post<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, body, options)
      .pipe(catchError(this.handleError));
  }

  put<T>(endpoint: string, body: any): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders()
    };
    return this.http.put<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, body, options)
      .pipe(catchError(this.handleError));
  }

  delete<T>(endpoint: string): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders()
    };
    return this.http.delete<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, options)
      .pipe(catchError(this.handleError));
  }

  uploadFile<T>(endpoint: string, file: File, additionalData?: any): Observable<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });
    }

    let headers = new HttpHeaders();
    // Добавляем токен авторизации для загрузки файлов
    if (this.isBrowser) {
      const token = this.getAuthToken();
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }
    }

    return this.http.post<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, formData, { headers })
      .pipe(catchError(this.handleError));
  }

  private createParams(params: any): HttpParams {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return httpParams;
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'Произошла ошибка';
    
    if (error.error instanceof ErrorEvent) {
      // Клиентская ошибка
      errorMessage = `Ошибка: ${error.error.message}`;
    } else {
      // Серверная ошибка
      errorMessage = `Ошибка ${error.status}: ${error.message}`;
      
      if (error.status === 401) {
        errorMessage = 'Сессия истекла. Пожалуйста, войдите снова.';
        // Здесь можно вызвать refresh token или logout
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      } else if (error.status === 403) {
        errorMessage = 'Доступ запрещен';
      } else if (error.status === 404) {
        errorMessage = 'Ресурс не найден';
      } else if (error.status === 500) {
        errorMessage = 'Внутренняя ошибка сервера';
      }
    }
    
    console.error('API Error:', errorMessage, error);
    return throwError(() => new Error(errorMessage));
  }
}