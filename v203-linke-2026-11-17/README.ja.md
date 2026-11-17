# v203-linke-2026-11-17

WCH-LinkE（`FBC18F0680B0`、ファーム 2.23）→ CH32V203C8T6（UID `dbb1abcd43e8bc6a`、chip ID `0x20310500`）の RVSWD を、
OEP の ESP32-P4X（`e8f60ae84dd7`、ファーム 0.0.56+b9b46df、HS はポート 3-4）で LinkE の側のピンから 160 MS/s で取り込んだ
生の記録（2026-11-17）。GPIO21 = SWCLK、GPIO16 = SWDIO、流し続け（40 MB/s）、グリッチフィルタなし。1 回に ch32rv 0.31.2 の操作 1 つ。

V203 の速い転送（LinkE の速さ high）は、SWCLK の High が約 19 ns（周期 100 ns）で、160 MS/s でも 3 サンプル。この記録が
欲しかった理由はそこ（9 月の fixture の 50 MS/s では、DMI のアクセスの約半分を取りこぼしていた）。

## 中身

配線が不安定だったので、全部は取れていない。大事なものから 37 本:

- `runs/{high,low}/<操作>`: LinkE の速さ high と low で、L103（`l103-linke-2026-11-17`）と同じ 14 操作。
- `runs/high/x_*`: 64 KiB の読み出し、20 KiB の RAM の読み出し、step の連続 3 回、`target_info` の繰り返し 4 回。

medium、ほかの追加の操作、取り込みの速さを振った組は取っていない（速さは 160 MS/s から作れる: l103 の rate_compare）。

## 撮る前と後

撮る前の flash は WCH の評価用のサンプル（GPIO Toggle）。撮った後、それを書き戻して読み戻して同じことを、オプション
バイトも撮る前と同じことを確かめた。

## 160 MS/s の読みと正解

37 本すべてで ch32rv の DmiOp が 160 MS/s の読みの中に順にすべて見つかり（`truth.log`）、読み出しの 10 本は `read.bin`
と完全に一致する（WireSkein の RVSWD の BURST の割れの直しの後: wireskein の bench/notes/2026-11-17-test-plan の穴 a）。
