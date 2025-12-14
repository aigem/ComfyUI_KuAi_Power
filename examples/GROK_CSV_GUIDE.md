# Grok 批量视频生成 CSV 使用指南

## 概述

使用 CSV 文件可以批量创建多个 Grok 视频生成任务，适合需要生成大量视频的场景。

## CSV 文件格式

### 必需列

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `prompt` | 文本 | 视频生成提示词 | "A cat playing with a ball" |

### 可选列

| 列名 | 类型 | 默认值 | 说明 | 可选值 |
|------|------|--------|------|--------|
| `aspect_ratio` | 文本 | 3:2 | 视频宽高比 | 1:1, 2:3, 3:2 |
| `size` | 文本 | 1080P | 视频分辨率 | 720P, 1080P |
| `image_urls` | 文本 | 空 | 参考图片URL（多个用逗号分隔） | https://example.com/img.jpg |
| `output_prefix` | 文本 | task_N | 输出文件前缀 | my_video |

## 示范文件

### 1. 基础文本生成视频 (grok_batch_basic.csv)

```csv
prompt,aspect_ratio,size,image_urls,output_prefix
"A cute cat playing with a colorful ball in a sunny garden, slow motion, cinematic lighting",3:2,1080P,,cat_playing
"A majestic eagle soaring through the clouds at sunset, aerial view, 4K quality",3:2,1080P,,eagle_sunset
"A dancer performing in the rain, dramatic lighting, close-up shot, artistic style",2:3,1080P,,dancer_rain
"A beautiful landscape with mountains and rivers, time-lapse, golden hour",1:1,720P,,landscape_timelapse
"A sports car driving on a coastal highway, tracking shot, cinematic",3:2,1080P,,car_highway
```

**说明**：
- 5 个不同场景的视频生成任务
- 使用不同的宽高比和分辨率
- 每个任务有独特的输出前缀

### 2. 图片到视频 (grok_batch_with_images.csv)

```csv
prompt,aspect_ratio,size,image_urls,output_prefix
"Animate this image with gentle camera movement and natural lighting",3:2,1080P,https://example.com/image1.jpg,animated_scene_1
"Add dynamic motion to this scene, cinematic style",2:3,1080P,https://example.com/image2.jpg,animated_scene_2
"Transform this image into a video with smooth transitions",1:1,720P,https://example.com/image3.jpg,animated_scene_3
```

**说明**：
- 基于参考图片生成视频
- 每个任务使用一张参考图片
- 提示词描述如何动画化图片

### 3. 中文提示词模板 (grok_batch_template.csv)

```csv
prompt,aspect_ratio,size,image_urls,output_prefix
"示例1: 一只可爱的猫咪在阳光花园里玩彩色球，慢动作，电影级光照",3:2,1080P,,example_1
"示例2: 一只雄鹰在日落时分翱翔云端，航拍视角，4K画质",3:2,1080P,,example_2
"示例3: 舞者在雨中表演，戏剧性光照，特写镜头，艺术风格",2:3,1080P,,example_3
"示例4: 美丽的山川河流风景，延时摄影，黄金时刻",1:1,720P,,example_4
"示例5: 跑车在海岸公路上行驶，跟踪镜头，电影感",3:2,1080P,,example_5
```

**说明**：
- 支持中文提示词
- 可以作为模板修改使用

## 使用步骤

### 步骤 1: 准备 CSV 文件

1. 复制示范文件或创建新文件
2. 编辑提示词和参数
3. 保存为 UTF-8 编码的 CSV 文件

**注意事项**：
- 提示词包含逗号时，必须用双引号包裹
- 空值可以留空或不填
- 文件必须包含表头行

### 步骤 2: 在 ComfyUI 中设置工作流

```
CSVBatchReader → GrokBatchProcessor
├─ csv_path: 你的CSV文件路径
└─ ...
```

**节点连接**：
1. 添加 `CSVBatchReader` 节点
2. 添加 `GrokBatchProcessor` 节点
3. 将 CSVBatchReader 的输出连接到 GrokBatchProcessor 的 `batch_tasks` 输入

### 步骤 3: 配置批量处理器参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| api_key | 留空 | 使用环境变量 KUAI_API_KEY |
| output_dir | ./output/grok_batch | 任务信息保存目录 |
| delay_between_tasks | 2.0 | 任务间延迟（秒） |
| wait_for_completion | false | 是否等待所有任务完成 |
| max_wait_time | 600 | 单个任务最大等待时间（秒） |
| poll_interval | 10 | 轮询间隔（秒） |

### 步骤 4: 执行批量处理

1. 点击 `Queue Prompt` 按钮
2. 查看 ComfyUI 控制台日志
3. 等待所有任务提交完成

### 步骤 5: 查看结果

**输出文件**：
- `output_dir/tasks.json` - 所有任务的列表
- `output_dir/{output_prefix}_{task_id}.json` - 每个任务的详细信息

**任务信息包含**：
- task_id - 任务ID
- prompt - 提示词
- status - 任务状态
- video_url - 视频URL（完成后）
- created_at - 创建时间
- completed_at - 完成时间（如果等待完成）

## 两种处理模式

### 模式 1: 快速提交（推荐）

**配置**：
- `wait_for_completion = false`

**特点**：
- 快速提交所有任务
- 不等待视频生成完成
- 适合大批量任务

**后续操作**：
- 使用 `GrokQueryVideo` 节点查询任务状态
- 或稍后使用任务ID批量查询

### 模式 2: 等待完成

**配置**：
- `wait_for_completion = true`
- `max_wait_time = 600`（根据需要调整）

**特点**：
- 等待每个任务完成后再处理下一个
- 自动获取视频URL
- 耗时较长（每个任务 5-12 分钟）

**适用场景**：
- 少量任务（1-5个）
- 需要立即获取视频URL
- 有充足的等待时间

## 高级用法

### 1. 使用多张参考图片

```csv
prompt,aspect_ratio,size,image_urls,output_prefix
"Create a video from these images",3:2,1080P,"https://example.com/img1.jpg,https://example.com/img2.jpg",multi_image
```

**注意**：多个URL用逗号分隔，整个字段用双引号包裹。

### 2. 动态生成 CSV

使用 Python 脚本生成 CSV：

```python
import csv

prompts = [
    "Scene 1: A cat playing",
    "Scene 2: A dog running",
    "Scene 3: A bird flying",
]

with open('batch.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['prompt', 'aspect_ratio', 'size', 'output_prefix'])
    writer.writeheader()

    for i, prompt in enumerate(prompts, 1):
        writer.writerow({
            'prompt': prompt,
            'aspect_ratio': '3:2',
            'size': '1080P',
            'output_prefix': f'scene_{i}'
        })
```

### 3. 批量查询任务状态

处理完成后，使用 tasks.json 中的任务ID批量查询：

```python
import json
import requests

with open('output/grok_batch/tasks.json', 'r') as f:
    tasks = json.load(f)

for task in tasks:
    task_id = task['task_id']
    # 使用 GrokQueryVideo 节点查询
    # 或使用 API 直接查询
```

## 性能优化建议

### 1. 任务数量
- **小批量**（1-10个）：可以使用 `wait_for_completion = true`
- **中批量**（10-50个）：使用 `wait_for_completion = false`，稍后批量查询
- **大批量**（50+个）：分批处理，避免一次性提交过多任务

### 2. 分辨率选择
- **测试阶段**：使用 720P 快速验证提示词效果
- **正式生成**：使用 1080P 获得最佳画质

### 3. 任务间延迟
- **默认值**：2.0 秒（推荐）
- **快速提交**：0.5 秒（可能触发限流）
- **保守设置**：5.0 秒（更稳定）

### 4. 成本控制
- 使用 720P 可以节省成本和时间
- 先用少量任务测试提示词效果
- 确认效果后再批量生成

## 常见问题

### Q1: CSV 文件编码问题
A: 确保 CSV 文件使用 UTF-8 编码保存，特别是包含中文时。

### Q2: 提示词包含逗号怎么办？
A: 用双引号包裹整个提示词：
```csv
"A scene with trees, mountains, and rivers"
```

### Q3: 如何查看批量处理进度？
A: 查看 ComfyUI 控制台日志，会显示每个任务的处理状态。

### Q4: 任务失败怎么办？
A:
- 检查 CSV 格式是否正确
- 查看控制台错误信息
- 检查 API Key 是否有效
- 验证参数值是否在允许范围内

### Q5: 可以暂停批量处理吗？
A: 不支持暂停，但可以：
- 停止 ComfyUI 执行
- 修改 CSV 文件删除已处理的行
- 重新开始处理

### Q6: 如何获取已完成的视频？
A:
- 查看 `output_dir/tasks.json` 文件
- 找到 `video_url` 字段
- 使用浏览器或下载工具下载视频

## 示例工作流

### 完整的批量处理工作流

```
1. 准备 CSV 文件
   ├─ 编辑提示词
   ├─ 设置参数
   └─ 保存文件

2. ComfyUI 工作流
   ├─ CSVBatchReader
   │  └─ csv_path: examples/grok_batch_basic.csv
   │
   └─ GrokBatchProcessor
      ├─ batch_tasks: (从 CSVBatchReader)
      ├─ api_key: (留空)
      ├─ output_dir: ./output/grok_batch
      ├─ delay_between_tasks: 2.0
      └─ wait_for_completion: false

3. 执行处理
   └─ Queue Prompt

4. 查看结果
   ├─ 控制台日志
   ├─ output/grok_batch/tasks.json
   └─ 各个任务的 JSON 文件

5. 查询任务状态（可选）
   └─ 使用 GrokQueryVideo 节点
```

## 最佳实践

1. **先小后大**：先用 2-3 个任务测试，确认无误后再批量处理
2. **提示词优化**：使用详细的提示词以获得更好的效果
3. **参数一致性**：同一批次使用相同的分辨率和宽高比
4. **输出命名**：使用有意义的 output_prefix 便于管理
5. **定期查询**：对于大批量任务，定期查询任务状态
6. **备份 CSV**：保存原始 CSV 文件以便重新处理

## 相关资源

- **批量处理器节点**：`nodes/Grok/batch_processor.py`
- **CSV 读取器**：`nodes/Utils/csv_reader.py`
- **示范文件目录**：`examples/`
- **详细文档**：`docs/GROK_VIDEO_GUIDE.md`

---

开始使用批量处理，高效创作大量精彩视频！🎬
