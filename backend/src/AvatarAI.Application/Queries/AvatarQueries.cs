using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Queries;

public class GetAvatarTrainingProgressQuery : IRequest<TrainingProgressDto>
{
    public Guid AvatarId { get; set; }
    
    public GetAvatarTrainingProgressQuery(Guid avatarId)
    {
        AvatarId = avatarId;
    }
}

public class TrainingProgressDto
{
    public Guid AvatarId { get; set; }
    public string Status { get; set; } = string.Empty;
    public int Progress { get; set; }
    public int TotalSteps { get; set; }
    public int CurrentStep { get; set; }
    public string CurrentStepName { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
    public DateTime StartedAt { get; set; }
    public DateTime? EstimatedCompletion { get; set; }
}