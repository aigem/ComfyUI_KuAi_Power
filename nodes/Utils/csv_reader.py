"""CSV 批量读取节点 - 用于批量图像生成任务"""

import csv
import os
import json

# 尝试导入 ComfyUI 的 folder_paths
try:
    import folder_paths
    HAS_FOLDER_PATHS = True
except ImportError:
    HAS_FOLDER_PATHS = False
    print("[CSVBatchReader] 警告: folder_paths 模块不可用，文件上传功能将受限")


class CSVBatchReader:
    """CSV 批量任务读取器 - 支持文件上传和路径输入"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "upload": ("IMAGEUPLOAD", {"tooltip": "点击上传 CSV 文件（上传后需刷新节点）"}),
                "csv_path": ("STRING", {"default": "", "multiline": False, "tooltip": "直接输入 CSV 文件的完整路径"}),
            }
        }

    @classmethod
    def VALIDATE_INPUTS(cls, csv_path="", upload=None):
        """验证输入参数 - 在节点创建时允许空值"""
        # 允许节点创建，在执行时再检查
        return True

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("批量任务数据",)
    FUNCTION = "read_csv"
    CATEGORY = "KuAi/配套能力"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "upload": "上传文件",
            "csv_path": "文件路径",
        }

    @classmethod
    def IS_CHANGED(cls, csv_path="", upload=None):
        """检测输入是否改变"""
        # 检查文件路径
        if csv_path and csv_path.strip():
            csv_path = csv_path.strip()
            if os.path.exists(csv_path):
                return os.path.getmtime(csv_path)

        return float("nan")

    def read_csv(self, upload=None, csv_path=""):
        """读取 CSV 文件并返回 JSON 格式的任务列表

        Args:
            upload: 文件上传 widget（上传后文件会保存到 input 目录）
            csv_path: 直接输入的文件路径（支持绝对路径或相对于 input 目录的路径）
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
                        print(f"[CSVBatchReader] 从 input 目录读取: {csv_path}")
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

            print(f"[CSVBatchReader] 读取文件: {file_path}")

            # 检查文件扩展名
            if not file_path.lower().endswith('.csv'):
                raise ValueError(f"文件必须是 CSV 格式: {file_path}")

            # 读取 CSV 文件
            tasks = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                # 验证必需的列
                if not reader.fieldnames:
                    raise ValueError("CSV 文件为空或格式不正确")

                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是标题）
                    # 跳过空行
                    if not any(row.values()):
                        continue

                    # 清理数据（去除空白）
                    cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                    cleaned_row['_row_number'] = row_num  # 添加行号用于调试
                    tasks.append(cleaned_row)

            if not tasks:
                raise ValueError("CSV 文件中没有有效的任务数据")

            # 转换为 JSON 字符串
            tasks_json = json.dumps(tasks, ensure_ascii=False, indent=2)

            print(f"[CSVBatchReader] 成功读取 {len(tasks)} 个任务")
            return (tasks_json,)

        except Exception as e:
            error_msg = f"读取 CSV 文件失败: {str(e)}"
            print(f"\033[91m[CSVBatchReader] {error_msg}\033[0m")
            raise RuntimeError(error_msg)


NODE_CLASS_MAPPINGS = {
    "CSVBatchReader": CSVBatchReader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CSVBatchReader": "CSV批量读取器",
}
