"""CSV 查看器节点 - 以表格形式查看 CSV 文件内容"""

import csv
import os
import json

# 尝试导入 ComfyUI 的 folder_paths
try:
    import folder_paths
    HAS_FOLDER_PATHS = True
except ImportError:
    HAS_FOLDER_PATHS = False
    print("[CSVViewer] 警告: folder_paths 模块不可用，文件上传功能将受限")


class CSVViewer:
    """CSV 查看器 - 以表格形式显示 CSV 文件内容"""

    @classmethod
    def INPUT_TYPES(cls):
        # 获取上传的 CSV 文件列表
        csv_files = []
        if HAS_FOLDER_PATHS:
            try:
                input_dir = folder_paths.get_input_directory()
                if os.path.exists(input_dir):
                    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
            except Exception as e:
                print(f"[CSVViewer] 无法读取 input 目录: {e}")

        # 如果没有文件，提供一个提示选项
        if not csv_files:
            csv_files = ["请先上传CSV文件到input目录"]

        return {
            "required": {
                "csv_file": (sorted(csv_files), {"tooltip": "从下拉菜单选择已上传的 CSV 文件"}),
            },
            "optional": {
                "upload": ("IMAGEUPLOAD", {"tooltip": "点击上传 CSV 文件（上传后需刷新节点）"}),
                "csv_path": ("STRING", {"default": "", "multiline": False, "tooltip": "或者直接输入 CSV 文件的完整路径"}),
                "max_rows": ("INT", {"default": 100, "min": 1, "max": 10000, "step": 1, "tooltip": "最多显示的行数"}),
            }
        }

    @classmethod
    def VALIDATE_INPUTS(cls, csv_file=None, csv_path="", max_rows=100, upload=None):
        """验证输入参数"""
        # 如果两个参数都没有提供
        if (not csv_file or csv_file == "" or csv_file == "请先上传CSV文件到input目录") and (not csv_path or csv_path.strip() == ""):
            return "请上传 CSV 文件或输入文件路径"
        return True

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("表格数据",)
    FUNCTION = "view_csv"
    CATEGORY = "KuAi/配套能力"
    OUTPUT_NODE = True  # 标记为输出节点，这样可以在前端显示

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "csv_file": "CSV文件",
            "upload": "上传文件",
            "csv_path": "文件路径",
            "max_rows": "最大行数",
        }

    @classmethod
    def IS_CHANGED(cls, csv_file=None, csv_path="", max_rows=100, upload=None):
        """检测输入是否改变"""
        # 优先使用 csv_file
        if csv_file and csv_file != "请先上传CSV文件到input目录" and HAS_FOLDER_PATHS:
            try:
                input_dir = folder_paths.get_input_directory()
                file_path = os.path.join(input_dir, csv_file)
                if os.path.exists(file_path):
                    return os.path.getmtime(file_path)
            except:
                pass

        # 其次使用 csv_path
        if csv_path and csv_path.strip():
            csv_path = csv_path.strip()
            if os.path.exists(csv_path):
                return os.path.getmtime(csv_path)

        return float("nan")

    def view_csv(self, csv_file=None, upload=None, csv_path="", max_rows=100):
        """读取 CSV 文件并返回表格数据

        Args:
            csv_file: 从下拉菜单选择的文件名
            upload: 文件上传 widget（仅用于触发上传界面）
            csv_path: 直接输入的文件路径
            max_rows: 最多显示的行数
        """
        try:
            # 确定文件路径（优先使用 csv_file）
            file_path = None

            if csv_file and csv_file.strip() and csv_file != "请先上传CSV文件到input目录":
                # 从 ComfyUI 的 input 目录读取
                if not HAS_FOLDER_PATHS:
                    raise RuntimeError("文件上传功能不可用，请使用 csv_path 参数直接输入文件路径")

                input_dir = folder_paths.get_input_directory()
                file_path = os.path.join(input_dir, csv_file)

                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"上传的文件不存在: {csv_file}")

                print(f"[CSVViewer] 读取上传的文件: {csv_file}")

            elif csv_path and csv_path.strip():
                # 使用直接输入的路径
                file_path = csv_path.strip()

                # 检查文件是否存在
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"CSV 文件不存在: {file_path}")

                print(f"[CSVViewer] 读取路径文件: {file_path}")

            else:
                raise ValueError("请上传 CSV 文件或输入文件路径")

            # 检查文件扩展名
            if not file_path.lower().endswith('.csv'):
                raise ValueError(f"文件必须是 CSV 格式: {file_path}")

            # 读取 CSV 文件
            rows = []
            headers = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)

                # 读取标题行
                try:
                    headers = next(reader)
                except StopIteration:
                    raise ValueError("CSV 文件为空")

                # 读取数据行（限制最大行数）
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)

            if not rows:
                raise ValueError("CSV 文件中没有数据行")

            # 构建表格数据结构
            table_data = {
                "type": "csv_table",
                "headers": headers,
                "rows": rows,
                "total_rows": len(rows),
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
            }

            # 转换为 JSON 字符串
            table_json = json.dumps(table_data, ensure_ascii=False, indent=2)

            print(f"[CSVViewer] 成功读取 {len(rows)} 行数据（共 {len(headers)} 列）")

            # 返回表格数据和 UI 配置
            return {"ui": {"csv_table": [table_data]}, "result": (table_json,)}

        except Exception as e:
            error_msg = f"读取 CSV 文件失败: {str(e)}"
            print(f"\033[91m[CSVViewer] {error_msg}\033[0m")
            raise RuntimeError(error_msg)


NODE_CLASS_MAPPINGS = {
    "CSVViewer": CSVViewer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CSVViewer": "CSV查看器",
}
