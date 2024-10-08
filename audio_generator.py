import torch
import torchaudio
from bark import generate_audio, preload_models


# Convert selected lore entry to audio using Bark, explicitly running on GPU
def convert_to_audio_bark(text, output_file):
    # Ensure GPU is available and use it
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on device: {device}")

    # Load Bark models, preload to GPU if available
    preload_models()

    # Generate audio using Bark on the GPU
    audio_array = generate_audio(text, device=device)  # Specify GPU usage in generation

    # Save the audio file
    audio_file = f"{output_file}.wav"
    torchaudio.save(audio_file, audio_array, 24000)  # Assuming 24kHz sampling rate
    print(f"Audio saved as {audio_file}")
