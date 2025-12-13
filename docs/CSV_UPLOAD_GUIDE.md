# CSV 文件上传使用指南

## 功能概述

CSV批量读取器节点现在支持两种模式：
1. **upload 模式**: 从 ComfyUI 的 input 目录上传和选择 CSV 文件
2. **path 模式**: 直接输入 CSV 文件的完整路径

## 使用方法

### 方法 1: 文件上传模式（推荐）

#### 步骤 1: 上传 CSV 文件到 ComfyUI

将您的 CSV 文件复制到 ComfyUI 的 input 目录：

```bash
# ComfyUI input 目录通常位于：
ComfyUI/input/

# 复制 CSV 文件
cp your_batch_tasks.csv ComfyUI/input/
```

#### 步骤 2: 在节点中选择文件

1. 添加 `CSVBatchReader` 节点
2. 设置 `mode` 为 `upload`
3. 在 `csv_file` 下拉菜单中选择您上传的文件
4. 运行工作流

**优点**:
- ✅ 文件管理集中
- ✅ 下拉菜单选择，不易出错
- ✅ 自动检测文件变更
- ✅ 支持文件名自动补全

### 方法 2: 路径输入模式

#### 步骤 1: 准备 CSV 文件

将 CSV 文件放在任意位置，记录完整路径。

#### 步骤 2: 在节点中输入路径

1. 添加 `CSVBatchReader` 节点
2. 设置 `mode` 为 `path`
3. 在 `csv_path` 输入框中输入完整路径
4. 运行工作流

**支持的路径格式**:
```bash
# Windows
C:\Users\Name\Documents\batch_tasks.csv
C:/Users/Name/Documents/batch_tasks.csv

# macOS/Linux
/home/user/documents/batch_tasks.csv
~/documents/batch_tasks.csv
./batch_tasks.csv
```

**优点**:
- ✅ 灵活，文件可以在任意位置
- ✅ 适合自动化脚本
- ✅ 不需要复制文件

## 节点参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `mode` | 下拉菜单 | 选择模式：`upload` 或 `path` |

### 可选参数

| 参数 | 类型 | 说明 | 使用模式 |
|------|------|------|----------|
| `csv_file` | 下拉菜单 | 选择已上传的 CSV 文件 | upload |
| `csv_path` | 文本输入 | CSV 文件的完整路径 | path |

## 工作流示例

### 示例 1: 使用上传模式

```
1. 上传 CSV 文件到 ComfyUI/input/
   - nanobana_batch_tasks.csv

2. 添加节点并连接：
   CSVBatchReader (mode=upload, csv_file=nanobana_batch_tasks.csv)
       ↓
   NanoBananaBatchProcessor
       ↓
   查看输出目录
```

### 示例 2: 使用路径模式

```
1. 准备 CSV 文件：
   /home/user/projects/batch_tasks.csv

2. 添加节点并连接：
   CSVBatchReader (mode=path, csv_path=/home/user/projects/batch_tasks.csv)
       ↓
   NanoBananaBatchProcessor
       ↓
   查看输出目录
```

## 文件变更检测

节点会自动检测 CSV 文件的变更：
- 修改 CSV 文件后，ComfyUI 会自动重新读取
- 无需手动刷新或重启

## 常见问题

### Q1: 上传模式下看不到我的 CSV 文件？

**解决方案**:
1. 确认文件已复制到 `ComfyUI/input/` 目录
2. 确认文件扩展名是 `.csv`（小写）
3. 刷新 ComfyUI 页面
4. 如果仍然看不到，切换到 `path` 模式

### Q2: 路径模式下提示文件不存在？

**解决方案**:
1. 检查路径是否正确（复制完整路径）
2. 确认文件确实存在
3. Windows 用户：使用正斜杠 `/` 或双反斜杠 `\\`
4. 避免路径中有特殊字符或空格

### Q3: 如何知道使用哪种模式？

**建议**:
- **新手用户**: 使用 `upload` 模式（更简单）
- **高级用户**: 使用 `path` 模式（更灵活）
- **自动化脚本**: 使用 `path` 模式

### Q4: 可以同时使用两种模式吗？

**回答**: 不可以。每次只能选择一种模式。节点会根据 `mode` 参数决定使用哪种方式读取文件。

## 技术细节

### 文件编码

节点支持以下编码：
- UTF-8（推荐）
- UTF-8 with BOM

**建议**: 使用 UTF-8 编码保存 CSV 文件，以确保中文字符正确显示。

### 文件大小限制

- 理论上无限制
- 建议单个 CSV 文件不超过 1000 行任务
- 大批量任务建议分成多个 CSV 文件

### 性能优化

- 节点会缓存文件内容
- 只有文件修改时间变更时才重新读取
- 使用 `IS_CHANGED` 方法优化性能

## 安全注意事项

1. **路径验证**: 节点会验证文件路径和扩展名
2. **文件存在检查**: 读取前会检查文件是否存在
3. **编码处理**: 自动处理 UTF-8 BOM
4. **错误处理**: 提供详细的错误信息

## 相关文档

- [CSV 模板使用说明](./workflows/CSV_TEMPLATES_README.md)
- [CSV 快速参考](./workflows/CSV_QUICK_REFERENCE.md)
- [NanoBanana 批量处理指南](./NANOBANA_BATCH_GUIDE.md)

---

**文档版本**: 1.0
**最后更新**: 2025-12-13
