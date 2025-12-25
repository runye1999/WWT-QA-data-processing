import json
import os
import sys
from pathlib import Path

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def count_qa_pairs_in_folder(folder_path):
    """
    统计指定文件夹中所有JSON文件的问答对数
    
    Args:
        folder_path: 文件夹路径
    
    Returns:
        dict: 包含统计信息的字典
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"错误：文件夹 {folder_path} 不存在")
        return None
    
    total_pairs = 0
    file_stats = []
    
    # 遍历文件夹中的所有JSON文件
    json_files = list(folder.glob("*.json"))
    
    if not json_files:
        print(f"警告：在 {folder_path} 中未找到JSON文件")
        return None
    
    print(f"开始统计 {folder_path} 中的问答对...")
    print(f"找到 {len(json_files)} 个JSON文件\n")
    
    # 统计每个文件的问答对数
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 如果数据是列表，统计列表长度
            if isinstance(data, list):
                qa_count = len(data)
            else:
                # 如果不是列表，可能是单个对象
                qa_count = 1 if data else 0
            
            total_pairs += qa_count
            file_stats.append({
                'filename': json_file.name,
                'count': qa_count
            })
            
        except json.JSONDecodeError as e:
            print(f"警告：文件 {json_file.name} JSON解析失败: {e}")
            file_stats.append({
                'filename': json_file.name,
                'count': 0,
                'error': str(e)
            })
        except Exception as e:
            print(f"警告：读取文件 {json_file.name} 时出错: {e}")
            file_stats.append({
                'filename': json_file.name,
                'count': 0,
                'error': str(e)
            })
    
    # 输出统计结果
    print("=" * 80)
    print("统计结果")
    print("=" * 80)
    print(f"总文件数: {len(json_files)}")
    print(f"总问答对数: {total_pairs}")
    print(f"平均每个文件问答对数: {total_pairs / len(json_files):.2f}")
    print()
    
    # 找出问答对数最多和最少的文件
    valid_stats = [s for s in file_stats if 'error' not in s]
    if valid_stats:
        max_file = max(valid_stats, key=lambda x: x['count'])
        min_file = min(valid_stats, key=lambda x: x['count'])
        print()
        print(f"问答对数最多的文件: {max_file['count']} 对")
        print(f"问答对数最少的文件: {min_file['count']} 对")
    
    return {
        'total_files': len(json_files),
        'total_pairs': total_pairs,
        'average_pairs': total_pairs / len(json_files) if json_files else 0,
        'file_stats': file_stats
    }

if __name__ == "__main__":
    # paper1240文件夹路径
    paper1240_path = Path(__file__).parent / "text_to_qa" / "weixiu139"
    
    # 执行统计
    result = count_qa_pairs_in_folder(paper1240_path)
    
    if result:
        print()
        print("=" * 80)
        print("统计完成！")

