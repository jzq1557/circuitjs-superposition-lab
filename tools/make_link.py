#!/usr/bin/env python3
"""把 CircuitJS 电路文本转成 eetree 上可直接打开的链接。

用法:
    python tools/make_link.py 电路文件/工况3-共同激励.txt
    python tools/make_link.py 电路文本.txt            # 含多段时只取第一段
    python tools/make_link.py a.txt --open            # 生成后顺手用浏览器打开

原理: 网站电路页是标准 CircuitJS1，查询参数会被转发给内嵌的 circuitjs-real.html，
      其中 ?cct= 接收 URL 编码后的电路文本（内容就是 .txt 里的那几十行）。
"""
import argparse
import sys
import urllib.parse
import webbrowser
from pathlib import Path

BASE = "https://www.eetree.cn/circuitjs/circuitjs.html?cct="


def read_circuit(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    # 允许文件里有多段（用空行分隔）：取第一段，即第一个 "$" 到下一个空行
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines) if ln.startswith("$")), None)
    if start is None:
        raise SystemExit("没有找到以 $ 开头的电路文件头，确认这是 CircuitJS 电路文本")
    block = []
    for ln in lines[start:]:
        if ln.strip() == "":
            break
        block.append(ln)
    return "\n".join(block) + "\n"


def build_url(text: str) -> str:
    return BASE + urllib.parse.quote(text, safe="")


def main() -> None:
    ap = argparse.ArgumentParser(description="CircuitJS 电路文本 → eetree 可点击链接")
    ap.add_argument("file", type=Path, help="电路文本文件（.txt）")
    ap.add_argument("--open", action="store_true", help="生成后用默认浏览器打开")
    args = ap.parse_args()

    if not args.file.is_file():
        raise SystemExit(f"找不到文件: {args.file}")

    text = read_circuit(args.file)
    url = build_url(text)
    print(url)
    print(f"\n# {args.file.name}: {len(text.splitlines())} 行, 链接长度 {len(url)}", file=sys.stderr)
    if args.open:
        webbrowser.open(url)


if __name__ == "__main__":
    main()
