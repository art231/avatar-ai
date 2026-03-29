namespace AvatarAI.Domain.Entities;

public class VoiceProfile : BaseEntity
{
    public Guid AvatarId { get; private set; }
    public string AudioSamplePath { get; private set; }
    public string? XttsModelPath { get; private set; }
    
    // Navigation properties
    public virtual Avatar Avatar { get; private set; } = null!;

    private VoiceProfile() 
    {
        // Инициализация для EF Core
        AudioSamplePath = string.Empty;
    } // For EF Core

    public VoiceProfile(Guid avatarId, string audioSamplePath)
    {
        AvatarId = avatarId;
        AudioSamplePath = audioSamplePath ?? throw new ArgumentNullException(nameof(audioSamplePath));
    }

    public void UpdateAudioSamplePath(string audioSamplePath)
    {
        if (string.IsNullOrWhiteSpace(audioSamplePath))
            throw new ArgumentException("Audio sample path cannot be empty", nameof(audioSamplePath));
        
        AudioSamplePath = audioSamplePath;
        UpdateTimestamps();
    }

    public void SetXttsModelPath(string xttsModelPath)
    {
        XttsModelPath = xttsModelPath ?? throw new ArgumentNullException(nameof(xttsModelPath));
        UpdateTimestamps();
    }

    public void ClearXttsModelPath()
    {
        XttsModelPath = null;
        UpdateTimestamps();
    }

    public bool IsReadyForSynthesis()
    {
        return !string.IsNullOrWhiteSpace(XttsModelPath);
    }
}