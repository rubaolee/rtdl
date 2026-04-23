#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _hash_summary(summary: Any) -> str:
    payload = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_goal835_row(*, app: str, path_name: str, baseline_name: str) -> dict[str, Any]:
    from scripts.goal835_rtx_baseline_collection_plan import build_plan

    for row in build_plan()["rows"]:
        if (
            row.get("app") == app
            and row.get("path_name") == path_name
            and baseline_name in row.get("required_baselines", ())
        ):
            return row
    raise KeyError(f"no Goal835 row for {app}:{path_name}:{baseline_name}")


def build_baseline_artifact(
    *,
    row: dict[str, Any],
    baseline_name: str,
    source_backend: str,
    benchmark_scale: dict[str, Any] | None,
    repeated_runs: int,
    correctness_parity: bool,
    phase_seconds: dict[str, float],
    summary: dict[str, Any],
    notes: list[str] | None = None,
    validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact = {
        "goal": "Goal839 local baseline artifact writer",
        "app": row["app"],
        "path_name": row["path_name"],
        "baseline_name": baseline_name,
        "status": "ok" if correctness_parity else "invalid",
        "source_backend": source_backend,
        "correctness_parity": bool(correctness_parity),
        "phase_separated": True,
        "authorizes_public_speedup_claim": False,
        "repeated_runs": int(repeated_runs),
        "required_phase_coverage": list(row["required_phases"]),
        "comparable_metric_scope": row["comparable_metric_scope"],
        "benchmark_scale": benchmark_scale,
        "claim_limit": row["claim_limit"],
        "phase_seconds": dict(phase_seconds),
        "summary": summary,
        "summary_sha256": _hash_summary(summary),
        "notes": list(notes or ()),
    }
    if validation is not None:
        artifact["validation"] = validation
    return artifact


def write_baseline_artifact(path: str | Path, artifact: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
