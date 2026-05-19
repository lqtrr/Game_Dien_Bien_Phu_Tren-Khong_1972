import wave
import struct
import math
import os

sample_rate = 44100

def generate_tone(filename, frequency_list, duration, volume=0.3):
    filepath = os.path.join("assets", filename)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for freq in frequency_list:
            n_samples = int(sample_rate * (duration / len(frequency_list)))
            for i in range(n_samples):
                t = float(i) / sample_rate
                # Add some fade out to avoid clicks
                fade = 1.0
                if i > n_samples - 500:
                    fade = (n_samples - i) / 500.0
                if i < 500:
                    fade = i / 500.0
                
                # Use square wave for more "retro" game feel
                val = 1 if math.sin(2.0 * math.pi * freq * t) > 0 else -1
                value = int(volume * fade * 32767.0 * val)
                
                data = struct.pack('<h', value)
                wav_file.writeframesraw(data)

os.makedirs("assets", exist_ok=True)

# Coin sound: High pitch, short "bling"
generate_tone('coin.wav', [988, 1318], 0.15)

# Game over sound: Descending pitch
generate_tone('game_over.wav', [300, 250, 200, 150], 0.8)

# Win sound: Ascending triumphant
generate_tone('win.wav', [440, 554, 659, 880], 0.8)

print("Generated audio files in assets folder.")
