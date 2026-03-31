using System.Linq.Expressions;

namespace AvatarAI.Application.Interfaces;

public interface IBackgroundJobService
{
    string EnqueueAvatarGeneration(Guid avatarId, Guid voiceProfileId, string text);
    string EnqueueVoiceCloning(Guid voiceProfileId, string audioSamplePath);
    string EnqueueLipsync(Guid generationTaskId, string videoPath, string audioPath);
    string EnqueueLoraTraining(Guid avatarId, IEnumerable<string> imagePaths);
    
    // General purpose enqueue method
    string Enqueue(Expression<Func<Task>> task);
    
    bool CancelJob(string jobId);
    string GetJobStatus(string jobId);
    IEnumerable<string> GetActiveJobs();
}
