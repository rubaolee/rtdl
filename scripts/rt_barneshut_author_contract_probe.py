from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rt_barneshut_author_contract import (  # noqa: E402
    RT_BARNESHUT_AUTHOR_COMMIT,
    RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
    parse_rt_barneshut_author_stdout,
    run_rt_barneshut_cpu_author_semantics_oracle,
    validate_rt_barneshut_author_contract_summary,
    write_trimmed_rt_barneshut_author_dataset,
)


def _run_author_binary(binary: Path, file_type: str, dataset: Path) -> dict[str, object]:
    start = time.perf_counter()
    proc = subprocess.run(
        [str(binary), file_type, str(dataset)],
        text=True,
        capture_output=True,
        check=False,
    )
    wall = time.perf_counter() - start
    return {
        "cmd": [str(binary), file_type, str(dataset)],
        "returncode": proc.returncode,
        "wall_seconds": wall,
        "stdout_tail": proc.stdout.splitlines()[-40:],
        "stderr_tail": proc.stderr.splitlines()[-40:],
        "parsed": parse_rt_barneshut_author_stdout(proc.stdout),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the RT-BarnesHut same-input contract gate. This is a semantic "
            "gate, not a public speedup benchmark."
        )
    )
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--file-type", required=True, choices=("treelogy", "csv"))
    parser.add_argument("--limit", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--author-binary", type=Path)
    parser.add_argument("--keep-trimmed-dataset", type=Path)
    args = parser.parse_args()

    if args.limit <= 0:
        raise SystemExit("--limit must be positive")

    if args.keep_trimmed_dataset is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="rtdl_rt_barneshut_")
        trimmed_path = Path(temp_dir.name) / f"trimmed_{args.limit}.{args.file_type}"
    else:
        temp_dir = None
        trimmed_path = args.keep_trimmed_dataset

    try:
        write_trimmed_rt_barneshut_author_dataset(
            args.dataset,
            trimmed_path,
            file_type=args.file_type,
            limit=args.limit,
        )

        oracle = run_rt_barneshut_cpu_author_semantics_oracle(
            trimmed_path,
            file_type=args.file_type,
            limit=args.limit,
        )
        validate_rt_barneshut_author_contract_summary(oracle)

        author_run = None
        if args.author_binary is not None:
            author_run = _run_author_binary(args.author_binary, args.file_type, trimmed_path)

        payload = {
            "status": "rt_barneshut_author_contract_probe_complete",
            "contract_version": RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
            "author_commit": RT_BARNESHUT_AUTHOR_COMMIT,
            "source_dataset": str(args.dataset),
            "trimmed_dataset": str(trimmed_path),
            "file_type": args.file_type,
            "limit": args.limit,
            "rtdl_cpu_author_semantics_oracle": asdict(oracle),
            "author_binary_run": author_run,
            "fairness": {
                "same_input_as_author_binary": author_run is not None,
                "same_author_file_parser_contract": True,
                "same_author_tree_and_force_cpu_contract": True,
                "performance_comparison_authorized": False,
                "reason": (
                    "The RTDL row here is a CPU semantic oracle. It validates the "
                    "paper contract and author input path; it is not yet the V4 "
                    "RT-core performance route."
                ),
            },
            "claim_boundary": {
                "paper_semantics_contract_gate": True,
                "rt_core_performance_route": False,
                "v2_v3_v4_speedup_claim_authorized": False,
                "authors_code_speedup_claim_authorized": False,
                "public_release_claim_authorized": False,
            },
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if author_run is None or author_run["returncode"] == 0 else int(author_run["returncode"])
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
