import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PatentUploadResponse {
  message: string;
  status: string;
}

export interface PatentUploadError {
  error: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly apiUrl = '/api';

  constructor(private http: HttpClient) {}

  uploadPatent(file: File): Observable<PatentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<PatentUploadResponse>(
      `${this.apiUrl}/patent`,
      formData
    );
  }
}

