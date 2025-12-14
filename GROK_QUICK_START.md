# Grok 视频生成 - 快速开始指南

## 🎉 安装完成

Grok 视频生成节点已成功安装到 ComfyUI_KuAi_Power 插件中！

## 📦 包含的节点

1. **🤖 Grok 创建视频** (GrokCreateVideo)
   - 创建视频生成任务，返回任务ID

2. **🔍 Grok 查询视频** (GrokQueryVideo)
   - 查询任务状态和视频URL

3. **⚡ Grok 一键生成视频** (GrokCreateAndWait)
   - 创建并自动等待完成，推荐使用

## 🚀 快速开始

### 步骤 1: 设置 API 密钥

选择以下任一方式：

**方式 A: 环境变量（推荐）**
```bash
export KUAI_API_KEY=sk-kpXUUC5LidOkfhTEi3T78w11CXqEKooA2cXjJMsm2kvazaXX
```

**方式 B: 节点参数**
在节点的 `api_key` 参数中直接输入密钥

### 步骤 2: 重启 ComfyUI

重启 ComfyUI 以加载新节点

### 步骤 3: 使用节点

#### 方法 1: 使用快捷面板（推荐）
1. 按 `Ctrl + Shift + K` 打开快捷面板
2. 找到 "🤖 Grok 视频生成" 分类
3. 点击 "⚡ Grok 一键生成视频"

#### 方法 2: 右键菜单
1. 在画布上右键
2. 选择 `Add Node` → `KuAi` → `Grok`
3. 选择需要的节点

### 步骤 4: 配置参数

**基础配置**：
- **prompt**: 输入视频描述（支持中英文）
- **aspect_ratio**: 选择宽高比
  - `3:2` - 横屏（推荐）
  - `2:3` - 竖屏
  - `1:1` - 正方形
- **size**: 选择分辨率
  - `1080P` - 高清（推荐）
  - `720P` - 标清（更快）

### 步骤 5: 执行生成

点击 `Queue Prompt` 按钮，等待视频生成完成（通常 5-12 分钟）

## 💡 使用示例

### 示例 1: 简单文本生成视频

```
提示词: A cute cat playing with a colorful ball in a sunny garden
宽高比: 3:2
分辨率: 1080P
```

### 示例 2: 电影级视频

```
提示词: A majestic eagle soaring through the clouds at sunset,
        cinematic lighting, slow motion, 4K quality
宽高比: 3:2
分辨率: 1080P
```

### 示例 3: 竖屏短视频

```
提示词: A dancer performing in the rain, dramatic lighting,
        close-up shot, artistic style
宽高比: 2:3
分辨率: 1080P
```

## 📝 提示词技巧

### 好的提示词包含：
1. **主体**: 描述主要对象
2. **动作**: 描述发生的事情
3. **环境**: 描述场景和背景
4. **风格**: 描述视觉风格
5. **镜头**: 描述拍摄方式

### 示例对比：

❌ **差**: `cat`

✅ **好**: `A fluffy white cat playing with a red ball in a sunny garden, slow motion, cinematic lighting`

### 常用关键词：

**镜头运动**:
- `slow motion` - 慢动作
- `time-lapse` - 延时摄影
- `tracking shot` - 跟踪镜头
- `aerial view` - 航拍视角
- `close-up` - 特写

**光照效果**:
- `cinematic lighting` - 电影级光照
- `golden hour` - 黄金时刻
- `dramatic lighting` - 戏剧性光照
- `soft lighting` - 柔和光照

**视觉风格**:
- `photorealistic` - 照片级真实
- `4K quality` - 4K 画质
- `artistic style` - 艺术风格
- `anime style` - 动漫风格

## 🔧 高级用法

### 图片到视频

1. 使用 `KuAi 图片上传` 节点上传图片
2. 将图片URL连接到 `image_urls` 参数
3. 在提示词中描述如何动画化图片

### 手动控制流程

```
GrokCreateVideo → 获取 task_id → GrokQueryVideo
```

适用于：
- 批量任务管理
- 需要在等待期间执行其他操作
- 更灵活的错误处理

## ⚙️ 参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| prompt | 文本 | 视频描述 |
| aspect_ratio | 选择 | 1:1, 2:3, 3:2 |
| size | 选择 | 720P, 1080P |
| api_key | 文本 | API密钥（可用环境变量） |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image_urls | 文本 | 空 | 参考图片URL |
| max_wait_time | 整数 | 600 | 最大等待时间（秒） |
| poll_interval | 整数 | 10 | 轮询间隔（秒） |

## 🐛 常见问题

### Q: 生成需要多长时间？
A: 通常 5-12 分钟，取决于分辨率和服务器负载。

### Q: 如何查看进度？
A: 查看 ComfyUI 控制台日志，会显示轮询状态。

### Q: 生成失败怎么办？
A: 检查：
1. API Key 是否正确
2. 网络连接是否正常
3. 提示词是否符合内容政策

### Q: 可以使用本地图片吗？
A: 需要先用 `KuAi 图片上传` 节点上传到云端。

### Q: 支持中文提示词吗？
A: 支持，但英文提示词通常效果更好。

## 📚 更多资源

- **详细文档**: `docs/GROK_VIDEO_GUIDE.md`
- **测试文件**: `test/test_grok_nodes.py`
- **实现总结**: `GROK_IMPLEMENTATION_SUMMARY.md`
- **API 文档**: https://api.kuai.host/docs
- **注册账号**: https://api.kuai.host/register?aff=z2C8

## 🎬 开始创作

现在你已经准备好使用 Grok 视频生成节点了！

1. 重启 ComfyUI
2. 按 `Ctrl + Shift + K`
3. 选择 "⚡ Grok 一键生成视频"
4. 输入创意提示词
5. 点击生成
6. 等待精彩视频！

祝你创作愉快！🎉
