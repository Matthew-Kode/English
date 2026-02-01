### Agent Guidelines (`GEMINI.md`)

- Agent only proceeds to code when user approves
```markdown
# 🤖 Project Context: "Visa Denied" (PersonaPlex Combat English)

## 📌 Project Summary
A high-pressure English learning simulation app for Korean users.
**Core Philosophy:** "Combat Training" > "Polite Tutoring."
**Key Tech:** NVIDIA PersonaPlex (Full Duplex AI) to allow natural interruption and fast turn-taking (<350ms).

## 🏗️ Technical Architecture (The "Receptionist Pattern")

### 1. The Mobile Client (Flutter)
* **Role:** The "Face." Handles Audio I/O and Scenario Logic.
* **Critical Logic:**
    * **Scenario Masking:** Never show a "Loading" spinner. Show a 30s "Mission Briefing" while the GPU boots in the background.
    * **Audio:** Uses `flutter_sound` or `audio_session`. MUST enable Hardware Echo Cancellation (AEC).
    * **Protocol:** WebSockets (Raw PCM or Opus) directly to the GPU Worker (after Gateway handoff).
    * **Security:** **NO API KEYS.** Client authenticates with Gateway only.

### 2. The Gateway (Python FastAPI)
* **Role:** The "Bouncer." Cheap CPU Server (AWS t3.micro).
* **Responsibilities:**
    * **Boot:** calls RunPod API to start a fresh Pod on `POST /boot` using **Server-Side Credentials**.
    * **Route:** Returns the WebSocket URL of the active Pod to the App.
    * **Kill:** Runs a Cron Job every 10 mins to kill "Zombie Pods" (>20 mins uptime).

### 3. The GPU Worker (RunPod / Docker)
* **Role:** The "Brain." Ephemeral Container.
* **Hardware:** 1x RTX 4090 per Pod.
* **Software:** `nvidia/personaplex` repo (Moshi architecture).
* **Constraint:** Takes ~25s to cold boot (Load Weights + Warmup).
* **Safety:** Contains a "Suicide Pill" in `server.py` (Self-destruct if 5 mins of silence).

## 🛑 Hard Rules for AI Generation

### 1. Cost Safety First
* **NEVER** suggest leaving GPUs running idle. Always implement the "Three-Layer Kill Switch."
* **Rule:** If writing backend code, always include a `finally` block that triggers pod termination.

### 2. Latency > Complexity
* **Do NOT** suggest standard VAD Gating (Silence -> Stop -> Think).
* **DO** use **Full Duplex** (Continuous Streaming). The model listens *while* speaking.
* **Target:** < 350ms Round Trip.

### 3. "Generic Pod" Principle
* **Do NOT** hardcode personas into the Docker image.
* **DO** inject Personas dynamically via URL parameters (`?text_prompt=...&voice_prompt=...`) when the WebSocket connects.
* **Database:** Scenarios (Tom, Cindy) live in the App/Gateway JSON, not on the GPU.

## 🛠️ Tech Stack Cheatsheet
* **Frontend:** Flutter, Dart, Riverpod.
* **Backend:** Python 3.10, FastAPI, Uvicorn.
* **GPU Infra:** RunPod API, Docker, NVIDIA PyTorch Base.
* **Model:** PersonaPlex (7B, 4-bit quantized).

## 📝 Common Tasks & Commands
* **Boot Pod:** `runpod.create_pod(image="my-personaplex-v1", gpu_type="RTX4090")`
* **Kill Pod:** `runpod.terminate_pod(pod_id)`
* **Connect WS:** `WebSocketChannel.connect(Uri.parse('wss://.../api/chat'))`

```