using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Commands;

public class CreateGenerationTaskCommand : IRequest<GenerationTaskDto>
{
    public Guid AvatarId { get; set; }
    public string SpeechText { get; set; } = string.Empty;
    public string? ActionPrompt { get; set; }
    
    public CreateGenerationTaskCommand(Guid avatarId, string speechText, string? actionPrompt = null)
    {
        AvatarId = avatarId;
        SpeechText = speechText;
        ActionPrompt = actionPrompt;
    }
}