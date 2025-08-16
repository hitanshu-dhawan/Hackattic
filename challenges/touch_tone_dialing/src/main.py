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
    Improved Goertzel algorithm implementation.
    Detects the presence of a specific frequency in a signal.
    
    Parameters:
    - samples: audio data
    - sample_rate: sampling rate in Hz
    - target_freq: frequency to detect in Hz
    
    Returns:
    - Magnitude of target frequency in the signal
    """
    # Number of samples
    N = len(samples)
    
    # Normalized frequency - more precise calculation
    k = (N * target_freq) / sample_rate
    omega = 2 * np.pi * k / N
    
    # Goertzel coefficients
    coeff = 2 * np.cos(omega)
    
    # Initialization
    s_prev = 0.0
    s_prev2 = 0.0
    
    # Process samples
    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    
    # Calculate final result using complex exponential
    real_part = s_prev - s_prev2 * np.cos(omega)
    imag_part = s_prev2 * np.sin(omega)
    
    # Return magnitude (not power)
    magnitude = np.sqrt(real_part**2 + imag_part**2)
    return magnitude

def detect_dtmf_tones(audio_data, sample_rate):
    """
    Detect DTMF tones in the audio data.
    Uses improved Goertzel algorithm with better parameters.
    """
    # Parameters for detection - adjusted for better accuracy
    frame_size = int(0.030 * sample_rate)  # 30ms frames (shorter for better resolution)
    hop_size = int(0.010 * sample_rate)    # 10ms hop
    
    sequence = []
    previous_tone = None
    tone_count = 0
    min_tone_duration = 3  # Minimum frames for a valid tone
    silence_count = 0
    min_silence_duration = 2  # Minimum frames of silence between tones
    
    print(f"Processing audio: {len(audio_data)} samples at {sample_rate} Hz")
    print(f"Frame size: {frame_size}, Hop size: {hop_size}")
    
    # Process the audio in frames
    total_frames = (len(audio_data) - frame_size) // hop_size
    for i, start in enumerate(range(0, len(audio_data) - frame_size, hop_size)):
        frame = audio_data[start:start + frame_size]
        
        # Apply window function to reduce spectral leakage
        window = np.hanning(len(frame))
        frame = frame * window
        
        # Calculate magnitudes for all frequencies
        row_magnitudes = {}
        col_magnitudes = {}
        
        for freq in ROW_FREQUENCIES:
            row_magnitudes[freq] = goertzel_algorithm(frame, sample_rate, freq)
        
        for freq in COL_FREQUENCIES:
            col_magnitudes[freq] = goertzel_algorithm(frame, sample_rate, freq)
        
        # Find the strongest frequencies
        max_row_freq = max(row_magnitudes, key=row_magnitudes.get)
        max_col_freq = max(col_magnitudes, key=col_magnitudes.get)
        
        max_row_mag = row_magnitudes[max_row_freq]
        max_col_mag = col_magnitudes[max_col_freq]
        
        # Calculate average magnitude to set dynamic threshold
        avg_row_mag = np.mean(list(row_magnitudes.values()))
        avg_col_mag = np.mean(list(col_magnitudes.values()))
        
        # Dynamic threshold based on signal strength
        row_threshold = avg_row_mag * 2.0  # Row frequency must be 2x average
        col_threshold = avg_col_mag * 2.0  # Column frequency must be 2x average
        
        # Check if we have valid DTMF tone
        if max_row_mag > row_threshold and max_col_mag > col_threshold:
            current_tone = DTMF_FREQUENCIES.get((max_row_freq, max_col_freq))
            
            if current_tone:
                if current_tone == previous_tone:
                    tone_count += 1
                else:
                    # New tone detected
                    if previous_tone and tone_count >= min_tone_duration:
                        sequence.append(previous_tone)
                        print(f"Detected tone: {previous_tone} (duration: {tone_count} frames)")
                    
                    previous_tone = current_tone
                    tone_count = 1
                    silence_count = 0
        else:
            # Silence or noise
            silence_count += 1
            if silence_count >= min_silence_duration and previous_tone and tone_count >= min_tone_duration:
                sequence.append(previous_tone)
                print(f"Detected tone: {previous_tone} (duration: {tone_count} frames)")
                previous_tone = None
                tone_count = 0
        
        # Progress indicator
        if i % 100 == 0:
            progress = (i / total_frames) * 100
            print(f"Processing: {progress:.1f}%", end='\r')
    
    # Handle last tone if still active
    if previous_tone and tone_count >= min_tone_duration:
        sequence.append(previous_tone)
        print(f"Detected tone: {previous_tone} (duration: {tone_count} frames)")
    
    print(f"\nDetected {len(sequence)} tones")
    return ''.join(sequence)

def solve_challenge(access_token):
    """Solve the touch tone dialing challenge"""
    try:
        # Get problem data
        problem_url = f"https://hackattic.com/challenges/touch_tone_dialing/problem?access_token={access_token}"
        print(f"Fetching problem from: {problem_url}")
        response = requests.get(problem_url)
        if response.status_code != 200:
            raise Exception(f"Failed to get problem: {response.status_code}")
        
        problem_data = response.json()
        wav_url = problem_data['wav_url']
        print(f"Downloading WAV file from: {wav_url}")
        
        # Download and process the WAV file
        wav_buffer = download_wav_file(wav_url)
        sample_rate, audio_data = wavfile.read(wav_buffer)
        print(f"Audio loaded: {audio_data.shape}, sample rate: {sample_rate}")
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
            print("Converted stereo to mono")
        
        # Normalize audio data
        audio_data = audio_data.astype(float)
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
            print("Audio normalized")
        
        # Detect DTMF tones
        sequence = detect_dtmf_tones(audio_data, sample_rate)
        
        print(f"Final detected sequence: {sequence}")
        
        if not sequence:
            print("No sequence detected! Trying with different parameters...")
            return {"error": "No sequence detected"}
        
        # Submit solution
        solution = {"sequence": sequence}
        solve_url = f"https://hackattic.com/challenges/touch_tone_dialing/solve?access_token={access_token}" + "&playground=1"
        print(f"Submitting solution: {solution}")
        solution_response = requests.post(solve_url, json=solution)
        
        return solution_response.json()
    
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    access_token = os.getenv("ACCESS_TOKEN")
    result = solve_challenge(access_token)
    print(f"Result: {result}")
