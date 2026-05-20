# NVIDIA API Key Checker 

Test your `nvapi-*` keys from [build.nvidia.com](https://build.nvidia.com) with a full server-side fallback chain.

## What it does

| Feature | How |
|---|---|
| ✅ **Check Key** | Server-side via `/api/check` — 6 methods, 2 URLs |
| 🚀 **Send Prompt** | Direct browser → NVIDIA (with URL fallback) |
| ⚡ **Auto-Check** | Loops all 120+ models directly from browser |

### Fallback Chain (Check Key)
```
A1 → openai pkg  → api.nvidia.com
A2 → openai pkg  → integrate.api.nvidia.com
B1 → requests    → api.nvidia.com
B2 → requests    → integrate.api.nvidia.com
C1 → http.client → api.nvidia.com        (pure stdlib)
C2 → http.client → integrate.api.nvidia.com  (pure stdlib)
```
Stops at first success. Returns detailed logs shown in the UI.

---

## Project Structure

```
nvidia-key-checker/
├── api/
│   └── check.py        ← Vercel Python serverless endpoint
├── public/
│   └── index.html      ← Frontend (stone glassmorphism UI)
├── vercel.json         ← Vercel config
├── requirements.txt    ← openai + requests
└── README.md
```

---

## Deploy

### 1. GitHub
```bash
git init
git add .
git commit -m "init: nvidia api key checker"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/nvidia-key-checker.git
git branch -M main
git push -u origin main
```

### 2. Vercel
1. Go to **vercel.com** → **Add New Project**
2. Import your GitHub repo
3. Framework preset → **Other**
4. Root directory → leave as `/`
5. Click **Deploy**

That's it. Vercel auto-detects:
- `api/check.py` → serverless Python endpoint at `/api/check`
- `public/index.html` → static frontend at `/`

### Live URLs after deploy
- Frontend: `https://nvidia-key-checker.vercel.app/`
- API: `https://nvidia-key-checker.vercel.app/api/check`

---

## Local Testing (Python CLI)

The `api/check.py` logic works standalone too:

```bash
pip install openai requests
python - <<'EOF'
import sys; sys.path.insert(0, 'api')
from check import run_check
result = run_check("nvapi-YOUR-KEY-HERE")
for line in result['log']: print(line)
print("valid:", result['valid'])
EOF
```

---

## Vercel Plan Notes

| | Hobby (free) | Pro |
|---|---|---|
| Function timeout | 10s | 60s |
| `maxDuration` in vercel.json | max 10 | up to 60 |

On the free plan, change `vercel.json` → `"maxDuration": 10`.
The checker still works — it stops at the first successful method.

---

## API Reference

**POST `/api/check`**

Request:
```json
{ "api_key": "nvapi-xxxxxxxxxxxx" }
```

Response:
```json
{
  "valid": true,
  "method": "openai-pkg",
  "base_url": "https://api.nvidia.com/v1",
  "model": "meta/llama-3.1-8b-instruct",
  "reply": "Hi! How can I help you?",
  "elapsed_ms": 842,
  "status_code": 200,
  "error": null,
  "log": [
    "OK    Key format valid → nvapi-...xxxx",
    "INFO  [A] openai package available v1.x.x",
    "TRY   [A1] openai → https://api.nvidia.com/v1",
    "OK    [A1] 200 OK | meta/llama-3.1-8b-instruct | 842ms",
    ...
  ]
}
```
