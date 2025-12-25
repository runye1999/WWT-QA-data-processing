import os
import json
from pathlib import Path
"""
合并多个包含 `val.json` 的子目录下的数据。
"""
# 所有包含 train.json 的子目录
SOURCE_DIRS = [
    r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\datasplit\paper-dataset",
    r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\datasplit\Technical-dataset",
    r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\datasplit\internal-dataset"
]

OUTPUT_FILE = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\final_dataset\val.json"
#os.makedirs("final_dataset", exist_ok=True)

def merge_trains(source_dirs, output_file):
    all_data = []

    for dir_path in source_dirs:
        train_path = Path(dir_path) / "val.json"
        if train_path.exists():
            with open(train_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                        print(f"✅ 加载：{train_path}，数量: {len(data)}")
                    else:
                        print(f"⚠️ 跳过（不是列表格式）：{train_path}")
                except Exception as e:
                    print(f"❌ 读取失败：{train_path}，错误：{e}")
        else:
            print(f"⚠️ 未找到：{train_path}")

    with open(output_file, "w", encoding="utf-8") as f_out:
        json.dump(all_data, f_out, ensure_ascii=False, indent=2)
        print(f"\n✅ 合并完成：{output_file}，总计样本数: {len(all_data)}")

# 执行合并
merge_trains(SOURCE_DIRS, OUTPUT_FILE)
