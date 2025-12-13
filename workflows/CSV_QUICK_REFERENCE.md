# CSV 批量处理快速参考

## 📋 CSV 列标题（复制粘贴使用）

```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,image_size,temperature,use_search,image_1,image_2,image_3,image_4,image_5,image_6,output_prefix
```

---

## 🎯 必需列

| 列名 | 说明 | 示例 |
|------|------|------|
| `task_type` | 任务类型 | `generate`, `edit`, `生图`, `改图` |
| `prompt` | 提示词 | `A futuristic city` |

---

## ⚙️ 可选列（默认值）

| 列名 | 默认值 | 可选值 |
|------|--------|--------|
| `system_prompt` | 空 | 任意文本 |
| `model_name` | `gemini-3-pro-image-preview` | `gemini-2.5-flash-image` |
| `seed` | `0` | 0 - 18446744073709551615 |
| `aspect_ratio` | `1:1` | `1:1`, `16:9`, `9:16`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `21:9` |
| `image_size` | `2K` | `1K`, `2K`, `4K` |
| `temperature` | `1.0` | `0.0` - `2.0` |
| `use_search` | `true` | `true`, `false` |
| `image_1` ~ `image_6` | 空 | 本地图片路径 |
| `output_prefix` | `task_N` | 任意文本 |

---

## 📝 快速示例

### 文生图（最简单）
```csv
task_type,prompt
generate,A futuristic city with flying cars
```

### 文生图（完整参数）
```csv
task_type,prompt,system_prompt,model_name,seed,aspect_ratio,output_prefix
generate,A magical forest,You are a fantasy artist,gemini-3-pro-image-preview,42,16:9,forest_001
```

### 图生图（单张参考图）
```csv
task_type,prompt,model_name,image_1,output_prefix
edit,Make it more colorful,gemini-2.5-flash-image,/path/to/photo.jpg,colorful_001
```

### 图生图（多张参考图）
```csv
task_type,prompt,image_1,image_2,image_3,output_prefix
edit,Combine these styles,/path/to/img1.jpg,/path/to/img2.jpg,/path/to/img3.jpg,combined_001
```

---

## 🌐 路径格式

### Windows
```csv
C:\Users\Name\Pictures\photo.jpg
C:/Users/Name/Pictures/photo.jpg
```

### macOS/Linux
```csv
/home/user/images/photo.jpg
~/Pictures/photo.jpg
./images/photo.jpg
```

---

## ⚡ 快速开始

1. **下载模板**: 选择合适的 CSV 模板
2. **填写数据**: 添加您的任务行
3. **保存文件**: UTF-8 编码保存
4. **在 ComfyUI 中使用**:
   - 添加 `CSVBatchReader` 节点
   - 添加 `NanoBananaBatchProcessor` 节点
   - 连接节点并运行

---

## 📦 可用模板

| 模板 | 用途 | 文件名 |
|------|------|--------|
| 空白模板 | 自定义任务 | `nanobana_batch_template_blank.csv` |
| 文生图模板 | 批量生成新图像 | `nanobana_batch_template_text2image.csv` |
| 图生图模板 | 批量编辑图像 | `nanobana_batch_template_image2image.csv` |
| 中文模板 | 中文用户友好 | `nanobana_batch_template_chinese.csv` |

---

## ❗ 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 中文乱码 | 编码问题 | 保存为 UTF-8 编码 |
| 图片不存在 | 路径错误 | 使用绝对路径 |
| 列名错误 | 拼写错误 | 复制标准列标题 |
| 任务跳过 | 空行 | 删除空行 |

---

## 📚 详细文档

- **完整指南**: [NANOBANA_BATCH_GUIDE.md](../NANOBANA_BATCH_GUIDE.md)
- **模板说明**: [CSV_TEMPLATES_README.md](./CSV_TEMPLATES_README.md)
- **项目文档**: [CLAUDE.md](../CLAUDE.md)

---

**版本**: 1.0 | **更新**: 2025-12-13
