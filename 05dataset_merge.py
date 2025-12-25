"""
合并指定文件夹下的 JSON 文件
"""
import os
import json
from pathlib import Path

INPUT_ROOT = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\datasplit\standard"
OUTPUT_DIR = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\datasplit\standard-dataset"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def merge_json_files(subdir_name):
    input_path = Path(INPUT_ROOT) / subdir_name
    merged_data = []

    for file in input_path.glob("*.json"):#取下面的所有json文件
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    merged_data.extend(data)#
                else:
                    print(f"⚠️ 文件格式错误（不是list）：{file.name}")
            except Exception as e:
                print(f"❌ 读取失败：{file.name} 错误：{e}")

    output_path = Path(OUTPUT_DIR) / f"{subdir_name}.json"
    with open(output_path, 'w', encoding='utf-8') as out_f:
        json.dump(merged_data, out_f, ensure_ascii=False, indent=2)

    print(f"✅ 合并完成：{subdir_name}.json | 样本总数: {len(merged_data)}")

def main():
    for split in ['train', 'val', 'test']:
        merge_json_files(split)

if __name__ == "__main__":
    main()
