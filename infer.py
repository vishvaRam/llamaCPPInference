import base64
from openai import OpenAI
import time
from pydantic import BaseModel, Field
import json # Import the json module to potentially load the string if needed

# Define a Pydantic model for the structured output
class ImageAnalysisResult(BaseModel):
    image_title: str = Field(..., description="A concise title for the image content.")
    description: str = Field(..., description="A detailed description of what is depicted in the image.")

# Set up the client
client = OpenAI(
    base_url="http://[ip]:8000/v1",
    api_key="not-needed"
)

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image file
image_path = "img.jpg" # Make sure 'img.jpg' exists in the same directory

# --- Start Image Processing Timer ---
start_image_processing_time = time.time()

# Encode image
base64_image = encode_image(image_path)
print("Image Processed...")

# --- End Image Processing Timer ---
end_image_processing_time = time.time()
image_processing_duration = end_image_processing_time - start_image_processing_time
print(f"Image processing took: {image_processing_duration:.2f} seconds")

# --- Start API Request Timer ---
start_api_request_time = time.time()

# Modify the prompt to ask for structured JSON output
# This is crucial for the model to generate Pydantic-compatible output
prompt_content = """
Analyze the provided image and provide a JSON output with two fields:
1. `image_title`: A concise title summarizing the image.
2. `description`: A detailed description of what is depicted in the image.

Example output:
{
  "image_title": "Cityscape at Sunset",
  "description": "An aerial view of a vibrant city during sunset, with tall buildings illuminated against an orange and purple sky. Cars can be seen on the bustling streets below."
}
"""

# Send request
response = client.chat.completions.create(
    model="not-used-here", # Replace with your actual model name if applicable
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_content},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ],
    max_tokens=1024,
    temperature=0.01,
    response_format={ "type": "json_object" } # Request JSON object output
)

# --- End API Request Timer ---
end_api_request_time = time.time()
api_request_duration = end_api_request_time - start_api_request_time
print(f"API request took: {api_request_duration:.2f} seconds")

# Output result
print("\n--- Model Response (Raw) ---")
raw_response_content = response.choices[0].message.content
print(raw_response_content)

# Parse the response content into the Pydantic model
try:
    # model_validate_json expects a JSON string.
    # The response_format parameter should ensure raw_response_content is already a valid JSON string.
    analysis_result = ImageAnalysisResult.model_validate_json(raw_response_content)
    print("\n--- Structured Model Response ---")
    print(f"Image Title: {analysis_result.image_title}")
    print(f"Description: {analysis_result.description}")

except Exception as e:
    print(f"\nError parsing model response with Pydantic: {e}")
    print("Please ensure the model generates valid JSON according to the schema.")


# --- Total Time ---
total_duration = image_processing_duration + api_request_duration
print(f"\nTotal execution time: {total_duration:.2f} seconds")
