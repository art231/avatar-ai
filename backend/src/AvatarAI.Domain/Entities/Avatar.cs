using AvatarAI.Domain.Enums;

namespace AvatarAI.Domain.Entities;

public class Avatar : BaseEntity
{
    public Guid UserId { get; private set; }
    public string Name { get; private set; }
    public AvatarStatus Status { get; private set; }
    public string? LoraPath { get; private set; }
    public string? ModelPath { get; private set; }
    public Dictionary<string, object>? VoiceProfile { get; private set; }
    
    // Navigation properties
    public virtual User User { get; private set; } = null!;
    public virtual ICollection<GenerationTask> GenerationTasks { get; private set; } = new List<GenerationTask>();

    private Avatar() 
    {
        // Инициализация для EF Core
        Name = string.Empty;
        GenerationTasks = new List<GenerationTask>();
    } // For EF Core

    public Avatar(Guid userId, string name)
    {
        UserId = userId;
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Status = AvatarStatus.Pending;
    }

    public void UpdateName(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name cannot be empty", nameof(name));
        
        Name = name;
        UpdateTimestamps();
    }

    public void UpdateStatus(AvatarStatus status)
    {
        Status = status;
        UpdateTimestamps();
    }

    public void SetLoraPath(string loraPath)
    {
        LoraPath = loraPath ?? throw new ArgumentNullException(nameof(loraPath));
        UpdateTimestamps();
    }

    public void ClearLoraPath()
    {
        LoraPath = null;
        UpdateTimestamps();
    }

    public void SetModelPath(string modelPath)
    {
        ModelPath = modelPath ?? throw new ArgumentNullException(nameof(modelPath));
        UpdateTimestamps();
    }

    public void ClearModelPath()
    {
        ModelPath = null;
        UpdateTimestamps();
    }

    public void SetVoiceProfile(Dictionary<string, object> voiceProfile)
    {
        VoiceProfile = voiceProfile ?? throw new ArgumentNullException(nameof(voiceProfile));
        UpdateTimestamps();
    }

    public void ClearVoiceProfile()
    {
        VoiceProfile = null;
        UpdateTimestamps();
    }

    public bool IsReadyForGeneration()
    {
        return Status == AvatarStatus.Ready && VoiceProfile != null && ModelPath != null;
    }
}
