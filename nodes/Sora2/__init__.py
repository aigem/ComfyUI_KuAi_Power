"""Sora2 节点模块 - 统一导出"""

from .script_generator import (
    ProductInfoBuilder,
    SoraPromptFromProduct,
    NODE_CLASS_MAPPINGS as SCRIPT_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as SCRIPT_DISPLAY_MAPPINGS
)

from .sora2 import (
    SoraCreateVideo,
    SoraQueryTask,
    SoraCreateAndWait,
    SoraText2Video,
    NODE_CLASS_MAPPINGS as SORA2_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as SORA2_DISPLAY_MAPPINGS
)

# 合并所有节点映射
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(SCRIPT_MAPPINGS)
NODE_CLASS_MAPPINGS.update(SORA2_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(SCRIPT_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(SORA2_DISPLAY_MAPPINGS)

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    # Script Generator
    "ProductInfoBuilder",
    "SoraPromptFromProduct",
    # Sora2 API
    "SoraCreateVideo",
    "SoraQueryTask",
    "SoraCreateAndWait",
    "SoraText2Video",
]
