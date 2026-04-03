using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Commands;

public class CreateGenerationTaskCommand : IRequest<GenerationTaskDto>
{
    public Guid AvatarId { get; set; }
    public string SpeechText { get; set; } = string.Empty;
    public string? ActionPrompt { get; set; }
    public string? VoiceStyle { get; set; }
    public string? VideoLength { get; set; }
    public string? Resolution { get; set; }
    public string? Background { get; set; }
    
    public CreateGenerationTaskCommand(
        Guid avatarId, 
        string speechText, 
        string? actionPrompt = null,
        string? voiceStyle = null,
        string? videoLength = null,
        string? resolution = null,
        string? background = null)
    {
        AvatarId = avatarId;
        SpeechText = speechText;
        ActionPrompt = actionPrompt;
        VoiceStyle = voiceStyle;
        VideoLength = videoLength;
        Resolution = resolution;
        Background = background;
    }
}
