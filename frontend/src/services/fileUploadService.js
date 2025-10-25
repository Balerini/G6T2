// src/services/fileUploadService.js
import { storage } from '../firebase.js';
import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';

class FileUploadService {
  async uploadFile(file, taskId, userId) {
    try {
      console.log('Starting file upload:', { fileName: file.name, taskId, userId });
      
      // Validate file before upload
      const validation = this.validateFile(file);
      if (!validation.valid) {
        throw new Error(validation.error);
      }
      
      // Create a unique filename with timestamp and user info
      const timestamp = Date.now();
      const sanitizedFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
      const fileName = `${timestamp}_${userId}_${sanitizedFileName}`;
      console.log('Generated filename:', fileName);
      
      // Create storage reference with simpler organization
      const storageRef = ref(storage, `tasks/${fileName}`);
      console.log('Storage reference created:', storageRef.fullPath);
      
      // Upload file
      console.log('Starting upload...');
      const snapshot = await uploadBytes(storageRef, file);
      console.log('Upload completed, getting download URL...');
      
      // Get download URL
      const downloadURL = await getDownloadURL(snapshot.ref);
      console.log('Download URL obtained:', downloadURL);
      
      const result = {
        id: `${taskId}_${timestamp}`, // Unique ID for the attachment
        name: file.name,
        originalName: file.name,
        size: file.size,
        type: file.type,
        downloadURL: downloadURL,
        storagePath: snapshot.ref.fullPath,
        uploadedAt: new Date().toISOString(),
        uploadedBy: userId,
        taskId: taskId
      };
      
      console.log('File upload result:', result);
      return result;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw new Error(`Failed to upload file: ${error.message}`);
    }
  }

  async uploadSubtaskFile(file, subtaskId, userId) {
    try {
      console.log('Starting subtask file upload:', { fileName: file.name, subtaskId, userId });
      
      // Validate file before upload
      const validation = this.validateFile(file);
      if (!validation.valid) {
        throw new Error(validation.error);
      }
      
      // Create a unique filename with timestamp and user info
      const timestamp = Date.now();
      const sanitizedFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
      const fileName = `${timestamp}_${userId}_${sanitizedFileName}`;
      console.log('Generated filename:', fileName);
      
      // Create storage reference for subtask files
      const storageRef = ref(storage, `subtask/${subtaskId}/attachments/${fileName}`);
      console.log('Storage reference created:', storageRef.fullPath);
      
      // Upload file
      console.log('Starting upload...');
      const snapshot = await uploadBytes(storageRef, file);
      console.log('Upload completed, getting download URL...');
      
      // Get download URL
      const downloadURL = await getDownloadURL(snapshot.ref);
      console.log('Download URL obtained:', downloadURL);
      
      const result = {
        id: `${subtaskId}_${timestamp}`, // Unique ID for the attachment
        name: file.name,
        originalName: file.name,
        size: file.size,
        type: file.type,
        downloadURL: downloadURL,
        storagePath: snapshot.ref.fullPath,
        uploadedAt: new Date().toISOString(),
        uploadedBy: userId,
        subtaskId: subtaskId
      };
      
      console.log('Subtask file upload result:', result);
      return result;
    } catch (error) {
      console.error('Error uploading subtask file:', error);
      throw new Error(`Failed to upload subtask file: ${error.message}`);
    }
  }

 
  async uploadMultipleFiles(files, taskId, userId) {
    try {
      console.log('Starting multiple file upload:', { fileCount: files.length, taskId, userId });
      const uploadPromises = files.map((file, index) => {
        console.log(`Uploading file ${index + 1}/${files.length}:`, file.name);
        return this.uploadFile(file, taskId, userId);
      });
      const uploadedFiles = await Promise.all(uploadPromises);
      console.log('All files uploaded successfully:', uploadedFiles);
      return uploadedFiles;
    } catch (error) {
      console.error('Error uploading multiple files:', error);
      throw new Error(`Failed to upload files: ${error.message}`);
    }
  }

  async uploadMultipleSubtaskFiles(files, subtaskId, userId) {
    try {
      console.log('Starting multiple subtask file upload:', { fileCount: files.length, subtaskId, userId });
      const uploadPromises = files.map((file, index) => {
        console.log(`Uploading subtask file ${index + 1}/${files.length}:`, file.name);
        return this.uploadSubtaskFile(file, subtaskId, userId);
      });
      const uploadedFiles = await Promise.all(uploadPromises);
      console.log('All subtask files uploaded successfully:', uploadedFiles);
      return uploadedFiles;
    } catch (error) {
      console.error('Error uploading multiple subtask files:', error);
      throw new Error(`Failed to upload subtask files: ${error.message}`);
    }
  }

 
  async deleteFile(storagePath) {
    try {
      const fileRef = ref(storage, storagePath);
      await deleteObject(fileRef);
    } catch (error) {
      console.error('Error deleting file:', error);
      throw new Error(`Failed to delete file: ${error.message}`);
    }
  }

  
  validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/png',
      'text/plain'
    ];

    if (file.size > maxSize) {
      return {
        valid: false,
        error: `File "${file.name}" is too large. Maximum size is 10MB`
      };
    }

    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `File type "${file.type}" is not allowed. Allowed types: PDF, DOC, DOCX, JPG, PNG, TXT`
      };
    }

    return { valid: true };
  }

  
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  getFileIcon(fileType) {
    if (fileType.startsWith('image/')) {
      return '🖼️';
    } else if (fileType.includes('pdf')) {
      return '📄';
    } else if (fileType.includes('word') || fileType.includes('document')) {
      return '📝';
    } else if (fileType.includes('text')) {
      return '📄';
    } else {
      return '📎';
    }
  }

  getFileTypeColor(fileType) {
    if (fileType.startsWith('image/')) {
      return '#10b981'; // Green
    } else if (fileType.includes('pdf')) {
      return '#ef4444'; // Red
    } else if (fileType.includes('word') || fileType.includes('document')) {
      return '#3b82f6'; // Blue
    } else if (fileType.includes('text')) {
      return '#6b7280'; // Gray
    } else {
      return '#8b5cf6'; // Purple
    }
  }

 
  async testStorageConnection() {
    try {
      console.log('Testing Firebase Storage connection...');
      const testRef = ref(storage, 'test/connection-test.txt');
      const testBlob = new Blob(['Firebase Storage Test'], { type: 'text/plain' });
      
      await uploadBytes(testRef, testBlob);
      console.log('Firebase Storage connection test successful');
      return true;
    } catch (error) {
      console.error('Firebase Storage connection test failed:', error);
      return false;
    }
  }
}

export const fileUploadService = new FileUploadService();
