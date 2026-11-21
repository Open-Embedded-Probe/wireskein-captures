# x035-swio-2026-11-21

[English](README.md)

OEP のプローブが出す SWIO（CH32V00x の 1 線のデバッグ）の波形を、OEP の ESP32-P4（30eda0e31451）で 80 MS/s で取り込んだものです。
CH32X035 を OEP のプローブにするときの、SWIO の時間の合わせ込みに使います。

| run | 出したもの | CH32V003 で |
|---|---|---|
| `p4_ref` | ESP32-P4 自身の SWIO（GPIO15、同じチャネルで取り込む） | 通る（同じファームが常駐ベンチの V003 に attach する） |
| `x035_late-5-9-10` | CH32X035F8U6 の SWIO（PA0）。エッジごとの遅れを段ごとに 5 / 9 / 10 tick 差し引いた版 | 通らない |
| `x035_readbit-timeline` | 上に加え、読みのビットを締め切りの足し算だけで進め、1 を読んだら立ち上がりを待たない版 | 通らない |
| `x035_half-late-2` | 上に加え、読みの half の差し引きを 2 tick にした版 | 通らない |
| `x035_sample-750ns` | 上に加え、読みの最初の押し上げ（recharge）をやめ、放してから 750 ns でサンプルする版 | 通る（attach 10 回中 10 回、target info、flash 16 KiB の読み出し 2 回が一致） |

- 取り込んだ線には相手の石がいません（X035 の PA0 と P4 の GPIO15 だけ）。波形はプローブが出したもので、読みのビットはプルアップで high に戻ります。
- 「CH32V003 で」の列は、同じ版を別の CH32X035F8U6（WeAct のボード、PA0 に V003 の SWIO、V003 は X035 のボードの 3V3 から給電）に焼いて attach した結果です。その線は取り込んでいません。
- X035 の取り込み元は WeAct の CH32X035F8U6 のボード（OEP プローブ 283fbc5cc016abcd、UID c016abcd283fbc5c）です。PA0〜PA7、PB0、PB1、PB3、PB11、PB12、PC14、PC15 が P4 につながっています（PA0 が GPIO15）。

WireSkein の読み（`tools/summary.py`、各 run のフレームの中央値）:

| run | フレーム | 短い low | 長い low | 書き込みの high | 読みの 1 ビットの周期 | 読みの high |
|---|---|---|---|---|---|---|
| `p4_ref` | 16、全部 ok | 312.5 ns | 912.5 ns | 312.5 ns | 850.0 ns | 425.0 ns |
| `x035_late-5-9-10` | 24、全部 ok | 287.5 ns | 850.0 ns | 350.0 ns | 1387.5 ns | 1012.5 ns |
| `x035_readbit-timeline` | 24、全部 ok | 287.5 ns | 812.5 ns | 400.0 ns | 950.0 ns | 687.5 ns |
| `x035_half-late-2` | 24、全部 ok | 287.5 ns | 812.5 ns | 400.0 ns | 950.0 ns | 687.5 ns |
| `x035_sample-750ns` | 24、全部 ok | 287.5 ns | 812.5 ns | 337.5 ns | 734.4 ns | 768.8 ns |

参考に、WCH-LinkE → CH32V003 の SWIO（`../v003-linke-2026-11-17/runs/high/target_info`）は、短い low 250 ns、長い low 875 ns、
書き込みの high 369 ns、読みの 1 ビットの周期 766 ns、読みの high 391 ns です。

## 道具

- `tools/capture.py`: 1 本取る（`p4_ref`、または `x035 <版の名前>`）。ワンショット 400k サンプル（5 ms）を SWIO の最初の立ち下がりで切り、待ち受けの間に attach を走らせる。
- `tools/summary.py`: 各 run を WireSkein で読み、フレームの中央値を出す。
- `tools/runs.py`: 1 本の run の SWIO を、フレームごとに L / H の長さで出す。

```sh
uv run --project <wireskein> --with-editable <oep-client-python> python tools/capture.py runs x035 <版の名前> [メモ]
uv run --project <wireskein> python tools/summary.py runs/*
```
