"""
NVIDIA API Key Checker — Vercel Serverless Function
POST /api/check  { "api_key": "nvapi-..."  ,  "model"?,  "temperature"?,  "max_tokens"?,  "timeout"? }
Returns: { valid, method, base_url, model, reply, elapsed_ms, error, log[] }
"""

from http.server import BaseHTTPRequestHandler
import json, time, http.client, ssl, urllib.parse

BASE_URLS = [
    "https://api.nvidia.com/v1",
    "https://integrate.api.nvidia.com/v1",
]
DEFAULT_MODELS = [
    "meta/llama-3.1-8b-instruct",
    "mistralai/mistral-7b-instruct-v0.3",
    "meta/llama-3.3-70b-instruct",
    "nvidia/llama-3.1-nemotron-70b-instruct",
]
PROMPT = "hi"
DEFAULT_TIMEOUT = 12

def run_check(api_key: str, model: str = None, temperature: float = 0.7, max_tokens: int = 48, timeout: int = DEFAULT_TIMEOUT) -> dict:
    log = []
    result = {
        "valid": False,
        "method": None,
        "base_url": None,
        "model": None,
        "reply": None,
        "elapsed_ms": None,
        "status_code": None,
        "error": None,
        "log": log,
    }

    # ── Validate key format ────────────────────────────────────────
    if not api_key:
        result["error"] = "No API key provided"
        return result
    if not api_key.startswith("nvapi-"):
        log.append("WARN  Key does not start with 'nvapi-' — proceeding anyway")
    else:
        log.append(f"OK    Key format valid → nvapi-...{api_key[-4:]}")

    # Determine models to test
    if model:
        models_to_test = [model]
        log.append(f"INFO  Using user-specified model: {model}")
    else:
        models_to_test = DEFAULT_MODELS

    # ── Method A: openai package ────────────────────────────────────
    try:
        import openai
        log.append(f"INFO  [A] openai package available v{openai.__version__}")
        for base_url in BASE_URLS:
            label = "A1" if "//api." in base_url else "A2"
            log.append(f"TRY   [{label}] openai → {base_url}")
            for mdl in models_to_test:
                t0 = time.time()
                try:
                    client = openai.OpenAI(api_key=api_key, base_url=base_url)
                    comp = client.chat.completions.create(
                        model=mdl,
                        messages=[{"role": "user", "content": PROMPT}],
                        max_tokens=max_tokens,
                        temperature=temperature,
                        timeout=timeout,
                    )
                    elapsed = int((time.time() - t0) * 1000)
                    reply = comp.choices[0].message.content.strip()
                    usage = comp.usage
                    log.append(f"OK    [{label}] 200 OK | {mdl} | {elapsed}ms")
                    log.append(f"      tokens prompt={usage.prompt_tokens} completion={usage.completion_tokens}")
                    log.append(f"      reply → {reply[:100]}")
                    result.update(
                        valid=True, method="openai-pkg",
                        base_url=base_url, model=mdl,
                        reply=reply, elapsed_ms=elapsed, status_code=200
                    )
                    return result
                except openai.AuthenticationError as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] 401 Unauthorized | {mdl} | {elapsed}ms")
                    log.append(f"      {str(e)[:120]}")
                    result["error"] = "401 Unauthorized — key invalid or expired"
                    result["status_code"] = 401
                    break
                except openai.RateLimitError as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"WARN  [{label}] 429 Rate Limited | {mdl} | {elapsed}ms — key is VALID")
                    result.update(
                        valid=True, method="openai-pkg",
                        base_url=base_url, model=mdl,
                        elapsed_ms=elapsed, status_code=429,
                        error="429 Rate Limited — key is valid but quota exceeded"
                    )
                    return result
                except openai.NotFoundError:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"WARN  [{label}] 404 model not found '{mdl}' | {elapsed}ms → trying next")
                    continue
                except openai.APIConnectionError as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] Connection error → {base_url} | {elapsed}ms")
                    log.append(f"      {str(e)[:120]}")
                    break
                except openai.APIStatusError as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] HTTP {e.status_code} | {mdl} | {elapsed}ms")
                    log.append(f"      {str(e)[:120]}")
                    if e.status_code == 401:
                        result["error"] = "401 Unauthorized — key invalid"
                        result["status_code"] = 401
                        break
                    continue
                except Exception as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] {type(e).__name__}: {str(e)[:120]} | {elapsed}ms")
                    break
    except ImportError:
        log.append("INFO  [A] openai package not installed — skipping A1/A2")

    # ── Method B: requests ──────────────────────────────────────────
    try:
        import requests as req
        log.append(f"INFO  [B] requests available v{req.__version__}")
        for idx, base_url in enumerate(BASE_URLS):
            label = f"B{idx+1}"
            log.append(f"TRY   [{label}] requests → {base_url}")
            for mdl in models_to_test:
                endpoint = f"{base_url}/chat/completions"
                t0 = time.time()
                try:
                    resp = req.post(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": mdl,
                            "messages": [{"role": "user", "content": PROMPT}],
                            "max_tokens": max_tokens,
                            "temperature": temperature,
                        },
                        timeout=timeout,
                    )
                    elapsed = int((time.time() - t0) * 1000)
                    status = resp.status_code
                    log.append(f"      [{label}] HTTP {status} | {mdl} | {elapsed}ms")
                    if status == 200:
                        data = resp.json()
                        reply = data["choices"][0]["message"]["content"].strip()
                        usage = data.get("usage", {})
                        log.append(f"OK    [{label}] 200 OK | tokens prompt={usage.get('prompt_tokens','?')} completion={usage.get('completion_tokens','?')}")
                        log.append(f"      reply → {reply[:100]}")
                        result.update(
                            valid=True, method="requests",
                            base_url=base_url, model=mdl,
                            reply=reply, elapsed_ms=elapsed, status_code=200
                        )
                        return result
                    elif status == 401:
                        body = resp.text[:150]
                        log.append(f"FAIL  [{label}] 401 Unauthorized — key INVALID")
                        log.append(f"      {body}")
                        result["error"] = "401 Unauthorized — key invalid"
                        result["status_code"] = 401
                        break
                    elif status == 429:
                        log.append(f"WARN  [{label}] 429 Rate Limited — key is VALID")
                        result.update(
                            valid=True, method="requests",
                            base_url=base_url, model=mdl,
                            elapsed_ms=elapsed, status_code=429,
                            error="429 Rate Limited — key valid"
                        )
                        return result
                    elif status == 404:
                        log.append(f"WARN  [{label}] 404 model '{mdl}' not found → trying next")
                        continue
                    elif status == 403:
                        log.append(f"WARN  [{label}] 403 Forbidden for '{mdl}' → trying next")
                        continue
                    else:
                        log.append(f"FAIL  [{label}] HTTP {status} unexpected — {resp.text[:100]}")
                        continue
                except req.exceptions.ConnectionError as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] ConnectionError → {base_url} | {elapsed}ms")
                    break
                except req.exceptions.Timeout:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] Timeout after {timeout}s")
                    break
                except Exception as e:
                    elapsed = int((time.time() - t0) * 1000)
                    log.append(f"FAIL  [{label}] {type(e).__name__}: {str(e)[:100]} | {elapsed}ms")
                    break
    except ImportError:
        log.append("INFO  [B] requests not installed — skipping B1/B2")

    # ── Method C: pure stdlib http.client ────────────────────────────
    log.append("INFO  [C] stdlib http.client (no pip packages required)")
    for idx, base_url in enumerate(BASE_URLS):
        label = f"C{idx+1}"
        parsed = urllib.parse.urlparse(base_url)
        host = parsed.netloc
        base_path = parsed.path
        log.append(f"TRY   [{label}] http.client → {base_url}")
        for mdl in models_to_test:
            path = base_path.rstrip("/") + "/chat/completions"
            payload = json.dumps({
                "model": mdl,
                "messages": [{"role": "user", "content": PROMPT}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }).encode("utf-8")
            t0 = time.time()
            try:
                ctx = ssl.create_default_context()
                conn = http.client.HTTPSConnection(host, timeout=timeout, context=ctx)
                conn.request("POST", path, body=payload, headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Content-Length": str(len(payload)),
                })
                resp = conn.getresponse()
                elapsed = int((time.time() - t0) * 1000)
                body_raw = resp.read().decode("utf-8", errors="replace")
                status = resp.status
                log.append(f"      [{label}] HTTP {status} | {mdl} | {elapsed}ms")
                if status == 200:
                    data = json.loads(body_raw)
                    reply = data["choices"][0]["message"]["content"].strip()
                    usage = data.get("usage", {})
                    log.append(f"OK    [{label}] 200 OK | tokens prompt={usage.get('prompt_tokens','?')} completion={usage.get('completion_tokens','?')}")
                    log.append(f"      reply → {reply[:100]}")
                    result.update(
                        valid=True, method="stdlib-http",
                        base_url=base_url, model=mdl,
                        reply=reply, elapsed_ms=elapsed, status_code=200
                    )
                    return result
                elif status == 401:
                    log.append(f"FAIL  [{label}] 401 Unauthorized — key INVALID")
                    log.append(f"      {body_raw[:150]}")
                    result["error"] = "401 Unauthorized — key invalid"
                    result["status_code"] = 401
                    break
                elif status == 429:
                    log.append(f"WARN  [{label}] 429 Rate Limited — key is VALID")
                    result.update(
                        valid=True, method="stdlib-http",
                        base_url=base_url, model=mdl,
                        elapsed_ms=elapsed, status_code=429,
                        error="429 Rate Limited — key valid"
                    )
                    return result
                elif status == 404:
                    log.append(f"WARN  [{label}] 404 model '{mdl}' not found → trying next")
                    continue
                else:
                    log.append(f"FAIL  [{label}] HTTP {status} — {body_raw[:100]}")
                    continue
                conn.close()
            except (ConnectionRefusedError, OSError) as e:
                elapsed = int((time.time() - t0) * 1000)
                log.append(f"FAIL  [{label}] OS/Connection error: {str(e)[:100]} | {elapsed}ms")
                break
            except Exception as e:
                elapsed = int((time.time() - t0) * 1000)
                log.append(f"FAIL  [{label}] {type(e).__name__}: {str(e)[:100]} | {elapsed}ms")
                break

    if not result["error"]:
        result["error"] = "All methods failed — check network/firewall or key validity"
    log.append(f"DONE  valid={result['valid']} error={result['error']}")
    return result


# ─── Vercel HTTP Handler (updated to read optional fields) ──────────

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            body = json.loads(raw)
            api_key = (body.get("api_key") or "").strip()
            model = body.get("model", None) or None   # '' → None
            temperature = float(body.get("temperature", 0.7))
            max_tokens = int(body.get("max_tokens", 48))
            timeout = int(body.get("timeout", DEFAULT_TIMEOUT))
            # clamp reasonable values
            temperature = max(0, min(2, temperature))
            max_tokens = max(1, min(4096, max_tokens))
            timeout = max(3, min(120, timeout))
        except Exception as e:
            self._json(400, {"error": "Invalid JSON body"})
            return

        if not api_key:
            self._json(400, {"error": "api_key field is required"})
            return

        result = run_check(api_key, model=model, temperature=temperature, max_tokens=max_tokens, timeout=timeout)
        self._json(200, result)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass