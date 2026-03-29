namespace AvatarAI.Domain.Entities;

public class User : BaseEntity
{
    public string Email { get; private set; }
    public string PasswordHash { get; private set; }
    
    // Navigation properties
    public virtual ICollection<Avatar> Avatars { get; private set; } = new List<Avatar>();

    private User() 
    {
        // Инициализация для EF Core
        Email = string.Empty;
        PasswordHash = string.Empty;
        Avatars = new List<Avatar>();
    } // For EF Core

    public User(string email, string passwordHash)
    {
        Email = email ?? throw new ArgumentNullException(nameof(email));
        PasswordHash = passwordHash ?? throw new ArgumentNullException(nameof(passwordHash));
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
}