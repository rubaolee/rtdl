from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Optional, List


def summarize_benchmark(payload: dict[str, object]) -> str:
    lines = [
        "RTDL Embree Baseline Summary",
        "============================",
        f"iterations: {payload['iterations']}",
        f"warmup    : {payload['warmup']}",
        "",
    ]
    grouped: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
    for record in payload["records"]:
        grouped.setdefault((record["workload"], record["dataset"]), {})[record["backend"]] = record

    for (workload, dataset), backends in grouped.items():
        lines.append(f"{workload} :: {dataset}")
        cpu = backends.get("cpu")
        embree = backends.get("embree")
        if cpu is not None:
            lines.append(f"  cpu    mean={cpu['mean_sec']:.6f}s median={cpu['median_sec']:.6f}s")
        if embree is not None:
            lines.append(f"  embree mean={embree['mean_sec']:.6f}s median={embree['median_sec']:.6f}s")
            if cpu is not None and embree["mean_sec"] > 0:
                lines.append(f"  speedup {cpu['mean_sec'] / embree['mean_sec']:.3f}x")
            if "parity" in embree:
                lines.append(f"  parity  {embree['parity']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize RTDL Embree baseline benchmark JSON.")
    parser.add_argument("benchmark_json")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.benchmark_json).read_text(encoding="utf-8"))
    print(summarize_benchmark(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
