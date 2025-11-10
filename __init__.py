"""ComfyUI_KuAi_Power 多节点"""

import os
import importlib
from pathlib import Path

# 节点映射
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def auto_register_nodes():
    """自动扫描并注册 nodes 目录下的所有节点"""
    nodes_dir = Path(__file__).parent / "nodes"
    
    if not nodes_dir.exists():
        return
    
    # 直接加载根级别的模块（script_generator.py, sora2.py）
    for node_file in nodes_dir.glob("*.py"):
        if node_file.name.startswith("_") or node_file.name == "utils.py":
            continue
        
        try:
            module_path = f".nodes.{node_file.stem}"
            mod = importlib.import_module(module_path, package=__name__)
            cls_map = getattr(mod, "NODE_CLASS_MAPPINGS", {})
            name_map = getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
            NODE_CLASS_MAPPINGS.update(cls_map)
            NODE_DISPLAY_NAME_MAPPINGS.update(name_map)
            print(f"[ComfyUI_KuAi_Power] Loaded {len(cls_map)} nodes from {node_file.stem}")
        except Exception as e:
            print(f"[ComfyUI_KuAi_Power] Failed to load {node_file.name}: {e}")
    
    # 遍历子目录（脚本生成, NanoBanana, Sora2）
    for category_dir in nodes_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("_"):
            continue
        
        # 检查是否有 __init__.py
        init_file = category_dir / "__init__.py"
        if init_file.exists():
            try:
                module_path = f".nodes.{category_dir.name}"
                mod = importlib.import_module(module_path, package=__name__)
                cls_map = getattr(mod, "NODE_CLASS_MAPPINGS", {})
                name_map = getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
                NODE_CLASS_MAPPINGS.update(cls_map)
                NODE_DISPLAY_NAME_MAPPINGS.update(name_map)
                print(f"[ComfyUI_KuAi_Power] Loaded {len(cls_map)} nodes from {category_dir.name}")
            except Exception as e:
                print(f"[ComfyUI_KuAi_Power] Failed to load {category_dir.name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            # 没有 __init__.py，直接扫描 .py 文件
            for node_file in category_dir.glob("*.py"):
                if node_file.name.startswith("_"):
                    continue
                
                try:
                    module_path = f".nodes.{category_dir.name}.{node_file.stem}"
                    mod = importlib.import_module(module_path, package=__name__)
                    
                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if (isinstance(attr, type) and 
                            hasattr(attr, "INPUT_TYPES") and 
                            hasattr(attr, "RETURN_TYPES")):
                            
                            NODE_CLASS_MAPPINGS[attr_name] = attr
                            display_name = attr_name
                            NODE_DISPLAY_NAME_MAPPINGS[attr_name] = display_name
                            print(f"[ComfyUI_KuAi_Power] Auto-registered: {attr_name}")
                except Exception as e:
                    print(f"[ComfyUI_KuAi_Power] Failed to load {node_file.name}: {e}")

# 自动注册所有节点
auto_register_nodes()

# 前端扩展
WEB_DIRECTORY = "./web"

# 导出
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print(f"[ComfyUI_KuAi_Power] Total loaded: {len(NODE_CLASS_MAPPINGS)} nodes")
print(f"[ComfyUI_KuAi_Power] Nodes: {list(NODE_CLASS_MAPPINGS.keys())}")
