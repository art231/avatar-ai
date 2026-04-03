using Microsoft.EntityFrameworkCore;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Infrastructure.Persistence;

namespace AvatarAI.Infrastructure.Persistence.Repositories;

public class TaskLogRepository : BaseRepository<TaskLog>, ITaskLogRepository
{
    public TaskLogRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<IEnumerable<TaskLog>> GetByTaskIdAsync(Guid taskId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(l => l.TaskId == taskId)
            .Include(l => l.Task)
            .ThenInclude(t => t.Avatar)
            .OrderByDescending(l => l.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<TaskLog>> GetByStageAsync(Domain.Enums.TaskStage stage, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(l => l.Stage == stage)
            .Include(l => l.Task)
            .ThenInclude(t => t.Avatar)
            .OrderByDescending(l => l.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<TaskLog>> GetRecentLogsAsync(int count = 100, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(l => l.Task)
            .ThenInclude(t => t.Avatar)
            .OrderByDescending(l => l.CreatedAt)
            .Take(count)
            .ToListAsync(cancellationToken);
    }

    public async Task ClearOldLogsAsync(DateTime cutoffDate, CancellationToken cancellationToken = default)
    {
        var oldLogs = await _dbSet
            .Where(l => l.CreatedAt < cutoffDate)
            .ToListAsync(cancellationToken);

        if (oldLogs.Any())
        {
            _dbSet.RemoveRange(oldLogs);
            await _context.SaveChangesAsync(cancellationToken);
        }
    }

    public override async Task<TaskLog?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(l => l.Task)
            .ThenInclude(t => t.Avatar)
            .FirstOrDefaultAsync(l => l.Id == id, cancellationToken);
    }

    public override async Task<IEnumerable<TaskLog>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(l => l.Task)
            .ThenInclude(t => t.Avatar)
            .OrderByDescending(l => l.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<int> GetLogCountByTaskIdAsync(Guid taskId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .CountAsync(l => l.TaskId == taskId, cancellationToken);
    }

    public async Task<IEnumerable<TaskLog>> GetLogsByDateRangeAsync(DateTime startDate, DateTime endDate, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(l => l.CreatedAt >= startDate && l.CreatedAt <= endDate)
            .Include(l => l.Task)
            .ThenInclude(t => t.Avatar)
            .OrderByDescending(l => l.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task AddLogAsync(Guid taskId, Domain.Enums.TaskStage stage, string message, CancellationToken cancellationToken = default)
    {
        var log = new TaskLog(taskId, stage, message);
        await _dbSet.AddAsync(log, cancellationToken);
        await _context.SaveChangesAsync(cancellationToken);
    }

    public async Task AddBatchLogsAsync(IEnumerable<TaskLog> logs, CancellationToken cancellationToken = default)
    {
        await _dbSet.AddRangeAsync(logs, cancellationToken);
        await _context.SaveChangesAsync(cancellationToken);
    }
}