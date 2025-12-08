import { Component, DestroyRef, inject, signal } from '@angular/core';
import { AsyncPipe, CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { TuiInputFiles, TuiFiles, TuiFile } from '@taiga-ui/kit';
import { TuiButton, TuiScrollbar } from '@taiga-ui/core';
import { TuiTable } from '@taiga-ui/addon-table';
import { map, startWith, catchError, of } from 'rxjs';
import { ApiService, PatentUploadResponse } from '../../services/api.service';

interface UploadedFile {
  fileName: string;
  response: PatentUploadResponse | { error: string };
}

interface TableRow {
  fileName: string;
  [key: string]: string;
}

@Component({
  selector: 'app-main-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    TuiInputFiles,
    TuiFiles,
    TuiScrollbar,
    TuiFile,
    TuiButton,
    ...TuiTable,
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
  readonly uploadedFiles = signal<UploadedFile[]>([]);

  readonly tableData = signal<TableRow[]>([]);
  readonly propertyColumns = signal<string[]>([]);

  get columns(): string[] {
    return ['fileName', ...this.propertyColumns()];
  }

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
          const errorResponse = { error: error.error?.error || error.message || 'Upload failed' };
          this.addResponseToTable(file.name, errorResponse);
          this.uploadStatus.set(`Error: ${errorResponse.error}`);
          this.isUploading.set(false);
          this.uploadProgress.set(0);
          return of(null);
        })
      )
      .subscribe((result: PatentUploadResponse | null) => {
        if (result) {
          this.addResponseToTable(file.name, result);
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

  private addResponseToTable(fileName: string, response: PatentUploadResponse | { error: string }): void {
    const uploadedFile: UploadedFile = {
      fileName,
      response
    };

    this.uploadedFiles.update(files => [...files, uploadedFile]);

    // Create a row for this file with all properties
    const row: TableRow = { fileName };

    // Add all properties to the row
    Object.entries(response).forEach(([property, value]) => {
      row[property] = typeof value === 'object' ? JSON.stringify(value) : String(value);
    });

    // Update property columns to include any new properties
    this.propertyColumns.update(columns => {
      const newColumns = [...columns];
      Object.keys(response).forEach(property => {
        if (!newColumns.includes(property)) {
          newColumns.push(property);
        }
      });
      return newColumns;
    });

    // Add the new row
    this.tableData.update(data => [...data, row]);
  }
}

