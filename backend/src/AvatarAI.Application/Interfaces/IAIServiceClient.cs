namespace AvatarAI.Application.Interfaces;

public interface IAIServiceClient
{
    Task<string> PreprocessAudioAsync(string audioFilePath, CancellationToken cancellationToken = default);
    Task<string> CloneAndSynthesizeVoiceAsync(string voiceSamplePath, string text, string language = "ru", CancellationToken cancellationToken = default);
    Task<string> AnalyzeMediaAsync(string mediaFilePath, CancellationToken cancellationToken = default);
    Task<string> ApplyLipsyncAsync(string videoPath, string audioPath, CancellationToken cancellationToken = default);
}