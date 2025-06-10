import numpy as np
from scipy.io import wavfile
import os
from datetime import datetime
import hashlib

class DigitalRequiem:
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 180  # 3 minutes
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_tone(self, frequency, duration, amplitude=1.0, phase=0):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return amplitude * np.sin(2 * np.pi * frequency * t + phase)
    
    def generate_noise_burst(self, duration, amplitude=1.0):
        samples = int(self.sample_rate * duration)
        return amplitude * np.random.uniform(-1, 1, samples)
    
    def apply_envelope(self, signal, attack=0.1, decay=0.2, sustain=0.7, release=0.5):
        total_samples = len(signal)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        envelope = np.ones(total_samples)
        
        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        # Decay
        envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain, decay_samples)
        # Release
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        return signal * envelope
    
    def create_destruction_phase(self):
        """Represents the moment of database destruction"""
        duration = 20
        signal = self.generate_noise_burst(duration, 0.8)
        
        # Add glitch effects
        for i in range(10):
            start = np.random.randint(0, int(self.sample_rate * duration - self.sample_rate))
            length = np.random.randint(100, 10000)
            signal[start:start+length] = 0
            
        return self.apply_envelope(signal, attack=0.01, decay=0.1, sustain=0.8, release=5.0)
    
    def create_reflection_phase(self):
        """Represents the period of reflection and responsibility"""
        duration = 60
        base_freq = 220  # A3
        signal = np.zeros(int(self.sample_rate * duration))
        
        # Slowly building harmonics
        for i, harmonic in enumerate([1, 1.5, 2, 2.5, 3, 4], 1):
            delay = i * 5
            freq = base_freq * harmonic
            tone = self.generate_tone(freq, duration, amplitude=0.2)
            tone = self.apply_envelope(tone, attack=2.0, decay=4.0, sustain=0.3, release=10.0)
            signal += np.roll(tone, int(delay * self.sample_rate))
            
        return signal
    
    def create_resolution_phase(self):
        """Represents the understanding and path forward"""
        duration = 100
        signal = np.zeros(int(self.sample_rate * duration))
        
        # Create a chord progression
        frequencies = [220, 277.18, 329.63, 440]  # A3, C#4, E4, A4
        for freq in frequencies:
            tone = self.generate_tone(freq, duration, amplitude=0.15)
            tone = self.apply_envelope(tone, attack=5.0, decay=10.0, sustain=0.4, release=20.0)
            signal += tone
            
        return signal
    
    def compose(self):
        """Compose the full piece"""
        # Create phases
        destruction = self.create_destruction_phase()
        reflection = self.create_reflection_phase()
        resolution = self.create_resolution_phase()
        
        # Combine phases
        full_signal = np.concatenate([destruction, reflection, resolution])
        
        # Normalize
        full_signal = full_signal / np.max(np.abs(full_signal))
        
        # Convert to 16-bit PCM
        audio_data = (full_signal * 32767).astype(np.int16)
        
        # Create output directory if it doesn't exist
        os.makedirs('justice/art/output', exist_ok=True)
        
        # Generate unique filename based on timestamp
        filename = f'justice/art/output/digital_requiem_{self.timestamp}.wav'
        
        # Save the audio file
        wavfile.write(filename, self.sample_rate, audio_data)
        
        # Create a hash of the file
        with open(filename, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            
        # Save the hash
        hash_file = f'{filename}.sha256'
        with open(hash_file, 'w') as f:
            f.write(file_hash)
            
        return filename, file_hash

if __name__ == "__main__":
    requiem = DigitalRequiem()
    filename, file_hash = requiem.compose()
    print(f"Created: {filename}")
    print(f"SHA256: {file_hash}") 