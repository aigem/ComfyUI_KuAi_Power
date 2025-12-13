"""CSV 批量读取节点 - 用于批量图像生成任务"""

import csv
import os
import json


class CSVBatchReader:
    """CSV 批量任务读取器"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "csv_path": ("STRING", {"default": "", "tooltip": "CSV 文件路径"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("批量任务数据",)
    FUNCTION = "read_csv"
    CATEGORY = "KuAi/Utils"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "csv_path": "CSV文件路径",
        }

    def read_csv(self, csv_path):
        """读取 CSV 文件并返回 JSON 格式的任务列表"""
        try:
            # 验证文件路径
            if not csv_path or not csv_path.strip():
                raise ValueError("CSV 文件路径不能为空")

            csv_path = csv_path.strip()

            # 检查文件是否存在
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")

            # 检查文件扩展名
            if not csv_path.lower().endswith('.csv'):
                raise ValueError(f"文件必须是 CSV 格式: {csv_path}")

            # 读取 CSV 文件
            tasks = []
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
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
