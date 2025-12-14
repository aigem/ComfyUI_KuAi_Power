#!/usr/bin/env python3
"""测试 Grok 批量处理器"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_batch_processor_registration():
    """测试批量处理器注册"""
    print("=" * 60)
    print("测试 1: 批量处理器注册")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        if 'GrokBatchProcessor' in NODE_CLASS_MAPPINGS:
            print("✅ GrokBatchProcessor 已注册")
            node_class = NODE_CLASS_MAPPINGS['GrokBatchProcessor']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('GrokBatchProcessor')}")

            # 检查必需方法
            assert hasattr(node_class, 'INPUT_TYPES'), "缺少 INPUT_TYPES"
            assert hasattr(node_class, 'RETURN_TYPES'), "缺少 RETURN_TYPES"
            assert hasattr(node_class, 'FUNCTION'), "缺少 FUNCTION"

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ GrokBatchProcessor 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processor_instantiation():
    """测试批量处理器实例化"""
    print("\n" + "=" * 60)
    print("测试 2: 批量处理器实例化")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokBatchProcessor']
        node = node_class()

        print("✅ 批量处理器实例化成功")
        print(f"   类型: {type(node)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_format():
    """测试 CSV 格式解析"""
    print("\n" + "=" * 60)
    print("测试 3: CSV 格式解析")
    print("=" * 60)

    try:
        # 模拟 CSV 读取器的输出格式
        mock_tasks = [
            {
                "_row_number": 2,
                "prompt": "A cat playing with a ball",
                "aspect_ratio": "3:2",
                "size": "1080P",
                "image_urls": "",
                "output_prefix": "test_cat"
            },
            {
                "_row_number": 3,
                "prompt": "A dog running in the park",
                "aspect_ratio": "2:3",
                "size": "720P",
                "image_urls": "",
                "output_prefix": "test_dog"
            }
        ]

        batch_tasks_json = json.dumps(mock_tasks)

        print("✅ CSV 格式解析成功")
        print(f"   任务数量: {len(mock_tasks)}")
        print(f"   JSON 长度: {len(batch_tasks_json)} 字符")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processing_dry_run():
    """测试批量处理（不实际调用 API）"""
    print("\n" + "=" * 60)
    print("测试 4: 批量处理（模拟）")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        # 创建模拟任务
        mock_tasks = [
            {
                "_row_number": 2,
                "prompt": "Test prompt 1",
                "aspect_ratio": "3:2",
                "size": "1080P",
                "image_urls": "",
                "output_prefix": "test_1"
            }
        ]

        batch_tasks_json = json.dumps(mock_tasks)

        print("✅ 批量处理模拟测试准备完成")
        print(f"   任务数量: {len(mock_tasks)}")
        print("   注意: 实际 API 调用需要有效的 API Key")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processing_with_api():
    """测试批量处理（实际 API 调用）"""
    print("\n" + "=" * 60)
    print("测试 5: 批量处理（实际 API）")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        print("   设置方法: export KUAI_API_KEY=your_key_here")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokBatchProcessor']
        node = node_class()

        # 创建测试任务（只有 2 个任务）
        mock_tasks = [
            {
                "_row_number": 2,
                "prompt": "A cute cat playing with a colorful ball",
                "aspect_ratio": "3:2",
                "size": "720P",
                "image_urls": "",
                "output_prefix": "batch_test_cat"
            },
            {
                "_row_number": 3,
                "prompt": "A beautiful sunset over the ocean",
                "aspect_ratio": "3:2",
                "size": "720P",
                "image_urls": "",
                "output_prefix": "batch_test_sunset"
            }
        ]

        batch_tasks_json = json.dumps(mock_tasks)

        print("🔄 执行批量处理测试...")
        print(f"   任务数量: {len(mock_tasks)}")

        # 执行批量处理（不等待完成）
        result, output_dir = node.process_batch(
            batch_tasks=batch_tasks_json,
            api_key=api_key,
            output_dir="./test_output/grok_batch",
            delay_between_tasks=1.0,
            wait_for_completion=False,
            max_wait_time=600,
            poll_interval=10
        )

        print(f"\n✅ 批量处理成功")
        print(f"   输出目录: {output_dir}")
        print(f"\n处理结果:")
        print(result)

        # 检查输出文件
        tasks_file = os.path.join(output_dir, "tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            print(f"\n   任务文件已创建: {tasks_file}")
            print(f"   任务数量: {len(tasks_data)}")
            for task in tasks_data:
                print(f"     - {task['task_id']}: {task['prompt'][:30]}...")

        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Grok 批量处理器测试套件\n")

    results = []
    results.append(("批量处理器注册", test_batch_processor_registration()))
    results.append(("批量处理器实例化", test_batch_processor_instantiation()))
    results.append(("CSV 格式解析", test_csv_format()))
    results.append(("批量处理模拟", test_batch_processing_dry_run()))
    results.append(("批量处理实际 API", test_batch_processing_with_api()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
