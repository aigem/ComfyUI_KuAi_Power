"""NanoBanana 批量处理节点"""

import json
import os
import time
import torch
import numpy as np
from PIL import Image

from ..Sora2.kuai_utils import env_or
from .nano_banana import NanoBananaAIO, pil_to_base64, to_pil_from_comfy


class NanoBananaBatchProcessor:
    """NanoBanana 批量图像生成处理器"""

    def __init__(self):
        self.generator = NanoBananaAIO()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_tasks": ("STRING", {"forceInput": True, "tooltip": "来自 CSV 读取器的批量任务数据"}),
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API 端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API 密钥"}),
                "output_dir": ("STRING", {"default": "./output/nanobana_batch", "tooltip": "输出目录"}),
                "delay_between_tasks": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 60.0, "step": 0.5, "tooltip": "任务间延迟(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("处理结果", "输出目录")
    FUNCTION = "process_batch"
    CATEGORY = "KuAi/NanoBanana"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "batch_tasks": "批量任务",
            "api_base": "API地址",
            "api_key": "API密钥",
            "output_dir": "输出目录",
            "delay_between_tasks": "任务间延迟",
        }

    def process_batch(self, batch_tasks, api_base="https://api.kuai.host", api_key="",
                     output_dir="./output/nanobana_batch", delay_between_tasks=2.0):
        """批量处理图像生成任务"""
        try:
            # 解析任务数据
            tasks = json.loads(batch_tasks)
            if not tasks:
                raise ValueError("没有任务需要处理")

            # 获取 API Key
            api_key = env_or(api_key, "KUAI_API_KEY")
            if not api_key:
                raise ValueError("未配置 API Key")

            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 处理结果统计
            results = {
                "total": len(tasks),
                "success": 0,
                "failed": 0,
                "errors": []
            }

            print(f"\n{'='*60}")
            print(f"[NanoBananaBatch] 开始批量处理 {len(tasks)} 个任务")
            print(f"[NanoBananaBatch] 输出目录: {output_dir}")
            print(f"{'='*60}\n")

            # 逐个处理任务
            for idx, task in enumerate(tasks, start=1):
                try:
                    print(f"\n[{idx}/{len(tasks)}] 处理任务 (行 {task.get('_row_number', '?')})")

                    # 处理单个任务
                    self._process_single_task(task, idx, api_base, api_key, output_dir)

                    results["success"] += 1
                    print(f"✓ 任务 {idx} 完成")

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"任务 {idx} (行 {task.get('_row_number', '?')}): {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"\033[91m✗ {error_msg}\033[0m")

                # 任务间延迟
                if idx < len(tasks) and delay_between_tasks > 0:
                    time.sleep(delay_between_tasks)

            # 生成结果报告
            report = self._generate_report(results)
            print(f"\n{'='*60}")
            print(report)
            print(f"{'='*60}\n")

            return (report, output_dir)

        except Exception as e:
            error_msg = f"批量处理失败: {str(e)}"
            print(f"\033[91m[NanoBananaBatch] {error_msg}\033[0m")
            raise RuntimeError(error_msg)

    def _process_single_task(self, task, task_idx, api_base, api_key, output_dir):
        """处理单个任务"""
        # 解析任务参数
        task_type = task.get("task_type", "").lower()
        if task_type not in ["generate", "edit", "生图", "改图"]:
            raise ValueError(f"无效的任务类型: {task_type}，必须是 'generate/生图' 或 'edit/改图'")

        # 统一任务类型
        is_edit = task_type in ["edit", "改图"]

        # 必需参数
        prompt = task.get("prompt", "").strip()
        if not prompt:
            raise ValueError("提示词 (prompt) 不能为空")

        # 可选参数（带默认值）
        model_name = task.get("model_name", "gemini-3-pro-image-preview").strip()
        system_prompt = task.get("system_prompt", "").strip()
        seed = int(task.get("seed", 0))
        aspect_ratio = task.get("aspect_ratio", "1:1").strip()
        image_size = task.get("image_size", "2K").strip()
        temperature = float(task.get("temperature", 1.0))
        use_search = task.get("use_search", "true").lower() in ["true", "1", "yes"]
        output_prefix = task.get("output_prefix", f"task_{task_idx}").strip()

        # 处理参考图像（改图模式）
        reference_images = []
        if is_edit:
            for i in range(1, 7):  # 最多6张参考图
                img_path = task.get(f"image_{i}", "").strip()
                if img_path:
                    # 加载本地图片
                    pil_img = self._load_image_from_path(img_path)
                    # 转换为 ComfyUI IMAGE 格式
                    img_np = np.array(pil_img).astype(np.float32) / 255.0
                    img_tensor = torch.from_numpy(img_np)[None,]
                    reference_images.append(img_tensor)

        # 调用生成器
        print(f"  模型: {model_name}")
        print(f"  提示词: {prompt[:50]}...")
        if system_prompt:
            print(f"  系统提示词: {system_prompt[:50]}...")
        if is_edit:
            print(f"  参考图数量: {len(reference_images)}")

        # 准备参数
        kwargs = {
            "model_name": model_name,
            "prompt": prompt,
            "image_count": 1,
            "use_search": use_search,
            "seed": seed,
            "system_prompt": system_prompt,
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
            "temperature": temperature,
            "api_base": api_base,
            "api_key": api_key,
            "timeout": 180,
        }

        # 添加参考图像
        for i, img_tensor in enumerate(reference_images, start=1):
            kwargs[f"image_{i}"] = img_tensor

        # 生成图像
        image_tensor, thinking, grounding = self.generator.generate_unified(**kwargs)

        # 保存图像
        output_path = self._save_image(image_tensor, output_dir, output_prefix)
        print(f"  保存到: {output_path}")

        # 保存元数据
        metadata = {
            "task_type": task_type,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model_name": model_name,
            "seed": seed,
            "thinking": thinking,
            "grounding": grounding,
        }
        metadata_path = output_path.replace(".png", "_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _load_image_from_path(self, img_path):
        """从本地路径加载图片"""
        # 处理路径（支持相对路径和绝对路径）
        img_path = os.path.expanduser(img_path)  # 展开 ~ 符号
        img_path = os.path.abspath(img_path)  # 转换为绝对路径

        if not os.path.exists(img_path):
            raise FileNotFoundError(f"图片文件不存在: {img_path}")

        # 加载图片
        pil_img = Image.open(img_path)

        # 转换为 RGB（如果是 RGBA 或其他格式）
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        return pil_img

    def _save_image(self, image_tensor, output_dir, prefix):
        """保存图像到文件"""
        # 转换 tensor 到 PIL
        if isinstance(image_tensor, torch.Tensor):
            # 假设 tensor 格式是 [B, H, W, C]，取第一张
            img_np = image_tensor[0].cpu().numpy()
            img_np = (img_np * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)
        else:
            raise ValueError("不支持的图像格式")

        # 生成文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)

        # 保存图片
        pil_img.save(output_path, "PNG")

        return output_path

    def _generate_report(self, results):
        """生成处理结果报告"""
        lines = [
            "\n批量处理完成",
            f"总任务数: {results['total']}",
            f"成功: {results['success']}",
            f"失败: {results['failed']}",
        ]

        if results['errors']:
            lines.append("\n失败任务详情:")
            for error in results['errors']:
                lines.append(f"  - {error}")

        return "\n".join(lines)


NODE_CLASS_MAPPINGS = {
    "NanoBananaBatchProcessor": NanoBananaBatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBananaBatchProcessor": "NanoBanana批量处理器",
}
