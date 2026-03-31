using AvatarAI.Domain.Entities;

namespace AvatarAI.Application.Interfaces;

public interface ITrainingPipelineService
{
    Task<GenerationTask> StartTrainingPipelineAsync(
        Guid userId,
        Guid avatarId,
        List<string> imagePaths,
        string voiceSamplePath,
        string trainingConfig,
        CancellationToken cancellationToken = default);
        
    Task ExecuteTrainingPipelineAsync(Guid taskId, CancellationToken cancellationToken = default);
}