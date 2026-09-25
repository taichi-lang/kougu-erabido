#!/usr/bin/env python3
"""索引に出ている記事と出ていない記事を、記事側の属性で突き合わせる。

使い方:
    python index_gap.py notes/index-log/2026-09-26_ddg.txt

引数は `notes/index-measure.md` の手順で保存した URL 一覧(1行1URL・ホスト名込み)。
出力は「カテゴリ別」「追加日別」「文字数別」「被リンク数別」の出現率と、出ていない記事の一覧。

⚠ ここで扱うのは DuckDuckGo の索引であって Google ではない。
  `notes/index-measure.md` の「読み方」を先に読むこと。
"""
import collections
import json
import os
import re
import subprocess
import sys

ART_DIR = "articles"


def load_articles():
    """articles/*.html の META と本文を読む。"""
    arts, bodies = {}, {}
    for fn in sorted(os.listdir(ART_DIR)):
        if not fn.endswith(".html"):
            continue
        text = open(os.path.join(ART_DIR, fn), encoding="utf-8").read()
        m = re.search(r"<!--META\s*(\{.*?\})\s*META-->", text, re.S)
        if not m:
            continue
        meta = json.loads(m.group(1))
        arts[meta["slug"]] = meta
        bodies[meta["slug"]] = text
    return arts, bodies


def inbound_links(arts, bodies):
    """記事から記事への被リンク数(自分自身は数えない)。"""
    c = collections.Counter()
    for slug, text in bodies.items():
        for target in set(re.findall(r'href="/([a-z0-9\-]+)"', text)):
            if target != slug and target in arts:
                c[target] += 1
    return c


def first_commit_date(slug):
    """記事が最初にコミットされた日。記事 META の date とはずれることがある。"""
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%ad", "--date=short",
         "--", f"{ART_DIR}/{slug}.html"],
        capture_output=True, text=True).stdout.strip()
    return out.split("\n")[-1] if out else "?"


def rate(rows, key_fn, label):
    d = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        k = key_fn(r)
        d[k][0] += 1
        d[k][1] += r["inIndex"]
    print(f"\n--- {label} ---")
    for k in sorted(d, key=str):
        n, y = d[k]
        print(f"  {str(k):16s} 記事{n:3d} 出{y:3d} ({y * 100 // n:3d}%)")


def main(path):
    present = set()
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        present.add(line.split("/", 1)[1] if "/" in line else "")

    arts, bodies = load_articles()
    inb = inbound_links(arts, bodies)
    rows = []
    for slug, meta in arts.items():
        rows.append({
            "slug": slug,
            "inIndex": slug in present,
            "cat": meta.get("category", ""),
            "added": first_commit_date(slug),
            "chars": len(re.sub("<[^>]+>", "", bodies[slug])),
            "links": inb[slug],
        })

    hit = sum(r["inIndex"] for r in rows)
    print(f"記事 {len(rows)}本 / 索引に出ている {hit}本 / 出ていない {len(rows) - hit}本")
    rate(rows, lambda r: r["cat"], "カテゴリ別")
    rate(rows, lambda r: "早期(〜08/05)" if r["added"] <= "2026-08-05" else "後期(08/06〜)", "追加時期別")
    rate(rows, lambda r: f"{r['chars'] // 1500 * 1500}字〜", "文字数別")
    rate(rows, lambda r: f"被リンク{r['links'] // 5 * 5}〜", "被リンク数別")

    print("\n--- 出ていない記事(追加日順) ---")
    for r in sorted([r for r in rows if not r["inIndex"]], key=lambda r: r["added"]):
        print(f"  {r['added']} {r['cat']:6s} {r['chars']:6d}字 被{r['links']:2d} {r['slug']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
