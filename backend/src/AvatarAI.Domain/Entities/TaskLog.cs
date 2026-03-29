using AvatarAI.Domain.Enums;

namespace AvatarAI.Domain.Entities;

public class TaskLog : BaseEntity
{
    public Guid TaskId { get; private set; }
    public TaskStage Stage { get; private set; }
    public string Message { get; private set; }
    
    // Navigation properties
    public virtual GenerationTask Task { get; private set; } = null!;

    private TaskLog() 
    {
        // Инициализация для EF Core
        Message = string.Empty;
    } // For EF Core

    public TaskLog(Guid taskId, TaskStage stage, string message) : this()
    {
        TaskId = taskId;
        Stage = stage;
        Message = message ?? throw new ArgumentNullException(nameof(message));
    }

    public void UpdateMessage(string message)
    {
        if (string.IsNullOrWhiteSpace(message))
            throw new ArgumentException("Message cannot be empty", nameof(message));
        
        Message = message;
        UpdateTimestamps();
    }
}