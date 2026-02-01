Here is the **Final, Production-Grade PRD (v3.1)**.

It explicitly incorporates the **Multi-Scenario Architecture**, **Zero-User-API-Key Security Model**, and the **Hybrid Development Strategy** we agreed upon.

---

# Product Requirements Document (PRD)

**Project Name:** "Visa Denied" (Real-Life Combat English)
**Version:** 3.1 (Hybrid Dev & Security Update)
**Status:** **Approved for Engineering**
**Author:** Staff Architect & Product Lead

---

## 1️⃣ Product Overview

### **Problem Statement**

Korean English learners suffer from "Mute English." They score high on reading/writing tests but freeze in real-world, high-pressure situations (Immigration, Ordering Food, Police Stops). Current apps are too polite and turn-based; they fail to simulate the **adrenaline, time pressure, and rudeness** of reality.

### **Target Personas**

1. **The Panic Learner:** Freezes when an Immigration Officer asks "Why are you here?" Needs desensitization.
2. **The High-Performer:** Advanced speaker who wants to test their fluency against hostile, fast-talking natives (e.g., a rushed New York barista).

### **Success Definition**

* **MVP (Alpha):** A user can complete 2 distinct scenarios ("Tom - Immigration" & "Cindy - Subway") with <350ms latency. The 30s "Mission Briefing" successfully masks the GPU boot time 100% of the time.
* **Production:** Support 1,000 concurrent users with a **< $5.00/month** infrastructure cost per active user, maintaining a 40% D30 retention rate.

---

## 2️⃣ Scope Definition

### **MVP Scope (Phase 1)**

* **Core Loop:** Scenario Selection  30s Briefing (GPU Boot)  5-min Combat Call  Pass/Fail Result.
* **Scenarios:**
1. **"Tom" (Immigration Officer):** Suspicious, authoritative, interrupts if you stutter.
2. **"Cindy" (Subway Part-Timer):** Rushed, impatient, asks complex customization questions fast.


* **Architecture:** Flutter App + Python Gateway (The Bouncer) + On-Demand RunPod GPUs.
* **Audio:** Full-Duplex (Always-on mic), Raw PCM/Opus streaming.

### **Features Explicitly Out-of-Scope**

* User Accounts / Login (Device ID only for MVP).
* **User API Keys (Strictly Prohibited).**
* Payment Gateway (Free Beta).
* Avatar Animation (Voice only).

### **Post-MVP / Scale Scope (Phase 2-4)**

* **Phase 2:** Subscription (Stripe/RevenueCat), "Queue" system for peak times.
* **Phase 3:** "Scenario Builder" (JSON-based definition of new characters).
* **Phase 4:** Multiplayer (Spectator Mode).

---

## 3️⃣ Functional Requirements

### **Feature 1: The "Mission Briefing" (Latency Masking)**

* **Feature Name:** Scenario Pre-Loader
* **User Story:** As a user, I need to read the context of the situation so I can prepare my story, unaware that the server is booting up.
* **Functional Behavior:**
1. User taps "Start Simulation: Tom".
2. App displays **"MISSION BRIEFING"** text (Role, Goal, Constraints).
3. A **30-second countdown** begins. "Start" button is disabled.
4. **Background:** App calls Gateway `POST /boot_pod`. Gateway provisions a GPU using **Server-Side Credentials**.
5. **State Change:** When GPU WebSocket is ready (~25s), the "Connecting..." status secretly flips to "Ready."
6. **Action:** When timer hits 0 (or user clicks "I'm Ready"), the call connects instantly.


* **Edge Cases:**
* *GPU Slow Boot (>30s):* Button stays "Connecting..." with a "Tom is finishing a shift..." message.
* *User Quits Early:* App sends `DELETE /pod` to Gateway immediately to save cost.



### **Feature 2: Multi-Persona Injection**

* **Feature Name:** Dynamic Persona Loader
* **User Story:** I want to talk to different people (Tom, Cindy) without downloading a new app.
* **Functional Behavior:**
* The GPU Worker is **generic**. It does not know who it is until the call starts.
* **Handshake:** Flutter sends initial payload: `{ "persona": "tom_v1", "voice_id": "male_deep_04" }`.
* **Server Action:** `server.py` injects the System Prompt and loads the specific Voice Embedding `.pt` file from disk.


* **Edge Cases:**
* *Missing Voice File:* Fallback to default voice, log error.


* **MVP Notes:** Store 5-10 voice files in the Docker image.

### **Feature 3: The "Three-Layer" Kill Switch**

* **Feature Name:** Cost Control Bouncer
* **User Story:** As the business owner, I ensure no GPU runs for more than 5 minutes to prevent bankruptcy.
* **Functional Behavior:**
1. **Layer 1 (Active):** App disconnect  Gateway calls `runpod.terminate_pod()`.
2. **Layer 2 (Passive):** `server.py` has a 5-minute watchdog. No audio packets?  Self-destruct.
3. **Layer 3 (Nuclear):** Gateway Cron Job runs every 10 mins. Kills any pod >20 mins old.



---

## 4️⃣ Non-Functional Requirements

### **Performance**

* **Latency:** End-to-end audio round trip **< 350ms** (Perceived as instant).
* **Boot Time:** < 28 seconds (Must be hidden by the 30s briefing).

### **Availability**

* **Gateway:** 99.9% Uptime (Cheap CPU server).
* **GPU Workers:** "Best Effort." If RunPod is out of GPUs, Gateway returns `503 Service Unavailable` with a user-friendly message.

### **Security**

* **Zero User Keys:** The Mobile App **NEVER** handles RunPod/AWS keys. All infrastructure orchestration happens on the Gateway.
* **Auth:** Simple Signed Token between App and Gateway to prevent API abuse.

---

## 5️⃣ Technical Architecture

### **MVP Architecture (The "Receptionist")**

* **Frontend:** Flutter (Mobile).
* **Middleware:** **Gateway Server** (Python FastAPI on AWS t3.micro).
* *Role:* Authenticates user, holds the `RUNPOD_API_KEY`, orchestrates pods.


* **Backend:** **RunPod On-Demand GPU** (RTX 4090).
* *Role:* Runs Docker container with `nvidia/personaplex`.
* *State:* Ephemeral (Born at briefing, dies at hangup).



### **Production Architecture (The "Hybrid Pool")**

* **Evolution:**
* **Reserved Pool:** Keep 2-3 GPUs running 24/7 for premium/first users (Zero boot time).
* **Orchestrator:** Gateway checks: "Is a Reserved GPU free?"  YES: Connect instantly.  NO: Boot an On-Demand Pod.
* **State:** Redis instance on Gateway to track "Occupied Slots" in the Reserved Pool.



---

## 6️⃣ Recommended Tech Stack

### **Frontend**

* **Framework:** Flutter (Dart)
* **Audio:** `flutter_sound` (PCM) or `audio_session`.
* **Network:** `web_socket_channel` (for full-duplex streaming).
* **State:** Riverpod.

### **Backend (Gateway)**

* **Language:** Python 3.10+
* **Framework:** FastAPI (Async is critical for WebSockets).
* **Hosting:** AWS EC2 (t3.micro) or DigitalOcean Droplet ($4/mo).
* **DB:** Redis (Session tracking).

### **Infrastructure (GPU Workers)**

* **Provider:** **RunPod** (Primary).
* **Hardware:** RTX 4090 (24GB VRAM).
* **Containerization:** Docker.
* **Model:** NVIDIA PersonaPlex (7B parameters).

---

## 7️⃣ Development Milestones & Timeline

### **Phase 0: Foundation (Week 1)**

* [ ] **Repo Setup:** Initialize Flutter app and Python Gateway repo.
* [ ] **Docker Image:** Build the "Generic Pod" image containing PersonaPlex + 10 Voice Files + `server.py` with "Suicide Pill."
* [ ] **Gateway Logic:** Write `boot_pod` / `kill_pod` API wrappers (Mocked locally).

### **Phase 1: Local Development (Week 2)**

* **Constraint:** Write Code Locally  Mock the GPU Response.
* [ ] **Frontend:** Build "Mission Briefing" UI & WebSocket handlers in Flutter.
* [ ] **Gateway:** Implement FastAPI routes locally.
* [ ] **Scenarios:** Write JSON configs for "Tom" & "Cindy".

### **Phase 2: Remote Integration (Week 3)**

* **Constraint:** Deploy to VPS only for Model Testing.
* [ ] **Integration:** Connect Gateway to real RunPod API.
* [ ] **Audio Tuning:** Test "Tom" on a real GPU to verify <350ms interruption speed.
* [ ] **Exit Criteria:** 3-minute conversation with "Tom" without crashing.

### **Phase 3: Production Scale (Month 2)**

* [ ] **Payments:** Integrate RevenueCat.
* [ ] **Hybrid Scaling:** Implement "Reserved Pool" logic.

---

## 8️⃣ Risks & Constraints

### **Technical Risks**

* **Risk:** RunPod runs out of On-Demand GPUs during peak hours (8 PM KST).
* *Mitigation:* Implement a "Queue" UI or fallback to secondary provider.


* **Risk:** "Zombie Pods" draining wallet.
* *Mitigation:* The "Layer 3" Cron Job is non-negotiable.



### **Product Risks**

* **Risk:** Users feel the 30s wait is too long after the 10th time.
* *Mitigation:* Phase 2 "Reserved Instances" for instant entry.



---

## 9️⃣ Metrics & KPIs

### **MVP Validation Metrics**

* **Technical Success:** % of sessions where Audio starts < 1s after "Briefing" ends. (Target: 95%).
* **Engagement:** Average Session Duration (Target: > 3 mins).
* **Reliability:** % of Boot Failures (Target: < 2%).

### **Engineering Health**

* **Cost Per Session:** Target < $0.15.
* **Zombie Rate:** % of pods requiring "Force Kill" by Cron Job.

---

## 🔟 Open Questions & Decision Log

* **Q: Voice Cloning Rights?**
* *Decision:* Use NVIDIA's default `NAT` (Natural) voices for MVP.


* **Q: Audio Codec?**
* *Decision:* Start with **PCM (Raw)**. Switch to **Opus** in Week 3 if needed.


* **Q: Protocol?**
* *Decision:* **WebSockets** (Simplest for full duplex).



---

