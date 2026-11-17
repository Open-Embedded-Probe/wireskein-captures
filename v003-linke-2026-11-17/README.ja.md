# v003-linke-2026-11-17

WCH-LinkE（`FBC18F0680B0`、ファーム 2.23）→ CH32V003F4P6（UID `ef17abcd5957be73`、chip ID `0x00300510`）の SWIO を、
OEP の ESP32-P4X（`e8f60ae84dd7`、HS はポート 3-4）で LinkE の側のピンから取り込んだ生の記録（2026-11-17）。1 回に
ch32rv 0.31.2 の操作 1 つ。

## 取り方

- `runs/{high,medium,low}/<操作>`、`runs/high/x_*`: SWIO（GPIO16、LinkE の SWDIO）の 1 線だけ、160 MS/s の流し続け
  （20 MB/s）。LinkE の速さ 3 段で同じ 14 操作と、追加の操作。L103（`l103-linke-2026-11-17`）と同じ組で、V003 の大きさに
  合わせたもの（flash 16 KiB、RAM 2 KiB）。
- `runs/rate/<MHz>/<操作>`: 4 操作を、取り込みの速さ 160、133.3、50、10、5 MHz で。
- `runs/attach2/<速さ>/target_info`: 接続のときに LinkE が 2 線（RVSWD）で問い合わせる所（約 100 ms）を、SWIO と SWCLK
  （GPIO21）の 2 線で。SWCLK の最初の立ち下がりから 0.15 秒の 1 回取り（プローブのメモリへ）、160 MS/s。
- 正解は `truth.json`（ch32rv の USB の記録の DmiOp と読み出しの結果）。`reading.json` はその時の WireSkein の読み
  （正解ではない）。

## プローブのファーム

撮る間に、プローブのファームが替わった（どの run がどれかは、取り込みの `meta.probe.firmware`）。

| ファーム | run | 説明 |
|---|---|---|
| 0.0.56+645fbad-diag | 28（high / medium の初め） | 診断の版。流し続けの回収が 36.7 MB/s で頭打ち。1 線（20 MB/s）では欠けない |
| 0.0.56+958a231 | 95 | 正式な版 |
| 0.0.56+b9b46df | 3（attach2） | トリガーを待つ 1 回取りの欠けを直した版（それより前の版では、2 線・160 MS/s の 1 回取りが欠けた） |

どの run も欠けなし（取り込みの時計で、操作が収まったことを確かめてある）。

## 撮る前と後

撮る前の V003 の flash は空（すべて 0xFF）。撮った後、flash を消し、オプションバイトを撮る前の値
（`a55af50aff00ff00ff00ff00ff00ff00`、NRST 12 ms）に書き戻し、読み戻して同じことを確かめた。

## 160 MS/s の読みと正解

ch32rv の DmiOp が、160 MS/s の SWIO の読みの中に順にすべて見つかったのは 126 本中 104 本（`truth.log`。attach2 の 3 本は DmiOp 0 件）。見つからない
22 本は短い操作（dbg_halt、dbg_resume、DMI の単発の読み書きなど）で、接続のあとのフレームが「読めなかった区間」に
なっている。LinkE の 2.23 は SWIO のフレームの間を詰めて送り、WireSkein の SWIO はそれを区切れない
（wireskein の bench/notes/2026-11-17-test-plan の穴 b）。
