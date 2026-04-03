using MediatR;
using AvatarAI.Application.DTOs;
using Microsoft.AspNetCore.Http;

namespace AvatarAI.Application.Commands;

public class CreateAvatarCommand : IRequest<AvatarDto>
{
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public List<IFormFile> Images { get; set; }
    public IFormFile? VoiceSample { get; set; }
    
    public CreateAvatarCommand(
        Guid userId, 
        string name, 
        string? description,
        List<IFormFile> images,
        IFormFile? voiceSample)
    {
        UserId = userId;
        Name = name;
        Description = description;
        Images = images;
        VoiceSample = voiceSample;
    }
}
