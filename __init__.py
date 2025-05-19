"""
ComfyUI Little Tools - 视频下载工具
提供从URL下载视频的功能，支持多种格式和质量选项
"""

__version__ = "1.0.0"

from .load_video_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']