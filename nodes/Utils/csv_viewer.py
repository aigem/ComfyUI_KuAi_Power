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
        return {
            "required": {},
            "optional": {
                "upload": ("IMAGEUPLOAD", {"tooltip": "点击上传 CSV 文件（上传后需刷新节点）"}),
                "csv_path": ("STRING", {"default": "", "multiline": False, "tooltip": "直接输入 CSV 文件的完整路径"}),
                "max_rows": ("INT", {"default": 100, "min": 1, "max": 10000, "step": 1, "tooltip": "最多显示的行数"}),
            }
        }

    @classmethod
    def VALIDATE_INPUTS(cls, csv_path="", max_rows=100, upload=None):
        """验证输入参数 - 在节点创建时允许空值"""
        # 允许节点创建，在执行时再检查
        return True

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("表格数据",)
    FUNCTION = "view_csv"
    CATEGORY = "KuAi/配套能力"
    OUTPUT_NODE = True  # 标记为输出节点，这样可以在前端显示

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "upload": "上传文件",
            "csv_path": "文件路径",
            "max_rows": "最大行数",
        }

    @classmethod
    def IS_CHANGED(cls, csv_path="", max_rows=100, upload=None):
        """检测输入是否改变"""
        # 检查文件路径
        if csv_path and csv_path.strip():
            csv_path = csv_path.strip()
            if os.path.exists(csv_path):
                return os.path.getmtime(csv_path)

        return float("nan")

    def view_csv(self, upload=None, csv_path="", max_rows=100):
        """读取 CSV 文件并返回表格数据

        Args:
            upload: 文件上传 widget（上传后文件会保存到 input 目录）
            csv_path: 直接输入的文件路径（支持绝对路径或相对于 input 目录的路径）
            max_rows: 最多显示的行数
        """
        try:
            # 检查是否提供了文件路径
            if not csv_path or csv_path.strip() == "":
                raise ValueError(
                    "请输入 CSV 文件路径。\n\n"
                    "使用方法：\n"
                    "1. 点击 'upload' 上传文件到 ComfyUI/input/ 目录\n"
                    "2. 在 'csv_path' 中输入文件名（如 'myfile.csv'）或完整路径\n"
                    "3. 如果文件在 input 目录，只需输入文件名即可"
                )

            file_path = csv_path.strip()

            # 如果不是绝对路径，尝试从 input 目录读取
            if not os.path.isabs(file_path) and HAS_FOLDER_PATHS:
                try:
                    input_dir = folder_paths.get_input_directory()
                    potential_path = os.path.join(input_dir, file_path)
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        print(f"[CSVViewer] 从 input 目录读取: {csv_path}")
                except:
                    pass

            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"CSV 文件不存在: {file_path}\n\n"
                    f"请检查：\n"
                    f"1. 文件路径是否正确\n"
                    f"2. 文件是否已上传到 ComfyUI/input/ 目录\n"
                    f"3. 文件名是否包含正确的扩展名 (.csv)"
                )

            print(f"[CSVViewer] 读取文件: {file_path}")

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
