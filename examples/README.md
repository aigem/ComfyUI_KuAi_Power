# Grok 批量视频生成示例

## 📁 文件说明

### CSV 示范文件

1. **grok_batch_basic.csv** - 基础文本生成视频
   - 5 个不同场景的视频任务
   - 包含各种宽高比和分辨率
   - 适合快速测试和学习

2. **grok_batch_with_images.csv** - 图片到视频生成
   - 3 个基于参考图片的任务
   - 演示如何使用 image_urls 参数
   - 需要替换为实际的图片URL

3. **grok_batch_template.csv** - 中文提示词模板
   - 5 个中文提示词示例
   - 可以直接复制修改使用
   - 展示中文提示词的写法

### 文档

- **GROK_CSV_GUIDE.md** - 完整的 CSV 批量处理使用指南
  - CSV 格式详细说明
  - 使用步骤和工作流
  - 高级用法和最佳实践
  - 常见问题解答

## 🚀 快速开始

### 1. 选择示范文件

```bash
# 复制示范文件
cp examples/grok_batch_basic.csv my_videos.csv

# 编辑文件
nano my_videos.csv
```

### 2. 在 ComfyUI 中使用

```
工作流:
CSVBatchReader → GrokBatchProcessor
├─ csv_path: my_videos.csv
└─ output_dir: ./output/my_batch
```

### 3. 执行生成

1. 点击 Queue Prompt
2. 查看控制台日志
3. 等待任务提交完成
4. 查看 output_dir/tasks.json

## 📝 CSV 格式

### 必需列
- `prompt` - 视频生成提示词

### 可选列
- `aspect_ratio` - 宽高比（1:1, 2:3, 3:2）
- `size` - 分辨率（720P, 1080P）
- `image_urls` - 参考图片URL
- `output_prefix` - 输出文件前缀

### 示例

```csv
prompt,aspect_ratio,size,image_urls,output_prefix
"A cat playing with a ball",3:2,1080P,,cat_video
"A dog running in the park",2:3,720P,,dog_video
```

## 💡 提示词技巧

### 好的提示词包含：
1. **主体** - 描述主要对象
2. **动作** - 描述发生的事情
3. **环境** - 描述场景和背景
4. **风格** - 描述视觉风格
5. **镜头** - 描述拍摄方式

### 示例对比

❌ **差**: `cat`

✅ **好**: `A fluffy white cat playing with a red ball in a sunny garden, slow motion, cinematic lighting`

### 常用关键词

**镜头运动**:
- `slow motion` - 慢动作
- `tracking shot` - 跟踪镜头
- `aerial view` - 航拍视角
- `close-up` - 特写

**光照效果**:
- `cinematic lighting` - 电影级光照
- `golden hour` - 黄金时刻
- `dramatic lighting` - 戏剧性光照

**视觉风格**:
- `photorealistic` - 照片级真实
- `4K quality` - 4K 画质
- `artistic style` - 艺术风格

## 📊 处理模式

### 快速提交（推荐）
- 快速提交所有任务
- 不等待视频生成完成
- 适合大批量任务

**配置**:
```
wait_for_completion = false
```

### 等待完成
- 等待每个任务完成
- 自动获取视频URL
- 适合少量任务

**配置**:
```
wait_for_completion = true
max_wait_time = 600
```

## 🎯 使用场景

### 场景 1: 批量生成产品视频
```csv
prompt,aspect_ratio,size,output_prefix
"Product A showcase, rotating view, studio lighting",3:2,1080P,product_a
"Product B demo, close-up details, professional",3:2,1080P,product_b
"Product C features, dynamic presentation",3:2,1080P,product_c
```

### 场景 2: 社交媒体内容
```csv
prompt,aspect_ratio,size,output_prefix
"Trendy fashion scene, urban style",2:3,1080P,fashion_1
"Food preparation, appetizing view",2:3,1080P,food_1
"Travel destination, scenic beauty",2:3,1080P,travel_1
```

### 场景 3: 教育内容
```csv
prompt,aspect_ratio,size,output_prefix
"Science experiment demonstration",3:2,1080P,science_1
"Historical event recreation",3:2,1080P,history_1
"Math concept visualization",3:2,1080P,math_1
```

## 📚 更多资源

- **详细文档**: `GROK_CSV_GUIDE.md`
- **视频生成指南**: `../docs/GROK_VIDEO_GUIDE.md`
- **快速开始**: `../GROK_QUICK_START.md`
- **测试文件**: `../test/test_grok_batch.py`

## ⚙️ 参数建议

| 用途 | aspect_ratio | size | 说明 |
|------|--------------|------|------|
| 抖音/快手 | 2:3 | 1080P | 竖屏高清 |
| YouTube/B站 | 3:2 | 1080P | 横屏高清 |
| Instagram | 1:1 | 1080P | 正方形 |
| 快速测试 | 3:2 | 720P | 节省时间 |

## 🐛 常见问题

### Q: CSV 文件编码问题？
A: 确保使用 UTF-8 编码保存，特别是包含中文时。

### Q: 提示词包含逗号怎么办？
A: 用双引号包裹整个提示词。

### Q: 如何查看批量处理进度？
A: 查看 ComfyUI 控制台日志。

### Q: 任务失败怎么办？
A: 检查 CSV 格式、API Key 和参数值。

## 🎉 开始使用

1. 选择或创建 CSV 文件
2. 在 ComfyUI 中设置工作流
3. 配置批量处理器参数
4. 执行并查看结果

祝你批量创作愉快！🎬
