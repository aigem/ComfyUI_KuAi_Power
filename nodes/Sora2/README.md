# ComfyUI KuAi Power 节点模块

## 模块说明

### utils.py
通用工具函数库，提供：
- 图像格式转换（ComfyUI IMAGE ↔ PIL）
- HTTP 请求辅助函数
- URL 列表解析
- JSON 路径提取

### script_generator.py
脚本生成相关节点（分类：`KuAi/ScriptGenerator`）：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| ProductInfoBuilder | 产品信息构建 | 产品名称、卖点、视频类型等 | product_json, reference_image_url |
| SoraPromptFromProduct | AI 生成提示词 | product_json, 参考图 | sora_prompt, raw_ai_response |
| DeepseekOCRToPrompt | OCR 文本提取 | image_url | ocr_text, raw_response_json |

### sora2.py
Sora2 API 调用节点（分类：`KuAi/Sora2`）：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| UploadToImageHost | 上传图片 | IMAGE | url, created_ms |
| SoraCreateVideo | 创建视频任务 | images, prompt | task_id, status, status_update_time |
| SoraQueryTask | 查询任务状态 | task_id | status, video_url, gif_url, thumbnail_url |
| SoraCreateAndWait | 一键创建并等待 | images, prompt | status, video_url, gif_url, thumbnail_url, task_id |

## 使用示例

### 产品视频生成工作流

```
1. LoadImage → UploadToImageHost → 获取图片 URL
2. ProductInfoBuilder → 填写产品信息 → product_json
3. SoraPromptFromProduct → 生成 AI 提示词 → sora_prompt
4. SoraCreateAndWait → 生成视频 → video_url
```

### OCR 驱动的视频生成

```
1. LoadImage → UploadToImageHost → image_url
2. DeepseekOCRToPrompt → OCR 提取 → ocr_text
3. SoraCreateVideo → 创建任务 → task_id
4. SoraQueryTask → 查询结果 → video_url
```

## 环境变量

- `KUAI_API_KEY`: 云雾 AI API 密钥（可选，节点参数优先）

## 依赖

```bash
pip install requests pillow numpy
```
