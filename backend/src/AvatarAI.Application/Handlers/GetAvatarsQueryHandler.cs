using MediatR;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.Queries;
using AvatarAI.Application.DTOs;
using AutoMapper;

namespace AvatarAI.Application.Handlers;

public class GetAvatarsQueryHandler : IRequestHandler<GetAvatarsQuery, IEnumerable<AvatarDto>>
{
    private readonly IAvatarRepository _avatarRepository;
    private readonly IMapper _mapper;

    public GetAvatarsQueryHandler(IAvatarRepository avatarRepository, IMapper mapper)
    {
        _avatarRepository = avatarRepository;
        _mapper = mapper;
    }

    public async Task<IEnumerable<AvatarDto>> Handle(GetAvatarsQuery request, CancellationToken cancellationToken)
    {
        IEnumerable<Domain.Entities.Avatar> avatars;
        
        if (request.UserId.HasValue)
        {
            avatars = await _avatarRepository.GetByUserIdAsync(request.UserId.Value, cancellationToken);
        }
        else
        {
            avatars = await _avatarRepository.GetAllAsync(cancellationToken);
        }

        return _mapper.Map<IEnumerable<AvatarDto>>(avatars);
    }
}