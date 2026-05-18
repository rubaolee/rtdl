from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _phase(phases: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(phases, dict):
        return None
    return phases.get(key)


def _fixture_rows(input_dir: Path) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for filename in [
        "fixture_lsi_prepared_count.json",
        "fixture_pip_prepared_rows_nomaterialize.json",
    ]:
        payload = _load(input_dir / filename)
        if payload is None:
            rows.append([filename, "missing", None, None, None, None, None])
            continue
        phases = payload.get("phases_sec")
        rows.append(
            [
                payload.get("workload", filename),
                payload.get("result_mode"),
                payload.get("row_count"),
                _phase(phases, "query_pack_sec"),
                _phase(phases, "static_shape_pack_sec"),
                _phase(phases, "prepare_static_scene_sec"),
                _phase(phases, "prepared_query_sec"),
            ]
        )
    return rows


def _same_query_rows(input_dir: Path) -> list[list[Any]]:
    payload = _load(input_dir / "same_query_prepared_comparison.json")
    if payload is None:
        return [["same-query stream replay", "skipped", None, None, None, None, None]]

    rows: list[list[Any]] = []
    lsi = payload.get("lsi", {})
    if isinstance(lsi, dict):
        rows.append(
            [
                "lsi/raw_rows",
                lsi.get("query_count"),
                lsi.get("left_segments"),
                lsi.get("right_segments"),
                lsi.get("prepare_sec"),
                (lsi.get("raw_rows") or {}).get("median_sec"),
                lsi.get("row_count_parity"),
            ]
        )
        rows.append(
            [
                "lsi/scalar_count",
                lsi.get("query_count"),
                lsi.get("left_segments"),
                lsi.get("right_segments"),
                lsi.get("prepare_sec"),
                (lsi.get("scalar_count") or {}).get("median_sec"),
                lsi.get("row_count_parity"),
            ]
        )
    pip = payload.get("pip", {})
    if isinstance(pip, dict):
        rows.append(
            [
                "pip/positive_rows",
                pip.get("query_count"),
                pip.get("points"),
                pip.get("shapes"),
                pip.get("prepare_sec"),
                (pip.get("positive_rows") or {}).get("median_sec"),
                pip.get("row_count_parity"),
            ]
        )
        rows.append(
            [
                "pip/scalar_count",
                pip.get("query_count"),
                pip.get("points"),
                pip.get("shapes"),
                pip.get("prepare_sec"),
                (pip.get("scalar_count") or {}).get("median_sec"),
                pip.get("row_count_parity"),
            ]
        )
    return rows


def _write_table(lines: list[str], headers: list[str], rows: list[list[Any]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_fmt(value) for value in row) + " |")


def summarize(input_dir: Path) -> str:
    lines: list[str] = [
        "# Goal2327 RayJoin Pod Artifact Summary",
        "",
        f"Input directory: `{input_dir}`",
        "",
    ]
    gpu_text = (input_dir / "gpu.txt").read_text(encoding="utf-8").strip() if (input_dir / "gpu.txt").exists() else "n/a"
    lines.extend(["## Hardware", "", f"- GPU: `{gpu_text}`", ""])

    lines.extend(["## Fixture Prepared OptiX Route", ""])
    _write_table(
        lines,
        [
            "workload",
            "mode",
            "rows/count",
            "query_pack_sec",
            "shape_pack_sec",
            "prepare_sec",
            "query_sec",
        ],
        _fixture_rows(input_dir),
    )
    lines.append("")

    lines.extend(["## Same-Query Stream Replay", ""])
    _write_table(
        lines,
        [
            "route",
            "queries",
            "left/items",
            "right/shapes",
            "prepare_sec",
            "median_query_sec",
            "parity",
        ],
        _same_query_rows(input_dir),
    )
    lines.append("")

    boundary = _load(input_dir / "claim_boundary.json") or {}
    lines.extend(["## Claim Boundary", ""])
    for key in sorted(boundary):
        lines.append(f"- `{key}`: `{_fmt(boundary[key])}`")
    lines.append("")
    lines.append(
        "This summary is descriptive evidence only. It does not authorize a "
        "RayJoin paper-speedup claim or a v2.0 release claim."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Goal2327 RayJoin pod artifacts.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(summarize(input_dir), encoding="utf-8")
    print(f"wrote {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
