using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using AvatarAI.Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace AvatarAI.Infrastructure.Services
{
    /// <summary>
    /// Сервис для работы с файловым хранилищем на локальной файловой системе
    /// </summary>
    public class FileStorageService : IFileStorageService
    {
        private readonly string _baseStoragePath;
        private readonly ILogger<FileStorageService> _logger;

        public FileStorageService(IConfiguration configuration, ILogger<FileStorageService> logger)
        {
            _logger = logger;
            
            // Получаем базовый путь из конфигурации или используем значение по умолчанию
            _baseStoragePath = configuration["Storage:BasePath"] ?? "uploads";
            
            // Создаем базовую директорию, если она не существует
            if (!Directory.Exists(_baseStoragePath))
            {
                Directory.CreateDirectory(_baseStoragePath);
                _logger.LogInformation("Created base storage directory: {BasePath}", _baseStoragePath);
            }
            
            _logger.LogInformation("FileStorageService initialized with base path: {BasePath}", _baseStoragePath);
        }

        public async Task<string> SaveFileAsync(Stream stream, string containerName, string fileName, string contentType)
        {
            if (stream == null)
                throw new ArgumentNullException(nameof(stream));
            
            if (string.IsNullOrEmpty(containerName))
                throw new ArgumentException("Container name cannot be null or empty", nameof(containerName));
            
            if (string.IsNullOrEmpty(fileName))
                throw new ArgumentException("File name cannot be null or empty", nameof(fileName));

            var containerPath = GetContainerPath(containerName);
            var filePath = Path.Combine(containerPath, fileName);
            
            // Создаем директорию контейнера, если она не существует
            Directory.CreateDirectory(containerPath);
            
            _logger.LogDebug("Saving file to: {FilePath} (Content-Type: {ContentType})", filePath, contentType);
            
            using (var fileStream = new FileStream(filePath, FileMode.Create, FileAccess.Write))
            {
                await stream.CopyToAsync(fileStream);
            }
            
            _logger.LogInformation("File saved successfully: {FilePath}", filePath);
            
            return GetRelativePath(filePath);
        }

        public async Task<string> SaveFileAsync(byte[] data, string containerName, string fileName, string contentType)
        {
            if (data == null)
                throw new ArgumentNullException(nameof(data));
            
            using (var stream = new MemoryStream(data))
            {
                return await SaveFileAsync(stream, containerName, fileName, contentType);
            }
        }

        public Task<Stream> GetFileStreamAsync(string filePath)
        {
            var fullPath = GetFullPath(filePath);
            
            if (!File.Exists(fullPath))
            {
                _logger.LogWarning("File not found: {FilePath}", filePath);
                throw new FileNotFoundException($"File not found: {filePath}", filePath);
            }
            
            var stream = new FileStream(fullPath, FileMode.Open, FileAccess.Read, FileShare.Read);
            _logger.LogDebug("File stream opened: {FilePath}", filePath);
            
            return Task.FromResult<Stream>(stream);
        }

        public async Task<byte[]> GetFileBytesAsync(string filePath)
        {
            var fullPath = GetFullPath(filePath);
            
            if (!File.Exists(fullPath))
            {
                _logger.LogWarning("File not found: {FilePath}", filePath);
                throw new FileNotFoundException($"File not found: {filePath}", filePath);
            }
            
            _logger.LogDebug("Reading file bytes: {FilePath}", filePath);
            return await File.ReadAllBytesAsync(fullPath);
        }

        public Task<string> GetFileUrlAsync(string filePath)
        {
            var fullPath = GetFullPath(filePath);
            
            if (!File.Exists(fullPath))
            {
                _logger.LogWarning("File not found when generating URL: {FilePath}", filePath);
                throw new FileNotFoundException($"File not found: {filePath}", filePath);
            }
            
            // В реальном приложении здесь должен быть URL к файловому серверу или CDN
            // Для локальной разработки возвращаем относительный путь
            var url = $"/files/{filePath}";
            _logger.LogDebug("Generated file URL: {Url}", url);
            
            return Task.FromResult(url);
        }

        public Task<bool> DeleteFileAsync(string filePath)
        {
            var fullPath = GetFullPath(filePath);
            
            if (!File.Exists(fullPath))
            {
                _logger.LogWarning("File not found for deletion: {FilePath}", filePath);
                return Task.FromResult(false);
            }
            
            try
            {
                File.Delete(fullPath);
                _logger.LogInformation("File deleted successfully: {FilePath}", filePath);
                return Task.FromResult(true);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting file: {FilePath}", filePath);
                return Task.FromResult(false);
            }
        }

        public Task<bool> FileExistsAsync(string filePath)
        {
            var fullPath = GetFullPath(filePath);
            var exists = File.Exists(fullPath);
            
            _logger.LogDebug("File exists check: {FilePath} = {Exists}", filePath, exists);
            return Task.FromResult(exists);
        }

        public Task<long> GetFileSizeAsync(string filePath)
        {
            var fullPath = GetFullPath(filePath);
            
            if (!File.Exists(fullPath))
            {
                _logger.LogWarning("File not found when getting size: {FilePath}", filePath);
                throw new FileNotFoundException($"File not found: {filePath}", filePath);
            }
            
            var fileInfo = new FileInfo(fullPath);
            _logger.LogDebug("File size: {FilePath} = {Size} bytes", filePath, fileInfo.Length);
            
            return Task.FromResult(fileInfo.Length);
        }

        public Task<IEnumerable<string>> ListFilesAsync(string containerName, string? prefix = null)
        {
            var containerPath = GetContainerPath(containerName);
            
            if (!Directory.Exists(containerPath))
            {
                _logger.LogDebug("Container directory not found: {ContainerPath}", containerPath);
                return Task.FromResult(Enumerable.Empty<string>());
            }
            
            var files = Directory.GetFiles(containerPath, "*", SearchOption.AllDirectories);
            
            // Фильтруем по префиксу, если указан
            if (!string.IsNullOrEmpty(prefix))
            {
                files = files.Where(f => Path.GetFileName(f).StartsWith(prefix, StringComparison.OrdinalIgnoreCase)).ToArray();
            }
            
            // Преобразуем в относительные пути
            var relativePaths = files.Select(f => GetRelativePath(f)).ToList();
            
            _logger.LogDebug("Listed {Count} files in container: {ContainerName}", relativePaths.Count, containerName);
            
            return Task.FromResult<IEnumerable<string>>(relativePaths);
        }

        public async Task<bool> CopyFileAsync(string sourcePath, string destinationPath)
        {
            var sourceFullPath = GetFullPath(sourcePath);
            var destinationFullPath = GetFullPath(destinationPath);
            
            if (!File.Exists(sourceFullPath))
            {
                _logger.LogWarning("Source file not found for copy: {SourcePath}", sourcePath);
                return false;
            }
            
            // Создаем директорию назначения, если она не существует
            var destinationDir = Path.GetDirectoryName(destinationFullPath);
            if (!string.IsNullOrEmpty(destinationDir) && !Directory.Exists(destinationDir))
            {
                Directory.CreateDirectory(destinationDir);
            }
            
            try
            {
                await Task.Run(() => File.Copy(sourceFullPath, destinationFullPath, overwrite: true));
                _logger.LogInformation("File copied: {SourcePath} -> {DestinationPath}", sourcePath, destinationPath);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error copying file: {SourcePath} -> {DestinationPath}", sourcePath, destinationPath);
                return false;
            }
        }

        public async Task<bool> MoveFileAsync(string sourcePath, string destinationPath)
        {
            var sourceFullPath = GetFullPath(sourcePath);
            var destinationFullPath = GetFullPath(destinationPath);
            
            if (!File.Exists(sourceFullPath))
            {
                _logger.LogWarning("Source file not found for move: {SourcePath}", sourcePath);
                return false;
            }
            
            // Создаем директорию назначения, если она не существует
            var destinationDir = Path.GetDirectoryName(destinationFullPath);
            if (!string.IsNullOrEmpty(destinationDir) && !Directory.Exists(destinationDir))
            {
                Directory.CreateDirectory(destinationDir);
            }
            
            try
            {
                await Task.Run(() => File.Move(sourceFullPath, destinationFullPath, overwrite: true));
                _logger.LogInformation("File moved: {SourcePath} -> {DestinationPath}", sourcePath, destinationPath);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error moving file: {SourcePath} -> {DestinationPath}", sourcePath, destinationPath);
                return false;
            }
        }

        #region Helper Methods

        private string GetContainerPath(string containerName)
        {
            // Очищаем имя контейнера от недопустимых символов
            var safeContainerName = string.Join("_", containerName.Split(Path.GetInvalidFileNameChars()));
            return Path.Combine(_baseStoragePath, safeContainerName);
        }

        private string GetFullPath(string relativePath)
        {
            // Если путь уже абсолютный, возвращаем как есть
            if (Path.IsPathRooted(relativePath))
                return relativePath;
            
            return Path.Combine(_baseStoragePath, relativePath);
        }

        private string GetRelativePath(string fullPath)
        {
            // Преобразуем абсолютный путь в относительный относительно базовой директории
            if (fullPath.StartsWith(_baseStoragePath, StringComparison.OrdinalIgnoreCase))
            {
                return fullPath.Substring(_baseStoragePath.Length).TrimStart(Path.DirectorySeparatorChar);
            }
            
            return fullPath;
        }

        #endregion
    }
}