# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ComfyUI_KuAi_Power** is a ComfyUI extension plugin providing AI video generation (Sora2, Veo3) and image generation (Nano Banana/Gemini) capabilities through the kuai.host API. The plugin is designed for Chinese users with full Chinese UI labels and focuses on e-commerce video content creation.

**Key Technologies**: ComfyUI nodes, Pydantic settings, async task polling, PIL image processing, kuai.host API integration

## Development Commands

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run diagnostics to verify setup
python diagnose.py

# Configure API key (choose one method)
export KUAI_API_KEY=your_key_here
# OR create .env file
echo "KUAI_API_KEY=your_key_here" > .env
```

### Testing
```bash
# Test CSV nodes
python test_csv_nodes.py

# Test node labels
python test_labels.py

# Manual API testing
curl -H "Authorization: Bearer $KUAI_API_KEY" https://api.kuai.host/v1/models
```

### Development Workflow
1. Make changes to node files in `nodes/`
2. Restart ComfyUI to reload nodes (no hot reload)
3. Check ComfyUI console for `[ComfyUI_KuAi_Power]` log messages
4. Test nodes in ComfyUI UI (Ctrl+Shift+K for quick panel)

## Architecture

### Node Auto-Registration System

The plugin uses a **dynamic node discovery system** (`__init__.py:11-78`) that automatically registers all nodes without manual imports:

1. **Root-level scan**: Loads `nodes/*.py` files
2. **Subdirectory scan**: Recursively loads `nodes/*/` directories
3. **Type detection**: Auto-detects classes with `INPUT_TYPES` and `RETURN_TYPES`
4. **Mapping registration**: Populates `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`

**Key Pattern**: Each subdirectory has an `__init__.py` that exports:
```python
NODE_CLASS_MAPPINGS = {"NodeClassName": NodeClass}
NODE_DISPLAY_NAME_MAPPINGS = {"NodeClassName": "🎬 Display Name"}
```

### Directory Structure
```
nodes/
├── Sora2/              # Sora2 video generation
│   ├── __init__.py     # Exports NODE_CLASS_MAPPINGS
│   ├── sora2.py        # Core video nodes
│   ├── script_generator.py  # AI script generation
│   └── kuai_utils.py   # Shared utilities
├── Veo3/               # Veo3 video generation
│   ├── __init__.py
│   └── veo3.py
├── NanoBanana/         # Gemini image generation
│   ├── __init__.py
│   ├── nano_banana.py  # Single/multi-turn image gen
│   └── batch_processor.py  # CSV batch processing
└── Utils/              # Utility nodes
    ├── __init__.py
    ├── image_upload.py
    ├── deepseek_ocr.py
    └── csv_reader.py
```

### Configuration System

Uses **Pydantic Settings** (`config.py`) with `.env` file support:
```python
class Settings(BaseSettings):
    WEBHOOK_BASE_PATH: str = "/webhook"
    SECRET_TOKEN: str = ""
    HTTP_TIMEOUT: int = 30
    HTTP_RETRY: int = 0

    class Config:
        env_file = ".env"
```

**Environment Variables**:
- `KUAI_API_KEY`: API key (required, can also be passed per-node)
- `HTTP_TIMEOUT`: Request timeout in seconds (default: 30)

### API Integration Patterns

**Base URL**: `https://api.kuai.host`

**Authentication**: Bearer token in Authorization header
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

**Common Utilities** (`nodes/Sora2/kuai_utils.py`):
- `env_or(value, env_name)`: Prioritize parameter over environment variable
- `to_pil_from_comfy(image_any)`: Convert ComfyUI IMAGE (torch.Tensor/numpy) to PIL.Image
- `save_image_to_buffer(pil, fmt, quality)`: Save PIL to BytesIO for upload
- `ensure_list_from_urls(urls_str)`: Parse comma/semicolon/newline separated URLs
- `http_headers_json(api_key)`: Generate standard JSON headers with auth

### Async Task Pattern

Video generation uses **polling-based async** (`*AndWait` nodes):
```python
def create_and_wait(self, ...):
    # 1. Submit task
    task_id, status, _ = self.create(...)

    # 2. Poll until complete
    elapsed = 0
    while elapsed < max_wait_time:
        if status in ["completed", "failed"]:
            break
        time.sleep(poll_interval)
        task_id, status, video_url, _ = self.query(task_id, ...)
        elapsed += poll_interval

    # 3. Return or raise error
    if status != "completed":
        raise RuntimeError(f"Task failed: {status}")
    return (task_id, status, video_url, ...)
```

**Pattern**: Separate `Create` + `Query` nodes for manual control, `CreateAndWait` for convenience.

### Image Processing Pipeline

```
ComfyUI IMAGE (torch.Tensor/numpy.ndarray, BHWC format, float32 0-1)
  ↓ to_pil_from_comfy()
PIL.Image (RGB, uint8)
  ↓ save_image_to_buffer()
io.BytesIO (JPEG/PNG/WebP)
  ↓ HTTP POST multipart/form-data
Image URL (kuai.host CDN)
  ↓ Pass to API
Video/Image generation task
```

### Node Structure Convention

All nodes follow this pattern:
```python
class MyNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param1": ("STRING", {"default": ""}),
            },
            "optional": {
                "param2": ("INT", {"default": 0}),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        """Chinese labels for UI"""
        return {
            "param1": "参数1",
            "param2": "参数2"
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("输出1", "输出2")
    FUNCTION = "execute"
    CATEGORY = "KuAi/CategoryName"

    def execute(self, param1, param2=0):
        # Implementation
        return (result1, result2)
```

**Important Conventions**:
- All categories start with `KuAi/`
- Use Chinese for `RETURN_NAMES` and `INPUT_LABELS`
- Use emoji prefixes in `NODE_DISPLAY_NAME_MAPPINGS` (🎬 🖼️ 🍌 📦 🔍 ⚡)
- Raise `RuntimeError` with user-friendly Chinese error messages
- Log with `print(f"[ComfyUI_KuAi_Power] ...")`

## Key API Endpoints

### Video Generation
```
POST /v1/video/create
{
  "model": "sora-2" | "veo3.1",
  "prompt": "...",
  "images": ["url1", "url2"],  // optional
  "duration": 10 | 15 | 25,
  "orientation": "portrait" | "landscape",
  "aspect_ratio": "16:9" | "9:16"
}
→ {"id": "task_id", "status": "pending"}

GET /v1/video/query?task_id={id}
→ {"id": "...", "status": "completed", "video_url": "..."}
```

### Image Generation (Nano Banana)
```
POST /v1/images/generate
{
  "model": "gemini-3-pro-image-preview" | "gemini-2.5-flash-image",
  "prompt": "...",
  "generationConfig": {
    "seed": 12345,  // INT32, 0 = random
    "temperature": 1.0,
    "imageConfig": {
      "aspectRatio": "1:1",
      "imageSize": "2K"  // only for gemini-3-pro
    }
  },
  "systemInstruction": "...",  // optional
  "useSearch": true,  // only for gemini-3-pro
  "referenceImages": ["url1", "url2"]
}
→ {"image_url": "...", "thinking": "...", "grounding_sources": "..."}

POST /v1/chat/images  // Multi-turn chat
{
  "model": "...",
  "messages": [
    {"role": "user", "content": "...", "image_url": "..."},
    {"role": "assistant", "content": "...", "image_url": "..."}
  ],
  "generationConfig": {...}
}
```

### Utilities
```
POST /v1/upload  // Image upload
Content-Type: multipart/form-data
→ {"url": "..."}

POST /v1/chat/completions  // AI text generation
{
  "model": "deepseek-v3.2-exp",
  "messages": [{"role": "system", "content": "..."}, ...]
}
```

## Complete Node Creation Workflow (10 Steps)

When creating new image generation or video generation nodes, follow this comprehensive workflow to ensure proper integration with CSV batch processing and the plugin ecosystem.

### Workflow Overview

1. **Plan the Node** - Define purpose, API, CSV compatibility, category
2. **Create Node Implementation** - Write the core generation node
3. **Register the Node** - Add to category's `__init__.py`
4. **Update Frontend Panel** - Add category to quick panel (if new)
5. **Create Documentation** - Write detailed usage guide
6. **Create Test File** - Write comprehensive test suite
7. **Run Tests** - Verify registration, execution, CSV compatibility
8. **Verify Integration** - Test in ComfyUI UI
9. **Create CSV Batch Processor** - Add batch processing support (for generation nodes)
   - 9.1: Create batch processor node
   - 9.2: Register batch processor
   - 9.3: Create sample CSV files (3+)
   - 9.4: Create CSV usage guide
   - 9.5: Create batch processor tests
   - 9.6: Test batch processing
10. **Update Main Documentation** - Update README and guides

**Note**: Step 9 (CSV Batch Processor) applies to image/video generation nodes. Skip for utility nodes.

---

### Step 1: Plan the Node

Before coding, determine:
- **Node purpose**: Image generation, video generation, or utility
- **API endpoint**: Which kuai.host API will be used
- **CSV compatibility**: What parameters should be configurable via CSV
- **Category**: Which category folder (Sora2, Veo3, NanoBanana, Utils, or new category)

### Step 2: Create Node Implementation

**Location**: `/workspaces/ComfyUI_KuAi_Power/nodes/CategoryName/node_name.py`

**Template for Image/Video Generation Node**:
```python
"""节点名称 - 简短描述"""

import os
import requests
from ..Sora2.kuai_utils import env_or, http_headers_json, raise_for_bad_status

class MyGenerationNode:
    """节点类文档字符串"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "生成提示词"
                }),
                "model_name": (["model-1", "model-2"], {
                    "default": "model-1",
                    "tooltip": "选择模型"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "tooltip": "随机种子（0为随机）"
                }),
                "system_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "系统提示词（可选）"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        """中文标签"""
        return {
            "prompt": "提示词",
            "model_name": "模型名称",
            "api_key": "API密钥",
            "seed": "随机种子",
            "system_prompt": "系统提示词"
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "元数据")
    FUNCTION = "generate"
    CATEGORY = "KuAi/CategoryName"

    def generate(self, prompt, model_name, api_key="", seed=0, system_prompt=""):
        """执行生成"""
        # 1. 解析 API key
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置")

        # 2. 构建请求
        api_base = "https://api.kuai.host"
        headers = http_headers_json(api_key)

        payload = {
            "model": model_name,
            "prompt": prompt,
            "seed": seed if seed > 0 else None,
        }

        if system_prompt:
            payload["systemInstruction"] = system_prompt

        # 3. 调用 API
        try:
            resp = requests.post(
                f"{api_base}/v1/images/generate",
                json=payload,
                headers=headers,
                timeout=120
            )
            raise_for_bad_status(resp, "图像生成失败")

            result = resp.json()
            image_url = result.get("image_url")

            # 4. 下载图像并转换为 ComfyUI IMAGE 格式
            # ... (实现图像下载和转换逻辑)

            return (image_tensor, metadata_json)

        except Exception as e:
            raise RuntimeError(f"生成失败: {str(e)}")
```

**CSV Batch Processing Support**:
For nodes that should support CSV batch processing, ensure all configurable parameters are exposed in `INPUT_TYPES` and can be serialized to/from CSV format.

### Step 3: Register the Node

**Location**: `/workspaces/ComfyUI_KuAi_Power/nodes/CategoryName/__init__.py`

```python
"""CategoryName 节点集合"""

from .node_name import MyGenerationNode

NODE_CLASS_MAPPINGS = {
    "MyGenerationNode": MyGenerationNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyGenerationNode": "🎨 My Generation Node",
}
```

**Emoji Conventions**:
- 🎬 Video generation (Sora2)
- 🚀 Video generation (Veo3)
- 🍌 Image generation (Nano Banana)
- 🎨 Image generation (other)
- 📦 Batch processing
- 🔍 Query/status
- ⚡ One-click/convenience
- 🛠️ Utilities
- 📝 Script/text generation

### Step 4: Update Frontend Panel (if new category)

**Location**: `/workspaces/ComfyUI_KuAi_Power/web/kuaipower_panel.js`

If you created a **new category**, add it to the `categoryNameMap` (line 7-15):

```javascript
const categoryNameMap = {
  "ScriptGenerator": "📝 脚本生成",
  "Sora2": "🎬 Sora2 视频生成",
  "Veo3": "🚀 Veo3.1 视频生成",
  "NanoBanana": "🍌 Nano Banana 图像生成",
  "Utils": "🛠️ 工具节点",
  "YourNewCategory": "🎨 Your Category Name",  // ADD THIS
};
```

**Note**: If using an existing category, no changes needed - the panel auto-discovers nodes.

### Step 5: Create Documentation

**Location**: `/workspaces/ComfyUI_KuAi_Power/docs/NODE_NAME_GUIDE.md`

**Documentation Template**:
```markdown
# MyGenerationNode 使用指南

## 概述
简要描述节点的功能和用途。

## 参数说明

### 必需参数
- **prompt** (提示词): 描述要生成的内容
- **model_name** (模型名称): 选择使用的模型
  - `model-1`: 模型1的特点
  - `model-2`: 模型2的特点

### 可选参数
- **seed** (随机种子): 0为随机，固定值可复现结果
- **system_prompt** (系统提示词): 指导AI的整体风格和行为

## 返回值
- **图像**: 生成的图像（ComfyUI IMAGE格式）
- **元数据**: JSON格式的生成信息

## 使用示例

### 基础用法
1. 添加节点到画布
2. 输入提示词
3. 选择模型
4. 执行生成

### CSV批量处理
支持通过CSV文件批量生成，CSV格式：
\`\`\`csv
task_type,prompt,model_name,seed,system_prompt
generate,描述1,model-1,12345,风格指导
generate,描述2,model-2,0,
\`\`\`

## API说明
- **端点**: `POST /v1/images/generate`
- **模型**: model-1, model-2
- **超时**: 120秒

## 常见问题
1. **生成失败**: 检查API key和网络连接
2. **结果不理想**: 调整提示词或尝试不同模型

## 更新日志
- 2025-XX-XX: 初始版本
```

### Step 6: Create Test File

**Location**: `/workspaces/ComfyUI_KuAi_Power/test/test_node_name.py`

**Test Template**:
```python
#!/usr/bin/env python3
"""测试 MyGenerationNode 节点"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.CategoryName import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        if 'MyGenerationNode' in NODE_CLASS_MAPPINGS:
            print("✅ MyGenerationNode 已注册")
            node_class = NODE_CLASS_MAPPINGS['MyGenerationNode']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('MyGenerationNode')}")

            # 检查必需方法
            assert hasattr(node_class, 'INPUT_TYPES'), "缺少 INPUT_TYPES"
            assert hasattr(node_class, 'RETURN_TYPES'), "缺少 RETURN_TYPES"
            assert hasattr(node_class, 'FUNCTION'), "缺少 FUNCTION"

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ MyGenerationNode 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_node_execution():
    """测试节点执行（需要API key）"""
    print("\n" + "=" * 60)
    print("测试 2: 节点执行")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        print("   设置方法: export KUAI_API_KEY=your_key_here")
        return True

    try:
        from nodes.CategoryName import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['MyGenerationNode']
        node = node_class()

        # 执行测试
        print("🔄 执行生成测试...")
        result = node.generate(
            prompt="test prompt",
            model_name="model-1",
            api_key=api_key,
            seed=12345
        )

        print(f"✅ 生成成功")
        print(f"   返回类型: {type(result)}")
        print(f"   返回值数量: {len(result)}")

        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_compatibility():
    """测试CSV批量处理兼容性"""
    print("\n" + "=" * 60)
    print("测试 3: CSV批量处理兼容性")
    print("=" * 60)

    try:
        from nodes.CategoryName import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['MyGenerationNode']
        input_types = node_class.INPUT_TYPES()

        # 检查关键参数
        required = input_types.get('required', {})
        optional = input_types.get('optional', {})

        csv_compatible_params = ['prompt', 'model_name', 'seed', 'system_prompt']
        all_params = {**required, **optional}

        missing = [p for p in csv_compatible_params if p not in all_params]

        if missing:
            print(f"⚠️  缺少CSV兼容参数: {missing}")
        else:
            print("✅ 所有CSV兼容参数都已定义")

        return len(missing) == 0

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 MyGenerationNode 节点测试套件\n")

    results = []
    results.append(("节点注册", test_node_registration()))
    results.append(("节点执行", test_node_execution()))
    results.append(("CSV兼容性", test_csv_compatibility()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
```

### Step 7: Run Tests

```bash
# 1. Test node registration
python test/test_node_name.py

# 2. Test with actual API (provide API key)
export KUAI_API_KEY=your_test_key_here
python test/test_node_name.py

# 3. Run full diagnostics
python diagnose.py
```

### Step 8: Verify Integration

1. **Restart ComfyUI** to load the new node
2. **Check console logs** for `[ComfyUI_KuAi_Power]` messages
3. **Open quick panel** (Ctrl+Shift+K) and verify node appears in correct category
4. **Test in UI**:
   - Add node to canvas
   - Configure parameters
   - Execute and verify output

### Step 9: Create CSV Batch Processor (for generation nodes)

**Note**: This step applies to image/video generation nodes. Skip for utility nodes.

#### 9.1: Create Batch Processor Node

**Location**: `/workspaces/ComfyUI_KuAi_Power/nodes/CategoryName/batch_processor.py`

**Template**:
```python
"""CategoryName 批量处理器"""

import json
import os
import time
from ..Sora2.kuai_utils import env_or
from .node_name import MyGenerationNode

class MyBatchProcessor:
    """批量处理器"""

    def __init__(self):
        self.generator = MyGenerationNode()

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
                    "tooltip": "API 密钥"
                }),
                "output_dir": ("STRING", {
                    "default": "./output/batch",
                    "tooltip": "输出目录"
                }),
                "delay_between_tasks": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 60.0,
                    "step": 0.5,
                    "tooltip": "任务间延迟（秒）"
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
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("处理结果", "输出目录")
    FUNCTION = "process_batch"
    CATEGORY = "KuAi/CategoryName"

    def process_batch(self, batch_tasks, api_key="", output_dir="./output/batch",
                     delay_between_tasks=2.0):
        """批量处理任务"""
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
            print(f"[Batch] 开始批量处理 {len(tasks)} 个任务")
            print(f"{'='*60}\n")

            # 逐个处理任务
            for idx, task in enumerate(tasks, start=1):
                try:
                    print(f"\n[{idx}/{len(tasks)}] 处理任务 (行 {task.get('_row_number', '?')})")

                    # 处理单个任务
                    task_info = self._process_single_task(task, idx, api_key, output_dir)

                    results["success"] += 1
                    results["task_ids"].append(task_info)
                    print(f"✓ 任务 {idx} 完成")

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"任务 {idx}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"✗ {error_msg}")

                # 任务间延迟
                if idx < len(tasks) and delay_between_tasks > 0:
                    time.sleep(delay_between_tasks)

            # 保存任务列表
            tasks_file = os.path.join(output_dir, "tasks.json")
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(results["task_ids"], f, ensure_ascii=False, indent=2)

            # 生成结果报告
            report = self._generate_report(results)
            print(f"\n{'='*60}")
            print(report)
            print(f"{'='*60}\n")

            return (report, output_dir)

        except Exception as e:
            error_msg = f"批量处理失败: {str(e)}"
            print(f"[Batch] {error_msg}")
            raise RuntimeError(error_msg)

    def _process_single_task(self, task, task_idx, api_key, output_dir):
        """处理单个任务 - 根据实际节点实现"""
        # 解析任务参数
        prompt = task.get("prompt", "").strip()
        if not prompt:
            raise ValueError("提示词不能为空")

        # 调用生成器
        result = self.generator.generate(
            prompt=prompt,
            api_key=api_key,
            # ... 其他参数
        )

        # 保存结果
        task_info = {
            "task_id": f"task_{task_idx}",
            "prompt": prompt,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return task_info

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
    "MyBatchProcessor": MyBatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyBatchProcessor": "📦 My Batch Processor",
}
```

#### 9.2: Register Batch Processor

Update `nodes/CategoryName/__init__.py`:
```python
from .node_name import MyGenerationNode
from .batch_processor import MyBatchProcessor

NODE_CLASS_MAPPINGS = {
    "MyGenerationNode": MyGenerationNode,
    "MyBatchProcessor": MyBatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyGenerationNode": "🎨 My Generation Node",
    "MyBatchProcessor": "📦 My Batch Processor",
}
```

#### 9.3: Create Sample CSV Files

**Location**: `/workspaces/ComfyUI_KuAi_Power/examples/category_batch_basic.csv`

**Example**:
```csv
prompt,model_name,seed,output_prefix
"Example prompt 1",model-1,12345,example_1
"Example prompt 2",model-2,0,example_2
"Example prompt 3",model-1,67890,example_3
```

Create at least 3 sample CSV files:
1. `category_batch_basic.csv` - Basic examples
2. `category_batch_advanced.csv` - Advanced examples with all parameters
3. `category_batch_template.csv` - Chinese template for users to copy

#### 9.4: Create CSV Usage Guide

**Location**: `/workspaces/ComfyUI_KuAi_Power/examples/CATEGORY_CSV_GUIDE.md`

**Template**:
```markdown
# CategoryName 批量处理 CSV 使用指南

## CSV 格式

### 必需列
- `prompt` - 提示词

### 可选列
- `model_name` - 模型名称（默认：model-1）
- `seed` - 随机种子（默认：0）
- `output_prefix` - 输出前缀

## 使用步骤

1. 准备 CSV 文件
2. 在 ComfyUI 中设置工作流：CSVBatchReader → MyBatchProcessor
3. 配置参数
4. 执行处理
5. 查看结果

## 示范文件

- `category_batch_basic.csv` - 基础示例
- `category_batch_advanced.csv` - 高级示例
- `category_batch_template.csv` - 中文模板

## 常见问题

Q: CSV 文件编码问题？
A: 确保使用 UTF-8 编码保存。

Q: 提示词包含逗号怎么办？
A: 用双引号包裹整个提示词。
```

#### 9.5: Create Batch Processor Tests

**Location**: `/workspaces/ComfyUI_KuAi_Power/test/test_category_batch.py`

**Template**:
```python
#!/usr/bin/env python3
"""测试 CategoryName 批量处理器"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_batch_processor_registration():
    """测试批量处理器注册"""
    print("=" * 60)
    print("测试 1: 批量处理器注册")
    print("=" * 60)

    try:
        from nodes.CategoryName import NODE_CLASS_MAPPINGS

        if 'MyBatchProcessor' in NODE_CLASS_MAPPINGS:
            print("✅ MyBatchProcessor 已注册")
            return True
        else:
            print("❌ MyBatchProcessor 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_batch_processing_with_api():
    """测试批量处理（实际 API）"""
    print("\n" + "=" * 60)
    print("测试 2: 批量处理（实际 API）")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        return True

    try:
        from nodes.CategoryName import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS['MyBatchProcessor']()

        # 创建测试任务
        mock_tasks = [
            {
                "_row_number": 2,
                "prompt": "Test prompt 1",
                "output_prefix": "test_1"
            },
            {
                "_row_number": 3,
                "prompt": "Test prompt 2",
                "output_prefix": "test_2"
            }
        ]

        batch_tasks_json = json.dumps(mock_tasks)

        print("🔄 执行批量处理测试...")
        result, output_dir = node.process_batch(
            batch_tasks=batch_tasks_json,
            api_key=api_key,
            output_dir="./test_output/batch",
            delay_between_tasks=1.0
        )

        print(f"✅ 批量处理成功")
        print(f"   输出目录: {output_dir}")

        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 CategoryName 批量处理器测试套件\n")

    results = []
    results.append(("批量处理器注册", test_batch_processor_registration()))
    results.append(("批量处理实际 API", test_batch_processing_with_api()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
```

#### 9.6: Test Batch Processing

```bash
# Run batch processor tests
KUAI_API_KEY=your_key_here python test/test_category_batch.py

# Verify CSV files
ls -lh examples/category_*.csv

# Check CSV guide
cat examples/CATEGORY_CSV_GUIDE.md
```

### Step 10: Update Main Documentation

Add node information to:
- `/workspaces/ComfyUI_KuAi_Power/README.md` - User-facing documentation
- `/workspaces/ComfyUI_KuAi_Power/CLAUDE.md` - This file (if architectural changes)
- Update main node guide to include batch processor information

### Checklist for New Nodes

Before considering a node complete, verify:

#### Core Node (Steps 1-8)
- [ ] Node file created in correct `nodes/CategoryName/` directory
- [ ] Node class implements all required methods (INPUT_TYPES, RETURN_TYPES, FUNCTION, CATEGORY)
- [ ] Chinese labels provided via INPUT_LABELS
- [ ] Node registered in category's `__init__.py`
- [ ] Display name uses appropriate emoji prefix
- [ ] Frontend panel updated (if new category)
- [ ] Documentation created in `docs/`
- [ ] Test file created in `test/`
- [ ] Tests pass (registration, execution, CSV compatibility)
- [ ] Node appears in ComfyUI UI quick panel
- [ ] Node executes successfully in ComfyUI
- [ ] Error messages are user-friendly and in Chinese
- [ ] Logging uses `[ComfyUI_KuAi_Power]` prefix

#### CSV Batch Processing (Step 9 - for generation nodes)
- [ ] Batch processor node created (`batch_processor.py`)
- [ ] Batch processor registered in `__init__.py`
- [ ] At least 3 sample CSV files created in `examples/`
  - [ ] `category_batch_basic.csv` - Basic examples
  - [ ] `category_batch_advanced.csv` - Advanced examples (optional)
  - [ ] `category_batch_template.csv` - Chinese template
- [ ] CSV usage guide created (`examples/CATEGORY_CSV_GUIDE.md`)
- [ ] Batch processor test file created (`test/test_category_batch.py`)
- [ ] Batch processor tests pass (registration, API execution)
- [ ] CSV files use UTF-8 encoding
- [ ] CSV format documented with all columns explained
- [ ] Batch processor appears in ComfyUI UI
- [ ] Batch processing works with CSVBatchReader node

#### Documentation (Step 10)
- [ ] Main documentation updated (`README.md`)
- [ ] CLAUDE.md updated (if architectural changes)
- [ ] Node guide includes batch processor information
- [ ] Examples directory has README.md explaining CSV files

### Common Patterns for CSV Batch Processing

To make a node CSV-compatible, ensure:

1. **All configurable parameters** are in INPUT_TYPES (not hardcoded)
2. **Parameter names** match CSV column names
3. **Default values** are sensible for batch processing
4. **Optional parameters** have clear defaults
5. **Image inputs** support file paths (for batch processing)

Example CSV-compatible parameter structure:
```python
"required": {
    "prompt": ("STRING", {"default": ""}),
    "model_name": (["model-1", "model-2"], {"default": "model-1"}),
},
"optional": {
    "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
    "system_prompt": ("STRING", {"default": ""}),
    "image_1": ("IMAGE", {}),  # Optional reference image
    "output_prefix": ("STRING", {"default": "output"}),
}
```

### Testing with User-Provided API Key

When user provides a test API key:

```bash
# Set API key for testing
export KUAI_API_KEY=user_provided_key

# Run comprehensive tests
python test/test_node_name.py

# Test actual generation
python -c "
from nodes.CategoryName import NODE_CLASS_MAPPINGS
node = NODE_CLASS_MAPPINGS['MyGenerationNode']()
result = node.generate(
    prompt='test image',
    model_name='model-1',
    api_key='$KUAI_API_KEY'
)
print('Success:', result)
"
```

This workflow ensures consistent, high-quality node development with proper testing, documentation, and integration.

## Important Patterns

### Error Handling
```python
# Unified error handling for API responses
def raise_for_bad_status(resp: requests.Response, context: str = ""):
    if resp.status_code >= 400:
        try:
            err_data = resp.json()
            msg = err_data.get("error", {}).get("message", resp.text)
        except:
            msg = resp.text
        raise RuntimeError(f"{context}: HTTP {resp.status_code} - {msg}")
```

### API Key Resolution
```python
# Priority: node parameter > environment variable
api_key = env_or(api_key_param, "KUAI_API_KEY")
if not api_key:
    raise RuntimeError("API Key 未配置")
```

### Model-Specific Configuration
```python
# Different models have different capabilities
if model_name == "gemini-3-pro-image-preview":
    # Supports imageSize and useSearch
    config["imageConfig"]["imageSize"] = image_size
    config["useSearch"] = use_search
elif model_name == "gemini-2.5-flash-image":
    # Faster, cheaper, no imageSize/search support
    pass
```

### CSV Batch Processing
The batch processor supports two modes:
- **Upload mode**: Read from `ComfyUI/input/` directory (dropdown selection)
- **Path mode**: Direct file path input (cross-platform)

CSV columns: `task_type`, `prompt`, `system_prompt`, `model_name`, `seed`, `aspect_ratio`, `image_size`, `temperature`, `use_search`, `image_1`-`image_6`, `output_prefix`

## Frontend Extensions

Located in `web/`:
- `kuaipower_panel.js`: Quick access panel (Ctrl+Shift+K)
- `video_preview.js`: Video preview widget

## Common Issues

### Nodes Not Showing
1. Check dependencies: `pip install -r requirements.txt`
2. Run diagnostics: `python diagnose.py`
3. Check ComfyUI console for `[ComfyUI_KuAi_Power]` logs
4. Verify node structure (INPUT_TYPES, RETURN_TYPES, FUNCTION, CATEGORY)

### API Failures
1. Verify API key: `echo $KUAI_API_KEY`
2. Test connectivity: `curl -H "Authorization: Bearer $KUAI_API_KEY" https://api.kuai.host/v1/models`
3. Check timeout settings in config.py

### Image Upload Issues
- Supported formats: JPEG, PNG, WebP
- Adjust quality parameter (80-90 recommended)
- Check file size limits

## Resources

- **API Service**: https://api.kuai.host/register?aff=z2C8
- **Video Tutorial**: https://www.bilibili.com/video/BV1umCjBqEpt/
- **Detailed Docs**: See README.md and docs/ directory
