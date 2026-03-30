using System.Text.Json.Serialization;

namespace AvatarAI.Domain.Entities;

public class User : BaseEntity
{
    public string Email { get; private set; }
    public string PasswordHash { get; private set; }
    public string Role { get; private set; } = "User";
    public string? RefreshToken { get; private set; }
    public DateTime? RefreshTokenExpiryTime { get; private set; }
    
    // Navigation properties
    [JsonIgnore]
    public virtual ICollection<Avatar> Avatars { get; private set; } = new List<Avatar>();

    private User() 
    {
        // Инициализация для EF Core
        Email = string.Empty;
        PasswordHash = string.Empty;
        Avatars = new List<Avatar>();
    } // For EF Core

    public User(string email, string passwordHash, string role = "User")
    {
        Email = email ?? throw new ArgumentNullException(nameof(email));
        PasswordHash = passwordHash ?? throw new ArgumentNullException(nameof(passwordHash));
        Role = role ?? throw new ArgumentNullException(nameof(role));
    }

    public void UpdateEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
            throw new ArgumentException("Email cannot be empty", nameof(email));
        
        Email = email;
        UpdateTimestamps();
    }

    public void UpdatePasswordHash(string passwordHash)
    {
        if (string.IsNullOrWhiteSpace(passwordHash))
            throw new ArgumentException("Password hash cannot be empty", nameof(passwordHash));
        
        PasswordHash = passwordHash;
        UpdateTimestamps();
    }

    public void UpdateRole(string role)
    {
        if (string.IsNullOrWhiteSpace(role))
            throw new ArgumentException("Role cannot be empty", nameof(role));
        
        Role = role;
        UpdateTimestamps();
    }

    public void SetRefreshToken(string refreshToken, DateTime expiryTime)
    {
        RefreshToken = refreshToken;
        RefreshTokenExpiryTime = expiryTime;
        UpdateTimestamps();
    }

    public void RevokeRefreshToken()
    {
        RefreshToken = null;
        RefreshTokenExpiryTime = null;
        UpdateTimestamps();
    }

    public bool IsRefreshTokenValid(string refreshToken)
    {
        return !string.IsNullOrEmpty(RefreshToken) 
            && RefreshToken == refreshToken 
            && RefreshTokenExpiryTime.HasValue 
            && RefreshTokenExpiryTime.Value > DateTime.UtcNow;
    }
}
