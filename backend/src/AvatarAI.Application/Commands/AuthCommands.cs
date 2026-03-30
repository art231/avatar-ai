using AvatarAI.Application.DTOs;
using MediatR;

namespace AvatarAI.Application.Commands;

public class RegisterCommand : IRequest<AuthResponse>
{
    public RegisterRequest Request { get; }

    public RegisterCommand(RegisterRequest request)
    {
        Request = request;
    }
}

public class LoginCommand : IRequest<AuthResponse>
{
    public LoginRequest Request { get; }

    public LoginCommand(LoginRequest request)
    {
        Request = request;
    }
}

public class RefreshTokenCommand : IRequest<AuthResponse>
{
    public RefreshTokenRequest Request { get; }

    public RefreshTokenCommand(RefreshTokenRequest request)
    {
        Request = request;
    }
}

public class RevokeTokenCommand : IRequest<Unit>
{
    public string RefreshToken { get; }

    public RevokeTokenCommand(string refreshToken)
    {
        RefreshToken = refreshToken;
    }
}

public class GetUserProfileCommand : IRequest<UserProfileDto>
{
    public Guid UserId { get; }

    public GetUserProfileCommand(Guid userId)
    {
        UserId = userId;
    }
}