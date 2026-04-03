using MediatR;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.Commands;
using AvatarAI.Application.DTOs;
using AutoMapper;

namespace AvatarAI.Application.Handlers;

public class CreateAvatarCommandHandler : IRequestHandler<CreateAvatarCommand, AvatarDto>
{
    private readonly IUserRepository _userRepository;
    private readonly IAvatarRepository _avatarRepository;
    private readonly IMapper _mapper;

    public CreateAvatarCommandHandler(
        IUserRepository userRepository, 
        IAvatarRepository avatarRepository,
        IMapper mapper)
    {
        _userRepository = userRepository;
        _avatarRepository = avatarRepository;
        _mapper = mapper;
    }

    public async Task<AvatarDto> Handle(CreateAvatarCommand request, CancellationToken cancellationToken)
    {
        // Validate user exists
        var user = await _userRepository.GetByIdAsync(request.UserId, cancellationToken);
        if (user == null)
        {
            throw new ArgumentException($"User with ID {request.UserId} not found");
        }

        // Check if avatar name already exists for this user
        var existingAvatar = await _avatarRepository.GetByUserIdAsync(request.UserId, cancellationToken);
        if (existingAvatar.Any(a => a.Name.Equals(request.Name, StringComparison.OrdinalIgnoreCase)))
        {
            throw new ArgumentException($"Avatar with name '{request.Name}' already exists for this user");
        }

        // Create avatar
        var avatar = new Avatar(request.UserId, request.Name);
        
        // Save to database
        await _avatarRepository.AddAsync(avatar, cancellationToken);
        
        // Map to DTO
        var avatarDto = _mapper.Map<AvatarDto>(avatar);
        
        return avatarDto;
    }
}
