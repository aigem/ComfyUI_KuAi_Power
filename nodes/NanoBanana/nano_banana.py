"""Nano Banana 节点实现 - 基于 kuai.host API (使用 base64 图片传递)"""

import io
import json
import time
import base64
import random
import torch
import numpy as np
import requests
from PIL import Image

from ..Sora2.kuai_utils import (
    env_or,
    to_pil_from_comfy,
    http_headers_json,
    raise_for_bad_status
)


def pil_to_base64(pil_image: Image.Image, format: str = "PNG") -> str:
    """将 PIL 图像转换为 base64 字符串"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def base64_to_pil(base64_str: str) -> Image.Image:
    """将 base64 字符串转换为 PIL 图像"""
    image_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


class NanoBananaAIO:
    """Nano Banana Pro 多功能节点：支持单/多图生成、grounding、搜索和 thinking 能力"""

    def __init__(self):
        self._preview_warning_shown = False

    @classmethod
    def INPUT_TYPES(cls):
        model_list = ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0], "tooltip": "选择 Gemini 模型"}),
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic nano banana dish", "tooltip": "图像生成提示词"}),
                "image_count": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1, "tooltip": "生成图像数量"}),
                "use_search": ("BOOLEAN", {"default": True, "tooltip": "启用网络搜索增强"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "随机种子值，0为随机"}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "系统提示词，用于指导 AI 的行为和风格"}),
                "image_1": ("IMAGE", {"tooltip": "参考图1"}),
                "image_2": ("IMAGE", {"tooltip": "参考图2"}),
                "image_3": ("IMAGE", {"tooltip": "参考图3"}),
                "image_4": ("IMAGE", {"tooltip": "参考图4"}),
                "image_5": ("IMAGE", {"tooltip": "参考图5"}),
                "image_6": ("IMAGE", {"tooltip": "参考图6"}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                                {"default": "1:1", "tooltip": "图像宽高比"}),
                "image_size": (["1K", "2K", "4K"], {"default": "2K", "tooltip": "图像尺寸,只对gemini-3-pro-image-preview起作用"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1, "tooltip": "生成温度"}),
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API 端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API 密钥"}),
                "timeout": ("INT", {"default": 180, "min": 60, "max": 900, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("图像", "思考过程", "引用来源")
    FUNCTION = "generate_unified"
    CATEGORY = "KuAi/NanoBanana"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "model_name": "模型",
            "prompt": "提示词",
            "image_count": "图像数量",
            "use_search": "启用搜索",
            "seed": "种子值",
            "system_prompt": "系统提示词",
            "image_1": "参考图1",
            "image_2": "参考图2",
            "image_3": "参考图3",
            "image_4": "参考图4",
            "image_5": "参考图5",
            "image_6": "参考图6",
            "aspect_ratio": "宽高比",
            "image_size": "尺寸",
            "temperature": "温度",
            "api_base": "API地址",
            "api_key": "API密钥",
            "timeout": "超时",
        }

    def _handle_error(self, message):
        """统一错误处理"""
        print(f"\033[91m[NanoBanana] 错误: {message}\033[0m")
        return (torch.zeros(1, 64, 64, 3), "", "")

    def generate_unified(self, model_name, prompt, image_count=1, use_search=True, seed=0,
                        system_prompt="", image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, image_6=None,
                        aspect_ratio="1:1", image_size="2K", temperature=1.0,
                        api_base="https://api.kuai.host", api_key="", timeout=120):
        """统一生成接口"""
        try:
            # 验证参数
            if not prompt or prompt.strip() == "":
                return self._handle_error("提示词不能为空")

            if image_count < 1 or image_count > 10:
                return self._handle_error("图像数量必须在 1-10 之间")

            # 获取 API Key
            api_key = env_or(api_key, "KUAI_API_KEY")
            if not api_key:
                return self._handle_error("未配置 API Key，请设置 KUAI_API_KEY 环境变量或在节点中填写")

            # 处理种子值：0表示随机
            if seed == 0:
                actual_seed = random.randint(1, 0xffffffffffffffff)
                print(f"[NanoBanana] 使用随机种子: {actual_seed}")
            else:
                actual_seed = seed
                print(f"[NanoBanana] 使用固定种子: {actual_seed}")

            # 准备参考图像（转换为 base64）
            reference_images_base64 = []
            for img_tensor in [image_1, image_2, image_3, image_4, image_5, image_6]:
                if img_tensor is not None:
                    try:
                        pil_img = to_pil_from_comfy(img_tensor)
                        base64_str = pil_to_base64(pil_img, format="JPEG")
                        reference_images_base64.append(base64_str)
                    except Exception as e:
                        print(f"[NanoBanana] 警告: 转换参考图失败: {e}")

            # 根据图像数量选择生成方式
            if image_count == 1:
                return self._generate_single_image(
                    api_base, api_key, model_name, prompt, system_prompt, reference_images_base64,
                    aspect_ratio, image_size, temperature, use_search, actual_seed, timeout
                )
            else:
                return self._generate_multiple_images(
                    api_base, api_key, model_name, prompt, system_prompt, image_count, reference_images_base64,
                    aspect_ratio, image_size, temperature, use_search, actual_seed, timeout
                )

        except Exception as e:
            return self._handle_error(f"生成失败: {str(e)}")

    def _generate_single_image(self, api_base, api_key, model_name, prompt, system_prompt, reference_images_base64,
                               aspect_ratio, image_size, temperature, use_search, seed, timeout):
        """生成单张图像"""
        # 使用 Google Gemini API 格式: /v1beta/models/{model}:generateContent
        endpoint = api_base.rstrip("/") + f"/v1beta/models/{model_name}:generateContent"

        # 构建 contents（Gemini API 格式）
        contents = []

        # 添加参考图像（如果有）
        for img_base64 in reference_images_base64:
            contents.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_base64
                }
            })

        # 添加文本提示词
        contents.append({"text": prompt})

        # 构建 generation_config
        generation_config = {
            "temperature": float(temperature),
            "response_modalities": ["TEXT", "IMAGE"],
            "seed": int(seed)
        }

        # 构建请求 payload（Gemini API 格式）
        payload = {
            "contents": [{"parts": contents}],
            "generationConfig": generation_config
        }

        # 添加系统提示词（如果提供）
        if system_prompt and system_prompt.strip():
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt.strip()}]
            }

        # 根据模型类型添加不同的配置
        if model_name == "gemini-3-pro-image-preview":
            # gemini-3-pro-image-preview 支持 imageConfig
            payload["imageConfig"] = {
                "aspect_ratio": aspect_ratio,
                "image_size": image_size
            }
        elif model_name == "gemini-2.5-flash-image":
            # gemini-2.5-flash-image 使用不同的配置方式
            # 将 aspect_ratio 添加到 generation_config 中
            generation_config["aspect_ratio"] = aspect_ratio
            # gemini-2.5-flash-image 不支持 image_size 参数
            payload["generationConfig"] = generation_config

        # 如果启用搜索，添加 tools（仅 gemini-3-pro-image-preview 支持）
        if use_search and model_name == "gemini-3-pro-image-preview":
            payload["tools"] = [{"googleSearch": {}}]

        try:
            resp = requests.post(
                endpoint,
                headers=http_headers_json(api_key),
                data=json.dumps(payload),
                timeout=int(timeout)
            )
            raise_for_bad_status(resp, "Nano Banana 生成失败")
            data = resp.json()
        except Exception as e:
            return self._handle_error(f"API 调用失败: {str(e)}")

        # 解析 Gemini API 响应格式
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                return self._handle_error("API 返回的 candidates 为空")

            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            # 提取图像和文本
            image_base64 = None
            thinking = ""

            for part in parts:
                # 检查 inline_data（图像）
                if "inlineData" in part or "inline_data" in part:
                    inline_data = part.get("inlineData") or part.get("inline_data")
                    image_base64 = inline_data.get("data")
                # 检查 text（文本）
                elif "text" in part:
                    thinking += part.get("text", "")

            if not image_base64:
                return self._handle_error(f"响应中缺少图像数据: {json.dumps(data, ensure_ascii=False)}")

            # 提取 grounding 信息
            grounding_metadata = candidate.get("groundingMetadata", )
            grounding_sources = self._extract_grounding_info(grounding_metadata, thinking)

        except Exception as e:
            return self._handle_error(f"解析响应失败: {str(e)}")

        # 解码 base64 图像
        try:
            pil_image = base64_to_pil(image_base64)
        except Exception as e:
            return self._handle_error(f"解码图像失败: {str(e)}")

        # 转换为 tensor
        image_np = np.array(pil_image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]

        return (image_tensor, thinking, grounding_sources)

    def _generate_multiple_images(self, api_base, api_key, model_name, prompt, system_prompt, image_count, reference_images_base64,
                                  aspect_ratio, image_size, temperature, use_search, seed, timeout):
        """生成多张图像"""
        generated_images = []
        all_thinking = []
        all_grounding = []

        for i in range(image_count):
            # 为每张图像添加序号和不同的种子值
            current_prompt = f"{prompt} (Image {i+1} of {image_count})"
            current_seed = seed + i  # 每张图像使用不同的种子值

            image_tensor, thinking, grounding = self._generate_single_image(
                api_base, api_key, model_name, current_prompt, system_prompt, reference_images_base64,
                aspect_ratio, image_size, temperature, use_search, current_seed, timeout
            )

            # 检查是否生成成功
            if image_tensor.shape[1] == 64 and image_tensor.shape[2] == 64:
                # 这是错误占位符，停止生成
                break

            generated_images.append(image_tensor)
            all_thinking.append(thinking)
            all_grounding.append(grounding)

            # 避免请求过快
            if i < image_count - 1:
                time.sleep(1)

        if not generated_images:
            return self._handle_error("未能生成任何图像")

        # 合并结果
        combined_images = torch.cat(generated_images, dim=0)
        combined_thinking = "\n\n---\n\n".join(all_thinking)
        combined_grounding = "\n\n---\n\n".join(all_grounding)

        return (combined_images, combined_thinking, combined_grounding)

    def _extract_grounding_info(self, grounding_metadata, text_content):
        """提取 grounding 信息"""
        if not grounding_metadata:
            return text_content

        lines = [text_content, "\n\n----\n## Grounding Sources\n"]

        # 提取搜索查询
        web_search_queries = grounding_metadata.get("webSearchQueries", [])
        if web_search_queries:
            lines.append(f"\n**Web Search Queries:** {', '.join(web_search_queries)}\n")

        # 提取 grounding chunks
        grounding_chunks = grounding_metadata.get("groundingChunks", [])
        if grounding_chunks:
            lines.append("\n### Sources\n")
            for i, chunk in enumerate(grounding_chunks, start=1):
                web = chunk.get("web", {})
                uri = web.get("uri", "")
                title = web.get("title", "Source")
                lines.append(f"{i}. [{title}]({uri})\n")

        return "".join(lines)


class NanoBananaMultiTurnChat:
    """Nano Banana 多轮对话节点：支持基于对话历史的迭代图像生成和编辑"""

    def __init__(self):
        self.conversation_history = []
        self.last_image_base64 = None  # 保存上一轮生成的图像 base64
        self._preview_warning_shown = False

    @classmethod
    def INPUT_TYPES(cls):
        model_list = ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0], "tooltip": "选择 Gemini 模型"}),
                "prompt": ("STRING", {"multiline": True, "default": "Create an image of a clear perfume bottle sitting on a vanity.", "tooltip": "对话提示词"}),
                "reset_chat": ("BOOLEAN", {"default": False, "tooltip": "重置对话历史"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "随机种子值，0为随机"}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                                {"default": "1:1", "tooltip": "图像宽高比"}),
                "image_size": (["1K", "2K", "4K"], {"default": "2K", "tooltip": "图像尺寸,只对gemini-3-pro-image-preview起作用"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1, "tooltip": "生成温度"}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "系统提示词，用于指导 AI 的行为和风格"}),
                "image_input": ("IMAGE", {"tooltip": "初始参考图像"}),
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API 端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API 密钥"}),
                "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("图像", "响应文本", "元数据", "对话历史")
    FUNCTION = "generate_multiturn_image"
    CATEGORY = "KuAi/NanoBanana"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "model_name": "模型",
            "prompt": "提示词",
            "reset_chat": "重置对话",
            "seed": "种子值",
            "aspect_ratio": "宽高比",
            "image_size": "尺寸",
            "temperature": "温度",
            "system_prompt": "系统提示词",
            "image_input": "参考图",
            "api_base": "API地址",
            "api_key": "API密钥",
            "timeout": "超时",
        }

    def _handle_error(self, message):
        """统一错误处理"""
        print(f"\033[91m[NanoBanana] 错误: {message}\033[0m")
        return (torch.zeros(1, 64, 64, 3), "", "", "")

    def generate_multiturn_image(self, model_name, prompt, reset_chat=False, seed=0,
                                aspect_ratio="1:1", image_size="2K", temperature=1.0,
                                system_prompt="", image_input=None, api_base="https://api.kuai.host",
                                api_key="", timeout=120):
        """多轮对话图像生成"""
        try:
            # 重置对话
            if reset_chat:
                self.conversation_history = []
                self.last_image_base64 = None
                print("[NanoBanana] 对话已重置")

            # 验证参数
            if not prompt or prompt.strip() == "":
                return self._handle_error("提示词不能为空")

            # 获取 API Key
            api_key = env_or(api_key, "KUAI_API_KEY")
            if not api_key:
                return self._handle_error("未配置 API Key")

            # 处理种子值：0表示随机
            if seed == 0:
                actual_seed = random.randint(1, 0xffffffffffffffff)
                print(f"[NanoBanana] 使用随机种子: {actual_seed}")
            else:
                actual_seed = seed
                print(f"[NanoBanana] 使用固定种子: {actual_seed}")

            # 使用 Gemini Chat API 格式
            endpoint = api_base.rstrip("/") + f"/v1beta/models/{model_name}:streamGenerateContent"

            # 构建 contents（Gemini Chat API 格式）
            contents = []

            # 添加历史对话
            for msg in self.conversation_history:
                parts = []
                # 添加图像（如果有）
                if "image_base64" in msg:
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": msg["image_base64"]
                        }
                    })
                # 添加文本
                parts.append({"text": msg["content"]})
                contents.append({"role": msg["role"], "parts": parts})

            # 添加当前消息
            current_parts = []

            # 1. 如果是首次对话且有输入图像，使用输入图像
            if len(self.conversation_history) == 0 and image_input is not None:
                try:
                    pil_img = to_pil_from_comfy(image_input)
                    image_base64 = pil_to_base64(pil_img, format="JPEG")
                    current_parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    })
                except Exception as e:
                    print(f"[NanoBanana] 警告: 转换输入图像失败: {e}")
            # 2. 如果有上一轮生成的图像，使用它
            elif self.last_image_base64:
                current_parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": self.last_image_base64
                    }
                })

            # 添加当前提示词
            current_parts.append({"text": prompt})
            contents.append({"role": "user", "parts": current_parts})

            # 构建请求 payload
            generation_config = {
                "temperature": float(temperature),
                "response_modalities": ["TEXT", "IMAGE"],
                "seed": int(actual_seed)
            }

            payload = {
                "contents": contents,
                "generationConfig": generation_config
            }

            # 添加系统提示词（如果提供）
            if system_prompt and system_prompt.strip():
                payload["systemInstruction"] = {
                    "parts": [{"text": system_prompt.strip()}]
                }

            # 根据模型类型添加不同的配置
            if model_name == "gemini-3-pro-image-preview":
                # gemini-3-pro-image-preview 支持 imageConfig
                payload["imageConfig"] = {
                    "aspect_ratio": aspect_ratio,
                    "image_size": image_size
                }
            elif model_name == "gemini-2.5-flash-image":
                # gemini-2.5-flash-image 使用不同的配置方式
                generation_config["aspect_ratio"] = aspect_ratio
                payload["generationConfig"] = generation_config

            try:
                resp = requests.post(
                    endpoint,
                    headers=http_headers_json(api_key),
                    data=json.dumps(payload),
                    timeout=int(timeout)
                )
                raise_for_bad_status(resp, "多轮对话生成失败")
                data = resp.json()
            except Exception as e:
                return self._handle_error(f"API 调用失败: {str(e)}")

            # 解析 Gemini API 响应
            try:
                candidates = data.get("candidates", [])
                if not candidates:
                    return self._handle_error("API 返回的 candidates 为空")

                candidate = candidates[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])

                # 提取图像和文本
                image_base64 = None
                response_text = ""

                for part in parts:
                    if "inlineData" in part or "inline_data" in part:
                        inline_data = part.get("inlineData") or part.get("inline_data")
                        image_base64 = inline_data.get("data")
                    elif "text" in part:
                        response_text += part.get("text", "")

                if not image_base64:
                    return self._handle_error(f"响应中缺少图像数据: {json.dumps(data, ensure_ascii=False)}")

                # 提取元数据
                finish_reason = candidate.get("finishReason", "UNKNOWN")
                metadata = f"Finish Reason: {finish_reason}"

            except Exception as e:
                return self._handle_error(f"解析响应失败: {str(e)}")

            # 解码图像
            try:
                pil_image = base64_to_pil(image_base64)
            except Exception as e:
                return self._handle_error(f"解码图像失败: {str(e)}")

            # 更新对话历史和图像状态
            # 保存用户消息
            user_msg = {"role": "user", "content": prompt}
            if len(self.conversation_history) == 0 and image_input is not None:
                pil_img = to_pil_from_comfy(image_input)
                user_msg["image_base64"] = pil_to_base64(pil_img, format="JPEG")
            elif self.last_image_base64:
                user_msg["image_base64"] = self.last_image_base64

            self.conversation_history.append(user_msg)

            # 保存助手响应
            self.conversation_history.append({
                "role": "model",  # Gemini 使用 "model" 而不是 "assistant"
                "content": response_text if response_text else "Image generated",
                "image_base64": image_base64
            })
            self.last_image_base64 = image_base64

            # 转换为 tensor
            image_np = np.array(pil_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            # 格式化对话历史（不包含 base64 数据，太长了）
            chat_history_display = []
            for msg in self.conversation_history:
                display_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                if "image_base64" in msg:
                    display_msg["has_image"] = True
                chat_history_display.append(display_msg)

            chat_history_str = json.dumps(chat_history_display, ensure_ascii=False, indent=2)

            return (image_tensor, response_text, metadata, chat_history_str)

        except Exception as e:
            return self._handle_error(f"生成失败: {str(e)}")
