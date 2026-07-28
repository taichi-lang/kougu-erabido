"""工具えらび堂 — 静的サイトジェネレーター

articles/*.html(先頭に <!--META {json} META--> ブロック)を読み、
共通テンプレートで包んで dist/ に出力する。

設計方針:
- 商品比較テーブルはMETAのproductsから生成し、価格/メーカー/スペックで並び替え可能
- PR枠は ads.json に実在の広告がある場合のみ描画(空なら何も出さない=偽リンクを作らない)
- 商品リンクも links が空なら描画しない(アフィリエイト提携後に実URLを差し込む)
"""
import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES = os.path.join(ROOT, "articles")
DIST = os.path.join(ROOT, "dist")
ASSETS = os.path.join(ROOT, "assets")

SITE_NAME = "工具えらび堂"
SITE_DESC = "規格と公式スペックで選ぶ、誠実な工具選定ガイド"
SITE_URL = "https://kougu-erabido.vercel.app"

META_RE = re.compile(r"<!--META\s*(\{.*?\})\s*META-->", re.DOTALL)


def load_ads():
    path = os.path.join(ROOT, "ads.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def pr_slot(ads, slot):
    """実在の広告がある場合のみPR枠を描画する。"""
    items = ads.get(slot, [])
    if not items:
        return ""
    inner = "".join(
        f'<a class="pr-item" href="{a["url"]}" rel="sponsored nofollow" target="_blank">{a["label"]}</a>'
        for a in items if a.get("url")
    )
    if not inner:
        return ""
    return f'<aside class="pr-slot"><span class="pr-tag">PR</span>{inner}</aside>'


def product_table(products):
    if not products:
        return ""
    rows = []
    for p in products:
        links = "".join(
            f'<a href="{l["url"]}" rel="sponsored nofollow" target="_blank" class="shop-link">{l["label"]}</a>'
            for l in p.get("links", []) if l.get("url")
        ) or '<span class="muted">リンク準備中</span>'
        rows.append(f"""      <tr data-price="{p['price']}" data-maker="{p['maker']}" data-feature="{p['feature']}">
        <td class="td-maker">{p['maker']}</td>
        <td class="td-model">{p['model']}</td>
        <td><span class="feature-tag">{p['feature']}</span></td>
        <td class="td-spec">{p['spec']}</td>
        <td class="td-price">{p['price']:,}円<span class="price-note">{p.get('price_note','')}</span></td>
        <td>{links}</td>
      </tr>""")
    return f"""<div class="sort-bar" role="group" aria-label="並び替え">
  <span class="sort-label">並び替え:</span>
  <button class="sort-btn" data-key="price">価格</button>
  <button class="sort-btn" data-key="feature">スペック</button>
  <button class="sort-btn" data-key="maker">メーカー</button>
</div>
<div class="table-wrap">
  <table class="product-table" id="product-table">
    <thead><tr><th>メーカー</th><th>型番</th><th>スペック分類</th><th>詳細スペック</th><th>実勢価格目安</th><th>販売店</th></tr></thead>
    <tbody>
{chr(10).join(rows)}
    </tbody>
  </table>
</div>
<p class="price-disclaimer">※ 価格は編集部調査による目安(記事更新日時点)です。実際の販売価格は店舗・時期により変動します。スペックは各メーカー公式サイトの公表値に基づきます。</p>"""


def page(title, description, body, path_label=None, is_article=False, meta=None):
    breadcrumb = ""
    if path_label:
        breadcrumb = f'<nav class="breadcrumb"><a href="/">ホーム</a> &rsaquo; <span>{path_label}</span></nav>'
    date_line = ""
    if is_article and meta:
        date_line = f'<p class="article-meta">更新日: {meta["date"]}{" ／ カテゴリ: " + meta.get("category", "") if meta.get("category") else ""}</p>'
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/">{SITE_NAME}</a>
    <p class="site-desc">{SITE_DESC}</p>
  </div>
</header>
<main class="wrap">
{breadcrumb}
{date_line}
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>当サイトは、規格・メーカー公式スペック等の一次情報に基づいて工具の選び方を解説するサイトです。実機の使用体験を装ったレビューは掲載していません。</p>
    <p>当サイトはアフィリエイトプログラムに参加しており、記事内のリンクを経由した購入により報酬を得ることがあります。広告リンクには「PR」表記を行っています。</p>
    <nav><a href="/about">運営者情報</a> ／ <a href="/privacy">プライバシーポリシー</a></nav>
    <p>&copy; 2026 {SITE_NAME}</p>
  </div>
</footer>
<script src="/assets/sort.js"></script>
</body>
</html>"""


def build():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(ASSETS, os.path.join(DIST, "assets"))
    ads = load_ads()

    articles = []
    for fname in sorted(os.listdir(ARTICLES)):
        if not fname.endswith(".html"):
            continue
        with open(os.path.join(ARTICLES, fname), encoding="utf-8") as f:
            raw = f.read()
        m = META_RE.search(raw)
        if not m:
            raise ValueError(f"METAブロックがありません: {fname}")
        meta = json.loads(m.group(1))
        body = raw[m.end():].strip()
        body = body.replace("{{PRODUCT_TABLE}}", product_table(meta.get("products", [])))
        full = pr_slot(ads, "article_top") + f"<article><h1>{meta['title']}</h1>" + body + "</article>"
        html = page(f"{meta['title']} | {SITE_NAME}", meta["description"], full,
                    path_label=meta["title"], is_article=True, meta=meta)
        with open(os.path.join(DIST, meta["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(html)
        articles.append(meta)

    # トップページ(カテゴリ別記事一覧)
    cats = {}
    for a in articles:
        cats.setdefault(a.get("category", "その他"), []).append(a)
    sections = []
    for cat, items in cats.items():
        lis = "".join(
            f'<li><a href="/{a["slug"]}">{a["title"]}</a><span class="li-desc">{a["description"]}</span></li>'
            for a in sorted(items, key=lambda x: x["date"], reverse=True))
        sections.append(f'<section class="cat-block"><h2>{cat}</h2><ul class="article-list">{lis}</ul></section>')
    top_body = pr_slot(ads, "home_top") + f"""
<div class="site-intro">
  <p>{SITE_NAME}は、「使ってみた」ではなく<strong>規格とメーカー公式スペック</strong>で工具を選ぶためのガイドです。
  電圧・トルク・チャック径といった数字の意味から、用途別の選定手順までを、一次情報に基づいて解説します。</p>
</div>
{''.join(sections)}"""
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(f"{SITE_NAME} — {SITE_DESC}", SITE_DESC + "。電動工具の選び方を規格と公式スペックから解説。", top_body))

    # 運営者情報
    about = """<article><h1>運営者情報</h1>
<table class="plain-table">
<tr><th>サイト名</th><td>工具えらび堂</td></tr>
<tr><th>運営者</th><td>中村太一</td></tr>
<tr><th>お問い合わせ</th><td>nks.taichi@gmail.com</td></tr>
</table>
<h2>編集方針</h2>
<p>当サイトの記事は、メーカー公式サイトの公表スペック・JIS等の規格・公的機関の公開情報という一次情報に基づいて作成しています。
実機を使用した体験を装う表現(「使ってみた」「実際に握った感想」等)は用いません。体験に基づかない評価を体験談のように書くことは、読者に対する裏切りだと考えているためです。</p>
<p>記事内の価格は調査時点の目安であり、購入時は必ず販売店の表示価格をご確認ください。</p>
<h2>広告について</h2>
<p>当サイトはアフィリエイトプログラムに参加しています。広告・アフィリエイトリンクには「PR」表記を行い、報酬の有無が記事の評価に影響しない運営を行います。</p></article>"""
    with open(os.path.join(DIST, "about.html"), "w", encoding="utf-8") as f:
        f.write(page(f"運営者情報 | {SITE_NAME}", "工具えらび堂の運営者情報と編集方針", about, path_label="運営者情報"))

    # プライバシーポリシー
    privacy = """<article><h1>プライバシーポリシー</h1>
<p>当サイトは、お問い合わせ対応以外で個人情報を取得しません。</p>
<p>アクセス解析ツール・広告配信サービスを導入した場合、それらはCookieを使用して匿名のトラフィックデータを収集することがあります。導入時は本ページに追記します。</p>
<p>制定日: 2026年7月28日</p></article>"""
    with open(os.path.join(DIST, "privacy.html"), "w", encoding="utf-8") as f:
        f.write(page(f"プライバシーポリシー | {SITE_NAME}", "工具えらび堂のプライバシーポリシー", privacy, path_label="プライバシーポリシー"))

    print(f"built {len(articles)} articles -> dist/")


if __name__ == "__main__":
    build()
