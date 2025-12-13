#!/usr/bin/env python3
"""测试 CSV 节点功能"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        # 检查 CSVBatchReader
        if 'CSVBatchReader' in NODE_CLASS_MAPPINGS:
            print("✅ CSVBatchReader 已注册")
            reader = NODE_CLASS_MAPPINGS['CSVBatchReader']
            print(f"   分类: {reader.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('CSVBatchReader', 'CSVBatchReader')}")

            # 检查 INPUT_TYPES
            input_types = reader.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            # 检查是否有 upload 参数
            if 'upload' in input_types.get('optional', {}):
                print("   ✅ 支持文件上传功能")
            else:
                print("   ❌ 不支持文件上传功能")
        else:
            print("❌ CSVBatchReader 未注册")

        print()

        # 检查 CSVViewer
        if 'CSVViewer' in NODE_CLASS_MAPPINGS:
            print("✅ CSVViewer 已注册")
            viewer = NODE_CLASS_MAPPINGS['CSVViewer']
            print(f"   分类: {viewer.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('CSVViewer', 'CSVViewer')}")

            # 检查 INPUT_TYPES
            input_types = viewer.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            # 检查是否有 upload 参数
            if 'upload' in input_types.get('optional', {}):
                print("   ✅ 支持文件上传功能")
            else:
                print("   ❌ 不支持文件上传功能")

            # 检查是否是输出节点
            if hasattr(viewer, 'OUTPUT_NODE') and viewer.OUTPUT_NODE:
                print("   ✅ 标记为输出节点（支持 UI 显示）")
            else:
                print("   ⚠️  未标记为输出节点")
        else:
            print("❌ CSVViewer 未注册")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_reader_functionality():
    """测试 CSVBatchReader 功能"""
    print("\n" + "=" * 60)
    print("测试 2: CSVBatchReader 功能")
    print("=" * 60)

    try:
        from nodes.Utils.csv_reader import CSVBatchReader

        # 创建测试 CSV 文件
        test_csv_path = "/tmp/test_batch.csv"
        with open(test_csv_path, 'w', encoding='utf-8') as f:
            f.write("task_type,prompt,seed\n")
            f.write("generate,Test image 1,42\n")
            f.write("generate,Test image 2,123\n")

        print(f"✅ 创建测试 CSV 文件: {test_csv_path}")

        # 测试读取
        reader = CSVBatchReader()
        result = reader.read_csv(csv_path=test_csv_path)

        print("✅ 成功读取 CSV 文件")
        print(f"   返回类型: {type(result)}")
        print(f"   返回长度: {len(result)}")

        # 解析 JSON
        import json
        tasks = json.loads(result[0])
        print(f"   任务数量: {len(tasks)}")
        print(f"   第一个任务: {tasks[0]}")

        # 清理
        os.remove(test_csv_path)
        print("✅ 清理测试文件")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_viewer_functionality():
    """测试 CSVViewer 功能"""
    print("\n" + "=" * 60)
    print("测试 3: CSVViewer 功能")
    print("=" * 60)

    try:
        from nodes.Utils.csv_viewer import CSVViewer

        # 创建测试 CSV 文件
        test_csv_path = "/tmp/test_viewer.csv"
        with open(test_csv_path, 'w', encoding='utf-8') as f:
            f.write("列1,列2,列3\n")
            f.write("数据1,数据2,数据3\n")
            f.write("数据4,数据5,数据6\n")

        print(f"✅ 创建测试 CSV 文件: {test_csv_path}")

        # 测试读取
        viewer = CSVViewer()
        result = viewer.view_csv(csv_path=test_csv_path, max_rows=100)

        print("✅ 成功读取 CSV 文件")
        print(f"   返回类型: {type(result)}")

        # 检查返回结构
        if isinstance(result, dict):
            if 'ui' in result:
                print("   ✅ 包含 UI 数据")
                if 'csv_table' in result['ui']:
                    table_data = result['ui']['csv_table'][0]
                    print(f"   表格标题: {table_data.get('headers')}")
                    print(f"   数据行数: {table_data.get('total_rows')}")
                    print(f"   文件名: {table_data.get('file_name')}")
            if 'result' in result:
                print("   ✅ 包含结果数据")

        # 清理
        os.remove(test_csv_path)
        print("✅ 清理测试文件")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_extension():
    """测试前端扩展文件"""
    print("\n" + "=" * 60)
    print("测试 4: 前端扩展文件")
    print("=" * 60)

    csv_viewer_js = os.path.join(os.path.dirname(__file__), "web", "csv_viewer.js")

    if os.path.exists(csv_viewer_js):
        print(f"✅ 前端扩展文件存在: {csv_viewer_js}")

        # 检查文件内容
        with open(csv_viewer_js, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'KuAi.CSVViewer' in content:
            print("   ✅ 包含扩展注册代码")
        if 'CSVViewer' in content:
            print("   ✅ 包含节点名称匹配")
        if 'csv_table' in content:
            print("   ✅ 包含表格数据处理")
        if 'createTableHTML' in content:
            print("   ✅ 包含表格 HTML 生成")
        if 'csv-table-container' in content:
            print("   ✅ 包含表格样式")

        return True
    else:
        print(f"❌ 前端扩展文件不存在: {csv_viewer_js}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("CSV 节点功能测试")
    print("=" * 60 + "\n")

    results = []

    # 运行测试
    results.append(("节点注册", test_node_registration()))
    results.append(("CSVBatchReader 功能", test_csv_reader_functionality()))
    results.append(("CSVViewer 功能", test_csv_viewer_functionality()))
    results.append(("前端扩展", test_frontend_extension()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    # 总体结果
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
