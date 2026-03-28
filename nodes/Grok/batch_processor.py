"""Grok 批量视频生成处理器"""

import json
import os
import time
from ...utils.kuai_utils import env_or
from .grok import GrokCreateVideo, GrokQueryVideo


class GrokBatchProcessor:
    """Grok 批量视频生成处理器"""

    def __init__(self):
        self.creator = GrokCreateVideo()
        self.querier = GrokQueryVideo()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_tasks": ("STRING", {
                    "forceInput": True,
                    "tooltip": "来自 CSV 读取器的批量任务数据"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API 密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
                "output_dir": ("STRING", {
                    "default": "./output/grok_batch",
                    "tooltip": "输出目录（保存任务信息）"
                }),
                "delay_between_tasks": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 60.0,
                    "step": 0.5,
                    "tooltip": "任务间延迟（秒）"
                }),
            },
            "optional": {
                "wait_for_completion": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否等待所有任务完成（会花费较长时间）"
                }),
                "max_wait_time": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 1800,
                    "tooltip": "单个任务最大等待时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 10,
                    "min": 5,
                    "max": 60,
                    "tooltip": "轮询间隔（秒）"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "batch_tasks": "批量任务",
            "api_key": "API密钥",
            "output_dir": "输出目录",
            "delay_between_tasks": "任务间延迟",
            "wait_for_completion": "等待完成",
            "max_wait_time": "最大等待时间",
            "poll_interval": "轮询间隔",
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("处理结果", "输出目录")
    FUNCTION = "process_batch"
    CATEGORY = "KuAi/Grok"

    def process_batch(self, batch_tasks, api_key="", output_dir="./output/grok_batch",
                     delay_between_tasks=2.0, wait_for_completion=False,
                     max_wait_time=600, poll_interval=10):
        """批量处理视频生成任务"""
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
                "errors": [],
                "task_ids": []
            }

            print(f"\n{'='*60}")
            print(f"[GrokBatch] 开始批量处理 {len(tasks)} 个视频生成任务")
            print(f"[GrokBatch] 输出目录: {output_dir}")
            print(f"[GrokBatch] 等待完成: {'是' if wait_for_completion else '否'}")
            print(f"{'='*60}\n")

            # 逐个处理任务
            for idx, task in enumerate(tasks, start=1):
                try:
                    print(f"\n[{idx}/{len(tasks)}] 处理任务 (行 {task.get('_row_number', '?')})")

                    # 处理单个任务
                    task_info = self._process_single_task(
                        task, idx, api_key, output_dir,
                        wait_for_completion, max_wait_time, poll_interval
                    )

                    results["success"] += 1
                    results["task_ids"].append(task_info)
                    print(f"✓ 任务 {idx} 完成")

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"任务 {idx} (行 {task.get('_row_number', '?')}): {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"\033[91m✗ {error_msg}\033[0m")

                # 任务间延迟
                if idx < len(tasks) and delay_between_tasks > 0:
                    time.sleep(delay_between_tasks)

            # 保存任务列表
            tasks_file = os.path.join(output_dir, "tasks.json")
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(results["task_ids"], f, ensure_ascii=False, indent=2)
            print(f"\n[GrokBatch] 任务列表已保存到: {tasks_file}")

            # 生成结果报告
            report = self._generate_report(results)
            print(f"\n{'='*60}")
            print(report)
            print(f"{'='*60}\n")

            return (report, output_dir)

        except Exception as e:
            error_msg = f"批量处理失败: {str(e)}"
            print(f"\033[91m[GrokBatch] {error_msg}\033[0m")
            raise RuntimeError(error_msg)

    def _process_single_task(self, task, task_idx, api_key, output_dir,
                            wait_for_completion, max_wait_time, poll_interval):
        """处理单个任务"""
        # 必需参数
        prompt = task.get("prompt", "").strip()
        if not prompt:
            raise ValueError("提示词 (prompt) 不能为空")

        # 可选参数（带默认值）
        aspect_ratio = task.get("aspect_ratio", "3:2").strip()
        size = task.get("size", "1080P").strip()
        image_urls = task.get("image_urls", "").strip()
        output_prefix = task.get("output_prefix", f"task_{task_idx}").strip()

        # 验证参数
        if aspect_ratio not in ["1:1", "2:3", "3:2"]:
            raise ValueError(f"无效的宽高比: {aspect_ratio}，必须是 1:1, 2:3 或 3:2")
        if size not in ["720P", "1080P"]:
            raise ValueError(f"无效的分辨率: {size}，必须是 720P 或 1080P")

        print(f"  提示词: {prompt[:50]}...")
        print(f"  宽高比: {aspect_ratio}, 分辨率: {size}")
        if image_urls:
            print(f"  参考图片: {image_urls[:50]}...")

        # 创建任务
        task_id, status, enhanced_prompt = self.creator.create(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            size=size,
            api_key=api_key,
            image_urls=image_urls
        )

        print(f"  任务ID: {task_id}")
        print(f"  状态: {status}")

        # 任务信息
        task_info = {
            "task_id": task_id,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "size": size,
            "image_urls": image_urls,
            "output_prefix": output_prefix,
            "status": status,
            "enhanced_prompt": enhanced_prompt,
            "video_url": None,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 如果需要等待完成
        if wait_for_completion:
            print(f"  等待视频生成完成...")
            task_info = self._wait_for_completion(
                task_id, task_info, api_key, max_wait_time, poll_interval
            )

        # 保存任务信息
        task_file = os.path.join(output_dir, f"{output_prefix}_{task_id.replace(':', '_')}.json")
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_info, f, ensure_ascii=False, indent=2)

        return task_info

    def _wait_for_completion(self, task_id, task_info, api_key, max_wait_time, poll_interval):
        """等待任务完成"""
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(poll_interval)
            elapsed += poll_interval

            try:
                _, status, video_url, enhanced_prompt = self.querier.query(task_id, api_key)

                task_info["status"] = status
                task_info["video_url"] = video_url
                if enhanced_prompt:
                    task_info["enhanced_prompt"] = enhanced_prompt

                if status == "completed":
                    print(f"  ✓ 视频生成完成！")
                    print(f"  视频URL: {video_url}")
                    task_info["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    return task_info
                elif status == "failed":
                    raise RuntimeError(f"视频生成失败")

                print(f"  进行中... 已等待 {elapsed}/{max_wait_time} 秒")

            except Exception as e:
                print(f"  查询出错: {str(e)}")
                # 继续等待

        # 超时
        print(f"  ⚠ 等待超时（{max_wait_time}秒），任务仍在进行中")
        task_info["timeout"] = True
        return task_info

    def _generate_report(self, results):
        """生成处理结果报告"""
        lines = [
            "\n批量处理完成",
            f"总任务数: {results['total']}",
            f"成功: {results['success']}",
            f"失败: {results['failed']}",
        ]

        if results['task_ids']:
            lines.append(f"\n已创建的任务:")
            for task_info in results['task_ids']:
                status_icon = "✓" if task_info.get("status") == "completed" else "⏳"
                lines.append(f"  {status_icon} {task_info['task_id']}: {task_info['prompt'][:30]}...")

        if results['errors']:
            lines.append("\n失败任务详情:")
            for error in results['errors']:
                lines.append(f"  - {error}")

        return "\n".join(lines)


NODE_CLASS_MAPPINGS = {
    "GrokBatchProcessor": GrokBatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokBatchProcessor": "📦 Grok 批量处理器",
}
