# ComfyUI/custom_nodes/openai_style_prompt/node.py
# OpenAI Style Prompt (Subjectless) v1.6 — modular
import os, pathlib
from typing import Dict, Optional

from .presets import PRESETS
from .cache import DiskCache, lru_get, lru_put, cache_key
from .utils import sanitize_subjects, format_prompt, image_to_b64, vision_hash, choose_model
from .api import ensure_client, build_system_msg, build_user_parts, call_openai

NODE_VERSION = "v1.6"

class OpenAIStylePrompt:
    """
    Subjectless Style/Environment Prompt Generator für ComfyUI (v1.6)
    - EIN String-Output
    - Optional Vision-Kontext
    - Presets + Style-Addon + Props (unbelebte Requisiten)
    - Kostenoptimierung: LRU+Disk Cache, Template-Mode, Tiered-Model-Policy
    - Formatter (schöne Kommas/Punkt) + konfigurierbarer Sanitizer
    - Responses API mit robustem Retry & Modell-Fallback
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ([ "gpt-5",
                            "gpt-5-mini",
                            "gpt-5-nano",
                            "gpt-4o",
                            "gpt-4o-mini",
                            "gpt-4-turbo",
                            "gpt-4.1",
                            "gpt-4.1-mini",
                            "gpt-4",
                            "gpt-3.5-turbo",
                            "o1-preview",
                            "o1-mini",
                        ], {"default": "gpt-4o"}),
                "preset": (list(PRESETS.keys()), {"default": "Greenscreen Studio"}),
                "style_addon": ("STRING", {"multiline": True, "default": ""}),
                "props": ("STRING", {"multiline": True, "default": ""}),
                "language": (["de", "en"], {"default": "de"}),
                "prompt_tone": (["neutral", "cinematic", "photography", "illustration", "product"], {"default": "photography"}),
                "detail_level": ("INT", {"default": 3, "min": 1, "max": 5}),
                "max_tokens": ("INT", {"default": 350, "min": 64, "max": 2000}),
                "temperature": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.1}),
                "template_mode": (["auto","on","off"], {"default": "auto"}),
                "cost_mode": (["auto","cheap","premium"], {"default": "auto"}),
                "use_cache": ("BOOLEAN", {"default": True}),
                "cache_ttl_days": ("INT", {"default": 0, "min": 0, "max": 365}),
                "sanitizer_strength": (["off","light","strict"], {"default": "strict"}),
                "strip_trailing_punctuation": ("BOOLEAN", {"default": True}),
                "debug_log": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "image": ("IMAGE",),
                "preset_override": ("STRING", {"default": ""}),
                "model_override": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("image_prompt",)
    FUNCTION = "run"
    CATEGORY = "LLM/OpenAI"

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY Umgebungsvariable fehlt.")
        self.client = ensure_client(api_key)
        user_dir = pathlib.Path(os.getenv("COMFYUI_USER_PATH", "ComfyUI/user"))
        self.cache = DiskCache(user_dir / "openai_style_prompt_cache")

    # -------- Template generator (kostenfrei) --------
    def _template_generate(self, preset_name: str, base_text: str, style_addon: str, props: str, tone: str, language: str) -> Optional[str]:
        base = base_text or PRESETS.get(preset_name)
        if not base:
            return None

        tone_map = {
            "neutral": {"de":"neutral ausgeleuchtet", "en":"neutral lighting"},
            "cinematic": {"de":"cinematisch mit weicher Kontrastführung", "en":"cinematic with gentle contrast"},
            "photography": {"de":"fotografischer Look mit realistischem Dynamikumfang", "en":"photographic look with realistic dynamic range"},
            "illustration": {"de":"klar strukturiert, illustrativer Stil", "en":"clean structured, illustrative style"},
            "product": {"de":"sauberer, produktorientierter Look", "en":"clean, product-oriented look"},
        }
        tline = tone_map.get(tone, tone_map["neutral"]).get(language, "neutral")

        props_txt = re_norm(props="")
        addon_txt = re_norm(props="")  # placeholder; below we'll use raw style_addon/props but cleaned minimally
        # we prefer not to lowercase user text here; just trim and normalize whitespace:
        def norm_keepcase(s: str) -> str:
            import re
            return re.sub(r"\s+", " ", (s or "").strip())

        props_line = norm_keepcase(props)
        addon_line = norm_keepcase(style_addon)

        if language == "de":
            lines = [
                f"{base} – {tline}",
                f"requisiten: {props_line}" if props_line else "",
                f"stil: {addon_line}" if addon_line else ""
            ]
        else:
            lines = [
                f"{base} – {tline}",
                f"props: {props_line}" if props_line else "",
                f"style: {addon_line}" if addon_line else ""
            ]
        prompt = ", ".join([l for l in lines if l]).strip()
        return prompt

    def run(self, model, preset, style_addon, props, language, prompt_tone, detail_level,
            max_tokens, temperature, template_mode, cost_mode, use_cache, cache_ttl_days,
            sanitizer_strength, strip_trailing_punctuation, debug_log,
            image=None, preset_override="", model_override=""):

        # Inputs & policy
        preset_text = (preset_override.strip() or PRESETS.get(preset, "")).strip()
        image_b64 = image_to_b64(image) if image is not None else None
        has_image = image_b64 is not None
        chosen_model = choose_model(model, model_override, cost_mode, has_image, debug_log)

        # Cache key
        vhash = vision_hash(image)
        key = cache_key(chosen_model, language, preset_text, style_addon, props, prompt_tone, detail_level, vhash, sanitizer_strength)

        # TTL
        ttl_sec = cache_ttl_days * 24 * 3600 if cache_ttl_days and cache_ttl_days > 0 else None

        # Cache read
        if use_cache:
            hit = lru_get(key)
            if hit:
                if debug_log: print(f"[OpenAIStylePrompt] LRU cache hit ({key[:8]}...)")
                return (hit,)
            disk_hit = self.cache.get(key, max_age_sec=ttl_sec)
            if disk_hit:
                if debug_log: print(f"[OpenAIStylePrompt] disk cache hit ({key[:8]}...)")
                lru_put(key, disk_hit)
                return (disk_hit,)
            if debug_log: print(f"[OpenAIStylePrompt] cache miss ({key[:8]}...)")

        # Template-mode (kostenfrei)
        if template_mode in ("auto","on"):
            if (template_mode == "on") or (image is None and not preset_override.strip() and detail_level <= 3):
                templ = self._template_generate(preset, preset_text if preset_override.strip() else "", style_addon, props, prompt_tone, language)
                if templ:
                    final_templ = sanitize_subjects(templ, sanitizer_strength, strip_trailing_punctuation)
                    if use_cache:
                        lru_put(key, final_templ)
                        self.cache.put(key, final_templ)
                    if debug_log: print(f"[OpenAIStylePrompt] template-mode output ({key[:8]}...)")
                    return (final_templ,)

        # OpenAI call (Responses API)
        system_msg = build_system_msg(language)
        user_parts = build_user_parts(preset_text, style_addon, props, prompt_tone, detail_level, image_b64)

        try:
            raw = call_openai(self.client, chosen_model, system_msg, user_parts, max_tokens, temperature, debug_log)
            prompt1 = sanitize_subjects(raw, sanitizer_strength, strip_trailing_punctuation)
            final_prompt = prompt1

            if use_cache and final_prompt:
                lru_put(key, final_prompt)
                self.cache.put(key, final_prompt)

            return (final_prompt,)

        except Exception as e:
            if debug_log: print(f"[OpenAIStylePrompt] API failed, fallback to template ({e})")
            templ = self._template_generate(preset, preset_text, style_addon, props, prompt_tone, language)
            if templ:
                final_templ = sanitize_subjects(templ, sanitizer_strength, strip_trailing_punctuation)
                if use_cache:
                    lru_put(key, final_templ)
                    self.cache.put(key, final_templ)
                return (final_templ,)
            fallback = preset_text
            fallback = sanitize_subjects(fallback, sanitizer_strength, strip_trailing_punctuation)
            if use_cache:
                lru_put(key, fallback)
                self.cache.put(key, fallback)
            return (fallback,)

# small local helper (kept here to avoid extra import just for two lines)
import re
def re_norm(props: str) -> str:
    return re.sub(r"\s+", " ", (props or "").strip().lower())
