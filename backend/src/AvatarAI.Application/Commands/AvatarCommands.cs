using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Commands;

public class UpdateAvatarCommand : IRequest<AvatarDto>
{
    public Guid AvatarId { get; set; }
    public string? Name { get; set; }
    public string? Description { get; set; }
    
    public UpdateAvatarCommand(Guid avatarId, string? name, string? description)
    {
        AvatarId = avatarId;
        Name = name;
        Description = description;
    }
}

public class DeleteAvatarCommand : IRequest<Unit>
{
    public Guid AvatarId { get; set; }
    
    public DeleteAvatarCommand(Guid avatarId)
    {
        AvatarId = avatarId;
    }
}

public class StartAvatarTrainingCommand : IRequest<Unit>
{
    public Guid AvatarId { get; set; }
    
    public StartAvatarTrainingCommand(Guid avatarId)
    {
        AvatarId = avatarId;
    }
}

public class GenerateVideoCommand : IRequest<GenerationTaskDto>
{
    public Guid AvatarId { get; set; }
    public string Text { get; set; }
    public string? VoiceStyle { get; set; }
    public string? VideoLength { get; set; }
    public string? Resolution { get; set; }
    public string? Background { get; set; }
    
    public GenerateVideoCommand(
        Guid avatarId, 
        string text,
        string? voiceStyle = null,
        string? videoLength = null,
        string? resolution = null,
        string? background = null)
    {
        AvatarId = avatarId;
        Text = text;
        VoiceStyle = voiceStyle;
        VideoLength = videoLength;
        Resolution = resolution;
        Background = background;
    }
}