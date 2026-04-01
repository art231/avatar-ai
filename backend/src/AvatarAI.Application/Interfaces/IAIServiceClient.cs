namespace AvatarAI.Application.Interfaces;

public interface IAIServiceClient
{
    Task<string> PreprocessAudioAsync(string audioFilePath, CancellationToken cancellationToken = default);
    Task<string> CloneAndSynthesizeVoiceAsync(string voiceSamplePath, string text, string language = "ru", CancellationToken cancellationToken = default);
    Task<string> AnalyzeMediaAsync(string mediaFilePath, CancellationToken cancellationToken = default);
    Task<string> ApplyLipsyncAsync(string videoPath, string audioPath, CancellationToken cancellationToken = default);
    
    // New methods for TrainingPipelineService
    Task<Dictionary<string, object>> AnalyzeImageAsync(string imagePath, CancellationToken cancellationToken = default);
    Task<Dictionary<string, object>> AnalyzeFaceAsync(string imagePath, CancellationToken cancellationToken = default);
    Task<Dictionary<string, object>> AnalyzeVoiceAsync(string audioPath, CancellationToken cancellationToken = default);
    Task<Dictionary<string, object>> TrainModelAsync(Dictionary<string, object> trainingConfig, CancellationToken cancellationToken = default);
    Task<Dictionary<string, object>> GenerateAudioAsync(string text, string modelPath, CancellationToken cancellationToken = default);
    
    // Training Pipeline methods
    Task<Dictionary<string, object>> StartTrainingAsync(
        string userId,
        string avatarId,
        List<string> imagePaths,
        string voiceSamplePath,
        Dictionary<string, object>? trainingConfig = null,
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> GetTrainingStatusAsync(
        string taskId,
        CancellationToken cancellationToken = default);
    
    // Motion Generator methods
    Task<Dictionary<string, object>> GenerateMotionAsync(
        string userId,
        string avatarId,
        string actionPrompt,
        int durationSec = 10,
        string motionPreset = "idle_talking",
        Dictionary<string, object>? motionConfig = null,
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> ExtractPoseAsync(
        string userId,
        string avatarId,
        string videoPath,
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> GetMotionTaskStatusAsync(
        string taskId,
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> GetMotionPresetsAsync(
        CancellationToken cancellationToken = default);
    
    // Video Renderer methods
    Task<Dictionary<string, object>> RenderVideoAsync(
        string userId,
        string avatarId,
        string loraPath,
        string prompt,
        string? negativePrompt = null,
        string? poseDataPath = null,
        string? referenceImagePath = null,
        int durationSec = 10,
        string qualityPreset = "medium",
        Dictionary<string, object>? renderConfig = null,
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> UpscaleVideoAsync(
        string userId,
        string avatarId,
        string inputVideoPath,
        int upscaleFactor = 2,
        string qualityPreset = "high",
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> GetRenderTaskStatusAsync(
        string taskId,
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> GetQualityPresetsAsync(
        CancellationToken cancellationToken = default);
    
    Task<Dictionary<string, object>> GetAvailableModelsAsync(
        CancellationToken cancellationToken = default);
}
