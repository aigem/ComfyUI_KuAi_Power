import os
import io
import typing
import numpy as np
import requests
from PIL import Image

def env_or(value: str, env_name: str) -> str:
    """优先使用参数，其次使用环境变量"""
    if value and str(value).strip():
        return value
    return os.environ.get(env_name, "").strip()

def to_pil_from_comfy(image_any, index: int = 0) -> Image.Image:
    """将 ComfyUI IMAGE 转换为 PIL.Image"""
    try:
        import torch
        is_torch = True
    except Exception:
        is_torch = False

    arr = image_any
    if is_torch:
        import torch
        if isinstance(arr, torch.Tensor):
            if arr.dim() == 4:
                arr = arr[index]
            arr = arr.detach().cpu().numpy()

    if isinstance(arr, np.ndarray):
        if arr.ndim == 4:
            arr = arr[index]
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        if arr.ndim == 3 and arr.shape[2] in (1, 3, 4):
            if arr.shape[2] == 1:
                arr = np.repeat(arr, 3, axis=2)
            return Image.fromarray(arr)
        return Image.fromarray(arr)

    if isinstance(arr, Image.Image):
        return arr

    raise ValueError("无法将输入转换为 PIL.Image")

def save_image_to_buffer(pil: Image.Image, fmt: str, quality: int) -> io.BytesIO:
    """保存 PIL 到内存缓冲"""
    fmt = fmt.lower().strip()
    buf = io.BytesIO()
    if fmt == "jpeg":
        pil = pil.convert("RGB")
        pil.save(buf, format="JPEG", quality=int(quality), optimize=True)
    elif fmt == "png":
        pil.save(buf, format="PNG", optimize=True)
    elif fmt == "webp":
        pil = pil.convert("RGB")
        pil.save(buf, format="WEBP", quality=int(quality), method=6)
    else:
        raise ValueError(f"不支持的图片格式: {fmt}")
    buf.seek(0)
    return buf

def ensure_list_from_urls(urls_str: str) -> typing.List[str]:
    """将分隔的 URL 字符串拆分为列表"""
    if isinstance(urls_str, list):
        return [u for u in urls_str if str(u).strip()]
    if not isinstance(urls_str, str):
        urls_str = str(urls_str or "")
    parts = [p.strip() for p in urls_str.replace(";", ",").replace("\n", ",").split(",")]
    return [p for p in parts if p]

def http_headers_json(api_key: str = "") -> dict:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    return headers

def http_headers_multipart(api_key: str = "") -> dict:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    return headers

def raise_for_bad_status(resp: requests.Response, hint: str = ""):
    try:
        resp.raise_for_status()
    except Exception as e:
        text = ""
        try:
            text = resp.text
        except Exception:
            pass
        raise RuntimeError(f"{hint} HTTP {resp.status_code} {str(e)}: {text}")

def json_get(d: dict, path: str, default=None):
    """简易 JSON path 提取"""
    cur = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur
