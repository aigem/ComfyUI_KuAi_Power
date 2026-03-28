# Nano Banana 多轮对话使用指南

## 什么是多轮对话？

多轮对话允许你通过连续的对话来迭代式地修改和完善图像，每一轮都基于上一轮生成的图像进行调整。

---

## 工作原理

### 状态保持机制

在 ComfyUI 中，`NanoBananaMultiTurnChat` 节点通过**实例状态**来保持对话历史：

```python
class NanoBananaMultiTurnChat:
    def __init__(self):
        self.conversation_history = []    # 保存所有对话
        self.last_image_base64 = None     # 保存上一轮的图像
```

### 执行流程

```
第一轮:
  用户输入 → 生成图像 → 保存图像和对话
                ↓
第二轮:
  用户输入 + 上一轮图像 → 生成新图像 → 更新保存
                ↓
第三轮:
  用户输入 + 上一轮图像 → 生成新图像 → 更新保存
                ↓
  ...继续...
```

---

## 使用步骤

### 1. 添加节点

在 ComfyUI 中添加 `NanoBananaMultiTurnChat` 节点：
- 方法 1: 右键菜单 → `KuAi/NanoBanana` → `🍌 Nano Banana 多轮对话`
- 方法 2: 快捷键 `Ctrl+Shift+K` → 选择 `🍌 Nano Banana 图像生成` → 点击 `🍌 Nano Banana 多轮对话`

### 2. 配置参数

**必需参数**:
- `model_name`: 选择模型（`gemini-3-pro-image-preview`、`gemini-3.1-flash-image-preview`、`gemini-2.5-flash-image`）
- `prompt`: 输入提示词
- `reset_chat`: 是否重置对话（默认 `False`）
- `aspect_ratio`: 图像宽高比（默认 `1:1`）
- `image_size`: 图像尺寸（默认 `2K`）
- `temperature`: 生成温度（默认 `1.0`）

**可选参数**:
- `image_input`: 初始参考图像（仅首次对话使用）
- `api_base`: API 端点（默认 `https://api.kuai.host`）
- `api_key`: API 密钥（或使用环境变量 `KUAI_API_KEY`）
- `timeout`: 超时时间（默认 120 秒）

### 3. 第一轮对话

**示例**:
```
prompt: "Create an image of a clear perfume bottle sitting on a vanity."
reset_chat: False
```

**执行后**:
- 生成初始图像
- 图像保存在节点内部状态中
- 对话历史开始记录

### 4. 第二轮对话

**重要**: 使用**同一个节点实例**

**示例**:
```
prompt: "Change the color of the liquid inside the glass bottle to a vibrant royal blue"
reset_chat: False
```

**执行后**:
- 节点自动使用上一轮的图像作为参考
- 生成修改后的图像
- 更新对话历史

### 5. 第三轮对话

**示例**:
```
prompt: "Extreme close-up on the glass texture and silver cap of the blue perfume bottle"
reset_chat: False
```

**执行后**:
- 继续基于上一轮图像进行修改
- 生成更精细的图像

### 6. 重置对话

当你想开始新的对话时：
```
reset_chat: True
```

这会清空对话历史和保存的图像。

---

## 完整工作流示例

### 示例 1: 产品设计迭代

```
工作流:
NanoBananaMultiTurnChat
  ↓
第一轮: "Create a modern smartphone design"
  → 生成初始设计
  ↓
第二轮: "Make the screen larger and add curved edges"
  → 基于第一轮修改
  ↓
第三轮: "Change the color to midnight blue"
  → 继续调整
  ↓
PreviewImage (查看最终结果)
```

### 示例 2: 艺术创作

```
工作流:
LoadImage (可选：提供初始图像)
  ↓
NanoBananaMultiTurnChat
  ↓
第一轮: "Transform this into an oil painting style"
  → 风格转换
  ↓
第二轮: "Add more vibrant colors and dramatic lighting"
  → 增强效果
  ↓
第三轮: "Focus on the central subject, blur the background"
  → 精细调整
  ↓
SaveImage
```

### 示例 3: 场景构建

```
工作流:
NanoBananaMultiTurnChat
  ↓
第一轮: "Create a cozy coffee shop interior"
  → 生成基础场景
  ↓
第二轮: "Add more plants and natural lighting from large windows"
  → 添加元素
  ↓
第三轮: "Place a barista behind the counter making coffee"
  → 添加人物
  ↓
第四轮: "Add warm afternoon sunlight streaming through the windows"
  → 调整氛围
```

---

## 输出说明

节点有 4 个输出：

1. **图像** (IMAGE)
   - 当前轮生成的图像
   - 可以连接到 `PreviewImage` 或 `SaveImage`

2. **响应文本** (STRING)
   - AI 对当前提示的文本响应
   - 可能包含对修改的说明

3. **元数据** (STRING)
   - 生成元数据（finish_reason, safety_ratings 等）
   - 用于调试和质量检查

4. **对话历史** (STRING)
   - 完整的对话历史记录（JSON 格式）
   - 不包含 base64 图像数据（太长）
   - 格式示例：
     ```json
     [
       {
         "role": "user",
         "content": "Create a perfume bottle",
         "has_image": false
       },
       {
         "role": "assistant",
         "content": "Image generated",
         "has_image": true
       },
       {
         "role": "user",
         "content": "Make it elegant",
         "has_image": true
       }
     ]
     ```

---

## 重要注意事项

### ✅ 正确做法

1. **使用同一个节点实例**
   - 不要删除节点
   - 不要复制节点
   - 每次执行都使用同一个节点

2. **按顺序执行**
   - 等待上一轮完成后再执行下一轮
   - 不要跳过中间步骤

3. **清晰的提示词**
   - 明确说明要修改什么
   - 使用相对描述（"更大"、"更亮"、"添加..."）

### ❌ 常见错误

1. **删除节点后重新添加**
   - ❌ 错误：状态会丢失
   - ✅ 正确：始终使用同一个节点

2. **复制节点**
   - ❌ 错误：新节点没有对话历史
   - ✅ 正确：使用原节点或设置 `reset_chat=True`

3. **重新加载工作流**
   - ❌ 错误：状态会丢失
   - ✅ 正确：在同一会话中完成所有对话

4. **忘记设置 API Key**
   - ❌ 错误：节点会报错
   - ✅ 正确：设置环境变量或在节点中填写

---

## 高级技巧

### 1. 使用初始图像

在第一轮对话时提供 `image_input`：
```
LoadImage → NanoBananaMultiTurnChat (image_input)
prompt: "Transform this image into a watercolor painting"
```

### 2. 组合使用

```
NanoBananaAIO (生成多个候选)
  ↓ 选择最好的一个
LoadImage
  ↓
NanoBananaMultiTurnChat (精细调整)
  ↓ 多轮迭代
SaveImage
```

### 3. 分支对话

如果想尝试不同的修改方向：
1. 在某一轮后复制节点
2. 在新节点上设置 `reset_chat=False`
3. 尝试不同的提示词

**注意**: 复制的节点不会继承状态，需要手动提供图像。

### 4. 保存中间结果

在每一轮后连接 `SaveImage` 节点：
```
NanoBananaMultiTurnChat
  ↓
PreviewImage (查看)
  ↓
SaveImage (保存)
```

---

## 故障排查

### 问题 1: "对话历史丢失"

**症状**: 节点似乎忘记了之前的对话

**原因**:
- 删除并重新添加了节点
- 重新加载了工作流
- 使用了不同的节点实例

**解决**:
- 使用同一个节点实例
- 或设置 `reset_chat=True` 重新开始

### 问题 2: "生成的图像与上一轮无关"

**症状**: 新图像没有基于上一轮的图像

**原因**:
- 后端 API 没有正确处理对话历史
- 图像 base64 数据丢失

**解决**:
- 检查后端 API 实现
- 确认 `last_image_base64` 正确保存

### 问题 3: "API 调用失败"

**症状**: 节点报错 "未配置 API Key"

**原因**:
- 没有设置 `KUAI_API_KEY` 环境变量
- 没有在节点中填写 `api_key`

**解决**:
```bash
# 方法 1: 设置环境变量
export KUAI_API_KEY=your_key_here

# 方法 2: 在 .env 文件中配置
echo "KUAI_API_KEY=your_key_here" > .env

# 方法 3: 在节点参数中填写
api_key: "your_key_here"
```

### 问题 4: "生成速度慢"

**症状**: 每轮对话需要很长时间

**原因**:
- 网络延迟
- API 服务器负载高
- base64 数据量大

**解决**:
- 使用较小的 `image_size`（1K 而不是 4K）
- 降低 `temperature`（更确定性的生成）
- 检查网络连接

---

## 最佳实践

### 1. 渐进式修改

不要一次性要求太多修改：
- ❌ 差: "Make it blue, add flowers, change the background, and make it brighter"
- ✅ 好:
  - 第一轮: "Make it blue"
  - 第二轮: "Add flowers"
  - 第三轮: "Change the background"
  - 第四轮: "Make it brighter"

### 2. 明确的指令

使用清晰、具体的描述：
- ❌ 差: "Make it better"
- ✅ 好: "Increase the contrast and add more vibrant colors"

### 3. 保持一致性

在同一对话中保持风格和主题一致：
- ✅ 好: 逐步完善同一个场景
- ❌ 差: 频繁切换完全不同的主题

### 4. 适时重置

当需要开始全新的创作时，使用 `reset_chat=True`：
```
完成一个项目 → reset_chat=True → 开始新项目
```

---

## 示例对话脚本

### 产品摄影优化

```
第 1 轮:
prompt: "Create a professional product photo of a luxury watch on a marble surface"
→ 生成基础产品照

第 2 轮:
prompt: "Add dramatic side lighting to highlight the watch's metallic finish"
→ 增强光照效果

第 3 轮:
prompt: "Blur the background slightly to make the watch stand out more"
→ 调整景深

第 4 轮:
prompt: "Add subtle reflections on the marble surface"
→ 添加细节
```

### 角色设计

```
第 1 轮:
prompt: "Create a fantasy character design - a young wizard with a staff"
→ 生成基础角色

第 2 轮:
prompt: "Add more intricate details to the wizard's robes with mystical symbols"
→ 丰富服装细节

第 3 轮:
prompt: "Make the staff glow with magical energy"
→ 添加魔法效果

第 4 轮:
prompt: "Add a mystical aura around the character"
→ 增强氛围
```

---

## 总结

多轮对话是一个强大的迭代式创作工具，关键要点：

1. ✅ **使用同一个节点实例**
2. ✅ **渐进式修改**
3. ✅ **清晰的提示词**
4. ✅ **保存中间结果**
5. ✅ **适时重置对话**

通过多轮对话，你可以像与设计师交流一样，逐步完善你的创意，直到达到理想效果！

---

**相关文档**:
- `CLAUDE.md` - 完整技术文档
- `API_SPECIFICATION.md` - API 规范
- `README.md` - 快速开始指南
