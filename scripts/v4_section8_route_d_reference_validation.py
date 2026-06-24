#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "future" / "v4" / "reference" / "route_d_fixed_radius_count_threshold_optix.cpp"
DEFAULT_BINARY = ROOT / "build" / "route_d_fixed_radius_count_threshold_optix"


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _build_command(binary: Path, optix_prefix: Path, cuda_prefix: Path) -> list[str]:
    return [
        str(cuda_prefix / "bin" / "nvcc"),
        "-std=c++17",
        "-O3",
        "-I" + str(optix_prefix / "include"),
        "-I" + str(cuda_prefix / "include"),
        str(REFERENCE),
        "-L" + str(cuda_prefix / "lib64"),
        "-lcuda",
        "-lnvrtc",
        "-o",
        str(binary),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V4 Section 8 Route D independent OptiX reference.")
    parser.add_argument("--copies", type=int, action="append", default=[])
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    parser.add_argument("--optix-prefix", type=Path, default=Path("/root/vendor/optix-dev"))
    parser.add_argument("--cuda-prefix", type=Path, default=Path("/usr/local/cuda-12.8"))
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    copies = tuple(args.copies) if args.copies else (8192, 32768, 131072)
    plan = {
        "protocol": "v4_section8_route_d_handwritten_optix_reference",
        "source": str(REFERENCE.relative_to(ROOT)),
        "binary": str(args.binary),
        "copies": list(copies),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "independence_contract": {
            "imports_rtdsl": False,
            "links_librtdl_optix": False,
            "calls_rtdl_optix_symbols": False,
            "uses_rtdl_python_app_route": False,
            "standalone_cuda_driver_optix": True,
        },
        "release_claim_authorized": False,
        "near_handwritten_optix_claim_authorized": False,
    }
    if args.dry_run:
        payload: dict[str, Any] = {"status": "dry_run", **plan}
    else:
        build = None
        if not args.skip_build:
            args.binary.parent.mkdir(parents=True, exist_ok=True)
            command = _build_command(args.binary, args.optix_prefix, args.cuda_prefix)
            build = _run(command, cwd=ROOT)
            if build.returncode != 0:
                payload = {
                    "status": "build_failed",
                    **plan,
                    "build_command": command,
                    "build_stdout": build.stdout,
                    "build_stderr": build.stderr,
                }
                text = json.dumps(payload, indent=2, sort_keys=True)
                if args.json_out:
                    args.json_out.parent.mkdir(parents=True, exist_ok=True)
                    args.json_out.write_text(text + "\n", encoding="utf-8")
                print(text)
                return 1
        results = []
        failures = []
        for copy_count in copies:
            command = [
                str(args.binary),
                "--copies",
                str(copy_count),
                "--repeat",
                str(args.repeat),
                "--warmup",
                str(args.warmup),
            ]
            run = _run(command, cwd=ROOT)
            if run.returncode != 0:
                failures.append(
                    {
                        "copies": copy_count,
                        "command": command,
                        "returncode": run.returncode,
                        "stdout": run.stdout,
                        "stderr": run.stderr,
                    }
                )
                continue
            results.append(json.loads(run.stdout))
        correctness_passed = all(
            bool(result.get("correctness", {}).get("correctness_passed"))
            for result in results
        ) and not failures
        payload = {
            "status": "measured" if not failures else "run_failed",
            **plan,
            "build": None
            if build is None
            else {
                "returncode": build.returncode,
                "stdout": build.stdout,
                "stderr": build.stderr,
            },
            "results": results,
            "failures": failures,
            "correctness_passed": correctness_passed,
            "route_d_reference_available": correctness_passed,
            "claim_boundary": (
                "Route D can support independent ceiling comparison only after external review; "
                "it does not authorize V4 release or broad speedup wording."
            ),
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"dry_run", "measured"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
