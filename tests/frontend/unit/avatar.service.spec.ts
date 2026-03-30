import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AvatarService, Avatar, CreateAvatarRequest } from '../../../frontend/src/application/services/avatar.service';
import { ApiResponse } from '../../../frontend/src/infrastructure/api/api-client.service';

describe('AvatarService', () => {
  let service: AvatarService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AvatarService]
    });

    service = TestBed.inject(AvatarService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getAvatars', () => {
    it('should return avatars from API', () => {
      const mockAvatars: Avatar[] = [
        {
          id: '1',
          name: 'Test Avatar 1',
          description: 'Test Description 1',
          status: 'active',
          trainedImages: 10,
          trainedVoice: true,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          name: 'Test Avatar 2',
          description: 'Test Description 2',
          status: 'training',
          trainedImages: 5,
          trainedVoice: false,
          createdAt: '2024-01-02T00:00:00Z',
          updatedAt: '2024-01-02T00:00:00Z'
        }
      ];

      const mockResponse: ApiResponse<Avatar[]> = {
        data: mockAvatars,
        success: true,
        message: 'Avatars retrieved successfully'
      };

      service.getAvatars().subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.data.length).toBe(2);
        expect(response.data[0].name).toBe('Test Avatar 1');
        expect(response.data[1].name).toBe('Test Avatar 2');
      });

      const req = httpMock.expectOne('/api/avatars');
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle API error', () => {
      const mockErrorResponse: ApiResponse<Avatar[]> = {
        data: [],
        success: false,
        message: 'Failed to retrieve avatars',
        errors: ['Internal server error']
      };

      service.getAvatars().subscribe(response => {
        expect(response.success).toBe(false);
        expect(response.errors).toContain('Internal server error');
      });

      const req = httpMock.expectOne('/api/avatars');
      req.flush(mockErrorResponse);
    });
  });

  describe('getAvatar', () => {
    it('should return a single avatar by ID', () => {
      const mockAvatar: Avatar = {
        id: '1',
        name: 'Test Avatar',
        description: 'Test Description',
        status: 'active',
        trainedImages: 15,
        trainedVoice: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      const mockResponse: ApiResponse<Avatar> = {
        data: mockAvatar,
        success: true,
        message: 'Avatar retrieved successfully'
      };

      service.getAvatar('1').subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.data.id).toBe('1');
        expect(response.data.name).toBe('Test Avatar');
      });

      const req = httpMock.expectOne('/api/avatars/1');
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });
  });

  describe('createAvatar', () => {
    it('should create a new avatar', () => {
      const createRequest: CreateAvatarRequest = {
        name: 'New Avatar',
        description: 'New Description',
        images: [new File([''], 'test.jpg')]
      };

      const mockAvatar: Avatar = {
        id: '3',
        name: 'New Avatar',
        description: 'New Description',
        status: 'training',
        trainedImages: 0,
        trainedVoice: false,
        createdAt: '2024-01-03T00:00:00Z',
        updatedAt: '2024-01-03T00:00:00Z'
      };

      const mockResponse: ApiResponse<Avatar> = {
        data: mockAvatar,
        success: true,
        message: 'Avatar created successfully'
      };

      service.createAvatar(createRequest).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.data.name).toBe('New Avatar');
        expect(response.data.status).toBe('training');
      });

      const req = httpMock.expectOne('/api/avatars');
      expect(req.request.method).toBe('POST');
      
      // Check that FormData was sent
      expect(req.request.body instanceof FormData).toBe(true);
      
      req.flush(mockResponse);
    });
  });

  describe('updateAvatar', () => {
    it('should update an existing avatar', () => {
      const updateRequest = {
        name: 'Updated Avatar',
        description: 'Updated Description'
      };

      const mockAvatar: Avatar = {
        id: '1',
        name: 'Updated Avatar',
        description: 'Updated Description',
        status: 'active',
        trainedImages: 15,
        trainedVoice: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-03T00:00:00Z'
      };

      const mockResponse: ApiResponse<Avatar> = {
        data: mockAvatar,
        success: true,
        message: 'Avatar updated successfully'
      };

      service.updateAvatar('1', updateRequest).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.data.name).toBe('Updated Avatar');
        expect(response.data.description).toBe('Updated Description');
      });

      const req = httpMock.expectOne('/api/avatars/1');
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(updateRequest);
      req.flush(mockResponse);
    });
  });

  describe('deleteAvatar', () => {
    it('should delete an avatar', () => {
      const mockResponse: ApiResponse<void> = {
        data: null as any,
        success: true,
        message: 'Avatar deleted successfully'
      };

      service.deleteAvatar('1').subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.success).toBe(true);
      });

      const req = httpMock.expectOne('/api/avatars/1');
      expect(req.request.method).toBe('DELETE');
      req.flush(mockResponse);
    });
  });

  describe('startTraining', () => {
    it('should start training for an avatar', () => {
      const mockResponse: ApiResponse<void> = {
        data: null as any,
        success: true,
        message: 'Training started successfully'
      };

      service.startTraining('1').subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.success).toBe(true);
      });

      const req = httpMock.expectOne('/api/avatars/1/train');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({});
      req.flush(mockResponse);
    });
  });

  describe('getTrainingProgress', () => {
    it('should get training progress for an avatar', () => {
      const mockProgress = {
        progress: 0.5,
        status: 'training'
      };

      const mockResponse: ApiResponse<{ progress: number; status: string }> = {
        data: mockProgress,
        success: true,
        message: 'Progress retrieved successfully'
      };

      service.getTrainingProgress('1').subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.data.progress).toBe(0.5);
        expect(response.data.status).toBe('training');
      });

      const req = httpMock.expectOne('/api/avatars/1/training-progress');
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });
  });

  describe('generateVideo', () => {
    it('should generate a video for an avatar', () => {
      const text = 'Hello, this is a test video.';
      const options = {
        voiceStyle: 'professional',
        background: 'studio'
      };

      const mockResponse: ApiResponse<{ taskId: string }> = {
        data: { taskId: 'video-task-123' },
        success: true,
        message: 'Video generation started'
      };

      service.generateVideo('1', text, options).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.data.taskId).toBe('video-task-123');
      });

      const req = httpMock.expectOne('/api/avatars/1/generate');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({ text, ...options });
      req.flush(mockResponse);
    });
  });
});