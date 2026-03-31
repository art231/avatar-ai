namespace AvatarAI.Domain.Enums;

public enum TaskStage
{
    AudioPreprocessing = 0,
    VoiceCloning = 1,
    MediaAnalysis = 2,
    Lipsync = 3,
    VideoRendering = 4,
    PostProcessing = 5,
    Completed = 6,
    
    // Training pipeline stages
    DataPreparation = 7,
    FaceAnalysis = 8,
    VoiceAnalysis = 9,
    ModelTraining = 10,
    ModelValidation = 11
}
