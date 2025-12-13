# Nano Banana API 规范

## 概述

本文档定义了 kuai.host 后端需要实现的 Nano Banana API 端点规范，用于支持 ComfyUI_KuAi_Power 插件中的 Nano Banana 节点。

---

## 认证

所有 API 请求都需要在 HTTP 头中包含 API 密钥：

```
Authorization: Bearer {api_key}
Content-Type: application/json
```

---

## API 端点

### 1. 图像生成 API

**端点**: `POST /v1/images/generate`

**功能**: 生成单张图像，支持文生图、图生图、搜索增强等功能

#### 请求格式

```json
{
  "model": "gemini-3-pro-image-preview",
  "prompt": "A futuristic nano banana dish",
  "aspect_ratio": "1:1",
  "image_size": "2K",
  "temperature": 1.0,
  "use_search": true,
  "reference_images": [
    "base64_encoded_image_1",
    "base64_encoded_image_2"
  ]
}
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称，可选值: `gemini-3-pro-image-preview`, `gemini-2.0-flash-exp` |
| `prompt` | string | 是 | 图像生成提示词 |
| `aspect_ratio` | string | 是 | 宽高比，可选值: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `image_size` | string | 是 | 图像尺寸，可选值: `1K`, `2K`, `4K` |
| `temperature` | float | 是 | 生成温度，范围 0.0-2.0 |
| `use_search` | boolean | 是 | 是否启用 Google 搜索增强 |
| `reference_images` | array[string] | 否 | 参考图像的 base64 编码数组（最多 6 张） |

#### 响应格式

```json
{
  "image_base64": "base64_encoded_generated_image",
  "thinking": "AI 的思考过程文本（如果可用）",
  "grounding_sources": "引用来源信息（格式化的 markdown）"
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `image_base64` | string | 生成图像的 base64 编码（PNG 或 JPEG 格式） |
| `thinking` | string | AI 的思考过程文本（仅 Vertex AI 可用） |
| `grounding_sources` | string | 引用来源信息，包含搜索查询、引用块等 |

#### 后端实现要点

1. **解码参考图像**:
   ```python
   import base64
   from PIL import Image
   import io

   reference_pil_images = []
   for base64_str in reference_images:
       image_bytes = base64.b64decode(base64_str)
       pil_image = Image.open(io.BytesIO(image_bytes))
       reference_pil_images.append(pil_image)
   ```

2. **调用 Google Gemini API**:
   ```python
   from google import genai
   from google.genai import types

   client = genai.Client(api_key=GOOGLE_API_KEY)
   # 或使用 Vertex AI
   # client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

   contents = [prompt] + reference_pil_images

   config = types.GenerateContentConfig(
       response_modalities=["TEXT", "IMAGE"],
       image_config=types.ImageConfig(
           aspect_ratio=aspect_ratio,
           image_size=image_size
       ),
       temperature=temperature,
       automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
   )

   if use_search:
       config.tools = [types.Tool(google_search=types.GoogleSearch())]

   response = client.models.generate_content(
       model=model,
       contents=contents,
       config=config
   )
   ```

3. **提取响应数据**:
   ```python
   # 提取图像
   image_bytes = None
   text_response = ""

   for part in response.candidates[0].content.parts:
       if part.inline_data:
           image_bytes = part.inline_data.data
       elif part.text:
           text_response += part.text

   # 编码为 base64
   image_base64 = base64.b64encode(image_bytes).decode('utf-8')

   # 提取 grounding 信息
   grounding_sources = extract_grounding_data(response)
   ```

4. **返回响应**:
   ```python
   return {
       "image_base64": image_base64,
       "thinking": text_response,
       "grounding_sources": grounding_sources
   }
   ```

---

### 2. 多轮对话图像生成 API

**端点**: `POST /v1/chat/images`

**功能**: 支持多轮对话的图像生成和编辑，保持对话上下文

#### 请求格式

```json
{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": "Create an image of a clear perfume bottle sitting on a vanity",
      "image_base64": "base64_encoded_initial_image"
    },
    {
      "role": "assistant",
      "content": "I've created an image of a clear perfume bottle on a vanity",
      "image_base64": "base64_encoded_generated_image_1"
    },
    {
      "role": "user",
      "content": "Make the bottle more elegant and add soft lighting",
      "image_base64": "base64_encoded_generated_image_1"
    }
  ],
  "aspect_ratio": "1:1",
  "image_size": "2K",
  "temperature": 1.0
}
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称 |
| `messages` | array[object] | 是 | 对话历史消息数组 |
| `aspect_ratio` | string | 是 | 宽高比 |
| `image_size` | string | 是 | 图像尺寸 |
| `temperature` | float | 是 | 生成温度 |

#### 消息对象格式

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `role` | string | 是 | 角色，可选值: `user`, `assistant` |
| `content` | string | 是 | 消息内容 |
| `image_base64` | string | 否 | 关联的图像 base64 编码 |

#### 响应格式

```json
{
  "image_base64": "base64_encoded_generated_image",
  "response": "AI 的响应文本",
  "metadata": "元数据信息（finish_reason, safety_ratings 等）"
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `image_base64` | string | 生成图像的 base64 编码 |
| `response` | string | AI 的响应文本 |
| `metadata` | string | 元数据信息 |

#### 后端实现要点

1. **创建 Chat Session**:
   ```python
   from google import genai
   from google.genai import types

   client = genai.Client(api_key=GOOGLE_API_KEY)

   config = types.GenerateContentConfig(
       response_modalities=['TEXT', 'IMAGE'],
       image_config=types.ImageConfig(
           aspect_ratio=aspect_ratio,
           image_size=image_size
       ),
       temperature=temperature,
       automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
   )

   chat = client.chats.create(
       model=model,
       config=config
   )
   ```

2. **重放历史消息**（如果需要）:
   ```python
   # 注意：Google Gemini Chat API 可能不需要手动重放历史
   # 如果需要，可以逐条发送历史消息
   for msg in messages[:-1]:  # 除了最后一条
       contents = [msg["content"]]
       if "image_base64" in msg:
           image_bytes = base64.b64decode(msg["image_base64"])
           pil_image = Image.open(io.BytesIO(image_bytes))
           contents.insert(0, pil_image)

       # 发送但不处理响应（仅用于建立上下文）
       chat.send_message(message=contents)
   ```

3. **发送当前消息**:
   ```python
   current_msg = messages[-1]
   contents = [current_msg["content"]]

   if "image_base64" in current_msg:
       image_bytes = base64.b64decode(current_msg["image_base64"])
       pil_image = Image.open(io.BytesIO(image_bytes))
       contents.insert(0, pil_image)

   response = chat.send_message(message=contents)
   ```

4. **提取响应**:
   ```python
   image_bytes = None
   text_response = ""

   for part in response.candidates[0].content.parts:
       if hasattr(part, 'inline_data') and part.inline_data:
           image_bytes = part.inline_data.data
       elif hasattr(part, 'text') and part.text:
           text_response += part.text

   image_base64 = base64.b64encode(image_bytes).decode('utf-8')

   # 提取元数据
   metadata = f"Finish Reason: {response.candidates[0].finish_reason}"
   if hasattr(response.candidates[0], 'safety_ratings'):
       # 添加安全评级信息
       pass
   ```

5. **返回响应**:
   ```python
   return {
       "image_base64": image_base64,
       "response": text_response,
       "metadata": metadata
   }
   ```

---

## Grounding 信息提取

### 详细提取方法

```python
def extract_grounding_data(response):
    """从 Gemini 响应中提取 grounding 信息"""
    try:
        candidate = response.candidates[0]
        grounding_metadata = candidate.grounding_metadata
        lines = []

        # 提取文本内容
        text_content = ""
        for part in candidate.content.parts:
            if hasattr(part, 'text') and part.text:
                text_content += part.text

        if text_content:
            lines.append(text_content)

        lines.append("\n\n----\n## Grounding Sources\n")

        # 提取 grounding supports（引用支持）
        if grounding_metadata and hasattr(grounding_metadata, 'grounding_supports'):
            ENCODING = "utf-8"
            text_bytes = text_content.encode(ENCODING) if text_content else b""
            last_byte_index = 0

            for support in grounding_metadata.grounding_supports:
                if text_bytes:
                    lines.append(
                        text_bytes[last_byte_index : support.segment.end_index].decode(ENCODING)
                    )

                    # 生成引用脚注 [1][2]
                    footnotes = "".join([f"[{i + 1}]" for i in support.grounding_chunk_indices])
                    lines.append(f" {footnotes}")

                    last_byte_index = support.segment.end_index

            if text_bytes and last_byte_index < len(text_bytes):
                lines.append(text_bytes[last_byte_index:].decode(ENCODING))

        # 提取 grounding chunks（引用块）
        if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks'):
            lines.append("\n### Grounding Chunks\n")
            for i, chunk in enumerate(grounding_metadata.grounding_chunks, start=1):
                context = chunk.web or chunk.retrieved_context or chunk.maps
                if not context:
                    continue

                uri = context.uri
                title = context.title or "Source"

                # 转换 GCS URI 为 HTTPS URL
                if uri:
                    uri = uri.replace(" ", "%20")
                    if uri.startswith("gs://"):
                        uri = uri.replace("gs://", "https://storage.googleapis.com/", 1)

                lines.append(f"{i}. [{title}]({uri})\n")

                if hasattr(context, "place_id") and context.place_id:
                    lines.append(f"    - Place ID: `{context.place_id}`\n\n")
                if hasattr(context, "text") and context.text:
                    lines.append(f"{context.text}\n\n")

        # 提取搜索查询
        if grounding_metadata and hasattr(grounding_metadata, 'web_search_queries'):
            lines.append(f"\n**Web Search Queries:** {grounding_metadata.web_search_queries}\n")
            if hasattr(grounding_metadata, 'search_entry_point'):
                lines.append(f"\n**Search Entry Point:**\n{grounding_metadata.search_entry_point.rendered_content}\n")
        elif grounding_metadata and hasattr(grounding_metadata, 'retrieval_queries'):
            lines.append(f"\n**Retrieval Queries:** {grounding_metadata.retrieval_queries}\n")

        return "".join(lines)

    except Exception as e:
        # 如果提取失败，至少返回文本内容
        candidate = response.candidates[0]
        text_content = ""
        for part in candidate.content.parts:
            if hasattr(part, 'text') and part.text:
                text_content += part.text
        return text_content + f"\n\nGrounding information not available: {str(e)}"
```

---

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息"
  }
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| `INVALID_API_KEY` | 401 | API 密钥无效或缺失 |
| `INVALID_MODEL` | 400 | 不支持的模型名称 |
| `INVALID_ASPECT_RATIO` | 400 | 不支持的宽高比 |
| `INVALID_IMAGE_SIZE` | 400 | 不支持的图像尺寸 |
| `INVALID_BASE64` | 400 | base64 解码失败 |
| `TOO_MANY_IMAGES` | 400 | 参考图像数量超过限制 |
| `GENERATION_FAILED` | 500 | 图像生成失败 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超过速率限制 |
| `QUOTA_EXCEEDED` | 429 | 超过配额限制 |

---

## 性能优化建议

### 1. Base64 编码优化

```python
# 使用 JPEG 格式减小 base64 大小
def optimize_base64_size(pil_image, max_size_kb=500):
    """优化图像大小以减小 base64 编码后的大小"""
    buffer = io.BytesIO()

    # 尝试不同的质量设置
    for quality in [95, 85, 75, 65]:
        buffer.seek(0)
        buffer.truncate()
        pil_image.save(buffer, format="JPEG", quality=quality, optimize=True)

        if len(buffer.getvalue()) / 1024 <= max_size_kb:
            break

    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')
```

### 2. 缓存机制

```python
# 缓存 Gemini API 响应（相同参数）
import hashlib
import json

def get_cache_key(payload):
    """生成缓存键"""
    # 排除 reference_images 以避免过大的键
    cache_data = {k: v for k, v in payload.items() if k != 'reference_images'}
    return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
```

### 3. 并发处理

```python
# 使用异步处理提高吞吐量
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def generate_image_async(payload):
    """异步图像生成"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            generate_image_sync,
            payload
        )
    return result
```

---

## 测试用例

### 1. 基础文生图

```bash
curl -X POST https://api.kuai.host/v1/images/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "prompt": "A futuristic nano banana dish",
    "aspect_ratio": "1:1",
    "image_size": "2K",
    "temperature": 1.0,
    "use_search": false
  }'
```

### 2. 图生图

```bash
curl -X POST https://api.kuai.host/v1/images/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "prompt": "Make this image more vibrant and colorful",
    "aspect_ratio": "16:9",
    "image_size": "2K",
    "temperature": 1.0,
    "use_search": false,
    "reference_images": ["BASE64_ENCODED_IMAGE"]
  }'
```

### 3. 多轮对话

```bash
curl -X POST https://api.kuai.host/v1/chat/images \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "messages": [
      {
        "role": "user",
        "content": "Create a perfume bottle"
      },
      {
        "role": "assistant",
        "content": "Image generated",
        "image_base64": "PREVIOUS_IMAGE_BASE64"
      },
      {
        "role": "user",
        "content": "Make it more elegant",
        "image_base64": "PREVIOUS_IMAGE_BASE64"
      }
    ],
    "aspect_ratio": "1:1",
    "image_size": "2K",
    "temperature": 1.0
  }'
```

---

## 总结

### 关键要点

1. **使用 base64 编码传递图像**，避免额外的上传/下载步骤
2. **完整保留 Gemini API 的所有功能**，包括 thinking 和 grounding
3. **支持多轮对话**，正确管理对话历史和图像上下文
4. **优化性能**，使用缓存和异步处理
5. **完善错误处理**，提供清晰的错误信息

### 实现优先级

1. **P0 (必需)**: 基础图像生成 API (`/v1/images/generate`)
2. **P0 (必需)**: 多轮对话 API (`/v1/chat/images`)
3. **P1 (重要)**: Grounding 信息提取
4. **P2 (优化)**: 缓存机制
5. **P2 (优化)**: 性能优化

---

**文档版本**: 1.0
**最后更新**: 2025-12-13
