"""Grok 视频生成节点集合"""

from .grok import GrokCreateVideo, GrokQueryVideo, GrokCreateAndWait
from .batch_processor import GrokBatchProcessor

NODE_CLASS_MAPPINGS = {
    "GrokCreateVideo": GrokCreateVideo,
    "GrokQueryVideo": GrokQueryVideo,
    "GrokCreateAndWait": GrokCreateAndWait,
    "GrokBatchProcessor": GrokBatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokCreateVideo": "🤖 Grok 创建视频",
    "GrokQueryVideo": "🔍 Grok 查询视频",
    "GrokCreateAndWait": "⚡ Grok 一键生成视频",
    "GrokBatchProcessor": "📦 Grok 批量处理器",
}
