# ComfyUI/custom_nodes/openai_style_prompt/api.py
import time, re
from typing import List

# OpenAI SDK (>=1.58) – Responses API
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

def ensure_client(api_key: str):
    if OpenAI is None:
        raise RuntimeError("openai-Paket fehlt. Bitte 'pip install openai>=1.58' installieren.")
    return OpenAI(api_key=api_key)

def build_system_msg(language: str) -> str:
    return (
        "You are an Image Prompt Generator for generative image models.\n"
        "STRICT SUBJECTLESS MODE:\n"
        "- Do NOT introduce people, humans, characters, silhouettes, faces, hands, animals, creatures, or any living beings.\n"
        "- Focus ONLY on environment/background, lighting, composition, camera, color, mood, textures, materials.\n"
        "- Use any provided image strictly as environmental context; never infer or add subjects.\n"
        f"- Respond in language: {language}.\n"
        "Output must be a SINGLE plain text prompt (no code block, no preface)."
    )

def build_user_parts(preset_text: str, style_addon: str, props: str,
                     tone: str, detail: int, image_b64: str | None):
    parts = []
    brief = (
        "TASK: Produce a polished, subjectless style/background prompt suitable for image generation. "
        "No subjects, no portraits, no silhouettes; environment only.\n"
        f"TONE: {tone}\nDETAIL_LEVEL: {detail}\n\n"
        f"PRESET:\n{preset_text}\n\n"
        f"STYLE_ADDON:\n{(style_addon or '').strip()}\n\n"
        f"PROPS (environmental objects only; optional):\n{(props or '').strip()}\n\n"
        "Constraints:\n"
        "- Do not mention or imply people/animals/characters.\n"
        "- Avoid brand names/logos/readable text.\n"
        "- Keep it concise but expressive; 1–2 sentences are fine.\n"
        "Return only the final prompt line."
    )
    parts.append({"type": "input_text", "text": brief})
    if image_b64:
        parts.append({"type": "input_image", "image_url": {"url": image_b64}})
    return parts

def extract_text(resp) -> str:
    text = getattr(resp, "output_text", None)
    if text:
        return text.strip()
    if getattr(resp, "output", None):
        chunks = []
        for item in resp.output:
            if getattr(item, "type", "") == "message":
                for c in item.content:
                    if isinstance(c, dict) and c.get("type") in ("output_text", "text"):
                        chunks.append(c.get("text", ""))
        if chunks:
            return "\n".join(chunks).strip()
    return ""

def call_openai_once(client, model: str, system_msg: str, user_parts: list, max_tokens: int, temperature: float):
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": system_msg}]},
            {"role": "user",   "content": user_parts},
        ],
        max_output_tokens=max_tokens,
        temperature=temperature,
    )
    return extract_text(resp)

def call_openai(client, model: str, system_msg: str, user_parts: list, max_tokens: int, temperature: float, debug: bool) -> str:
    delays = [0.0, 1.0, 2.5]
    last_err = None
    tried_fallback = False
    for i, d in enumerate(delays):
        if d > 0: time.sleep(d)
        try:
            return call_openai_once(client, model, system_msg, user_parts, max_tokens, temperature)
        except Exception as e:
            last_err = e
            msg = str(e)
            if debug: print(f"[OpenAIStylePrompt] API attempt {i+1}/{len(delays)} failed: {msg}")
            if (("model" in msg.lower() and "not" in msg.lower() and "available" in msg.lower())
                or ("access" in msg.lower() and "denied" in msg.lower())
               ) and not tried_fallback:
                if debug: print("[OpenAIStylePrompt] falling back to gpt-4o")
                model = "gpt-4o"
                tried_fallback = True
                continue
            continue
    if last_err:
        raise last_err
    return ""
