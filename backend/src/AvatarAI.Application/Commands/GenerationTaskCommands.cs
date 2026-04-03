using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Commands;

public class CancelGenerationTaskCommand : IRequest<Unit>
{
    public Guid TaskId { get; set; }
    
    public CancelGenerationTaskCommand(Guid taskId)
    {
        TaskId = taskId;
    }
}

public class RetryGenerationTaskCommand : IRequest<Unit>
{
    public Guid TaskId { get; set; }
    
    public RetryGenerationTaskCommand(Guid taskId)
    {
        TaskId = taskId;
    }
}

public class DeleteGenerationTaskCommand : IRequest<Unit>
{
    public Guid TaskId { get; set; }
    
    public DeleteGenerationTaskCommand(Guid taskId)
    {
        TaskId = taskId;
    }
}