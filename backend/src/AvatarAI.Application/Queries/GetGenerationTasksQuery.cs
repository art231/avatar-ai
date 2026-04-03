using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Queries;

public class GetGenerationTasksQuery : IRequest<IEnumerable<GenerationTaskDto>>
{
    public Guid? AvatarId { get; }
    public Guid? UserId { get; }

    public GetGenerationTasksQuery(Guid? avatarId = null, Guid? userId = null)
    {
        AvatarId = avatarId;
        UserId = userId;
    }
}