#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from goal15_compare_embree import compare_goal15
from tests._embree_support import embree_available


def run_command(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath_key = next((key for key in env if key.upper() == "PYTHONPATH"), "PYTHONPATH")
    pythonpath_entries = [str(ROOT / "src"), str(ROOT)]
    existing = env.get(pythonpath_key)
    if existing:
        pythonpath_entries.append(existing)
    env[pythonpath_key] = os.pathsep.join(pythonpath_entries)
    return subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def run_unittest_suite() -> dict[str, object]:
    cp = run_command(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "*_test.py")
    if cp.returncode != 0:
        raise RuntimeError(cp.stdout + ("\n" + cp.stderr if cp.stderr else ""))
    transcript = cp.stdout
    if cp.stderr:
        transcript = (transcript + ("\n" if transcript else "") + cp.stderr).strip()
    return {
        "command": sys.executable + " -m unittest discover -s tests -p '*_test.py'",
        "output": transcript,
    }


def run_cli_smokes() -> dict[str, object]:
    results: dict[str, object] = {}

    missing = run_command(sys.executable, "-m", "rtdsl.baseline_runner")
    if missing.returncode == 0 or "usage:" not in missing.stderr.lower():
        raise RuntimeError("baseline_runner missing-arg smoke check did not fail with usage output")
    results["baseline_runner_missing_arg"] = {"returncode": missing.returncode}

    invalid_dataset = run_command(
        sys.executable,
        "-m",
        "rtdsl.baseline_runner",
        "lsi",
        "--dataset",
        "__missing_dataset__",
    )
    invalid_text = (invalid_dataset.stdout or "") + "\n" + (invalid_dataset.stderr or "")
    if invalid_dataset.returncode == 0 or "unsupported lsi dataset" not in invalid_text:
        raise RuntimeError("baseline_runner invalid-dataset smoke check did not report the expected error")
    results["baseline_runner_invalid_dataset"] = {"returncode": invalid_dataset.returncode}

    cpu_ok = run_command(
        sys.executable,
        "-m",
        "rtdsl.baseline_runner",
        "lsi",
        "--backend",
        "cpu",
    )
    if cpu_ok.returncode != 0:
        raise RuntimeError(cpu_ok.stdout + ("\n" + cpu_ok.stderr if cpu_ok.stderr else ""))
    payload = json.loads(cpu_ok.stdout)
    if payload.get("workload") != "lsi" or "cpu_rows" not in payload:
        raise RuntimeError("baseline_runner CPU smoke did not emit the expected payload")
    results["baseline_runner_cpu"] = {"rows": len(payload["cpu_rows"])}
    return results


def run_artifact_smokes() -> dict[str, object]:
    results: dict[str, object] = {}
    if not embree_available():
        return {"skipped": True, "reason": "Embree is not installed in the current environment"}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        artifacts = rt.generate_embree_evaluation_artifacts(
            workloads=("lsi",),
            iterations=1,
            warmup=1,
            output_dir=tmp / "evaluation",
        )
        for key, path in artifacts.items():
            if not path.exists():
                raise RuntimeError(f"expected evaluation artifact `{key}` was not created")
        results["evaluation_artifacts"] = sorted(artifacts.keys())

        compare_payload = compare_goal15(tmp / "goal15")
        if not compare_payload["workloads"]["lsi"]["cpu_matches_native"]:
            raise RuntimeError("Goal 15 LSI native comparison failed during verification smoke")
        if not compare_payload["workloads"]["pip"]["embree_matches_native"]:
            raise RuntimeError("Goal 15 PIP Embree/native comparison failed during verification smoke")
        results["goal15_compare"] = {
            "lsi_pairs": compare_payload["workloads"]["lsi"]["native_pair_count"],
            "pip_pairs": compare_payload["workloads"]["pip"]["native_pair_count"],
        }
    return results


def run_embree_smokes() -> dict[str, object]:
    if not embree_available():
        return {"skipped": True, "reason": "Embree is not installed in the current environment"}
    payload = rt.run_baseline_case(
        rt.compile_kernel(county_zip_join_reference),
        "authored_lsi_minimal",
        backend="both",
    )
    if not payload.get("parity"):
        raise RuntimeError("Embree parity smoke failed for authored_lsi_minimal")
    return {"skipped": False, "parity": True, "cpu_rows": len(payload["cpu_rows"])}


def run_full_verification(*, skip_unittest: bool = False, skip_cli: bool = False, skip_artifacts: bool = False) -> dict[str, object]:
    results: dict[str, object] = {}
    if not skip_unittest:
        results["unittest"] = run_unittest_suite()
    if not skip_cli:
        results["cli"] = run_cli_smokes()
    if not skip_artifacts:
        results["artifacts"] = run_artifact_smokes()
    results["embree"] = run_embree_smokes()
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RTDL's full local verification package.")
    parser.add_argument("--skip-unittest", action="store_true")
    parser.add_argument("--skip-cli", action="store_true")
    parser.add_argument("--skip-artifacts", action="store_true")
    args = parser.parse_args(argv)

    payload = run_full_verification(
        skip_unittest=args.skip_unittest,
        skip_cli=args.skip_cli,
        skip_artifacts=args.skip_artifacts,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
