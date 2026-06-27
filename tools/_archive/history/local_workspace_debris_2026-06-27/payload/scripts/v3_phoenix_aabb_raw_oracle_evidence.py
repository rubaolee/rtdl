#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.aabb_index import prepare_aabb_index_2d  # noqa: E402


OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.json"
OUT_MD = OUT_JSON.with_suffix(".md")
DEFAULT_OUT_DIR = ROOT / "docs/rebuild/v3/evidence/phoenix_v3_aabb_raw_oracle_20260621"
SOURCE_MANIFEST_FILES = (
    "src/rtdsl/aabb_index.py",
    "src/rtdsl/optix_runtime.py",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "scripts/v3_phoenix_aabb_raw_oracle_evidence.py",
    "scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py",
    "scripts/v3_phoenix_aabb_native_query_handle_evidence.py",
)


def intersects_closed(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def cpu_oracle_rows(
    indexed_boxes: Iterable[tuple[float, float, float, float]],
    query_boxes: Iterable[tuple[float, float, float, float]],
    *,
    indexed_ids: Iterable[int],
    query_ids: Iterable[int],
) -> tuple[tuple[int, int], ...]:
    indexed_tuple = tuple(indexed_boxes)
    query_tuple = tuple(query_boxes)
    indexed_id_tuple = tuple(int(value) for value in indexed_ids)
    query_id_tuple = tuple(int(value) for value in query_ids)
    if len(indexed_tuple) != len(indexed_id_tuple):
        raise ValueError("indexed_ids length must match indexed_boxes length")
    if len(query_tuple) != len(query_id_tuple):
        raise ValueError("query_ids length must match query_boxes length")
    rows: set[tuple[int, int]] = set()
    for query_index, query_box in enumerate(query_tuple):
        for indexed_index, indexed_box in enumerate(indexed_tuple):
            if intersects_closed(query_box, indexed_box):
                rows.add((query_id_tuple[query_index], indexed_id_tuple[indexed_index]))
    return tuple(sorted(rows))


def fixture_catalog() -> tuple[dict[str, Any], ...]:
    return (
        {
            "name": "mixed_overlap_zero_touch_duplicate",
            "indexed_boxes": (
                (0.0, 0.0, 1.0, 1.0),
                (0.5, 0.5, 1.5, 1.5),
                (2.0, 2.0, 3.0, 3.0),
                (4.0, 4.0, 5.0, 5.0),
                (0.5, 0.5, 1.5, 1.5),
            ),
            "indexed_ids": (101, 102, 103, 104, 105),
            "query_boxes": (
                (0.75, 0.75, 0.9, 0.9),
                (1.5, 1.5, 2.0, 2.0),
                (10.0, 10.0, 11.0, 11.0),
                (5.0, 5.0, 6.0, 6.0),
                (0.5, -0.5, 0.5, 0.5),
            ),
            "query_ids": (201, 202, 203, 204, 205),
            "fixture_boundary": (
                "multiple overlaps, duplicate-prone identical indexed bounds, zero-overlap query, "
                "and closed-boundary edge-touch cases"
            ),
        },
        {
            "name": "dense_capacity_pressure",
            "indexed_boxes": (
                (0.0, 0.0, 4.0, 4.0),
                (0.5, 0.5, 4.5, 4.5),
                (1.0, 1.0, 5.0, 5.0),
                (-0.5, -0.5, 3.5, 3.5),
            ),
            "indexed_ids": (301, 302, 303, 304),
            "query_boxes": (
                (0.25, 0.25, 1.25, 1.25),
                (2.0, 2.0, 3.0, 3.0),
                (3.75, 3.75, 4.25, 4.25),
                (-1.0, -1.0, 0.0, 0.0),
            ),
            "query_ids": (401, 402, 403, 404),
            "fixture_boundary": "dense many-to-many overlaps for capacity and duplicate-row pressure",
        },
    )


def run_backend_fixture(backend: str, fixture: dict[str, Any]) -> dict[str, Any]:
    expected = cpu_oracle_rows(
        fixture["indexed_boxes"],
        fixture["query_boxes"],
        indexed_ids=fixture["indexed_ids"],
        query_ids=fixture["query_ids"],
    )
    row_capacity = max(1, len(expected) * 2 + 8)
    started = time.perf_counter()
    prepared = prepare_aabb_index_2d(
        fixture["indexed_boxes"],
        indexed_ids=fixture["indexed_ids"],
        backend=backend,
    )
    try:
        if backend == "optix":
            rows = prepared.intersection_rows(
                fixture["query_boxes"],
                tuple(fixture["query_ids"]),
                row_capacity=row_capacity,
            )
        elif backend == "embree":
            rows = prepared.intersection_rows(
                fixture["query_boxes"],
                tuple(fixture["query_ids"]),
            )
        else:
            rows = cpu_oracle_rows(
                fixture["indexed_boxes"],
                fixture["query_boxes"],
                indexed_ids=fixture["indexed_ids"],
                query_ids=fixture["query_ids"],
            )
        cache_stats = getattr(prepared, "prepared_query_cache_stats", lambda: {})()
    finally:
        close = getattr(prepared, "close", None)
        if callable(close):
            close()
    elapsed = time.perf_counter() - started
    return {
        "backend": backend,
        "fixture": fixture["name"],
        "row_capacity": row_capacity if backend == "optix" else None,
        "expected_row_count": len(expected),
        "actual_row_count": len(rows),
        "expected_rows": expected,
        "actual_rows": tuple(sorted((int(a), int(b)) for a, b in rows)),
        "matches_independent_cpu_oracle": tuple(sorted(rows)) == expected,
        "elapsed_sec": elapsed,
        "prepared_query_cache_stats": cache_stats,
    }


def run_optix_capacity_pressure(fixture: dict[str, Any]) -> dict[str, Any]:
    expected = cpu_oracle_rows(
        fixture["indexed_boxes"],
        fixture["query_boxes"],
        indexed_ids=fixture["indexed_ids"],
        query_ids=fixture["query_ids"],
    )
    low_capacity = max(0, min(2, len(expected) - 1))
    prepared = prepare_aabb_index_2d(
        fixture["indexed_boxes"],
        indexed_ids=fixture["indexed_ids"],
        backend="optix",
    )
    try:
        try:
            prepared.intersection_rows(
                fixture["query_boxes"],
                tuple(fixture["query_ids"]),
                row_capacity=low_capacity,
            )
        except RuntimeError as exc:
            text = str(exc)
            return {
                "backend": "optix",
                "fixture": fixture["name"],
                "low_capacity": low_capacity,
                "expected_required_unique_rows": len(expected),
                "overflow_fail_closed_observed": "failure_mode=fail_closed_overflow" in text,
                "error": text,
            }
        return {
            "backend": "optix",
            "fixture": fixture["name"],
            "low_capacity": low_capacity,
            "expected_required_unique_rows": len(expected),
            "overflow_fail_closed_observed": False,
            "error": None,
        }
    finally:
        close = getattr(prepared, "close", None)
        if callable(close):
            close()


def run_oracle(backends: tuple[str, ...]) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, Any] | None]:
    rows: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    capacity_pressure: dict[str, Any] | None = None
    fixtures = fixture_catalog()
    for backend in backends:
        for fixture in fixtures:
            try:
                rows.append(run_backend_fixture(backend, fixture))
            except Exception as exc:  # pragma: no cover - backend/host dependent
                errors[f"{backend}:{fixture['name']}"] = repr(exc)
        if backend == "optix":
            try:
                capacity_pressure = run_optix_capacity_pressure(fixtures[-1])
            except Exception as exc:  # pragma: no cover - backend/host dependent
                errors["optix:capacity_pressure"] = repr(exc)
    return rows, errors, capacity_pressure


def source_manifest() -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    root_hash = hashlib.sha256()
    for rel in SOURCE_MANIFEST_FILES:
        path = ROOT / rel
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        entries.append({"path": rel, "sha256": digest})
        root_hash.update(rel.encode("utf-8"))
        root_hash.update(b"\0")
        root_hash.update(digest.encode("ascii"))
        root_hash.update(b"\0")
    return {
        "algorithm": "sha256",
        "files": entries,
        "sha256": root_hash.hexdigest(),
    }


def command_text(command: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - host tool dependent
        return f"ERROR: {exc!r}"
    text = completed.stdout.strip()
    if completed.stderr.strip():
        text = (text + "\n" if text else "") + completed.stderr.strip()
    return text


def environment_payload() -> dict[str, Any]:
    return {
        "tool": "v3_phoenix_aabb_raw_oracle_environment",
        "python": sys.version,
        "cwd": str(ROOT),
        "git_head": command_text(["git", "rev-parse", "HEAD"], cwd=ROOT).strip(),
        "nvidia_smi": command_text(
            ["nvidia-smi", "--query-gpu=name,driver_version,compute_cap", "--format=csv,noheader"]
        ).strip(),
        "source_manifest": source_manifest(),
        "env": {
            "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY"),
            "RTDL_EMBREE_LIBRARY": os.environ.get("RTDL_EMBREE_LIBRARY"),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
        },
    }


def build_payload(backends: tuple[str, ...]) -> dict[str, Any]:
    observed_rows, run_errors, capacity_pressure = run_oracle(backends)
    fixture_names = {fixture["name"] for fixture in fixture_catalog()}
    backend_names_with_rows = {row["backend"] for row in observed_rows}
    checks = {
        "all_requested_backends_ran_without_errors": not run_errors,
        "all_requested_backends_have_all_fixtures": all(
            {row["fixture"] for row in observed_rows if row["backend"] == backend} == fixture_names
            for backend in backends
        ),
        "all_rows_match_independent_cpu_oracle": bool(observed_rows)
        and all(row["matches_independent_cpu_oracle"] for row in observed_rows),
        "embree_backend_checked_if_requested": ("embree" not in backends) or ("embree" in backend_names_with_rows),
        "optix_backend_checked_if_requested": ("optix" not in backends) or ("optix" in backend_names_with_rows),
        "optix_capacity_pressure_fail_closed_if_requested": (
            "optix" not in backends
            or bool(capacity_pressure and capacity_pressure.get("overflow_fail_closed_observed") is True)
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    environment = environment_payload()
    status = "aabb_raw_oracle_pass_not_m7" if not failed_checks else "aabb_raw_oracle_fail_not_m7"
    return {
        "tool": "v3_phoenix_aabb_raw_oracle_evidence",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": "raw generic AABB_INDEX_QUERY_2D range_intersection_rows oracle",
        "backends_requested": list(backends),
        "fixtures": [
            {
                "name": fixture["name"],
                "indexed_box_count": len(fixture["indexed_boxes"]),
                "query_box_count": len(fixture["query_boxes"]),
                "expected_row_count": len(
                    cpu_oracle_rows(
                        fixture["indexed_boxes"],
                        fixture["query_boxes"],
                        indexed_ids=fixture["indexed_ids"],
                        query_ids=fixture["query_ids"],
                    )
                ),
                "fixture_boundary": fixture["fixture_boundary"],
            }
            for fixture in fixture_catalog()
        ],
        "observed_rows": observed_rows,
        "capacity_pressure": capacity_pressure,
        "run_errors": run_errors,
        "environment": environment,
        "source_manifest_sha256": environment["source_manifest"]["sha256"],
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "raw_aabb_oracle_closes_correctness_blocker": status == "aabb_raw_oracle_pass_not_m7"
        and {"embree", "optix"}.issubset(set(backends)),
        "checks": checks,
        "failed_checks": failed_checks,
        "interpretation": (
            "This packet validates raw generic AABB range_intersection_rows against an independent "
            "closed-boundary CPU oracle. It is correctness/provenance evidence only; it does not "
            "authorize M7 promotion, release wording, full Contact Manifold wording, or broad "
            "V3-over-V2 claims."
        ),
        "goal_level_decision_audit": {
            "decision": (
                "Add an independent raw AABB oracle gate for the native-query-handle candidate "
                "instead of relying on Contact Manifold final witness correctness."
            ),
            "was_i_foolish": (
                "No. This directly targets the Huygens P0 correctness blocker without creating a "
                "new performance claim."
            ),
            "foolish_actions": (
                "The foolish action would be to call Contact Manifold final witness parity the same "
                "as generic AABB candidate-row parity."
            ),
            "other_path": (
                "I could rerun the large benchmark again. That would test timing stability but would "
                "not prove the raw AABB row contract."
            ),
            "different_path_now": (
                "Use this oracle as a blocker-closure artifact, then separately add fresh-run stability "
                "before requesting another review."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 AABB Raw Oracle Evidence",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This packet checks raw generic `AABB_INDEX_QUERY_2D`",
        "`range_intersection_rows` output against an independent closed-boundary CPU",
        "AABB oracle. It is not release evidence and not a performance claim.",
        "",
        "## Fixtures",
        "",
        "| fixture | indexed boxes | query boxes | expected rows | boundary |",
        "|---|---:|---:|---:|---|",
    ]
    for fixture in payload["fixtures"]:
        lines.append(
            "| "
            f"{fixture['name']} | "
            f"{fixture['indexed_box_count']} | "
            f"{fixture['query_box_count']} | "
            f"{fixture['expected_row_count']} | "
            f"{fixture['fixture_boundary']} |"
        )
    lines.extend(["", "## Backend Results", "", "| backend | fixture | rows | matches oracle |", "|---|---|---:|---|"])
    for row in payload["observed_rows"]:
        lines.append(
            "| "
            f"{row['backend']} | "
            f"{row['fixture']} | "
            f"{row['actual_row_count']} | "
            f"{str(bool(row['matches_independent_cpu_oracle'])).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Capacity Pressure",
            "",
            f"`{payload['capacity_pressure']}`",
            "",
            "## Source Provenance",
            "",
            f"- Local git head: `{payload['environment']['git_head']}`",
            f"- Source manifest sha256: `{payload['source_manifest_sha256']}`",
            "",
            "## Boundaries",
            "",
            "- Release authorized: `false`",
            "- Public speedup claim authorized: `false`",
            "- Broad V3-over-V2 claim authorized: `false`",
            "- M7 promotion authorized: `false`",
            "",
            "## Checks",
            "",
        ]
    )
    for name, passed in payload["checks"].items():
        lines.append(f"- `{name}`: `{str(bool(passed)).lower()}`")
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            f"Failed checks: `{payload['failed_checks']}`",
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phoenix V3 raw AABB oracle evidence.")
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def parse_backends(value: str) -> tuple[str, ...]:
    backends = tuple(dict.fromkeys(part.strip().lower() for part in value.split(",") if part.strip()))
    allowed = {"cpu", "embree", "optix"}
    unknown = [backend for backend in backends if backend not in allowed]
    if unknown:
        raise ValueError(f"unsupported backend(s): {unknown}; allowed: {sorted(allowed)}")
    if not backends:
        raise ValueError("at least one backend is required")
    return backends


def main() -> int:
    args = parse_args()
    payload = build_payload(parse_backends(args.backends))
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    args.evidence_dir.joinpath("summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload if args.pretty else {"status": payload["status"], "failed_checks": payload["failed_checks"]}, indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
