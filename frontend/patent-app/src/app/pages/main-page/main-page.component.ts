import { Component, DestroyRef, inject, signal } from '@angular/core';
import { AsyncPipe, CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { TuiInputFiles, TuiFiles, TuiFile } from '@taiga-ui/kit';
import { TuiButton } from '@taiga-ui/core';
import { map, startWith, catchError, of } from 'rxjs';
import { ApiService, PatentUploadResponse } from '../../services/api.service';

@Component({
  selector: 'app-main-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    TuiInputFiles,
    TuiFiles,
    TuiFile,
    TuiButton,
    AsyncPipe
  ],
  templateUrl: './main-page.component.html',
  styleUrl: './main-page.component.css'
})
export class MainPageComponent {
  readonly control = new FormControl<File | null>(null);
  private destroyRef = inject(DestroyRef);
  private apiService = inject(ApiService);

  readonly file$ = this.control.valueChanges.pipe(
    startWith(this.control.value),
    map(file => file || null),
    takeUntilDestroyed(this.destroyRef)
  );

  readonly uploadProgress = signal<number>(0);
  readonly isUploading = signal<boolean>(false);
  readonly uploadStatus = signal<string>('');

  onReject(files: File | readonly File[]): void {
    const rejectedFile = Array.isArray(files) ? files[0] : files;
    console.log('Rejected file:', rejectedFile);
    this.control.setValue(null);
  }

  uploadFile(): void {
    const file = this.control.value;
    if (!file) {
      this.uploadStatus.set('Please select a file first');
      return;
    }

    this.isUploading.set(true);
    this.uploadProgress.set(0);
    this.uploadStatus.set('Uploading...');

    this.apiService.uploadPatent(file)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        catchError((error: any) => {
          this.uploadStatus.set(`Error: ${error.error?.error || error.message || 'Upload failed'}`);
          this.isUploading.set(false);
          this.uploadProgress.set(0);
          return of(null);
        })
      )
      .subscribe((result: PatentUploadResponse | null) => {
        if (result) {
          this.uploadStatus.set(result.message || 'Upload successful!');
          this.uploadProgress.set(100);
          this.isUploading.set(false);
          // Clear the file after successful upload
          setTimeout(() => {
            this.control.setValue(null);
            this.uploadStatus.set('');
            this.uploadProgress.set(0);
          }, 2000);
        }
      });
  }
}

