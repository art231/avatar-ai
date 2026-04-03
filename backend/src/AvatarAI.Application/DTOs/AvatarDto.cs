using AvatarAI.Domain.Enums;

namespace AvatarAI.Application.DTOs;

public class AvatarDto
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public AvatarStatus Status { get; set; }
    public string? LoraPath { get; set; }
    public int TrainedImages { get; set; }
    public bool TrainedVoice { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public VoiceProfileDto? VoiceProfile { get; set; }
    public List<GenerationTaskDto> GenerationTasks { get; set; } = new();
}
