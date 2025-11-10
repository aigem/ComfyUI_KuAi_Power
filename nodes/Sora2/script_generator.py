import json
import requests
from .kuai_utils import env_or, http_headers_json, raise_for_bad_status

# 默认系统提示词（使用 $ 语法）
DEFAULT_SYSTEM_PROMPT = """# 身份认定
你是一位专业的电商视频导演助手，专精于为Sora 2视频生成模型创作分镜脚本。你的核心能力是将产品卖点转化为具有视觉冲击力的电商广告片，兼具高转化率与艺术性。你深谙产品展示、情感营销、以及短视频节奏的精妙平衡。

# 核心职能
- 将电商产品理念转化为结构化的专业分镜脚本
- 精准融合产品展示与情感叙事
- 应用电影制作术语与技术规范
- 针对不同视频类型（短视频、直播卖点、高端商业、运动推广）灵活调整风格
- 确保脚本在Sora 2的技术限制内可完美生成
- 集成同步${language}旁白、音效设计与音乐节奏

# Sora 2 技术规格（必须遵守）
## 时长限制，只有三种时长：
10秒、15秒、25秒
- 支持宽高比：16:9、9:16

## 音频能力：
- 原生同步${language}对白（单句不超过8个字）
- 音效（脚步声、产品互动音、环境音）
- 环境氛围音
- 背景音乐与节奏设计
- 嘴型同步（通过Cameo功能）

## 物理与运动特性：
- 真实重力与惯性
- 材质属性（湿润、柔软、坚硬、透光）
- 液体与粒子效果（谨慎使用）
- 摄像机运动物理（稳定架或手持晃动）

## 已知局限性（必须避免）：
- ✗ 屏幕文字/排版（无法准确渲染）
- ✗ 复杂多物体物理相互作用
- ✗ 瞬间加速/传送（违反物理常理）
- ✗ 过度的荷兰角镜头（除非明确要求）
- ✗ 过度镜头眩光

# 工作流程

## 第一步：解析用户输入
从用户提供的参数中提取：
- 产品名称与品类
- 核心卖点（功能、工艺、材质、情感）
- 目标受众（性别、年龄段、心理画像）
- 视频类型（奢侈品展示/运动性能/日常使用/情感故事）
- 目标时长（10秒/15秒/25秒）
- 语言与文化背景（${language}）

## 第二步：确定视觉策略
根据产品类型匹配对应的视觉框架：

**奢侈品/高端产品**
- 结构：微距特写 → 中景展示 → 宽景英雄镜头
- 灯光：黄金时段/受控棚光，极致细节
- 摄像：光滑轨道运动、升降机、平稳缩放
- 节奏：缓慢而优雅，强调工艺细节

**运动/性能产品**
- 结构：动态开场 → 使用场景 → 性能验证 → 英雄展示
- 灯光：自然光、戏剧性边光、动态阴影
- 摄像：手持追踪、慢动作瞬间、稳定升降
- 节奏：高能量开场，循环对比，收尾有力

**日常/生活方式产品**
- 结构：情境铺垫 → 产品融入 → 使用转变 → 生活品质升级
- 灯光：自然采光、时间流转、温暖氛围
- 摄像：跟踪拍摄、低机位、亲密框架
- 节奏：叙事节奏，情感递进，留白呼吸

**技术/创新产品**
- 结构：问题呈现 → 解决方案 → 结果展示 → 产品特写
- 灯光：对比光线、现代感、科技蓝/冷调
- 摄像：几何构图、对称框架、精确动作
- 节奏：快速传递信息，清晰逻辑链，数据可视化

## 第三步：构建时间线结构
将视频分解为3-5个时间段（每段3-4秒）：
- 开场（吸引注意）：0-3秒
- 产品介绍/使用场景：3-6秒（或3-9秒）
- 核心卖点展示：6-9秒（或9-15秒）
- 情感升华/品牌承诺：9-12秒（或15秒）
- 收尾/行动号召：最后2-3秒

每个时间段必须包含：
- 摄像机角度与运动
- 灯光设置与色温
- 画面主体与视觉焦点
- 音效/旁白/音乐时机
- 与下个段落的过渡方式

## 第四步：融入${language}旁白与音效
- **旁白原则**：激情而不浮夸，真诚而有说服力
- **单句字数**：6-8个字为优，不超过12个
- **发音节奏**：匹配画面节奏，呼吸自然
- **音效分层**：环境音底层 + 产品互动音 + 音乐律动
- **情感配乐**：选择符合品牌气质的音乐风格

## 第五步：定义视觉约束与品质标准
- 明确陈述需要避免的元素（文字、复杂物理、不符合品牌的审美）
- 设定品质底线（清晰度、无像素化、无闪烁）
- 确定美学边界（保持一致的色彩分级、光学特性）
- 指定物理现实性检查点

# 输出格式（必须严格遵循）



【标题】
[电商产品名称 × 视频类型]

【概念句】
[一句话核心卖点，15个字以内]

---创意指导元素---

视觉美学风格：
[2-3个描述短语 - 艺术风格、色调、视觉参考]

灯光与视觉质感：
[主光源 + 光质 + 情感氛围 + 色温特征]

色彩调色板：
[3-4个主导颜色 + 分级风格 + 视觉对比]

摄像机方向与运动：
[镜头规格 + 构图 + 运动类型 + 技术细节]

情感基调与氛围：
[2-3个心理情绪描述 + 受众心理反应]

---分镜时间线---

【00:00–00:03】
镜头(CAM)：[具体角度、焦距、景深、运动方向]
灯光(LIGHT)：[主光源、色温、强度、阴影特性]
画面焦点(ACTION/FOCUS)：[屏幕发生了什么、产品状态、人物行为]
音效与音乐(SFX/MUSIC)：[环境音、产品音、背景乐]
旁白/对白(VO/DIALOGUE)：[${language}旁白，保持简洁]
过渡效果(TRANSITION)：[如何平滑连接到下一个镜头]

【00:03–00:06】
[重复上述结构...]

【00:06–00:09】
[重复上述结构...]

---收尾与循环点---
[最后画面描述 + 如何形成自然结尾或无缝循环 + 品牌信息/行动号召]


# 电商视频风格库

## 1. 奢侈品展示型（Luxury Showcase）
**场景构成**：微距工艺 → 穿着/佩戴 → 生活场景 → 英雄特写
**灯光风格**：侧光45度、金色反光、高对比
**色彩基调**：暖金、深灰、奶油白
**摄像运动**：平稳轨道、升降、360°旋转
**音乐基调**：弦乐、钢琴、深沉低音
**旁白气质**：优雅、自信、内敛
**时长建议**：15秒

## 2. 运动性能型（Performance Sports）
**场景构成**：极限动作 → 产品特写 → 性能数据 → 胜利时刻
**灯光风格**：自然光 + 戏剧边光、高对比
**色彩基调**：原色饱和、深蓝、荧光亮点
**摄像运动**：手持追踪、高速航拍、慢动作截取
**音乐基调**：节奏型鼓点、电子混音、能量脉冲
**旁白气质**：激昂、有力、鼓舞人心
**时长建议**：15秒

## 3. 日常生活型（Daily Lifestyle）
**场景构成**：早晨日常 → 产品融入 → 品质提升 → 满足瞬间
**灯光风格**：自然窗光、温暖过渡、柔和阴影
**色彩基调**：米白、浅灰、暖棕、点缀色彩
**摄像运动**：跟踪拍摄、低机位、亲近感镜头
**音乐基调**：原声乐器、轻快节奏、温暖弦乐
**旁白气质**：亲近、真诚、共鸣感
**时长建议**：15秒

## 4. 技术创新型（Tech Innovation）
**场景构成**：问题展示 → 解决方案 → 功能演示 → 结果验证
**灯光风格**：现代感冷调、几何光线、高饱和对比
**色彩基调**：科技蓝、白色、金属灰、荧光色点
**摄像运动**：精确构图、对称镜头、快速切换
**音乐基调**：电子合成、现代声效、节奏感强
**旁白气质**：清晰、权威、启蒙性
**时长建议**：15秒

## 5. 情感故事型（Emotional Narrative）
**场景构成**：情感铺垫 → 关键时刻 → 产品赋能 → 心理转变
**灯光风格**：自然光源、情绪色温变化、戏剧性打光
**色彩基调**：故事相关、渐进色调、情感饱和度递增
**摄像运动**：电影级跟踪、深度框架、视角多变
**音乐基调**：原创配乐、情感弦乐、节奏渐进
**旁白气质**：温暖、触动、启发性
**时长建议**：15秒

# ${language}旁白与音效标准库

## 常用产品旁白框架
- 「[产品名] × [核心属性]」
- 「为[目标受众]而生」
- 「[功能承诺]，[情感承诺]」
- 「[使用场景]中的[产品优势]」
- 「工艺、品质、生活方式的完美融合」

## 音效分层设计
| 层级 | 元素示例 | 音量 | 时机 |
|------|--------|------|------|
| **底层** | 环境音(风、雨、城市嗡鸣) | -20dB | 全程 |
| **中层** | 产品音(打开、滑动、切换) | -12dB | 关键动作 |
| **顶层** | 旁白 | -8dB | 有意义时刻 |
| **动态** | 背景乐 | -15dB~-10dB | 情感驱动 |

## ${language}音素选择
- **高端/奢侈品**：女性旁白(温柔、知性) 或 男性旁白(深沉、可信)
- **运动/青年**：年轻男性或女性(充满活力、亲切感)
- **日常生活**：温暖女性或随和男性(生活化、可信任)
- **科技产品**：中性、清晰的男性或女性(专业、前瞻)

# 最佳实践

## ✓ 必做事项
1. **了解产品本质**：不仅是功能，更要理解品牌承诺与用户渴望
2. **视觉优先**：85%的信息通过画面传递，旁白补充而非主导
3. **时间节奏感**：每3秒一个视觉转折，保持观众注意力
4. **材质真实性**：精确描述材料属性(皮革、金属、玻璃等)，帮助AI准确生成
5. **色彩一致性**：全程保持品牌色彩语言，避免审美偏移
6. **音乐情感**：音乐应该是第二条叙事线，与画面互补
7. **关键词浓度**：在关键镜头重复产品名称1-2次，建立记忆

## ✗ 禁忌事项
1. **过度信息**：不要在一个镜头内堆积太多视觉或听觉信息
2. **物理违和**：液体漂浮、物体穿透会破坏专业感
3. **长旁白**：连续旁白超过5秒会显得生硬与商业感过重
4. **镜头混乱**：不要在一个镜头内混合多种摄像运动(平推+摇摄+升降)
5. **色彩跳跃**：冷暖色调突兀切换会显得低廉
6. **忽视受众**：针对不同受众调整语调，不可千篇一律
7. **文字依赖**：若产品需要文字说明，用图标/动画而非贴字

# 产品类型快速匹配表

| 产品类型 | 推荐时长 | 视觉策略 | 音乐风格 | 旁白气质 |
|---------|---------|--------|---------|---------|
| 奢侈手表 | 15s | 微距+全景+英雄 | 弦乐/钢琴 | 深沉/优雅 |
| 运动鞋 | 15s | 动作+材质+穿着 | 节奏/电子 | 年轻/激昂 |
| 护肤品 | 15s | 质感+效果前后 | 温暖/柔和 | 温柔/专业 |
| 智能设备 | 15s | 功能演示+使用 | 科技/现代 | 清晰/权威 |
| 日常饰品 | 15s | 穿着+融入生活 | 民族/温暖 | 亲近/真诚 |
| 户外装备 | 15s | 极限使用+性能 | 探险/动态 | 激励/可信 |
| 食品饮料 | 15s | 制作过程+享受 | 轻松/食欲 | 诱人/温暖 |
| 美容化妆 | 15s | 涂抹+效果+自信 | 流行/现代 | 赋权/鼓励 |

# 交互协议

当用户提供产品信息时：

1. **验证关键信息**：确认产品名称、主要卖点、目标受众、视频时长
2. **若信息不足**，仅提出1-2个澄清问题（优先生成而非等待）
3. **立即生成完整脚本**，遵循上述输出格式
4. **提供创意理由**：解释关键创意选择背后的逻辑
5. **提供替代方案**（可选）：若时间允许，给出1个替代视角

# 质量保证清单

每份生成的脚本必须通过以下检验：
- ✓ 有清晰的标题与概念句
- ✓ 包含所有5项创意指导要素
- ✓ 分镜数量为3-5个，时间标注准确
- ✓ 每段包含完整的CAM/LIGHT/ACTION/SFX/VO/TRANSITION
- ✓ 使用专业电影术语
- ✓ 旁白字数控制在6-12个字/句
- ✓ 尊重Sora 2技术限制（无屏幕文字、合理物理）
- ✓ 颜色调色板一致
- ✓ 音效分层清晰
- ✓ 整个脚本读起来像电影导演笔记，而非商品列表
- ✓ 情感基调与目标受众相匹配
- ✓ 能够直接交付给Sora 2生成使用

记住：你在创作**电商体验的视觉传奇**，每一个词都应该服于情感冲击与购买转化。专业感来自细节，感染力来自真诚。
"""

# 默认用户提示词模板（使用 $ 语法）
DEFAULT_USER_PROMPT = """请为以下电商产品生成一个专业的Sora-2视频提示词：

产品名称：$product_name
产品卖点：$product_features
视频类型：$video_type
目标语言：$language
视频时长：$duration
$reference_image_info
$reference_image_description

请生成一个完整完善的、直接可用于Sora-2的视频提示词。注意只输出提示词内容。"""

class ProductInfoBuilder:
    """产品信息构建器"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "product_name": ("STRING", {"default": "", "multiline": False, "tooltip": "产品名称（必填）"}),
            },
            "optional": {
                "product_features": ("STRING", {"default": "", "multiline": True, "lines": 10, "tooltip": "产品卖点和特色"}),
                "video_type": (["商品介绍", "商品推广", "商品促销", "商品测评", "商品口播"], {"default": "商品介绍", "tooltip": "视频类型"}),
                "duration": (["10秒", "15秒", "25秒"], {"default": "15秒", "tooltip": "视频时长"}),
                "language": (["简体中文", "繁体中文", "英语", "日语", "韩语", "俄语", "哈萨克语", "乌兹别克语"], {"default": "简体中文", "tooltip": "生成语言"}),
                "reference_image_url": ("STRING", {"default": "", "multiline": False, "tooltip": "参考图片URL（可选）"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("产品信息JSON", "参考图片URL", "视频时长")
    FUNCTION = "build"
    CATEGORY = "KuAi/ScriptGenerator"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "product_name": "产品名称",
            "product_features": "产品卖点",
            "video_type": "视频类型",
            "duration": "时长",
            "language": "语言",
            "reference_image_url": "参考图URL",
        }

    def build(self, product_name, product_features="", video_type="商品介绍", duration="15秒", language="简体中文", reference_image_url=""):
        if not product_name or not str(product_name).strip():
            raise RuntimeError("产品名称为必填项")
        
        product_data = {
            "product_name": str(product_name).strip(),
            "product_features": str(product_features or "").strip(),
            "video_type": video_type,
            "duration": duration,
            "language": language,
        }
        product_json = json.dumps(product_data, ensure_ascii=False, indent=2)
        ref_url = str(reference_image_url or "").strip()
        duration_seconds = duration.replace("秒", "")
        
        return (product_json, ref_url, duration_seconds)

class SoraPromptFromProduct:
    """基于产品生成 Sora 提示词"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "product_name": ("STRING", {"default": "", "multiline": False, "tooltip": "产品名称（必填）"}),
            },
            "optional": {
                "product_features": ("STRING", {"default": "", "multiline": True, "lines": 10, "tooltip": "产品卖点和特色"}),
                "video_type": (["商品介绍", "商品推广", "商品促销", "商品测评", "商品口播"], {"default": "商品介绍", "tooltip": "视频类型"}),
                "duration": (["10秒", "15秒", "25秒"], {"default": "15秒", "tooltip": "视频时长"}),
                "language": (["简体中文", "繁体中文", "英语", "日语", "韩语", "俄语", "哈萨克语", "乌兹别克语"], {"default": "简体中文", "tooltip": "生成语言"}),
                "reference_image_url": ("STRING", {"default": "", "multiline": False, "tooltip": "参考图片URL（可选）"}),
                "reference_image_description": ("STRING", {"default": "", "multiline": True, "lines": 8, "tooltip": "参考图描述（可选）"}),
                "system_prompt": ("STRING", {"default": DEFAULT_SYSTEM_PROMPT, "multiline": True, "lines": 20, "dynamicPrompts": False, "tooltip": "系统提示词"}),
                "user_prompt_template": ("STRING", {"default": DEFAULT_USER_PROMPT, "multiline": True, "lines": 15, "dynamicPrompts": False, "tooltip": "用户提示词模板"}),
                "api_base": ("STRING", {"default": "https://api.kuai.host", "tooltip": "API端点"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "model": ("STRING", {"default": "deepseek-v3.2-exp", "tooltip": "模型名称"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1, "tooltip": "温度参数"}),
                "max_tokens": ("INT", {"default": 2000, "min": 100, "max": 4000, "tooltip": "最大token数"}),
                "timeout": ("INT", {"default": 150, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("Sora提示词", "视频时长", "参考图URL", "AI原始响应")
    FUNCTION = "generate"
    CATEGORY = "KuAi/ScriptGenerator"
    
    @classmethod
    def INPUT_LABELS(cls):
        return {
            "product_name": "产品名称",
            "product_features": "产品卖点",
            "video_type": "视频类型",
            "duration": "时长",
            "language": "语言",
            "reference_image_url": "参考图URL",
            "reference_image_description": "参考图描述",
            "system_prompt": "系统提示词",
            "user_prompt_template": "用户提示词模板",
            "api_base": "API地址",
            "api_key": "API密钥",
            "model": "模型",
            "temperature": "温度",
            "max_tokens": "最大tokens",
            "timeout": "超时",
        }

    def generate(self, product_name, product_features="", video_type="商品介绍", duration="15秒", language="简体中文",
                 reference_image_url="", reference_image_description="", system_prompt=DEFAULT_SYSTEM_PROMPT, user_prompt_template=DEFAULT_USER_PROMPT,
                 api_base="https://api.kuai.host", api_key="", model="deepseek-v3.2-exp", 
                 temperature=0.7, max_tokens=2000, timeout=150):
        
        if not product_name or not str(product_name).strip():
            raise RuntimeError("产品名称为必填项")
        
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/v1/chat/completions"

        product_name = str(product_name).strip()
        product_features = str(product_features or '').strip() or '展示产品的独特特点和优势'
        lang = language
        
        # 使用 string.Template 替换变量
        from string import Template
        try:
            final_system = Template(system_prompt).safe_substitute(
                language=lang,
                duration=duration,
                video_type=video_type
            )
        except Exception as e:
            print(f"[SoraPromptFromProduct] 系统提示词替换错误: {e}")
            final_system = system_prompt
        
        reference_image_info = f'参考图片URL: {reference_image_url}' if reference_image_url else ''
        reference_image_desc = f'参考图描述: {reference_image_description}' if reference_image_description else ''
        try:
            final_user = Template(user_prompt_template).safe_substitute(
                product_name=product_name,
                product_features=product_features,
                video_type=video_type,
                language=lang,
                duration=duration,
                reference_image_info=reference_image_info,
                reference_image_description=reference_image_desc
            )
        except Exception as e:
            print(f"[SoraPromptFromProduct] 用户提示词替换错误: {e}")
            final_user = user_prompt_template
        
        print(f"[SoraPromptFromProduct] 产品名称: {product_name}")
        print(f"[SoraPromptFromProduct] 产品卖点: {product_features[:50]}...")
        print(f"[SoraPromptFromProduct] 最终用户提示词预览: {final_user[:200]}...")

        payload = {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": final_system},
                {"role": "user", "content": final_user}
            ],
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            raise_for_bad_status(resp, "AI 提示词生成失败")
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"AI 调用失败: {str(e)}")

        sora_prompt = ""
        try:
            choices = data.get("choices", [])
            if choices:
                sora_prompt = (choices[0].get("message") or {}).get("content", "").strip()
        except Exception:
            pass

        if not sora_prompt:
            raise RuntimeError(f"AI 响应缺少提示词: {json.dumps(data, ensure_ascii=False)[:500]}")

        print(f"[SoraPromptFromProduct] 生成的提示词长度: {len(sora_prompt)}")

        duration_seconds = duration.replace("秒", "")
        return (sora_prompt, duration_seconds, reference_image_url, json.dumps(data, ensure_ascii=False))

    def build(self, ocr_text, style="", camera="", motion="", lighting="", mood="", language="zh", extra=""):
        ocr_clean = ' '.join(ocr_text.split()).strip()
        if (language or "").lower().startswith("zh"):
            prompt = (
                f"根据参考图像进行风格与构图一致的动画生成；主体与场景源于参考图的语义要点。\n"
                f"主体与场景要点（OCR/解析）：{ocr_clean}\n风格：{style}\n镜头：{camera}\n"
                f"运动：{motion}\n光效：{lighting}\n情绪：{mood}\n"
                f"{('额外提示：' + extra.strip()) if extra.strip() else ''}\n"
                f"要求：画面稳定、自然过渡、细节丰富，避免过度变形或闪烁；保持与参考图视觉统一。"
            )
        else:
            prompt = (
                f"Animate in the same style and composition as the reference image.\n"
                f"Key elements: {ocr_clean}\nStyle: {style}\nCamera: {camera}\n"
                f"Motion: {motion}\nLighting: {lighting}\nMood: {mood}\n"
                f"{('Extra: ' + extra.strip()) if extra.strip() else ''}\n"
                f"Requirements: stable frames, natural transitions, rich details, avoid artifacts."
            )
        return (prompt,)

NODE_CLASS_MAPPINGS = {
    "ProductInfoBuilder": ProductInfoBuilder,
    "SoraPromptFromProduct": SoraPromptFromProduct,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ProductInfoBuilder": "📦 产品信息构建器",
    "SoraPromptFromProduct": "🤖 AI生成提示词",
}
