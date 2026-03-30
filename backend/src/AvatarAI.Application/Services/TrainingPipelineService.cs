using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using AvatarAI.Application.Interfaces;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Enums;
using AvatarAI.Domain.Interfaces;

namespace AvatarAI.Application.Services
{
    public class TrainingPipelineService : ITrainingPipelineService
    {
        private readonly ILogger<TrainingPipelineService> _logger;
        private readonly IGenerationTaskRepository _taskRepository;
        private readonly ITaskLogRepository _taskLogRepository;
        private readonly IAvatarRepository _avatarRepository;
        private readonly IAIServiceClient _aiServiceClient;
        private readonly IBackgroundJobService _backgroundJobService;

        public TrainingPipelineService(
            ILogger<TrainingPipelineService> logger,
            IGenerationTaskRepository taskRepository,
            ITaskLogRepository taskLogRepository,
            IAvatarRepository avatarRepository,
            IAIServiceClient aiServiceClient,
            IBackgroundJobService backgroundJobService)
        {
            _logger = logger;
            _taskRepository = taskRepository;
            _taskLogRepository = taskLogRepository;
            _avatarRepository = avatarRepository;
            _aiServiceClient = aiServiceClient;
            _backgroundJobService = backgroundJobService;
        }

        public async Task<GenerationTask> StartTrainingPipelineAsync(
            Guid userId,
            Guid avatarId,
            List<string> imagePaths,
            string voiceSamplePath,
            string trainingConfig,
            CancellationToken cancellationToken = default)
        {
            try
            {
                _logger.LogInformation("Starting training pipeline for user {UserId}, avatar {AvatarId}", userId, avatarId);

                // Create new generation task
                var task = new GenerationTask
                {
                    Id = Guid.NewGuid(),
                    UserId = userId,
                    AvatarId = avatarId,
                    Status = TaskStatus.Pending,
                    Stage = TaskStage.DataPreparation,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow,
                    Metadata = new Dictionary<string, object>
                    {
                        ["image_paths"] = imagePaths,
                        ["voice_sample_path"] = voiceSamplePath,
                        ["training_config"] = trainingConfig,
                        ["total_stages"] = 5
                    }
                };

                await _taskRepository.AddAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                // Log task creation
                await LogTaskEventAsync(task.Id, "Training pipeline started", TaskStage.DataPreparation, cancellationToken);

                // Start pipeline in background
                _backgroundJobService.Enqueue(() => ExecuteTrainingPipelineAsync(task.Id, cancellationToken));

                return task;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to start training pipeline for user {UserId}, avatar {AvatarId}", userId, avatarId);
                throw;
            }
        }

        public async Task ExecuteTrainingPipelineAsync(Guid taskId, CancellationToken cancellationToken = default)
        {
            GenerationTask task = null;
            try
            {
                task = await _taskRepository.GetByIdAsync(taskId, cancellationToken);
                if (task == null)
                {
                    _logger.LogError("Task {TaskId} not found", taskId);
                    return;
                }

                _logger.LogInformation("Executing training pipeline for task {TaskId}", taskId);

                // Stage 1: Data Preparation
                await UpdateTaskStageAsync(task, TaskStage.DataPreparation, "Preparing training data", cancellationToken);
                var preparedData = await PrepareTrainingDataAsync(task, cancellationToken);

                // Stage 2: Face Analysis
                await UpdateTaskStageAsync(task, TaskStage.FaceAnalysis, "Analyzing facial features", cancellationToken);
                var faceAnalysis = await AnalyzeFaceAsync(task, preparedData, cancellationToken);

                // Stage 3: Voice Analysis
                await UpdateTaskStageAsync(task, TaskStage.VoiceAnalysis, "Analyzing voice sample", cancellationToken);
                var voiceAnalysis = await AnalyzeVoiceAsync(task, cancellationToken);

                // Stage 4: Model Training
                await UpdateTaskStageAsync(task, TaskStage.ModelTraining, "Training AI model", cancellationToken);
                var trainedModel = await TrainModelAsync(task, preparedData, faceAnalysis, voiceAnalysis, cancellationToken);

                // Stage 5: Model Validation
                await UpdateTaskStageAsync(task, TaskStage.ModelValidation, "Validating trained model", cancellationToken);
                var validationResult = await ValidateModelAsync(task, trainedModel, cancellationToken);

                // Complete task
                await CompleteTaskAsync(task, validationResult, cancellationToken);

                _logger.LogInformation("Training pipeline completed successfully for task {TaskId}", taskId);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Training pipeline failed for task {TaskId}", taskId);
                if (task != null)
                {
                    await FailTaskAsync(task, ex.Message, cancellationToken);
                }
            }
        }

        private async Task<Dictionary<string, object>> PrepareTrainingDataAsync(GenerationTask task, CancellationToken cancellationToken)
        {
            try
            {
                await LogTaskEventAsync(task.Id, "Starting data preparation", task.Stage, cancellationToken);

                // Call audio preprocessor service
                var audioPreprocessorResult = await _aiServiceClient.PreprocessAudioAsync(
                    task.Metadata["voice_sample_path"].ToString(),
                    cancellationToken);

                // Call media analyzer service for images
                var imageAnalysisResults = new List<Dictionary<string, object>>();
                var imagePaths = (List<string>)task.Metadata["image_paths"];

                foreach (var imagePath in imagePaths)
                {
                    var analysisResult = await _aiServiceClient.AnalyzeImageAsync(imagePath, cancellationToken);
                    imageAnalysisResults.Add(analysisResult);
                }

                var preparedData = new Dictionary<string, object>
                {
                    ["audio_preprocessed"] = audioPreprocessorResult,
                    ["image_analyses"] = imageAnalysisResults,
                    ["total_images"] = imagePaths.Count,
                    ["prepared_at"] = DateTime.UtcNow
                };

                // Update task metadata
                task.Metadata["prepared_data"] = preparedData;
                task.Progress = 0.2m; // 20% complete
                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, "Data preparation completed", task.Stage, cancellationToken);

                return preparedData;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Data preparation failed for task {TaskId}", task.Id);
                throw new Exception($"Data preparation failed: {ex.Message}", ex);
            }
        }

        private async Task<Dictionary<string, object>> AnalyzeFaceAsync(
            GenerationTask task,
            Dictionary<string, object> preparedData,
            CancellationToken cancellationToken)
        {
            try
            {
                await LogTaskEventAsync(task.Id, "Starting face analysis", task.Stage, cancellationToken);

                var imageAnalyses = (List<Dictionary<string, object>>)preparedData["image_analyses"];
                var faceAnalysisResults = new List<Dictionary<string, object>>();

                foreach (var imageAnalysis in imageAnalyses)
                {
                    // Call media analyzer service for detailed face analysis
                    var faceAnalysis = await _aiServiceClient.AnalyzeFaceAsync(
                        imageAnalysis["image_path"].ToString(),
                        cancellationToken);

                    faceAnalysisResults.Add(faceAnalysis);
                }

                // Aggregate face analysis results
                var aggregatedAnalysis = new Dictionary<string, object>
                {
                    ["face_analyses"] = faceAnalysisResults,
                    ["average_landmarks"] = CalculateAverageLandmarks(faceAnalysisResults),
                    ["dominant_features"] = ExtractDominantFeatures(faceAnalysisResults),
                    ["analysis_completed_at"] = DateTime.UtcNow
                };

                // Update task metadata
                task.Metadata["face_analysis"] = aggregatedAnalysis;
                task.Progress = 0.4m; // 40% complete
                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, "Face analysis completed", task.Stage, cancellationToken);

                return aggregatedAnalysis;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Face analysis failed for task {TaskId}", task.Id);
                throw new Exception($"Face analysis failed: {ex.Message}", ex);
            }
        }

        private async Task<Dictionary<string, object>> AnalyzeVoiceAsync(GenerationTask task, CancellationToken cancellationToken)
        {
            try
            {
                await LogTaskEventAsync(task.Id, "Starting voice analysis", task.Stage, cancellationToken);

                var preparedData = (Dictionary<string, object>)task.Metadata["prepared_data"];
                var audioPreprocessed = (Dictionary<string, object>)preparedData["audio_preprocessed"];

                // Call XTTS service for voice analysis
                var voiceAnalysis = await _aiServiceClient.AnalyzeVoiceAsync(
                    audioPreprocessed["processed_audio_path"].ToString(),
                    cancellationToken);

                var voiceProfile = new Dictionary<string, object>
                {
                    ["voice_analysis"] = voiceAnalysis,
                    ["voice_characteristics"] = ExtractVoiceCharacteristics(voiceAnalysis),
                    ["voice_embedding"] = voiceAnalysis.GetValueOrDefault("embedding", new List<float>()),
                    ["analysis_completed_at"] = DateTime.UtcNow
                };

                // Update task metadata
                task.Metadata["voice_analysis"] = voiceProfile;
                task.Progress = 0.6m; // 60% complete
                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, "Voice analysis completed", task.Stage, cancellationToken);

                return voiceProfile;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Voice analysis failed for task {TaskId}", task.Id);
                throw new Exception($"Voice analysis failed: {ex.Message}", ex);
            }
        }

        private async Task<Dictionary<string, object>> TrainModelAsync(
            GenerationTask task,
            Dictionary<string, object> preparedData,
            Dictionary<string, object> faceAnalysis,
            Dictionary<string, object> voiceAnalysis,
            CancellationToken cancellationToken)
        {
            try
            {
                await LogTaskEventAsync(task.Id, "Starting model training", task.Stage, cancellationToken);

                // Prepare training configuration
                var trainingConfig = new Dictionary<string, object>
                {
                    ["face_analysis"] = faceAnalysis,
                    ["voice_analysis"] = voiceAnalysis,
                    ["training_data"] = preparedData,
                    ["config"] = task.Metadata["training_config"],
                    ["task_id"] = task.Id.ToString()
                };

                // Call LoRA trainer service
                var trainingResult = await _aiServiceClient.TrainModelAsync(trainingConfig, cancellationToken);

                var trainedModel = new Dictionary<string, object>
                {
                    ["training_result"] = trainingResult,
                    ["model_path"] = trainingResult.GetValueOrDefault("model_path", ""),
                    ["training_metrics"] = trainingResult.GetValueOrDefault("metrics", new Dictionary<string, object>()),
                    ["training_completed_at"] = DateTime.UtcNow
                };

                // Update task metadata
                task.Metadata["trained_model"] = trainedModel;
                task.Progress = 0.8m; // 80% complete
                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, "Model training completed", task.Stage, cancellationToken);

                return trainedModel;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Model training failed for task {TaskId}", task.Id);
                throw new Exception($"Model training failed: {ex.Message}", ex);
            }
        }

        private async Task<Dictionary<string, object>> ValidateModelAsync(
            GenerationTask task,
            Dictionary<string, object> trainedModel,
            CancellationToken cancellationToken)
        {
            try
            {
                await LogTaskEventAsync(task.Id, "Starting model validation", task.Stage, cancellationToken);

                // Generate test samples using the trained model
                var testSamples = await GenerateTestSamplesAsync(task, trainedModel, cancellationToken);

                // Validate generated samples
                var validationResults = await ValidateSamplesAsync(testSamples, cancellationToken);

                var validationResult = new Dictionary<string, object>
                {
                    ["test_samples"] = testSamples,
                    ["validation_results"] = validationResults,
                    ["overall_quality"] = CalculateOverallQuality(validationResults),
                    ["validation_passed"] = validationResults.GetValueOrDefault("passed", false),
                    ["validation_completed_at"] = DateTime.UtcNow
                };

                // Update task metadata
                task.Metadata["validation_result"] = validationResult;
                task.Progress = 0.9m; // 90% complete
                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, "Model validation completed", task.Stage, cancellationToken);

                return validationResult;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Model validation failed for task {TaskId}", task.Id);
                throw new Exception($"Model validation failed: {ex.Message}", ex);
            }
        }

        private async Task CompleteTaskAsync(
            GenerationTask task,
            Dictionary<string, object> validationResult,
            CancellationToken cancellationToken)
        {
            try
            {
                // Update avatar with trained model
                var avatar = await _avatarRepository.GetByIdAsync(task.AvatarId, cancellationToken);
                if (avatar != null)
                {
                    var trainedModel = (Dictionary<string, object>)task.Metadata["trained_model"];
                    var voiceAnalysis = (Dictionary<string, object>)task.Metadata["voice_analysis"];

                    avatar.ModelPath = trainedModel["model_path"].ToString();
                    avatar.VoiceProfile = voiceAnalysis;
                    avatar.Status = AvatarStatus.Trained;
                    avatar.UpdatedAt = DateTime.UtcNow;

                    await _avatarRepository.UpdateAsync(avatar, cancellationToken);
                }

                // Update task status
                task.Status = TaskStatus.Completed;
                task.Stage = TaskStage.Completed;
                task.Progress = 1.0m;
                task.CompletedAt = DateTime.UtcNow;
                task.UpdatedAt = DateTime.UtcNow;

                task.Metadata["completed_at"] = DateTime.UtcNow;
                task.Metadata["validation_passed"] = validationResult.GetValueOrDefault("validation_passed", false);
                task.Metadata["overall_quality"] = validationResult.GetValueOrDefault("overall_quality", 0.0);

                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, "Training pipeline completed successfully", task.Stage, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to complete task {TaskId}", task.Id);
                throw;
            }
        }

        private async Task FailTaskAsync(GenerationTask task, string errorMessage, CancellationToken cancellationToken)
        {
            try
            {
                task.Status = TaskStatus.Failed;
                task.ErrorMessage = errorMessage;
                task.CompletedAt = DateTime.UtcNow;
                task.UpdatedAt = DateTime.UtcNow;

                await _taskRepository.UpdateAsync(task, cancellationToken);
                await _taskRepository.SaveChangesAsync(cancellationToken);

                await LogTaskEventAsync(task.Id, $"Training pipeline failed: {errorMessage}", task.Stage, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to mark task {TaskId} as failed", task.Id);
            }
        }

        private async Task UpdateTaskStageAsync(
            GenerationTask task,
            TaskStage stage,
            string stageDescription,
            CancellationToken cancellationToken)
        {
            task.Stage = stage;
            task.UpdatedAt = DateTime.UtcNow;

            await _taskRepository.UpdateAsync(task, cancellationToken);
            await _taskRepository.SaveChangesAsync(cancellationToken);

            await LogTaskEventAsync(task.Id, stageDescription, stage, cancellationToken);
        }

        private async Task LogTaskEventAsync(
            Guid taskId,
            string message,
            TaskStage stage,
            CancellationToken cancellationToken)
        {
            var taskLog = new TaskLog
            {
                Id = Guid.NewGuid(),
                TaskId = taskId,
                Stage = stage,
                Message = message,
                CreatedAt = DateTime.UtcNow
            };

            await _taskLogRepository.AddAsync(taskLog, cancellationToken);
            await _taskLogRepository.SaveChangesAsync(cancellationToken);
        }

        #region Helper Methods

        private Dictionary<string, object> CalculateAverageLandmarks(List<Dictionary<string, object>> faceAnalyses)
        {
            // Simplified implementation - in production would calculate actual averages
            return new Dictionary<string, object>
            {
                ["landmark_count"] = faceAnalyses.Count,
                ["average_confidence"] = faceAnalyses.Average(f => Convert.ToDouble(f.GetValueOrDefault("confidence", 0.0))),
                ["calculated_at"] = DateTime.UtcNow
            };
        }

        private Dictionary<string, object> ExtractDominantFeatures(List<Dictionary<string, object>> faceAnalyses)
        {
            // Simplified implementation
            return new Dictionary<string, object>
            {
                ["feature_count"] = faceAnalyses.Count,
                ["dominant_emotion"] = "neutral", // Would analyze from face analysis
                ["extracted_at"] = DateTime.UtcNow
            };
        }

        private Dictionary<string, object> ExtractVoiceCharacteristics(Dictionary<string, object> voiceAnalysis)
        {
            return new Dictionary<string, object>
            {
                ["pitch"] = voiceAnalysis.GetValueOrDefault("pitch", 0.0),
                ["speech_rate"] = voiceAnalysis.GetValueOrDefault("speech_rate", 0.0),
                ["timbre"] = voiceAnalysis.GetValueOrDefault("timbre", ""),
                ["extracted_at"] = DateTime.UtcNow
            };
        }

        private async Task<List<Dictionary<string, object>>> GenerateTestSamplesAsync(
            GenerationTask task,
            Dictionary<string, object> trainedModel,
            CancellationToken cancellationToken)
        {
            // Generate test audio using trained voice model
            var testTexts = new[]
            {
                "Hello, this is a test of the trained voice model.",
                "How are you doing today?",
                "The