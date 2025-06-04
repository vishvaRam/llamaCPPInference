FROM ghcr.io/ggml-org/llama.cpp:server AS builder

# Copy the model into the image
COPY ./models/Model-7.6B-Q4_0.gguf /models/Model-7.6B-Q4_0.gguf
COPY ./models/mmproj-model-f16.gguf /models/mmproj-model-f16.gguf

# Use the original image as the final stage
FROM ghcr.io/ggml-org/llama.cpp:server

# Copy the model from the builder stage
COPY --from=builder /models/Model-7.6B-Q4_0.gguf /models/Model-7.6B-Q4_0.gguf
COPY --from=builder /models/mmproj-model-f16.gguf /models/mmproj-model-f16.gguf