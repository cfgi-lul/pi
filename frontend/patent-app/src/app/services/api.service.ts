import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface PatentUploadResponse {
  message: string;
  status: string;
  extracted_text?: string;
  metadata?: any;
  alloy_info?: string;
}

export interface PatentUploadError {
  error: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  uploadPatent(file: File): Observable<PatentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<PatentUploadResponse>(
      `${this.apiUrl}/patent`,
      formData
    ).pipe(
      catchError((error: HttpErrorResponse) => {
        const errorMessage = error.error?.detail || error.error?.error || error.message || 'Upload failed';
        return throwError(() => new Error(errorMessage));
      })
    );
  }
}

