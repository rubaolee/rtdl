from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


DEFAULT_INPUT = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper" / "data" / "fixtures" / "tiny3d_core_count.csv"


def _read_points(path: Path) -> tuple[tuple[float, float, float], ...]:
    points: list[tuple[float, float, float]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part for part in re.split(r"[\s,]+", line) if part]
        if len(parts) != 3:
            raise ValueError(f"{path}:{line_number} expected exactly 3 coordinates, got {len(parts)}")
        points.append((float(parts[0]), float(parts[1]), float(parts[2])))
    if not points:
        raise ValueError(f"{path} contains no points")
    return tuple(points)


def _to_rtdl_points(points: tuple[tuple[float, float, float], ...]) -> tuple[rt.Point3D, ...]:
    return tuple(rt.Point3D(id=index, x=x, y=y, z=z) for index, (x, y, z) in enumerate(points))


def _cpu_reference_core_count(points: tuple[tuple[float, float, float], ...], *, epsilon: float, min_points: int) -> int:
    radius_sq = float(epsilon) * float(epsilon)
    core_count = 0
    for qx, qy, qz in points:
        count = 0
        for sx, sy, sz in points:
            dx = sx - qx
            dy = sy - qy
            dz = sz - qz
            if dx * dx + dy * dy + dz * dz <= radius_sq + 1e-12:
                count += 1
        if count >= int(min_points):
            core_count += 1
    return core_count


def _rtdl_optix_core_count(points: tuple[tuple[float, float, float], ...], *, epsilon: float, min_points: int) -> dict[str, object]:
    import numpy as np

    rtdl_points = _to_rtdl_points(points)
    with rt.prepare_optix_fixed_radius_count_threshold_3d(rtdl_points, max_radius=epsilon) as prepared:
        result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
            prepared,
            rtdl_points,
            radius=epsilon,
            threshold=int(min_points),
            partner="numba",
            return_metadata=True,
        )
    flags = np.asarray(result["columns"]["threshold_flags"].copy_to_host(), dtype=np.uint32)
    return {
        "backend": "optix",
        "core_count": int(flags.sum()),
        "metadata": dict(result["metadata"]),
    }


def _rtdl_core_count(points: tuple[tuple[float, float, float], ...], *, epsilon: float, min_points: int, backend: str) -> dict[str, object]:
    if backend == "cpu_reference":
        return {
            "backend": "cpu_reference",
            "core_count": _cpu_reference_core_count(points, epsilon=epsilon, min_points=min_points),
            "metadata": {
                "native_engine_row_contract": "not_called_cpu_reference_only",
                "rt_core_accelerated": False,
            },
        }
    if backend == "optix":
        return _rtdl_optix_core_count(points, epsilon=epsilon, min_points=min_points)
    raise ValueError("backend must be cpu_reference or optix")


def _last_json_line(path: Path) -> dict[str, object]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for line in reversed(lines):
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise ValueError(f"{path} does not contain a JSON payload line")


def _run_author(author_binary: Path, input_path: Path, *, size: int, epsilon: float, min_points: int, output_path: Path) -> dict[str, object]:
    if output_path.exists():
        output_path.unlink()
    command = [
        str(author_binary),
        str(input_path),
        str(int(size)),
        str(float(epsilon)),
        str(int(min_points)),
        str(output_path),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            "AuthorOfficial RT-DBSCAN core-count run failed with exit code "
            f"{completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    payload = _last_json_line(output_path)
    payload["command"] = command
    payload["stdout_tail"] = completed.stdout[-2000:]
    payload["stderr_tail"] = completed.stderr[-2000:]
    return payload


def run_gate(
    *,
    input_path: Path,
    epsilon: float,
    min_points: int,
    backend: str,
    author_binary: Path | None = None,
    author_output: Path | None = None,
) -> dict[str, object]:
    points = _read_points(input_path)
    rtdl_result = _rtdl_core_count(points, epsilon=epsilon, min_points=min_points, backend=backend)
    author_payload = None
    if author_binary is not None:
        output_path = author_output
        if output_path is None:
            tmp = tempfile.NamedTemporaryFile(prefix="rt_dbscan_author_core_count_", suffix=".jsonl", delete=False)
            tmp.close()
            output_path = Path(tmp.name)
        author_payload = _run_author(
            author_binary,
            input_path,
            size=len(points),
            epsilon=epsilon,
            min_points=min_points,
            output_path=output_path,
        )
    matched = None
    if author_payload is not None:
        matched = int(author_payload["core_count"]) == int(rtdl_result["core_count"])
    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.authorofficial_core_count_gate.v1",
        "paper_app": "rt-dbscan-paper",
        "input_path": str(input_path),
        "point_count": len(points),
        "epsilon": float(epsilon),
        "min_points": int(min_points),
        "rtdl": rtdl_result,
        "author": author_payload,
        "author_comparator_used": author_payload is not None,
        "matched": matched,
        "bounded_core_count_reproduction_claim_authorized": bool(author_payload is not None and matched),
        "paper_reproduction_claim_authorized": False,
        "whole_program_speedup_claim_authorized": False,
        "performance_claim_authorized": False,
        "boundary": (
            "Bounded same-input RT-DBSCAN core-count comparator gate. It covers "
            "the call-1 fixed-radius core predicate count only; it does not claim "
            "full DBSCAN labels, exact paper dataset reproduction, or performance."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RT-DBSCAN AuthorOfficial core-count comparator gate.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--epsilon", type=float, default=0.35)
    parser.add_argument("--min-points", type=int, default=3)
    parser.add_argument("--backend", choices=("cpu_reference", "optix"), default="cpu_reference")
    parser.add_argument("--author-binary", type=Path, default=None)
    parser.add_argument("--author-output", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = run_gate(
        input_path=args.input,
        epsilon=args.epsilon,
        min_points=args.min_points,
        backend=args.backend,
        author_binary=args.author_binary,
        author_output=args.author_output,
    )
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n", encoding="utf-8")
    print(text)
    if summary["author_comparator_used"] and not summary["matched"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
