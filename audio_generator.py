import torch
import torchaudio
from bark import generate_audio, preload_models


# Convert selected lore entry to audio using Bark, with options for smaller models
def convert_to_audio_bark(text, output_file, model_type="large"):
    # Ensure GPU is available and use it
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on device: {device}")

    # Preload Bark models
    if model_type == "small":
        print("Loading smaller, faster model...")
        preload_models(model_type="small")  # Load smaller model if available
    else:
        print("Loading larger, high-quality model...")
        preload_models(model_type="large")  # Load default large model

    # Generate audio using Bark on the specified device
    audio_array = generate_audio(text, device=device)  # Specify GPU usage in generation

    # Save the audio file
    audio_file = f"{output_file}.wav"
    torchaudio.save(audio_file, audio_array, 24000)  # Assuming 24kHz sampling rate
    print(f"Audio saved as {audio_file}")
