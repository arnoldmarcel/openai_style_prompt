# ComfyUI/custom_nodes/openai_style_prompt/__init__.py
from .node import OpenAIStylePrompt

NODE_CLASS_MAPPINGS = {
    "OpenAIStylePrompt": OpenAIStylePrompt
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenAIStylePrompt": "OpenAI Style Prompt (Subjectless)"
}
