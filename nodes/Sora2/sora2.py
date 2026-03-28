import json
import time
import requests
from ...utils.kuai_utils import (env_or, ensure_list_from_urls,
                                http_headers_json, raise_for_bad_status, json_get)


class SoraCreateVideo:
    """创建 Sora 视频任务"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("STRING", {"default": "", "multiline": False, "tooltip": "图片URL列表，逗号分隔"}),
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "视频提示词"}),
                "model": (["sora-2-all", "sora-2-pro-all"], {"default": "sora-2-all", "tooltip": "模型选择"}),
                "duration_sora2": (["10", "15"], {"default": "10", "tooltip": "sora-2时长(秒)"}),
                "duration_sora2pro": (["15", "25"], {"default": "15", "tooltip": "sora-2-pro时长(秒)"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "orientation": (["portrait", "landscape"], {"default": "portrait", "tooltip": "视频方向：竖屏/横屏"}),
                "size": (["small", "large"], {"default": "large", "tooltip": "视频尺寸"}),
                "watermark": ("BOOLEAN", {"default": False, "tooltip": "是否添加水印"}),
                "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "状态更新时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Sora2"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "images": "图片列表",
            "prompt": "提示词",
            "model": "模型",
            "duration_sora2": "sora-2时长",
            "duration_sora2pro": "sora-2-pro时长",
            "api_base": "API地址",
            "api_key": "API密钥",
            "orientation": "方向",
            "size": "尺寸",
            "watermark": "水印",
            "timeout": "超时",
        }

    def create(self, images, prompt, model="sora-2-all", duration_sora2="10", duration_sora2pro="15",
               api_base="https://api.kuai.host", api_key="", orientation="portrait", size="large", watermark=False, timeout=120):
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/v1/video/create"

        images_list = ensure_list_from_urls(images)
        if not images_list:
            raise RuntimeError("请至少提供一个图片 URL")
        
        # 根据模型选择时长
        duration = int(duration_sora2) if model == "sora-2-all" else int(duration_sora2pro)
        
        payload = {
            "images": images_list,
            "model": model,
            "orientation": orientation,
            "prompt": prompt,
            "size": size,
            "duration": duration,
            "watermark": bool(watermark),
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            raise_for_bad_status(resp, "Sora create failed")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"创建视频失败: {str(e)}")

        task_id = data.get("id") or data.get("task_id") or ""
        status = data.get("status") or ""
        status_update_time = int(data.get("status_update_time") or 0)

        if not task_id:
            raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

        return (task_id, status, status_update_time)


class SoraQueryTask:
    """查询 Sora 视频任务"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_id": ("STRING", {"default": "", "tooltip": "任务ID"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "wait": ("BOOLEAN", {"default": True, "tooltip": "是否等待任务完成"}),
                "poll_interval_sec": ("INT", {"default": 15, "min": 5, "max": 90, "tooltip": "轮询间隔(秒)"}),
                "timeout_sec": ("INT", {"default": 1200, "min": 600, "max": 9600, "tooltip": "总超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("状态", "视频URL", "GIF_URL", "缩略图URL", "原始响应JSON")
    FUNCTION = "query"
    CATEGORY = "KuAi/Sora2"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "task_id": "任务ID",
            "api_base": "API地址",
            "api_key": "API密钥",
            "wait": "等待完成",
            "poll_interval_sec": "轮询间隔",
            "timeout_sec": "总超时",
        }

    def query(self, task_id, api_base="https://api.kuai.host", api_key="", wait=True, poll_interval_sec=5, timeout_sec=600):
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/v1/video/query"

        def once():
            try:
                resp = requests.get(endpoint, headers=http_headers_json(api_key), params={"id": task_id}, timeout=60)
                raise_for_bad_status(resp, "Sora query failed")
                data = resp.json()
            except Exception as e:
                raise RuntimeError(f"查询失败: {str(e)}")

            status = data.get("status") or json_get(data, "detail.status") or ""
            video_url = data.get("video_url") or json_get(data, "detail.url") or json_get(data, "detail.downloadable_url") or ""
            gif_url = json_get(data, "detail.gif_url") or json_get(data, "detail.encodings.gif.path") or ""
            thumbnail_url = data.get("thumbnail_url") or json_get(data, "detail.encodings.thumbnail.path") or ""

            return status, video_url, gif_url, thumbnail_url, json.dumps(data, ensure_ascii=False)

        if not wait:
            return once()

        print(f"[SoraQueryTask] 开始轮询任务 {task_id}，超时 {timeout_sec} 秒，间隔 {poll_interval_sec} 秒")
        deadline = time.time() + int(timeout_sec)
        last_raw = ""
        poll_count = 0
        while time.time() < deadline:
            poll_count += 1
            status, video_url, gif_url, thumbnail_url, raw = once()
            last_raw = raw
            print(f"[SoraQueryTask] 第 {poll_count} 次查询: 状态={status}")
            if status in ("completed", "failed"):
                print(f"[SoraQueryTask] 任务完成: {status}")
                return (status, video_url, gif_url, thumbnail_url, raw)
            time.sleep(int(poll_interval_sec))
        
        print(f"[SoraQueryTask] 轮询超时")
        return ("timeout", "", "", "", last_raw or json.dumps({"error": "timeout"}, ensure_ascii=False))


class SoraCreateAndWait:
    """创建视频并等待完成"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("STRING", {"default": "", "multiline": False, "tooltip": "图片URL列表，逗号分隔"}),
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "视频提示词"}),
                "model": (["sora-2-all", "sora-2-pro-all"], {"default": "sora-2-all", "tooltip": "模型选择"}),
                "duration_sora2": (["10", "15"], {"default": "10", "tooltip": "sora-2时长(秒)"}),
                "duration_sora2pro": (["15", "25"], {"default": "15", "tooltip": "sora-2-pro时长(秒)"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "orientation": (["portrait", "landscape"], {"default": "portrait", "tooltip": "视频方向：竖屏/横屏"}),
                "size": (["small", "large"], {"default": "large", "tooltip": "视频尺寸"}),
                "watermark": ("BOOLEAN", {"default": False, "tooltip": "是否添加水印"}),
                "create_timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "创建超时(秒)"}),
                "wait_poll_interval_sec": ("INT", {"default": 5, "min": 1, "max": 60, "tooltip": "轮询间隔(秒)"}),
                "wait_timeout_sec": ("INT", {"default": 600, "min": 5, "max": 9600, "tooltip": "等待超时(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("状态", "视频URL", "GIF_URL", "缩略图URL", "任务ID")
    FUNCTION = "run"
    CATEGORY = "KuAi/Sora2"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "images": "图片列表",  # 显示为“图片列表”
            "prompt": "提示词",    # 显示为“提示词”
            "model": "模型",       # 显示为“模型”
            "duration_sora2": "sora-2时长",
            "duration_sora2pro": "sora-2-pro时长",
            "api_base": "API地址",
            "api_key": "API密钥",
            "orientation": "方向",
            "size": "尺寸",
            "watermark": "水印",
            "create_timeout": "创建超时",
            "wait_poll_interval_sec": "轮询间隔",
            "wait_timeout_sec": "等待超时",
        }

    def run(self, images, prompt, model="sora-2", duration_sora2="10", duration_sora2pro="15",
            api_base="https://api.kuai.host", api_key="", orientation="portrait", size="large", watermark=False,
            create_timeout=120, wait_poll_interval_sec=5, wait_timeout_sec=600):

        creator = SoraCreateVideo()
        task_id, status, _ = creator.create(
            images=images, prompt=prompt, model=model, duration_sora2=duration_sora2, duration_sora2pro=duration_sora2pro,
            api_base=api_base, api_key=api_key, orientation=orientation, size=size,
            watermark=watermark, timeout=create_timeout
        )

        querier = SoraQueryTask()
        status, video_url, gif_url, thumbnail_url, _raw = querier.query(
            task_id=task_id, api_base=api_base, api_key=api_key, wait=True,
            poll_interval_sec=wait_poll_interval_sec, timeout_sec=wait_timeout_sec
        )
        
        return (status, video_url, gif_url, thumbnail_url, task_id)

class SoraText2Video:
    """文生视频（无需图片）"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "视频提示词"}),
                "model": (["sora-2-all", "sora-2-pro-all"], {"default": "sora-2-all", "tooltip": "模型选择"}),
                "duration_sora2": (["10", "15"], {"default": "10", "tooltip": "sora-2时长(秒)"}),
                "duration_sora2pro": (["15", "25"], {"default": "15", "tooltip": "sora-2-pro时长(秒)"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "orientation": (["portrait", "landscape"], {"default": "portrait", "tooltip": "视频方向：竖屏/横屏"}),
                "size": (["small", "large"], {"default": "large", "tooltip": "视频尺寸"}),
                "watermark": ("BOOLEAN", {"default": False, "tooltip": "是否添加水印"}),
                "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "状态更新时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Sora2"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model": "模型",
            "duration_sora2": "sora-2时长",
            "duration_sora2pro": "sora-2-pro时长",
            "api_base": "API地址",
            "api_key": "API密钥",
            "orientation": "方向",
            "size": "尺寸",
            "watermark": "水印",
            "timeout": "超时",
        }

    def create(self, prompt, model="sora-2", duration_sora2="10", duration_sora2pro="15",
               api_base="https://api.kuai.host", api_key="", orientation="portrait", size="large", watermark=False, timeout=120):
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/v1/video/create"
        
        duration = int(duration_sora2) if model == "sora-2" else int(duration_sora2pro)
        
        payload = {
            "model": model,
            "orientation": orientation,
            "prompt": prompt,
            "size": size,
            "duration": duration,
            "watermark": bool(watermark),
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            raise_for_bad_status(resp, "Sora text2video failed")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"创建视频失败: {str(e)}")

        task_id = data.get("id") or data.get("task_id") or ""
        status = data.get("status") or ""
        status_update_time = int(data.get("status_update_time") or 0)

        if not task_id:
            raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

        return (task_id, status, status_update_time)


class SoraCreateCharacter:
    """创建 Sora 角色"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "timestamps": ("STRING", {"default": "1,3", "tooltip": "时间范围(秒)，例如 '1,3' 表示1-3秒，范围差值最大3秒最小1秒"}),
            },
            "optional": {
                "url": ("STRING", {"default": "", "multiline": False, "tooltip": "视频URL（url和from_task二选一）"}),
                "from_task": ("STRING", {"default": "", "tooltip": "任务ID（url和from_task二选一）"}),
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "timeout": ("INT", {"default": 60, "min": 5, "max": 300, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("角色ID", "角色名称", "角色主页", "角色头像URL")
    FUNCTION = "create_character"
    CATEGORY = "KuAi/Sora2"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "timestamps": "时间范围",
            "url": "视频URL",
            "from_task": "任务ID",
            "api_base": "API地址",
            "api_key": "API密钥",
            "timeout": "超时",
        }

    def create_character(self, timestamps, url="", from_task="", api_base="https://api.kuai.host", api_key="", timeout=60):
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/sora/v1/characters"

        if not url and not from_task:
            raise RuntimeError("请提供视频URL或任务ID（二选一）")

        if url and from_task:
            raise RuntimeError("url和from_task只能提供一个")

        payload = {
            "timestamps": timestamps,
        }

        if url:
            payload["url"] = url
        if from_task:
            payload["from_task"] = from_task

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            raise_for_bad_status(resp, "Sora create character failed")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"创建角色失败: {str(e)}")

        character_id = data.get("id", "")
        username = data.get("username", "")
        permalink = data.get("permalink", "")
        profile_picture_url = data.get("profile_picture_url", "")

        if not character_id:
            raise RuntimeError(f"创建角色响应缺少角色ID: {json.dumps(data, ensure_ascii=False)}")

        print(f"[SoraCreateCharacter] 角色创建成功: {character_id} (@{username})")
        return (character_id, username, permalink, profile_picture_url)


class SoraRemixVideo:
    """编辑视频（Remix）"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_id": ("STRING", {"default": "", "tooltip": "已完成的视频ID（例如：video_xxx）"}),
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "编辑提示词"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("新任务ID", "状态", "原始视频ID")
    FUNCTION = "remix"
    CATEGORY = "KuAi/Sora2"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "video_id": "视频ID",
            "prompt": "编辑提示词",
            "api_base": "API地址",
            "api_key": "API密钥",
            "timeout": "超时",
        }

    def remix(self, video_id, prompt, api_base="https://api.kuai.host", api_key="", timeout=120):
        api_key = env_or(api_key, "KUAI_API_KEY")

        if not video_id:
            raise RuntimeError("请提供视频ID")

        if not prompt:
            raise RuntimeError("请提供编辑提示词")

        endpoint = api_base.rstrip("/") + f"/v1/videos/{video_id}/remix"

        payload = {
            "prompt": prompt,
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            raise_for_bad_status(resp, "Sora remix video failed")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"视频编辑失败: {str(e)}")

        new_task_id = data.get("id", "")
        status = data.get("status", "")
        remixed_from = data.get("remixed_from_video_id", video_id)

        if not new_task_id:
            raise RuntimeError(f"编辑响应缺少任务ID: {json.dumps(data, ensure_ascii=False)}")

        print(f"[SoraRemixVideo] 视频编辑任务创建成功: {new_task_id} (基于 {video_id})")
        return (new_task_id, status, remixed_from)


NODE_CLASS_MAPPINGS = {
    "SoraCreateVideo": SoraCreateVideo,
    "SoraQueryTask": SoraQueryTask,
    "SoraCreateAndWait": SoraCreateAndWait,
    "SoraText2Video": SoraText2Video,
    "SoraCreateCharacter": SoraCreateCharacter,
    "SoraRemixVideo": SoraRemixVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SoraCreateVideo": "🎥 创建视频任务",
    "SoraQueryTask": "🔍 查询任务状态",
    "SoraCreateAndWait": "⚡ 一键生成视频",
    "SoraText2Video": "📝 文生视频",
    "SoraCreateCharacter": "👤 创建角色",
    "SoraRemixVideo": "🎬 编辑视频",
}
