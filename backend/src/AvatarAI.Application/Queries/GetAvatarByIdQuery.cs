using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Queries;

public class GetAvatarByIdQuery : IRequest<AvatarDto?>
{
    public Guid Id { get; }

    public GetAvatarByIdQuery(Guid id)
    {
        Id = id;
    }
}