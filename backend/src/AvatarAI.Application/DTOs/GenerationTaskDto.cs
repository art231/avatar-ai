using AvatarAI.Domain.Enums;

namespace AvatarAI.Application.DTOs;

public class GenerationTaskDto
{
    public Guid Id { get; set; }
    public Guid AvatarId { get; set; }
    public Guid UserId { get; set; }
    public string SpeechText { get; set; } = string.Empty;
    public string? ActionPrompt { get; set; }
    public Domain.Enums.TaskStatus Status { get; set; }
    public TaskStage Stage { get; set; }
    public decimal Progress { get; set; }
    public string? OutputPath { get; set; }
    public string? ErrorMessage { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public List<TaskLogDto> TaskLogs { get; set; } = new();
    
    // Настройки из фронтенда
    public string? VoiceStyle { get; set; }
    public string? VideoLength { get; set; }
    public string? Resolution { get; set; }
    public string? Background { get; set; }
    
    // Дополнительные поля для фронтенда
    public string? AvatarName { get; set; }
    public string? VideoUrl { get; set; }
    public string? AudioUrl { get; set; }
}
