# 起票前ドラフトと既存Issueの整理

2026-11-23時点の承認前原稿。新規候補は以下の3件。各英語タイトルと本文を、そのまま対象repoの `gh issue create --title` と `--body-file` に渡せる。実行は別段階。既存Issueの残件は追記案として区別し、同じ機能を再起票しない。

## V1　看板案件の横断受け入れ（P1・L）

Repository: `kajisho5/Velisa`

Title: **Accept a Japanese talk-to-short edit through one approved revision and verified delivery**

```markdown
Track the integration evidence across #167 (review), #168 (duration), #169 (resume) and #170 (spoken selects). Their feature work stays in those issues. The deliverable here is one reproducible production receipt on macOS.

- [ ] Record source rights, source timebase, local ASR/model, tool versions and a two-speaker excerpt with one usable audio channel.
- [ ] From spoken-word candidates, preview a 60-second selection. Record source spans and approval before semantic cuts. Show the crop at the start, middle and end of moving shots. Apply the review and duration policies proposed in PRs #164, #165, #166 and #171.
- [ ] Replace one quote. Save both recipe revisions, the affected stages and a new preview. Confirm that transcript extraction is reused and the final mix is measured again.
- [ ] Verify caption wording and timing, dual-mono channel levels and independent loudness/true-peak rows. Reference kajisho5/ffmpeg-skill#721 and kajisho5/ffmpeg-skill#722.
- [ ] Keep the exported file, technical QC and human acceptance as separate evidence. Exercise publishing with a mock. Require explicit approval before any live post.

Dependencies: the four existing workflow issues and a cleared Japanese-language fixture. Scope: Velisa's plan/review/receipt integration. No new ffmpeg-skill contract surface.
```

## V2　Control Roomの証拠表示（P1・M）

Repository: `kajisho5/Velisa`

Title: **Show operation-level contract, adapter and acceptance evidence in Control Room**

```markdown
The ownership ledger, historical status docs and current agent adapters answer different questions. A repository marked active can expose a handoff, an executable operation, or an independent tool. Build on the health data tracked in #152.

- [ ] Display owner, producer commit, pinned contract, runtime acceptance, adapter/handoff, synthetic result and real-material result independently. Include evidence URI, observed revision and environment per result.
- [ ] Demonstrate three cases against source: Remotion's measured-motion path, HyperFrames' executable alpha layer alongside a scene handoff, and NLE read-back via diff.
- [ ] Preserve an unknown result where evidence is missing. Mark old evidence with its revision. Show standalone acceptance for disc kits, oncemore, stepcap and governance tools.
- [ ] Verify the rendered view against a fixture with matching pin bytes but no runtime run, another with a stale passing receipt, and a real pass at the selected revision.

Dependencies: ecosystem.json, agent pins/adapters and System Intelligence observations. Change the dashboard data/view and its tests; do not change producer contracts merely to populate a cell.
```

## C1　対応する下位ビルドでalpha拒否を解除（P0・M）

Repository: `kajisho5/color-grading-skill`

Title: **Enable alpha-preserving grades for premultiplied input when the engine declares support**

```markdown
LUT_APPLY and PRIMARY_CORRECTION currently refuse premultiplied inputs when retaining alpha. Consume the engine capability tracked in kajisho5/ffmpeg-skill#453 and PR #715. Gate implementation on the actual installed capability.

- [ ] Verify rejection with reason alpha_premultiplied on an older engine. On a capable build pass the declared source alpha mode and verify the mode in the returned result.
- [ ] Exercise LUT and primary correction with both qtrle and ProRes 4444. Compare alpha, opaque pixels and re-straightened edge colours against a straight reference. Agree tolerances per effective bit depth, codec, grade and alpha band before the run.
- [ ] Verify straight defaults, RETAG and another consumer of the shared premultiplied write path. Save commands, versions and the failed band/TC when applicable.
- [ ] Run the same request through video-production-agent and attach numeric results plus matched black/white background composites for a rights-cleared production logo/title. Final visual acceptance belongs to the project owner.

Dependencies: stage 1 engine acceptance on #715, then consumer capability detection and the agent pin update if needed. Scope: consumer contract, executor and integration tests. The production fixture path is still unverified. No additional engine freeze exception.
```

## 既存案件に残す作業

|所有先|扱い・依存・完了条件|
|---|---|
|Velisa #167〜#170|各機能は元Issueで追跡。V1が実ジョブの受け入れを束ねる。#164〜#166・#171は提案差分として参照し、マージ状況と実装を照合する。|
|[remotion-ffmpeg-skill #32](https://github.com/kajisho5/remotion-ffmpeg-skill/issues/32)|P1。kit@1をconsumerで投影し、colours入力・不要キー・元ファイル不変・still/render/deliveryの一致を確認。新規票不要。|
|[video-production-agent #60](https://github.com/kajisho5/video-production-agent/issues/60)|P1。現行pinでconcat→speed→resize→fit/fillを実行。要求寸法、compiler引数、実測を比較し、consumerの修正か期待値の訂正かを決定。|
|ffmpeg-skill|#453は唯一の既存凍結例外、#721・#722は既存のP1。いずれも既存票を参照する。|

## Velisa旧監査 #33〜#38 の整理案

|既存Issue|担当・優先度|照合する証拠と扱い|
|---|---|---|
|[#33](https://github.com/kajisho5/Velisa/issues/33) multicam/sync|Agent・FF、P1|現行の直接呼出しと上位の所有操作を分け、2カメラの同期・切替のPlan→Receiptを照合。所有者と実行証拠が揃えばクローズ候補。|
|[#34](https://github.com/kajisho5/Velisa/issues/34) export/render/batch|Agent・納品、P1|配信計画、書出し、複数件実行について所有者とconsumerを操作別に特定。所有宣言のみなら実ジョブの参照を残す。|
|[#35](https://github.com/kajisho5/Velisa/issues/35) matrixの旧版記述|Velisa、P2|4.7.0のContractと現行pinを比較し、資料の版・生成日を表示。歴史資料を現行値で上書きせず、現行表に導線を付ける。|
|[#36](https://github.com/kajisho5/Velisa/issues/36) 能力衝突|Registry・QC・解析、P1|checkとQA判定、scenesと観測能力の識別子を現行Contractで突合。重複なら明示選択・既定・拒否の各テストを保存。|
|[#37](https://github.com/kajisho5/Velisa/issues/37) allowed_input_roots|各consumer・統制、P1|opt-in、既定制限、読み書き対象の範囲を現行版ごとに記録。既存利用者の互換性と安全な導入例の両方をレビュー。|
|[#38](https://github.com/kajisho5/Velisa/issues/38) 配布・CI|各repo・統制、P1|各componentの実際の配布方式に沿ってクリーン導入、タグ、CI、Agent pinを照合。PyPIが不要なCLIや独立kitはその配布経路で受け入れる。|

旧票はこの文書作成時には状態を変更しない。クローズ判断には当該commitの証拠と、残作業を所有するIssueが必要。
