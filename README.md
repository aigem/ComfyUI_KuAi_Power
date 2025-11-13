# ComfyUI KuAi Power

ComfyUI 节点扩展，提供对 Sora2 和 Veo 视频生成模型以及 AI 脚本生成功能的支持。

> **API 服务**: [kuai.host](https://api.kuai.host/register?aff=z2C8) | **国内镜像**: [v.kuai.host](https://v.kuai.host/) | **视频教程**: [Bilibili](https://www.bilibili.com/video/BV1umCjBqEpt/)

> 可配合[本地一键包「CNB钞能力一键包-free」来使用](https://pan.quark.cn/s/987bd66a6197)

`https://pan.quark.cn/s/987bd66a6197 提取码：AJFP`

## 🚀 快速开始

### 1. 安装依赖
```bash
# 进入插件目录
cd ComfyUI/custom_nodes/ComfyUI_KuAi_Power
# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key
在节点参数中直接填写，或创建 `.env` 文件并设置环境变量 `KUAI_API_KEY=your_api_key_here`。

### 3. 重启 ComfyUI
重启后，即可在右键菜单或 `Ctrl+Shift+K` 快捷面板中找到新节点。

---

## ✨ 核心功能

所有节点均提供全中文界面，分类清晰，易于使用。

### 🚀 Veo 视频生成 (`KuAi/Veo3`)
新一代视频模型，支持文生视频和图生视频。

| 节点名称 | 功能简介 |
| :--- | :--- |
| **🎬 Veo 文生视频** | 仅通过文本提示词创建视频。 |
| **🖼️ Veo 图生视频** | 使用 1-3 张参考图和提示词创建视频。 |
| **🔍 Veo 查询任务** | 查询指定任务的状态和结果。 |
| **⚡ Veo 一键文生视频** | 提交任务并自动等待视频生成完成。 |
| **⚡ Veo 一键图生视频** | 提交带参考图的任务并等待完成。 |

### 🎬 Sora2 视频生成 (`KuAi/Sora2`)
强大的图生视频模型。

| 节点名称 | 功能简介 |
| :--- | :--- |
| **🎥 创建视频任务** | 提交图生视频任务。 |
| **📝 文生视频** | 仅通过文本提示词创建视频。 |
| **🔍 查询任务状态** | 查询指定任务的状态和结果。 |
| **⚡ 一键生成视频** | 提交任务并自动等待视频生成完成。 |

### 📝 AI 脚本生成 (`KuAi/ScriptGenerator`)
利用大语言模型自动为您的产品生成专业的视频脚本/提示词。

| 节点名称 | 功能简介 |
| :--- | :--- |
| **📦 产品信息构建器** | 将产品信息结构化，为 AI 生成做准备。 |
| **🤖 AI 生成提示词** | 根据产品信息，调用 AI 生成专业级的 Sora 提示词。 |

### 🛠️ 其他工具

| 节点名称 | 分类 | 功能简介 |
| :--- | :--- | :--- |
| **UploadToImageHost** | `KuAi/Utils` | 将本地图片上传到图床并返回 URL。 |
| **DeepseekOCRToPrompt**| `KuAi/Utils` | 提取图片中的文本内容。 |

---

## 💡 工作流示例

### 示例 1: Veo 文生视频
```
(输入提示词) → VeoText2VideoAndWait → (获取视频URL)
```

### 示例 2: Sora2 产品视频生成
```
LoadImage → UploadToImageHost → ProductInfoBuilder → SoraPromptFromProduct → SoraCreateAndWait
```

---

## 🔧 开发与排错

### 文件结构
```
ComfyUI_KuAi_Power/
├── nodes/
│   ├── Sora2/             # Sora2 节点
│   └── Veo3/              # Veo 节点
├── web/
│   └── kuaipower_panel.js # 前端快捷面板
├── __init__.py
└── README.md
```

### 运行诊断脚本
如果遇到节点不显示等问题，请先运行诊断脚本。
```bash
python diagnose.py
```

### 常见问题
- **节点不显示?** 确认依赖已安装并重启 ComfyUI。检查控制台有无报错。
- **API 调用失败?** 检查 API Key 是否正确，网络是否通畅。

---

## 📄 许可证
MIT License
