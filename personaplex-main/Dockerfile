# Base Image (PyTorch 2.4 + CUDA 12.4)
FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime

# 1. System Dependencies
RUN apt-get update && apt-get install -y \
    libopus-dev \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# 2. Set Up Working Directory
WORKDIR /app

# 3. Copy Code (We copy everything so we can install)
COPY . /app

# 4. Install Python Dependencies
# (Assumes we are at the root of 'English' repo where 'personaplex-main' is a subfolder)
RUN pip install --no-cache-dir -e personaplex-main/moshi
RUN pip install --no-cache-dir huggingface_hub

# 5. Model Weights (BAKED IN)
# We use a Build ARG so you don't hardcode the token in the file
ARG HF_TOKEN

# CRITICAL: Set HF_HOME explicitly so cache is found at runtime
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface

# Download each file the server needs using hf_hub_download (same as server.py)
# This ensures the cache structure matches what the server expects
RUN if [ -n "$HF_TOKEN" ]; then \
    huggingface-cli login --token $HF_TOKEN && \
    python3 -c "from huggingface_hub import hf_hub_download; \
    repo = 'nvidia/personaplex-7b-v1'; \
    print('Downloading model.safetensors...'); hf_hub_download(repo, 'model.safetensors'); \
    print('Downloading tokenizer...'); hf_hub_download(repo, 'tokenizer-e351c8d8-checkpoint125.safetensors'); \
    print('Downloading text tokenizer...'); hf_hub_download(repo, 'tokenizer_spm_32k_3.model'); \
    print('Downloading config...'); hf_hub_download(repo, 'config.json'); \
    print('Downloading voices...'); hf_hub_download(repo, 'voices.tgz'); \
    print('Downloading dist...'); hf_hub_download(repo, 'dist.tgz'); \
    print('✅ All model files downloaded!')" && \
    echo '✅ Model cached at /root/.cache/huggingface/hub'; \
    else \
    echo "⚠️ WARNING: HF_TOKEN not provided. Model weights will NOT be baked in."; \
    fi

# 6. Copy Entrypoint
COPY personaplex-main/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 7. Ports & Start
EXPOSE 8998
ENTRYPOINT ["/app/entrypoint.sh"]
