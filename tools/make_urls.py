#!/usr/bin/env python3
"""根据仓库的 remote 地址，为 images/ 下的所有图片生成 GitHub 直链。

用法：
    python tools/make_urls.py            # 生成 urls.md
    python tools/make_urls.py --print    # 只打印到终端
"""

import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def parse_remote(url: str) -> tuple[str, str]:
    """从 https / ssh 形式的 remote 里取出 owner 和 repo。"""
    url = url.strip()
    if url.startswith("git@"):
        path = url.split(":", 1)[1]
    else:
        path = url.split("github.com/", 1)[1]
    path = path.removesuffix(".git").strip("/")
    owner, repo = path.split("/")[:2]
    return owner, repo


def main() -> int:
    try:
        remote = git("remote", "get-url", "origin")
    except subprocess.CalledProcessError:
        print("错误：还没有配置 origin 远程地址。", file=sys.stderr)
        return 1

    owner, repo = parse_remote(remote)
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "main"

    files = sorted(
        p for p in (ROOT / "images").rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXT
    )
    if not files:
        print("images/ 下没有找到图片。", file=sys.stderr)
        return 1

    rows = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        encoded = "/".join(quote(seg) for seg in rel.split("/"))
        rows.append(
            {
                "name": f.name,
                "raw": f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{encoded}",
                "blob": f"https://github.com/{owner}/{repo}/blob/{branch}/{encoded}",
                "jsdelivr": f"https://cdn.jsdelivr.net/gh/{owner}/{repo}@{branch}/{encoded}",
                "jsdelivr_cf": f"https://testingcf.jsdelivr.net/gh/{owner}/{repo}@{branch}/{encoded}",
                "ghproxy": f"https://ghproxy.net/https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{encoded}",
            }
        )

    lines = [
        f"# {owner}/{repo} 图片链接",
        "",
        f"分支：`{branch}`　图片数量：{len(rows)}",
        "",
        "## 一览表",
        "",
        "| 文件名 | 原始直链（raw） | 国内直达（testingcf） |",
        "| --- | --- | --- |",
    ]
    for r in rows:
        lines.append(f"| {r['name']} | {r['raw']} | {r['jsdelivr_cf']} |")

    lines += [
        "",
        "## 备用通道（cdn.jsdelivr.net 在国内常会 301 跳回 raw，故不列为主用）",
        "",
    ]
    for r in rows:
        lines += [
            f"**{r['name']}**",
            "",
            f"- cdn.jsdelivr.net：{r['jsdelivr']}",
            f"- ghproxy.net：{r['ghproxy']}",
            "",
        ]

    lines += ["", "## Markdown 引用片段", ""]
    for r in rows:
        lines += [f"### {r['name']}", "", "```markdown", f"![{r['name']}]({r['raw']})", "```", ""]
        lines += ["国内直达版：", "", "```markdown", f"![{r['name']}]({r['jsdelivr_cf']})", "```", ""]

    lines += [
        "## HTML 引用片段",
        "",
        "```html",
        *[
            f'<img src="{r["jsdelivr_cf"]}" alt="{r["name"]}" />'
            for r in rows
        ],
        "```",
        "",
    ]

    out = "\n".join(lines)
    if "--print" in sys.argv:
        print(out)
    else:
        (ROOT / "urls.md").write_text(out, encoding="utf-8")
        print(f"已生成 urls.md，共 {len(rows)} 条链接（owner={owner}, repo={repo}, branch={branch}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
