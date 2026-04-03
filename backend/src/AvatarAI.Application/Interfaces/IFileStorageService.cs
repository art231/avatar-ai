using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

namespace AvatarAI.Application.Interfaces
{
    /// <summary>
    /// Интерфейс сервиса для работы с файловым хранилищем
    /// </summary>
    public interface IFileStorageService
    {
        /// <summary>
        /// Сохранить файл из потока
        /// </summary>
        /// <param name="stream">Поток с данными файла</param>
        /// <param name="containerName">Имя контейнера/папки</param>
        /// <param name="fileName">Имя файла</param>
        /// <param name="contentType">Тип содержимого</param>
        /// <returns>Путь к сохраненному файлу</returns>
        Task<string> SaveFileAsync(Stream stream, string containerName, string fileName, string contentType);

        /// <summary>
        /// Сохранить файл из массива байтов
        /// </summary>
        /// <param name="data">Данные файла</param>
        /// <param name="containerName">Имя контейнера/папки</param>
        /// <param name="fileName">Имя файла</param>
        /// <param name="contentType">Тип содержимого</param>
        /// <returns>Путь к сохраненному файлу</returns>
        Task<string> SaveFileAsync(byte[] data, string containerName, string fileName, string contentType);

        /// <summary>
        /// Получить файл как поток
        /// </summary>
        /// <param name="filePath">Путь к файлу</param>
        /// <returns>Поток с данными файла</returns>
        Task<Stream> GetFileStreamAsync(string filePath);

        /// <summary>
        /// Получить файл как массив байтов
        /// </summary>
        /// <param name="filePath">Путь к файлу</param>
        /// <returns>Данные файла</returns>
        Task<byte[]> GetFileBytesAsync(string filePath);

        /// <summary>
        /// Получить URL файла
        /// </summary>
        /// <param name="filePath">Путь к файлу</param>
        /// <returns>URL для доступа к файлу</returns>
        Task<string> GetFileUrlAsync(string filePath);

        /// <summary>
        /// Удалить файл
        /// </summary>
        /// <param name="filePath">Путь к файлу</param>
        /// <returns>True если файл удален успешно</returns>
        Task<bool> DeleteFileAsync(string filePath);

        /// <summary>
        /// Проверить существование файла
        /// </summary>
        /// <param name="filePath">Путь к файлу</param>
        /// <returns>True если файл существует</returns>
        Task<bool> FileExistsAsync(string filePath);

        /// <summary>
        /// Получить размер файла
        /// </summary>
        /// <param name="filePath">Путь к файлу</param>
        /// <returns>Размер файла в байтах</returns>
        Task<long> GetFileSizeAsync(string filePath);

        /// <summary>
        /// Получить список файлов в контейнере
        /// </summary>
        /// <param name="containerName">Имя контейнера/папки</param>
        /// <param name="prefix">Префикс для фильтрации файлов</param>
        /// <returns>Список путей к файлам</returns>
        Task<IEnumerable<string>> ListFilesAsync(string containerName, string? prefix = null);

        /// <summary>
        /// Копировать файл
        /// </summary>
        /// <param name="sourcePath">Исходный путь</param>
        /// <param name="destinationPath">Путь назначения</param>
        /// <returns>True если копирование успешно</returns>
        Task<bool> CopyFileAsync(string sourcePath, string destinationPath);

        /// <summary>
        /// Переместить файл
        /// </summary>
        /// <param name="sourcePath">Исходный путь</param>
        /// <param name="destinationPath">Путь назначения</param>
        /// <returns>True если перемещение успешно</returns>
        Task<bool> MoveFileAsync(string sourcePath, string destinationPath);
    }
}
