# NanoBanana 批量处理使用指南

## 📋 概述

NanoBanana 批量处理功能允许您通过 CSV 文件批量生成或编辑图像，大幅提高工作效率。

## 🎯 新增功能

### 1. 系统提示词支持
两个 NanoBanana 节点现在都支持 `system_prompt` 参数，用于指导 AI 的行为和风格。

**示例**:
- "You are a professional concept artist specializing in sci-fi designs"
- "Create images in a minimalist, modern style"
- "你是一个专业的产品摄影师，擅长拍摄高端商品"

### 2. 批量处理系统
通过 CSV 文件批量处理图像生成任务，支持：
- ✅ 批量文生图
- ✅ 批量图生图（最多6张参考图）
- ✅ 自定义每个任务的所有参数
- ✅ 自动保存图像和元数据
- ✅ 详细的处理报告

---

## 📝 CSV 文件格式

### 必需列

| 列名 | 说明 | 可选值 | 示例 |
|------|------|--------|------|
| `task_type` | 任务类型 | `generate`/`生图` 或 `edit`/`改图` | `generate` |
| `prompt` | 图像生成提示词 | 任意文本 | `A futuristic city` |

### 可选列

| 列名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `system_prompt` | 系统提示词 | 空 | `You are a creative artist` |
| `model_name` | 模型名称 | `gemini-3-pro-image-preview` | `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`, `gemini-2.5-flash-image` |
| `seed` | 随机种子 | `0`（随机） | `42` |
| `aspect_ratio` | 宽高比 | `1:1` | `16:9`, `9:16`, `3:2` 等 |
| `image_size` | 图像尺寸 | `2K` | `1K`, `2K`, `4K` |
| `temperature` | 生成温度 | `1.0` | `0.0` - `2.0` |
| `use_search` | 启用搜索 | `true` | `true`/`false` |
| `image_1` ~ `image_6` | 参考图路径 | 空 | `/path/to/image.jpg` |
| `output_prefix` | 输出文件前缀 | `task_N` | `city_001` |

### 参考图路径说明

支持以下路径格式：
- **绝对路径**: `/home/user/images/photo.jpg`
- **相对路径**: `./images/photo.jpg`
- **用户目录**: `~/Pictures/photo.jpg`
- **Windows路径**: `C:\Users\Name\Pictures\photo.jpg`

**注意**:
- 只有 `task_type` 为 `edit`/`改图` 时才需要提供参考图
- 最多支持 6 张参考图（`image_1` 到 `image_6`）
- 图片格式支持: JPG, PNG, WebP 等常见格式

---

## 📄 CSV 示例

### 示例 1: 纯文生图批量任务

```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,image_size,temperature,use_search,output_prefix
generate,A futuristic city with flying cars,You are a creative sci-fi artist,gemini-3-pro-image-preview,42,16:9,2K,1.0,true,city_001
generate,A serene mountain landscape at sunset,Create beautiful natural scenes,gemini-2.5-flash-image,100,1:1,2K,0.9,false,mountain_001
generate,A cyberpunk street at night,Cyberpunk aesthetic specialist,gemini-3-pro-image-preview,200,9:16,4K,1.2,true,cyberpunk_001
```

### 示例 2: 图生图批量任务

```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,image_size,temperature,use_search,image_1,image_2,output_prefix
edit,Make the colors more vibrant,Enhance image quality,gemini-3-pro-image-preview,300,1:1,2K,0.8,false,/home/user/images/photo1.jpg,,vibrant_001
edit,Transform into cyberpunk style,Apply cyberpunk aesthetic,gemini-2.5-flash-image,400,16:9,2K,1.0,false,/home/user/images/photo2.jpg,/home/user/images/photo3.jpg,cyber_001
```

### 示例 3: 混合任务（中英文）

```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,output_prefix
生图,一个未来感十足的机器人,你是一个专业的概念设计师,gemini-3-pro-image-preview,0,1:1,robot_001
改图,让这张图片更加明亮和温暖,增强图片的温暖感,gemini-2.5-flash-image,500,9:16,warm_001
generate,A magical forest with glowing trees,Fantasy art specialist,gemini-3-pro-image-preview,600,16:9,forest_001
```

---

## 🔧 ComfyUI 工作流设置

### 节点连接

```
CSVBatchReader
    ↓ (批量任务数据)
NanoBananaBatchProcessor
    ↓ (处理结果, 输出目录)
输出显示
```

### 详细步骤

1. **添加 CSV 批量读取器节点**
   - 节点名称: `CSVBatchReader`
   - 分类: `KuAi/Utils`
   - 参数: `csv_path` - CSV 文件的完整路径

2. **添加 NanoBanana 批量处理器节点**
   - 节点名称: `NanoBananaBatchProcessor`
   - 分类: `KuAi/NanoBanana`
   - 参数:
     - `batch_tasks`: 连接到 CSVBatchReader 的输出
     - `api_base`: API 端点地址（默认: `https://api.kuai.host`）
     - `api_key`: API 密钥（或使用环境变量 `KUAI_API_KEY`）
     - `output_dir`: 输出目录（默认: `./output/nanobana_batch`）
     - `delay_between_tasks`: 任务间延迟秒数（默认: 2.0）

3. **连接节点**
   - 将 `CSVBatchReader` 的 `批量任务数据` 输出连接到 `NanoBananaBatchProcessor` 的 `batch_tasks` 输入

4. **运行工作流**
   - 点击 "Queue Prompt" 开始批量处理
   - 查看控制台输出了解处理进度

---

## 📊 输出结果

### 文件结构

```
output/nanobana_batch/
├── city_001_20250101_120000.png          # 生成的图像
├── city_001_20250101_120000_metadata.json # 元数据
├── mountain_001_20250101_120030.png
├── mountain_001_20250101_120030_metadata.json
└── ...
```

### 元数据文件内容

```json
{
  "task_type": "generate",
  "prompt": "A futuristic city with flying cars",
  "system_prompt": "You are a creative sci-fi artist",
  "model_name": "gemini-3-pro-image-preview",
  "seed": 42,
  "thinking": "AI 的思考过程...",
  "grounding": "引用来源信息..."
}
```

### 处理报告

批量处理完成后，会在控制台输出详细报告：

```
============================================================
批量处理完成
总任务数: 10
成功: 9
失败: 1

失败任务详情:
  - 任务 5 (行 6): 图片文件不存在: /path/to/missing.jpg
============================================================
```

---

## ⚙️ 高级配置

### 1. 任务间延迟

为避免 API 速率限制，可以设置任务间延迟：

```python
delay_between_tasks = 2.0  # 每个任务之间等待 2 秒
```

### 2. 环境变量配置

在 `.env` 文件中配置 API 密钥：

```bash
KUAI_API_KEY=your_api_key_here
```

### 3. 输出目录自定义

可以为不同的批次指定不同的输出目录：

```python
output_dir = "./output/batch_20250101"
output_dir = "./output/product_images"
output_dir = "./output/concept_art"
```

---

## 🎨 使用场景

### 场景 1: 产品图批量生成

```csv
task_type,prompt,system_prompt,model_name,aspect_ratio,output_prefix
generate,Professional product photo of a luxury watch,You are a professional product photographer,gemini-3-pro-image-preview,1:1,watch_001
generate,Professional product photo of a smartphone,You are a professional product photographer,gemini-3-pro-image-preview,1:1,phone_001
generate,Professional product photo of headphones,You are a professional product photographer,gemini-3-pro-image-preview,1:1,headphones_001
```

### 场景 2: 风格迁移批量处理

```csv
task_type,prompt,system_prompt,model_name,image_1,output_prefix
edit,Transform into oil painting style,Apply classical oil painting techniques,gemini-3-pro-image-preview,./photos/photo1.jpg,oil_001
edit,Transform into oil painting style,Apply classical oil painting techniques,gemini-3-pro-image-preview,./photos/photo2.jpg,oil_002
edit,Transform into oil painting style,Apply classical oil painting techniques,gemini-3-pro-image-preview,./photos/photo3.jpg,oil_003
```

### 场景 3: 概念设计批量创作

```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,output_prefix
generate,Futuristic vehicle design concept,You are an industrial designer,gemini-3-pro-image-preview,100,16:9,vehicle_v1
generate,Futuristic vehicle design concept,You are an industrial designer,gemini-3-pro-image-preview,200,16:9,vehicle_v2
generate,Futuristic vehicle design concept,You are an industrial designer,gemini-3-pro-image-preview,300,16:9,vehicle_v3
```

---

## ❗ 常见问题

### Q1: CSV 文件读取失败

**原因**: 文件编码问题或路径错误

**解决方案**:
- 确保 CSV 文件使用 UTF-8 编码保存
- 使用绝对路径或确保相对路径正确
- 检查文件扩展名是否为 `.csv`

### Q2: 参考图加载失败

**原因**: 图片路径不存在或格式不支持

**解决方案**:
- 检查图片路径是否正确
- 使用绝对路径避免路径问题
- 确保图片格式为 JPG, PNG, WebP 等常见格式

### Q3: API 调用失败

**原因**: API 密钥无效或网络问题

**解决方案**:
- 检查 API 密钥是否正确配置
- 确认网络连接正常
- 检查 API 配额是否充足

### Q4: 批量处理中断

**原因**: 某个任务失败导致整个批次停止

**解决方案**:
- 批量处理器会自动跳过失败的任务并继续处理
- 查看处理报告了解失败原因
- 修复失败任务后重新运行

---

## 📚 参考资料

### CSV 文件模板

项目中提供了示例 CSV 文件：
- 路径: `/workspaces/ComfyUI_KuAi_Power/workflows/nanobana_batch_example.csv`
- 包含各种任务类型的示例

### 相关文档

- [CLAUDE.md](./CLAUDE.md) - 项目完整文档
- [API_SPECIFICATION.md](./API_SPECIFICATION.md) - API 规范
- [NANO_BANANA_API_UPDATE.md](./NANO_BANANA_API_UPDATE.md) - API 更新说明

---

## 🔄 更新日志

### 2025-12-13
- ✅ 添加 `system_prompt` 参数支持
- ✅ 实现 CSV 批量读取器
- ✅ 实现 NanoBanana 批量处理器
- ✅ 支持文生图和图生图批量处理
- ✅ 自动保存图像和元数据
- ✅ 详细的处理报告和错误处理

---

**文档版本**: 1.0
**最后更新**: 2025-12-13
