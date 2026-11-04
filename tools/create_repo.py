#!/usr/bin/env python3
"""用 GitHub REST API 创建空仓库，并把 origin 设置为干净的 HTTPS 地址。

需要环境变量 GH_TOKEN（Personal Access Token，勾选 repo 权限）。
    GH_TOKEN=xxx python tools/create_repo.py --repo my-images --public

脚本不会把 token 写进任何文件，也不会写进 .git/config。
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"


def call(token: str, method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "workbuddy-image-host",
        },
    )
    body = urllib.request.urlopen(req).read()
    return json.loads(body) if body else {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--private", action="store_true", help="默认创建公开仓库")
    ap.add_argument("--description", default="个人图床：存放图片并生成外链 URL")
    args = ap.parse_args()

    token = os.environ.get("GH_TOKEN")
    if not token:
        print("错误：缺少环境变量 GH_TOKEN。", file=sys.stderr)
        return 1

    me = call(token, "GET", "/user")
    owner = me["login"]

    try:
        repo = call(
            token,
            "POST",
            "/user/repos",
            {
                "name": args.repo,
                "description": args.description,
                "private": args.private,
                "has_issues": False,
                "has_wiki": False,
                "auto_init": False,
            },
        )
        print(f"已创建仓库：{repo['html_url']}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        if e.code == 422 and "already exists" in detail:
            print(f"仓库 {owner}/{args.repo} 已存在，直接复用。")
            repo = call(token, "GET", f"/repos/{owner}/{args.repo}")
        else:
            print(f"创建失败 HTTP {e.code}: {detail}", file=sys.stderr)
            return 1

    remote = f"https://github.com/{owner}/{args.repo}.git"
    subprocess.run(["git", "remote", "remove", "origin"], cwd=ROOT, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", remote], cwd=ROOT, check=True)
    print(f"origin -> {remote}")
    print(f"OWNER={owner}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
