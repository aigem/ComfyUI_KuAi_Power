# NanoBanana CSV 批量处理模板

## 📁 可用模板

本目录提供了多个 CSV 模板文件，方便您快速开始批量图像生成任务。

### 1. 空白模板 (nanobana_batch_template_blank.csv)
**用途**: 从零开始创建自定义批量任务

**特点**:
- 只包含列标题
- 适合有经验的用户
- 完全自定义所有参数

**下载**: [nanobana_batch_template_blank.csv](./nanobana_batch_template_blank.csv)

---

### 2. 文生图模板 (nanobana_batch_template_text2image.csv)
**用途**: 批量生成全新图像（无需参考图）

**特点**:
- 包含 3 个示例任务
- 展示不同的应用场景（科幻、风景、产品摄影）
- 展示不同模型的使用方法

**示例任务**:
1. 科幻城市场景
2. 山水风景
3. 产品摄影

**下载**: [nanobana_batch_template_text2image.csv](./nanobana_batch_template_text2image.csv)

---

### 3. 图生图模板 (nanobana_batch_template_image2image.csv)
**用途**: 批量编辑或转换现有图像

**特点**:
- 包含 3 个示例任务
- 展示图像编辑场景（色彩增强、风格转换、光影调整）
- 展示如何使用参考图

**示例任务**:
1. 色彩增强
2. 赛博朋克风格转换
3. 戏剧性光影效果

**下载**: [nanobana_batch_template_image2image.csv](./nanobana_batch_template_image2image.csv)

**重要提示**: 使用前请将 `/path/to/your/imageX.jpg` 替换为您的实际图片路径！

---

### 4. 中文模板 (nanobana_batch_template_chinese.csv)
**用途**: 中文用户友好的批量任务模板

**特点**:
- 包含 5 个示例任务（3个生图 + 2个改图）
- 所有提示词和系统提示词都是中文
- 展示中文任务类型（生图/改图）

**示例任务**:
1. 科幻城市
2. 山水风景画
3. 产品摄影
4. 色彩增强
5. 赛博朋克风格

**下载**: [nanobana_batch_template_chinese.csv](./nanobana_batch_template_chinese.csv)

---

### 5. 完整示例 (nanobana_batch_example.csv)
**用途**: 学习和参考的完整示例

**特点**:
- 包含 6 个示例任务
- 混合中英文
- 展示所有功能和参数

**下载**: [nanobana_batch_example.csv](./nanobana_batch_example.csv)

---

## 📝 CSV 列说明

### 必需列

| 列名 | 说明 | 示例 |
|------|------|------|
| `task_type` | 任务类型 | `generate`, `edit`, `生图`, `改图` |
| `prompt` | 图像生成提示词 | `A futuristic city with flying cars` |

### 可选列（留空则使用默认值）

| 列名 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `system_prompt` | 系统提示词 | 空 | 任意文本 |
| `model_name` | 模型名称 | `gemini-3-pro-image-preview` | `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`, `gemini-2.5-flash-image` |
| `seed` | 随机种子 | `0` (随机) | 0 - 18446744073709551615 |
| `aspect_ratio` | 宽高比 | `1:1` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `image_size` | 图像尺寸 | `2K` | `1K`, `2K`, `4K` (仅 gemini-3-pro-image-preview 和 gemini-3.1-flash-image-preview) |
| `temperature` | 生成温度 | `1.0` | 0.0 - 2.0 |
| `use_search` | 启用搜索 | `true` | `true`, `false` |
| `image_1` ~ `image_6` | 参考图路径 | 空 | 本地图片路径 |
| `output_prefix` | 输出文件前缀 | `task_N` | 任意文本（建议英文） |

---

## 🎯 使用步骤

### 1. 选择合适的模板

根据您的需求选择模板：
- **新手**: 使用 `text2image` 或 `chinese` 模板
- **图像编辑**: 使用 `image2image` 模板
- **自定义**: 使用 `blank` 模板

### 2. 下载并编辑模板

1. 下载模板文件到本地
2. 使用 Excel、Google Sheets 或文本编辑器打开
3. 根据需求修改或添加任务行
4. **重要**: 保存为 UTF-8 编码的 CSV 文件

### 3. 填写参数

#### 文生图任务示例
```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,output_prefix
generate,A magical forest with glowing trees,You are a fantasy artist,gemini-3-pro-image-preview,42,16:9,forest_001
```

#### 图生图任务示例
```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,image_1,output_prefix
edit,Make it more colorful,Enhance colors,gemini-2.5-flash-image,100,1:1,/home/user/photo.jpg,colorful_001
```

### 4. 在 ComfyUI 中使用

1. 添加 `CSVBatchReader` 节点
2. 输入 CSV 文件路径
3. 连接到 `NanoBananaBatchProcessor` 节点
4. 配置 API 密钥和输出目录
5. 运行工作流

---

## 💡 使用技巧

### 1. 系统提示词的作用

系统提示词用于指导 AI 的整体风格和行为：

**好的系统提示词**:
- ✅ `You are a professional product photographer specializing in luxury goods`
- ✅ `Create images in a minimalist, modern style with clean lines`
- ✅ `你是一个专业的概念设计师，擅长科幻和未来主义风格`

**避免**:
- ❌ 太短: `good`, `nice`
- ❌ 太具体: `make it red` (应该放在 prompt 中)

### 2. 种子值的使用

- `seed = 0`: 每次生成不同的随机结果
- `seed = 固定值`: 相同参数生成相似结果
- 批量生成变体: 使用不同种子值（42, 100, 200...）

### 3. 模型选择

**gemini-3-pro-image-preview / gemini-3.1-flash-image-preview**:
- ✅ 支持 Google 搜索增强
- ✅ 支持 image_size 参数 (1K/2K/4K)
- ✅ 更强的理解能力
- ⚠️ 速度较慢

**gemini-2.5-flash-image**:
- ✅ 速度更快
- ✅ 成本更低
- ⚠️ 不支持 image_size 参数
- ⚠️ 不支持搜索增强

### 4. 参考图路径

支持的路径格式：
```csv
# 绝对路径（推荐）
/home/user/images/photo.jpg
C:\Users\Name\Pictures\photo.jpg

# 相对路径
./images/photo.jpg
../photos/photo.jpg

# 用户目录
~/Pictures/photo.jpg
```

**注意事项**:
- Windows 路径可以使用反斜杠 `\` 或正斜杠 `/`
- 路径中有空格时，无需加引号
- 确保文件存在且可读

### 5. 输出文件命名

建议使用有意义的前缀：
```csv
output_prefix
product_watch_v1
concept_car_design_01
portrait_style_cyberpunk
```

生成的文件名格式：
```
{output_prefix}_{timestamp}.png
product_watch_v1_20250113_143022.png
```

---

## ⚠️ 常见错误

### 错误 1: CSV 编码问题
**症状**: 中文乱码或读取失败

**解决方案**:
- Excel: 另存为 → 选择 "CSV UTF-8 (逗号分隔)"
- Google Sheets: 文件 → 下载 → 逗号分隔值 (.csv)
- 文本编辑器: 保存时选择 UTF-8 编码

### 错误 2: 参考图路径错误
**症状**: `图片文件不存在: /path/to/...`

**解决方案**:
- 使用绝对路径
- 检查文件是否存在
- 检查路径拼写是否正确

### 错误 3: 列名错误
**症状**: `无效的任务类型` 或其他参数错误

**解决方案**:
- 确保第一行是列标题
- 列名必须完全匹配（区分大小写）
- 不要修改列标题

### 错误 4: 空行导致错误
**症状**: 某些任务被跳过

**解决方案**:
- 删除 CSV 中的空行
- 确保每行都有 task_type 和 prompt

---

## 📚 更多资源

- **详细使用指南**: [NANOBANA_BATCH_GUIDE.md](../NANOBANA_BATCH_GUIDE.md)
- **项目文档**: [CLAUDE.md](../CLAUDE.md)
- **API 规范**: [API_SPECIFICATION.md](../API_SPECIFICATION.md)

---

## 🔄 模板更新日志

### 2025-12-13
- ✅ 创建空白模板
- ✅ 创建文生图模板
- ✅ 创建图生图模板
- ✅ 创建中文模板
- ✅ 创建完整示例

---

**文档版本**: 1.0
**最后更新**: 2025-12-13
