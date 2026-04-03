using MediatR;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Queries;

public class GetGenerationTaskByIdQuery : IRequest<GenerationTaskDto?>
{
    public Guid Id { get; }

    public GetGenerationTaskByIdQuery(Guid id)
    {
        Id = id;
    }
}