using AutoMapper;
using AvatarAI.Domain.Entities;
using AvatarAI.Application.DTOs;

namespace AvatarAI.Application.Mapping;

public class MappingProfile : Profile
{
    public MappingProfile()
    {
        // User mappings
        CreateMap<User, UserDto>();
        
        // Avatar mappings
        CreateMap<Avatar, AvatarDto>()
            .ForMember(dest => dest.VoiceProfile, opt => opt.MapFrom(src => src.VoiceProfile))
            .ForMember(dest => dest.GenerationTasks, opt => opt.MapFrom(src => src.GenerationTasks));
        
        // VoiceProfile mappings
        CreateMap<VoiceProfile, VoiceProfileDto>();
        
        // GenerationTask mappings
        CreateMap<GenerationTask, GenerationTaskDto>()
            .ForMember(dest => dest.TaskLogs, opt => opt.MapFrom(src => src.TaskLogs));
        
        // TaskLog mappings
        CreateMap<TaskLog, TaskLogDto>();
    }
}