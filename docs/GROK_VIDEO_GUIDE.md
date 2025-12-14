# Grok 视频生成节点使用指南

## 概述

Grok 视频生成节点集成了 Grok-Video-3 模型，提供高质量的 AI 视频生成能力。支持文本到视频、图片到视频等多种生成模式，适用于创意视频制作、产品展示、内容创作等场景。

## 节点列表

### 1. 🤖 Grok 创建视频 (GrokCreateVideo)

创建 Grok 视频生成任务，返回任务ID用于后续查询。

**适用场景**：
- 需要手动控制任务查询时机
- 批量提交多个视频生成任务
- 与其他节点组合使用的工作流

### 2. 🔍 Grok 查询视频 (GrokQueryVideo)

查询已创建的视频生成任务状态和结果。

**适用场景**：
- 检查任务进度
- 获取已完成的视频URL
- 调试和监控任务状态

### 3. ⚡ Grok 一键生成视频 (GrokCreateAndWait)

创建任务并自动等待完成，一步到位获取视频结果。

**适用场景**：
- 快速生成单个视频
- 简化工作流程
- 实时预览生成结果

### 4. 📦 Grok 批量处理器 (GrokBatchProcessor)

通过 CSV 文件批量创建多个视频生成任务。

**适用场景**：
- 批量生成大量视频
- 自动化视频制作流程
- 基于数据驱动的视频生成

**详细文档**：参见 `examples/GROK_CSV_GUIDE.md`

## 参数说明

### 必需参数

#### prompt (提示词)
- **类型**：多行文本
- **说明**：描述要生成的视频内容
- **示例**：
  ```
  A majestic cat playing with a colorful ball in a sunny garden,
  slow motion, cinematic lighting, 4K quality
  ```
- **提示**：
  - 使用详细的描述以获得更好的效果
  - 可以包含镜头运动、光照、风格等细节
  - 支持中英文提示词

#### aspect_ratio (宽高比)
- **类型**：下拉选择
- **选项**：
  - `1:1` - 正方形（适合社交媒体）
  - `2:3` - 竖屏（适合手机短视频）
  - `3:2` - 横屏（适合桌面播放）
- **默认值**：`3:2`

#### size (分辨率)
- **类型**：下拉选择
- **选项**：
  - `720P` - 标清（生成速度快，成本低）
  - `1080P` - 高清（画质更好，推荐）
- **默认值**：`1080P`

#### api_key (API密钥)
- **类型**：文本
- **说明**：kuai.host API密钥
- **获取方式**：https://api.kuai.host/register?aff=z2C8
- **提示**：
  - 可以留空使用环境变量 `KUAI_API_KEY`
  - 建议使用环境变量以保护密钥安全

### 可选参数

#### image_urls (参考图片URL)
- **类型**：多行文本
- **说明**：用于图片到视频生成的参考图片
- **格式**：多个URL用逗号、分号或换行分隔
- **示例**：
  ```
  https://example.com/image1.jpg
  https://example.com/image2.png
  ```
- **提示**：
  - 支持 JPEG、PNG、WebP 格式
  - 可以使用 KuAi 图片上传节点获取URL
  - 留空则为纯文本生成视频

#### max_wait_time (最大等待时间)
- **类型**：整数
- **单位**：秒
- **范围**：60-1800
- **默认值**：600（10分钟）
- **说明**：仅用于 `GrokCreateAndWait` 节点

#### poll_interval (轮询间隔)
- **类型**：整数
- **单位**：秒
- **范围**：5-60
- **默认值**：10
- **说明**：仅用于 `GrokCreateAndWait` 节点

## 返回值

### GrokCreateVideo 返回值
1. **任务ID** (STRING) - 用于查询任务状态
2. **状态** (STRING) - 任务初始状态（通常为 `processing`）
3. **增强提示词** (STRING) - AI 优化后的提示词（可能为空）

### GrokQueryVideo 返回值
1. **任务ID** (STRING) - 任务标识符
2. **状态** (STRING) - 任务状态
   - `pending` - 等待中
   - `processing` - 生成中
   - `completed` - 已完成
   - `failed` - 失败
3. **视频URL** (STRING) - 生成的视频下载链接（完成后可用）
4. **增强提示词** (STRING) - AI 优化后的提示词

### GrokCreateAndWait 返回值
同 `GrokQueryVideo`，但保证返回时任务已完成或失败。

## 使用示例

### 示例 1：基础文本生成视频

**工作流**：
```
GrokCreateAndWait
├─ prompt: "A beautiful sunset over the ocean with waves crashing"
├─ aspect_ratio: 3:2
├─ size: 1080P
└─ api_key: (使用环境变量)
```

**结果**：直接获得视频URL，可用于下载或预览。

### 示例 2：图片到视频生成

**工作流**：
```
ImageUpload → GrokCreateAndWait
              ├─ prompt: "Animate this image with gentle camera movement"
              ├─ image_urls: (从 ImageUpload 获取)
              ├─ aspect_ratio: 2:3
              └─ size: 1080P
```

**结果**：基于上传的图片生成动态视频。

### 示例 3：手动控制任务流程

**工作流**：
```
GrokCreateVideo → GrokQueryVideo
├─ prompt: "..."    ├─ task_id: (从 CreateVideo 获取)
└─ ...              └─ api_key: ...
```

**优势**：
- 可以在等待期间执行其他操作
- 适合批量任务管理
- 更灵活的错误处理

### 示例 4：批量生成视频

**工作流**：
```
CSVBatchReader → GrokBatchProcessor
├─ csv_path: examples/grok_batch_basic.csv
└─ ...
```

**CSV 格式**：
```csv
prompt,aspect_ratio,size,image_urls,output_prefix
"Cat playing with ball",3:2,1080P,,cat_video
"Dog running in park",2:3,720P,,dog_video
"Bird flying in sky",1:1,1080P,,bird_video
```

**详细说明**：参见 `examples/GROK_CSV_GUIDE.md`

## 最佳实践

### 提示词编写技巧

1. **详细描述**：包含主体、动作、环境、风格
   ```
   好：A fluffy white cat playing with a red ball in a sunny garden,
       slow motion, cinematic lighting, shallow depth of field

   差：cat playing
   ```

2. **镜头语言**：使用电影术语增强效果
   - `slow motion` - 慢动作
   - `cinematic lighting` - 电影级光照
   - `aerial view` - 航拍视角
   - `close-up` - 特写
   - `tracking shot` - 跟踪镜头

3. **风格指定**：明确视觉风格
   - `photorealistic` - 照片级真实
   - `anime style` - 动漫风格
   - `watercolor painting` - 水彩画风格
   - `3D render` - 3D渲染

### 参数选择建议

| 用途 | aspect_ratio | size | 说明 |
|------|--------------|------|------|
| 抖音/快手短视频 | 2:3 | 1080P | 竖屏高清 |
| YouTube/B站 | 3:2 | 1080P | 横屏高清 |
| Instagram | 1:1 | 1080P | 正方形 |
| 快速预览 | 3:2 | 720P | 节省时间和成本 |

### 性能优化

1. **使用 720P 进行测试**：在确定提示词效果前使用低分辨率
2. **合理设置等待时间**：
   - 720P 视频：建议 300-600 秒
   - 1080P 视频：建议 600-900 秒
3. **批量任务**：使用 `GrokCreateVideo` + 定时查询，避免长时间阻塞

### 错误处理

常见错误及解决方案：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| API Key 未配置 | 未设置密钥 | 设置环境变量或节点参数 |
| 任务超时 | 生成时间过长 | 增加 `max_wait_time` 或使用手动查询 |
| 任务失败 | 提示词违规或服务异常 | 检查提示词内容，重试任务 |
| 图片URL无效 | 图片链接失效 | 使用 KuAi 图片上传节点 |

## API 说明

### 创建视频端点
- **URL**：`POST https://api.kuai.host/v1/video/create`
- **模型**：`grok-video-3`
- **超时**：30秒（仅提交任务）

### 查询视频端点
- **URL**：`GET https://api.kuai.host/v1/video/query`
- **参数**：`id` (任务ID)
- **超时**：30秒

### 生成时间
- **720P**：通常 3-8 分钟
- **1080P**：通常 5-12 分钟
- **实际时间**：取决于服务器负载和视频复杂度

## 常见问题

### Q1: 视频生成需要多长时间？
A: 通常 5-12 分钟，取决于分辨率和服务器负载。建议使用 `GrokCreateAndWait` 节点自动等待。

### Q2: 可以使用本地图片吗？
A: 需要先使用 `KuAi 图片上传` 节点将本地图片上传到云端，获取URL后再使用。

### Q3: 如何查看任务进度？
A: 使用 `GrokQueryVideo` 节点定期查询，或查看 ComfyUI 控制台日志。

### Q4: 生成失败怎么办？
A: 检查：
1. API Key 是否有效
2. 提示词是否符合内容政策
3. 网络连接是否正常
4. 使用 `GrokQueryVideo` 查看详细错误信息

### Q5: 支持哪些视频时长？
A: Grok-Video-3 生成的视频时长由模型自动决定，通常为 5-10 秒。

### Q6: 可以指定视频风格吗？
A: 可以在提示词中添加风格描述，如 "cinematic style"、"anime style" 等。

## 技术细节

### 节点实现
- **位置**：`/workspaces/ComfyUI_KuAi_Power/nodes/Grok/grok.py`
- **依赖**：`requests`、`kuai_utils`
- **分类**：`KuAi/Grok`

### 轮询机制
`GrokCreateAndWait` 使用轮询机制等待任务完成：
1. 提交任务获取 task_id
2. 每隔 `poll_interval` 秒查询一次状态
3. 状态为 `completed` 时返回结果
4. 超过 `max_wait_time` 抛出超时错误

### 错误处理
- 所有 API 错误都会转换为用户友好的中文错误消息
- 网络错误会自动重试（根据 HTTP_RETRY 配置）
- 超时错误会保留 task_id 供后续查询

## 更新日志

### 2025-12-14
- ✅ 初始版本发布
- ✅ 支持 Grok-Video-3 模型
- ✅ 实现创建、查询、一键生成三个节点
- ✅ 支持文本到视频和图片到视频
- ✅ 完整的中文标签和错误提示
- ✅ 集成到 KuAi Power 快捷面板

## 相关资源

- **API 文档**：https://api.kuai.host/docs
- **注册账号**：https://api.kuai.host/register?aff=z2C8
- **视频教程**：https://www.bilibili.com/video/BV1umCjBqEpt/
- **问题反馈**：https://github.com/anthropics/claude-code/issues

## 许可证

本节点遵循 ComfyUI_KuAi_Power 插件的许可证。
