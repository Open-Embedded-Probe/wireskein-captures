# l103-linke-2026-11-17

WCH-LinkE（`0E028F0692F1`）→ CH32L103C8T6（UID `3a6dabcda282bc48`）の RVSWD を、OEP の ESP32-P4X（`e8f60ae84dd7`、
ファーム 0.0.56+dea9e3c）で LinkE の側のピンから取り込んだ生の記録（2026-11-17）。GPIO12 = SWCLK、GPIO15 = SWDIO、
流し続け、グリッチフィルタなし。1 回に ch32rv 0.31.2 の操作 1 つ。

- `runs/{high,medium,low}/<操作>`: LinkE の速さ 3 段で同じ 14 操作、`runs/high/x_*`: 追加の 61 操作。160 MS/s。
- `runs/rate/<MHz>/<操作>`: 4 操作を、取り込みの速さ 26 種（160 MHz の整数分周と分数分周、160 MHz〜627 kHz）で。
- `runs/retries.jsonl`: 撮り直した試行と理由（P4X の HS の USB が 2 回切れた: 07:07:05、07:47:59）。
- `backup/`: 収録の前の L103 のオプションバイトと target info（収録の後に flash とオプションバイトを収録の前と同じに戻し、読み戻して確かめた。flash の中身はほかのプロジェクトの試験用ファームなので、ここには入れていない）。
- `*.log`、`rate-report.md`、`rate-compare.json`: 収録、正解の照合、取り込みの速さの比較の出力。

道具（`capture.py`、`truth.py`、`publish.py`、`rate_report.py`、`rate_compare.py`）と説明は、wireskein の
`bench/data/l103-linke-2026-11-17/`（測定台の写し）にあります。取り込みの道具は ch32rv を PATH か環境変数 `CH32RV` から使い、
`take.json` の引数のファイルは道具のフォルダ（`tools/`）からの相対です。
