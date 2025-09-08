# ComfyUI/custom_nodes/openai_style_prompt/cache.py
import json, pathlib, time, hashlib, re
from collections import OrderedDict
from typing import Optional

NODE_VERSION = "v1.6"
_LRU_CAPACITY = 256

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

class LRU(OrderedDict):
    def __init__(self, capacity=_LRU_CAPACITY):
        super().__init__()
        self.capacity = capacity
    def get(self, key):
        if key in self:
            self.move_to_end(key)
            return super().get(key)
        return None
    def put(self, key, value):
        self[key] = value
        self.move_to_end(key)
        if len(self) > self.capacity:
            self.popitem(last=False)

LRU_MEM = LRU()

def lru_get(key: str) -> Optional[str]:
    return LRU_MEM.get(key)

def lru_put(key: str, value: str) -> None:
    LRU_MEM.put(key, value)

def cache_key(model, language, preset_text, style_addon, props, tone, detail, vhash, sanitizer_strength, node_ver=NODE_VERSION, extra=""):
    raw = "|".join([
        str(model), str(language), _norm(preset_text), _norm(style_addon),
        _norm(props), str(tone), str(detail), str(vhash), str(node_ver),
        f"san:{sanitizer_strength}", str(extra)
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class DiskCache:
    def __init__(self, base_dir: pathlib.Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def path(self, key: str) -> pathlib.Path:
        return self.base_dir / f"{key}.json"

    def get(self, key: str, max_age_sec: Optional[int]=None) -> Optional[str]:
        p = self.path(key)
        if not p.exists(): return None
        if max_age_sec is not None:
            try:
                if time.time() - p.stat().st_mtime > max_age_sec:
                    return None
            except Exception:
                return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("prompt")
        except Exception:
            return None

    def put(self, key: str, prompt: str) -> None:
        try:
            self.path(key).write_text(json.dumps({"prompt": prompt}, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
