"""测试节点 INPUT_LABELS 是否正确"""
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from nodes.Sora2 import NODE_CLASS_MAPPINGS as SORA2_MAPPINGS
from nodes.Utils import NODE_CLASS_MAPPINGS as UTILS_MAPPINGS

all_mappings = {}
all_mappings.update(SORA2_MAPPINGS)
all_mappings.update(UTILS_MAPPINGS)

print("=" * 60)
print("检查所有节点的 INPUT_LABELS")
print("=" * 60)

for node_name, node_class in all_mappings.items():
    print(f"\n节点: {node_name}")
    print(f"类名: {node_class.__name__}")
    
    # 检查是否有 INPUT_LABELS
    if hasattr(node_class, 'INPUT_LABELS'):
        print("✓ 有 INPUT_LABELS 方法")
        
        # 获取 INPUT_TYPES
        input_types = node_class.INPUT_TYPES()
        all_params = set()
        if 'required' in input_types:
            all_params.update(input_types['required'].keys())
        if 'optional' in input_types:
            all_params.update(input_types['optional'].keys())
        
        # 获取 INPUT_LABELS
        input_labels = node_class.INPUT_LABELS()
        
        print(f"  INPUT_TYPES 参数: {sorted(all_params)}")
        print(f"  INPUT_LABELS 参数: {sorted(input_labels.keys())}")
        
        # 检查是否匹配
        missing = all_params - set(input_labels.keys())
        extra = set(input_labels.keys()) - all_params
        
        if missing:
            print(f"  ⚠ 缺少标签: {missing}")
        if extra:
            print(f"  ⚠ 多余标签: {extra}")
        if not missing and not extra:
            print("  ✓ 参数完全匹配")
            
        # 显示标签内容
        print("  标签内容:")
        for key, label in input_labels.items():
            print(f"    {key}: {label}")
    else:
        print("✗ 没有 INPUT_LABELS 方法")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
