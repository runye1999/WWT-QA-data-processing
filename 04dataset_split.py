"""
该脚本将 JSON 数据集按不同比例划分为训练集、验证集和测试集。
根据数据集大小选择不同的划分比例。
保存划分后的数据集为 JSON 文件。
"""
import os
import json
from pathlib import Path
from sklearn.model_selection import train_test_split

INPUT_DIR = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\text_to_qa\standard"
OUTPUT_ROOT = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\datasplit\standard"
#确保输出目录下有 train / val / test 三个子文件夹
for subdir in ['train', 'val', 'test']:
    os.makedirs(os.path.join(OUTPUT_ROOT, subdir), exist_ok=True)
#将数据保存为json文件
def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
#定义一个函数 split_by_ratio，根据样本数量自动进行 train/val/test 划分，并保存到相应文件。
def split_by_ratio(data, base_name):
    total = len(data)

    if total >= 10:
        # 正常 8:1:1 划分
        train_size = 0.8
        val_test_size = 0.2
        train_data, temp = train_test_split(data, test_size=val_test_size, random_state=42)
        val_data, test_data = train_test_split(temp, test_size=0.5, random_state=42)

    elif total >= 5:#如果样本数在5-9之间
        train_num = max(3, int(total * 0.8))#按80%计算训练集数量，和3比较，取较大值，保证训练集至少3条
        val_num = max(1, (total - train_num) // 2)#剩余样本数一半给验证集，保证验证集至少1条
        test_num = total - train_num - val_num#剩下的全部作为测试集

        train_data = data[:train_num]
        val_data = data[train_num:train_num + val_num]
        test_data = data[train_num + val_num:]

    elif total >= 3:#如果样本数在3-4之间
        train_data = data[:1]#取第一条作为训练集
        val_data = data[1:2]#第二条作为验证集
        test_data = data[2:]#剩下的作为测试集
    else:
        # 少于3条时全部放入 train
        train_data, val_data, test_data = data, [], []

    # 保存
    save_json(train_data, os.path.join(OUTPUT_ROOT, 'train', f'{base_name}.json'))
    save_json(val_data, os.path.join(OUTPUT_ROOT, 'val', f'{base_name}.json'))
    save_json(test_data, os.path.join(OUTPUT_ROOT, 'test', f'{base_name}.json'))

    print(f"✅ {base_name}.json 总数: {total} → train={len(train_data)}, val={len(val_data)}, test={len(test_data)}")

def main():
    files = Path(INPUT_DIR).glob("*.json")#遍历目录中的所有json文件并处理
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)#读取并解析json文件内容
                if isinstance(data, list) and len(data) >= 1:
                    split_by_ratio(data, file.stem)#是一个列表并对数据进行划分
                else:
                    print(f"⚠️ 空文件或非数组格式：{file.name}")
            except Exception as e:
                print(f"❌ 加载失败：{file.name} 错误：{e}")

if __name__ == "__main__":
    main()
