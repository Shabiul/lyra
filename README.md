# 🌸 Lyra — Offline Waifu AI Companion

> A fully local, privacy-first AI companion. No cloud. No API keys. Everything runs on your machine.

---

## Stack

| Layer | Tech |
|---|---|
| LLM | Ollama (Qwen2.5 32B) |
| Memory | ChromaDB + SQLite |
| STT | faster-whisper (CUDA) |
| TTS | XTTSv2 (Coqui) |
| Vision | OpenCV + MediaPipe |
| Backend | Python (FastAPI) + Node.js (Express) |

---

## Quick Start

### 1. Prerequisites
- [Ollama](https://ollama.com) installed and running
- Python 3.11+
- Node.js 20+
- CUDA toolkit (for GPU acceleration)

### 2. Pull the LLM model
```powershell
ollama pull qwen2.5:32b
```

### 3. Install dependencies
```powershell
cd lyra
.\scripts\setup.ps1
```

### 4. Start all services
```powershell
.\scripts\start-all.ps1
```

### 5. Talk to Lyra
```powershell
# Quick test via curl
curl -X POST http://localhost:8001/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "hey lyra", "session_id": "test"}'
```

---

## Services

| Service | Port | Language | Status |
|---|---|---|---|
| api-gateway | 3000 | Node.js | 🔜 In progress |
| llm-core | 8001 | Python | ✅ Done |
| memory | 8002 | Python | 🔜 In progress |
| voice | 8003 | Python | 🔜 In progress |
| vision | 8004 | Python | 🔜 In progress |
| avatar-bridge | 3001 | Node.js | ⏳ Later |

---

## Project Structure

```
lyra/
├── services/
│   ├── llm-core/       ✅ Lyra's brain
│   ├── memory/         🔜 Long-term memory
│   ├── voice/          🔜 TTS + STT
│   ├── vision/         🔜 Webcam awareness
│   ├── api-gateway/    🔜 Main entry point
│   └── avatar-bridge/  ⏳ Live2D/Unity (later)
├── shared/
│   ├── config/         ✅ lyra.config.json
│   ├── types/          ✅ Pydantic models
│   └── utils/          ✅ Config loader
├── data/               Auto-created at runtime
├── scripts/            ✅ setup / start / stop
└── docs/
```
