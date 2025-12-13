# ComfyUI_KuAi_Power - 项目文档

## 项目概述

**ComfyUI_KuAi_Power** 是一个 ComfyUI 扩展插件，为中文用户提供 AI 视频生成和电商脚本创作功能。通过集成 api.kuai.host 的API 服务，支持 Sora2 和 Veo3 视频生成、Nano Banana 相关模型，专注于电商视频内容创作场景。

### 核心特性
- 🎬 **多模型支持**: Sora2、Veo3.1 等主流视频生成模型
- 🖼️ **图像生成**: 基于 Gemini 的 Nano Banana 多模态图像生成
- 🇨🇳 **中文界面**: 全中文节点标签和提示，降低使用门槛
- 🛍️ **电商优化**: AI 驱动的产品视频脚本生成
- 💬 **多轮对话**: 支持迭代式图像编辑和渐进式创作
- ⚡ **异步处理**: 支持任务提交和轮询查询
- 🔧 **工具集成**: 图片上传、OCR 识别等实用工具

---

## 技术架构

### 目录结构
```
ComfyUI_KuAi_Power/
├── __init__.py              # 节点自动注册系统
├── config.py                # 全局配置管理 (Pydantic)
├── requirements.txt         # Python 依赖
├── diagnose.py             # 诊断工具
├── nodes/                  # 节点实现
│   ├── Sora2/             # Sora2 视频生成节点
│   │   ├── sora2.py       # 核心节点类
│   │   ├── script_generator.py  # AI 脚本生成
│   │   └── kuai_utils.py  # 工具函数库
│   ├── Veo3/              # Veo3 视频生成节点
│   │   └── veo3.py
│   ├── NanoBanana/        # Nano Banana 图像生成节点
│   │   └── nano_banana.py # 多模态图像生成
│   └── Utils/             # 工具节点
│       ├── image_upload.py
│       └── deepseek_ocr.py
├── web/                   # 前端扩展
│   ├── kuaipower_panel.js # 快捷面板 (Ctrl+Shift+K)
│   └── video_preview.js
└── workflows/             # 预置工作流模板
```

### 依赖项
```python
requests>=2.28.0      # HTTP 请求
pillow>=9.0.0         # 图像处理
numpy>=1.21.0         # 数值计算
pydantic>=2.0.0       # 数据验证
pydantic-settings>=2.0.0  # 配置管理
```

### 配置系统
使用 Pydantic Settings 管理配置，支持 `.env` 文件和环境变量：
```python
# config.py:6-14
class Settings(BaseSettings):
    WEBHOOK_BASE_PATH: str = "/webhook"
    SECRET_TOKEN: str = ""
    HTTP_TIMEOUT: int = 30
    HTTP_RETRY: int = 0

    class Config:
        env_file = ".env"
```

**关键环境变量**:
- `KUAI_API_KEY`: API 密钥（必需）
- `HTTP_TIMEOUT`: 请求超时时间（默认 30 秒）

---

## 节点系统

### 自动注册机制
插件使用动态扫描机制自动注册所有节点（`__init__.py:11-78`）：

1. **根级模块扫描**: 加载 `nodes/*.py` 文件
2. **子目录扫描**: 递归加载 `nodes/*/` 目录
3. **类型检测**: 自动识别包含 `INPUT_TYPES` 和 `RETURN_TYPES` 的类
4. **映射注册**: 填充 `NODE_CLASS_MAPPINGS` 和 `NODE_DISPLAY_NAME_MAPPINGS`

### 节点分类

#### 1. Sora2 视频生成 (`KuAi/Sora2`)

##### SoraCreateVideo
**功能**: 创建图生视频任务
**输入参数**:
- `images` (STRING): 图片 URL 列表，逗号分隔
- `prompt` (STRING): 视频提示词
- `model` (ENUM): `sora-2` | `sora-2-pro`
- `duration_sora2` (ENUM): `10` | `15` 秒
- `duration_sora2pro` (ENUM): `15` | `25` 秒
- `orientation` (ENUM): `portrait` | `landscape`
- `size` (ENUM): `small` | `large`
- `watermark` (BOOLEAN): 是否添加水印

**返回值**: `(任务ID, 状态, 状态更新时间)`

**实现位置**: `nodes/Sora2/sora2.py:8-87`

##### SoraText2Video
**功能**: 纯文本生成视频（无参考图）
**特点**: 参数与 `SoraCreateVideo` 类似，但不需要 `images` 参数

##### SoraQueryTask
**功能**: 查询任务状态和结果
**输入**: `task_id` (STRING)
**返回**: `(任务ID, 状态, 视频URL, 状态更新时间)`

##### SoraCreateAndWait
**功能**: 一键生成视频（自动轮询等待）
**特点**:
- 提交任务后自动轮询直到完成
- 支持自定义轮询间隔和最大等待时间
- 失败时抛出详细错误信息

#### 2. Veo3 视频生成 (`KuAi/Veo3`)

##### VeoText2Video
**功能**: Veo 模型文生视频
**输入参数**:
- `prompt` (STRING): 视频提示词（支持中英文）
- `model` (ENUM): `veo3.1` | `veo3` | `veo3-fast` | `veo3-pro`
- `aspect_ratio` (ENUM): `16:9` | `9:16`
- `enhance_prompt` (BOOLEAN): 自动优化并翻译中文提示词
- `enable_upsample` (BOOLEAN): 启用超分提升质量

**实现位置**: `nodes/Veo3/veo3.py:8-60`

##### VeoImage2Video
**功能**: Veo 模型图生视频
**特点**:
- 支持 1-3 张参考图（首帧、尾帧、元素）
- 支持 `veo3.1-components` 和 `veo2-fast-components` 模型
- 参考图通过 `image_1`, `image_2`, `image_3` 可选参数传入

##### VeoQueryTask
**功能**: 查询 Veo 任务状态
**返回**: `(任务ID, 状态, 视频URL, 状态更新时间)`

##### VeoText2VideoAndWait / VeoImage2VideoAndWait
**功能**: 一键生成并等待完成
**参数**:
- `poll_interval` (INT): 轮询间隔（默认 10 秒）
- `max_wait_time` (INT): 最大等待时间（默认 600 秒）

#### 3. AI 脚本生成 (`KuAi/ScriptGenerator`)

##### ProductInfoBuilder
**功能**: 结构化产品信息
**输入参数**:
- `product_name` (STRING): 产品名称
- `product_category` (STRING): 产品类别
- `key_features` (STRING): 核心卖点（多行）
- `target_audience` (STRING): 目标受众
- `video_type` (ENUM): 产品介绍 | 促销活动 | 产品评测 | 直播卖点
- `duration` (ENUM): `10` | `15` | `25` 秒
- `language` (ENUM): 中文 | 英文 | 日语 | 韩语 | 俄语 | 中亚语言

**返回值**: `(产品信息JSON字符串)`

**实现位置**: `nodes/Sora2/script_generator.py`

##### SoraPromptFromProduct
**功能**: 使用 AI 生成专业视频脚本
**输入**:
- `product_info` (STRING): 产品信息 JSON
- `custom_requirements` (STRING): 自定义需求（可选）
- `system_prompt` (STRING): 系统提示词（可自定义）

**AI 模型**: `deepseek-v3.2-exp`
**特点**:
- 专业电商视频导演助手角色设定
- 遵循 Sora2 技术规格（时长、宽高比、音频能力）
- 输出结构化分镜脚本（时间线、镜头、灯光、音效）
- 支持多种视频风格（奢侈品、运动、日常、技术）

**系统提示词结构** (`script_generator.py:6-100`):
1. 身份认定：专业电商视频导演助手
2. 核心职能：分镜脚本创作、情感营销、技术规范
3. Sora2 技术规格：时长限制、音频能力、物理特性、已知局限
4. 工作流程：解析输入 → 确定视觉策略 → 构建时间线 → 融入旁白音效 → 输出脚本

#### 4. Nano Banana 图像生成 (`KuAi/NanoBanana`)

基于 Google Gemini 模型的多模态图像生成节点，支持文生图、图生图、多轮对话等高级功能。

##### NanoBananaAIO
**功能**: Nano Banana Pro 多功能节点 - 统一的多模态图像生成接口
**输入参数**:
- `model_name` (ENUM): `gemini-3-pro-image-preview` | `gemini-2.0-flash-exp`
- `prompt` (STRING): 图像生成提示词
- `image_count` (INT): 生成图像数量（1-10）
- `use_search` (BOOLEAN): 启用网络搜索增强
- `image_1` ~ `image_6` (IMAGE): 可选参考图像（最多 6 张）
- `aspect_ratio` (ENUM): 图像宽高比（1:1, 16:9, 9:16 等）
- `image_size` (ENUM): 图像尺寸（1K, 2K, 4K）
- `temperature` (FLOAT): 生成温度（0.0-2.0）
- `api_base` (STRING): API 端点地址（默认 `https://api.kuai.host`）
- `api_key` (STRING): API 密钥
- `timeout` (INT): 超时时间（秒）

**返回值**: `(图像, 思考过程, 引用来源)`

**特点**:
- **单/多图生成**: 通过 `image_count` 参数控制生成数量
- **参考图支持**: 最多支持 6 张参考图像
- **搜索增强**: 启用 `use_search` 可利用网络搜索提升生成质量
- **Grounding**: 自动提取引用来源和思考过程
- **灵活配置**: 支持自定义 API 端点和密钥

**实现位置**: `nodes/NanoBanana/nano_banana.py:18-217`

**使用场景**:
- 概念设计和创意探索
- 基于参考图的风格迁移
- 批量生成相似主题的图像
- 需要引用来源的专业内容创作

##### NanoBananaMultiTurnChat
**功能**: Nano Banana 多轮对话节点 - 支持基于对话历史的迭代图像生成和编辑
**输入参数**:
- `model_name` (ENUM): `gemini-3-pro-image-preview` | `gemini-2.0-flash-exp`
- `prompt` (STRING): 对话提示词
- `reset_chat` (BOOLEAN): 重置对话历史
- `aspect_ratio` (ENUM): 图像宽高比
- `image_size` (ENUM): 图像尺寸
- `temperature` (FLOAT): 生成温度
- `image_input` (IMAGE): 初始参考图像（可选）
- `api_base` (STRING): API 端点地址
- `api_key` (STRING): API 密钥
- `timeout` (INT): 超时时间

**返回值**: `(图像, 响应文本, 元数据, 对话历史)`

**特点**:
- **对话记忆**: 保持对话历史，支持迭代修改
- **上下文理解**: 基于之前生成的图像进行编辑
- **渐进式创作**: 通过多轮对话逐步完善图像
- **历史追踪**: 返回完整的对话历史记录

**实现位置**: `nodes/NanoBanana/nano_banana.py:220-445`

**使用场景**:
- 迭代式图像编辑（"把背景改成蓝色"、"添加一只猫"）
- 渐进式设计优化
- 需要多次调整的创意工作
- 基于反馈的图像改进

**工作流示例**:
```
# 首次生成
Prompt: "Create an image of a clear perfume bottle sitting on a vanity."
→ 生成初始图像

# 第二轮修改
Prompt: "Make the bottle more elegant and add soft lighting."
→ 基于第一轮图像进行修改

# 第三轮调整
Prompt: "Add some flowers in the background."
→ 继续在之前基础上调整
```

#### 5. 工具节点 (`KuAi/Utils`)

##### UploadToImageHost
**功能**: 上传图片到临时图床
**输入**:
- `image` (IMAGE): ComfyUI 图像对象
- `format` (ENUM): `jpeg` | `png` | `webp`
- `quality` (INT): 图片质量（1-100）

**返回**: `(图片URL)`
**实现位置**: `nodes/Utils/image_upload.py`

##### DeepseekOCRToPrompt
**功能**: 从图片提取文本内容
**输入**: `image` (IMAGE)
**返回**: `(提取的文本)`
**AI 模型**: `deepseek-ocr`

---

## API 集成

### 服务端点
- **主 API**: `https://api.kuai.host`

### 认证方式
```python
# nodes/Sora2/kuai_utils.py:72-76
def http_headers_json(api_key: str = "") -> dict:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    return headers
```

### API 端点

#### 1. 创建视频任务
```
POST /v1/video/create
Content-Type: application/json
Authorization: Bearer {api_key}

# Sora2 请求体
{
  "images": ["url1", "url2"],
  "model": "sora-2",
  "orientation": "portrait",
  "prompt": "视频描述",
  "size": "large",
  "duration": 10,
  "watermark": false
}

# Veo3 请求体
{
  "model": "veo3.1",
  "prompt": "视频描述",
  "aspect_ratio": "16:9",
  "enhance_prompt": true,
  "enable_upsample": true,
  "images": ["url1", "url2", "url3"]  // 可选
}

# 响应
{
  "id": "task_id",
  "status": "pending",
  "status_update_time": 1234567890
}
```

#### 2. 查询任务状态
```
GET /v1/video/query?task_id={task_id}
Authorization: Bearer {api_key}

# 响应
{
  "id": "task_id",
  "status": "completed",  // pending | processing | completed | failed
  "video_url": "https://...",
  "status_update_time": 1234567890
}
```

#### 3. AI 文本生成
```
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "model": "deepseek-v3.2-exp",
  "messages": [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户输入"}
  ],
  "temperature": 0.7,
  "max_tokens": 4000
}
```

#### 4. 图片上传
```
POST /v1/upload
Content-Type: multipart/form-data
Authorization: Bearer {api_key}

file: <binary data>

# 响应
{
  "url": "https://..."
}
```

#### 5. Nano Banana 图像生成
```
POST /v1/images/generate
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "model": "gemini-3-pro-image-preview",
  "prompt": "A futuristic nano banana dish",
  "aspect_ratio": "1:1",
  "image_size": "2K",
  "temperature": 1.0,
  "use_search": true,
  "reference_images": ["url1", "url2"]  // 可选
}

# 响应
{
  "image_url": "https://...",
  "thinking": "思考过程文本",
  "grounding_sources": "引用来源信息"
}
```

#### 6. Nano Banana 多轮对话
```
POST /v1/chat/images
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": "Create an image of a perfume bottle",
      "image_url": "https://..."  // 可选
    },
    {
      "role": "assistant",
      "content": "Image generated",
      "image_url": "https://..."
    },
    {
      "role": "user",
      "content": "Make it more elegant"
    }
  ],
  "aspect_ratio": "1:1",
  "image_size": "2K",
  "temperature": 1.0
}

# 响应
{
  "image_url": "https://...",
  "response": "响应文本",
  "metadata": "元数据信息"
}
```

### 错误处理
```python
# nodes/Sora2/kuai_utils.py
def raise_for_bad_status(resp: requests.Response, context: str = ""):
    """统一错误处理"""
    if resp.status_code >= 400:
        try:
            err_data = resp.json()
            msg = err_data.get("error", {}).get("message", resp.text)
        except:
            msg = resp.text
        raise RuntimeError(f"{context}: HTTP {resp.status_code} - {msg}")
```

---

## 工具函数库

### 核心工具 (`nodes/Sora2/kuai_utils.py`)

#### 环境变量处理
```python
# kuai_utils.py:8-12
def env_or(value: str, env_name: str) -> str:
    """优先使用参数，其次使用环境变量"""
    if value and str(value).strip():
        return value
    return os.environ.get(env_name, "").strip()
```

#### 图像转换
```python
# kuai_utils.py:14-44
def to_pil_from_comfy(image_any, index: int = 0) -> Image.Image:
    """将 ComfyUI IMAGE 转换为 PIL.Image

    支持:
    - torch.Tensor (4D/3D)
    - numpy.ndarray (4D/3D)
    - PIL.Image

    自动处理:
    - 数据类型转换 (float32 -> uint8)
    - 维度调整 (BHWC -> HWC)
    - 通道扩展 (灰度 -> RGB)
    """
```

#### 图像保存
```python
# kuai_utils.py:46-61
def save_image_to_buffer(pil: Image.Image, fmt: str, quality: int) -> io.BytesIO:
    """保存 PIL 到内存缓冲

    支持格式:
    - JPEG: 自动转 RGB，优化压缩
    - PNG: 优化压缩
    - WebP: 自动转 RGB，method=6 (最佳压缩)
    """
```

#### URL 列表处理
```python
# kuai_utils.py:63-70
def ensure_list_from_urls(urls_str: str) -> typing.List[str]:
    """将分隔的 URL 字符串拆分为列表

    支持分隔符: 逗号、分号、换行符
    自动去除空白和空字符串
    """
```

---

## 前端扩展

### 快捷面板 (`web/kuaipower_panel.js`)
**功能**: 提供快速访问节点的面板
**快捷键**: `Ctrl+Shift+K`
**特点**:
- 分类展示所有 KuAi 节点
- 点击节点名称快速添加到画布
- 支持拖拽定位

### 视频预览 (`web/video_preview.js`)
**功能**: 在 ComfyUI 界面中预览生成的视频
**支持格式**: MP4, WebM

---

## 使用场景

### 场景 1: 电商产品视频生成
```
工作流:
LoadImage (产品图)
  → UploadToImageHost (上传图床)
  → ProductInfoBuilder (构建产品信息)
  → SoraPromptFromProduct (AI 生成脚本)
  → SoraCreateAndWait (生成视频)
  → 输出视频 URL
```

**适用产品类型**:
- 奢侈品/高端产品：强调工艺细节和质感
- 运动/性能产品：展示动态效果和性能验证
- 日常/生活方式产品：情境化使用场景
- 技术/创新产品：问题-解决方案逻辑

### 场景 2: 文本直接生成视频
```
工作流:
VeoText2VideoAndWait (输入提示词)
  → 自动轮询等待
  → 输出视频 URL
```

**适用场景**:
- 概念验证
- 创意探索
- 无参考图的场景生成

### 场景 3: 图片动画化
```
工作流:
LoadImage (静态图)
  → UploadToImageHost
  → VeoImage2VideoAndWait (添加运动提示词)
  → 输出动态视频
```

**适用场景**:
- 产品展示动画
- 场景氛围营造
- 图片素材二次创作

### 场景 4: AI 图像生成与编辑
```
工作流 A: 单次生成
NanoBananaAIO
  → 输入提示词和参数
  → 生成图像 + 思考过程 + 引用来源

工作流 B: 迭代编辑
NanoBananaMultiTurnChat
  → 第一轮: "Create a perfume bottle"
  → 第二轮: "Make it more elegant"
  → 第三轮: "Add flowers in background"
  → 每轮基于上一轮结果进行修改
```

**适用场景**:
- 概念设计和创意探索
- 产品视觉设计
- 基于参考图的风格迁移
- 需要多次迭代的设计工作
- 需要引用来源的专业内容创作

### 场景 5: 批量图像生成
```
工作流:
NanoBananaAIO (设置 image_count=5)
  → 输入提示词
  → 一次性生成 5 张相似主题的图像
  → 输出图像批次
```

**适用场景**:
- 快速生成多个设计方案
- A/B 测试素材准备
- 批量创意探索

---

## 技术细节

### 异步任务处理
所有 `*AndWait` 节点使用轮询机制：
```python
# 伪代码
def create_and_wait(self, ...):
    # 1. 提交任务
    task_id, status, _ = self.create(...)

    # 2. 轮询等待
    elapsed = 0
    while elapsed < max_wait_time:
        if status in ["completed", "failed"]:
            break
        time.sleep(poll_interval)
        task_id, status, video_url, _ = self.query(task_id, ...)
        elapsed += poll_interval

    # 3. 返回结果
    if status != "completed":
        raise RuntimeError(f"任务失败或超时: {status}")
    return (task_id, status, video_url, ...)
```

### 提示词增强
Veo3 节点支持自动提示词优化：
- **中文检测**: 自动识别中文提示词
- **翻译优化**: 调用 AI 翻译并优化为英文
- **专业术语**: 添加电影制作术语和技术规范
- **可控开关**: `enhance_prompt` 参数控制是否启用

### 图像处理流程
```
ComfyUI IMAGE (torch.Tensor/numpy.ndarray)
  ↓ to_pil_from_comfy()
PIL.Image
  ↓ save_image_to_buffer()
io.BytesIO (内存缓冲)
  ↓ HTTP POST (multipart/form-data)
图床 URL
  ↓ 传递给视频生成 API
视频任务
```

---

## 诊断与调试

### 诊断脚本 (`diagnose.py`)
**运行方式**:
```bash
python diagnose.py
```

**检查项**:
1. Python 版本和依赖包
2. 环境变量配置
3. API 连接测试
4. 节点注册状态
5. 文件权限检查

### 常见问题

#### 1. 节点不显示
**原因**:
- 依赖未安装
- Python 版本不兼容
- 节点注册失败

**解决**:
```bash
cd ComfyUI/custom_nodes/ComfyUI_KuAi_Power
pip install -r requirements.txt
python diagnose.py
# 重启 ComfyUI
```

#### 2. API 调用失败
**原因**:
- API Key 未配置或错误
- 网络连接问题
- API 配额耗尽

**解决**:
```bash
# 检查环境变量
echo $KUAI_API_KEY

# 或在 .env 文件中配置
echo "KUAI_API_KEY=your_key_here" > .env

# 测试 API 连接
curl -H "Authorization: Bearer $KUAI_API_KEY" \
     https://api.kuai.host/v1/models
```

#### 3. 视频生成超时
**原因**:
- 服务器负载高
- 网络不稳定
- 超时时间设置过短

**解决**:
- 增加 `max_wait_time` 参数（默认 600 秒）
- 使用国内镜像 `v.kuai.host`
- 分开使用 `Create` + `Query` 节点手动控制

#### 4. 图片上传失败
**原因**:
- 图片格式不支持
- 文件过大
- 网络问题

**解决**:
- 使用支持的格式（JPEG, PNG, WebP）
- 调整 `quality` 参数降低文件大小
- 检查网络连接

---

## 开发指南

### 添加新节点

1. **创建节点类**:
```python
# nodes/YourCategory/your_node.py
class YourNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param1": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("输出",)
    FUNCTION = "execute"
    CATEGORY = "KuAi/YourCategory"

    def execute(self, param1):
        # 实现逻辑
        return (result,)
```

2. **注册节点**:
```python
# nodes/YourCategory/__init__.py
from .your_node import YourNode

NODE_CLASS_MAPPINGS = {
    "YourNode": YourNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YourNode": "你的节点",
}
```

3. **重启 ComfyUI** - 自动注册系统会发现新节点

### 最佳实践

1. **错误处理**: 使用 `raise RuntimeError()` 抛出用户友好的错误信息
2. **参数验证**: 在节点执行前验证所有必需参数
3. **中文标签**: 使用 `INPUT_LABELS()` 提供中文参数名
4. **工具提示**: 在 `INPUT_TYPES` 中添加 `tooltip` 说明
5. **类型安全**: 使用 Pydantic 进行数据验证
6. **日志输出**: 使用 `print(f"[ComfyUI_KuAi_Power] ...")` 统一日志格式

---

## 性能优化

### 图像处理优化
- **格式选择**: JPEG 适合照片，PNG 适合图形，WebP 平衡质量和大小
- **质量设置**: 80-90 通常是最佳平衡点
- **尺寸控制**: 视频生成前自动调整图片尺寸

### API 调用优化
- **连接复用**: 使用 `requests.Session()` 复用连接
- **超时设置**: 合理设置 `timeout` 避免长时间阻塞
- **重试机制**: 对临时性错误自动重试（可通过 `HTTP_RETRY` 配置）

### 轮询优化
- **动态间隔**: 初期短间隔，后期长间隔
- **早期退出**: 检测到失败状态立即返回
- **超时保护**: 设置最大等待时间防止无限等待

---

## 许可证

MIT License

---

## 相关资源

- **API 服务**: [kuai.host](https://api.kuai.host/register?aff=z2C8)

- **视频教程**: [Bilibili](https://www.bilibili.com/video/BV1umCjBqEpt/)

---

## 更新日志

### 最新版本
- ✅ 支持 Veo3.1 模型
- ✅ 新增 Nano Banana 图像生成节点
- ✅ 支持多轮对话式图像编辑
- ✅ 新增 AI 脚本生成功能
- ✅ 优化提示词自动翻译
- ✅ 添加快捷面板 (Ctrl+Shift+K)
- ✅ 完善错误处理和诊断工具
- ✅ 统一 API 端点配置（默认 https://api.kuai.host）

---

**文档生成时间**: 2025-12-13
**适用版本**: ComfyUI_KuAi_Power (当前版本)
