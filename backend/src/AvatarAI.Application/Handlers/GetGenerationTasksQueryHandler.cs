using MediatR;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.Queries;
using AvatarAI.Application.DTOs;
using AutoMapper;

namespace AvatarAI.Application.Handlers;

public class GetGenerationTasksQueryHandler : IRequestHandler<GetGenerationTasksQuery, IEnumerable<GenerationTaskDto>>
{
    private readonly IGenerationTaskRepository _generationTaskRepository;
    private readonly IMapper _mapper;

    public GetGenerationTasksQueryHandler(IGenerationTaskRepository generationTaskRepository, IMapper mapper)
    {
        _generationTaskRepository = generationTaskRepository;
        _mapper = mapper;
    }

    public async Task<IEnumerable<GenerationTaskDto>> Handle(GetGenerationTasksQuery request, CancellationToken cancellationToken)
    {
        IEnumerable<Domain.Entities.GenerationTask> tasks;
        
        if (request.AvatarId.HasValue)
        {
            tasks = await _generationTaskRepository.GetByAvatarIdAsync(request.AvatarId.Value, cancellationToken);
        }
        else if (request.UserId.HasValue)
        {
            tasks = await _generationTaskRepository.GetByUserIdAsync(request.UserId.Value, cancellationToken);
        }
        else
        {
            tasks = await _generationTaskRepository.GetAllAsync(cancellationToken);
        }

        return _mapper.Map<IEnumerable<GenerationTaskDto>>(tasks);
    }
}