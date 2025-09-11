import os, requests
OLLAMA = os.getenv("OLLAMA_BASE","http://ollama:11434")

def summarize_and_tags(text: str) -> str:
    prompt = f"Özetle ve 5 etiket öner:\n\n{text[:6000]}"
    try:
        r = requests.post(f"{OLLAMA}/api/generate", json={
            "model": "llama3", "prompt": prompt, "stream": False
        }, timeout=60)
        js = r.json(); return js.get("response", "")
    except Exception:
        return ""