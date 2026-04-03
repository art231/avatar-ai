using MediatR;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.Queries;
using AvatarAI.Application.DTOs;
using AutoMapper;

namespace AvatarAI.Application.Handlers;

public class GetAvatarByIdQueryHandler : IRequestHandler<GetAvatarByIdQuery, AvatarDto?>
{
    private readonly IAvatarRepository _avatarRepository;
    private readonly IMapper _mapper;

    public GetAvatarByIdQueryHandler(IAvatarRepository avatarRepository, IMapper mapper)
    {
        _avatarRepository = avatarRepository;
        _mapper = mapper;
    }

    public async Task<AvatarDto?> Handle(GetAvatarByIdQuery request, CancellationToken cancellationToken)
    {
        var avatar = await _avatarRepository.GetByIdAsync(request.Id, cancellationToken);
        
        if (avatar == null)
        {
            return null;
        }

        return _mapper.Map<AvatarDto>(avatar);
    }
}