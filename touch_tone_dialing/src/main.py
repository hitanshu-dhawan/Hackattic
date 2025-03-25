import os
import requests
import numpy as np
from scipy.io import wavfile
import tempfile
import json
import io

# Define DTMF frequencies according to standard
# DTMF uses a grid of frequencies:
# Low frequencies: 697, 770, 852, 941 Hz (rows)
# High frequencies: 1209, 1336, 1477, 1633 Hz (columns)
DTMF_FREQUENCIES = {
    (697, 1209): '1', (697, 1336): '2', (697, 1477): '3', (697, 1633): 'A',
    (770, 1209): '4', (770, 1336): '5', (770, 1477): '6', (770, 1633): 'B',
    (852, 1209): '7', (852, 1336): '8', (852, 1477): '9', (852, 1633): 'C',
    (941, 1209): '*', (941, 1336): '0', (941, 1477): '#', (941, 1633): 'D'
}

# All possible DTMF frequencies we need to check
ROW_FREQUENCIES = [697, 770, 852, 941]
COL_FREQUENCIES = [1209, 1336, 1477, 1633]

def download_wav_file(url):
    """Download the WAV file from the given URL"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download WAV file: {response.status_code}")
    return io.BytesIO(response.content)

def goertzel_algorithm(samples, sample_rate, target_freq):
    """
    Custom implementation of the Goertzel algorithm.
    Detects the presence of a specific frequency in a signal.
    
    Parameters:
    - samples: audio data
    - sample_rate: sampling rate in Hz
    - target_freq: frequency to detect in Hz
    
    Returns:
    - Power of target frequency in the signal
    """
    # Number of samples
    N = len(samples)
    
    # Normalized frequency
    k = int(0.5 + (N * target_freq) / sample_rate)
    omega = 2 * np.pi * k / N
    
    # Goertzel coefficients
    coeff = 2 * np.cos(omega)
    
    # Initialization
    s0, s1, s2 = 0, 0, 0
    
    # Process samples
    for i in range(N):
        s0 = samples[i] + coeff * s1 - s2
        s2 = s1
        s1 = s0
    
    # Calculate magnitude
    real = s1 - s2 * np.cos(omega)
    imag = s2 * np.sin(omega)
    
    # Return power
    return real**2 + imag**2

def detect_dtmf_tones(audio_data, sample_rate):
    """
    Detect DTMF tones in the audio data.
    Uses our custom Goertzel algorithm implementation.
    """
    # Parameters for detection
    frame_size = int(0.050 * sample_rate)  # 50ms frames
    hop_size = int(0.010 * sample_rate)    # 10ms hop
    threshold = 5.0  # Power threshold for tone detection - may need adjustment
    
    sequence = []
    current_tone = None
    silent_frames = 0
    required_silent_frames = 3  # Number of silent frames needed to consider a tone ended
    
    # Process the audio in frames
    for i in range(0, len(audio_data) - frame_size, hop_size):
        frame = audio_data[i:i + frame_size]
        
        # Detect frequencies in this frame
        row_freq = None
        col_freq = None
        max_row_power = threshold
        max_col_power = threshold
        
        # Check row frequencies
        for freq in ROW_FREQUENCIES:
            power = goertzel_algorithm(frame, sample_rate, freq)
            if power > max_row_power:
                max_row_power = power
                row_freq = freq
        
        # Check column frequencies
        for freq in COL_FREQUENCIES:
            power = goertzel_algorithm(frame, sample_rate, freq)
            if power > max_col_power:
                max_col_power = power
                col_freq = freq
        
        # If both frequencies detected, we have a tone
        if row_freq and col_freq:
            tone = DTMF_FREQUENCIES.get((row_freq, col_freq))
            if tone:
                if current_tone != tone:
                    current_tone = tone
                    silent_frames = 0
                    sequence.append(tone)
        else:
            # Silence detected
            if current_tone:
                silent_frames += 1
                if silent_frames >= required_silent_frames:
                    current_tone = None
    
    return ''.join(sequence)

def clean_sequence(raw_sequence):
    """
    Clean up the detected sequence by removing duplicates caused by continuous detection
    """
    result = ""
    prev_char = None
    
    for char in raw_sequence:
        if char != prev_char:
            result += char
            prev_char = char
    
    return result

def solve_challenge(access_token):
    """Solve the touch tone dialing challenge"""
    # Get problem data
    problem_url = f"https://hackattic.com/challenges/touch_tone_dialing/problem?access_token={access_token}"
    response = requests.get(problem_url)
    if response.status_code != 200:
        raise Exception(f"Failed to get problem: {response.status_code}")
    
    problem_data = response.json()
    wav_url = problem_data['wav_url']
    
    # Download and process the WAV file
    wav_buffer = download_wav_file(wav_url)
    sample_rate, audio_data = wavfile.read(wav_buffer)
    
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Normalize audio data
    audio_data = audio_data.astype(float)  # Ensure float for division
    if np.max(np.abs(audio_data)) > 0:  # Avoid division by zero
        audio_data = audio_data / np.max(np.abs(audio_data))
    
    # Detect DTMF tones
    raw_sequence = detect_dtmf_tones(audio_data, sample_rate)
    sequence = clean_sequence(raw_sequence)
    
    print(f"Detected sequence: {sequence}")
    
    # Submit solution
    solution = {"sequence": sequence}
    solve_url = f"https://hackattic.com/challenges/touch_tone_dialing/solve?access_token={access_token}"
    solution_response = requests.post(solve_url, json=solution)
    
    return solution_response.json()

if __name__ == "__main__":
    access_token = os.getenv("ACCESS_TOKEN")
    result = solve_challenge(access_token)
    print(f"Result: {result}")
