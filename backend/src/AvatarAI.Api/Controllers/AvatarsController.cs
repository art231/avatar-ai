using Microsoft.AspNetCore.Mvc;
using MediatR;
using AvatarAI.Application.Commands;
using AvatarAI.Application.Queries;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AvatarsController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly ILogger<AvatarsController> _logger;

    public AvatarsController(IMediator mediator, ILogger<AvatarsController> logger)
    {
        _mediator = mediator;
        _logger = logger;
    }

    [HttpPost]
    [ProducesResponseType(typeof(AvatarDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateAvatar([FromForm] CreateAvatarRequest request)
    {
        try
        {
            _logger.LogInformation("Creating avatar for user {UserId} with name {Name} and {ImageCount} images", 
                request.UserId, request.Name, request.Images?.Count ?? 0);
            
            var command = new CreateAvatarCommand(
                request.UserId, 
                request.Name, 
                request.Description,
                request.Images ?? new List<IFormFile>(),
                request.VoiceSample);
                
            var result = await _mediator.Send(command);
            
            return CreatedAtAction(nameof(GetAvatar), new { id = result.Id }, result);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for creating avatar");
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating avatar");
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(AvatarDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetAvatar(Guid id)
    {
        try
        {
            _logger.LogInformation("Getting avatar with ID {AvatarId}", id);
            
            var query = new GetAvatarByIdQuery(id);
            var avatar = await _mediator.Send(query);
            
            if (avatar == null)
            {
                _logger.LogWarning("Avatar with ID {AvatarId} not found", id);
                return NotFound(new { error = $"Avatar with ID {id} not found" });
            }
            
            return Ok(avatar);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting avatar with ID {AvatarId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<AvatarDto>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetAvatars([FromQuery] Guid? userId = null)
    {
        try
        {
            _logger.LogInformation("Getting avatars for user {UserId}", userId);
            
            var query = new GetAvatarsQuery(userId);
            var avatars = await _mediator.Send(query);
            
            return Ok(avatars);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting avatars for user {UserId}", userId);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpPut("{id:guid}")]
    [ProducesResponseType(typeof(AvatarDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> UpdateAvatar(Guid id, [FromBody] UpdateAvatarRequest request)
    {
        try
        {
            _logger.LogInformation("Updating avatar with ID {AvatarId}", id);
            
            var command = new UpdateAvatarCommand(id, request.Name, request.Description);
            var result = await _mediator.Send(command);
            
            return Ok(result);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for updating avatar");
            return BadRequest(new { error = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Avatar with ID {AvatarId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating avatar with ID {AvatarId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpDelete("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteAvatar(Guid id)
    {
        try
        {
            _logger.LogInformation("Deleting avatar with ID {AvatarId}", id);
            
            var command = new DeleteAvatarCommand(id);
            await _mediator.Send(command);
            
            return NoContent();
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Avatar with ID {AvatarId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting avatar with ID {AvatarId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpPost("{id:guid}/train")]
    [ProducesResponseType(StatusCodes.Status202Accepted)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> StartTraining(Guid id)
    {
        try
        {
            _logger.LogInformation("Starting training for avatar with ID {AvatarId}", id);
            
            var command = new StartAvatarTrainingCommand(id);
            await _mediator.Send(command);
            
            return Accepted(new { message = "Training started successfully", avatarId = id });
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for starting training");
            return BadRequest(new { error = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Avatar with ID {AvatarId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting training for avatar with ID {AvatarId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpGet("{id:guid}/training-progress")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetTrainingProgress(Guid id)
    {
        try
        {
            _logger.LogInformation("Getting training progress for avatar with ID {AvatarId}", id);
            
            var query = new GetAvatarTrainingProgressQuery(id);
            var progress = await _mediator.Send(query);
            
            return Ok(progress);
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Avatar with ID {AvatarId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting training progress for avatar with ID {AvatarId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }

    [HttpPost("{id:guid}/generate")]
    [ProducesResponseType(typeof(GenerationTaskDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> GenerateVideo(Guid id, [FromBody] GenerateVideoRequest request)
    {
        try
        {
            _logger.LogInformation("Generating video for avatar with ID {AvatarId} with text length: {TextLength}", 
                id, request.Text?.Length ?? 0);
            
            var command = new GenerateVideoCommand(
                id, 
                request.Text ?? string.Empty,
                request.VoiceStyle,
                request.VideoLength,
                request.Resolution,
                request.Background);
                
            var result = await _mediator.Send(command);
            
            return CreatedAtAction(nameof(GenerationTasksController.GetGenerationTask), 
                new { controller = "GenerationTasks", id = result.Id }, result);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Bad request for generating video");
            return BadRequest(new { error = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Avatar with ID {AvatarId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating video for avatar with ID {AvatarId}", id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Internal server error" });
        }
    }
}

public class CreateAvatarRequest
{
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public List<IFormFile>? Images { get; set; }
    public IFormFile? VoiceSample { get; set; }
}

public class UpdateAvatarRequest
{
    public string? Name { get; set; }
    public string? Description { get; set; }
}

public class GenerateVideoRequest
{
    public string? Text { get; set; }
    public string? VoiceStyle { get; set; }
    public string? VideoLength { get; set; }
    public string? Resolution { get; set; }
    public string? Background { get; set; }
}
