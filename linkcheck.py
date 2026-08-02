# -*- coding: utf-8 -*-
"""dist/ 内の内部リンク切れを機械チェックする。

出力: 参照されている内部リンクの総数と、実体のないリンクの一覧。
"""
import os
import re

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
HREF = re.compile(r'href="(/[^"#?]*)"')

pages = set()
for f in os.listdir(DIST):
    if f.endswith(".html"):
        slug = f[:-5]
        pages.add("/" + ("" if slug == "index" else slug))
pages.add("/")

total = 0
broken = []
for f in sorted(os.listdir(DIST)):
    if not f.endswith(".html"):
        continue
    with open(os.path.join(DIST, f), encoding="utf-8") as fh:
        html = fh.read()
    for m in HREF.finditer(html):
        target = m.group(1)
        if target.startswith("/assets/"):
            continue
        total += 1
        if target not in pages:
            broken.append((f, target))

print("internal links checked:", total)
print("broken:", len(broken))
for f, t in broken:
    print("  BROKEN", f, "->", t)

# 各記事への被リンク数
inbound = {}
for f in sorted(os.listdir(DIST)):
    if not f.endswith(".html"):
        continue
    with open(os.path.join(DIST, f), encoding="utf-8") as fh:
        html = fh.read()
    for m in HREF.finditer(html):
        t = m.group(1)
        if t.startswith("/assets/"):
            continue
        inbound.setdefault(t, set()).add(f)
for slug in ["/impact-wrench-vs-driver", "/grinder-toishi-size", "/hontai-nomi-hyouki"]:
    srcs = sorted(inbound.get(slug, set()) - {slug.lstrip("/") + ".html"})
    print(slug, "inbound:", len(srcs), srcs)
