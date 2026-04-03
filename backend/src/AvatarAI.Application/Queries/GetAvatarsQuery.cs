using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Queries;

public class GetAvatarsQuery : IRequest<IEnumerable<AvatarDto>>
{
    public Guid? UserId { get; }

    public GetAvatarsQuery(Guid? userId = null)
    {
        UserId = userId;
    }
}