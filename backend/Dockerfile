# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Clean NuGet cache and temporary files before copying
RUN rm -rf /root/.nuget /root/.local/share/NuGet /root/.dotnet/NuGetFallbackFolder

# Copy everything
COPY . .

# Clean any obj/bin directories that might have been copied from host
RUN find . -type d -name "obj" -o -name "bin" | xargs rm -rf 2>/dev/null || true

# Restore dependencies with clean cache
RUN dotnet restore AvatarAI.sln --force --no-cache

# Build and publish
RUN dotnet build AvatarAI.sln -c Release --no-restore
RUN dotnet publish src/AvatarAI.Api/AvatarAI.Api.csproj -c Release -o /app/publish --no-restore

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Install curl for health checks with retry logic
RUN apt-get update || apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy published application
COPY --from=build /app/publish .

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080
EXPOSE 8081

# Entry point
ENTRYPOINT ["dotnet", "AvatarAI.Api.dll"]