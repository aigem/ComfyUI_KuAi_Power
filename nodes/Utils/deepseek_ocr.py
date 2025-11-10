import json
import requests
import sys
from pathlib import Path

# 添加父目录到路径以导入 utils
parent_dir = Path(__file__).parent.parent / "Sora2"
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from kuai_utils import env_or, http_headers_json, raise_for_bad_status
except ImportError:
    import importlib.util
    utils_path = parent_dir / "kuai_utils.py"
    spec = importlib.util.spec_from_file_location("kuai_utils", utils_path)
    utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils)
    env_or = utils.env_or
    http_headers_json = utils.http_headers_json
    raise_for_bad_status = utils.raise_for_bad_status

class DeepseekOCRToPrompt:
    """Deepseek OCR 提取"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_url": ("STRING", {"default": "", "tooltip": "图片URL地址"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "OCR API端点"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "system_prompt": ("STRING", {
                    "default": "You are an OCR and visual describer. Extract text and summarize key scene elements, subjects, style, environment, camera, actions, mood, lighting. Output compact JSON.",
                    "multiline": True,
                    "tooltip": "系统提示词（定义OCR行为）"
                }),
                "timeout": ("INT", {"default": 60, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("OCR文本", "原始响应JSON")
    FUNCTION = "run_ocr"
    CATEGORY = "KuAi/配套能力"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image_url": "图片URL",
            "api_base": "API地址",
            "api_key": "API密钥",
            "system_prompt": "系统提示",
            "timeout": "超时",
        }

    def run_ocr(self, image_url, api_base="https://api.kuai.host", api_key="", system_prompt="", timeout=60):
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/v1/chat/completions"

        payload = {
            "model": "deepseek-ocr",
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt or "Free OCR."},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]}
            ]
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            raise_for_bad_status(resp, "Deepseek OCR failed")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"OCR 调用失败: {str(e)}")

        content = ""
        try:
            choices = data.get("choices", [])
            if choices:
                content = (choices[0].get("message") or {}).get("content") or ""
        except Exception:
            pass

        if not content:
            content = json.dumps(data, ensure_ascii=False)

        return (content, json.dumps(data, ensure_ascii=False))


NODE_CLASS_MAPPINGS = {
    "DeepseekOCRToPrompt": DeepseekOCRToPrompt,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DeepseekOCRToPrompt": "🔍 DeepSeek OCR 识图",
}
