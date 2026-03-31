using AvatarAI.Domain.Enums;

namespace AvatarAI.Domain.Entities;

public class GenerationTask : BaseEntity
{
    public Guid UserId { get; private set; }
    public Guid AvatarId { get; private set; }
    public string SpeechText { get; private set; }
    public string? ActionPrompt { get; private set; }
    public Enums.TaskStatus Status { get; private set; }
    public Enums.TaskStage Stage { get; private set; }
    public string? OutputPath { get; private set; }
    public DateTime? CompletedAt { get; private set; }
    public decimal Progress { get; private set; }
    public string? ErrorMessage { get; private set; }
    public Dictionary<string, object> Metadata { get; private set; }
    
    // Navigation properties
    public virtual Avatar Avatar { get; private set; } = null!;
    public virtual ICollection<TaskLog> TaskLogs { get; private set; } = new List<TaskLog>();

    private GenerationTask() 
    {
        // Инициализация для EF Core
        SpeechText = string.Empty;
        TaskLogs = new List<TaskLog>();
        Metadata = new Dictionary<string, object>();
        Stage = Enums.TaskStage.AudioPreprocessing;
        Progress = 0m;
    } // For EF Core

    // Конструктор для генерации контента
    public GenerationTask(Guid avatarId, string speechText, string? actionPrompt = null)
    {
        AvatarId = avatarId;
        SpeechText = speechText ?? throw new ArgumentNullException(nameof(speechText));
        ActionPrompt = actionPrompt;
        Status = Enums.TaskStatus.Pending;
        Stage = Enums.TaskStage.AudioPreprocessing;
        Progress = 0m;
        Metadata = new Dictionary<string, object>();
    }

    // Конструктор для тренировочного пайплайна
    public GenerationTask(Guid userId, Guid avatarId, Dictionary<string, object> metadata)
    {
        UserId = userId;
        AvatarId = avatarId;
        SpeechText = string.Empty;
        ActionPrompt = null;
        Status = Enums.TaskStatus.Pending;
        Stage = Enums.TaskStage.DataPreparation;
        Progress = 0m;
        Metadata = metadata ?? new Dictionary<string, object>();
    }

    public void UpdateUserId(Guid userId)
    {
        UserId = userId;
        UpdateTimestamps();
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

    public void UpdateStage(Enums.TaskStage stage)
    {
        Stage = stage;
        UpdateTimestamps();
    }

    public void UpdateProgress(decimal progress)
    {
        if (progress < 0m || progress > 1m)
            throw new ArgumentException("Progress must be between 0 and 1", nameof(progress));
        
        Progress = progress;
        UpdateTimestamps();
    }

    public void UpdateErrorMessage(string? errorMessage)
    {
        ErrorMessage = errorMessage;
        UpdateTimestamps();
    }

    public void UpdateMetadata(string key, object value)
    {
        Metadata[key] = value;
        UpdateTimestamps();
    }

    public void UpdateMetadata(Dictionary<string, object> metadata)
    {
        Metadata = metadata ?? new Dictionary<string, object>();
        UpdateTimestamps();
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
