"""
将 PDF 文件转换为 Word 文件
"""
import os
from win32com.client import Dispatch

# ======= 自己改这里的路径 =======
INPUT_DIR = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\pdf"          # 放 PDF 的文件夹
OUTPUT_DIR = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\pdf"        # 输出 Word 的文件夹
# =================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

def convert_all_pdfs_to_docx(input_dir, output_dir):
    # 打开 Word 程序（不显示窗口）
    word = Dispatch("Word.Application")
    word.Visible = False

    try:
        for root, dirs, files in os.walk(input_dir):
            # 保持原有子目录结构
            rel_root = os.path.relpath(root, input_dir)
            out_root = os.path.join(output_dir, rel_root)
            os.makedirs(out_root, exist_ok=True)

            for fname in files:
                if not fname.lower().endswith(".pdf"):
                    continue

                in_path = os.path.join(root, fname)
                base_name = os.path.splitext(fname)[0]
                out_path = os.path.join(out_root, base_name + ".docx")

                # 如果已经转换过，可以选择跳过
                if os.path.exists(out_path):
                    print("已存在，跳过：", out_path)
                    continue

                print("正在转换：", in_path)

                # 打开 PDF（Word 会自动进行“PDF 重排”）
                # ReadOnly=True 避免修改原文件；ConfirmConversions=False 不弹转换对话框
                doc = word.Documents.Open(in_path, ReadOnly=True)

                # FileFormat=16 表示 wdFormatDocumentDefault，一般就是 .docx
                doc.SaveAs(out_path, FileFormat=16)
                doc.Close()
    finally:
        # 关闭 Word 进程
        word.Quit()

if __name__ == "__main__":
    convert_all_pdfs_to_docx(INPUT_DIR, OUTPUT_DIR)
    print("PDF 转 Word 全部完成！")
