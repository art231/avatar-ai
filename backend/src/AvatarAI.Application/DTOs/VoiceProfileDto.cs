namespace AvatarAI.Application.DTOs;

public class VoiceProfileDto
{
    public Guid Id { get; set; }
    public Guid AvatarId { get; set; }
    public string AudioSamplePath { get; set; } = string.Empty;
    public string? XttsModelPath { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}