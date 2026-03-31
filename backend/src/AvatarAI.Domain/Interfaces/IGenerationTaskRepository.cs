using AvatarAI.Domain.Entities;

namespace AvatarAI.Domain.Interfaces;

public interface IGenerationTaskRepository : IRepository<GenerationTask>
{
    Task<IEnumerable<GenerationTask>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);
    Task<IEnumerable<GenerationTask>> GetByAvatarIdAsync(Guid avatarId, CancellationToken cancellationToken = default);
    Task<IEnumerable<GenerationTask>> GetPendingTasksAsync(CancellationToken cancellationToken = default);
    Task<GenerationTask?> GetWithLogsAsync(Guid taskId, CancellationToken cancellationToken = default);
}