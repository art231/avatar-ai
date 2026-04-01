import wave
import struct
import math

# Параметры аудио
sample_rate = 16000
duration = 2.0  # секунды
frequency = 440.0  # Гц (нота Ля)
amplitude = 32767 * 0.3  # 30% от максимальной амплитуды

# Создаем WAV файл
with wave.open('test_voice.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # моно
    wav_file.setsampwidth(2)  # 16 бит
    wav_file.setframerate(sample_rate)
    
    # Генерируем синусоидальную волну
    for i in range(int(sample_rate * duration)):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        wav_file.writeframes(struct.pack('<h', value))

print('Test voice file created: test_voice.wav')
print(f'Sample rate: {sample_rate} Hz')
print(f'Duration: {duration} seconds')
print(f'Frequency: {frequency} Hz')