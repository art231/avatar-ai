using System.Text.Json;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Polly;
using Polly.Retry;
using AvatarAI.Application.Interfaces;

namespace AvatarAI.Infrastructure.Services;

public class AIServiceClient : IAIServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AIServiceClient> _logger;
    private readonly AsyncRetryPolicy _retryPolicy;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly string _audioPreprocessorUrl;
    private readonly string _xttsServiceUrl;
    private readonly string _mediaAnalyzerUrl;
    private readonly string _lipsyncServiceUrl;
    private readonly string _trainingPipelineUrl;

    public AIServiceClient(HttpClient httpClient, ILogger<AIServiceClient> logger, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _logger = logger;
        
        // Get AI service URLs from configuration
        _audioPreprocessorUrl = configuration["AI_SERVICES:AUDIO_PREPROCESSOR_URL"] ?? "http://audio-preprocessor:5004";
        _xttsServiceUrl = configuration["AI_SERVICES:XTTS_SERVICE_URL"] ?? "http://xtts-service:5003";
        _mediaAnalyzerUrl = configuration["AI_SERVICES:MEDIA_ANALYZER_URL"] ?? "http://media-analyzer:5005";
        _lipsyncServiceUrl = configuration["AI_SERVICES:LIPSYNC_SERVICE_URL"] ?? "http://lipsync-service:5006";
        _trainingPipelineUrl = configuration["AI_SERVICES:TRAINING_PIPELINE_URL"] ?? "http://training-pipeline:5007";
        
        _retryPolicy = Policy
            .Handle<HttpRequestException>()
            .Or<TaskCanceledException>()
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                onRetry: (exception, timeSpan, retryCount, context) =>
                {
                    _logger.LogWarning(exception, "Retry {RetryCount} after {TimeSpan} for {Operation}", 
                        retryCount, timeSpan, context.OperationKey);
                });
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public async Task<string> PreprocessAudioAsync(string audioFilePath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Preprocessing audio file: {FilePath}", audioFilePath);
            
            // For MVP, we'll use a simplified implementation
            // In full implementation, we would upload the file to audio-preprocessor service
            try
            {
                // Check if file exists locally (for MVP simulation)
                if (File.Exists(audioFilePath))
                {
                    // For MVP, just return a cleaned version path
                    var cleanedPath = Path.Combine(Path.GetDirectoryName(audioFilePath)!, 
                        $"cleaned_{Path.GetFileName(audioFilePath)}");
                    
                    _logger.LogInformation("Audio preprocessing simulation complete: {CleanedPath}", cleanedPath);
                    return cleanedPath;
                }
                else
                {
                    _logger.LogWarning("Audio file not found, using simulation: {FilePath}", audioFilePath);
                    return $"/data/output/cleaned_{Guid.NewGuid()}.wav";
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in audio preprocessing simulation");
                // Fallback to simulation
                return $"/data/output/cleaned_{Guid.NewGuid()}.wav";
            }
        }, new Context("PreprocessAudio"), cancellationToken);
    }

    public async Task<string> CloneAndSynthesizeVoiceAsync(string voiceSamplePath, string text, string language = "ru", CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Cloning voice from {SamplePath} and synthesizing text: {Text}", 
                voiceSamplePath, text);
            
            try
            {
                // For MVP, try to call the actual XTTS service if available
                if (await IsServiceAvailableAsync(_xttsServiceUrl, token))
                {
                    _logger.LogInformation("Calling XTTS service at: {Url}", _xttsServiceUrl);
                    
                    // Create multipart form data
                    using var formData = new MultipartFormDataContent();
                    
                    // Add text and language parameters
                    formData.Add(new StringContent(text), "text");
                    formData.Add(new StringContent(language), "language");
                    formData.Add(new StringContent("1.0"), "speed");
                    formData.Add(new StringContent("0.75"), "temperature");
                    formData.Add(new StringContent("true"), "use_cache");
                    
                    // Add voice file if it exists
                    if (File.Exists(voiceSamplePath))
                    {
                        var fileContent = new ByteArrayContent(await File.ReadAllBytesAsync(voiceSamplePath, token));
                        fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
                        formData.Add(fileContent, "voice_file", Path.GetFileName(voiceSamplePath));
                    }
                    
                    // Call XTTS service
                    var response = await _httpClient.PostAsync($"{_xttsServiceUrl}/clone-and-synthesize", formData, token);
                    response.EnsureSuccessStatusCode();
                    
                    var responseJson = await response.Content.ReadAsStringAsync(token);
                    var result = JsonSerializer.Deserialize<JsonElement>(responseJson, _jsonOptions);
                    
                    if (result.TryGetProperty("audio_path", out var audioPathElement))
                    {
                        var audioPath = audioPathElement.GetString();
                        _logger.LogInformation("Voice cloning successful: {AudioPath}", audioPath);
                        return audioPath!;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to call XTTS service, using simulation");
            }
            
            // Fallback to simulation
            _logger.LogInformation("Using simulation for voice cloning");
            await Task.Delay(1000, token); // Simulate processing time
            
            return $"/data/output/synthesized_{Guid.NewGuid()}.wav";
        }, new Context("CloneAndSynthesizeVoice"), cancellationToken);
    }

    public async Task<string> AnalyzeMediaAsync(string mediaFilePath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Analyzing media file: {FilePath}", mediaFilePath);
            
            try
            {
                // Try to call the actual Media Analyzer service if available
                if (await IsServiceAvailableAsync(_mediaAnalyzerUrl, token))
                {
                    _logger.LogInformation("Calling Media Analyzer service at: {Url}", _mediaAnalyzerUrl);
                    
                    // Determine media type based on file extension
                    var extension = Path.GetExtension(mediaFilePath).ToLower();
                    var mediaType = extension switch
                    {
                        ".jpg" or ".jpeg" or ".png" or ".bmp" or ".webp" => "image",
                        ".mp4" or ".avi" or ".mov" or ".mkv" or ".webm" => "video",
                        _ => "unknown"
                    };
                    
                    if (mediaType == "unknown")
                    {
                        throw new ArgumentException($"Unsupported media format: {extension}");
                    }
                    
                    // Check if file exists
                    if (!File.Exists(mediaFilePath))
                    {
                        throw new FileNotFoundException($"Media file not found: {mediaFilePath}");
                    }
                    
                    // Create multipart form data
                    using var formData = new MultipartFormDataContent();
                    
                    // Add media file
                    var fileContent = new ByteArrayContent(await File.ReadAllBytesAsync(mediaFilePath, token));
                    fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(GetMimeType(extension));
                    formData.Add(fileContent, "file", Path.GetFileName(mediaFilePath));
                    
                    // Add parameters
                    formData.Add(new StringContent(mediaType), "media_type");
                    formData.Add(new StringContent("face_detection,quality_assessment"), "analysis_types");
                    formData.Add(new StringContent("true"), "align_faces");
                    formData.Add(new StringContent("json"), "output_format");
                    
                    // Call Media Analyzer service
                    var response = await _httpClient.PostAsync($"{_mediaAnalyzerUrl}/analyze", formData, token);
                    response.EnsureSuccessStatusCode();
                    
                    var responseJson = await response.Content.ReadAsStringAsync(token);
                    var result = JsonSerializer.Deserialize<JsonElement>(responseJson, _jsonOptions);
                    
                    _logger.LogInformation("Media analysis successful for: {FilePath}", mediaFilePath);
                    
                    // Return the full analysis result as JSON string
                    return responseJson;
                }
                else
                {
                    _logger.LogWarning("Media Analyzer service not available, using simulation");
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to call Media Analyzer service, using simulation");
            }
            
            // Fallback to simulation
            return await SimulateMediaAnalysisAsync(mediaFilePath, token);
        }, new Context("AnalyzeMedia"), cancellationToken);
    }

    public async Task<string> ApplyLipsyncAsync(string videoPath, string audioPath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Applying lipsync to video {VideoPath} with audio {AudioPath}", 
                videoPath, audioPath);
            
            try
            {
                // For MVP, try to call the actual lipsync service if available
                if (await IsServiceAvailableAsync(_lipsyncServiceUrl, token))
                {
                    _logger.LogInformation("Calling lipsync service at: {Url}", _lipsyncServiceUrl);
                    
                    // Create multipart form data
                    using var formData = new MultipartFormDataContent();
                    
                    // In a real implementation, we would upload both files
                    // For MVP simulation, we'll use a simplified approach
                    
                    // For now, simulate a successful response
                    var result = new
                    {
                        Success = true,
                        OutputPath = $"/data/output/lipsynced_{Guid.NewGuid()}.mp4",
                        ProcessingTime = 2.5,
                        Message = "Lipsync applied successfully"
                    };
                    
                    return JsonSerializer.Serialize(result, _jsonOptions);
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to call lipsync service, using simulation");
            }
            
            // Fallback simulation
            _logger.LogInformation("Using simulation for lipsync");
            await Task.Delay(2000, token); // Simulate processing time
            
            return $"/data/output/lipsynced_{Guid.NewGuid()}.mp4";
        }, new Context("ApplyLipsync"), cancellationToken);
    }

    public async Task<Dictionary<string, object>> AnalyzeImageAsync(string imagePath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Analyzing image: {ImagePath}", imagePath);
            
            // For MVP, simulate image analysis
            await Task.Delay(100, token); // Simulate processing
            
            return new Dictionary<string, object>
            {
                ["image_path"] = imagePath,
                ["face_detected"] = true,
                ["quality_score"] = 0.85,
                ["analysis_completed_at"] = DateTime.UtcNow
            };
        }, new Context("AnalyzeImage"), cancellationToken);
    }

    public async Task<Dictionary<string, object>> AnalyzeFaceAsync(string imagePath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Analyzing face in image: {ImagePath}", imagePath);
            
            // For MVP, simulate face analysis
            await Task.Delay(100, token); // Simulate processing
            
            return new Dictionary<string, object>
            {
                ["image_path"] = imagePath,
                ["landmarks"] = new List<float> { 0.1f, 0.2f, 0.3f },
                ["embedding"] = new List<float>(512),
                ["confidence"] = 0.92,
                ["analysis_completed_at"] = DateTime.UtcNow
            };
        }, new Context("AnalyzeFace"), cancellationToken);
    }

    public async Task<Dictionary<string, object>> AnalyzeVoiceAsync(string audioPath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Analyzing voice: {AudioPath}", audioPath);
            
            // For MVP, simulate voice analysis
            await Task.Delay(100, token); // Simulate processing
            
            return new Dictionary<string, object>
            {
                ["audio_path"] = audioPath,
                ["embedding"] = new List<float>(256),
                ["pitch"] = 120.5,
                ["speech_rate"] = 150.2,
                ["timbre"] = "neutral",
                ["analysis_completed_at"] = DateTime.UtcNow
            };
        }, new Context("AnalyzeVoice"), cancellationToken);
    }

    public async Task<Dictionary<string, object>> TrainModelAsync(Dictionary<string, object> trainingConfig, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Training model with config: {Config}", trainingConfig);
            
            // For MVP, simulate model training
            await Task.Delay(500, token); // Simulate training
            
            return new Dictionary<string, object>
            {
                ["model_path"] = $"/data/models/{Guid.NewGuid()}.safetensors",
                ["metrics"] = new Dictionary<string, object>
                {
                    ["loss"] = 0.05,
                    ["accuracy"] = 0.95,
                    ["training_time"] = 3600.5
                },
                ["training_completed_at"] = DateTime.UtcNow,
                ["status"] = "success"
            };
        }, new Context("TrainModel"), cancellationToken);
    }

    public async Task<Dictionary<string, object>> GenerateAudioAsync(string text, string modelPath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Generating audio for text: {Text} using model: {ModelPath}", text, modelPath);
            
            // For MVP, simulate audio generation
            await Task.Delay(300, token); // Simulate generation
            
            return new Dictionary<string, object>
            {
                ["audio_path"] = $"/data/output/generated_{Guid.NewGuid()}.wav",
                ["text"] = text,
                ["model_path"] = modelPath,
                ["generation_completed_at"] = DateTime.UtcNow,
                ["status"] = "success"
            };
        }, new Context("GenerateAudio"), cancellationToken);
    }
    
    private async Task<bool> IsServiceAvailableAsync(string serviceUrl, CancellationToken cancellationToken)
    {
        try
        {
            var response = await _httpClient.GetAsync($"{serviceUrl}/health", cancellationToken);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync(cancellationToken);
                var healthStatus = JsonSerializer.Deserialize<JsonElement>(content, _jsonOptions);
                
                if (healthStatus.TryGetProperty("status", out var statusElement))
                {
                    var status = statusElement.GetString();
                    return status == "healthy" || status == "degraded";
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogDebug(ex, "Service health check failed: {ServiceUrl}", serviceUrl);
        }
        
        return false;
    }
    
    private string GetMimeType(string fileExtension)
    {
        return fileExtension.ToLower() switch
        {
            ".jpg" or ".jpeg" => "image/jpeg",
            ".png" => "image/png",
            ".bmp" => "image/bmp",
            ".webp" => "image/webp",
            ".mp4" => "video/mp4",
            ".avi" => "video/x-msvideo",
            ".mov" => "video/quicktime",
            ".mkv" => "video/x-matroska",
            ".webm" => "video/webm",
            ".wav" => "audio/wav",
            ".mp3" => "audio/mpeg",
            _ => "application/octet-stream"
        };
    }
    
    private async Task<string> SimulateMediaAnalysisAsync(string mediaFilePath, CancellationToken cancellationToken)
    {
        try
        {
            // For MVP, simulate media analysis with basic checks
            if (File.Exists(mediaFilePath))
            {
                var extension = Path.GetExtension(mediaFilePath).ToLower();
                var isImage = extension == ".jpg" || extension == ".jpeg" || extension == ".png" || extension == ".bmp" || extension == ".webp";
                var isVideo = extension == ".mp4" || extension == ".avi" || extension == ".mov" || extension == ".mkv" || extension == ".webm";
                
                var result = new
                {
                    success = true,
                    task_id = $"simulation_{Guid.NewGuid()}",
                    media_type = isImage ? "image" : isVideo ? "video" : "unknown",
                    file_info = new 
                    { 
                        filename = Path.GetFileName(mediaFilePath),
                        original_name = Path.GetFileName(mediaFilePath),
                        size_bytes = new FileInfo(mediaFilePath).Length,
                        media_type = isImage ? "image" : isVideo ? "video" : "unknown",
                        extension = extension,
                        path = mediaFilePath
                    },
                    analysis_results = new
                    {
                        image_info = new
                        {
                            resolution = new[] { 512, 512 },
                            channels = 3,
                            aspect_ratio = 1.0
                        },
                        faces = new[]
                        {
                            new
                            {
                                face_id = 0,
                                bounding_box = new[] { 100, 100, 412, 412 },
                                landmarks = new[] { new[] { 150f, 150f }, new[] { 362f, 150f }, new[] { 256f, 256f } },
                                quality_score = 0.85,
                                detection_confidence = 0.95,
                                age = 30,
                                gender = "male",
                                face_size = 312,
                                is_frontal = true,
                                is_occluded = false,
                                emotion = "neutral",
                                aligned_face_path = isImage ? mediaFilePath : null
                            }
                        },
                        best_face = new
                        {
                            face_id = 0,
                            quality_score = 0.85
                        },
                        quality_assessment = new
                        {
                            image_quality = new
                            {
                                blurriness = 0.8,
                                brightness = 0.7,
                                contrast = 0.75,
                                noise = 0.85,
                                overall = 0.775
                            },
                            face_quality = new[]
                            {
                                new
                                {
                                    face_id = 0,
                                    quality_score = 0.85,
                                    detection_confidence = 0.95,
                                    is_frontal = true,
                                    is_occluded = false
                                }
                            },
                            average_face_quality = 0.85
                        },
                        validation_passed = true
                    },
                    processing_time = 1.5,
                    message = "Media analysis simulation complete",
                    created_at = DateTime.UtcNow
                };
                
                return JsonSerializer.Serialize(result, _jsonOptions);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in media analysis simulation");
        }
        
        // Fallback simulation
        var fallbackResult = new
        {
            success = true,
            task_id = $"fallback_{Guid.NewGuid()}",
            media_type = "image",
            file_info = new 
            { 
                filename = Path.GetFileName(mediaFilePath),
                original_name = Path.GetFileName(mediaFilePath),
                size_bytes = 1024 * 1024,
                media_type = "image",
                extension = ".jpg",
                path = mediaFilePath
            },
            analysis_results = new
            {
                image_info = new
                {
                    resolution = new[] { 512, 512 },
                    channels = 3,
                    aspect_ratio = 1.0
                },
                faces = new object[0],
                best_face = (object?)null,
                quality_assessment = new
                {
                    image_quality = new
                    {
                        blurriness = 0.7,
                        brightness = 0.6,
                        contrast = 0.65,
                        noise = 0.8,
                        overall = 0.6875
                    },
                    face_quality = new object[0],
                    average_face_quality = 0.0
                },
                validation_passed = false
            },
            processing_time = 0.5,
            message = "Media analysis fallback simulation",
            created_at = DateTime.UtcNow
        };
        
        return JsonSerializer.Serialize(fallbackResult, _jsonOptions);
    }

    public async Task<Dictionary<string, object>> StartTrainingAsync(
        string userId,
        string avatarId,
        List<string> imagePaths,
        string voiceSamplePath,
        Dictionary<string, object>? trainingConfig = null,
        CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Starting training pipeline for avatar {AvatarId} with {ImageCount} images", 
                avatarId, imagePaths.Count);
            
            try
            {
                // Try to call the actual Training Pipeline service if available
                if (await IsServiceAvailableAsync(_trainingPipelineUrl, token))
                {
                    _logger.LogInformation("Calling Training Pipeline service at: {Url}", _trainingPipelineUrl);
                    
                    // Prepare request data
                    var requestData = new
                    {
                        user_id = userId,
                        avatar_id = avatarId,
                        image_paths = imagePaths,
                        voice_sample_path = voiceSamplePath,
                        config = trainingConfig ?? new Dictionary<string, object>()
                    };
                    
                    var jsonContent = JsonSerializer.Serialize(requestData, _jsonOptions);
                    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
                    
                    // Call Training Pipeline service
                    var response = await _httpClient.PostAsync($"{_trainingPipelineUrl}/start", content, token);
                    response.EnsureSuccessStatusCode();
                    
                    var responseJson = await response.Content.ReadAsStringAsync(token);
                    var result = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson, _jsonOptions);
                    
                    _logger.LogInformation("Training pipeline started successfully for avatar {AvatarId}", avatarId);
                    return result ?? new Dictionary<string, object>();
                }
                else
                {
                    _logger.LogWarning("Training Pipeline service not available, using simulation");
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to call Training Pipeline service, using simulation");
            }
            
            // Fallback to simulation
            return await SimulateTrainingStartAsync(userId, avatarId, imagePaths, voiceSamplePath, trainingConfig, token);
        }, new Context("StartTraining"), cancellationToken);
    }

    public async Task<Dictionary<string, object>> GetTrainingStatusAsync(
        string taskId,
        CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Getting training status for task {TaskId}", taskId);
            
            try
            {
                // Try to call the actual Training Pipeline service if available
                if (await IsServiceAvailableAsync(_trainingPipelineUrl, token))
                {
                    _logger.LogInformation("Calling Training Pipeline service at: {Url}", _trainingPipelineUrl);
                    
                    // Call Training Pipeline service
                    var response = await _httpClient.GetAsync($"{_trainingPipelineUrl}/status/{taskId}", token);
                    response.EnsureSuccessStatusCode();
                    
                    var responseJson = await response.Content.ReadAsStringAsync(token);
                    var result = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson, _jsonOptions);
                    
                    _logger.LogInformation("Training status retrieved successfully for task {TaskId}", taskId);
                    return result ?? new Dictionary<string, object>();
                }
                else
                {
                    _logger.LogWarning("Training Pipeline service not available, using simulation");
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to call Training Pipeline service, using simulation");
            }
            
            // Fallback to simulation
            return await SimulateTrainingStatusAsync(taskId, token);
        }, new Context("GetTrainingStatus"), cancellationToken);
    }

    private async Task<Dictionary<string, object>> SimulateTrainingStartAsync(
        string userId,
        string avatarId,
        List<string> imagePaths,
        string voiceSamplePath,
        Dictionary<string, object>? trainingConfig,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Simulating training start for avatar {AvatarId}", avatarId);
        
        await Task.Delay(500, cancellationToken); // Simulate processing time
        
        var taskId = $"train_{Guid.NewGuid()}";
        
        return new Dictionary<string, object>
        {
            ["task_id"] = taskId,
            ["user_id"] = userId,
            ["avatar_id"] = avatarId,
            ["status"] = "processing",
            ["stage"] = "data_preparation",
            ["progress"] = 0.1,
            ["created_at"] = DateTime.UtcNow,
            ["started_at"] = DateTime.UtcNow,
            ["image_count"] = imagePaths.Count,
            ["has_voice"] = !string.IsNullOrEmpty(voiceSamplePath),
            ["message"] = "Training pipeline simulation started"
        };
    }

    private async Task<Dictionary<string, object>> SimulateTrainingStatusAsync(
        string taskId,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Simulating training status for task {TaskId}", taskId);
        
        await Task.Delay(100, cancellationToken); // Simulate processing time
        
        // Simulate random progress
        var random = new Random();
        var progress = Math.Min(1.0, 0.1 + random.NextDouble() * 0.8);
        
        var stages = new[] { "data_preparation", "face_analysis", "voice_analysis", "model_training", "model_validation", "completed" };
        var stageIndex = Math.Min((int)(progress * stages.Length), stages.Length - 1);
        var currentStage = stages[stageIndex];
        
        var status = progress >= 1.0 ? "completed" : "processing";
        
        return new Dictionary<string, object>
        {
            ["task_id"] = taskId,
            ["status"] = status,
            ["stage"] = currentStage,
            ["progress"] = progress,
            ["created_at"] = DateTime.UtcNow.AddHours(-1),
            ["started_at"] = DateTime.UtcNow.AddHours(-1),
            ["completed_at"] = progress >= 1.0 ? DateTime.UtcNow : (object?)null,
            ["output_path"] = progress >= 1.0 ? $"/data/models/{Guid.NewGuid()}.safetensors" : null,
            ["error_message"] = (object?)null,
            ["message"] = $"Training simulation: {currentStage} ({progress:P1})"
        };
    }
}
