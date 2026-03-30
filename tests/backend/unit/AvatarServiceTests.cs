using Xunit;
using Moq;
using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using AvatarAI.Application.Services;
using AvatarAI.Application.Interfaces;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Enums;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Tests.Backend.Unit
{
    public class AvatarServiceTests
    {
        private readonly Mock<IAvatarRepository> _avatarRepositoryMock;
        private readonly Mock<IBackgroundJobService> _backgroundJobServiceMock;
        private readonly Mock<IAIServiceClient> _aiServiceClientMock;
        private readonly Mock<ILogger<AvatarService>> _loggerMock;
        private readonly AvatarService _avatarService;

        public AvatarServiceTests()
        {
            _avatarRepositoryMock = new Mock<IAvatarRepository>();
            _backgroundJobServiceMock = new Mock<IBackgroundJobService>();
            _aiServiceClientMock = new Mock<IAIServiceClient>();
            _loggerMock = new Mock<ILogger<AvatarService>>();

            _avatarService = new AvatarService(
                _avatarRepositoryMock.Object,
                _backgroundJobServiceMock.Object,
                _aiServiceClientMock.Object,
                _loggerMock.Object
            );
        }

        [Fact]
        public async Task CreateAvatarAsync_ValidRequest_ReturnsAvatarDto()
        {
            // Arrange
            var request = new CreateAvatarRequest
            {
                Name = "Test Avatar",
                Description = "Test Description",
                UserId = Guid.NewGuid()
            };

            var avatar = new Avatar
            {
                Id = Guid.NewGuid(),
                Name = request.Name,
                Description = request.Description,
                UserId = request.UserId,
                Status = AvatarStatus.Pending,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            _avatarRepositoryMock
                .Setup(x => x.AddAsync(It.IsAny<Avatar>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(avatar);

            // Act
            var result = await _avatarService.CreateAvatarAsync(request, CancellationToken.None);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(avatar.Id, result.Id);
            Assert.Equal(avatar.Name, result.Name);
            Assert.Equal(avatar.Description, result.Description);
            Assert.Equal(AvatarStatus.Pending, result.Status);

            _avatarRepositoryMock.Verify(x => x.AddAsync(It.IsAny<Avatar>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task GetAvatarByIdAsync_ExistingId_ReturnsAvatarDto()
        {
            // Arrange
            var avatarId = Guid.NewGuid();
            var avatar = new Avatar
            {
                Id = avatarId,
                Name = "Test Avatar",
                Status = AvatarStatus.Active,
                CreatedAt = DateTime.UtcNow.AddDays(-1),
                UpdatedAt = DateTime.UtcNow
            };

            _avatarRepositoryMock
                .Setup(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync(avatar);

            // Act
            var result = await _avatarService.GetAvatarByIdAsync(avatarId, CancellationToken.None);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(avatarId, result.Id);
            Assert.Equal(avatar.Name, result.Name);
            Assert.Equal(avatar.Status, result.Status);

            _avatarRepositoryMock.Verify(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task GetAvatarByIdAsync_NonExistingId_ThrowsNotFoundException()
        {
            // Arrange
            var avatarId = Guid.NewGuid();

            _avatarRepositoryMock
                .Setup(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync((Avatar?)null);

            // Act & Assert
            await Assert.ThrowsAsync<NotFoundException>(() =>
                _avatarService.GetAvatarByIdAsync(avatarId, CancellationToken.None));

            _avatarRepositoryMock.Verify(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task UpdateAvatarAsync_ValidRequest_UpdatesAvatar()
        {
            // Arrange
            var avatarId = Guid.NewGuid();
            var request = new UpdateAvatarRequest
            {
                Name = "Updated Name",
                Description = "Updated Description"
            };

            var existingAvatar = new Avatar
            {
                Id = avatarId,
                Name = "Original Name",
                Description = "Original Description",
                Status = AvatarStatus.Active,
                CreatedAt = DateTime.UtcNow.AddDays(-1),
                UpdatedAt = DateTime.UtcNow.AddDays(-1)
            };

            _avatarRepositoryMock
                .Setup(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync(existingAvatar);

            _avatarRepositoryMock
                .Setup(x => x.UpdateAsync(It.IsAny<Avatar>(), It.IsAny<CancellationToken>()))
                .Returns(Task.CompletedTask);

            // Act
            var result = await _avatarService.UpdateAvatarAsync(avatarId, request, CancellationToken.None);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(request.Name, result.Name);
            Assert.Equal(request.Description, result.Description);
            Assert.True(result.UpdatedAt > existingAvatar.UpdatedAt);

            _avatarRepositoryMock.Verify(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
            _avatarRepositoryMock.Verify(x => x.UpdateAsync(It.IsAny<Avatar>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task DeleteAvatarAsync_ExistingId_DeletesAvatar()
        {
            // Arrange
            var avatarId = Guid.NewGuid();
            var avatar = new Avatar
            {
                Id = avatarId,
                Name = "Test Avatar",
                Status = AvatarStatus.Active
            };

            _avatarRepositoryMock
                .Setup(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync(avatar);

            _avatarRepositoryMock
                .Setup(x => x.DeleteAsync(avatar, It.IsAny<CancellationToken>()))
                .Returns(Task.CompletedTask);

            // Act
            await _avatarService.DeleteAvatarAsync(avatarId, CancellationToken.None);

            // Assert
            _avatarRepositoryMock.Verify(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
            _avatarRepositoryMock.Verify(x => x.DeleteAsync(avatar, It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task StartTrainingAsync_ValidAvatar_StartsTrainingJob()
        {
            // Arrange
            var avatarId = Guid.NewGuid();
            var avatar = new Avatar
            {
                Id = avatarId,
                Name = "Test Avatar",
                Status = AvatarStatus.Pending,
                TrainingDataPath = "/data/training/images"
            };

            _avatarRepositoryMock
                .Setup(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync(avatar);

            _avatarRepositoryMock
                .Setup(x => x.UpdateAsync(It.IsAny<Avatar>(), It.IsAny<CancellationToken>()))
                .Returns(Task.CompletedTask);

            _backgroundJobServiceMock
                .Setup(x => x.EnqueueTrainingJobAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync("job-123");

            // Act
            var result = await _avatarService.StartTrainingAsync(avatarId, CancellationToken.None);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("job-123", result.JobId);
            Assert.Equal(AvatarStatus.Training, avatar.Status);

            _avatarRepositoryMock.Verify(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
            _avatarRepositoryMock.Verify(x => x.UpdateAsync(avatar, It.IsAny<CancellationToken>()), Times.Once);
            _backgroundJobServiceMock.Verify(x => x.EnqueueTrainingJobAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task GetTrainingProgressAsync_ValidAvatar_ReturnsProgress()
        {
            // Arrange
            var avatarId = Guid.NewGuid();
            var progress = new TrainingProgress
            {
                AvatarId = avatarId,
                Progress = 0.5m,
                CurrentStage = "lora_training",
                EstimatedTimeRemaining = TimeSpan.FromMinutes(30)
            };

            _aiServiceClientMock
                .Setup(x => x.GetTrainingProgressAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync(progress);

            // Act
            var result = await _avatarService.GetTrainingProgressAsync(avatarId, CancellationToken.None);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(progress.Progress, result.Progress);
            Assert.Equal(progress.CurrentStage, result.CurrentStage);
            Assert.Equal(progress.EstimatedTimeRemaining, result.EstimatedTimeRemaining);

            _aiServiceClientMock.Verify(x => x.GetTrainingProgressAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task GenerateVideoAsync_ValidRequest_ReturnsTaskId()
        {
            // Arrange
            var avatarId = Guid.NewGuid();
            var request = new GenerateVideoRequest
            {
                Text = "Hello, this is a test video.",
                VoiceStyle = "professional",
                Background = "studio"
            };

            var avatar = new Avatar
            {
                Id = avatarId,
                Name = "Test Avatar",
                Status = AvatarStatus.Active,
                ModelPath = "/models/lora_model.safetensors",
                VoiceModelPath = "/models/voice_model.pth"
            };

            _avatarRepositoryMock
                .Setup(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()))
                .ReturnsAsync(avatar);

            _backgroundJobServiceMock
                .Setup(x => x.EnqueueGenerationJobAsync(avatarId, request, It.IsAny<CancellationToken>()))
                .ReturnsAsync("generation-job-123");

            // Act
            var result = await _avatarService.GenerateVideoAsync(avatarId, request, CancellationToken.None);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("generation-job-123", result.TaskId);

            _avatarRepositoryMock.Verify(x => x.GetByIdAsync(avatarId, It.IsAny<CancellationToken>()), Times.Once);
            _backgroundJobServiceMock.Verify(x => x.EnqueueGenerationJobAsync(avatarId, request, It.IsAny<CancellationToken>()), Times.Once);
        }
    }

    // Helper classes for testing
    public class CreateAvatarRequest
    {
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public Guid UserId { get; set; }
    }

    public class UpdateAvatarRequest
    {
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
    }

    public class GenerateVideoRequest
    {
        public string Text { get; set; } = string.Empty;
        public string VoiceStyle { get; set; } = "neutral";
        public string Background { get; set; } = "studio";
    }

    public class TrainingProgress
    {
        public Guid AvatarId { get; set; }
        public decimal Progress { get; set; }
        public string CurrentStage { get; set; } = string.Empty;
        public TimeSpan EstimatedTimeRemaining { get; set; }
    }

    public class NotFoundException : Exception
    {
        public NotFoundException(string message) : base(message) { }
    }
}