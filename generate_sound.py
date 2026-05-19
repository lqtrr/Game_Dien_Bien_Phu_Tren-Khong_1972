import wave
import struct
import math
import os

def generate_laser_sound(filename):
    sample_rate = 44100
    duration = 0.15 # 0.15 seconds
    num_samples = int(sample_rate * duration)
    
    # frequencies: start high, drop low
    start_freq = 1800.0
    end_freq = 150.0
    
    # ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    wavef = wave.open(filename, 'w')
    wavef.setnchannels(1) # mono
    wavef.setsampwidth(2) # 16-bit
    wavef.setframerate(sample_rate)
    
    for i in range(num_samples):
        t = float(i) / sample_rate
        
        # Pitch sweep: drop frequency rapidly
        current_freq = start_freq - ((start_freq - end_freq) * (t / duration) ** 0.5)
        
        # Square wave for retro laser sound
        phase = (current_freq * t) % 1.0
        value = 1.0 if phase < 0.5 else -1.0
        
        # Add some noise for texture
        # value += (math.sin(i * 100) * 0.2)
        
        # Envelope: fast attack, linear decay
        envelope = max(0.0, 1.0 - (t / duration))
        
        audio_sample = int(value * envelope * 32767.0 * 0.2) # 0.2 volume
        data = struct.pack('<h', audio_sample)
        wavef.writeframesraw(data)
        
    wavef.close()

generate_laser_sound('c:/Users/ADMIN/Documents/CNTT 18-11/Công nghệ trí tuệ nhân tạo/Maze_Pursuit/assets/shoot_sound.wav')
