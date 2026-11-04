# my-images

个人图床仓库，用于存放图片并生成可外链的直链 URL。

## 目录结构

```
my-images/
└── images/          # 所有图片文件
```

## 链接格式

公开仓库的图片有几种常用直链写法（把 `OWNER` 换成 GitHub 用户名）：

| 用途 | URL 格式 |
| --- | --- |
| 原始文件（Markdown / HTML 引用） | `https://raw.githubusercontent.com/OWNER/my-images/main/images/文件名.jpg` |
| 网页查看 | `https://github.com/OWNER/my-images/blob/main/images/文件名.jpg` |
| **国内直达（推荐）** | `https://testingcf.jsdelivr.net/gh/OWNER/my-images@main/images/文件名.jpg` |
| 备用代理 | `https://ghproxy.net/https://raw.githubusercontent.com/OWNER/my-images/main/images/文件名.jpg` |

实测说明（2026-11-04）：

- `raw.githubusercontent.com` 国内多数网络环境可通，但速度不稳、偶发超时。
- `cdn.jsdelivr.net` 在国内会被 301 跳回 `raw.githubusercontent.com`，等于没有加速，因此不推荐。
- `testingcf.jsdelivr.net` 直接返回 200（0 次跳转），是目前最稳的国内通道。
- `cdn.statically.io` 当前不可访问。

## 注意

- 文件名建议使用**英文、数字、连字符**，避免空格和中文。GitHub 会自动把空格和中文编码成 `%20` 和 UTF-8 百分号序列，链接虽然能用但很难看、也容易在部分平台失效。
- 图片单文件建议不超过 25 MB（GitHub 网页上传限制），仓库总大小建议不超过 1 GB。
