import re
import sys

with open('backend/src/AvatarAI.Application/Services/TrainingPipelineService.cs', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace direct property assignments with method calls
patterns = [
    # task.Progress = X -> task.UpdateProgress(X)
    (r'task\.Progress\s*=\s*([\d\.]+m)', r'task.UpdateProgress(\1)'),
    # task.Stage = X -> task.UpdateStage(X)
    (r'task\.Stage\s*=\s*([\w\.]+)', r'task.UpdateStage(\1)'),
    # task.Status = TaskStatus.X -> task.UpdateStatus(Domain.Enums.TaskStatus.X)
    (r'task\.Status\s*=\s*TaskStatus\.(\w+)', r'task.UpdateStatus(Domain.Enums.TaskStatus.\1)'),
    # avatar.Status = AvatarStatus.X -> avatar.UpdateStatus(AvatarStatus.X)
    (r'avatar\.Status\s*=\s*AvatarStatus\.(\w+)', r'avatar.UpdateStatus(AvatarStatus.\1)'),
    # avatar.ModelPath = X -> avatar.SetModelPath(X)
    (r'avatar\.ModelPath\s*=\s*([^;]+);', r'avatar.SetModelPath(\1);'),
    # avatar.VoiceProfile = X -> avatar.SetVoiceProfile(X)
    (r'avatar\.VoiceProfile\s*=\s*([^;]+);', r'avatar.SetVoiceProfile(\1);'),
    # task.ErrorMessage = X -> task.UpdateErrorMessage(X)
    (r'task\.ErrorMessage\s*=\s*([^;]+);', r'task.UpdateErrorMessage(\1);'),
    # task.CompletedAt = X -> (cannot assign directly, need to use UpdateStatus)
    # We'll handle this separately
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# 2. Replace Metadata direct assignment with UpdateMetadata
def replace_metadata(match):
    key = match.group(1)
    value = match.group(2)
    return f'task.UpdateMetadata("{key}", {value})'

content = re.sub(r'task\.Metadata\["([^"]+)"\]\s*=\s*([^;]+);', replace_metadata, content)

# 3. Fix TaskLog creation
tasklog_pattern = r'var taskLog = new TaskLog\s*\r?\n\s*{\s*\r?\n\s*Id = Guid\.NewGuid\(\),\s*\r?\n\s*TaskId = taskId,\s*\r?\n\s*Stage = stage,\s*\r?\n\s*Message = message,\s*\r?\n\s*CreatedAt = DateTime\.UtcNow\s*\r?\n\s*};'
tasklog_replacement = 'var taskLog = new TaskLog(taskId, stage, message);'
content = re.sub(tasklog_pattern, tasklog_replacement, content, flags=re.DOTALL)

# 4. Fix ambiguous TaskStatus references
content = content.replace('TaskStatus.', 'Domain.Enums.TaskStatus.')

# 5. Fix Metadata access - we need to keep reading access
# task.Metadata["key"] stays as is, only writing changes

with open('backend/src/AvatarAI.Application/Services/TrainingPipelineService.cs', 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully")
