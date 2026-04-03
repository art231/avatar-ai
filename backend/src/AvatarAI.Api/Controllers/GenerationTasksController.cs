using Microsoft.AspNetCore.Mvc;
using MediatR;
using AvatarAI.Application.Commands;
using AvatarAI.Application.Queries;
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
            _logger.LogInformation("Creating generation task for avatar {AvatarId} with text length: {TextLength} and settings: {Settings}", 
                request.AvatarId, request.SpeechText?.Length ?? 0, 
                new { request.VoiceStyle, request.VideoLength, request.Resolution, request.Background });
            
            var command = new CreateGenerationTaskCommand(
                request.AvatarId, 
                request.SpeechText ?? string.Empty, 
                request.ActionPrompt,
                request.VoiceStyle,
                request.VideoLength,
                request.Resolution,
                request.Background);
            
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
    public async Task<IActionResult> GetGenerationTask(Guid id)
    {
        try
        {
            _logger.LogInformation("Getting generation task with ID {TaskId}", id);
            
            var query = new GetGenerationTaskByIdQuery(id);
            var task = await _mediator.Send(query);
            
            if (task == null)
            {
                _logger.LogWarning("Generation task with ID {TaskId} not found", id);
                return NotFound(new { error = $"Generation task with ID {id} not found" });
            }
            
            return Ok(task);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting generation task with ID {TaskId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<GenerationTaskDto>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetGenerationTasks([FromQuery] Guid? avatarId = null, [FromQuery] Guid? userId = null)
    {
        try
        {
            _logger.LogInformation("Getting generation tasks for avatar {AvatarId}, user {UserId}", avatarId, userId);
            
            var query = new GetGenerationTasksQuery(avatarId, userId);
            var tasks = await _mediator.Send(query);
            
            return Ok(tasks);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting generation tasks for avatar {AvatarId}, user {UserId}", avatarId, userId);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpGet("{id:guid}/progress")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetTaskProgress(Guid id)
    {
        try
        {
            _logger.LogInformation("Getting progress for task {TaskId}", id);
            
            var query = new GetGenerationTaskByIdQuery(id);
            var task = await _mediator.Send(query);
            
            if (task == null)
            {
                _logger.LogWarning("Generation task with ID {TaskId} not found", id);
                return NotFound(new { error = $"Generation task with ID {id} not found" });
            }
            
            var progress = new
            {
                TaskId = task.Id,
                Status = task.Status.ToString(),
                Progress = task.Progress * 100,
                CurrentStage = task.Stage.ToString(),
                EstimatedTimeRemaining = CalculateEstimatedTimeRemaining(task),
                Logs = task.TaskLogs?.Select(log => new 
                { 
                    Timestamp = log.CreatedAt, 
                    Stage = log.Stage.ToString(),
                    Message = log.Message 
                }).OrderByDescending(log => log.Timestamp).Take(10)
            };
            
            return Ok(progress);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting progress for task {TaskId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpPost("{id:guid}/cancel")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CancelTask(Guid id)
    {
        try
        {
            _logger.LogInformation("Cancelling generation task with ID {TaskId}", id);
            
            var command = new CancelGenerationTaskCommand(id);
            await _mediator.Send(command);
            
            return Ok(new { message = "Task cancelled successfully", taskId = id });
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for cancelling task");
            return BadRequest(new { error = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Generation task with ID {TaskId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error cancelling generation task with ID {TaskId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpPost("{id:guid}/retry")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> RetryTask(Guid id)
    {
        try
        {
            _logger.LogInformation("Retrying generation task with ID {TaskId}", id);
            
            var command = new RetryGenerationTaskCommand(id);
            await _mediator.Send(command);
            
            return Ok(new { message = "Task retry initiated successfully", taskId = id });
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for retrying task");
            return BadRequest(new { error = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Generation task with ID {TaskId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrying generation task with ID {TaskId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpDelete("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteTask(Guid id)
    {
        try
        {
            _logger.LogInformation("Deleting generation task with ID {TaskId}", id);
            
            var command = new DeleteGenerationTaskCommand(id);
            await _mediator.Send(command);
            
            return NoContent();
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Generation task with ID {TaskId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting generation task with ID {TaskId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    private string? CalculateEstimatedTimeRemaining(GenerationTaskDto task)
    {
        if (task.Status == Domain.Enums.TaskStatus.Completed || task.Status == Domain.Enums.TaskStatus.Failed)
        {
            return null;
        }

        // Simple estimation based on stage
        var stageWeights = new Dictionary<Domain.Enums.TaskStage, int>
        {
            { Domain.Enums.TaskStage.AudioPreprocessing, 10 },
            { Domain.Enums.TaskStage.VoiceCloning, 25 },
            { Domain.Enums.TaskStage.MediaAnalysis, 15 },
            { Domain.Enums.TaskStage.Lipsync, 30 },
            { Domain.Enums.TaskStage.VideoRendering, 15 },
            { Domain.Enums.TaskStage.PostProcessing, 5 }
        };

        if (stageWeights.TryGetValue(task.Stage, out var weight))
        {
            var estimatedSeconds = weight * 2; // 2 seconds per weight unit
            return $"{estimatedSeconds} seconds";
        }

        return "Unknown";
    }
}

public class CreateGenerationTaskRequest
{
    public Guid AvatarId { get; set; }
    public string? SpeechText { get; set; }
    public string? ActionPrompt { get; set; }
    public string? VoiceStyle { get; set; }
    public string? VideoLength { get; set; }
    public string? Resolution { get; set; }
    public string? Background { get; set; }
}
