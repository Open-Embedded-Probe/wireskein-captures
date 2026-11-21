# x035-rvswd-2026-11-21

[English](README.md)

OEP のプローブが出す RVSWD（2 線）の attach の波形を、OEP の ESP32-P4（30eda0e31451）で 80 MS/s で取り込んだものです。相手の石は
いません。CH32X035 を RVSWD のプローブにするときの、時間の見当をつけるためのものです。

| run | 出したもの |
|---|---|
| `p4_ref` | ESP32-P4 自身の RVSWD（GPIO15 が SWDIO、GPIO14 が SWCLK。同じチャネルで取り込む） |
| `x035_a7adace` | CH32X035F8U6（WeAct のボード、OEP プローブ 283fbc5cc016abcd、配布の版 0.0.60+a7adace）の RVSWD（PA0 が SWDIO、PA1 が SWCLK。P4 の GPIO15 / GPIO14） |

- 相手の石がいないので、どちらも attach の探し（返事を待つ遅い速さ）だけが見えます。RVSWD は相手が返事をしてから速さを上げるので、
  通常の速さは、相手のいる線でしか見えません。
- SWCLK（`tools/runs.py` で読んだ生の長さ）: `p4_ref` は low 560〜720 ns、high 620〜840 ns（周期 約 1.2〜1.5 µs）。`x035_a7adace` は
  low 1.3〜1.5 µs、high 2.0〜2.2 µs（周期 約 3.3 µs）。
- WireSkein は、どちらも RVSWD として読めません（相手の返事が無いので）。

## 道具

- `tools/capture.py`: 1 本取る（`p4_ref`、または `x035 <版の名前>`）。ワンショット 400k サンプル（5 ms）を SWDIO の最初の立ち下がりで
  切り、待ち受けの間に attach を走らせる。
- `tools/runs.py`: 1 本の run の 1 本の線を、L / H の長さで出す（`tools/runs.py runs/<run> 0 40 SWCLK`）。
- `tools/summary.py`: SWIO 用（`../x035-swio-2026-11-21` と同じ）。RVSWD の run には使えない。
