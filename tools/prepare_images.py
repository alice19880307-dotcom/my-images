#!/usr/bin/env python3
"""收图 + 规整文件名。

规则：只处理「URL 不友好」的文件名（含中文、空格、括号、#/&/% 等），
纯英文数字的干净文件名原样保留，不动它。

相比 GitHub 的默认行为：空格会变成 %20、中文会变成一长串 %E6%B7%B7… 百分号编码，
链接能用但难看，部分平台（公众号、部分 CMS）还会截断。

用法：
    python tools/prepare_images.py                    # 扫描工作目录根 + images/，收图并规整
    python tools/prepare_images.py "C:/a/b.png"       # 指定文件
    python tools/prepare_images.py --dir "C:/某目录"   # 指定目录（不递归）
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "images"
WORKSPACE = ROOT.parent
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"}

# 只要出现这些字符，就认为文件名在 URL 里不好看
UNSAFE = re.compile(r"[^A-Za-z0-9._-]")


def is_safe(name: str) -> bool:
    return not UNSAFE.search(name)


def slugify(stem: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def unique(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix, n = target.stem, target.suffix, 2
    while True:
        cand = target.with_name(f"{stem}-{n}{suffix}")
        if not cand.exists():
            return cand
        n += 1


def collect_images() -> list[Path]:
    """工作目录根 + images/ 下的所有图片。"""
    found = []
    for d in (WORKSPACE, DEST):
        if d.is_dir():
            found += [
                p for p in d.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_EXT
            ]
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="图片文件路径")
    ap.add_argument("--dir", help="批量导入某个目录下的所有图片（不递归）")
    args = ap.parse_args()

    if args.files or args.dir:
        sources = [Path(f) for f in args.files]
        if args.dir:
            sources += [p for p in sorted(Path(args.dir).iterdir()) if p.is_file()]
        sources = [p for p in sources if p.is_file() and p.suffix.lower() in IMAGE_EXT]
    else:
        sources = collect_images()

    if not sources:
        print("没有找到可导入的图片。", file=sys.stderr)
        return 1

    DEST.mkdir(parents=True, exist_ok=True)
    moved, renamed, kept = [], [], []

    for src in sources:
        src = src.resolve()
        in_dest = src.parent == DEST.resolve()

        if not in_dest:
            # 从外部收进来
            if is_safe(src.name):
                target = unique(DEST / src.name)
                shutil.move(str(src), str(target))
                moved.append((src.name, target.name))
            else:
                target = unique(DEST / f"{slugify(src.stem) or 'image'}{src.suffix.lower()}")
                shutil.move(str(src), str(target))
                moved.append((src.name, target.name))
            continue

        # 已在 images/ 里，只看名字要不要规整
        if is_safe(src.name):
            kept.append(src.name)
        else:
            target = unique(DEST / f"{slugify(src.stem) or 'image'}{src.suffix.lower()}")
            src.rename(target)
            renamed.append((src.name, target.name))

    if moved:
        print("已收进 images/：")
        for old, new in moved:
            print(f"  {old}" + ("" if old == new else f"  →  {new}"))
    if renamed:
        print("已规整文件名：")
        for old, new in renamed:
            print(f"  {old}  →  {new}")
    if kept:
        print("文件名已规范，保持原样：")
        for name in kept:
            print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
