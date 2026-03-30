using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Interfaces
{
    public interface IPipelineOrchestrator
    {
        Task<GenerationTaskDto> ProcessAvatarGenerationAsync(
            GenerationTaskDto taskDto,
            CancellationToken cancellationToken = default);

        Task<GenerationTaskDto> ProcessVoiceCloningAsync(
            VoiceProfileDto voiceProfileDto,
            string textToSynthesize,
            CancellationToken cancellationToken = default);

        Task<GenerationTaskDto> ProcessLipSyncOnlyAsync(
            string videoPath,
            string audioPath,
            CancellationToken cancellationToken = default);

        // Методы для фоновых задач
        Task GenerateAvatarAsync(Guid avatarId, Guid voiceProfileId, string text);
        Task CloneVoiceAsync(Guid voiceProfileId, string audioSamplePath);
        Task ApplyLipsyncAsync(Guid generationTaskId, string videoPath, string audioPath);
        Task TrainLoraAsync(Guid avatarId, List<string> imagePaths);
    }
}
