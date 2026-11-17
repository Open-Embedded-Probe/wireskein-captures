# wireskein-captures

[WireSkein](https://github.com/Open-Embedded-Probe/wireskein) の分析を測るための、実機の取り込みです。どれも
WireSkein の外から取った正解（デバッガやファームウェア自身の記録、読み書きした中身）を添えています。

ここに置くのは生の記録です。WireSkein のアルゴリズムの測定台（wireskein の `bench/`）は、`bench/data/` にある
写しを読みます。写しは、各取り込みをその操作の区間に切り出し、正解を添えたものです。写しの `SOURCE.json` が、
このリポジトリのコミットと、各ファイルの元を指します。取り方と切り出し方の道具は、写しの `tools/` にあります。

| フォルダ | 内容 |
|---|---|
| `l103-linke-2026-11-17/` | WCH-LinkE → CH32L103C8T6 の RVSWD を、OEP の ESP32-P4X で LinkE の側のピンから 160 MS/s で。ch32rv の操作 103 種（LinkE の速さ high / medium / low ほか）と、4 操作を取り込みの速さ 26 種で（160 MHz〜627 kHz、整数分周と分数分周）。正解は ch32rv の USB の記録（DMI の操作）と、読んだ中身 |

各 run は wireskein-run/1（`run.json`、`c0001.wireskein`）に、`take.json`（取り方）、`truth.json`（正解）、
`reading.json`（その時の WireSkein の読み。正解ではない）、デバッガ自身のファイルを添えたものです。

MIT License（`LICENSE`）。
