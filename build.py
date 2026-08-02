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


def shop_block(ads, meta):
    """記事の末尾に、その記事のテーマに合う商品検索への導線を出す。

    ads.json の rakuten.affiliate_url_template に実際のアフィリエイトURLの雛形が
    入っているときだけ描画する。雛形が無ければ何も出さない(偽リンクを作らない)。
    雛形は {q} をURLエンコード済みの検索語で置換する形式。
    記事側は META の shop_keyword で検索語を指定する。
    """
    import urllib.parse
    kw = meta.get("shop_keyword", "")
    if not kw:
        return ""
    q = urllib.parse.quote(kw)

    buttons = []
    for key, label in (("rakuten", "楽天市場"), ("amazon", "Amazon")):
        tmpl = (ads.get(key) or {}).get("affiliate_url_template", "")
        if tmpl:
            # href属性に入れるので、クエリ区切りの & をHTMLエスケープする
            url = tmpl.replace("{q}", q).replace("&", "&amp;")
            buttons.append(
                f'<a class="shop-cta shop-{key}" href="{url}" '
                f'rel="sponsored nofollow" target="_blank">{label}で「{kw}」を見る</a>')
    if not buttons:
        return ""

    return f"""<aside class="shop-block">
  <span class="pr-tag">PR</span>
  <p class="shop-lead">この記事で扱った{meta.get('shop_label', kw)}を実際に探す場合はこちらから。
  価格と在庫は変動するため、最新の情報は販売サイトでご確認ください。</p>
  <div class="shop-ctas">{''.join(buttons)}</div>
  <p class="shop-note">上記リンクは広告(アフィリエイト)です。リンク経由での購入により当サイトに紹介料が発生する場合がありますが、
  掲載内容の選定・評価は紹介料の有無とは無関係に、メーカー公式スペックに基づいて行っています。</p>
</aside>"""


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
<meta name="google-site-verification" content="cnmJh_5HFVfXrRwlZqi1CpgyxR8yQioO23UlJTq89aA">
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
    <nav><a href="/about">運営者情報</a> ／ <a href="/advertise">広告掲載のご案内</a> ／ <a href="/privacy">プライバシーポリシー</a></nav>
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
        full = (pr_slot(ads, "article_top")
                + f"<article><h1>{meta['title']}</h1>" + body + shop_block(ads, meta)
                + "</article>")
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

    # 広告掲載のご案内(メディアガイド)
    ad_count = len(articles)
    adguide = f"""<article><h1>広告掲載のご案内</h1>
<p>工具えらび堂は、電動工具の<strong>規格と公式スペックに基づく選定情報</strong>を扱う専門メディアです。
読者は「これから工具を買う人」に限定されており、購買前の比較検討段階で接触できる点を評価いただいています。</p>

<div class="point-box"><span class="pb-title">掲載をご検討の企業様へ — 先にお伝えすること</span>
<ul>
<li>当メディアは<strong>2026年7月に開設したばかり</strong>で、掲載枠はすべて先行導入の位置づけです(現在の記事数: {ad_count}本)</li>
<li>アクセス実績は計測開始後に開示します。<strong>実績値が出るまでは試験導入価格でのご相談を承ります</strong></li>
<li>広告出稿の有無によって、記事内の製品評価・掲載順を変更することはありません(下記「編集の独立性」)</li>
</ul></div>

<h2>掲載メニュー</h2>
<div class="table-wrap">
<table class="product-table">
<thead><tr><th>メニュー</th><th>内容</th><th>掲載位置</th><th>料金(税別)</th></tr></thead>
<tbody>
<tr>
  <td class="td-maker">タイアップ記事</td>
  <td class="td-spec">貴社製品を軸にした選定ガイド記事を編集部が制作。規格・公式スペックに基づく解説形式で、読者に「なぜその製品が選択肢に入るか」を伝えます。制作費込み・恒久掲載</td>
  <td>独立記事(PR表記)</td>
  <td class="td-price">150,000円<span class="price-note">1本・制作込み</span></td>
</tr>
<tr>
  <td class="td-maker">トップPR枠</td>
  <td class="td-spec">サイト最上部のPR枠にテキストリンクを掲載。全訪問者の視界に入る位置です</td>
  <td>トップページ最上部</td>
  <td class="td-price">50,000円<span class="price-note">月額</span></td>
</tr>
<tr>
  <td class="td-maker">記事内PR枠</td>
  <td class="td-spec">比較記事・基礎知識記事の本文上部にテキストリンクを掲載。カテゴリ指定可</td>
  <td>各記事の上部</td>
  <td class="td-price">30,000円<span class="price-note">月額</span></td>
</tr>
<tr>
  <td class="td-maker">比較表への製品掲載</td>
  <td class="td-spec">既存の比較記事へ貴社製品を追加。<strong>編集部の判断で掲載可否を決定するため、この枠は無償です</strong>(公式スペックが公開されていることが条件)</td>
  <td>該当記事の比較表</td>
  <td class="td-price">無償<span class="price-note">編集判断</span></td>
</tr>
</tbody>
</table>
</div>
<p class="price-disclaimer">※ 期間・本数・複数枠のお申し込みについては別途ご相談ください。開設初期のため、実績値をご覧いただいてからのご判断でも構いません。</p>

<h2>編集の独立性について</h2>
<p>当メディアの価値は、読者が「広告ではなく判断材料」として信頼できる点にあります。したがって次を運営方針として明示します。</p>
<ul>
<li>広告出稿の有無で、記事内の製品評価・比較表の並び順・推奨内容を変更しません</li>
<li>タイアップ記事には必ず「PR」表記を行い、通常記事と区別します</li>
<li>実機を使用した体験を装う表現は、タイアップ記事でも用いません(<a href="/about">編集方針</a>)</li>
<li>公表スペックと異なる内容、根拠を示せない優位性の記載はお受けできません</li>
</ul>

<h2>お問い合わせ</h2>
<table class="plain-table">
<tr><th>担当</th><td>工具えらび堂 編集部(運営者: 中村太一)</td></tr>
<tr><th>メール</th><td>nks.taichi@gmail.com</td></tr>
<tr><th>ご連絡いただきたい事項</th><td>貴社名・ご担当者名・ご検討中のメニュー・対象製品</td></tr>
</table>
<p>掲載可否は、当サイトの読者にとって有益かどうかを基準に編集部で判断させていただきます。</p>
</article>"""
    with open(os.path.join(DIST, "advertise.html"), "w", encoding="utf-8") as f:
        f.write(page(f"広告掲載のご案内 | {SITE_NAME}",
                     "工具えらび堂の広告掲載メニュー・料金・編集方針のご案内。タイアップ記事、PR枠の掲載を承ります。",
                     adguide, path_label="広告掲載のご案内"))

    # プライバシーポリシー
    privacy = """<article><h1>プライバシーポリシー</h1>
<p>当サイトは、お問い合わせ対応以外で個人情報を取得しません。</p>
<p>アクセス解析ツール・広告配信サービスを導入した場合、それらはCookieを使用して匿名のトラフィックデータを収集することがあります。導入時は本ページに追記します。</p>
<p>制定日: 2026年7月28日</p></article>"""
    with open(os.path.join(DIST, "privacy.html"), "w", encoding="utf-8") as f:
        f.write(page(f"プライバシーポリシー | {SITE_NAME}", "工具えらび堂のプライバシーポリシー", privacy, path_label="プライバシーポリシー"))

    # sitemap.xml(Search Consoleに登録した瞬間に効くよう、記事の更新日を反映する)
    static_pages = [("", None), ("about", None), ("advertise", None), ("privacy", None)]
    today = date.today().isoformat()
    urls = []
    for path, _ in static_pages:
        loc = f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n  </url>")
    for a in sorted(articles, key=lambda x: x["date"], reverse=True):
        urls.append(
            f'  <url>\n    <loc>{SITE_URL}/{a["slug"]}</loc>\n'
            f'    <lastmod>{a["date"]}</lastmod>\n  </url>'
        )
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # robots.txt(全ページ許可 + サイトマップの所在を明示)
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"built {len(articles)} articles -> dist/ (sitemap: {len(urls)} URLs)")


if __name__ == "__main__":
    build()
