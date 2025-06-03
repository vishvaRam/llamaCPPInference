from huggingface_hub import hf_hub_download
import os

# Define the model details
repo_id = "openbmb/MiniCPM-o-2_6-gguf"

# List of filenames to download
filenames = ["Model-7.6B-Q8_0.gguf", "mmproj-model-f16.gguf"]

# Define the local directory to save the models
# You can change this to your preferred path
local_dir = "./models"

# Create the directory if it doesn't exist
os.makedirs(local_dir, exist_ok=True)

print(f"Attempting to download files from {repo_id}...")

for filename in filenames:
    try:
        # Download the model
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False  # Set to False to ensure a direct copy
        )
        print(f"File '{filename}' downloaded successfully to: {model_path}")
    except Exception as e:
        print(f"An error occurred during download of '{filename}': {e}")

print("\nNext steps:")
print(f"1. Make sure you have llama.cpp compiled and installed.")
print(f"2. You can use these models with llama.cpp's `llava` example for vision inference.")
print(f"   For example, in your terminal, navigate to the llama.cpp directory and run:")
print(f"   ./llava -m {os.path.join(local_dir, 'Model-7.6B-Q8_0.gguf')} --image <your_image_path> -p \"<your_prompt>\"")
print(f"   (Replace <your_image_path> and <your_prompt> with your actual image and prompt)")
