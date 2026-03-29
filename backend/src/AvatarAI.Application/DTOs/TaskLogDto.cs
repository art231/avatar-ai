using AvatarAI.Domain.Enums;

namespace AvatarAI.Application.DTOs;

public class TaskLogDto
{
    public Guid Id { get; set; }
    public Guid TaskId { get; set; }
    public TaskStage Stage { get; set; }
    public string Message { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}