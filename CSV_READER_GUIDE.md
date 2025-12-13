# CSVBatchReader 使用指南

## 节点功能

**CSVBatchReader（CSV 批量读取器）** - 读取 CSV 文件并解析为批量任务数据，用于批量图像生成。

## 参数说明

### 输入参数

- **csv_file** (下拉列表, 可选): 从 input 目录选择 CSV 文件
  - 自动扫描 `ComfyUI/input/` 目录中的所有 `.csv` 文件
  - 选择后无需输入路径

- **csv_path** (字符串, 可选): 或输入完整路径
  - 支持绝对路径: `/path/to/file.csv`
  - 支持相对路径: `data/file.csv`
  - 支持文件名: `myfile.csv`（会从 input 目录查找）

### 输出

- **批量任务数据** (STRING): JSON 格式的任务列表，可传递给 NanoBananaBatchProcessor

## 使用方法

### 方法 1: 使用下拉列表（推荐）

1. **复制文件到 input 目录**:
   ```bash
   cp myfile.csv /path/to/ComfyUI/input/
   ```

2. **添加节点**:
   - 在 ComfyUI 中添加 `CSVBatchReader` 节点

3. **选择文件**:
   - 从 `csv_file` 下拉列表中选择文件
   - 列表会自动显示 input 目录中的所有 CSV 文件

4. **执行工作流**:
   - 点击 "Queue Prompt" 执行

### 方法 2: 输入完整路径

1. **添加节点**:
   - 在 ComfyUI 中添加 `CSVBatchReader` 节点

2. **输入路径**:
   - 在 `csv_path` 参数中输入完整路径
   - 例如: `/home/user/data/myfile.csv`

3. **执行工作流**:
   - 点击 "Queue Prompt" 执行

## 文件自动发现

节点会自动扫描 `ComfyUI/input/` 目录：

- ✅ 自动发现所有 `.csv` 文件
- ✅ 按文件名排序
- ✅ 实时更新（添加新文件后刷新节点即可）
- ✅ 支持子目录中的文件

## CSV 文件格式

### 批量图像生成

```csv
task_type,prompt,model_name,seed,aspect_ratio
generate,A futuristic city at sunset,gemini-3-pro-image-preview,42,16:9
generate,A cute cat playing with yarn,gemini-2.5-flash-image,0,1:1
generate,Mountain landscape with lake,gemini-3-pro-image-preview,123,9:16
```

### 批量图像编辑

```csv
task_type,prompt,image_1,seed,temperature
edit,Make the sky more dramatic,/path/to/image1.jpg,42,1.0
edit,Add more vibrant colors,/path/to/image2.jpg,0,0.8
edit,Enhance the lighting,/path/to/image3.jpg,123,1.2
```

## 工作流示例

```
CSVBatchReader
  ├─ csv_file: "batch_tasks.csv" (从下拉列表选择)
  └─ 输出: 批量任务数据
       ↓
NanoBananaBatchProcessor
  ├─ batch_tasks: (连接到 CSVBatchReader)
  ├─ api_key: "your_api_key"
  └─ 输出: 处理结果
```

## 路径处理优先级

节点按以下优先级处理输入：

1. **csv_file** (下拉列表)
   - 如果选择了文件，直接从 input 目录读取
   - 路径: `ComfyUI/input/{csv_file}`

2. **csv_path** (字符串)
   - 如果 csv_file 为空，使用 csv_path
   - 绝对路径: 直接使用
   - 相对路径: 尝试从 input 目录查找

## 常见问题

### Q1: 下拉列表为空？

**���因**: input 目录中没有 CSV 文件

**解决方法**:
1. 将 CSV 文件复制到 `ComfyUI/input/` 目录
2. 刷新节点（右键 → Refresh）
3. 或使用 `csv_path` 参数输入完整路径

### Q2: 添加新文件后看不到？

**解决方法**:
1. 右键点击节点
2. 选择 "Refresh"
3. 或重新加载页面（F5）

### Q3: 文件不存在错误？

**检查**:
1. 文件是否在 input 目录
2. 文件名拼写是否正确
3. 文件扩展名是否为 `.csv`

### Q4: 两个参数都不填会怎样？

**结果**: 执行时会报错，提示选择或输入文件

**错误信息**:
```
ValueError: 请选择或输入 CSV 文件。

使用方法：
1. 从 'csv_file' 下拉列表选择 input 目录中的文件
2. 或在 'csv_path' 中输入完整路径
```

## 技术细节

### 文件扫描逻辑

```python
# 扫描 input 目录
csv_files = []
if HAS_FOLDER_PATHS:
    input_dir = folder_paths.get_input_directory()
    csv_files = sorted([f for f in os.listdir(input_dir)
                       if f.lower().endswith('.csv')])

# 返回文件列表
return {
    "optional": {
        "csv_file": (csv_files if csv_files else [""], {...}),
        "csv_path": ("STRING", {...}),
    }
}
```

### 路径解析逻辑

```python
# 1. 优先使用 csv_file
if csv_file:
    file_path = os.path.join(input_dir, csv_file)

# 2. 其次使用 csv_path
elif csv_path:
    # 如果是绝对路径，直接使用
    if os.path.isabs(csv_path):
        file_path = csv_path
    # 如果是相对路径，尝试从 input 目录查找
    else:
        potential_path = os.path.join(input_dir, csv_path)
        if os.path.exists(potential_path):
            file_path = potential_path
        else:
            file_path = csv_path
```

## 相关文档

- [CSV 批量处理指南](./NANOBANA_BATCH_GUIDE.md)
- [CSV 模板说明](./workflows/CSV_TEMPLATES_README.md)
- [CSV 快速参考](./workflows/CSV_QUICK_REFERENCE.md)
- [项目文档](./CLAUDE.md)

## 更新日志

### 2025-12-13
- ✅ 移除 CSVViewer 节点
- ✅ 添加文件自动发现功能
- ✅ 支持下拉列表选择文件
- ✅ 保留完整路径输入选项
- ✅ 优化路径处理逻辑

---

**提示**: 修改后需要重启 ComfyUI 才能生效。
