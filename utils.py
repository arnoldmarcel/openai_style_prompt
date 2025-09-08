# ComfyUI/custom_nodes/openai_style_prompt/utils.py
import io, re, base64
from typing import Optional, List
try:
    from PIL import Image
except Exception:
    Image = None

# ----- Subjectless Sanitizer -----
FORBIDDEN_TOKENS_STRICT = [
    "person","people","human","character","model","portrait","face","faces","hand","hands","silhouette",
    "girl","boy","man","woman","male","female","child","children","kid","baby","selfie","body","bodies",
    "actor","actress","figure","subject",
    "animal","dog","cat","bird","horse","creature","monster","pet","wildlife","insect","fish",
    "crowd","group","couple"
]
FORBIDDEN_TOKENS_LIGHT = [
    "person","people","human",
    "girl","boy","man","woman","male","female","child","children","kid","baby",
    "animal","dog","cat","bird","horse","creature","monster","pet","wildlife"
]
FORBIDDEN_PHRASES_STRICT = [
    r"\bfull[- ]?body\b", r"\bheadshot\b", r"\bselfie\b", r"\bgroup photo\b", r"\bclose[- ]?up\b"
]

def format_prompt(s: str) -> str:
    if not s:
        return s
    txt = s.strip()
    txt = re.sub(r"[–—−]", ";", txt)             # unify dashes
    parts = re.split(r"[;|]", txt)
    cleaned = []
    for p in parts:
        seg = p.strip(" ,.;:").strip()
        if seg:
            cleaned.append(seg)
    seen = set()
    uniq = []
    for seg in cleaned:
        low = seg.lower()
        if low not in seen:
            seen.add(low)
            uniq.append(seg)
    out = ", ".join(uniq).strip()
    out = re.sub(r"\s+", " ", out)
    if not re.search(r"[.!?]$", out):
        out += "."
    return out

def sanitize_subjects(s: str, strength: str, strip_trailing_punct: bool) -> str:
    out = (s or "").strip()
    if strength == "off":
        if strip_trailing_punct:
            out = re.sub(r"[;,\.\s]+$", "", out).strip()
        return format_prompt(out)

    # protect "no/without ..." blocks
    placeholders = []
    def _protect(match):
        placeholders.append(match.group(0))
        return f"__NEG_BLOCK_{len(placeholders)-1}__"
    out = re.sub(r"\b(no|without)\b[^\.]*", _protect, out, flags=re.IGNORECASE)

    tokens = FORBIDDEN_TOKENS_LIGHT if strength == "light" else FORBIDDEN_TOKENS_STRICT
    for t in tokens:
        out = re.sub(rf"\b{re.escape(t)}\b", "background", out, flags=re.IGNORECASE)

    if strength == "strict":
        for pat in FORBIDDEN_PHRASES_STRICT:
            out = re.sub(pat, "background", out, flags=re.IGNORECASE)
        out = re.sub(r"\b(for|with)\s+(a|the)\s+(subject|person|character|model)\b",
                     "for the background", out, flags=re.IGNORECASE)

    out = re.sub(r"\b(background)(\s+\1\b)+", r"\1", out, flags=re.IGNORECASE)
    out = re.sub(r"\s+", " ", out).strip()

    for i, blk in enumerate(placeholders):
        out = out.replace(f"__NEG_BLOCK_{i}__", blk)

    if strip_trailing_punct:
        out = re.sub(r"[;,\.\s]+$", "", out).strip()

    return format_prompt(out)

# ----- Image helpers -----
def tensor_to_pil(image_tensor) -> Optional[Image.Image]:
    if image_tensor is None or Image is None:
        return None
    arr = image_tensor
    if hasattr(arr, "cpu"):
        arr = arr.cpu().numpy()
    if getattr(arr, "ndim", 0) == 4:
        arr = arr[0]
    try:
        amax = float(arr.max()) if hasattr(arr, "max") else 1.0
        amin = float(arr.min()) if hasattr(arr, "min") else 0.0
        if amax <= 1.01 and amin >= 0.0:
            arr = (arr * 255.0).clip(0, 255).astype("uint8")
        else:
            arr = arr.clip(0, 255).astype("uint8")
        return Image.fromarray(arr)
    except Exception:
        return None

def image_to_b64(image_tensor) -> Optional[str]:
    pil = tensor_to_pil(image_tensor)
    if pil is None:
        return None
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    import base64
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def ahash_8x8(pil: Image.Image) -> str:
    img = pil.convert("L").resize((8, 8), Image.BILINEAR)
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = ''.join('1' if p > avg else '0' for p in pixels)
    return f"{int(bits, 2):016x}"

def vision_hash(image_tensor) -> str:
    if image_tensor is None or Image is None:
        return ""
    pil = tensor_to_pil(image_tensor)
    if pil is None:
        return ""
    try:
        return ahash_8x8(pil)
    except Exception:
        return ""

# ----- Model choice -----
def choose_model(selected: str, override: str, cost_mode: str, has_image: bool, debug: bool) -> str:
    if override and override.strip():
        if debug: print(f"[OpenAIStylePrompt] using model override: {override.strip()}")
        return override.strip()
    if cost_mode == "premium":
        if debug: print(f"[OpenAIStylePrompt] cost_mode=premium, using selected: {selected}")
        return selected
    if cost_mode == "cheap":
        chosen = "gpt-5-nano"
        if debug: print(f"[OpenAIStylePrompt] cost_mode=cheap, using: {chosen}")
        return chosen
    chosen = "gpt-4o" if has_image else "gpt-5-mini"
    if debug: print(f"[OpenAIStylePrompt] cost_mode=auto, using: {chosen}")
    return chosen
