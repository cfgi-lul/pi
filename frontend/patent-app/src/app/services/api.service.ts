import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType, HttpProgressEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

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
  private readonly apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}
  uploadPatent(file: File): Observable<PatentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<PatentUploadResponse>(
      `${this.apiUrl}/patent`,
      formData,
      {
        reportProgress: true,
        observe: 'events'
      }
    ).pipe(
      map((event: HttpEvent<PatentUploadResponse>) => {
        if (event.type === HttpEventType.Response) {
          return event.body!;
        }
        throw new Error('Unexpected event type');
      })
    );
  }
}

