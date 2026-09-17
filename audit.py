"""工具えらび堂 — 記事の監査。

週次ルーティーンの「どの記事を直すか」を選ぶための道具。
判断はしない。事実だけを並べる。

使い方:
    python audit.py            # 全体サマリ + 改修候補
    python audit.py --all      # 全記事を1行ずつ
    python audit.py --gate     # 編集方針違反だけを見る(違反があれば終了コード1)

見ているもの:
    比較表     … METAの products。アフィリエイトの主戦場。無い記事が改修候補
    両モール   … products の各行に楽天とAmazonの両方が入っているか
    内部リンク … 本文中の自サイトへのリンク数(末尾リストではなく本文中に置く方針)
    タイトル   … 32文字以内か(前半にキーワードを置く方針)
    説明文     … 120文字前後か
    体験表現   … 「使ってみた」等。この事業では書かない(編集方針の芯)
    alt        … 画像のalt。空にしない(直上の見出しの文言を入れる方針)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES = os.path.join(ROOT, "articles")
META_RE = re.compile(r"<!--META\s*(\{.*?\})\s*META-->", re.DOTALL)

TITLE_MAX = 32
DESC_MIN, DESC_MAX = 90, 130

# 実機レビューを装う表現。この事業では使わない(README・about に明記している方針)。
# ただし「使ってみた印象は書きません」「使ってみても分からない」のような打ち消しは違反ではない。
# 検出したら直後を見て、打ち消していれば除外する。
EXPERIENCE_PAT = re.compile(
    r"使ってみた|使ってみて|実際に使っ|握った感想|試してみた|愛用して|買ってみた|レビューして")
NEGATION_PAT = re.compile(r"ません|しない|ない|分から|書きま|避け")

# 記事のテーマと結びついていない検索語。末尾の商品導線がテーマとずれると、
# アクセスがあってもクリックされない(報酬の3因数のうちCTRが落ちる)。
GENERIC_KW = {"電動工具", "工具", "ドリルドライバー", "インパクトドライバー",
              "インパクトレンチ", "レーザー墨出し器", "コーススレッド"}


def load():
    rows = []
    for fname in sorted(os.listdir(ARTICLES)):
        if not fname.endswith(".html"):
            continue
        raw = open(os.path.join(ARTICLES, fname), encoding="utf-8").read()
        m = META_RE.search(raw)
        if not m:
            print(f"!! METAブロックがありません: {fname}")
            continue
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        rows.append(audit_one(fname, meta, body))
    return rows


def audit_one(fname, meta, body):
    products = meta.get("products") or []
    both = sum(1 for p in products
               if {l.get("label") for l in p.get("links", []) if l.get("url")}
               >= {"楽天市場", "Amazon"})
    exp = []
    for m in EXPERIENCE_PAT.finditer(body):
        tail = body[m.end():m.end() + 14]
        if not NEGATION_PAT.search(tail):
            exp.append(m.group(0))
    alts = re.findall(r"<img[^>]*>", body)
    empty_alt = sum(1 for t in alts if 'alt=""' in t or "alt=" not in t)
    return {
        "file": fname,
        "slug": meta.get("slug", ""),
        "title": meta.get("title", ""),
        "title_len": len(meta.get("title", "")),
        "desc_len": len(meta.get("description", "")),
        "category": meta.get("category", ""),
        "date": meta.get("date", ""),
        "products": len(products),
        "both_mall": both,
        "has_table": "{{PRODUCT_TABLE}}" in body,
        "shop_kw": meta.get("shop_keyword", ""),
        "inlinks": len(re.findall(r'href="/[a-z0-9-]+"', body)),
        "chars": len(re.sub(r"<[^>]+>", "", body)),
        "images": len(alts),
        "empty_alt": empty_alt,
        "experience": exp,
        "generic_kw": meta.get("shop_keyword", "") in GENERIC_KW,
    }


def gate(rows):
    """編集方針に反しているものだけを出す。ここが空であることが健全な状態。"""
    bad = False
    for r in rows:
        if r["experience"]:
            bad = True
            print(f"[体験表現] {r['slug']}: {'/'.join(sorted(set(r['experience'])))}")
        if r["empty_alt"]:
            bad = True
            print(f"[空のalt]  {r['slug']}: {r['empty_alt']}件")
        if r["products"] and not r["has_table"]:
            bad = True
            print(f"[表が未配置] {r['slug']}: productsが{r['products']}件あるが本文に"
                  "{{PRODUCT_TABLE}}が無い")
        if r["generic_kw"]:
            bad = True
            print(f"[汎用kw]   {r['slug']}: shop_keyword が「{r['shop_kw']}」。"
                  "記事のテーマまで絞らないと末尾導線がクリックされない")
        if not r["shop_kw"]:
            bad = True
            print(f"[導線なし] {r['slug']}: shop_keyword が空(末尾の商品導線が出ない)")
    if not bad:
        print("違反なし。")
    return bad


def inbound(rows):
    """比較表を持つ記事(=換金する記事)に、本文中リンクがどれだけ集まっているか。

    順位を上げたい記事へは、同カテゴリの既存記事の本文中からリンクを集める。
    記事末尾の関連記事リストではない。
    """
    counts = {r["slug"]: 0 for r in rows}
    for r in rows:
        raw = open(os.path.join(ARTICLES, r["file"]), encoding="utf-8").read()
        for slug in re.findall(r'href="/([a-z0-9-]+)"', raw):
            if slug in counts and slug != r["slug"]:
                counts[slug] += 1
    print("\n--- 比較表を持つ記事への本文中リンク ---")
    print("※ 換金する記事に読者を集める。少ないなら同カテゴリの記事の本文中から張る。")
    for r in rows:
        if r["has_table"]:
            print(f"  {r['slug']:<34} 被リンク{counts[r['slug']]:>3}本  "
                  f"商品{r['products']}件")


def summary(rows):
    n = len(rows)
    with_table = [r for r in rows if r["has_table"]]
    print(f"記事数: {n}")
    print(f"比較表あり: {len(with_table)}本  /  なし: {n - len(with_table)}本"
          f"  ← アフィリエイトの伸びしろはここ")
    print(f"末尾の商品導線(shop_keyword)あり: {sum(1 for r in rows if r['shop_kw'])}本")
    print(f"タイトル{TITLE_MAX}文字超: {sum(1 for r in rows if r['title_len'] > TITLE_MAX)}本")
    print(f"説明文が{DESC_MIN}〜{DESC_MAX}文字の外: "
          f"{sum(1 for r in rows if not DESC_MIN <= r['desc_len'] <= DESC_MAX)}本")
    print(f"画像が1枚も無い記事: {sum(1 for r in rows if r['images'] == 0)}本")
    print(f"本文中の内部リンクが5本未満: {sum(1 for r in rows if r['inlinks'] < 5)}本")

    cats = {}
    for r in rows:
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    print("\nカテゴリ内訳(購入に近い順に厚くする):")
    for c, v in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {c}: {v}本")

    print("\n--- 比較表が無い記事(改修候補) ---")
    print("※ 並び順はここでは決められない。Search Console の表示回数上位から選ぶこと。")
    for r in rows:
        if not r["has_table"]:
            print(f"  {r['slug']:<34} {r['category']:<6} 内部リンク{r['inlinks']:>3}  "
                  f"{r['chars']:>6}字  kw={r['shop_kw']}")


def all_rows(rows):
    print(f"{'slug':<34}{'表':>3}{'商品':>5}{'両':>3}{'内部':>5}{'題':>4}{'説明':>5}{'字数':>7}  カテゴリ")
    for r in rows:
        print(f"{r['slug']:<34}{'○' if r['has_table'] else '−':>3}{r['products']:>5}"
              f"{r['both_mall']:>3}{r['inlinks']:>5}{r['title_len']:>4}{r['desc_len']:>5}"
              f"{r['chars']:>7}  {r['category']}")


if __name__ == "__main__":
    rows = load()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--gate":
        sys.exit(1 if gate(rows) else 0)
    elif arg == "--all":
        all_rows(rows)
    else:
        summary(rows)
        inbound(rows)
        print("\n--- 編集方針ゲート ---")
        gate(rows)
