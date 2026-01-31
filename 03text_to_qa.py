"""
该脚本使用通义千问 API 根据文本内容生成问答对，并将其转换为 Alpaca 格式保存为 JSON 文件。
检测文件编码并读取文本内容。
根据文件大小决定生成问答对的数量。
调用通义千问 API 生成问答对。
将问答对转换为 Alpaca 格式并保存为 JSON 文件。
政策问答提示词：
        prompt = (
        "您是中文污水处理政策/法规/标准问答生成助手。\n"
        "任务：\n"
        f"根据以下文本，生成至少 {qa_count} 个高质量问答对，确保问答内容严格基于文本。\n"
        "内容范围：\n"
        "- 适用范围/适用性\n"
        "- 主要要求\n"
        "- 指标限​​值/阈值（包括单位和条件）\n"
        "- 职责/角色\n"
        "- 实施程序/工作流程（包括报告/记录/验收，如有提及）\n"
        "规则：\n\n"
        "1) 请勿添加文本中未提及的信息。如果文本中没有某个细节，请勿推断。\n"
        "2) 请用中文撰写。\n"
        '3) 优先选择可检查合规性的问题（例如，"应当/不应当"、"必须/不得"、"限值/阈值"、"监测/采样频率"、"责任方/实体"、"程序步骤/工作流程"）。\n'
        "4) 避免重复或近似重复；每个问答对应针对不同的条款/要点。\n"
        "5) 答案务必简洁明了。请完全保留原文中的数字、单位和条件。\n"
        "输出：\n"
        "仅返回一个 JSON 数组，例如：\n"
        "[\n"
        '{"question":"...", "answer":"..."},\n'
        "...\n"
        "]\n"
        "文本：\n"
        f"{text}"
    )

    try:
        response = dashscope.Generation.call(
            model='qwen-turbo',
            messages=[
                {'role': 'system', 'content': '您是中文污水处理政策/法规/标准问答生成助手。'},#设定模型角色
                {'role': 'user', 'content': prompt}#用户的内容就是上面构造的prompt
            ],
            result_format='message',#指定返回格式为“message”形式（SDK 自己的格式）
            temperature=0.7,#默认值
            max_tokens=2048  # 限制模型最大输出长度
        )#调用通义千问生成接口
"""
import os
import json
import chardet
from pathlib import Path
import dashscope#导入通义千问SDK，用于调用大模型生成问答

# 设置你的通义千问 API 密钥，用于认证你调用通义千问API的身份
dashscope.api_key = 'sk-'  # ←←← 替换为你的密钥

# 自定义输出文件夹，创建一个 Path 对象，表示输出 JSON 文件存放的目录。
OUTPUT_DIR = Path(r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\text_to_qa")  # ←←← 你可以修改为任意路径
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)#如果目录不存在，创建。如果存在，不报错

"""检测文本文件的编码"""
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:#以二进制打开文件，因为chardet需要原始字节
        raw_data = f.read()#读出全部字节内容
    result = chardet.detect(raw_data)#用 chardet 检测编码，返回一个字典
    return result['encoding'] or 'utf-8'#取检测到的编码，如果没有检测出来默认utf-8

def read_text(file_path):
    encoding = detect_encoding(file_path)#先检测文件编码方式
    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:#按文件编码方式以文本模式r打开文件，把整个文件内容读成一个字符串返回
        return f.read()

"""根据文件大小决定问答对数量"""
def decide_qa_count(file_size_bytes):
    kb = file_size_bytes / 1024
    if kb < 5:
        return 5
    elif kb < 20:
        return 10
    elif kb < 50:
        return 15
    elif kb < 100:
        return 20
    elif kb < 300:
        return 30
    elif kb < 600:
        return 40
    else:
        return 50
"""调用通义千问生成问答对
text：整个文章内容
qa_count：希望生成的问答对数量
"""
def generate_qa_pairs(text, qa_count):
    prompt = (
        "您是一位负责生成中文污水处理运行知识问答对的助手。\n\n"
        "任务：\n"
        f"根据以下文本，生成至少 {qa_count} 个信息丰富、不冗余且严格基于文本的问答对。\n\n"
        "涵盖范围：\n"
        "- 定义/概念\n"
        "- 原理/机制\n"
        "- 工艺流程/步骤\n"
        "- 效益/适用性\n"
        "- 注意事项/限制/安全须知\n"
        "- 常见问题/故障模式\n"
        "- 控制策略/故障排除措施\n"
        "规则：\n"
        "1) 请勿添加文本中未提及的信息。请勿推断缺失的细节。\n"
        "2) 请用中文撰写。\n"
        "3) 优先选择涵盖关键原理和概念的问题，以及具有高度实用性和可操作性的问题（例如，参数、运行条件、程序/步骤、异常情况、可能原因、纠正措施和检查）。\n"
        "4) 避免重复或近似重复；每个问答对应针对一个不同的要点。\n"
        "5) 答案应简洁明了。请完全保留文本中的数字、单位和条件。\n"
        "输出：\n"
        "仅返回一个 JSON 数组，例如：\n"
        "[\n"
        '{"question":"...", "answer":"..."},\n'
        "...\n"
        "]\n"
        "文本：\n"
        f"{text}"
    )

    try:
        response = dashscope.Generation.call(
            model='qwen-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a question-answer pair generation assistant for Chinese wastewater-treatment operational knowledge.'},#设定模型角色
                {'role': 'user', 'content': prompt}#用户的内容就是上面构造的prompt
            ],
            result_format='message',#指定返回格式为“message”形式（SDK 自己的格式）
            temperature=0.7,#默认值
            max_tokens=2048  # 限制模型最大输出长度
        )#调用通义千问生成接口
        print(response)
        content = response['output']['choices'][0]['message']['content'].strip()#提取通义千问模型实际生成的内容，并去掉首尾空白字符
        json_start = content.find('[')#找到第一个[的位置
        json_end = content.rfind(']') + 1#找到最后一个 ] 的位置再加 1

        #取出从第一个[到最后一个]的字串，把这个字符除按解析成python列表，每个元素就是一个字典
        qa_list = json.loads(content[json_start:json_end])
        return qa_list#返回问答对列表
    except Exception as e:
        print(f"[❌ ERROR] API 调用失败或 JSON 解析错误：{e}")
        return []
"""处理一个文件夹里的所有txt文件"""
def process_folder(input_folder):
    folder = Path(input_folder)
    txt_files = list(folder.glob("*.txt"))#所有txt文件路径
    if not txt_files:
        print("⚠️ 没有找到 .txt 文件")
        return

    for txt_path in txt_files:
        print(f"\n📄 正在处理: {txt_path.name}")
        file_size = txt_path.stat().st_size#返回文件大小 30585517B
        #30585517 字节 ≈ 29868.7 KB，生成 50 个问答对
        qa_count = decide_qa_count(file_size)#生成的问答对个数
        print(f"📏 文件大小: {file_size} 字节 ≈ {file_size/1024:.1f} KB，生成 {qa_count} 个问答对")

        text = read_text(txt_path)#读取文本内容
        if not text.strip():
            print("⚠️ 文本内容为空，跳过")
            continue

        qa_pairs = generate_qa_pairs(text, qa_count)#传入全文内容和问答数量，调用通义千问。生成问答对
        if not qa_pairs:
            print("⚠️ 没有生成问答对")
            continue

        # 转换为 Alpaca 格式
        alpaca_data = []
        output_path = OUTPUT_DIR / f"{txt_path.stem}.json"#abc.txt → abc
        if output_path.exists():
            print(f"⏩ 已存在转换文件，跳过：{output_path.name}")
            continue
        for pair in qa_pairs:#遍历每一个问答对
            if isinstance(pair, str):
                try:
                    pair = json.loads(pair)
                    print(pair)
                except json.JSONDecodeError:
                    print(f"⚠️ 跳过无法解析的问答对：{pair}")
                    continue
            if not isinstance(pair, dict):
                print(f"⚠️ 跳过非字典格式的问答对：{pair}")
                continue
            question = pair.get("question", "").strip()#取出question字段并去掉首尾空白
            answer = pair.get("answer", "").strip()
            if question and answer:#都非空
                alpaca_data.append({
                    "instruction": question,#问题
                    "input": "",#有些任务会用input传入上下文
                    "output": answer#答案
                })

        # 写入 JSON 文件（仅包含问答对列表）
        with open(output_path, "w", encoding="utf-8") as f:#以写模式、utf-8 编码打开输出文件
            json.dump(alpaca_data, f, ensure_ascii=False, indent=2)#把alpaca_data写入json文件，保证直接写入中文，缩进2个空格方便阅读

        print(f"✅ 已保存（Alpaca 格式）：{output_path.resolve()}")

if __name__ == "__main__":
    #修改输入文件夹路径
    input_dir = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing1\wordtxt"  # ←←← 替换为你的输入路径
    process_folder(input_dir)
