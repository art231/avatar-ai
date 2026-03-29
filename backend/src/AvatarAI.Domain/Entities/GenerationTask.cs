using AvatarAI.Domain.Enums;

namespace AvatarAI.Domain.Entities;

public class GenerationTask : BaseEntity
{
    public Guid AvatarId { get; private set; }
    public string SpeechText { get; private set; }
    public string? ActionPrompt { get; private set; }
    public Enums.TaskStatus Status { get; private set; }
    public string? OutputPath { get; private set; }
    public DateTime? CompletedAt { get; private set; }
    
    // Navigation properties
    public virtual Avatar Avatar { get; private set; } = null!;
    public virtual ICollection<TaskLog> TaskLogs { get; private set; } = new List<TaskLog>();

    private GenerationTask() 
    {
        // Инициализация для EF Core
        SpeechText = string.Empty;
        TaskLogs = new List<TaskLog>();
    } // For EF Core

    public GenerationTask(Guid avatarId, string speechText, string? actionPrompt = null)
    {
        AvatarId = avatarId;
        SpeechText = speechText ?? throw new ArgumentNullException(nameof(speechText));
        ActionPrompt = actionPrompt;
        Status = Enums.TaskStatus.Pending;
    }

    public void UpdateSpeechText(string speechText)
    {
        if (string.IsNullOrWhiteSpace(speechText))
            throw new ArgumentException("Speech text cannot be empty", nameof(speechText));
        
        SpeechText = speechText;
        UpdateTimestamps();
    }

    public void UpdateActionPrompt(string? actionPrompt)
    {
        ActionPrompt = actionPrompt;
        UpdateTimestamps();
    }

    public void UpdateStatus(Enums.TaskStatus status)
    {
        Status = status;
        UpdateTimestamps();

        if (status == Enums.TaskStatus.Completed || status == Enums.TaskStatus.Failed)
        {
            CompletedAt = DateTime.UtcNow;
        }
    }

    public void SetOutputPath(string outputPath)
    {
        OutputPath = outputPath ?? throw new ArgumentNullException(nameof(outputPath));
        UpdateTimestamps();
    }

    public void ClearOutputPath()
    {
        OutputPath = null;
        UpdateTimestamps();
    }

    public void AddLog(TaskStage stage, string message)
    {
        var log = new TaskLog(Id, stage, message);
        TaskLogs.Add(log);
    }

    public bool CanBeProcessed()
    {
        return Status == Enums.TaskStatus.Pending;
    }
}
