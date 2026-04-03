using Microsoft.EntityFrameworkCore;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Infrastructure.Persistence;

namespace AvatarAI.Infrastructure.Persistence.Repositories;

public class AvatarRepository : BaseRepository<Avatar>, IAvatarRepository
{
    public AvatarRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<IEnumerable<Avatar>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(a => a.UserId == userId)
            .Include(a => a.GenerationTasks)
            .ThenInclude(gt => gt.TaskLogs)
            .Include(a => a.VoiceProfile)
            .OrderByDescending(a => a.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<Avatar?> GetByModelPathAsync(string modelPath, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .FirstOrDefaultAsync(a => a.ModelPath == modelPath, cancellationToken);
    }

    public async Task<bool> AvatarNameExistsAsync(string name, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .AnyAsync(a => a.Name == name, cancellationToken);
    }

    public override async Task<Avatar?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(a => a.User)
            .Include(a => a.GenerationTasks)
            .ThenInclude(gt => gt.TaskLogs)
            .Include(a => a.VoiceProfile)
            .FirstOrDefaultAsync(a => a.Id == id, cancellationToken);
    }

    public override async Task<IEnumerable<Avatar>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(a => a.User)
            .Include(a => a.GenerationTasks)
            .ThenInclude(gt => gt.TaskLogs)
            .Include(a => a.VoiceProfile)
            .OrderByDescending(a => a.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<Avatar>> GetReadyForGenerationAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(a => a.Status == Domain.Enums.AvatarStatus.Ready && 
                       a.VoiceProfile != null && 
                       a.ModelPath != null)
            .Include(a => a.User)
            .Include(a => a.VoiceProfile)
            .ToListAsync(cancellationToken);
    }

    public async Task<IEnumerable<Avatar>> GetByStatusAsync(Domain.Enums.AvatarStatus status, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(a => a.Status == status)
            .Include(a => a.User)
            .Include(a => a.VoiceProfile)
            .OrderByDescending(a => a.CreatedAt)
            .ToListAsync(cancellationToken);
    }
}