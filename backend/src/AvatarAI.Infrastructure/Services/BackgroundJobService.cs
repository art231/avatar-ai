using AvatarAI.Application.Interfaces;
using Hangfire;
using Hangfire.States;

namespace AvatarAI.Infrastructure.Services;

public class BackgroundJobService : IBackgroundJobService
{
    private readonly IBackgroundJobClient _backgroundJobClient;
    private readonly IRecurringJobManager _recurringJobManager;
    private readonly IPipelineOrchestrator _pipelineOrchestrator;

    public BackgroundJobService(
        IBackgroundJobClient backgroundJobClient,
        IRecurringJobManager recurringJobManager,
        IPipelineOrchestrator pipelineOrchestrator)
    {
        _backgroundJobClient = backgroundJobClient;
        _recurringJobManager = recurringJobManager;
        _pipelineOrchestrator = pipelineOrchestrator;
    }

    public string EnqueueAvatarGeneration(Guid avatarId, Guid voiceProfileId, string text)
    {
        return _backgroundJobClient.Enqueue(() => 
            _pipelineOrchestrator.GenerateAvatarAsync(avatarId, voiceProfileId, text));
    }

    public string EnqueueVoiceCloning(Guid voiceProfileId, string audioSamplePath)
    {
        return _backgroundJobClient.Enqueue(() => 
            _pipelineOrchestrator.CloneVoiceAsync(voiceProfileId, audioSamplePath));
    }

    public string EnqueueLipsync(Guid generationTaskId, string videoPath, string audioPath)
    {
        return _backgroundJobClient.Enqueue(() => 
            _pipelineOrchestrator.ApplyLipsyncAsync(generationTaskId, videoPath, audioPath));
    }

    public string EnqueueLoraTraining(Guid avatarId, IEnumerable<string> imagePaths)
    {
        return _backgroundJobClient.Enqueue(() => 
            _pipelineOrchestrator.TrainLoraAsync(avatarId, imagePaths.ToList()));
    }

    public bool CancelJob(string jobId)
    {
        try
        {
            var job = JobStorage.Current.GetConnection().GetJobData(jobId);
            if (job != null && job.State == EnqueuedState.StateName)
            {
                _backgroundJobClient.Delete(jobId);
                return true;
            }
            return false;
        }
        catch
        {
            return false;
        }
    }

    public string GetJobStatus(string jobId)
    {
        try
        {
            var job = JobStorage.Current.GetConnection().GetJobData(jobId);
            return job?.State ?? "Unknown";
        }
        catch
        {
            return "Error";
        }
    }

    public IEnumerable<string> GetActiveJobs()
    {
        try
        {
            var monitoringApi = JobStorage.Current.GetMonitoringApi();
            var jobs = monitoringApi.EnqueuedJobs("default", 0, 100);
            return jobs.Select(j => j.Key).ToList();
        }
        catch
        {
            return Enumerable.Empty<string>();
        }
    }

    // Методы для периодических задач
    public void ScheduleCleanupOldFiles()
    {
        _recurringJobManager.AddOrUpdate(
            "cleanup-old-files",
            () => CleanupOldFilesAsync(),
            Cron.Daily);
    }

    public void ScheduleHealthCheck()
    {
        _recurringJobManager.AddOrUpdate(
            "health-check",
            () => CheckAIServicesHealthAsync(),
            Cron.Hourly);
    }

    [AutomaticRetry(Attempts = 3)]
    public async Task CleanupOldFilesAsync()
    {
        // Логика очистки старых файлов
        await Task.Delay(100); // Заглушка
    }

    [AutomaticRetry(Attempts = 3)]
    public async Task CheckAIServicesHealthAsync()
    {
        // Логика проверки здоровья AI сервисов
        await Task.Delay(100); // Заглушка
    }
}