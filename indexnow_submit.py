"""IndexNow へのURL送信。

なぜ要るか:
  当サイトは被リンクが実質0本で、クローラの入口がサイトマップの送信しかない。
  IndexNow は「更新したURLを検索エンジン側に能動的に通知する」公開プロトコルで、
  アカウント登録もオーナー操作も不要。所有確認は https://<ドメイン>/<キー>.txt の
  設置だけで行われる。B5が自力で増やせる、数少ない発見経路のひとつ。

使い方:
  python build.py && vercel deploy --prod   # 先にキーファイルを本番へ出す
  python indexnow_submit.py                 # そのあとで送信する

  キーファイルが本番に無い状態で送ると 403 が返る。順序を守ること。
"""
import json
import re
import sys
import urllib.request

from build import INDEXNOW_KEY, SITE_URL

HOST = SITE_URL.split("//", 1)[1]
ENDPOINT = "https://api.indexnow.org/indexnow"


def load_urls():
    """本番のsitemap.xmlから送信対象URLを読む(手元のdistではなく本番を見る)。"""
    with urllib.request.urlopen(SITE_URL + "/sitemap.xml", timeout=30) as r:
        xml = r.read().decode("utf-8")
    return re.findall(r"<loc>(.*?)</loc>", xml)


def check_key_file():
    """本番にキーファイルが出ているかを先に確かめる。"""
    url = f"{SITE_URL}/{INDEXNOW_KEY}.txt"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read().decode("utf-8").strip()
    except Exception as e:  # noqa: BLE001
        print(f"NG キーファイルを取得できません: {url} ({e})")
        return False
    if body != INDEXNOW_KEY:
        print(f"NG キーファイルの中身が一致しません: {url}")
        return False
    print(f"OK キーファイルを本番で確認: {url}")
    return True


def submit(urls):
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read().decode("utf-8", "replace")


def main():
    if not check_key_file():
        return 1
    urls = load_urls()
    print(f"送信対象: {len(urls)} URL")
    status, body = submit(urls)
    print(f"HTTP {status} {body!r}")
    # 200 = 受理 / 202 = 受理(キー確認は保留)
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
