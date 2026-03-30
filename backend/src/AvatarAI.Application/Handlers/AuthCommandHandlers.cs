using AvatarAI.Application.Commands;
using AvatarAI.Application.DTOs;
using AvatarAI.Application.Interfaces;
using MediatR;

namespace AvatarAI.Application.Handlers;

public class RegisterCommandHandler : IRequestHandler<RegisterCommand, AuthResponse>
{
    private readonly IAuthService _authService;

    public RegisterCommandHandler(IAuthService authService)
    {
        _authService = authService;
    }

    public async Task<AuthResponse> Handle(RegisterCommand request, CancellationToken cancellationToken)
    {
        return await _authService.RegisterAsync(request.Request);
    }
}

public class LoginCommandHandler : IRequestHandler<LoginCommand, AuthResponse>
{
    private readonly IAuthService _authService;

    public LoginCommandHandler(IAuthService authService)
    {
        _authService = authService;
    }

    public async Task<AuthResponse> Handle(LoginCommand request, CancellationToken cancellationToken)
    {
        return await _authService.LoginAsync(request.Request);
    }
}

public class RefreshTokenCommandHandler : IRequestHandler<RefreshTokenCommand, AuthResponse>
{
    private readonly IAuthService _authService;

    public RefreshTokenCommandHandler(IAuthService authService)
    {
        _authService = authService;
    }

    public async Task<AuthResponse> Handle(RefreshTokenCommand request, CancellationToken cancellationToken)
    {
        return await _authService.RefreshTokenAsync(request.Request.RefreshToken);
    }
}

public class RevokeTokenCommandHandler : IRequestHandler<RevokeTokenCommand, Unit>
{
    private readonly IAuthService _authService;

    public RevokeTokenCommandHandler(IAuthService authService)
    {
        _authService = authService;
    }

    public async Task<Unit> Handle(RevokeTokenCommand request, CancellationToken cancellationToken)
    {
        await _authService.RevokeTokenAsync(request.RefreshToken);
        return Unit.Value;
    }
}

public class GetUserProfileCommandHandler : IRequestHandler<GetUserProfileCommand, UserProfileDto>
{
    private readonly IAuthService _authService;

    public GetUserProfileCommandHandler(IAuthService authService)
    {
        _authService = authService;
    }

    public async Task<UserProfileDto> Handle(GetUserProfileCommand request, CancellationToken cancellationToken)
    {
        return await _authService.GetUserProfileAsync(request.UserId);
    }
}