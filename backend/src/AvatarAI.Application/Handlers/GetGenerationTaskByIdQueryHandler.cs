using MediatR;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.Queries;
using AvatarAI.Application.DTOs;
using AutoMapper;

namespace AvatarAI.Application.Handlers;

public class GetGenerationTaskByIdQueryHandler : IRequestHandler<GetGenerationTaskByIdQuery, GenerationTaskDto?>
{
    private readonly IGenerationTaskRepository _generationTaskRepository;
    private readonly IMapper _mapper;

    public GetGenerationTaskByIdQueryHandler(IGenerationTaskRepository generationTaskRepository, IMapper mapper)
    {
        _generationTaskRepository = generationTaskRepository;
        _mapper = mapper;
    }

    public async Task<GenerationTaskDto?> Handle(GetGenerationTaskByIdQuery request, CancellationToken cancellationToken)
    {
        var task = await _generationTaskRepository.GetWithLogsAsync(request.Id, cancellationToken);
        
        if (task == null)
        {
            return null;
        }

        return _mapper.Map<GenerationTaskDto>(task);
    }
}