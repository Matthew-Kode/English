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
    HF_TOKEN=$HF_TOKEN python3 -c "import os, tarfile; from huggingface_hub import hf_hub_download; \
    repo='nvidia/personaplex-7b-v1'; t=os.environ.get('HF_TOKEN'); \
    print(f'🚀 Downloading from {repo}...'); \
    hf_hub_download(repo, 'model.safetensors', token=t); \
    hf_hub_download(repo, 'tokenizer-e351c8d8-checkpoint125.safetensors', token=t); \
    hf_hub_download(repo, 'tokenizer_spm_32k_3.model', token=t); \
    hf_hub_download(repo, 'config.json', token=t); \
    v=hf_hub_download(repo, 'voices.tgz', token=t); tarfile.open(v, 'r:gz').extractall(path=os.path.dirname(v)); \
    d=hf_hub_download(repo, 'dist.tgz', token=t); tarfile.open(d, 'r:gz').extractall(path=os.path.dirname(d)); \
    print('✅ Model files downloaded and extracted!')" && \
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
