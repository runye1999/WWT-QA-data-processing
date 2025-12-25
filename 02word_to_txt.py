"""
批量将 Word(.doc/.docx) 转为 .txt
- 递归处理目录，保持相对目录结构
- 并行处理（WORKERS）
- 跳过已存在（OVERWRITE=False），或强制覆盖（OVERWRITE=True）
- 失败不中断
- 不插入任何分隔符/占位符；图片内容会被忽略
"""

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from docx import Document#解析word内容
from docx.text.paragraph import Paragraph

# ========== 在这里直接配置路径与参数 ==========
# 单文件：把 INPUT_PATH 设为某个 .doc/.docx 文件；目录：设为文件夹
INPUT_PATH  = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\word"
# 对于单文件：OUTPUT_PATH 可为目标 .txt 文件路径；为空则默认与源同名同目录
# 对于目录：OUTPUT_PATH 为输出根目录；为空则默认在输入目录下创建 txt_out/
OUTPUT_PATH = r"F:\PhD-item-experment\answer\knowledge\knowledgecode\Code\dataset_processing\wordtxt"

# 并行线程数（0 表示自动：min(32, CPU*2)）
WORKERS     = 0
# 是否覆盖已存在的目标文件（默认 False：跳过）
OVERWRITE   = False

# ================== 通用工具函数 ==================

def _norm(s: str) -> str:
    """归一化文本，去除回车与首尾空白。"""
    return (s or "").replace("\r", "").strip()

def _paragraph_to_text(p) -> str:
    """合并段落内 runs 的纯文本。，拼接纯文本"""
    parts = []
    for r in p.runs:#遍历段落的所有runs（格式化的文本片段）
        if r.text:#如果run有文本内容，就添加到parts列表中
            parts.append(r.text)
    return "".join(parts).strip()#用空字符串连接所有片段，并去除首尾空白后返回。

def _table_to_tsv(table) -> str: 
    """
    表格输出为纯文本：将表格每行拼成 \t 分隔的字符串，再把各行用 \n 连接
    """
    lines = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            # 合并单元格内所有段落的文本（已归一化），中间用空格
            txt = " ".join(_norm(p.text) for p in cell.paragraphs if _norm(p.text))
            cells.append(txt)
        lines.append("\t".join(cells).rstrip())
    return "\n".join(lines) + "\n" if lines else ""

def docx_to_txt(docx_path: Path, txt_path: Path):
    doc = Document(str(docx_path))#使用 docx 库解析 docx 文件，获取 Document 对象。
    out = []#用于存储转换后的文本内容。

    def iter_block_items(parent):#内部生成器遍历 docx 的段落/表格下的段落或表格。 每个段落或表格都生成一个 Paragraph 或 Table 对象。
        from docx.document import Document as _DocxDocument
        from docx.text.paragraph import Paragraph
        from docx.table import _Cell, Table

        if isinstance(parent, _DocxDocument):#如果当前父节点是整个文档对象，就取它底层的 body 元素，里面包含顶层段落和表格的 XML。
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):#若父节点是表格单元格 _Cell，取其 _tc（table cell）元素，这里面同样可以嵌段落或表格。
            parent_elm = parent._tc
        else:
            if hasattr(parent, "element") and hasattr(parent.element, "body"):
                parent_elm = parent.element.body
            elif hasattr(parent, "_tc"):
                parent_elm = parent._tc
            else:
                raise ValueError(f"Unsupported parent: {type(parent)}")

        for child in parent_elm.iterchildren():#遍历父节点底层 XML 的直接子元素。
            if child.tag.endswith('}p'):#标签以 }p 结尾表示段落元素，包装成 Paragraph 返回。
                yield Paragraph(child, parent)
            elif child.tag.endswith('}tbl'):
                yield Table(child, parent)#标签以 }tbl 结尾表示表格元素，包装成 Table 返回

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            txt = _paragraph_to_text(block) #段落调用 _paragraph_to_text
            if txt: #如果段落有文本内容，就添加到out列表中
                out.append(txt)
        else:
            tsv = _table_to_tsv(block) #表格调用 _table_to_tsv
            if _norm(tsv):
                out.append(tsv.rstrip("\n"))  # 统一在最后统一加换行

    # 写出文件（不添加额外分隔符
    #将非空块写入目标 txt，每块之间换行，末尾补换行，并确保输出目录存在。
    #确保输出文件的父目录存在：parents=True 会递归创建所有缺失的父目录；exist_ok=True 表示目录已存在时不报错。
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    #以 UTF-8 编码打开目标文件用于写入，with 确保写入完成后自动关闭
    with open(txt_path, "w", encoding="utf-8") as f:
        # 段落/表格块之间用换行分隔，末尾补一个换行
        f.write("\n".join([s for s in out if _norm(s)]).strip() + "\n")
    return txt_path #返回目标文件路径

# ================== .doc -> .docx 转换与批处理 ==================

def soffice_convert_to_docx(input_doc: Path) -> Path:
    """用 LibreOffice 把 .doc 转为 .docx；返回新路径"""
    if shutil.which("soffice") is None:
        raise RuntimeError("未检测到 soffice（LibreOffice）。请安装 LibreOffice 或在 Windows 上使用 Word。")
    out_dir = input_doc.parent / "_converted_docx"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = f'soffice --headless --convert-to docx "{input_doc}" --outdir "{out_dir}"'
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return out_dir / (input_doc.stem + ".docx")

def convert_one(src: Path, dst: Path) -> Path:
    ext = src.suffix.lower()#获取源文件的后缀，并转换为小写。
    if ext == ".docx":
        return docx_to_txt(src, dst)#如果后缀是 .docx，直接调用 docx_to_txt 函数进行转换。
    elif ext == ".doc":
        docx_path = soffice_convert_to_docx(src)#如果后缀是 .doc，先调用 soffice_convert_to_docx 函数将 .doc 转换为 .docx，再调用 docx_to_txt 函数进行转换。
        return docx_to_txt(docx_path, dst)
    else:
        raise ValueError(f"只支持 .docx/.doc：{src}")#如果后缀既不是 .docx 也不是 .doc，抛出 ValueError 异常。

# ---------------- 批量处理核心 ----------------

def collect_inputs(input_path: Path) -> list[Path]:
    """收集要处理的 .doc/.docx 文件列表（递归）。"""
    if input_path.is_file():#如果输入路径本身是个文件，检查它的后缀是否是.docx 或 .doc，符合则返回它的列表，不符合返回空
        return [input_path] if input_path.suffix.lower() in {".docx", ".doc"} else []
    files = []
    for f in input_path.rglob("*"):#递归遍历输入路径下的所有文件，包括子目录
        if f.is_file() and f.suffix.lower() in {".docx", ".doc"}:
            files.append(f)#把符合条件的文件路径加入列表。
    return files#返回所有符合条件的列表

def map_dst(src: Path, in_root: Path, out_root: Path | None, ext: str = ".txt") -> Path:
    """将 src 映射到 out_root 下的目标路径，保持相对目录结构。"""
    if in_root.is_file():
        if out_root and out_root.suffix.lower() == ext:
            return out_root
        base = out_root if (out_root and out_root.exists() and out_root.is_dir()) else in_root.parent
        return base / (in_root.stem + ext)
    rel = src.relative_to(in_root).with_suffix(ext)#src 相对于 in_root 的相对路径。在相对路径上把扩展名改为目标后缀（默认 .txt）
    return (out_root or (in_root / "txt_out")) / rel
    #先使用用户配置的 out_root；如果没指定，则默认在输入目录下新建 txt_out 作为输出根目录，利用 Path 的 / 运算符拼接路径，得到完整的目标文件路径。

def _safe_convert(src: Path, dst: Path):
    convert_one(src, dst)#调用 convert_one 函数，传入源文件路径和目标文件路径，进行实际的转换操作。

def batch_convert(input_path: Path,
                  output_path: Path | None,
                  workers: int = 0,
                  overwrite: bool = False):
    in_path = input_path
    out_root = output_path

    files = collect_inputs(in_path)#包含所有doc或docx文件的路径列表
    if not files:
        raise FileNotFoundError(f"未找到可处理文件：{input_path}")

    tasks = []
    for src in files:
        dst = map_dst(src, in_path, out_root)#得到每个文件的目标文件.txt路径
        if not overwrite and dst.exists():#如果没有开启 OVERWRITE 且目标 txt 已存在，就不再重复生成。
            tasks.append(("skip", src, dst, "exists"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)#确保目标文件所在的目录已经创建（包括多级新目录），避免写文件时报错。
            tasks.append(("run", src, dst, ""))#把任务标记为 run，表示需要转换

    total = len(tasks)#任务总数
    will_run = sum(1 for t in tasks if t[0] == "run")#需要转换的任务数
    skipped = total - will_run#跳过的任务数

    print(f"发现 {total} 个文档，计划转换 {will_run} 个，跳过已存在 {skipped} 个。")

    results = []#用于记录每个任务的执行结果
    #根据用户配置或自动计算最大线程数，避免过多线程导致系统负担过大。
    max_workers = workers if workers and workers > 0 else min(32, (os.cpu_count() or 4) * 2)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=max_workers) as ex:#创建线程池
        futures = {}#用于存储每个任务的 future 对象，方便后续获取结果。
        for tag, src, dst, note in tasks:#tag：标签 src：源路径 dst：目标txt路径 note：exists说明txt件已存在或"空字符串"目标文件还未转换
            if tag == "skip":
                results.append({"src": str(src), "dst": str(dst), "status": "skipped", "error": note})
            else:
                fut = ex.submit(_safe_convert, src, dst)#对需要执行的任务，将 _safe_convert(src, dst) 提交到线程池
                futures[fut] = (src, dst)#并在 futures 中保存 Future 与对应的源/目标路径。

        for fut in as_completed(futures):
            src, dst = futures[fut]
            try:
                fut.result()
                results.append({"src": str(src), "dst": str(dst), "status": "ok", "error": ""})
            except Exception as e:
                results.append({"src": str(src), "dst": str(dst), "status": "fail", "error": str(e)})

    ok = sum(1 for r in results if r["status"] == "ok")
    fail = sum(1 for r in results if r["status"] == "fail")
    skip = sum(1 for r in results if r["status"] == "skipped")
    print(f"完成：成功 {ok}，失败 {fail}，跳过 {skip}。")

# ---------------- 入口 ----------------

if __name__ == "__main__":
    in_path = Path(INPUT_PATH)
    out_path = Path(OUTPUT_PATH) if OUTPUT_PATH else None
    # 单文件输入且未提供输出：默认与源同名同目录 .txt
    if in_path.is_file() and out_path is None:
        out_path = in_path.with_suffix(".txt")

    batch_convert(
        input_path=in_path,
        output_path=out_path,
        workers=WORKERS,
        overwrite=OVERWRITE,
    )
