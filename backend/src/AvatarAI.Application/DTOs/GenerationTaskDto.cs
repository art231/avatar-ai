using AvatarAI.Domain.Enums;

namespace AvatarAI.Application.DTOs;

public class GenerationTaskDto
{
    public Guid Id { get; set; }
    public Guid AvatarId { get; set; }
    public string SpeechText { get; set; } = string.Empty;
    public string? ActionPrompt { get; set; }
    public Domain.Enums.TaskStatus Status { get; set; }
    public string? OutputPath { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public List<TaskLogDto> TaskLogs { get; set; } = new();
}
