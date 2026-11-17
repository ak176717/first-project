import wave
import math
import struct
import random

SAMPLE_RATE = 44100
DURATION = 60.0
NUM_SAMPLES = int(SAMPLE_RATE * DURATION)

# Notes in Raag Bhupali / Yaman (in Hz)
C3 = 130.81
G3 = 196.00
C4 = 261.63
D4 = 293.66
E4 = 329.63
G4 = 392.00
A4 = 440.00
C5 = 523.25
D5 = 587.33
E5 = 659.25
G5 = 783.99

# Flute Melody Sequence: (start_sec, duration_sec, freq)
flute_notes = [
    # Scene 1: The Divine Meeting (0 - 10s)
    (1.0, 2.2, C4), (3.3, 1.8, D4), (5.2, 2.5, E4), (7.8, 2.0, G4),
    # Scene 2: The Ring of Trust (10 - 20s)
    (10.5, 2.0, E4), (12.6, 2.2, G4), (14.9, 2.5, A4), (17.5, 2.2, G4),
    # Scene 3: The Ocean Leap (20 - 30s)
    (20.3, 1.8, G4), (22.2, 2.0, A4), (24.3, 2.5, C5), (26.9, 1.8, D5), (28.8, 1.2, C5),
    # Scene 4: The Sanjeevani Mountain (30 - 40s)
    (30.4, 2.0, C5), (32.5, 2.2, D5), (34.8, 2.5, E5), (37.4, 2.4, D5),
    # Scene 5: The Divine Embrace (40 - 50s)
    (40.5, 2.5, E5), (43.1, 2.2, C5), (45.4, 2.4, A4), (47.9, 2.0, G4),
    # Scene 6: Enshrined in the Heart (50 - 60s)
    (50.3, 2.5, G4), (52.9, 2.2, E4), (55.2, 2.5, D4), (57.8, 2.0, C4)
]

# Bell strike moments (seconds)
bell_times = [0.1, 10.0, 20.0, 30.0, 40.0, 50.0, 57.5]

print("Synthesizing 60-second devotional soundtrack...")

# Initialize left and right audio buffers
left_channel = [0.0] * NUM_SAMPLES
right_channel = [0.0] * NUM_SAMPLES

# 1. Tanpura drone (continuous Sa-Pa-Sa-Sa plucking cycles)
tanpura_strings = [
    (G3, 0.0),    # Pa
    (C4, 0.75),   # Sa
    (C4, 1.50),   # Sa
    (C3, 2.25)    # Kharaj Sa
]
cycle_len = 3.0
num_cycles = int(DURATION / cycle_len) + 1

for cycle in range(num_cycles):
    cycle_start = cycle * cycle_len
    for freq, offset in tanpura_strings:
        pluck_time = cycle_start + offset
        if pluck_time >= DURATION:
            continue
        start_idx = int(pluck_time * SAMPLE_RATE)
        # Ring for 4 seconds with rich harmonics
        ring_samples = int(SAMPLE_RATE * 4.0)
        end_idx = min(NUM_SAMPLES, start_idx + ring_samples)
        
        for i in range(start_idx, end_idx):
            t = (i - start_idx) / SAMPLE_RATE
            env = math.exp(-t * 0.85) * (1.0 - math.exp(-t * 30.0))
            
            # Sum 7 harmonics with subtle jawari buzz
            harmonics = [1.0, 0.55, 0.35, 0.22, 0.15, 0.08, 0.04]
            sample_val = 0.0
            for h_idx, amp in enumerate(harmonics, start=1):
                h_freq = freq * h_idx
                # Subtle pitch drift
                phase = 2 * math.pi * h_freq * t + 0.02 * math.sin(6 * math.pi * t)
                sample_val += amp * math.sin(phase)
            
            # Slight stereo panning for each string
            pan = 0.45 + (freq % 10) * 0.02
            val = sample_val * env * 0.08
            left_channel[i] += val * (1.0 - pan)
            right_channel[i] += val * pan

# 2. Deep Sub-bass / Om meditation drone
for i in range(NUM_SAMPLES):
    t = i / SAMPLE_RATE
    # 65.4 Hz (C2) with slow breathing modulation
    breath = 0.5 + 0.5 * math.sin(2 * math.pi * 0.12 * t)
    sub = math.sin(2 * math.pi * 65.4 * t) * 0.04 * breath
    left_channel[i] += sub
    right_channel[i] += sub

# 3. Temple Bells (Tibetan Singing Bowl / Ghanti)
for bt in bell_times:
    b_idx = int(bt * SAMPLE_RATE)
    bell_len = int(SAMPLE_RATE * 5.5)
    max_idx = min(NUM_SAMPLES, b_idx + bell_len)
    
    # Inharmonic bell frequencies (Tibetan singing bowl spectrum)
    partials = [
        (880.0, 1.0, 0.9),
        (880.0 * 2.76, 0.5, 1.4),
        (880.0 * 5.40, 0.25, 2.2),
        (880.0 * 0.5, 0.4, 0.6)  # warm sub-fundamental
    ]
    
    for i in range(b_idx, max_idx):
        t = (i - b_idx) / SAMPLE_RATE
        strike_env = (1.0 - math.exp(-t * 80.0))
        val = 0.0
        for p_freq, p_amp, decay_rate in partials:
            env = math.exp(-t * decay_rate) * strike_env
            shimmer = 1.0 + 0.08 * math.sin(2 * math.pi * 4.5 * t)
            val += p_amp * math.sin(2 * math.pi * p_freq * t) * env * shimmer
            
        b_val = val * 0.12
        left_channel[i] += b_val * 0.55
        right_channel[i] += b_val * 0.45

# 4. Sacred Bansuri (Bamboo Flute)
for start_t, dur_t, f0 in flute_notes:
    s_idx = int(start_t * SAMPLE_RATE)
    d_samples = int(dur_t * SAMPLE_RATE)
    e_idx = min(NUM_SAMPLES, s_idx + d_samples)
    
    for i in range(s_idx, e_idx):
        t = (i - s_idx) / SAMPLE_RATE
        # ADSR Envelope for flute (gentle attack, soft release)
        attack_t = 0.28
        release_t = 0.35
        if t < attack_t:
            env = math.sin((t / attack_t) * (math.pi / 2))
        elif t > (dur_t - release_t):
            rel_progress = (t - (dur_t - release_t)) / release_t
            env = math.cos(rel_progress * (math.pi / 2))
        else:
            env = 1.0
            
        # Flute vibrato (5 Hz, begins after 0.4s)
        vib_intensity = min(1.0, max(0.0, (t - 0.4) / 0.5)) * 0.015
        vib = 1.0 + vib_intensity * math.sin(2 * math.pi * 5.2 * t)
        inst_freq = f0 * vib
        
        # Bamboo flute overtones (rich odd & even harmonics)
        flute_sig = (
            1.0 * math.sin(2 * math.pi * inst_freq * t) +
            0.45 * math.sin(2 * math.pi * (2 * inst_freq) * t) +
            0.20 * math.sin(2 * math.pi * (3 * inst_freq) * t) +
            0.08 * math.sin(2 * math.pi * (4 * inst_freq) * t)
        )
        
        # Subtle breath wind noise
        noise = (random.random() * 2.0 - 1.0) * 0.04
        sample_flute = (flute_sig + noise) * env * 0.14
        
        left_channel[i] += sample_flute * 0.52
        right_channel[i] += sample_flute * 0.48

# 5. Master Fade in (first 1.5s) and Fade out (last 2.0s)
for i in range(NUM_SAMPLES):
    t = i / SAMPLE_RATE
    master_gain = 1.0
    if t < 1.5:
        master_gain = t / 1.5
    elif t > (DURATION - 2.0):
        master_gain = (DURATION - t) / 2.0
    left_channel[i] *= master_gain
    right_channel[i] *= master_gain

# 6. Normalize and Export WAV
max_amp = max(max(map(abs, left_channel)), max(map(abs, right_channel)))
print(f"Max audio amplitude before normalization: {max_amp:.4f}")
gain = 0.88 / (max_amp if max_amp > 0 else 1.0)

wav_path = "/home/agent/workspace/assets/soundtrack_60s.wav"
with wave.open(wav_path, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2) # 16-bit
    wf.setframerate(SAMPLE_RATE)
    
    frames = bytearray()
    for i in range(NUM_SAMPLES):
        l_val = int(max(-32767, min(32767, left_channel[i] * gain * 32767)))
        r_val = int(max(-32767, min(32767, right_channel[i] * gain * 32767)))
        frames.extend(struct.pack("<hh", l_val, r_val))
    
    wf.writeframes(frames)

print(f"Soundtrack exported successfully to {wav_path} (60.00 seconds)")
