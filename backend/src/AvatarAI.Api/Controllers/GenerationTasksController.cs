using Microsoft.AspNetCore.Mvc;
using MediatR;
using AvatarAI.Application.Commands;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class GenerationTasksController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly ILogger<GenerationTasksController> _logger;

    public GenerationTasksController(IMediator mediator, ILogger<GenerationTasksController> logger)
    {
        _mediator = mediator;
        _logger = logger;
    }

    [HttpPost]
    [ProducesResponseType(typeof(GenerationTaskDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateGenerationTask([FromBody] CreateGenerationTaskRequest request)
    {
        try
        {
            _logger.LogInformation("Creating generation task for avatar {AvatarId} with text length: {TextLength}", 
                request.AvatarId, request.SpeechText?.Length ?? 0);
            
            var command = new CreateGenerationTaskCommand(
                request.AvatarId, 
                request.SpeechText ?? string.Empty, 
                request.ActionPrompt);
            
            var result = await _mediator.Send(command);
            
            return CreatedAtAction(nameof(GetGenerationTask), new { id = result.Id }, result);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for creating generation task");
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating generation task");
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(GenerationTaskDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public Task<IActionResult> GetGenerationTask(Guid id)
    {
        // In real implementation, we would query task from database
        // For MVP, we'll simulate a response
        var task = new GenerationTaskDto
        {
            Id = id,
            AvatarId = Guid.NewGuid(),
            SpeechText = "Привет, это тестовый текст для генерации видео.",
            Status = Domain.Enums.TaskStatus.Completed,
            OutputPath = $"/data/output/final_{id}.mp4",
            CreatedAt = DateTime.UtcNow.AddMinutes(-10),
            UpdatedAt = DateTime.UtcNow.AddMinutes(-1),
            CompletedAt = DateTime.UtcNow.AddMinutes(-1),
            TaskLogs = new List<TaskLogDto>
            {
                new() { Stage = Domain.Enums.TaskStage.AudioPreprocessing, Message = "Audio preprocessing started", CreatedAt = DateTime.UtcNow.AddMinutes(-9) },
                new() { Stage = Domain.Enums.TaskStage.VoiceCloning, Message = "Voice cloning completed", CreatedAt = DateTime.UtcNow.AddMinutes(-7) },
                new() { Stage = Domain.Enums.TaskStage.MediaAnalysis, Message = "Media analysis successful", CreatedAt = DateTime.UtcNow.AddMinutes(-5) },
                new() { Stage = Domain.Enums.TaskStage.Lipsync, Message = "Lipsync applied", CreatedAt = DateTime.UtcNow.AddMinutes(-3) },
                new() { Stage = Domain.Enums.TaskStage.Completed, Message = "Generation task completed successfully", CreatedAt = DateTime.UtcNow.AddMinutes(-1) }
            }
        };
        
        return Task.FromResult<IActionResult>(Ok(task));
    }

    [HttpGet]
    [ProducesResponseType(typeof(List<GenerationTaskDto>), StatusCodes.Status200OK)]
    public Task<IActionResult> GetGenerationTasks([FromQuery] Guid? avatarId = null)
    {
        // In real implementation, we would query tasks from database
        // For MVP, we'll return simulated data
        var tasks = new List<GenerationTaskDto>
        {
            new()
            {
                Id = Guid.NewGuid(),
                AvatarId = avatarId ?? Guid.NewGuid(),
                SpeechText = "Добро пожаловать в AvatarAI!",
                Status = Domain.Enums.TaskStatus.Completed,
                OutputPath = "/data/output/final_1.mp4",
                CreatedAt = DateTime.UtcNow.AddHours(-2),
                UpdatedAt = DateTime.UtcNow.AddHours(-1),
                CompletedAt = DateTime.UtcNow.AddHours(-1)
            },
            new()
            {
                Id = Guid.NewGuid(),
                AvatarId = avatarId ?? Guid.NewGuid(),
                SpeechText = "Это демонстрация технологии синтеза речи и видео.",
                Status = Domain.Enums.TaskStatus.Processing,
                CreatedAt = DateTime.UtcNow.AddMinutes(-30),
                UpdatedAt = DateTime.UtcNow.AddMinutes(-5)
            },
            new()
            {
                Id = Guid.NewGuid(),
                AvatarId = avatarId ?? Guid.NewGuid(),
                SpeechText = "Следующее поколение цифровых аватаров уже здесь.",
                Status = Domain.Enums.TaskStatus.Pending,
                CreatedAt = DateTime.UtcNow.AddMinutes(-10),
                UpdatedAt = DateTime.UtcNow.AddMinutes(-10)
            }
        };
        
        return Task.FromResult<IActionResult>(Ok(tasks));
    }

    [HttpGet("{id:guid}/progress")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public Task<IActionResult> GetTaskProgress(Guid id)
    {
        // In real implementation, this would be Server-Sent Events (SSE) or WebSocket
        // For MVP, we'll return current progress
        var progress = new
        {
            TaskId = id,
            Status = "processing",
            Progress = 60,
            CurrentStage = "lipsync",
            EstimatedTimeRemaining = "45 seconds",
            Logs = new[]
            {
                new { Timestamp = DateTime.UtcNow.AddMinutes(-4), Message = "Audio preprocessing completed" },
                new { Timestamp = DateTime.UtcNow.AddMinutes(-3), Message = "Voice cloning in progress" },
                new { Timestamp = DateTime.UtcNow.AddMinutes(-2), Message = "Media analysis started" },
                new { Timestamp = DateTime.UtcNow.AddMinutes(-1), Message = "Applying lipsync to video" }
            }
        };
        
        return Task.FromResult<IActionResult>(Ok(progress));
    }
}

public class CreateGenerationTaskRequest
{
    public Guid AvatarId { get; set; }
    public string? SpeechText { get; set; }
    public string? ActionPrompt { get; set; }
}