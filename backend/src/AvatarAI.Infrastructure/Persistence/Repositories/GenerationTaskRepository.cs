using Microsoft.EntityFrameworkCore;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Infrastructure.Persistence;

namespace AvatarAI.Infrastructure.Persistence.Repositories;

public class GenerationTaskRepository : BaseRepository<GenerationTask>, IGenerationTaskRepository
{
    public GenerationTaskRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<IEnumerable<GenerationTask>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(t => t.UserId == userId)
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<GenerationTask>> GetByAvatarIdAsync(Guid avatarId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(t => t.AvatarId == avatarId)
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<GenerationTask>> GetPendingTasksAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(t => t.Status == Domain.Enums.TaskStatus.Pending)
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderBy(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<GenerationTask?> GetWithLogsAsync(Guid taskId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .FirstOrDefaultAsync(t => t.Id == taskId, cancellationToken);
    }

    public override async Task<GenerationTask?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .FirstOrDefaultAsync(t => t.Id == id, cancellationToken);
    }

    public override async Task<IEnumerable<GenerationTask>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<GenerationTask>> GetByStatusAsync(Domain.Enums.TaskStatus status, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(t => t.Status == status)
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<GenerationTask>> GetByStageAsync(Domain.Enums.TaskStage stage, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(t => t.Stage == stage)
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<GenerationTask>> GetRecentTasksAsync(int count = 100, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(t => t.Avatar)
            .ThenInclude(a => a.VoiceProfile)
            .Include(t => t.TaskLogs)
            .OrderByDescending(t => t.CreatedAt)
            .Take(count)
            .ToListAsync(cancellationToken);
    }

    public async Task<int> GetTaskCountByStatusAsync(Domain.Enums.TaskStatus status, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .CountAsync(t => t.Status == status, cancellationToken);
    }

    public async Task<bool> HasActiveTasksForAvatarAsync(Guid avatarId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .AnyAsync(t => t.AvatarId == avatarId && 
                          (t.Status == Domain.Enums.TaskStatus.Pending || 
                           t.Status == Domain.Enums.TaskStatus.Processing), 
                     cancellationToken);
    }
}