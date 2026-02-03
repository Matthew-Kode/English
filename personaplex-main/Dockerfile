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
RUN pip install --no-cache-dir huggingface_hub && \
    HF_TOKEN=$HF_TOKEN python3 -c "from huggingface_hub import hf_hub_download; import tarfile, os, sys; \
    repo = 'nvidia/personaplex-7b-v1'; token = os.environ.get('HF_TOKEN'); \
    try: \
        print(f'🚀 Starting download from {repo} (Token provided: {bool(token)})'); \
        files = ['model.safetensors', 'tokenizer-e351c8d8-checkpoint125.safetensors', 'tokenizer_spm_32k_3.model', 'config.json']; \
        for f in files: print(f'  Downloading {f}...'); hf_hub_download(repo, f, token=token); \
        print('  Downloading voices.tgz...'); v_path = hf_hub_download(repo, 'voices.tgz', token=token); \
        with tarfile.open(v_path, 'r:gz') as tar: tar.extractall(path=os.path.dirname(v_path)); \
        print('  Downloading dist.tgz...'); d_path = hf_hub_download(repo, 'dist.tgz', token=token); \
        with tarfile.open(d_path, 'r:gz') as tar: tar.extractall(path=os.path.dirname(d_path)); \
        print('✅ All model files downloaded and extracted!'); \
    except Exception as e: \
        print(f'❌ DOWNLOAD FAILED: {e}'); sys.exit(1)" && \
    echo '✅ Model cached at /root/.cache/huggingface/hub'

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
