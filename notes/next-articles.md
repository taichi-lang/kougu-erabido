# 次に書く記事（企画部隊 → b5-kougu-routine）

作成: 2026-10-07 01:12〜 `kougu-article-planner` ／ 対象: 2026-10-07 02:15 の執筆分
**3本。3本とも失敗・トラブル系。** 比較表の候補は、メーカー公式ページを実際に開いて仕様表を取得できたものだけを載せた。

> 前回分（刈払機の草絡まり／ヘッジトリマー／バンドソー）は公開済み（`32ceccd`、112本）。
> 今回は**「吹く・吸う」の空気系3本**（ブロワ／充電式クリーナー／集じん機）。既存112本に空気系のトラブル記事は無い。
> 高圧洗浄機（汚れが落ちない）も候補にしたが、**検索上位がケルヒャー公式のFAQ（メーカー本体）だったので着手ゲートで捨てた。**

## 全体の注意（3本共通）

- **マキタの製品ページ（`/product/detail/?model=...`）は仕様表を JavaScript で描画する。** WebFetch では数値が取れない。
  ブラウザで1ページ開き、同一オリジンの `iframe` で他機種を読み込み、約8秒待って**最後の `table`** の innerText を読む（2026-10-07 もこの方法で取得）。
  **型番の末尾に注意**：`CL184FD`・`MUB185D`・`VC866DZ` は表が出ない。公式の型番は `CL184D`・`VC866D`（末尾Zなし）
- **HiKOKI は `curl -A "Mozilla/5.0"` で仕様表まで取れる。** 製品URLの一覧は
  ブロワ `/products/powertools/li-ion-blower/li-ion-blower.html`・`/products/gardening/blower/blower.html`、
  クリーナ／集じん機 `/products/powertools/li-ion-cleaner/li-ion-cleaner.html` から拾える
- **「公式ページに記載が無い」は「その機能が無い」ではない。** 本文では「公式の製品ページには記載が見当たらない」と書く
- **体験を装わない。** 原因の説明は一般論＋公式の公表値まで
- **測定条件がメーカーで違う数値を横並びで優劣にしない。** 風量は「ノズルなし」(HiKOKI) と条件明記なし(マキタ)、吸込仕事率は「EN62841-1準拠」(マキタ一部) と注記なし(HiKOKI) が混在する。表には注記欄を付け、本文で条件差を明示する
- 価格は未調査（両社とも希望小売価格は出ているが実売ではない）。`price_note` に調査時点を書く通常手順で
- 着手ゲートの検索上位は WebSearch（米国経由）で見ただけ。**Search Console は未登録で、表示回数は見ていない**

---

## 1. ブロワで落ち葉が飛ばない

- **slug 案**: `blower-ochiba-tobanai`
- **タイトル案**: ブロワで落ち葉が飛ばない原因｜風量・風速で選ぶ充電式（26字）
- **型**: 失敗・トラブル系。買ったブロワで濡れ落ち葉や溜まった葉が動かない、という場面で検索される。
  原因（風量不足＝動かせる葉の量／風速不足＝湿った葉・張り付いた葉／ノズルの形・長さ／バッテリ残量で回転数が落ちる）を切り分けて、
  **風量 m³/min と風速 m/s の両方**を見て選ぶ流れにできる。
- **軸**: **最大風量（0.7〜19.8 m³/min）と最大風速（52〜122 m/s）が機種で逆転する。**
  手持ちの小型機（RA18DA・RB36DB）は風速は高いが風量が1 m³/min前後、園芸用の大型機（MUB001G・RB36DC）は風量13〜20 m³/minで風速は50〜70 m/s。
  「風速が高い＝落ち葉が飛ぶ」ではないことが公表値で示せる。
- **着手ゲート**: 上位は my-best・sakidori・gizmodo 等の媒体。メーカー公式・省庁の1位は見当たらない。
- **既存記事との重複**: `blower-nozzle-tekigou`（ノズルの適合＝規格辞典）とは意図が違う。トラブル系は無い。
- **比較表の候補（6件。表は4〜5件に絞ってよい）**

| メーカー | 型番 | 公式で確認できた仕様 | 公式ページ |
| --- | --- | --- | --- |
| マキタ | MUB184D | 18V／風量13 m³/min／風速 最大52・平均43 m/s（ノズル付）／6.0Ahで約50分〜12分／2.8kg（バッテリ含む）／ブラシレス | https://www.makita.co.jp/product/detail/?model=MUB184D |
| マキタ | MUB362D | 36V(18V×2)／風量13.4〜6.9 m³/min（ダイヤル6〜1）／風速 最大65〜33・平均54〜27 m/s／6.0Ah ダイヤル6 約12分・ダイヤル1 約1時間24分／4.1kg | https://www.makita.co.jp/product/detail/?model=MUB362D |
| マキタ | MUB001G | 40Vmax／風量16（ブースト）・13.5（クルーズ最大）m³/min／風速 最大64・53 m/s／2.5Ahで約1時間〜7分／3.1kg（バッテリ・ノズル含む）／IPX4／エンジン換算28mL | https://www.makita.co.jp/product/detail/?model=MUB001G |
| HiKOKI | RB36DC | マルチボルト／風量 ノーマル0〜15.0・ターボ19.8 m³/min／風速 最大62.6（ノーマル）・71.5（ターボ）m/s／36V-4.0Ahで約15分／3.7kg（蓄電池装着時）／ブラシレス | https://www.hikoki-powertools.jp/products/gardening/blower/rb36dc/rb36dc.html |
| HiKOKI | RB18DC | 18V(14.4V)／風量（ノズルなし）0〜3.5 m³/min／風速（ノズル取付時）最大95・平均78 m/s／1.8kg／直流モーター（ブラシ付） | https://www.hikoki-powertools.jp/products/powertools/li-ion-blower/rb18dc/rb18dc.html |
| HiKOKI | RB36DB | マルチボルト／最大風量（ノズルなし）1.2 m³/min／風速（ノズル組(S)）最大102・平均83 m/s／1.4kg／ブラシレス | https://www.hikoki-powertools.jp/products/powertools/li-ion-blower/rb36db/rb36db.html |

- 予備: HiKOKI RA18DA（エアダスタ。最大風量0.70 m³/min・風速最大122 m/s・最高圧力18kPa・1.2kg）https://www.hikoki-powertools.jp/products/powertools/li-ion-blower/ra18da/ra18da.html
  — 「風速だけ高い機種」の例として本文で触れるのに向く。HiKOKI RB18DC(BCL)（園芸向け。風量0〜3.5・風速最大78 m/s・1.6kg）https://www.hikoki-powertools.jp/products/gardening/blower/rb18dc_bcl/rb18dc_bcl.html
- **公式で取れなかった項目・注意**
  - **風量の測定条件がメーカーで違う**：HiKOKI は「ノズルなし」と明記、マキタは条件の記載なし（風速は「ノズル付」と明記）。横並びの優劣にしない
  - **マキタ MUB185D・MUB183D は製品ページは存在するが仕様表が取得できなかった**（2026-10-07）。載せない
  - 「落ち葉を動かすのに必要な風量・風速」の数値を示す一次情報は取れていない。**数値を出典なしで書かない**
  - 連続運転時間は両社とも参考値で条件が違う。横並びで比べない
- **内部リンク先**: `blower-nozzle-tekigou` ／ `battery-ah-erabikata` ／ `makita-vs-hikoki` ／ `juudenki-taiou-battery` ／ `karibarai-kusa-karamaru` ／ `hedge-trimmer-kirenai` ／ `dendou-kougu-bousui`

---

## 2. 充電式クリーナーが吸わない・吸引力が落ちた

- **slug 案**: `cordless-cleaner-suwanai`
- **タイトル案**: 充電式クリーナーが吸わない原因｜吸込仕事率で比較（24字）
- **型**: 失敗・トラブル系。マキタ等の充電式クリーナーで「買ったときより吸わない」「細かい粉を吸わない」場面で検索される。
  原因（紙パック・ダストバッグの目詰まり／フィルタの目詰まり／サイクロンのダストケース満杯／モード設定が「標準」のまま／バッテリ残量で出力が落ちる／10.8Vと18Vの出力差）を切り分けて、
  **吸込仕事率 W と集じん方式（紙パック／サイクロン一体）**で選び直す流れにできる。
- **軸**: **吸込仕事率（パワフル時 32〜155 W）が電圧と方式で3〜5倍違う。** 同じ18Vでも紙パック式 CL184D（38W）とサイクロン一体式 CL286FD（100W）で差があり、
  HiKOKI R36DB（155W）が最大。標準モードは5〜65Wで、**モード設定だけで吸込仕事率が数倍変わる**ことが公表値で示せる。
- **着手ゲート**: 上位は lifehacker・gizmodo・my-best 等の媒体。メーカー公式の1位は見当たらない。
- **既存記事との重複**: 充電式クリーナーの記事は無い（`shujinki-*` は集じん機）。
- **比較表の候補（7件。表は4〜5件に絞ってよい）**

| メーカー | 型番 | 公式で確認できた仕様 | 公式ページ |
| --- | --- | --- | --- |
| マキタ | CL107FD | 10.8V(スライド)／紙パック式／吸込仕事率 パワフル32・強20・標準5 W／集じん容量 ダストバッグ500・紙パック330 mL／パワフル約10分／1.1kg | https://www.makita.co.jp/product/detail/?model=CL107FD |
| マキタ | CL184D | 18V／紙パック式／吸込仕事率 パワフル38・強23・標準5 W／500/330 mL／パワフル約20分／2.0kg（バッテリ含む）／ハンディ形 | https://www.makita.co.jp/product/detail/?model=CL184D |
| マキタ | CL282FD | 18V／紙パック式／吸込仕事率 パワフル60・強42・標準15 W／500/330 mL／パワフル約15分／1.5kg／ブラシレス | https://www.makita.co.jp/product/detail/?model=CL282FD |
| マキタ | CL286FD | 18V／サイクロン一体式／吸込仕事率 パワフル100・強60・標準35・エコ15 W／集じん容量250 mL／パワフル約8分／1.7kg／ブラシレス | https://www.makita.co.jp/product/detail/?model=CL286FD |
| マキタ | CL003G | 40Vmax／サイクロン一体式／吸込仕事率 パワフル100・強60・標準35・エコ15 W（EN62841-1準拠、サイクロンアタッチメント無しで測定）／250 mL／パワフル約16分／1.8kg | https://www.makita.co.jp/product/detail/?model=CL003G |
| HiKOKI | R18DC | 18V・マルチボルト／吸込仕事率 強40・標準30・弱16 W（R18DC(S) 1段サイクロンは 25/18/10 W）／集じん容量560 mL（(S)は400）／5.0Ahで強約40分／1.7kg | https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/r18dc/r18dc.html |
| HiKOKI | R36DB | マルチボルト／吸込仕事率 強155・標準65・弱35 W（R36DB(SC) 2段サイクロンは 90/50/25 W）／560 mL／1.6kg／充電約25分 | https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/r36db/r36db.html |

- 予備: HiKOKI R12DC（10.8V・吸込仕事率 強30/標準18/弱10 W・560 mL・1.1kg）https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/r12dc/r12dc.html
  HiKOKI R18DPA（紙パック式・強33/標準26/弱17 W・400 mL・1.8kg）https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/r18dpa/r18dpa.html
- **公式で取れなかった項目・注意**
  - **吸込仕事率の測定条件**：マキタは「各標準設定バッテリの満充電相当」（CL286FD/CL003G は EN62841-1準拠と明記）。HiKOKI は注記が取れていない。**同じ条件とは言い切らない**
  - **ゴミが溜まったときの吸込仕事率の低下量**を示す公表値は両社とも無い。「満杯で落ちる」は一般論として書き、数値は書かない
  - フィルタの目詰まりと吸引力の関係を数値で示す一次情報は無い
  - マキタ CL185FD は表が取得できなかった。載せない
  - 本文で「吸わない」の対処（紙パック交換・フィルタ水洗い）を書くときは**各社の取扱説明書に従う旨**を添え、手順を断定しない
- **内部リンク先**: `battery-ah-erabikata` ／ `makita-10v-vs-18v` ／ `makita-vs-hikoki` ／ `hijunsei-battery` ／ `hontai-nomi-hyouki` ／ `shujinki-kamipack`

---

## 3. 集じん機の吸引力が落ちる・粉じんを吸わない

- **slug 案**: `shujinki-kyuinryoku-ochiru`
- **タイトル案**: 集じん機の吸引力が落ちる原因｜風量と真空度で比較（24字）
- **型**: 失敗・トラブル系。丸ノコ・サンダーに接続した集じん機が「最初は吸ったのに吸わなくなった」「細かい粉が舞う」場面で検索される。
  原因（フィルタ・紙パックの目詰まり＝風量が落ちる／ホース径と長さの不一致／乾湿両用機で水を吸った後のフィルタ／乾式専用機で湿った粉を吸う／工具側のダストノズル径の不適合）を切り分けて、
  **最大風量 m³/min・最大真空度 kPa・吸込仕事率 W・集じん方式（乾式専用／乾湿両用／粉じん専用）**で選び直す流れにできる。
- **軸**: **同じメーカーの同じ電圧帯でも「風量」と「真空度」の組み合わせが用途で違う。**
  マキタ 18V×2 の3機種は VC865D（乾湿・風量2.1・真空度11kPa）／VC866D（乾式専用・1.9・10）／VC867D（粉じん専用・1.3・11）と風量が違い、
  40Vmax の VC001G/VC003G（風量3.2・真空度23kPa・吸込仕事率310W）と HiKOKI RP3608DA/RP3615DA（風量3.5・真空度20.1kPa・300W）が上位。
  「電動工具接続用」は風量より真空度・フィルタ構成で選ぶ、という整理が公表値でできる。
- **着手ゲート**: 「集じん機 吸引力 落ちる」の上位は Panasonic・三菱電機の**家庭用掃除機**のサポートページ（メーカー本体）。
  ただし工具用集じん機の記事ではなく、検索意図が違う。**タイトルと冒頭で「電動工具用の集じん機」であることを明示**して、家庭用掃除機の意図と分ける。
  工具用に限った「集じん機 吸わない」のメーカー公式1位は確認できていない（未測定）。
- **既存記事との重複**: `shujinki-hose-kei`（ホース径の規格）・`shujinki-kamipack`（紙パックの適合）・`shujinki-rendou-consent`（連動コンセントの比較）とは意図が違う。
  トラブル系の集じん機記事は無い。この3本には**本文中からリンクを張る**（原因の切り分けでそれぞれ参照先になる）。
- **比較表の候補（7件。表は4〜5件に絞ってよい）**

| メーカー | 型番 | 公式で確認できた仕様 | 公式ページ |
| --- | --- | --- | --- |
| マキタ | VC750D | 18V／乾湿両用／吸込仕事率 強50・標準25 W／最大風量 強1.6・標準1.3 m³/min／最大真空度 強6.7・標準4.2 kPa／集じん容量7.5L・吸水4.5L／BL1860Bで強約36分／4.1kg | https://www.makita.co.jp/product/detail/?model=VC750D |
| マキタ | VC865D | 36V(18V×2)／乾湿両用／吸込仕事率 吸込力5:105・1:35 W／最大風量2.1 m³/min／最大真空度11 kPa／8L・吸水6L／7.6kg（BL1860B×2） | https://www.makita.co.jp/product/detail/?model=VC865D |
| マキタ | VC866D | 36V(18V×2)／乾式専用（紙パック7L）／吸込仕事率 90・30 W／最大風量1.9 m³/min／最大真空度10 kPa／ホースφ32mm×1.7m／7.6kg | https://www.makita.co.jp/product/detail/?model=VC866D |
| マキタ | VC867D | 36V(18V×2)／粉じん専用（電動工具接続専用）／吸込仕事率 75・25 W／最大風量1.3 m³/min／最大真空度11 kPa／ホース内径28mm×5.0m／パウダフィルタ・プレフィルタ・ダンパ付属／無線連動／8.3kg | https://www.makita.co.jp/product/detail/?model=VC867D |
| マキタ | VC001G | 40Vmax／乾湿両用／吸込仕事率 最大310・最小30 W／最大風量3.2 m³/min／最大真空度23 kPa／8L・吸水6L／ホース内径38mm×2.5m／BL4050F×2で最大約28分／10kg／IP54 | https://www.makita.co.jp/product/detail/?model=VC001G |
| HiKOKI | RP3608DA(L) | マルチボルト×2／乾湿両用／布フィルタ／吸込仕事率300W／最大風量3.5 m³/min／最大真空度20.1 kPa／8L（吸水6L）／ホースø38mm×1.5m／9.3kg／マキタ工具接続用D38アダプタ付属 | https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/rp3608da_l/rp3608da_l.html |
| HiKOKI | R3640DA | マルチボルト／吸込仕事率 ターボ80・標準33・eco11 W／最大風量 3.9・3.1・2.1 m³/min／最大真空度 8.4・4.7・2.0 kPa／18L／無線連動あり／ホース内径ø28×5m／3.0kg | https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/r3640da/r3640da.html |

- 予備: マキタ VC003G（VC001G の15L版。風量3.2・真空度23kPa・310W・10.3kg）https://www.makita.co.jp/product/detail/?model=VC003G
  HiKOKI RP3615DA（RP3608DA の15L版。風量3.5・真空度20.1kPa・300W・9.6kg）https://www.hikoki-powertools.jp/products/powertools/li-ion-cleaner/rp3615da/rp3615da.html
- **公式で取れなかった項目・注意**
  - **フィルタが目詰まりしたときの風量・真空度の低下量**を示す公表値は両社とも無い。「目詰まりで風量が落ちる」は一般論として書き、数値を書かない
  - マキタの「吸込力5／1」と HiKOKI の「ターボ／標準／eco」はモード名で、条件が同じかは公式に記載が無い。横並びで優劣にしない
  - **HiKOKI R3640DA は吸込仕事率80Wでも風量3.9 m³/minと、マキタ VC001G（310W・3.2）より風量が大きい。** 吸込仕事率＝吸引力ではないことを本文で説明する（真空度は8.4kPaと低い）
  - 粉じん専用・乾式専用機で水や湿った粉を吸った場合の扱いは**各社の取扱説明書に従う旨**を添え、断定しない
  - マキタ VC866DZ / VC867DZ（末尾Z）では製品ページの表が出ない。**公式型番は VC866D / VC867D** で開く
- **内部リンク先**: `shujinki-hose-kei` ／ `shujinki-kamipack` ／ `shujinki-rendou-consent` ／ `marunoko-dust-nozzle` ／ `sander-kezuriato-nokoru` ／ `battery-ah-erabikata` ／ `makita-vs-hikoki`

---

## 捨てた案（記録）

| 案 | 捨てた理由 |
| --- | --- |
| 高圧洗浄機で汚れが落ちない（吐出圧力・吐出水量で比較） | 「高圧洗浄機 汚れが落ちない」「水圧が弱い」とも**検索1位がケルヒャー公式FAQ**（メーカー本体）→ 着手ゲート。HiKOKI AW18DBL（吐出圧力0.5〜2.0MPa・吐出水量0.5〜1.2L/min https://www.hikoki-powertools.jp/products/gardening/washer/p-aw14dbl/aw14dbl.html ）とケルヒャー K2 サイレント（ https://www.kaercher.com/jp/home-garden/pressure-washers/k-2-silent-um-16009200.html ）の公式ページは実在を確認した。別の切り口（「充電式と100Vの違い」など比較系）なら再検討できる |
