#!/usr/bin/env python3
"""Bind exact host/build bytes and explicit owner authorization for Goal5798."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments" / "goal5798_premeasurement"
sys.path.insert(0, str(GOAL))
from contract_runtime import digest, load_freeze, validate_host_binding
from worker_common import load_runtime_manifest, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--host-binding", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--rtdl-native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--owner-authorized-exact-goal5798", action="store_true")
    parser.add_argument("--owner-authorized-goal5798-portable", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    freeze_path = args.freeze.resolve()
    freeze = load_freeze(freeze_path)
    portable = freeze["schema"] == "rtdl.goal5798.portable_premeasurement_freeze.v5"
    if portable and not args.owner_authorized_goal5798_portable:
        raise RuntimeError("portable owner authorization literal absent")
    if not portable and not args.owner_authorized_exact_goal5798:
        raise RuntimeError("exact owner authorization literal absent")
    runtime = load_runtime_manifest(args.runtime_manifest.resolve())
    binding = json.loads(args.host_binding.read_text(encoding="utf-8"))
    reasons = validate_host_binding(freeze, binding)
    if reasons:
        raise RuntimeError("host binding rejected: " + ",".join(reasons))
    result = {
        "schema": "rtdl.goal5798.execution_authority.v1",
        "freeze_file_sha256": sha256_file(freeze_path),
        "freeze_sha256": freeze["freeze_sha256"],
        "runtime_manifest_sha256": runtime["manifest_sha256"],
        "host_binding": binding,
        "host_binding_sha256": binding["binding_sha256"],
        "built_artifacts": {
            "direct_binary_sha256": sha256_file(args.direct_binary.resolve()),
            "rtdl_native_sha256": sha256_file(args.rtdl_native.resolve()),
        },
        "authorizations": {
            "exact_host_bound": True,
            "functional_smoke": True,
            "memory_workers": True,
            "performance_workers": True,
            "worker_zero": True,
        },
        "failure_policy": {
            "retry": False, "resume": False, "replacement": False,
            "row_drop": False, "any_memory_or_correctness_failure_stops_before_timing": True,
        },
    }
    result["authority_sha256"] = digest(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": ("AUTHORIZED_PORTABLE_GOAL5798" if portable
                   else "AUTHORIZED_EXACT_GOAL5798"),
        "authority_sha256": result["authority_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
