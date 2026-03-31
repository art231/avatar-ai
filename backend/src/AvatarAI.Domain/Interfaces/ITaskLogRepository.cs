using AvatarAI.Domain.Entities;

namespace AvatarAI.Domain.Interfaces;

public interface ITaskLogRepository : IRepository<TaskLog>
{
    Task<IEnumerable<TaskLog>> GetByTaskIdAsync(Guid taskId, CancellationToken cancellationToken = default);
    Task<IEnumerable<TaskLog>> GetByStageAsync(Domain.Enums.TaskStage stage, CancellationToken cancellationToken = default);
    Task<IEnumerable<TaskLog>> GetRecentLogsAsync(int count = 100, CancellationToken cancellationToken = default);
    Task ClearOldLogsAsync(DateTime cutoffDate, CancellationToken cancellationToken = default);
}