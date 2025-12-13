# NanoBanana API 参数修复报告

## 修复日期
2025-12-13

## 问题描述

用户报告在 ComfyUI 中选择 4K 和 16:9 参数后，生成的图像实际分辨率仍然是 1376x768（1K），而不是预期的 5504x3072（4K）。

## 根本原因分析

经过排查和测试，发现了三个关键问题：

### 1. 种子值范围错误
**问题**: 使用了 UINT64 范围（0 - 18446744073709551615），超出了 Gemini API 的 INT32 要求。

**错误示例**:
```
Invalid value at 'generation_config.seed' (TYPE_INT32), 459318242873821
```

**原因**: Gemini API 要求种子值必须是 INT32 类型（最大值 2147483647）。

### 2. 参数命名格式错误
**问题**: 使用了 Python 风格的 snake_case 命名，而 Gemini REST API 要求 camelCase。

**错误代码**:
```python
"imageConfig": {
    "aspect_ratio": "16:9",  # ❌ 错误
    "image_size": "4K"       # ❌ 错误
}
```

**正确代码**:
```python
"imageConfig": {
    "aspectRatio": "16:9",   # ✅ 正确
    "imageSize": "4K"        # ✅ 正确
}
```

### 3. 参数结构位置错误
**问题**: `imageConfig` 被放置在与 `generationConfig` 平级的位置，而不是作为其子对象。

**错误结构**:
```json
{
  "generationConfig": { ... },
  "imageConfig": { ... }     // ❌ 错误：平级
}
```

**正确结构**:
```json
{
  "generationConfig": {
    "temperature": 1.0,
    "seed": 12345,
    "imageConfig": {         // ✅ 正确：嵌套
      "aspectRatio": "16:9",
      "imageSize": "4K"
    }
  }
}
```

## 修复内容

### 修复 1: 种子值范围限制

**文件**: `nodes/NanoBanana/nano_banana.py`

**修改位置**:
- 第 50 行 (NanoBananaAIO)
- 第 123 行 (NanoBananaAIO)
- 第 351 行 (NanoBananaMultiTurnChat)
- 第 416 行 (NanoBananaMultiTurnChat)

**修改内容**:
```python
# 修改前
"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, ...})
actual_seed = random.randint(1, 0xffffffffffffffff)

# 修改后
"seed": ("INT", {"default": 0, "min": 0, "max": 2147483647, ...})
actual_seed = random.randint(1, 2147483647)
```

### 修复 2 & 3: 参数命名和结构

**文件**: `nodes/NanoBanana/nano_banana.py`

**修改位置**:
- `_generate_single_image` 方法（第 176-206 行）
- `generate_multiturn_image` 方法（第 471-500 行）

**修改内容**:
```python
# 修改前
payload = {
    "contents": [...],
    "generationConfig": {
        "temperature": float(temperature),
        "seed": int(seed)
    },
    "imageConfig": {                    # ❌ 错误位置
        "aspect_ratio": aspect_ratio,   # ❌ 错误命名
        "image_size": image_size         # ❌ 错误命名
    }
}

# 修改后
generation_config = {
    "temperature": float(temperature),
    "seed": int(seed),
    "imageConfig": {                    # ✅ 正确位置
        "aspectRatio": aspect_ratio,    # ✅ 正确命名
        "imageSize": image_size          # ✅ 正确命名
    }
}

payload = {
    "contents": [...],
    "generationConfig": generation_config
}
```

## 测试验证

### 测试环境
- API Base: `https://api.kuai.host`
- 模型: `gemini-3-pro-image-preview`
- 测试日期: 2025-12-13

### 测试结果

| 配置 | 宽高比 | 实际分辨率 | 状态 |
|------|--------|-----------|------|
| 1K | 16:9 | 1376 x 768 | ✅ 通过 |
| 2K | 16:9 | 2752 x 1536 | ✅ 通过 |
| 4K | 16:9 | 5504 x 3072 | ✅ 通过 |

### 分辨率倍数关系

- **1K**: 1376 x 768（基准）
- **2K**: 2752 x 1536（2倍）
- **4K**: 5504 x 3072（4倍）

### 测试代码

```python
import requests
import json

api_key = 'YOUR_API_KEY'
api_base = 'https://api.kuai.host'
model_name = 'gemini-3-pro-image-preview'
endpoint = f'{api_base}/v1beta/models/{model_name}:generateContent'

payload = {
    'contents': [{'parts': [{'text': 'A simple geometric shape'}]}],
    'generationConfig': {
        'temperature': 1.0,
        'response_modalities': ['TEXT', 'IMAGE'],
        'seed': 12345,
        'imageConfig': {
            'aspectRatio': '16:9',
            'imageSize': '4K'
        }
    }
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
# 状态码: 200 ✅
# 实际分辨率: 5504 x 3072 ✅
```

## 完整的 API 格式参考

### gemini-3-pro-image-preview

```json
{
  "contents": [
    {
      "parts": [
        {"text": "prompt text"}
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "response_modalities": ["TEXT", "IMAGE"],
    "seed": 12345,
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "4K"
    }
  },
  "systemInstruction": {
    "parts": [{"text": "system prompt"}]
  },
  "tools": [{"googleSearch": {}}]
}
```

### gemini-2.5-flash-image

```json
{
  "contents": [
    {
      "parts": [
        {"text": "prompt text"}
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "response_modalities": ["TEXT", "IMAGE"],
    "seed": 12345,
    "imageConfig": {
      "aspectRatio": "16:9"
    }
  },
  "systemInstruction": {
    "parts": [{"text": "system prompt"}]
  }
}
```

**注意**: `gemini-2.5-flash-image` 不支持 `imageSize` 参数和 `googleSearch` 工具。

## 支持的参数值

### aspectRatio
- `"1:1"` - 正方形
- `"2:3"` - 竖版
- `"3:2"` - 横版
- `"3:4"` - 竖版
- `"4:3"` - 横版
- `"4:5"` - 竖版
- `"5:4"` - 横版
- `"9:16"` - 手机竖屏
- `"16:9"` - 宽屏
- `"21:9"` - 超宽屏

### imageSize (仅 gemini-3-pro-image-preview)
- `"1K"` - 标清（1376 x 768 @ 16:9）
- `"2K"` - 高清（2752 x 1536 @ 16:9）
- `"4K"` - 超高清（5504 x 3072 @ 16:9）

**注意**: 必须使用大写 `K`。

### seed
- 范围: 0 - 2147483647 (INT32)
- 0 表示随机种子

## 使用说明

### 在 ComfyUI 中使用

1. **重启 ComfyUI** 以加载更新后的代码
2. 添加 `NanoBananaAIO` 或 `NanoBananaMultiTurnChat` 节点
3. 选择模型: `gemini-3-pro-image-preview`
4. 设置参数:
   - `aspect_ratio`: 选择 `16:9`
   - `image_size`: 选择 `4K`
   - `seed`: 输入固定值或保持 `0`（随机）
5. 运行生成

### 预期结果

- **1K**: 生成 1376 x 768 像素的图像
- **2K**: 生成 2752 x 1536 像素的图像
- **4K**: 生成 5504 x 3072 像素的图像

## 常见问题

### Q1: 为什么之前 4K 不生效？
**A**: 因为 `imageConfig` 的位置和命名格式都不正确，API 服务器忽略了这些参数，使用了默认的 1K 分辨率。

### Q2: 种子值超出范围会怎样？
**A**: API 会返回 400 错误：`Invalid value at 'generation_config.seed' (TYPE_INT32)`

### Q3: gemini-2.5-flash-image 支持 4K 吗？
**A**: 不支持。该模型只支持 `aspectRatio` 参数，不支持 `imageSize` 参数。

### Q4: 如何验证生成的图像分辨率？
**A**: 在 ComfyUI 中查看图像属性，或使用图像查看器检查分辨率。

## 参考文档

- [Google Gemini API - Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini API Reference](https://ai.google.dev/api/rest)

## 更新日志

### 2025-12-13
- ✅ 修复种子值范围（UINT64 → INT32）
- ✅ 修复参数命名格式（snake_case → camelCase）
- ✅ 修复参数结构位置（imageConfig 移入 generationConfig）
- ✅ 通过实际 API 测试验证所有分辨率
- ✅ 创建完整的修复文档

---

**文档版本**: 1.0
**最后更新**: 2025-12-13
**状态**: ✅ 所有问题已修复并验证通过
