# Base Image (PyTorch 2.4 + CUDA 12.4)
FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime

# 1. System Dependencies
RUN apt-get update && apt-get install -y \
    libopus-dev \
    git \
    git-lfs \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set Environment Variables for Cache
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface

# 4. DOWNLOAD MODEL WEIGHTS (The "Heavy" Layer)
# We do this BEFORE 'COPY . /app'.
ARG HF_TOKEN
RUN pip install huggingface_hub && \
    if [ -n "$HF_TOKEN" ]; then \
    huggingface-cli login --token $HF_TOKEN && \
    python3 -c "from huggingface_hub import hf_hub_download; \
    repo = 'nvidia/personaplex-7b-v1'; \
    print('Downloading model.safetensors...'); hf_hub_download(repo, 'model.safetensors'); \
    print('Downloading tokenizer...'); hf_hub_download(repo, 'tokenizer-e351c8d8-checkpoint125.safetensors'); \
    print('Downloading text tokenizer...'); hf_hub_download(repo, 'tokenizer_spm_32k_3.model'); \
    print('Downloading config...'); hf_hub_download(repo, 'config.json'); \
    print('Downloading voices...'); voices_path = hf_hub_download(repo, 'voices.tgz'); \
    print('Extracting voices...'); \
    import tarfile, os; \
    with tarfile.open(voices_path, 'r:gz') as tar: tar.extractall(path=os.path.dirname(voices_path)); \
    print('Downloading dist...'); dist_path = hf_hub_download(repo, 'dist.tgz'); \
    print('Extracting dist...'); \
    with tarfile.open(dist_path, 'r:gz') as tar: tar.extractall(path=os.path.dirname(dist_path)); \
    print('✅ All model files downloaded and extracted!')" && \
    echo '✅ Model cached at /root/.cache/huggingface/hub'; \
    else \
    echo "⚠️ WARNING: HF_TOKEN not provided. Model weights will NOT be baked in."; \
    fi

# 5. NOW Copy Your Code (The "Light" Layer)
WORKDIR /app
COPY . /app

# 6. Install Local Python Dependencies
# We do this after COPY because it needs the 'personaplex-main' folder to exist.
RUN pip install --no-cache-dir -e personaplex-main/moshi

# 6. Copy Entrypoint
COPY personaplex-main/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 7. Ports & Start
EXPOSE 8998
ENTRYPOINT ["/app/entrypoint.sh"]
