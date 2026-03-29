using Microsoft.EntityFrameworkCore;
using AvatarAI.Domain.Entities;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

namespace AvatarAI.Infrastructure.Persistence;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<Avatar> Avatars { get; set; }
    public DbSet<VoiceProfile> VoiceProfiles { get; set; }
    public DbSet<GenerationTask> GenerationTasks { get; set; }
    public DbSet<TaskLog> TaskLogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // User configuration
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
            entity.Property(e => e.PasswordHash).IsRequired().HasMaxLength(255);
            entity.Property(e => e.CreatedAt).IsRequired();
            entity.Property(e => e.UpdatedAt).IsRequired();
            
            entity.HasIndex(e => e.Email).IsUnique();
            
            entity.HasMany(e => e.Avatars)
                .WithOne(e => e.User)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Avatar configuration
        modelBuilder.Entity<Avatar>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(255);
            entity.Property(e => e.Status).IsRequired().HasConversion<string>();
            entity.Property(e => e.LoraPath).HasMaxLength(500);
            entity.Property(e => e.CreatedAt).IsRequired();
            entity.Property(e => e.UpdatedAt).IsRequired();
            
            entity.HasIndex(e => e.UserId);
            entity.HasIndex(e => e.Status);
            
            entity.HasOne(e => e.User)
                .WithMany(e => e.Avatars)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(e => e.VoiceProfile)
                .WithOne(e => e.Avatar)
                .HasForeignKey<VoiceProfile>(e => e.AvatarId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasMany(e => e.GenerationTasks)
                .WithOne(e => e.Avatar)
                .HasForeignKey(e => e.AvatarId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // VoiceProfile configuration
        modelBuilder.Entity<VoiceProfile>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.AudioSamplePath).IsRequired().HasMaxLength(500);
            entity.Property(e => e.XttsModelPath).HasMaxLength(500);
            entity.Property(e => e.CreatedAt).IsRequired();
            entity.Property(e => e.UpdatedAt).IsRequired();
            
            entity.HasIndex(e => e.AvatarId).IsUnique();
            
            entity.HasOne(e => e.Avatar)
                .WithOne(e => e.VoiceProfile)
                .HasForeignKey<VoiceProfile>(e => e.AvatarId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // GenerationTask configuration
        modelBuilder.Entity<GenerationTask>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.SpeechText).IsRequired();
            entity.Property(e => e.ActionPrompt).HasMaxLength(500);
            entity.Property(e => e.Status).IsRequired().HasConversion<string>();
            entity.Property(e => e.OutputPath).HasMaxLength(500);
            entity.Property(e => e.CreatedAt).IsRequired();
            entity.Property(e => e.UpdatedAt).IsRequired();
            entity.Property(e => e.CompletedAt);
            
            entity.HasIndex(e => e.AvatarId);
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.CreatedAt);
            
            entity.HasOne(e => e.Avatar)
                .WithMany(e => e.GenerationTasks)
                .HasForeignKey(e => e.AvatarId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasMany(e => e.TaskLogs)
                .WithOne(e => e.Task)
                .HasForeignKey(e => e.TaskId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // TaskLog configuration
        modelBuilder.Entity<TaskLog>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Stage).IsRequired().HasConversion<string>();
            entity.Property(e => e.Message).IsRequired();
            entity.Property(e => e.CreatedAt).IsRequired();
            
            entity.HasIndex(e => e.TaskId);
            entity.HasIndex(e => e.Stage);
            
            entity.HasOne(e => e.Task)
                .WithMany(e => e.TaskLogs)
                .HasForeignKey(e => e.TaskId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }

    public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateTimestamps();
        return await base.SaveChangesAsync(cancellationToken);
    }

    public override int SaveChanges()
    {
        UpdateTimestamps();
        return base.SaveChanges();
    }

    private void UpdateTimestamps()
    {
        var entries = ChangeTracker
            .Entries()
            .Where(e => e.Entity is BaseEntity && 
                       (e.State == EntityState.Added || e.State == EntityState.Modified));

        foreach (var entityEntry in entries)
        {
            var entity = (BaseEntity)entityEntry.Entity;
            
            if (entityEntry.State == EntityState.Added)
            {
                entity.CreatedAt = DateTime.UtcNow;
            }
            
            entity.UpdatedAt = DateTime.UtcNow;
        }
    }
}