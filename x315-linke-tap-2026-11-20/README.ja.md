# x315-linke-tap-2026-11-20

WCH-LinkE（`FBC18F0680B0`）→ CH32X315MCU6（UID `36a0abcd9eb5bc48`）の `ch32rv target info`（0.32.2、rc 0）を、
OEP の ESP32-P4X（`e8f60ae84dd7`、ファーム 0.0.59+6412594）で LinkE の側のピンから取った 3 本（2026-11-20）。
GPIO21 = SWCLK、GPIO16 = SWDIO。oneshot で、SWCLK の最初の立ち下がりがトリガー。

置いた理由は、**分岐が浮いていた記録と、直した後の記録の組**であること。同じ台・同じ操作で、片方は GPIO16 の分岐が
LinkE の SWDIO に届いておらず（ユーザーが配線を直す前）、もう片方は直した後。浮いた入力を見分ける試験の正解に使える。
X315 の SWIO の操作の組は、別に取る。

| run | 速さ | 分岐 | 中身 |
|---|---|---|---|
| `runs/loose_80M/` | 80 MS/s、0.5 s、前 12.5 ms | 浮いていた | SWDIO に 1 線の形がない |
| `runs/loose_160M/` | 160 MS/s、0.42 s（プローブの上限）、前 500000 サンプル | 浮いていた | 同じ |
| `runs/fixed_160M/` | 160 MS/s、0.42 s、前 500000 サンプル | 直した後 | 2 線の試しの後、1 線の SWIO |

各 run: `c0001.wireskein`（生の記録）、`ch32rv.ndjson`（ch32rv `--capture`: LinkE との USB の往復）、`capture.log`。

## 何が見えるか

- 浮いていた 2 本の SWDIO: 幅は 1 サンプルが一番多く、長くなるほど数が減る（どの幅にも固まらない）。300 ns の
  debounce の後も、数 µs〜十数 µs の不揃いな Low / High しか残らない。4〜6 ms おきのまとまりが、LinkE が動く前から
  ch32rv が終わった後まで続く。2 線の間は、SWDIO の変化の多くが SWCLK の端から数サンプル以内（クロックからの飛び移り）。
  WireSkein 0.0.32 の swio は decoded false。rvswd は中身 0 の NOP を 4 つ読むだけ（正しい読みではない）。
- 直した後: 1 線の SWDIO は Low 250 / 850 ns、High 350〜375 ns に固まる（v003-linke-2026-11-17 の SWIO と同じ形）。
  WireSkein の swio で 108 フレームすべて ok（0x7E / 0x7D への書き込みと 0x7C の読み出しから始まる）。
- 接続のとき、LinkE はまず 2 線で約 77 ms 問い合わせ（クロックのバースト 40 回、半周期 1062.5 ns、SWDIO に 7 変化ずつの
  まとまり）、X315 が答えないので 1 線に落ち、最後まで 1 線のまま。v003-linke-2026-11-17 の `runs/attach2/` と同じ形。

## 正解

`ch32rv.ndjson` の USB の記録だけ（attach は 89.6 ms、UID の読みは attach で得た値）。DmiOp との照合（`truth.py`）は
していない。浮いた記録の正解は「この線は信号を運んでいない」こと（直した後の記録と、同じ操作の USB の記録が根拠）。
