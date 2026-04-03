using MediatR;
using Microsoft.Extensions.Logging;
using AvatarAI.Domain.Entities;
using AvatarAI.Domain.Interfaces;
using AvatarAI.Application.Commands;
using AvatarAI.Application.DTOs;
using AvatarAI.Application.Interfaces;
using AutoMapper;

namespace AvatarAI.Application.Handlers;

public class CreateGenerationTaskCommandHandler : IRequestHandler<CreateGenerationTaskCommand, GenerationTaskDto>
{
    private readonly IAvatarRepository _avatarRepository;
    private readonly IGenerationTaskRepository _generationTaskRepository;
    private readonly ITaskLogRepository _taskLogRepository;
    private readonly IPipelineOrchestrator _pipelineOrchestrator;
    private readonly IMapper _mapper;
    private readonly ILogger<CreateGenerationTaskCommandHandler> _logger;

    public CreateGenerationTaskCommandHandler(
        IAvatarRepository avatarRepository,
        IGenerationTaskRepository generationTaskRepository,
        ITaskLogRepository taskLogRepository,
        IPipelineOrchestrator pipelineOrchestrator,
        IMapper mapper,
        ILogger<CreateGenerationTaskCommandHandler> logger)
    {
        _avatarRepository = avatarRepository;
        _generationTaskRepository = generationTaskRepository;
        _taskLogRepository = taskLogRepository;
        _pipelineOrchestrator = pipelineOrchestrator;
        _mapper = mapper;
        _logger = logger;
    }

    public async Task<GenerationTaskDto> Handle(CreateGenerationTaskCommand request, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Creating generation task for avatar {AvatarId} with text: {Text}", 
            request.AvatarId, request.SpeechText);

        // Validate avatar exists and is ready for generation
        var avatar = await _avatarRepository.GetByIdAsync(request.AvatarId, cancellationToken);
        if (avatar == null)
        {
            throw new ArgumentException($"Avatar with ID {request.AvatarId} not found");
        }

        if (!avatar.IsReadyForGeneration())
        {
            throw new ArgumentException($"Avatar with ID {request.AvatarId} is not ready for generation. Status: {avatar.Status}");
        }

        // Check if avatar already has active tasks
        var activeTasks = await _generationTaskRepository.GetByAvatarIdAsync(request.AvatarId, cancellationToken);
        var hasActiveTasks = activeTasks.Any(t => t.Status == Domain.Enums.TaskStatus.Pending || t.Status == Domain.Enums.TaskStatus.Processing);
        if (hasActiveTasks)
        {
            throw new ArgumentException($"Avatar with ID {request.AvatarId} already has active tasks. Please wait for them to complete.");
        }

        // Create and save task
        var task = new GenerationTask(request.AvatarId, request.SpeechText, request.ActionPrompt);
        await _generationTaskRepository.AddAsync(task, cancellationToken);

        // Add initial log
        var initialLog = new TaskLog(task.Id, Domain.Enums.TaskStage.AudioPreprocessing, "Generation task created and queued for processing");
        await _taskLogRepository.AddAsync(initialLog, cancellationToken);

        // Start pipeline processing in background (fire-and-forget)
        _ = Task.Run(async () =>
        {
            try
            {
                await ProcessTaskInBackground(task, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing task {TaskId} in background", task.Id);
            }
        }, cancellationToken);

        var taskDto = _mapper.Map<GenerationTaskDto>(task);
        return taskDto;
    }

    private async Task ProcessTaskInBackground(GenerationTask task, CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Starting background processing for task {TaskId}", task.Id);

            // Update task status to Processing
            task.UpdateStatus(Domain.Enums.TaskStatus.Processing);
            await _generationTaskRepository.UpdateAsync(task, cancellationToken);
            
            var processingLog = new TaskLog(task.Id, Domain.Enums.TaskStage.AudioPreprocessing, "Starting audio preprocessing");
            await _taskLogRepository.AddAsync(processingLog, cancellationToken);

            // Get avatar for pipeline processing
            var avatar = await _avatarRepository.GetByIdAsync(task.AvatarId, cancellationToken);
            if (avatar == null)
            {
                throw new InvalidOperationException($"Avatar with ID {task.AvatarId} not found during processing");
            }

            // Create task DTO for pipeline
            var taskDto = _mapper.Map<GenerationTaskDto>(task);
            
            // Process through pipeline orchestrator
            var processedTask = await _pipelineOrchestrator.ProcessAvatarGenerationAsync(taskDto, cancellationToken);
            
            // Update task with results
            task.UpdateStatus(processedTask.Status);
            task.UpdateStage(Domain.Enums.TaskStage.Completed);
            task.SetOutputPath(processedTask.OutputPath ?? string.Empty);
            task.UpdateProgress(1.0m);
            
            if (processedTask.CompletedAt.HasValue)
            {
                // Note: CompletedAt is set automatically when status changes to Completed
            }
            
            await _generationTaskRepository.UpdateAsync(task, cancellationToken);
            
            var completedLog = new TaskLog(task.Id, Domain.Enums.TaskStage.Completed, 
                $"Generation task completed successfully. Output: {processedTask.OutputPath}");
            await _taskLogRepository.AddAsync(completedLog, cancellationToken);
            
            _logger.LogInformation("Background processing completed for task {TaskId}", task.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in background processing for task {TaskId}", task.Id);
            
            // Update task status to Failed
            task.UpdateStatus(Domain.Enums.TaskStatus.Failed);
            task.UpdateErrorMessage(ex.Message);
            await _generationTaskRepository.UpdateAsync(task, cancellationToken);
            
            var failedLog = new TaskLog(task.Id, Domain.Enums.TaskStage.Failed, 
                $"Generation task failed: {ex.Message}");
            await _taskLogRepository.AddAsync(failedLog, cancellationToken);
        }
    }
}
