import base64
from openai import OpenAI, AsyncOpenAI # Import AsyncOpenAI
import time
from pydantic import BaseModel, Field
import asyncio
import json

# Define a Pydantic model for the structured output
class ImageAnalysisResult(BaseModel):
    image_title: str = Field(..., description="A concise title for the image content.")
    description: str = Field(..., description="A detailed description of what is depicted in the image.")

# Set up the client for asynchronous operations
client = AsyncOpenAI( # Use AsyncOpenAI here
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

# Modify the prompt to ask for structured JSON output
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

# --- Async Function for a Single API Request ---
async def analyze_image_async(client, base64_image, prompt_content, request_id):
    print(f"Sending request {request_id}...")
    try:
        # The 'create' method on AsyncOpenAI's chat.completions object is awaitable
        response = await client.chat.completions.create(
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
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        raw_response_content = response.choices[0].message.content
        print(f"Received response for request {request_id}. Parsing...")
        analysis_result = ImageAnalysisResult.model_validate_json(raw_response_content)
        return {"id": request_id, "status": "success", "result": analysis_result}
    except Exception as e:
        print(f"Error processing request {request_id}: {e}")
        return {"id": request_id, "status": "error", "message": str(e)}

# --- Main Async Batch Processing Function ---
async def main():
    num_requests = 15
    print(f"\n--- Starting {num_requests} Concurrent API Requests ---")
    start_batch_api_request_time = time.time()

    tasks = []
    for i in range(num_requests):
        task = analyze_image_async(client, base64_image, prompt_content, i + 1)
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    end_batch_api_request_time = time.time()
    batch_api_request_duration = end_batch_api_request_time - start_batch_api_request_time
    print(f"Batch API requests took: {batch_api_request_duration:.2f} seconds for {num_requests} requests")

    print("\n--- Batch Processing Results ---")
    for result in results:
        if result["status"] == "success":
            print(f"Request {result['id']}: SUCCESS")
            print(f"  Title: {result['result'].image_title}")
            # print(f"  Description: {result['result'].description[:50]}...") # Print a truncated description
        else:
            print(f"Request {result['id']}: ERROR - {result['message']}")

    # --- Total Time ---
    total_duration = image_processing_duration + batch_api_request_duration
    print(f"\nTotal execution time (including image processing and batch API): {total_duration:.2f} seconds")

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
