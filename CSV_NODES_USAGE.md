# CSV 节点使用指南

## 问题解决

之前的 `IMAGEUPLOAD` 类型导致节点无法创建，错误信息：
```
Error: Image upload widget requires imageInputName augmentation
```

**原因**: `IMAGEUPLOAD` 是 ComfyUI 专门为图片上传设计的类型，需要特殊的配置和增强（augmentation），不能直接用于 CSV 文件上传。

**解决方案**: 移除 `IMAGEUPLOAD` 参数，只使用简单的 `STRING` 类型输入文件路径。

## 节点配置

### CSVBatchReader（CSV 批量读取器）

**参数**:
- `csv_path` (STRING, 可选): CSV 文件路径

**返回**:
- `批量任务数据` (STRING): JSON 格式的任务列表

### CSVViewer（CSV 查看器）

**参数**:
- `csv_path` (STRING, 可选): CSV 文件路径
- `max_rows` (INT, 可选): 最多显示的行数（默认 100）

**返回**:
- `表格数据` (STRING): JSON 格式的表格数据
- **UI 显示**: 在节点中直接显示格式化的表格

## 使用方法

### 方法 1: 使用文件名（推荐）

1. **复制文件到 input 目录**:
   ```bash
   # 将 CSV 文件复制到 ComfyUI 的 input 目录
   cp myfile.csv /path/to/ComfyUI/input/
   ```

2. **添加节点**:
   - 在 ComfyUI 中添加 `CSVBatchReader` 或 `CSVViewer` 节点

3. **输入文件名**:
   - 在 `csv_path` 参数中输入文件名：`myfile.csv`
   - 节点会自动从 input 目录查找文件

4. **执行工作流**:
   - 点击 "Queue Prompt" 执行

### 方法 2: 使用完整路径

1. **添加节点**:
   - 在 ComfyUI 中添加节点

2. **输入完整路径**:
   - 在 `csv_path` 参数中输入完整路径
   - Windows: `C:/Users/username/data/myfile.csv`
   - Linux/Mac: `/home/username/data/myfile.csv`

3. **执行工作流**:
   - 点击 "Queue Prompt" 执行

### 方法 3: 使用相对路径

1. **添加节点**:
   - 在 ComfyUI 中添加节点

2. **输入相对路径**:
   - 相对于 ComfyUI 工作目录的路径
   - 例如: `data/myfile.csv`

3. **执行工作流**:
   - 点击 "Queue Prompt" 执行

## 路径处理逻辑

节点会智能处理文件路径：

```python
# 1. 如果是绝对路径，直接使用
/path/to/file.csv  →  /path/to/file.csv

# 2. 如果是相对路径，尝试从 input 目录查找
myfile.csv  →  ComfyUI/input/myfile.csv

# 3. 如果 input 目录中找不到，使用原始路径
data/file.csv  →  data/file.csv
```

## CSV 文件格式

### 批量图像生成任务

```csv
task_type,prompt,model_name,seed,aspect_ratio
generate,A futuristic city at sunset,gemini-3-pro-image-preview,42,16:9
generate,A cute cat playing with yarn,gemini-2.5-flash-image,0,1:1
generate,Mountain landscape with lake,gemini-3-pro-image-preview,123,9:16
```

### 批量图像编辑任务

```csv
task_type,prompt,image_1,seed,temperature
edit,Make the sky more dramatic,/path/to/image1.jpg,42,1.0
edit,Add more vibrant colors,/path/to/image2.jpg,0,0.8
edit,Enhance the lighting,/path/to/image3.jpg,123,1.2
```

## 工作流示例

### 示例 1: 批量图像生成

```
CSVBatchReader
  ├─ csv_path: "batch_tasks.csv"
  └─ 输出: 批量任务数据
       ↓
NanoBananaBatchProcessor
  ├─ batch_tasks: (连接到 CSVBatchReader)
  ├─ api_key: "your_api_key"
  └─ 输出: 处理结果
```

### 示例 2: CSV 内容查看

```
CSVViewer
  ├─ csv_path: "data.csv"
  ├─ max_rows: 100
  └─ 输出: 表格数据 + UI 显示
```

## 错误处理

### 错误 1: 文件不存在

```
FileNotFoundError: CSV 文件不存在: myfile.csv

请检查：
1. 文件路径是否正确
2. 文件是否已上传到 ComfyUI/input/ 目录
3. 文件名是否包含正确的扩展名 (.csv)
```

**解决方法**:
- 检查文件是否在 input 目录
- 确认文件名拼写正确
- 确认文件扩展名为 `.csv`

### 错误 2: 未输入路径

```
ValueError: 请输入 CSV 文件路径。

使用方法：
1. 将 CSV 文件复制到 ComfyUI/input/ 目录
2. 在 'csv_path' 中输入文件名（如 'myfile.csv'）
3. 或输入完整路径（如 '/path/to/file.csv'）
```

**解决方法**:
- 在 `csv_path` 参数中输入文件路径

### 错误 3: 文件格式错误

```
ValueError: 文件必须是 CSV 格式: myfile.txt
```

**解决方法**:
- 确保文件扩展名为 `.csv`
- 确保文件内容是有效的 CSV 格式

## 常见问题

### Q1: 为什么移除了文件上传功能？

**答**: `IMAGEUPLOAD` 类型需要特殊的配置（imageInputName augmentation），不能直接用于 CSV 文件。使用文件路径输入更简单、更可靠。

### Q2: 如何上传 CSV 文件？

**答**:
- 方法 1: 手动复制文件到 `ComfyUI/input/` 目录
- 方法 2: 使用 ComfyUI 的文件管理器（如果有）
- 方法 3: 使用完整路径直接访问文件

### Q3: 支持哪些路径格式？

**答**:
- ✅ 绝对路径: `/home/user/file.csv`
- ✅ 相对路径: `file.csv`（从 input 目录查找）
- ✅ Windows 路径: `C:/Users/user/file.csv`
- ✅ 子目录: `data/file.csv`

### Q4: CSV 文件必须在 input 目录吗？

**答**: 不是必须的。你可以：
- 将文件放在 input 目录，只输入文件名
- 或使用完整路径访问任何位置的文件

### Q5: 如何查看 CSV 文件内容？

**答**: 使用 `CSVViewer` 节点：
1. 添加 CSVViewer 节点
2. 输入文件路径
3. 执行工作流
4. 表格会直接显示在节点中

## 技术细节

### 参数类型

```python
# CSVBatchReader
INPUT_TYPES = {
    "required": {},
    "optional": {
        "csv_path": ("STRING", {"default": "", "multiline": False}),
    }
}

# CSVViewer
INPUT_TYPES = {
    "required": {},
    "optional": {
        "csv_path": ("STRING", {"default": "", "multiline": False}),
        "max_rows": ("INT", {"default": 100, "min": 1, "max": 10000}),
    }
}
```

### 为什么不使用 IMAGEUPLOAD？

`IMAGEUPLOAD` 类型的要求：

1. **需要 augmentation**: 必须提供 `imageInputName` 配置
2. **专门为图片设计**: 前端有特殊的图片预览和处理逻辑
3. **文件类型限制**: 可能只接受图片格式
4. **复杂的配置**: 需要额外的前端和后端配置

使用 `STRING` 类型的优点：

1. **简单直接**: 不需要特殊配置
2. **灵活**: 支持任何路径格式
3. **可靠**: 不依赖复杂的前端逻辑
4. **通用**: 适用于任何文件类型

## 相关文档

- [CSV 批量处理指南](./NANOBANA_BATCH_GUIDE.md)
- [CSV 模板说明](./workflows/CSV_TEMPLATES_README.md)
- [CSV 快速参考](./workflows/CSV_QUICK_REFERENCE.md)
- [项目文档](./CLAUDE.md)

## 更新日志

### 2025-12-13 - 最终修复
- ✅ 移除 IMAGEUPLOAD 参数
- ✅ 简化为单一 csv_path 参数
- ✅ 智能路径处理
- ✅ 友好的错误提示
- ✅ 完整的测试验证
- ✅ 节点可以正常添加到画布

---

**重要提示**: 修改后需要**完全重启 ComfyUI** 才能生效。重启后，节点应该可以正常添加到画布了。
