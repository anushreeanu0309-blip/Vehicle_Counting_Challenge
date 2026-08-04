from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def save_cars_per_minute_chart(events: list[dict], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    minute_counter = Counter()
    for event in events:
        minute = int(event.get('frame_index', 0) // max(1, event.get('fps_for_chart', 30) * 60))
        minute_counter[minute] += 1

    xs = sorted(minute_counter.keys())
    ys = [minute_counter[x] for x in xs]

    plt.figure(figsize=(10, 5))
    plt.plot(xs, ys, marker='o', linewidth=2)
    plt.title('Cars Per Minute')
    plt.xlabel('Minute Index')
    plt.ylabel('Count')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return output_path
