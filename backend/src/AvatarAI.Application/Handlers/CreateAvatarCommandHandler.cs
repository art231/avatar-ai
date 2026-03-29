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
    private readonly IMapper _mapper;

    public CreateAvatarCommandHandler(IUserRepository userRepository, IMapper mapper)
    {
        _userRepository = userRepository;
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

        // Create avatar
        var avatar = new Avatar(request.UserId, request.Name);
        
        // In real implementation, we would save to database
        // For now, we'll just map to DTO
        var avatarDto = _mapper.Map<AvatarDto>(avatar);
        
        return avatarDto;
    }
}