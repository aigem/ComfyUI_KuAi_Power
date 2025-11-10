import os
import requests
import hashlib
from pathlib import Path

class DownloadVideo:
    """下载在线视频到本地"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": "", "tooltip": "视频URL"}),
            },
            "optional": {
                "save_dir": ("STRING", {"default": "output", "tooltip": "保存目录(相对于ComfyUI根目录)"}),
                "filename": ("STRING", {"default": "", "tooltip": "文件名(留空自动生成)"}),
                "timeout": ("INT", {"default": 180, "min": 5, "max": 600, "tooltip": "超时(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("本地路径", "状态")
    FUNCTION = "download"
    OUTPUT_NODE = True
    CATEGORY = "KuAi/配套能力"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "video_url": "视频URL",
            "save_dir": "保存目录",
            "filename": "文件名",
            "timeout": "超时",
        }

    def download(self, video_url, save_dir="output", filename="", timeout=180):
        if not video_url:
            raise RuntimeError("视频URL不能为空")
        
        # 获取 ComfyUI 根目录
        comfy_root = Path(__file__).parent.parent.parent.parent.parent
        output_dir = comfy_root / save_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if not filename:
            url_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
            ext = ".mp4"
            if video_url.endswith(".gif"):
                ext = ".gif"
            elif video_url.endswith(".webm"):
                ext = ".webm"
            filename = f"sora2_video_{url_hash}{ext}"
        
        filepath = output_dir / filename
        
        # 下载视频
        print(f"[DownloadVideo] 下载: {video_url}")
        try:
            resp = requests.get(video_url, timeout=int(timeout), stream=True)
            resp.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 返回相对路径
            rel_path = filepath.relative_to(comfy_root)
            print(f"[DownloadVideo] 保存到: {filepath}")
            print(f"[DownloadVideo] 相对路径: {rel_path}")
            return (str(rel_path), "下载成功")
        except Exception as e:
            error_msg = f"下载失败: {str(e)}"
            print(f"[DownloadVideo] {error_msg}")
            return ("", error_msg)


class PreviewVideo:
    """预览视频(通过VHS节点格式)"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": "", "tooltip": "视频URL"}),
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "preview"
    CATEGORY = "KuAi/配套能力"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "video_url": "视频URL",
        }

    def preview(self, video_url):
        # 返回预览信息给前端
        return {"ui": {"video": [video_url]}}


NODE_CLASS_MAPPINGS = {
    "DownloadVideo": DownloadVideo,
    "PreviewVideo": PreviewVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DownloadVideo": "💾 下载视频",
    "PreviewVideo": "🎬 预览视频",
}
