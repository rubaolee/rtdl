from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())


WORKLOADS = ("pip", "lsi", "overlay_seed")


def _claim_boundary() -> dict[str, bool]:
    return {
        "internal_investigation_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "app_specific_native_engine_shortcut_authorized": False,
    }


def _command_output(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _json_from_stdout(stdout: str) -> dict[str, Any]:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        start = stdout.find("{")
        end = stdout.rfind("}")
        if start >= 0 and end > start:
            return json.loads(stdout[start : end + 1])
        raise


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
    }


def _run_one(
    *,
    root: Path,
    python: str,
    workload: str,
    dataset: str,
    optix_library: str,
    timeout_sec: int,
) -> dict[str, Any]:
    command = [
        python,
        "examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
        "--workload",
        workload,
        "--execution-route",
        "prepared_optix",
        "--result-mode",
        "count",
        "--dataset",
        dataset,
        "--no-rows",
    ]
    env = None
    if optix_library:
        import os

        env = os.environ.copy()
        env["RTDL_OPTIX_LIBRARY"] = optix_library
        env["PYTHONPATH"] = "src:."
    print(f"[goal3534] {root.name} {workload}: {' '.join(command)}", flush=True)
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
    )
    elapsed = time.perf_counter() - started
    record = {
        "command": command,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }
    if completed.returncode != 0:
        raise RuntimeError(json.dumps(record, indent=2, sort_keys=True))
    payload = _json_from_stdout(completed.stdout)
    return {"run": record, "payload": payload}


def _common_row_id(workload: str) -> str:
    return {
        "pip": "rayjoin_common_pip_prepared_optix_count",
        "lsi": "rayjoin_common_lsi_prepared_optix_scalar_count",
        "overlay_seed": "rayjoin_common_overlay_seed_prepared_optix_active_count",
    }[workload]


def _contract(workload: str) -> str:
    return {
        "pip": "point_closed_shape_membership_count",
        "lsi": "segment_pair_intersection_scalar_count",
        "overlay_seed": "shape_pair_active_dependency_scalar_count",
    }[workload]


def _summarize_version(
    *,
    root: Path,
    checkout_label: str,
    python: str,
    dataset: str,
    optix_library: str,
    repeats: int,
    timeout_sec: int,
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for workload in WORKLOADS:
        samples = []
        for repeat in range(1, repeats + 1):
            result = _run_one(
                root=root,
                python=python,
                workload=workload,
                dataset=dataset,
                optix_library=optix_library,
                timeout_sec=timeout_sec,
            )
            payload = result["payload"]
            query_sec = float(payload["phases_sec"]["prepared_query_sec"])
            samples.append(
                {
                    "repeat": repeat,
                    "prepared_query_sec": query_sec,
                    "summary": payload.get("summary", {}),
                    "run_elapsed_sec": result["run"]["elapsed_sec"],
                }
            )
        values = [float(sample["prepared_query_sec"]) for sample in samples]
        rows[workload] = {
            "row_id": _common_row_id(workload),
            "contract": _contract(workload),
            "checkout_label": checkout_label,
            "root": str(root),
            "commit": _command_output(["git", "rev-parse", "HEAD"], cwd=root),
            "metric_source": "phases_sec.prepared_query_sec",
            "metric_sec": _stats(values),
            "samples": samples,
            "claim_boundary": _claim_boundary(),
        }
    return rows


def _promoted_equivalence(row_id: str) -> dict[str, str | None]:
    mapping: dict[str, dict[str, str | None]] = {
        "rayjoin_count_parity_pip_prepared_optix": {
            "v23_equivalent_status": "common_scalar_contract_measured",
            "v23_baseline_row_id": "rayjoin_common_pip_prepared_optix_count",
        },
        "rayjoin_count_parity_overlay_seed_active_count": {
            "v23_equivalent_status": "common_scalar_output_contract_measured_but_v2_8_route_is_device_continuation_variant",
            "v23_baseline_row_id": "rayjoin_common_overlay_seed_prepared_optix_active_count",
        },
        "rayjoin_count_parity_lsi_left_id_dense_count": {
            "v23_equivalent_status": "no_same_contract_v23_has_scalar_total_lsi_count_only",
            "v23_baseline_row_id": "rayjoin_common_lsi_prepared_optix_scalar_count",
        },
    }
    return mapping.get(
        row_id,
        {
            "v23_equivalent_status": "no_equivalent_contract_in_v23_evidence_checkout",
            "v23_baseline_row_id": None,
        },
    )


def _promoted_rows_from_packet(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    packet = json.loads(path.read_text(encoding="utf-8"))
    promoted = []
    for row in packet.get("rows", []):
        equivalence = _promoted_equivalence(str(row["row_id"]))
        promoted.append(
            {
                "row_id": row["row_id"],
                "contract": row["contract"],
                "v23_equivalent_status": equivalence["v23_equivalent_status"],
                "v23_baseline_row_id": equivalence["v23_baseline_row_id"],
                "v28_metric_sec": row.get("primary_metric_sec"),
                "v28_metric_source": row.get("primary_metric_source"),
                "claim_boundary": _claim_boundary(),
            }
        )
    return promoted


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    dataset = f"{args.left_cdb} + {args.right_cdb}"
    if args.dry_run:
        return {
            "schema": "rtdl.goal3534.rayjoin_v23_contract_baseline_probe.v1",
            "goal": 3534,
            "dry_run": True,
            "dataset": dataset,
            "common_contract_rows": [_common_row_id(workload) for workload in WORKLOADS],
            "promoted_packet_path": str(args.promoted_packet),
            "claim_boundary": _claim_boundary(),
        }
    v23 = _summarize_version(
        root=args.v23_root,
        checkout_label="v23_evidence",
        python=args.python,
        dataset=dataset,
        optix_library=args.v23_optix_library,
        repeats=args.repeats,
        timeout_sec=args.timeout_sec,
    )
    v28 = _summarize_version(
        root=args.v28_root,
        checkout_label="v28_current",
        python=args.python,
        dataset=dataset,
        optix_library=args.v28_optix_library,
        repeats=args.repeats,
        timeout_sec=args.timeout_sec,
    )
    comparisons = []
    for workload in WORKLOADS:
        v23_sec = float(v23[workload]["metric_sec"]["median"])
        v28_sec = float(v28[workload]["metric_sec"]["median"])
        comparisons.append(
            {
                "row_id": _common_row_id(workload),
                "contract": _contract(workload),
                "v23_sec": v23_sec,
                "v28_sec": v28_sec,
                "v28_speedup_vs_v23": v23_sec / v28_sec if v28_sec > 0.0 else None,
                "v23_summary": v23[workload]["samples"][-1]["summary"],
                "v28_summary": v28[workload]["samples"][-1]["summary"],
                "metric_source": "median(phases_sec.prepared_query_sec)",
                "claim_boundary": _claim_boundary(),
            }
        )
    return {
        "schema": "rtdl.goal3534.rayjoin_v23_contract_baseline_probe.v1",
        "goal": 3534,
        "dry_run": False,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset": dataset,
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
        "repeats": int(args.repeats),
        "v23_root": str(args.v23_root),
        "v28_root": str(args.v28_root),
        "v23_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.v23_root),
        "v28_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.v28_root),
        "common_contract_comparisons": comparisons,
        "v23_rows": v23,
        "v28_rows": v28,
        "v2_8_promoted_rows_without_v23_equivalent": _promoted_rows_from_packet(args.promoted_packet),
        "claim_boundary": _claim_boundary(),
        "interpretation": (
            "Measures the old common RayJoin prepared_optix scalar count contracts in both checkouts "
            "and records v2.8 promoted contracts as no-v2.3-equivalent unless a matching v2.3 surface exists."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3534 RayJoin v2.3 contract baseline probe.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--v23-root", type=Path, default=Path("/root/rtdl_goal3524/v23_evidence"))
    parser.add_argument("--v28-root", type=Path, default=Path("/root/rtdl_goal3524/v28_current"))
    parser.add_argument("--v23-optix-library", default="/root/rtdl_goal3524/v23_evidence/build/librtdl_optix.so")
    parser.add_argument("--v28-optix-library", default="/root/rtdl_goal3524/v28_current/build/librtdl_optix.so")
    parser.add_argument("--left-cdb", default="tests/fixtures/rayjoin/br_county_subset.cdb")
    parser.add_argument("--right-cdb", default="tests/fixtures/rayjoin/br_county_subset.cdb")
    parser.add_argument("--promoted-packet", type=Path, default=ROOT / "docs" / "reports" / "goal3532_rayjoin_promoted_contract_packet_a5000_cdb_pair" / "summary.json")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--timeout-sec", type=int, default=120)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
