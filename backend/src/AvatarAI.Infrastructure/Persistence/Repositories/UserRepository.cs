using Microsoft.EntityFrameworkCore;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Infrastructure.Persistence;

namespace AvatarAI.Infrastructure.Persistence.Repositories;

public class UserRepository : BaseRepository<User>, IUserRepository
{
    public UserRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<User?> GetByEmailAsync(string email, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .FirstOrDefaultAsync(u => u.Email == email, cancellationToken);
    }

    public async Task<User?> GetByRefreshTokenAsync(string refreshToken, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .FirstOrDefaultAsync(u => u.RefreshToken == refreshToken, cancellationToken);
    }

    public async Task<bool> EmailExistsAsync(string email, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .AnyAsync(u => u.Email == email, cancellationToken);
    }

    public async Task<int> GetAvatarCountAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _context.Set<Avatar>()
            .CountAsync(a => a.UserId == userId, cancellationToken);
    }

    public override async Task<User?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(u => u.Avatars)
            .ThenInclude(a => a.VoiceProfile)
            .Include(u => u.Avatars)
            .ThenInclude(a => a.GenerationTasks)
            .FirstOrDefaultAsync(u => u.Id == id, cancellationToken);
    }

    public override async Task<IEnumerable<User>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(u => u.Avatars)
            .ToListAsync(cancellationToken);
    }
}
