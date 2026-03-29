using System.Text.Json;
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

    public AIServiceClient(HttpClient httpClient, ILogger<AIServiceClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        
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
            // In real implementation, we would upload the file and get processed file path
            // For MVP, we'll simulate the response
            _logger.LogInformation("Preprocessing audio file: {FilePath}", audioFilePath);
            
            // Simulate processing delay
            await Task.Delay(1000, token);
            
            return $"/data/output/cleaned_{Guid.NewGuid()}.wav";
        }, new Context("PreprocessAudio"), cancellationToken);
    }

    public async Task<string> CloneAndSynthesizeVoiceAsync(string voiceSamplePath, string text, string language = "ru", CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Cloning voice from {SamplePath} and synthesizing text: {Text}", 
                voiceSamplePath, text);
            
            // Simulate XTTS processing
            await Task.Delay(2000, token);
            
            return $"/data/output/synthesized_{Guid.NewGuid()}.wav";
        }, new Context("CloneAndSynthesizeVoice"), cancellationToken);
    }

    public async Task<string> AnalyzeMediaAsync(string mediaFilePath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Analyzing media file: {FilePath}", mediaFilePath);
            
            // Simulate media analysis
            await Task.Delay(1500, token);
            
            var result = new
            {
                FaceDetected = true,
                QualityScore = 0.85,
                AlignedFramesPath = $"/data/output/aligned_{Guid.NewGuid()}",
                Metadata = new { Width = 512, Height = 512, Frames = 25 }
            };
            
            return JsonSerializer.Serialize(result, _jsonOptions);
        }, new Context("AnalyzeMedia"), cancellationToken);
    }

    public async Task<string> ApplyLipsyncAsync(string videoPath, string audioPath, CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async (context, token) =>
        {
            _logger.LogInformation("Applying lipsync to video {VideoPath} with audio {AudioPath}", 
                videoPath, audioPath);
            
            // Simulate MuseTalk processing
            await Task.Delay(3000, token);
            
            return $"/data/output/lipsynced_{Guid.NewGuid()}.mp4";
        }, new Context("ApplyLipsync"), cancellationToken);
    }
}