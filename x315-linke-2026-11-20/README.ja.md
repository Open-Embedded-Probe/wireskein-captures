# x315-linke-2026-11-20

WCH-LinkE（`FBC18F0680B0`、ファーム 2.23）→ CH32X315MCU6（UID `36a0abcd9eb5bc48`、chip ID `0x31500000`）の SWIO を、OEP の
ESP32-P4X（`e8f60ae84dd7`、ファーム 0.0.59+6412594）で LinkE の側のピンから取った生の記録（2026-11-20）。1 回に ch32rv 0.32.3 の
操作 1 つ。道具は v003-linke-2026-11-17 の `tools/capture.py` を X315 に合わせたもの（target・UID・WRONG_CHIP、書き込む sketch を
ch32rv の `tests/fixtures/debug-smoke` の dmdata.bin = `tools/x315_smoke.bin` に。V003 用の clock の組は外した）。

## 取り方

- `runs/{high,medium,low}/<操作>`: SWIO（GPIO16）の 1 線だけ、160 MS/s の流し続け。LinkE の速さ 3 段で同じ 14 操作（42 本）と、
  `runs/high/x_target_info_{2,3,4}`。ほかの追加の操作・取り込みの速さの掃引・接続時の 2 線は撮っていない（ユーザーの判断:
  1 線の形と DMI の並びは V003 と同じなので、違いは 1 線と 2 線の切り替えだけ。それは `two-wire/` にある）。
- 正解は `truth.json`（ch32rv の USB の記録の DmiOp と read.bin）。`reading.json` は WireSkein の読み（正解ではない）。
- 全 45 本とも欠けなし（1 回目で取れた）。160 MS/s の読みに、ch32rv の DmiOp が順にすべて見つかった（`truth.log`）。
- `high/dbg_regs`、`medium/dbg_halt`、`medium/dbg_step` は ch32rv が rc 20（target-no-response、接続の失敗）。flash にパターンを
  書いた後の、target が不定のコードを走らせている間。失敗した接続の記録として残した。

## 撮る前と後

撮る前に flash（480 KiB）とオプションバイト（`a55af708ff00ff00ff00ff00ff00ff00`）を 2 回読んで一致を確かめて取っておき、撮った後に
chip erase と元の先頭 192768 byte の書き込みで戻し、480 KiB とオプションバイトを読み戻して一致を確かめた（sha256
`b8843ff1…a36001`）。

## 1 線と 2 線

`two-wire/README.ja.md`。
