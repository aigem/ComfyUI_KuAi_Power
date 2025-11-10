# ComfyUI KuAi Power

ComfyUI 节点扩展，提供 Sora2 视频生成和脚本生成功能。

## 快速开始

### 1. 安装依赖

```bash
cd ComfyUI/custom_nodes/ComfyUI_KuAi_Power
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

创建 `.env` 文件或设置环境变量：

```bash
KUAI_API_KEY=your_api_key_here
```

或在节点参数中直接填写 API Key。

### 3. 启动 ComfyUI

```bash
cd ComfyUI
python main.py
```

### 4. 使用节点

- 按快捷键 `Ctrl + Alt + F` 打开节点面板
- 面板显示中文分类：
  - 📝 脚本生成（4个节点）
  - 🎬 视频生成（4个节点）
- 或在右键菜单中找到 `KuAi/ScriptGenerator` 和 `KuAi/Sora2` 分类

## 节点列表

> 🎉 **全中文界面**：所有节点名称和输出标签均为中文，更加直观易用！

### 脚本生成器 (KuAi/ScriptGenerator)

#### 📦 产品信息构建器 (ProductInfoBuilder)
构建产品信息 JSON，用于后续生成视频提示词。

**输入：**
- `product_name` (必填) - 产品名称
- `product_features` - 产品卖点
- `video_type` - 视频类型（商品介绍/推广/促销/测评/口播）
- `duration` - 视频时长（10秒/15秒/25秒）
- `language` - 语言
- `reference_image_url` - 参考图片 URL

**输出：**
- `product_json` - 产品信息 JSON
- `reference_image_url` - 参考图片 URL

---

#### SoraPromptFromProduct - 基于产品生成提示词
调用 AI 根据产品信息和参考图生成 Sora 视频提示词。

**输入：**
- `product_json` - 产品信息 JSON
- `reference_image_url` - 参考图片 URL
- `api_base` - API 端点
- `api_key` - API 密钥
- `model` - 模型名称
- `timeout` - 超时时间

**输出：**
- `sora_prompt` - 生成的提示词
- `raw_ai_response` - 原始 AI 响应

---

#### DeepseekOCRToPrompt - OCR 文本提取
使用 Deepseek OCR 提取图片中的文本和视觉元素。

**输入：**
- `image_url` - 图片 URL
- `api_base` - API 端点
- `api_key` - API 密钥
- `system_prompt` - 系统提示词
- `timeout` - 超时时间

**输出：**
- `ocr_text` - 提取的文本
- `raw_response_json` - 原始响应

---

### Sora2 API (KuAi/Sora2)

#### UploadToImageHost - 上传图片
将 ComfyUI 图片上传到图床，获取 URL。

**输入：**
- `image` - ComfyUI IMAGE 类型
- `upload_url` - 图床 API 地址
- `format` - 图片格式（jpeg/png/webp）
- `quality` - 图片质量（1-100）
- `timeout` - 超时时间

**输出：**
- `url` - 图片 URL
- `created_ms` - 创建时间戳

---

#### SoraCreateVideo - 创建视频任务
创建 Sora 视频生成任务。

**输入：**
- `images` - 图片 URL 列表（逗号分隔）
- `prompt` - 视频提示词
- `api_base` - API 端点
- `api_key` - API 密钥
- `model` - 模型（sora-2/sora-2-pro）
- `orientation` - 方向（portrait/landscape）
- `size` - 尺寸（small/large）
- `duration` - 时长（5-60秒）
- `watermark` - 是否添加水印
- `timeout` - 超时时间

**输出：**
- `task_id` - 任务 ID
- `status` - 任务状态
- `status_update_time` - 状态更新时间

---

#### SoraQueryTask - 查询任务状态
查询 Sora 视频任务状态和结果。

**输入：**
- `task_id` - 任务 ID
- `api_base` - API 端点
- `api_key` - API 密钥
- `wait` - 是否等待完成
- `poll_interval_sec` - 轮询间隔（秒）
- `timeout_sec` - 超时时间（秒）

**输出：**
- `status` - 任务状态
- `video_url` - 视频 URL
- `gif_url` - GIF URL
- `thumbnail_url` - 缩略图 URL
- `raw_response_json` - 原始响应

---

#### SoraCreateAndWait - 创建并等待
一键创建视频任务并等待完成。

**输入：**
- 同 SoraCreateVideo + SoraQueryTask 的参数

**输出：**
- `status` - 任务状态
- `video_url` - 视频 URL
- `gif_url` - GIF URL
- `thumbnail_url` - 缩略图 URL
- `task_id` - 任务 ID

---

## 工作流示例

### 示例 1：产品视频生成

```
LoadImage 
  → UploadToImageHost (获取图片 URL)
  → ProductInfoBuilder (填写产品信息)
  → SoraPromptFromProduct (AI 生成提示词)
  → SoraCreateAndWait (生成视频)
```

### 示例 2：OCR 驱动视频生成

```
LoadImage 
  → UploadToImageHost (获取图片 URL)
  → DeepseekOCRToPrompt (提取文本)
  → SoraCreateVideo (创建任务)
  → SoraQueryTask (查询结果)
```

## 故障排查

### 运行诊断脚本

```bash
python diagnose.py
```

这将检查：
- ✅ 文件结构
- ✅ 依赖安装
- ✅ 模块导入
- ✅ 节点结构
- ✅ 节点分类

### 常见问题

**Q: 节点不显示？**
- 检查 ComfyUI 控制台是否有错误
- 确认依赖已安装：`pip install -r requirements.txt`
- 重启 ComfyUI

**Q: API 调用失败？**
- 检查 API Key 是否正确
- 确认网络连接正常
- 查看节点输出的错误信息

**Q: 图片上传失败？**
- 检查图床 URL 是否可访问
- 确认图片格式和大小符合要求

## 开发

### 文件结构

```
ComfyUI_KuAi_Power/
├── nodes/
│   └── Sora2/
│       ├── __init__.py          # 统一导出
│       ├── utils.py             # 工具函数
│       ├── script_generator.py  # 脚本生成节点
│       └── sora2.py            # Sora2 API 节点
├── web/
│   └── kuaipower_panel.js      # 前端面板
├── __init__.py                 # 主入口
├── requirements.txt            # 依赖
└── README.md                   # 本文档
```

### 添加新节点

1. 在 `script_generator.py` 或 `sora2.py` 中定义节点类
2. 在文件末尾的 `NODE_CLASS_MAPPINGS` 中注册
3. 设置正确的 `CATEGORY`（`KuAi/ScriptGenerator` 或 `KuAi/Sora2`）
4. 重启 ComfyUI

## 许可证

MIT License

## 支持

如有问题，请提交 Issue 或查看 [CHECKLIST.md](CHECKLIST.md) 获取详细检查清单。
