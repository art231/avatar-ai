using AvatarAI.Domain.Entities;

namespace AvatarAI.Domain.Interfaces;

public interface IAvatarRepository : IRepository<Avatar>
{
    Task<IEnumerable<Avatar>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);
    Task<Avatar?> GetByModelPathAsync(string modelPath, CancellationToken cancellationToken = default);
    Task<bool> AvatarNameExistsAsync(string name, CancellationToken cancellationToken = default);
}