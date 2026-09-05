"""Run the exact Goal5847 RTDL implementation under the Goal5848 harness."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .contracts import (
    BLOCKS,
    PREDECESSOR_RTDL_ARM,
    RELATION_TASK,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TRIANGLE_TASK,
    WORKER_SCHEMA,
    digest,
)
from .worker import _hardware, _run_rtdl, _write_create


def _git_identity(path: Path) -> dict[str, object]:
    values = {}
    for label, arguments in (
        ("commit", ("rev-parse", "HEAD")),
        ("tree", ("rev-parse", "HEAD^{tree}")),
        ("status", ("status", "--porcelain=v1", "--untracked-files=all")),
    ):
        values[label] = subprocess.run(
            ["git", "-C", str(path), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    return {**values, "clean": values["status"] == ""}


def _activate_predecessor(root: Path) -> Path:
    if "rtdsl" in sys.modules or any(
        name.startswith("rtdsl.") for name in sys.modules
    ):
        raise RuntimeError("Goal5848 predecessor process already imported rtdsl")
    source = root.resolve(strict=True) / "src"
    package = source / "rtdsl" / "v4_rtdlexe.py"
    if not package.is_file() or package.is_symlink():
        raise RuntimeError("Goal5848 predecessor rtdsl source is absent")
    sys.path.insert(0, str(source))
    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=(RELATION_TASK, TRIANGLE_TASK), required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument(
        "--classification",
        choices=("exploration", "formal"),
        default="exploration",
    )
    parser.add_argument("--predecessor-root", type=Path, required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=STEADY_WARMUPS)
    parser.add_argument("--repetitions", type=int, default=STEADY_REPETITIONS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if (
        not 0 <= args.block < BLOCKS
        or args.warmups <= 0
        or args.repetitions <= 0
    ):
        raise ValueError("Goal5848 predecessor timing arguments are invalid")
    root = args.predecessor_root.resolve(strict=True)
    source = _git_identity(root)
    if (
        source["commit"] != args.expected_predecessor_commit
        or source["clean"] is not True
    ):
        raise RuntimeError("Goal5848 predecessor source identity differs")
    _activate_predecessor(root)
    args.phase_instrumentation = "on"
    measurements = _run_rtdl(args, legacy_provider_timing_api=True)
    result = {
        "schema": WORKER_SCHEMA,
        "status": "PASS__GOAL5848_WORKER",
        "arm": PREDECESSOR_RTDL_ARM,
        "task": args.task,
        "block": args.block,
        "worker_id": args.worker_id,
        "classification": args.classification,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "python": sys.version.split()[0],
        "source": source,
        "hardware": _hardware(),
        "measurements": measurements,
        "claim_boundary": {
            "exploration_or_formal_classification_owned_by_controller": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
