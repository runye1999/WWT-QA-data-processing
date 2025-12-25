import json

"""
检查数据集有无问题
支持两种格式：
1. 标准 JSON 数组格式（整个文件是一个 JSON 数组）
2. JSON Lines 格式（每行是一个 JSON 对象）
"""
def validate_dataset_format(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # 首先尝试作为标准 JSON 数组解析
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    # 标准 JSON 数组格式
                    print(f"检测到标准 JSON 数组格式，共 {len(data)} 条记录")
                    for idx, item in enumerate(data):
                        if not isinstance(item, dict):
                            raise ValueError(f"第{idx+1}条记录不是字典格式")
                        # 检查必填字段是否存在
                        if not all(key in item for key in ["instruction", "output"]):
                            raise ValueError(f"第{idx+1}条记录缺少必填字段（instruction/output）")
                        # 可选：检查input字段类型（允许为空字符串）
                        if "input" in item and not isinstance(item["input"], str):
                            raise ValueError(f"第{idx+1}条记录input字段非字符串类型")
                    print("✅ 数据集格式验证通过！")
                    return True
                else:
                    raise ValueError("JSON 内容不是数组格式")
            except json.JSONDecodeError:
                # 如果标准 JSON 解析失败，尝试 JSON Lines 格式
                print("尝试 JSON Lines 格式...")
                f.seek(0)  # 重置文件指针
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue  # 跳过空行
                    data = json.loads(line)
                    # 检查必填字段是否存在
                    if not all(key in data for key in ["instruction", "output"]):
                        raise ValueError(f"第{idx+1}行缺少必填字段（instruction/output）")
                    # 可选：检查input字段类型（允许为空字符串）
                    if "input" in data and not isinstance(data["input"], str):
                        raise ValueError(f"第{idx+1}行input字段非字符串类型")
                print("✅ 数据集格式验证通过！")
                return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误：{e.msg}，位置：第{e.lineno}行第{e.colno}列")
        return False
    except Exception as e:
        print(f"❌ 其他错误：{e}")
        return False

# 调用验证函数
validate_dataset_format(r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\zhishifinal\test.json")