using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Commands;

public class CreateAvatarCommand : IRequest<AvatarDto>
{
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
    
    public CreateAvatarCommand(Guid userId, string name)
    {
        UserId = userId;
        Name = name;
    }
}