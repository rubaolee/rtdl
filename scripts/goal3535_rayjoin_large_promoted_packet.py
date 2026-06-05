from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.datasets import CdbChain  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402
from rtdsl.datasets import CdbPoint  # noqa: E402
from rtdsl.datasets import write_cdb  # noqa: E402


def _claim_boundary() -> dict[str, bool]:
    return {
        "internal_investigation_only": True,
        "generated_dataset_not_rayjoin_paper_input": True,
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


def _make_square_grid_cdb(
    *,
    name: str,
    grid: int,
    spacing: float,
    side: float,
    offset_x: float,
    offset_y: float,
    face_base: int,
) -> CdbDataset:
    chains: list[CdbChain] = []
    next_point_id = 1
    next_chain_id = 1
    for row in range(grid):
        for col in range(grid):
            x0 = col * spacing + offset_x
            y0 = row * spacing + offset_y
            points = (
                CdbPoint(x=x0, y=y0),
                CdbPoint(x=x0 + side, y=y0),
                CdbPoint(x=x0 + side, y=y0 + side),
                CdbPoint(x=x0, y=y0 + side),
            )
            chains.append(
                CdbChain(
                    chain_id=next_chain_id,
                    point_count=len(points),
                    first_point_id=next_point_id,
                    last_point_id=next_point_id + len(points) - 1,
                    left_face_id=face_base + next_chain_id,
                    right_face_id=0,
                    points=points,
                )
            )
            next_chain_id += 1
            next_point_id += len(points)
    return CdbDataset(name=name, chains=tuple(chains))


def _write_generated_pair(args: argparse.Namespace, artifact_dir: Path) -> dict[str, Any]:
    left = _make_square_grid_cdb(
        name=f"goal3535_left_square_grid_{args.grid}",
        grid=args.grid,
        spacing=args.spacing,
        side=args.side,
        offset_x=0.0,
        offset_y=0.0,
        face_base=1000000,
    )
    right = _make_square_grid_cdb(
        name=f"goal3535_right_square_grid_{args.grid}",
        grid=args.grid,
        spacing=args.spacing,
        side=args.side,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        face_base=2000000,
    )
    left_path = artifact_dir / f"goal3535_left_grid{args.grid}.cdb"
    right_path = artifact_dir / f"goal3535_right_grid{args.grid}.cdb"
    write_cdb(left, left_path)
    write_cdb(right, right_path)
    return {
        "left_cdb": str(left_path),
        "right_cdb": str(right_path),
        "grid": int(args.grid),
        "shape_count_per_side": int(args.grid * args.grid),
        "spacing": float(args.spacing),
        "side": float(args.side),
        "offset_x": float(args.offset_x),
        "offset_y": float(args.offset_y),
        "expected_local_overlap_pattern": (
            "Each right square is offset from a left square. With side > spacing/2, "
            "the relation stream should contain many but bounded local shape-pair overlaps."
        ),
        "claim_boundary": _claim_boundary(),
    }


def _json_from_stdout(stdout: str) -> dict[str, Any]:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        start = stdout.find("{")
        end = stdout.rfind("}")
        if start >= 0 and end > start:
            return json.loads(stdout[start : end + 1])
        raise


def _run_packet(args: argparse.Namespace, artifact_dir: Path, pair: dict[str, Any]) -> dict[str, Any]:
    packet_output = artifact_dir / "promoted_packet.json"
    packet_artifact_dir = artifact_dir / "packet_children"
    command = [
        str(args.python),
        "scripts/goal3532_rayjoin_promoted_contract_packet.py",
        "--left-cdb",
        str(pair["left_cdb"]),
        "--right-cdb",
        str(pair["right_cdb"]),
        "--artifact-dir",
        str(packet_artifact_dir),
        "--output",
        str(packet_output),
        "--iterations",
        str(args.iterations),
        "--max-rows",
        str(args.max_rows),
        "--timeout-sec",
        str(args.timeout_sec),
        "--overlay-timeout-sec",
        str(args.overlay_timeout_sec),
        "--overlay-executor-repeats",
        str(args.overlay_executor_repeats),
        "--overlay-device-planner-repeats",
        str(args.overlay_device_planner_repeats),
        "--relation-column-warmup-repeats",
        str(args.relation_column_warmup_repeats),
        "--payload-workers",
        str(args.payload_workers),
        "--progress-every",
        str(args.progress_every),
        "--max-triangle-pairs-per-task",
        str(args.max_triangle_pairs_per_task),
    ]
    print(f"[goal3535] running promoted packet: {' '.join(command)}", flush=True)
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=int(args.overlay_timeout_sec) + int(args.timeout_sec) * 2,
    )
    elapsed = time.perf_counter() - started
    run = {
        "command": command,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "packet_output": str(packet_output),
        "packet_artifact_dir": str(packet_artifact_dir),
    }
    if completed.returncode != 0:
        raise RuntimeError(json.dumps(run, indent=2, sort_keys=True))
    payload = json.loads(packet_output.read_text(encoding="utf-8")) if packet_output.exists() else _json_from_stdout(completed.stdout)
    return {"run": run, "payload": payload}


def _row_table(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in packet.get("rows", []):
        rows.append(
            {
                "row_id": row.get("row_id"),
                "contract": row.get("contract"),
                "primary_metric_sec": row.get("primary_metric_sec"),
                "primary_metric_source": row.get("primary_metric_source"),
                "row_count": row.get("row_count"),
                "relation_row_count": row.get("relation_row_count"),
                "candidate_relation_row_count": row.get("candidate_relation_row_count"),
                "supported_relation_row_count": row.get("supported_relation_row_count"),
                "status": row.get("status"),
                "claim_boundary": _claim_boundary(),
            }
        )
    return rows


def run(args: argparse.Namespace) -> dict[str, Any]:
    artifact_dir = args.artifact_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    pair = _write_generated_pair(args, artifact_dir)
    if args.dry_run:
        packet = {
            "schema": "rtdl.goal3532.rayjoin_promoted_contract_packet.v1",
            "dry_run": True,
            "rows": [],
        }
        packet_run = {"dry_run": True}
    else:
        packet_result = _run_packet(args, artifact_dir, pair)
        packet = packet_result["payload"]
        packet_run = packet_result["run"]
    return {
        "schema": "rtdl.goal3535.rayjoin_large_promoted_packet.v1",
        "goal": 3535,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=ROOT),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
        "dry_run": bool(args.dry_run),
        "artifact_dir": str(artifact_dir),
        "generated_pair": pair,
        "packet_run": packet_run,
        "packet_schema": packet.get("schema"),
        "packet_row_count": packet.get("row_count", len(packet.get("rows", []))),
        "promoted_rows": _row_table(packet),
        "claim_boundary": _claim_boundary(),
        "interpretation": (
            "Generated deterministic larger CDB square-grid pair and ran the Goal3532 promoted "
            "RayJoin packet. This is scale evidence for RTDL contracts, not RayJoin paper input."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3535 larger generated-CDB RayJoin promoted packet.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--grid", type=int, default=32)
    parser.add_argument("--spacing", type=float, default=2.0)
    parser.add_argument("--side", type=float, default=1.5)
    parser.add_argument("--offset-x", type=float, default=0.5)
    parser.add_argument("--offset-y", type=float, default=0.5)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--max-rows", type=int, default=1000000)
    parser.add_argument("--progress-every", type=int, default=10000)
    parser.add_argument("--max-triangle-pairs-per-task", type=int, default=512)
    parser.add_argument("--relation-column-warmup-repeats", type=int, default=2)
    parser.add_argument("--overlay-executor-repeats", type=int, default=3)
    parser.add_argument("--overlay-device-planner-repeats", type=int, default=3)
    parser.add_argument("--payload-workers", type=int, default=4)
    parser.add_argument("--timeout-sec", type=int, default=600)
    parser.add_argument("--overlay-timeout-sec", type=int, default=1800)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not args.dry_run:
        missing = [row["row_id"] for row in payload["promoted_rows"] if row.get("primary_metric_sec") is None]
        if missing:
            raise SystemExit(f"missing promoted-row metrics: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
