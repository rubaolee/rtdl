from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "examples" / "current" / "apps" / "ml" / "rtdl_dbscan_clustering_app.py"


def _run_app(*, copies: int, backend: str) -> dict[str, object]:
    command = [
        sys.executable,
        str(APP),
        "--backend",
        backend,
        "--copies",
        str(int(copies)),
        "--output-mode",
        "core_count",
    ]
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "RT-DBSCAN core-count smoke failed with exit code "
            f"{result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def run_smoke(*, copies: int = 1, backend: str = "cpu_python_reference") -> dict[str, object]:
    payload = _run_app(copies=copies, backend=backend)
    if not bool(payload.get("matches_oracle")):
        raise RuntimeError("RT-DBSCAN core-count smoke did not match oracle")
    if int(copies) == 1 and int(payload.get("core_count", -1)) != 7:
        raise RuntimeError("RT-DBSCAN one-copy core-count smoke expected core_count=7")
    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.core_count_smoke.v1",
        "paper_app": "rt-dbscan-paper",
        "status": "pass",
        "backend": backend,
        "copies": int(copies),
        "point_count": int(payload.get("point_count", 0)),
        "core_count": int(payload.get("core_count", 0)),
        "oracle_core_count": int(payload.get("oracle_core_count", payload.get("core_count", 0))),
        "matches_oracle": bool(payload.get("matches_oracle")),
        "summary_mode": payload.get("summary_mode"),
        "author_comparator_used": False,
        "paper_reproduction_claim_authorized": False,
        "whole_program_speedup_claim_authorized": False,
        "boundary": (
            "Local RTDL CPU-reference/oracle smoke for the first RT-DBSCAN paper-app "
            "target. This is not an author-comparator run, exact paper-input run, or "
            "performance result."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RT-DBSCAN paper-app core-count smoke gate.")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = run_smoke(copies=args.copies, backend=args.backend)
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
