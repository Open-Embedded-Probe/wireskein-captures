# wireskein-captures

[WireSkein](https://github.com/Open-Embedded-Probe/wireskein) の分析を測るための、実機の取り込みです。どれも
WireSkein の外から取った正解（デバッガやファームウェア自身の記録、読み書きした中身）を添えています。

ここに置くのは生の記録です。WireSkein のアルゴリズムの測定台（wireskein の `bench/`）は、`bench/data/` にある
写しを読みます。写しは、各取り込みをその操作の区間に切り出し、正解を添えたものです。写しの `SOURCE.json` が、
このリポジトリのコミットと、各ファイルの元を指します。

取り込みは、このリポジトリで行います。各フォルダの `tools/` が取り方（`capture.py`）、正解の照合（`truth.py`）、測定台への切り出し（`publish.py`）です。撮り終えて確定したものだけを、`publish.py` で wireskein の `bench/data/` に写します（wireskein の作業ツリーで撮らない）。

| フォルダ | 内容 |
|---|---|
| `l103-linke-2026-11-17/` | WCH-LinkE → CH32L103C8T6 の RVSWD を、OEP の ESP32-P4X で LinkE の側のピンから 160 MS/s で。ch32rv の操作 103 種（LinkE の速さ high / medium / low ほか）と、4 操作を取り込みの速さ 26 種で（160 MHz〜627 kHz、整数分周と分数分周）。正解は ch32rv の USB の記録（DMI の操作）と、読んだ中身 |
| `v003-linke-2026-11-17/` | WCH-LinkE → CH32V003F4P6 の SWIO を、同じ P4X で SWIO の 1 線だけ 160 MS/s で（接続の 2 線の問い合わせは別の 3 本で 2 線）。L103 と同じ組の操作と、取り込みの速さ 5 種。正解は ch32rv の USB の記録と読んだ中身 |
| `v203-linke-2026-11-17/` | WCH-LinkE → CH32V203C8T6 の RVSWD を、同じ P4X で 2 線・160 MS/s で（速い転送の SWCLK の High は約 19 ns）。LinkE の速さ high と low の 14 操作と追加の 9 本（配線が不安定で全部は取れていない）。正解は ch32rv の USB の記録と読んだ中身 |
| `x315-linke-2026-11-20/` | WCH-LinkE → CH32X315MCU6 の SWIO を、同じ P4X で SWIO の 1 線だけ 160 MS/s で。LinkE の速さ high / medium / low の 14 操作と target info 3 本（45 本、うち 3 本は接続の失敗）。`two-wire/` に 1 線 → 2 線の切り替えの実験 9 本（50 MS/s、SWIO・SWCLK。DMI `0x7E`・`0x7D` の書き込みと LinkE の `ee 02` / `ee 03`）。正解は ch32rv の USB の記録と読んだ中身 |
| `x315-linke-tap-2026-11-20/` | WCH-LinkE → CH32X315MCU6 の target info を、同じ P4X で 2 線（SWCLK・SWDIO）・80 / 160 MS/s で 3 本。うち 2 本は GPIO16 の分岐が浮いていた記録、1 本は直した後（1 線の SWIO が V003 と同じ形）。浮いた入力を見分ける試験の組。正解は ch32rv の USB の記録 |
| `x035-swio-2026-11-21/` | OEP のプローブの SWIO を、OEP の ESP32-P4 で 80 MS/s で（相手の石なし）。V003 に通る ESP32-P4 自身の波形と、CH32X035 の版ごとの波形（通らない 3 本と通る 2 本）。正解は同じ版を V003 に attach した結果 |

各 run は wireskein-run/1（`run.json`、`c0001.wireskein`）に、`take.json`（取り方）、`truth.json`（正解）、
`reading.json`（その時の WireSkein の読み。正解ではない）、デバッガ自身のファイルを添えたものです。

MIT License（`LICENSE`）。
