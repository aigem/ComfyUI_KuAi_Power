import json
import requests

from ...utils.kuai_utils import to_pil_from_comfy, save_image_to_buffer, http_headers_multipart, raise_for_bad_status

class UploadToImageHost:
    """上传图片到临时图床"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "要上传的图片"}),
            },
            "optional": {
                "upload_url": ("STRING", {"default": "https://imageproxy.zhongzhuan.chat/api/upload", "tooltip": "图床API地址"}),
                "format": (["jpeg", "png", "webp"], {"default": "jpeg", "tooltip": "图片格式"}),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100, "tooltip": "图片质量(1-100)"}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300, "tooltip": "超时时间(秒)"}),
            }
        }
    
    INPUT_IS_LIST = False
    OUTPUT_NODE = False

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("图片URL", "创建时间")
    FUNCTION = "upload"
    CATEGORY = "KuAi/配套能力"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image": "图片",
            "upload_url": "图床URL",
            "format": "格式",
            "quality": "质量",
            "timeout": "超时",
        }

    def upload(self, image, upload_url="https://imageproxy.zhongzhuan.chat/api/upload", format="jpeg", quality=100, timeout=30):
        pil = to_pil_from_comfy(image, index=0)
        buf = save_image_to_buffer(pil, fmt=format, quality=quality)

        files = {
            "file": (
                f"image.{'jpg' if format=='jpeg' else format}",
                buf,
                f"image/{'jpeg' if format=='jpeg' else format}"
            )
        }
        
        try:
            resp = requests.post(upload_url, headers=http_headers_multipart(), files=files, timeout=int(timeout))
            raise_for_bad_status(resp, "Upload image failed")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"上传失败: {str(e)}")

        url = data.get("url", "")
        created = str(data.get("created", ""))
        if not url:
            raise RuntimeError(f"上传响应缺少 url 字段: {json.dumps(data, ensure_ascii=False)}")
        return (url, created)


NODE_CLASS_MAPPINGS = {
    "UploadToImageHost": UploadToImageHost,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UploadToImageHost": "📷 传图到临时图床",
}
