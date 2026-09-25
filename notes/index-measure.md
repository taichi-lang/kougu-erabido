# 索引の測り方（2026-09-25 確定・毎回この手順で測る）

**22日間「索引は測れていない」と書き続けていた。道具を変えたら測れた。**
以後、索引件数はこの手順で測り、`ROUTINE_B5.md` と `KPI.md` に1行残す。

## 結論だけ先に

| 経路 | 使えるか | 実測（2026-09-25） |
|---|---|---|
| **DuckDuckGo `html` エンドポイント + ブラウザ** | ✅ **これを使う** | **40 URL**（sitemap 92 のうち） |
| Google `site:` （ブラウザ） | ❌ | bot 判定ページ。**CAPTCHA は解かない** |
| Bing `site:` （ブラウザ） | ❌ | 無関係な結果（baidu/zhihu）に落ちる。件数表示「約58件」は**この数字を採らない** |
| `curl` で各検索エンジン | ❌ | DuckDuckGo **HTTP 202** / Mojeek **JavaScript 必須の challenge** |

⚠ **`curl` では1つも測れない。ブラウザ必須。** 「スクリプト1本で毎日自動」にはできない。

## 手順（3操作・費用0円・ログイン0件）

1. ブラウザを開く
   `https://html.duckduckgo.com/html/?q=site%3Akougu-erabido.vercel.app`
2. ページ内で下の JS を実行する（同一オリジンなので `fetch` が通る）
3. **ブラウザを閉じる**（●全社-25：1回ごとに必ず閉じる）

```js
const urls=new Set(); let pages=0, stopped='cap';
const grab=d=>[...d.querySelectorAll('.result__url')].forEach(e=>urls.add(e.textContent.trim()));
let doc=document;
while(pages<40){
  grab(doc); pages++;
  const f=[...doc.querySelectorAll('form')].find(f=>f.querySelector('.btn--alt'));
  if(!f){stopped='no-next-form';break;}
  const r=await fetch('https://html.duckduckgo.com/html/',{method:'POST',body:new URLSearchParams(new FormData(f))});
  if(!r.ok){stopped='http-'+r.status;break;}
  doc=new DOMParser().parseFromString(await r.text(),'text/html');
  if(!doc.querySelector('.result__url')){stopped='empty-page';break;}
}
JSON.stringify({pages,stopped,distinct:urls.size,urls:[...urls].sort()},null,1)
```

## 読み方（ここを間違えると数字が嘘になる）

- **DuckDuckGo は「次へ」を無限に出す。**1ページ目だけでは 10件しか出ない
- **重複が非常に多い。**`distinct` を見る。12ページで37 → 40ページで40 と**収束する**
- `stopped:"cap"` で返ってきた値は **下限**である。「40件」ではなく「**40件（下限・収束）**」と書く
- **DuckDuckGo は Google ではない。**この数字で Google の索引を語らない。
  **Google は本日も測れていない**（bot 判定・CAPTCHA は解かない）

## ⚠ 過去の「索引1件」との関係

`ROUTINE_B5.md` の「索引は1件（トップのみ）」は **Google `site:` の読みである**。
同ファイルは当時すでに「`site:` は結果を省略することがある」と注意を書いていた。
**本日の40件は、その注意が当たっていたことを示す。ただし Google 側の1件を否定する材料ではない。**
**別の索引の、別の数字である。混ぜて書かない。**

## 測ったときに残すもの

`distinct` の値 / `pages` と `stopped` / sitemap の URL 数 / **増減の理由**（記事本数ではなく）

### ⚠ URL 一覧を必ず保存する（2026-09-26 追加）

**09-25 は件数（40）だけを記録し、URL 一覧を捨てた。**
翌日 45 に増えたが、**増えた5件がどれかを特定できなかった。**
→ 以後、JS の戻り値の `urls` を **`notes/index-log/<YYYY-MM-DD>_ddg.txt`（1行1URL）** に保存する。

突き合わせは次の1本で再現できる（カテゴリ・追加時期・文字数・被リンク数の出現率と、出ていない記事の一覧）:

```bash
python index_gap.py notes/index-log/2026-09-26_ddg.txt
```

**これまでに分かったことは `index-gap.md`。**
