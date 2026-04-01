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
}
