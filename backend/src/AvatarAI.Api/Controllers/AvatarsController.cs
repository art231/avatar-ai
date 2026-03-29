using Microsoft.AspNetCore.Mvc;
using MediatR;
using AvatarAI.Application.Commands;
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
    public async Task<IActionResult> CreateAvatar([FromBody] CreateAvatarRequest request)
    {
        try
        {
            _logger.LogInformation("Creating avatar for user {UserId} with name {Name}", 
                request.UserId, request.Name);
            
            var command = new CreateAvatarCommand(request.UserId, request.Name);
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
    public Task<IActionResult> GetAvatar(Guid id)
    {
        // In real implementation, we would have a query to get avatar by ID
        // For MVP, we'll return a simulated response
        var avatar = new AvatarDto
        {
            Id = id,
            UserId = Guid.NewGuid(),
            Name = "Test Avatar",
            Status = Domain.Enums.AvatarStatus.Active,
            CreatedAt = DateTime.UtcNow.AddDays(-1),
            UpdatedAt = DateTime.UtcNow
        };
        
        return Task.FromResult<IActionResult>(Ok(avatar));
    }

    [HttpGet]
    [ProducesResponseType(typeof(List<AvatarDto>), StatusCodes.Status200OK)]
    public Task<IActionResult> GetAvatars([FromQuery] Guid? userId = null)
    {
        // In real implementation, we would query avatars from database
        // For MVP, we'll return simulated data
        var avatars = new List<AvatarDto>
        {
            new()
            {
                Id = Guid.NewGuid(),
                UserId = userId ?? Guid.NewGuid(),
                Name = "Personal Avatar",
                Status = Domain.Enums.AvatarStatus.Active,
                CreatedAt = DateTime.UtcNow.AddDays(-2),
                UpdatedAt = DateTime.UtcNow.AddHours(-1)
            },
            new()
            {
                Id = Guid.NewGuid(),
                UserId = userId ?? Guid.NewGuid(),
                Name = "Business Avatar",
                Status = Domain.Enums.AvatarStatus.Training,
                CreatedAt = DateTime.UtcNow.AddDays(-1),
                UpdatedAt = DateTime.UtcNow
            }
        };
        
        return Task.FromResult<IActionResult>(Ok(avatars));
    }
}

public class CreateAvatarRequest
{
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
}