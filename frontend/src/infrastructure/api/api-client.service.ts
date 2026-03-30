import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

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

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });

    // Здесь можно добавить токен авторизации
    // const token = this.authService.getToken();
    // if (token) {
    //   headers = headers.set('Authorization', `Bearer ${token}`);
    // }

    return headers;
  }

  get<T>(endpoint: string, params?: any): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders(),
      params: this.createParams(params)
    };
    return this.http.get<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, options);
  }

  post<T>(endpoint: string, body: any): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders()
    };
    return this.http.post<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, body, options);
  }

  put<T>(endpoint: string, body: any): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders()
    };
    return this.http.put<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, body, options);
  }

  delete<T>(endpoint: string): Observable<ApiResponse<T>> {
    const options = {
      headers: this.getHeaders()
    };
    return this.http.delete<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, options);
  }

  uploadFile<T>(endpoint: string, file: File, additionalData?: any): Observable<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });
    }

    const headers = new HttpHeaders();
    // Не устанавливаем Content-Type для FormData - браузер сделает это сам

    return this.http.post<ApiResponse<T>>(`${this.baseUrl}${endpoint}`, formData, { headers });
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
}